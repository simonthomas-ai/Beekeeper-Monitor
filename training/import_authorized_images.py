#!/usr/bin/env python3
"""Import explicitly authorized images into a sanitized, unreviewed review queue."""
from __future__ import annotations
import argparse, csv, hashlib, io, ipaddress, os, socket, urllib.error, urllib.parse, urllib.request
from pathlib import Path

from inaturalist_media import normalize_if_inaturalist

LICENSE_URLS = {
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
}
ALLOWED = set(LICENSE_URLS)
FIELDS = ["source_id", "source_url", "image_url", "creator", "license", "license_url", "attribution"]
OUTPUT = FIELDS + ["requested_image_url", "image_path", "source_sha256", "sha256", "image_format", "width", "height", "exif_removed"]
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 30_000_000
MIME_FORMATS = {"image/jpeg": ("JPEG", ".jpg"), "image/png": ("PNG", ".png"), "image/webp": ("WEBP", ".webp")}


def public_https(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("public HTTPS URL required")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("public HTTPS URL required without credentials or fragments")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("source host could not be resolved") from exc
    if not addresses:
        raise ValueError("source host did not resolve")
    for entry in addresses:
        try:
            address = ipaddress.ip_address(entry[4][0].split("%", 1)[0])
        except ValueError as exc:
            raise ValueError("source host returned an invalid address") from exc
        if not address.is_global:
            raise ValueError("non-public address prohibited")
    return url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("redirects require manual source review")


def sanitize_image(data: bytes, content_type: str) -> tuple[bytes, str, str, int, int]:
    """Decode, apply EXIF orientation, re-encode pixels and drop copied metadata."""
    if content_type not in MIME_FORMATS:
        raise ValueError("unsupported image MIME type")
    expected_format, suffix = MIME_FORMATS[content_type]
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError("Install Pillow from training/requirements.txt before importing images") from exc
    try:
        with Image.open(io.BytesIO(data)) as source:
            if source.format != expected_format:
                raise ValueError("image bytes do not match the declared MIME type")
            if source.width < 1 or source.height < 1 or source.width * source.height > MAX_IMAGE_PIXELS:
                raise ValueError("image dimensions exceed the safe import limit")
            source.verify()
        with Image.open(io.BytesIO(data)) as source:
            source.load()
            oriented = ImageOps.exif_transpose(source)
            has_alpha = "A" in oriented.getbands() or "transparency" in oriented.info
            mode = "RGB" if expected_format == "JPEG" or not has_alpha else "RGBA"
            clean = oriented.convert(mode)
            output = io.BytesIO()
            if expected_format == "JPEG":
                clean.save(output, format="JPEG", quality=95, optimize=True)
            elif expected_format == "PNG":
                clean.save(output, format="PNG", optimize=True, compress_level=9)
            else:
                clean.save(output, format="WEBP", quality=95, method=6)
            sanitized = output.getvalue()
        with Image.open(io.BytesIO(sanitized)) as check:
            check.load()
            if check.getexif():
                raise ValueError("metadata removal verification failed")
            if check.width * check.height > MAX_IMAGE_PIXELS:
                raise ValueError("sanitized image exceeds the safe import limit")
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValueError("image exceeds Pillow decompression safety limits") from None
    except (OSError, SyntaxError) as exc:
        raise ValueError("image content is corrupt or cannot be decoded") from exc
    return sanitized, suffix, expected_format, clean.width, clean.height


def validate_rows(rows: list[dict]) -> list[dict]:
    if not rows:
        raise ValueError("No authorized source records")
    prepared, seen_ids = [], set()
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"CSV row {index} is invalid")
        normalized = {}
        for key in FIELDS:
            value = row.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"CSV row {index} is missing {key}")
            if len(value) > (4096 if key in {"source_url", "image_url"} else 2048):
                raise ValueError(f"CSV row {index} field {key} is too long")
            normalized[key] = value.strip()
        if normalized["source_id"] in seen_ids:
            raise ValueError("duplicate source_id in authorization CSV")
        seen_ids.add(normalized["source_id"])
        if normalized["license"] not in ALLOWED:
            raise ValueError("unapproved license; only exact CC0-1.0 or CC-BY-4.0 is accepted")
        if normalized["license_url"].rstrip("/") != LICENSE_URLS[normalized["license"]].rstrip("/"):
            raise ValueError("license URL does not match declared license; manual review required")
        for key in ("source_url", "image_url", "license_url"):
            public_https(normalized[key])
        requested_url = normalized["image_url"]
        normalized["image_url"] = normalize_if_inaturalist(requested_url)
        normalized["requested_image_url"] = requested_url
        # Validate the exact URL that will actually be downloaded.
        public_https(normalized["image_url"])
        prepared.append(normalized)
    return prepared


