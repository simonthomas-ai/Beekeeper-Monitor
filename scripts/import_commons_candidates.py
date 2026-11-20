#!/usr/bin/env python3
"""Download Commons candidates with verifiable license metadata; never auto-approve labels."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://commons.wikimedia.org/w/api.php"
ALLOWED = {"cc0", "cc by 4.0", "cc by 3.0", "cc by 2.0", "public domain"}
CATEGORIES = {
    "velutina": "Category:Vespa_velutina_nigrithorax",
    "crabro": "Category:Vespa_crabro",
}
FALLBACK_CATEGORIES = {"velutina": ["Category:Vespa_velutina"], "crabro": []}
def get_json(params):
    url = API + "?" + urlencode(params)
    with urlopen(Request(url, headers={"User-Agent": "VespaGuardResearchImporter/0.1 (noncommercial research; github.com/simonthomas-ai/Beekeeper-Monitor)"}), timeout=30) as response:
        return json.load(response)
def norm(value):
    return " ".join(str(value or "").lower().replace("-", " ").split())
def allowed(license_name):
    return norm(license_name) in ALLOWED
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--class-name", choices=sorted(CATEGORIES), required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--output", default="data/research-candidates")
    p.add_argument("--download", action="store_true", help="Explicit opt-in to downloading image bytes")
    args = p.parse_args()
    if not 1 <= args.limit <= 100:
        p.error("--limit must be 1..100")
    output = Path(args.output) / args.class_name
    output.mkdir(parents=True, exist_ok=True)
    query = {"action": "query", "generator": "categorymembers", "gcmtitle": CATEGORIES[args.class_name],
             "gcmtype": "file", "gcmlimit": args.limit, "prop": "imageinfo",
             "iiprop": "url|extmetadata|mime|size", "format": "json"}
    payload = get_json(query)
    if 'error' in payload or 'query' not in payload:
        raise RuntimeError('Commons API returned an error or incomplete response')
    entries = []
    seen = set()
    pages = list(payload.get("query", {}).get("pages", {}).values())
    if not pages:
        for category in FALLBACK_CATEGORIES[args.class_name]:
            fallback_query = {**query, "gcmtitle": category}
            fallback = get_json(fallback_query)
            if "error" in fallback or "query" not in fallback:
                raise RuntimeError("Commons fallback API error")
            pages.extend(fallback.get("query", {}).get("pages", {}).values())
            if pages:
                break
    for page in pages:
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        lic = meta.get("LicenseShortName", {}).get("value", "")
        media_url = info.get("url", "")
        mime = info.get("mime", "")
        if not allowed(lic) or mime not in ("image/jpeg", "image/png", "image/webp") or not media_url.startswith("https://"):
            continue
        sha = None
        file_name = None
        if args.download:
            req = Request(media_url, headers={"User-Agent": "VespaGuardResearchImporter/0.1"})
            with urlopen(req, timeout=40) as resp:
                body = resp.read(12_000_001)
            if len(body) > 12_000_000:
                continue
            sha = hashlib.sha256(body).hexdigest()
            if sha in seen:
                continue
            seen.add(sha)
            ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[mime]
            file_name = sha + ext
            (output / file_name).write_bytes(body)
        entries.append({"title": page.get("title"), "source_page": "https://commons.wikimedia.org/wiki/" + page.get("title", "").replace(" ", "_"),
                        "source_url": media_url, "license": lic,
                        "license_url": meta.get("LicenseUrl", {}).get("value", ""),
                        "artist_html": meta.get("Artist", {}).get("value", ""),
                        "credit_html": meta.get("Credit", {}).get("value", ""),
                        "mime": mime, "sha256": sha, "local_file": file_name,
                        "suggested_class": args.class_name, "species_verified": False,
                        "human_approved_for_training": False})
    # A category can contain files but none with an allowed license or MIME type.
    # In that case query the broader category too, rather than stopping at nonempty pages.
    if not entries and FALLBACK_CATEGORIES[args.class_name]:
        for category in FALLBACK_CATEGORIES[args.class_name]:
            if category == query["gcmtitle"]:
                continue
            fallback = get_json({**query, "gcmtitle": category})
            if "error" in fallback or "query" not in fallback:
                raise RuntimeError("Commons fallback API error")
            for page in fallback.get("query", {}).get("pages", {}).values():
                info = (page.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata") or {}
                lic = meta.get("LicenseShortName", {}).get("value", "")
                media_url = info.get("url", "")
                mime = info.get("mime", "")
                if not allowed(lic) or mime not in ("image/jpeg", "image/png", "image/webp") or not media_url.startswith("https://"):
                    continue
                # Download mode must not bypass byte hashing or size checks.
                if args.download:
                    req = Request(media_url, headers={"User-Agent": "VespaGuardResearchImporter/0.1"})
                    with urlopen(req, timeout=40) as resp:
                        body = resp.read(12_000_001)
                    if len(body) > 12_000_000:
                        continue
                    sha = hashlib.sha256(body).hexdigest()
                    if sha in seen:
                        continue
                    seen.add(sha)
                    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[mime]
                    file_name = sha + ext
                    (output / file_name).write_bytes(body)
                else:
                    sha, file_name = None, None
                entries.append({"title": page.get("title"),
                                "source_page": "https://commons.wikimedia.org/wiki/" + page.get("title", "").replace(" ", "_"),
                                "source_url": media_url, "license": lic,
                                "license_url": meta.get("LicenseUrl", {}).get("value", ""),
                                "artist_html": meta.get("Artist", {}).get("value", ""),
                                "credit_html": meta.get("Credit", {}).get("value", ""),
                                "mime": mime, "sha256": sha, "local_file": file_name,
                                "suggested_class": args.class_name, "species_verified": False,
                                "human_approved_for_training": False})
            if entries:
                break
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps({"source": "Wikimedia Commons API", "category": CATEGORIES[args.class_name],
                                   "downloaded": args.download, "items": entries}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(entries)} license-filtered candidates; manual species review required. Manifest: {manifest}")
if __name__ == "__main__":
    main()
