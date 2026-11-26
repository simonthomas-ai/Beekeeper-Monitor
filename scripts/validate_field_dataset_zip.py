#!/usr/bin/env python3
"""Validate a Beekeeper field-image export without importing or training.

This checker intentionally fails closed: an annotation ZIP is not evidence of
image rights, label quality, field suitability or model training eligibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import PurePosixPath
from pathlib import Path
from urllib.parse import urlparse


CLASSES = frozenset({
    "vespa_velutina",
    "vespa_crabro",
    "other_vespidae",
    "apis_mellifera",
    "bombus_spp",
    "syrphidae",
    "other_insect",
})
MAX_IMAGE_BYTES = 8 * 1024 * 1024
PSEUDONYMOUS_LABELER_ID = re.compile(r"^reviewer:[A-Za-z0-9][A-Za-z0-9._:-]{7,79}$")
ALLOWED_ANNOTATION_FIELDS = {
    "image", "labels", "captured_at", "capture_session_id",
    "labeler_id", "review_status", "rights",
}
RIGHTS_BASES = {"CC0-1.0", "CC-BY-4.0", "LicenseRef-ExplicitPermission"}
LICENSE_URLS = {
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
}
ALLOWED_RIGHTS_FIELDS = {
    "source", "basis", "status", "publication_allowed",
    "evidence_url", "attribution", "permission_ref",
}


def _credential_free_https(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return bool(
        parsed.scheme == "https" and parsed.netloc and
        not parsed.username and not parsed.password and
        not parsed.query and not parsed.fragment
    )


def validate_rights(rights: object, line_number: int, errors: list[str]) -> None:
    prefix = f"Zeile {line_number}: rights"
    if not isinstance(rights, dict):
        errors.append(f"{prefix} fehlt oder ist ungültig")
        return
    unknown = sorted(set(rights) - ALLOWED_RIGHTS_FIELDS)
    if unknown:
        errors.append(f"{prefix} enthält nicht unterstützte Felder: {', '.join(unknown)}")

    source = rights.get("source")
    if not isinstance(source, str) or not source.strip() or len(source.strip()) > 200:
        errors.append(f"{prefix}.source muss ein nichtleerer Text bis 200 Zeichen sein")
    elif source.strip().casefold() not in {"eigene feldaufnahme", "own field capture"}:
        if not _credential_free_https(source.strip()):
            errors.append(f"{prefix}.source muss eine HTTPS-URL ohne Zugangsdaten, Query oder Fragment sein")

    basis = rights.get("basis")
    if not isinstance(basis, str) or basis not in RIGHTS_BASES:
        errors.append(f"{prefix}.basis muss CC0-1.0, CC-BY-4.0 oder LicenseRef-ExplicitPermission sein")
    if rights.get("status") != "training_approved":
        errors.append(f"{prefix}.status ist nicht training_approved")

    if "publication_allowed" in rights and (
        type(rights["publication_allowed"]) is not bool or not rights["publication_allowed"]
    ):
        errors.append(f"{prefix}.publication_allowed muss true sein")

    if isinstance(basis, str) and basis in LICENSE_URLS:
        evidence = rights.get("evidence_url")
        if evidence is None:
            errors.append(f"{prefix}.evidence_url fehlt für die gewählte Lizenz")
        elif not _credential_free_https(evidence):
            errors.append(f"{prefix}.evidence_url muss eine HTTPS-URL ohne Zugangsdaten, Query oder Fragment sein")
        elif evidence.rstrip("/") != LICENSE_URLS[basis].rstrip("/"):
            errors.append(f"{prefix}.evidence_url passt nicht zur Rechtebasis")
    elif "evidence_url" in rights and not _credential_free_https(rights["evidence_url"]):
        errors.append(f"{prefix}.evidence_url muss eine HTTPS-URL ohne Zugangsdaten, Query oder Fragment sein")

    if basis == "CC-BY-4.0":
        attribution = rights.get("attribution")
        if not isinstance(attribution, str) or not attribution.strip() or len(attribution.strip()) > 500:
            errors.append(f"{prefix}.attribution ist für CC-BY-4.0 erforderlich (max. 500 Zeichen)")
    if basis == "LicenseRef-ExplicitPermission":
        permission_ref = rights.get("permission_ref")
        if not isinstance(permission_ref, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}", permission_ref.strip()):
            errors.append(f"{prefix}.permission_ref muss eine opake Referenz bis 200 Zeichen sein")


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def iso_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate(zip_path: Path) -> list[str]:
    errors: list[str] = []
    if not zip_path.is_file():
        return [f"ZIP nicht gefunden: {zip_path}"]

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad = archive.testzip()
            if bad:
                errors.append(f"Beschädigte ZIP-Datei: {bad}")
                return errors
            names = archive.namelist()
            if "annotations.jsonl" not in names:
                errors.append("Pflichtdatei annotations.jsonl fehlt")
                return errors

            if len(names) != len(set(names)):
                errors.append("ZIP enthält doppelte Dateinamen")

            image_names: set[str] = set()
            image_hashes: dict[str, str] = {}
            for name in names:
                pure = PurePosixPath(name)
                if name == "annotations.jsonl":
                    continue
                if (
                    pure.is_absolute() or "\\" in name or ".." in pure.parts or
                    len(pure.parts) != 2 or pure.parts[0] != "images" or
                    pure.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}
                ):
                    errors.append(f"Unzulässiger ZIP-Pfad: {name}")
                    continue
                content = archive.read(name)
                if not content:
                    errors.append(f"Leeres Bild: {name}")
                elif len(content) > MAX_IMAGE_BYTES:
                    errors.append(f"Bild größer als 8 MB: {name}")
                digest = hashlib.sha256(content).hexdigest()
                if digest in image_hashes:
                    errors.append(f"Duplizierter Bildinhalt: {name} und {image_hashes[digest]}")
                else:
                    image_hashes[digest] = name
                image_names.add(name)

            try:
                text = archive.read("annotations.jsonl").decode("utf-8")
            except UnicodeDecodeError:
                errors.append("annotations.jsonl ist kein UTF-8-Text")
                return errors

            seen_images: set[str] = set()
            line_count = 0
            for line_number, line in enumerate(text.splitlines(), start=1):
                line_count += 1
                try:
                    record = json.loads(line, object_pairs_hook=_unique_json_object)
                except (json.JSONDecodeError, ValueError) as exc:
                    errors.append(f"Zeile {line_number}: ungültiges JSON oder doppelter Schlüssel ({exc})")
                    continue
                if not isinstance(record, dict):
                    errors.append(f"Zeile {line_number}: Annotation muss ein Objekt sein")
                    continue
                if set(record).difference(ALLOWED_ANNOTATION_FIELDS):
                    errors.append(f"Zeile {line_number}: Annotation enthält nicht unterstützte Felder")
                required = ALLOWED_ANNOTATION_FIELDS - {"labeler_id"}
                if not required.issubset(record):
                    errors.append(f"Zeile {line_number}: Annotation enthält nicht alle Pflichtfelder")
                labeler_id = record.get("labeler_id")
                if labeler_id is not None and (
                    not isinstance(labeler_id, str) or not PSEUDONYMOUS_LABELER_ID.fullmatch(labeler_id)
                ):
                    errors.append(
                        f"Zeile {line_number}: labeler_id muss reviewer:<opaque-id> verwenden"
                    )

                forbidden = {"bbox", "boxes", "location", "gps", "station_id"}
                present_forbidden = sorted(forbidden.intersection(record))
                if present_forbidden:
                    errors.append(f"Zeile {line_number}: nicht unterstützte Felder: {', '.join(present_forbidden)}")

                image = record.get("image")
                if not isinstance(image, str) or image not in image_names:
                    errors.append(f"Zeile {line_number}: unbekannter oder fehlender Bildpfad")
                elif image in seen_images:
                    errors.append(f"Zeile {line_number}: Bild wird mehrfach annotiert: {image}")
                else:
                    seen_images.add(image)

                labels = record.get("labels")
                if not isinstance(labels, list):
                    errors.append(f"Zeile {line_number}: labels muss eine Liste sein")
                else:
                    if len(labels) != len(set(labels)):
                        errors.append(f"Zeile {line_number}: labels enthält doppelte Slugs")
                    unknown = sorted(set(labels).difference(CLASSES))
                    if unknown:
                        errors.append(f"Zeile {line_number}: unbekannte Label-Slugs: {', '.join(map(str, unknown))}")
                    if not all(isinstance(label, str) for label in labels):
                        errors.append(f"Zeile {line_number}: alle Label-Slugs müssen Strings sein")

                if not iso_timestamp(record.get("captured_at")):
                    errors.append(f"Zeile {line_number}: captured_at ist kein ISO-8601-Zeitstempel mit Zeitzone")
                session = record.get("capture_session_id")
                if not isinstance(session, str) or not session.strip() or len(session) > 160:
                    errors.append(f"Zeile {line_number}: capture_session_id fehlt oder ist ungültig")

                if record.get("review_status") != "approved":
                    errors.append(f"Zeile {line_number}: review_status ist nicht approved")

                validate_rights(record.get("rights"), line_number, errors)

            if line_count == 0:
                errors.append("annotations.jsonl ist leer")
            missing_annotations = sorted(image_names.difference(seen_images))
            if missing_annotations:
                errors.append("Bilder ohne Annotation: " + ", ".join(missing_annotations))
    except zipfile.BadZipFile:
        errors.append("Ungültiges ZIP-Archiv")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Prüft ein Beekeeper Feldbild-Export-ZIP")
    parser.add_argument("zip", type=Path, help="Pfad zum .zip-Export")
    args = parser.parse_args()
    errors = validate(args.zip)
    if errors:
        print("BLOCKED: Exportvertrag nicht erfüllt", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("OK: ZIP erfüllt den lokalen Feldbild-Exportvertrag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