def _download(opener, url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "BeekeeperMonitor-AuthorizedResearch/1.0"})
    try:
        with opener.open(request, timeout=20) as response:
            content_type = response.headers.get_content_type()
            if content_type not in MIME_FORMATS:
                raise ValueError("source returned an unsupported image MIME type")
            data = response.read(MAX_DOWNLOAD_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("authorized source could not be fetched; URL omitted") from exc
    if not 0 < len(data) <= MAX_DOWNLOAD_BYTES:
        raise ValueError("image exceeds 10 MB or is empty")
    return data, content_type


def import_candidates(input_path: str | Path, output_root: str | Path, *, limit: int = 50) -> dict:
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError("limit must be 1..500")
    with Path(input_path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError("Missing required input CSV columns")
        rows = list(reader)
    prepared = validate_rows(rows[:limit])
    root_input = Path(output_root).expanduser()
    root_input.mkdir(parents=True, exist_ok=True)
    root = root_input.resolve(strict=True)
    manifest = root / "licenses.csv"
    if manifest.exists():
        raise FileExistsError("Existing manifest found: refusing to overwrite")
    candidate_dir = root / "unreviewed"
    if candidate_dir.is_symlink():
        raise ValueError("unreviewed output directory must not be a symbolic link")
    candidate_dir.mkdir(mode=0o700, exist_ok=True)
    candidate_dir = candidate_dir.resolve(strict=True)
    candidate_dir.relative_to(root)

    opener = urllib.request.build_opener(NoRedirect())
    accepted, seen_content, created_paths = [], set(), []
    manifest_created = False
    try:
        for row in prepared:
            source_bytes, mime = _download(opener, row["image_url"])
            clean_bytes, suffix, image_format, width, height = sanitize_image(source_bytes, mime)
            source_digest = hashlib.sha256(source_bytes).hexdigest()
            digest = hashlib.sha256(clean_bytes).hexdigest()
            if digest in seen_content:
                continue
            seen_content.add(digest)
            destination = candidate_dir / (digest + suffix)
            if destination.exists():
                raise FileExistsError("candidate destination already exists; refusing to overwrite")
            try:
                with destination.open("xb") as target:
                    created_paths.append(destination)
                    target.write(clean_bytes)
                    target.flush()
                    os.fsync(target.fileno())
            except Exception:
                # Never remove a pre-existing file when exclusive creation fails.
                if destination in created_paths:
                    try: destination.unlink()
                    except FileNotFoundError: pass
                    created_paths.remove(destination)
                raise
            try: os.chmod(destination, 0o600)
            except OSError: pass
            accepted.append({
                **row, "image_path": "unreviewed/" + destination.name,
                "source_sha256": source_digest, "sha256": digest,
                "image_format": image_format, "width": width, "height": height,
                "exif_removed": "true",
            })
        try:
            with manifest.open("x", newline="", encoding="utf-8") as stream:
                manifest_created = True
                writer = csv.DictWriter(stream, fieldnames=OUTPUT)
                writer.writeheader()
                writer.writerows(accepted)
                stream.flush()
                os.fsync(stream.fileno())
            try: os.chmod(manifest, 0o600)
            except OSError: pass
        except Exception:
            if manifest_created:
                try: manifest.unlink()
                except FileNotFoundError: pass
            raise
    except Exception:
        for path in created_paths:
            try: path.unlink()
            except OSError: pass
        raise
    return {
        "downloaded": len(accepted), "candidate_directory": "unreviewed",
        "manifest": "licenses.csv", "training_approved": 0,
        "metadata_stripped": True,
        "notes": "Images remain unreviewed; this import does not approve ownership, taxonomy, annotations or training use.",
    }


def main() -> int:
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV of individually reviewed and authorized images")
    parser.add_argument("--output", default="datasets/hornet")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    try:
        result = import_candidates(args.input, args.output, limit=args.limit)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("No model training or training approval was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
