# Tiefenprüfung und Datenstatus – Beekeeper-Monitor

**Prüfdatum:** 21.11.2026  
**Geprüfter Ausgangsstand:** `main` nach Merge von PR #195, Commit `7d993e49fb53b80d6352fb385cb3ca3bd6274a2f`  
**Gegenstand:** kompletter Git-Baum (Dateiinventar) und vertiefte Prüfung von PWA, lokalen Datenverträgen, Bildquellen, Lizenz-/Provenienz-Gates, Annotation, Training und Deployment.

## 1. Repository-Inventar

Der rekursive Git-Baum enthält 215 Dateien in 15 Verzeichnissen:

| Dateityp | Anzahl |
| --- | ---: |
| Python | 89 |
| Markdown | 47 |
| GitHub-Workflows (YAML) | 38 |
| HTML | 12 |
| CommonJS-Test-/Konfigurationsdateien | 7 |
| JavaScript | 6 |
| JSON | 3 |
| KiCad / CAD | 4 |
| Sonstige (CSS, SVG, Webmanifest, CSV, Lock-/Textdateien) | 9 |

Die größten versionierten HTML-Dateien sind die menschlichen Fotoreview-Galerien und die Wissenschaftsseiten. Sie sind Review-Oberflächen beziehungsweise Dokumentation, keine Trainingsdaten.

## 2. Reale Datenbestände – Status

### Vorhanden
- `sources/catalog.json`: Metadatenkatalog recherchierter Quellen.
- `training/discover_inaturalist_candidates.py` und `training/discover_gbif_media_candidates.py`: Metadatenkandidaten aus externen Biodiversitätsquellen.
- `review/*.html`: manuelle Sichtungsgalerien, keine Trainingsfreigabe.
- `data/model-sources/varrodetector-best.json`: nur Referenz-/Provenienzdatensatz für ein externes Varroa-Modell, keine Gewichte.
- Lizenz-, Herkunfts-, Import-, Review-, Split- und Evaluationsskripte.

### Nicht vorhanden
- Kein freigegebener Ordner `datasets/beekeeper/`.
- Keine vollständige `provenance.jsonl` mit realen Medien und Rechtebelegen.
- Keine fachlich freigegebenen siebenklassigen Bounding-Box-Annotationen.
- Keine freigegebenen Insekten-Modellgewichte und keine unabhängig validierte Modellversion.
- Keine real gemessene Präzision, Recall, Konfusionsmatrix, Fehlalarme pro Stationsstunde oder Feld-Erkennungsqualität.

Der reale Trainingsdaten-Workflow meldet deshalb ausdrücklich: `NOTICE: Missing dataset; model training remains blocked.` Ein erfolgreicher Workflowstatus ist hier ein erfolgreich ausgeführter Prüfjob, nicht die Freigabe eines KI-Modells.

## 3. Datenquellen und Lizenzkette

- iNaturalist- und GBIF-Workflows erzeugen Kandidaten-/Metadaten und sind nicht gleichbedeutend mit einer Freigabe aller verknüpften Fotos.
- Medienlizenz und Datensatz-/Occurrence-Lizenz sind getrennt zu prüfen.
- CC-BY benötigt Urheber- und Attributionstext; eine ungeklärte Versionsangabe oder fehlende Attribution bleibt gesperrt.
- NC-/ND-, unbekannte oder widersprüchliche Rechte werden nicht automatisch für Training freigegeben.
- Öffentliche Sichtbarkeit oder ein Research-Grade-Status ersetzt keine menschliche Artbestimmung und keine Rechteprüfung.

## 4. Optimierung in PR #195 – unveränderliche Bild-/Label-Provenienz

Vorher wurde der Bildinhalt per SHA-256 gebunden, aber nicht der genaue Inhalt der zugehörigen YOLO-Labeldatei. Der Reviewstatus allein konnte deshalb eine spätere Änderung der Bounding Boxes nicht erkennen.

