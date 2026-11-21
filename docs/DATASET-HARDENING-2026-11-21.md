# Datensatz-Härtung

## Verbindliche Bild-/Annotationsbindung

Jeder Eintrag in `datasets/beekeeper/provenance.jsonl` muss jetzt sowohl das Bild als auch die dazugehörige YOLO-Labeldatei binden:

- `image_path` und `sha256`: exakter Bildpfad und SHA-256 der Bildbytes.
- `label_path` und `label_sha256`: exakter Labelpfad und SHA-256 der Annotation.
- Der Labelpfad muss denselben relativen Dateistamm und denselben Split wie das Bild verwenden, aber unter `labels/<split>/` liegen.
- Jede Labeldatei muss im Manifest genau einmal vorkommen; zusätzliche oder fehlende Labeldateien blockieren die Freigabe.
- Eine nachträgliche Änderung der Boxen ändert den Hash und blockiert den Trainingslauf, bis die Änderung erneut fachlich geprüft und dokumentiert wurde.

Die Härtung schließt die zuvor dokumentierte Lücke, dass ein Reviewstatus auf `verified` stehen konnte, obwohl sich der tatsächliche Inhalt einer Labeldatei nach dem Review geändert hatte.

## Weitere Datenqualität

Die fünf Kurzklassen werden bei der Aufteilung in die kanonische siebenklassige Modell-Taxonomie überführt. Vespula wird vorläufig als `other_vespidae` eingeordnet und muss fachlich bestätigt werden. Gruppenkennungen dürfen nicht klassenübergreifend auf mehrere Datenteile verteilt werden.

Wikimedia-Commons-Metadaten sind nur Kandidatenhinweise und kein vollständiger Rechtsnachweis. Ein Kandidatennachweis ist keine Lizenzfreigabe.

**Noch offen:** Es liegen weiterhin keine echten freigegebenen Trainingsdaten, vollständigen menschlichen Boxannotationen, Modellgewichte oder unabhängigen Feldtests vor. Nahezu identische Bilder über unterschiedliche Fotografen-/Standortgruppen hinweg benötigen weiterhin zusätzliche visuelle Duplikatprüfung; Gruppenkennungen allein beweisen keine Bildunabhängigkeit.
