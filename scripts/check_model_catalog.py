#!/usr/bin/env python3
"""Offline-only model inventory contract: never downloads or deserializes weights."""
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "models" / "candidates.json"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def validate(data):
    if data.get("schema_version") != 1 or data.get("status") != "candidates_only_no_execution":
        raise ValueError("Model catalog must be explicitly non-deployable")
    models = data.get("models")
    if not isinstance(models, list) or not models:
        raise ValueError("No models")
    ids = set()
    tasks = set()
    rows = []
    for model in models:
        mid = model.get("id")
        if not isinstance(mid, str) or not re.fullmatch(r"[a-z0-9-]+", mid) or mid in ids:
            raise ValueError("Invalid or duplicate model ID")
        ids.add(mid)
        upstream = model.get("upstream")
        if not isinstance(upstream, str) or not REPO.fullmatch(upstream):
            raise ValueError("Invalid upstream repository")
        path = model.get("path")
        if not isinstance(path, str) or path.startswith("/") or any(p in ("", ".", "..") for p in path.split("/")):
            raise ValueError("Unsafe model path")
        fmt = model.get("format")
        if fmt not in ("onnx", "pt") or not path.endswith("." + fmt):
            raise ValueError("Unrecognized model format")
        if type(model.get("bytes")) is not int or not 0 < model["bytes"] < 500_000_000:
            raise ValueError("Invalid model size")
        if not isinstance(model.get("git_blob"), str) or not HEX40.fullmatch(model["git_blob"]):
            raise ValueError("Missing Git blob fingerprint")
        commit = model.get("commit")
        if commit is not None and (not isinstance(commit, str) or not HEX40.fullmatch(commit)):
            raise ValueError("Invalid pinned commit")
        if "sha256" in model or "license_approved" in model:
            raise ValueError("Unverified hashes and licenses must not be invented")
        task = model.get("task")
        if task not in {"hornet_detection", "varroa_sticky_board", "varroa_on_bee"}:
            raise ValueError("Unknown model task")
        tasks.add(task)
        rows.append((mid, task, fmt, upstream, path, "pinned" if commit else "commit missing"))
    if tasks != {"hornet_detection", "varroa_sticky_board", "varroa_on_bee"}:
        raise ValueError("Required distinct model tasks missing")
    return rows


def main():
    rows = validate(json.loads(CATALOG.read_text(encoding="utf-8")))
    lines = ["## Gemeinsame Modellkandidaten-Prüfung (ohne Gewichtsausführung)", "",
             "| Modell | Aufgabe | Format | Herkunft | Versionsstand |",
             "|---|---|---|---|---|"]
    for mid, task, fmt, upstream, path, pin in rows:
        lines.append(f"| {mid} | {task} | {fmt} | {upstream}: \`{path}\` | {pin} |")
    lines += ["", "**Alle Modelle gesperrt:** Keine Binärgewichte geladen; kein SHA-256 der Downloadbytes, keine Lizenzfreigabe, keine Inferenz und keine Feldvalidierung.",
              "Ein erfolgreicher Katalogtest beweist ausschließlich die konsistente Kandidatenregistrierung.", ""]
    output = "\n".join(lines) + "\n"
    print(output)
    import os
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(output)


if __name__ == "__main__":
    main()