Jetzt verlangt `training/provenance.py` für jeden Bildeintrag zusätzlich:
- `label_path` mit exakt demselben relativen Stamm und Train/Val/Test-Split wie das Bild unter `labels/<split>/`.
- `label_sha256` mit SHA-256 über die tatsächlichen Labelbytes.
- Existenz, Pfadbegrenzung und Symlink-Sperre der Labeldatei.
- Exakt vollständige 1:1-Abdeckung aller Labeldateien im Provenienzmanifest.
- Abbruch bei geänderter Annotation, falschem Split-/Stammpfad sowie zusätzlichen/verwaisten Labeldateien.

Regressionstests prüfen die nachträgliche Änderung eines Labels, einen falschen Labelpfad und ein nicht im Manifest gebundenes Label. Der Gesamttest hat diese neun Provenienztests erfolgreich ausgeführt.

## 5. Öffentliche PWA und rechtliche Veröffentlichung

Die statische PWA, Browser-/WebKit-/iPhone-Tests, lokale Integrationstests und Quellcodeprüfungen sind erfolgreich. Der Pages-Deploy-Workflow blockiert die Veröffentlichung derzeit bewusst mit:

`Rechtstexte enthalten noch Platzhalter; Deployment gesperrt.`

Impressum und Datenschutzhinweise enthalten noch Betreiber-Platzhalter. Sie wurden nicht erfunden oder automatisch ersetzt. Deshalb gilt:
- Der zuletzt erfolgreich veröffentlichte Website-Stand bleibt die zuletzt verifizierte Live-Version.
- Ein neuer Pages-Deploy wird erst freigegeben, wenn die rechtlich verantwortlichen Angaben vollständig und korrekt eingetragen sind.
- Die öffentliche Website und die lokalen Stationsdatenbank bleiben aus Datenschutzgründen getrennt.

## 6. Prüfungen nach PR #195

- PWA-/Integrationsprüfung: erfolgreich.
- Chromium-Browserintegration: erfolgreich.
- Safari WebKit und iPhone-Emulation: erfolgreich.
- Import-/Lizenz-Sicherheitsprüfungen: erfolgreich.
- Europäische Taxonomieprüfung: erfolgreich.
- Provenienz-Regressionssuite: 9 Tests erfolgreich.
- Der separate KI-Trainings-/Annotationsschritt meldet weiterhin fehlende Daten und Annotationen; das Modell bleibt blockiert.
- GitHub Pages: absichtlich blockiert, solange Impressum/Datenschutz Platzhalter enthalten.

PR #195 wurde als Squash-Merge übernommen; Merge-Commit: `7d993e49fb53b80d6352fb385cb3ca3bd6274a2f`.

## 7. Reale Abnahmekriterien

1. Reale Originalmedien aus rechtmäßigen Quellen abrufen; genaue Lizenz, Creator, Attribution, URL, Abrufdatum und SHA-256 je Datei festhalten.
2. Fachkundige Artenbestimmung und Bounding Boxes ergänzen; Labelbytes nach Review mit eigenem SHA-256 binden.
3. Nach Beobachtung, Fotograf, Standort, Kamera und Zeit gruppenweise Train/Validation/Test aufteilen und Duplikat-/Near-Duplicate-Leckage prüfen.
4. Unabhängige, nicht für Training verwendete Testdaten und Feldmessungen erstellen.
5. Modellversion, Laufzeit, Pre-/Postprocessing und ONNX-Konvertierung reproduzierbar versionieren.
6. Pro Klasse Präzision, Recall, Konfusionsmatrix und Konfidenzintervalle sowie falsch-positive/übersehene Tiere pro Stationsstunde berichten.
7. Erst danach Modellmanifest und produktive Stationen freigeben.

## 8. Gesamturteil

Die PWA, lokale Empfangs-/Speicherstrecke, Ereignisverträge, Bildquelleninventur, Lizenzprüfung und Trainingsdaten-Gates sind als Software umgesetzt. Der eigentliche reale siebenklassige Trainingsbestand und die fachlich kontrollierten Labels fehlen; die KI ist nicht freigegeben. Die öffentlichen rechtlichen Betreiberangaben verhindern zusätzlich den nächsten Pages-Deploy. Diese Grenzen sind echte Freigabebedingungen und dürfen nicht durch synthetische Datensätze, Platzhalter oder als Genauigkeit missverstandene CI-Ergebnisse überspielt werden.
