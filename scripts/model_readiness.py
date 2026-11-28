#!/usr/bin/env python3
"""Truthful model-readiness inventory for GitHub Actions (no mock data)."""
from pathlib import Path
import os


def build_report(root: Path) -> tuple[bool, str]:
    base = root / "datasets" / "beekeeper"
    splits = ("train", "val", "test")
    rows = []
    provenance_path = base / "provenance.jsonl"
    provenance_rows = 0
    if provenance_path.is_file():
        provenance_rows = sum(
            1 for line in provenance_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    for split in splits:
        image_dir = base / "images" / split
        label_dir = base / "labels" / split
        images = [
            p for p in image_dir.rglob("*")
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ] if image_dir.is_dir() else []
        labels = list(label_dir.rglob("*.txt")) if label_dir.is_dir() else []
        rows.append((split, len(images), len(labels)))

    inventory_complete = (
        provenance_path.is_file()
        and provenance_rows > 0
        and all(
            images > 0 and labels > 0 and images == labels
            for _, images, labels in rows
        )
        and sum(images for _, images, _ in rows) == provenance_rows
    )
    report = [
        "## KI-Trainingsdaten-Inventar: " + (
            "vollständig gezählt (noch nicht validiert)"
            if inventory_complete else "unvollständig oder inkonsistent"
        ),
        "",
        "| Datensatz | Bilder | Labeldateien |",
        "|---|---:|---:|",
    ]
    report += [f"| {split} | {images} | {labels} |" for split, images, labels in rows]
    report += [
        f"| Provenienzmanifest | {provenance_rows} Bilddatensätze | "
        + ("vorhanden" if provenance_path.is_file() else "fehlt") + " |",
        "",
        "Der Kameradetektor nutzt sieben Klassen: Vespa velutina, Vespa crabro, andere Vespidae, Honigbienen, Hummeln, Schwebfliegen und sonstige Insekten.",
        "Die Trainingsfreigabe verlangt datasets/beekeeper/provenance.jsonl, einen Lizenz- und SHA-256-Nachweis pro Bild, menschlich geprüfte Art-/Boxlabels und split-sichere Beobachtungs-/Fotografen-/Standortgruppen.",
        "Die Zählprüfung verlangt gleiche Bild-/Labelzahlen je Split und einen Provenienzeintrag pro Bild; sie prüft nicht die Inhalte der Einträge.",
        "Diese Inventur belegt weder korrekte Annotationen noch Modellgewichte,",
        "Erkennungsgenauigkeit, SMS-Zustellung oder reale Hardwaretests.",
        "Die Modellfreigabe bleibt bis zu unabhängiger Validierung offen.",
    ]
    return inventory_complete, "\n".join(report) + "\n"


def main(root: Path | None = None) -> int:
    project_root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    inventory_complete, output = build_report(project_root)
    print(output)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(output)
    # The workflow marks this step continue-on-error so the overall software
    # CI can stay green while the summary truthfully records missing AI data.
    return 0 if inventory_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
