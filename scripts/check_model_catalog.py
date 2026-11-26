#!/usr/bin/env python3
"""Offline-only model inventory contract: never downloads or deserializes weights."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "models" / "candidates.json"
HEX40 = re.compile(r"[0-9a-f]{40}\\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\\Z")
ALLOWED_TASKS = {"hornet_detection", "varroa_sticky_board", "varroa_on_bee"}
PENDING_STATUS = "rights_and_runtime_pending"
EXECUTION_FIELDS = {"enabled", "active", "inference_enabled", "deployable"}


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Model catalog must be a JSON object")
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        raise ValueError("Unsupported model catalog schema")
    if data.get("status") != "candidates_only_no_execution":
        raise ValueError("Model catalog must be explicitly non-deployable")
    models = data.get("models")
    if not isinstance(models, list) or not models:
        raise ValueError("No models")

    ids = set()
    tasks = set()
    rows = []
    for model in models:
        if not isinstance(model, dict):
            raise ValueError("Each model candidate must be an object")
        mid = model.get("id")
        if not isinstance(mid, str) or not re.fullmatch(r"[a-z0-9-]+", mid) or mid in ids:
            raise ValueError("Invalid or duplicate model ID")
        ids.add(mid)

        upstream = model.get("upstream")
        if not isinstance(upstream, str) or not REPO.fullmatch(upstream):
            raise ValueError("Invalid upstream repository")

        path = model.get("path")
        if (
            not isinstance(path, str)
            or not path
            or path.startswith("/")
            or "\\\\" in path
            or "\\x00" in path
            or any(part in ("", ".", "..") for part in path.split("/"))
        ):
            raise ValueError("Unsafe model path")

        fmt = model.get("format")
        if not isinstance(fmt, str) or fmt not in ("onnx", "pt") or not path.endswith("." + fmt):
            raise ValueError("Unrecognized model format")
        if type(model.get("bytes")) is not int or not 0 < model["bytes"] < 500_000_000:
            raise ValueError("Invalid model size")
        if not isinstance(model.get("git_blob"), str) or not HEX40.fullmatch(model["git_blob"]):
            raise ValueError("Missing Git blob fingerprint")

        commit = model.get("commit")
        if not isinstance(commit, str) or not HEX40.fullmatch(commit):
            raise ValueError("Every model candidate requires an immutable 40-character commit pin")
        if model.get("review_status") != PENDING_STATUS:
            raise ValueError("Every candidate must remain explicitly rights/runtime pending")
        if any(key in model for key in EXECUTION_FIELDS | {"sha256", "license_approved"}):
            raise ValueError("Candidate catalog must not contain execution or unverified approval fields")

        task = model.get("task")
        if not isinstance(task, str) or task not in ALLOWED_TASKS:
            raise ValueError("Unknown model task")
        tasks.add(task)
        rows.append((mid, task, fmt, upstream, path, commit, model["git_blob"]))

    if tasks != ALLOWED_TASKS:
        raise ValueError("Required distinct model tasks missing")
    return rows


def main():
    rows = validate(json.loads(CATALOG.read_text(encoding="utf-8")))
    lines = [
        "## Gemeinsame Modellkandidaten-Prüfung (ohne Gewichtsausführung)",
        "",
        "| Modell | Aufgabe | Format | Herkunft | Commit (unveränderlich) | Status |",
        "|---|---|---|---|---|---|",
    ]
    for mid, task, fmt, upstream, path, commit, _git_blob in rows:
        lines.append(
            f"| {mid} | {task} | {fmt} | {upstream}: `{path}` | "
            f"`{commit[:12]}` | {PENDING_STATUS} |"
        )
    lines += [
        "",
        "**Alle Modelle bleiben gesperrt:** Keine Gewichtsdatei heruntergeladen, "
        "keine Modellbytes gehasht, keine Lizenzfreigabe, keine Inferenz und keine Feldvalidierung.",
        "Die Git-Blob-ID ist eine Git-Objekt-ID, kein SHA-256-Nachweis der Modellbytes.",
        "Ein erfolgreicher Katalogtest beweist ausschließlich die konsistente, revisionsgebundene Kandidatenregistrierung.",
        "",
    ]
    output = "\\n".join(lines)
    print(output)
    import os
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(output)


if __name__ == "__main__":
    main()
