#!/usr/bin/env python3
"""Erstellt einen vorsichtigen Freigabebericht aus Checkliste und CI-Status."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs" / "FREIGABE-CHECKLISTE.md"


def render(source: str, checks: dict[str, str]) -> str:
    passed = len(re.findall(r"(?m)^- \[x\] ", source))
    open_items = len(re.findall(r"(?m)^- \[ \] ", source))
    if passed + open_items == 0:
        raise ValueError("Keine Freigabe-Checklistenpunkte gefunden")
    rows = ["| Prüfung | CI-Ergebnis |", "|---|---|"]
    for name, value in checks.items():
        if value not in {"success", "failure", "cancelled", "skipped", "unknown"}:
            value = "unknown"
        rows.append(f"| {name} | {value} |")
    return "\n".join([
        "# VespaGuard – Freigabe- und Prüfnachweis",
        "",
        "**Freigabestatus: GESPERRT – keine automatische Freigabe.**",
        "",
        f"- In der Checkliste markierte historische Nachweise: **{passed}**.",
        f"- Offene Freigabepunkte: **{open_items}**.",
        "- Historische Häkchen sind keine Aussage über den aktuellen Commit.",
        "- Erfolgreiche CI-Tests sind keine Feldvalidierung, DSGVO-Zertifizierung oder KI-Modellfreigabe.",
        "",
        "## Aktuelle CI-Prüfergebnisse (dieser Lauf)",
        "",
        *rows,
        "",
        "## Verbindliche offene Entscheidungen",
        "",
        "- Betreiberidentität, Impressum, Rechtsgrundlagen und Hosting verifizieren.",
        "- Reale Hardware-, Restore- und Feldtests nachweisen.",
        "- Bild-/Modellrechte, unabhängige Modellvalidierung und Fehlerraten nachweisen.",
        "- Öffentliche Veröffentlichung benötigt eine gesonderte ausdrückliche Freigabe.",
        "",
        "Details: [Freigabe-Checkliste](docs/FREIGABE-CHECKLISTE.md).",
        "",
    ])


def main() -> None:
    source = CHECKLIST.read_text(encoding="utf-8")
    checks = {
        "Qualitätsprüfung": os.environ.get("QUALITY_STATUS", "unknown"),
        "Validierung": os.environ.get("VALIDATION_STATUS", "unknown"),
        "Browser-Integration im Gesamttest": os.environ.get("BROWSER_STATUS", "unknown"),
    }
    result = render(source, checks)
    print(result)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(result)


if __name__ == "__main__":
    main()
