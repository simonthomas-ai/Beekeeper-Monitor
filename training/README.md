# KI-Training mit echten Daten

Diese Trainingspipeline erstellt **einen Objektdetektor für sieben Klassen**, nicht sechs unabhängig validierte Modelle. Ein Objektdetektor kann nicht jede imkerliche Aufgabe lösen: Schwarmvorhersage und Brutbewertung benötigen gegebenenfalls andere Architekturen sowie zeitliche und weitere Kontextdaten.

## Architektur- und Feldvalidierungsplan

Der Vergleich von Ein-Stufen-YOLO und einer möglichen zweistufigen Detektor-/Crop-Klassifikator-Pipeline, die Bewertung der verfügbaren Quellen und die Feldabnahmekriterien sind in [DETECTION-ARCHITECTURE-REVIEW-2026-11-21.md](DETECTION-ARCHITECTURE-REVIEW-2026-11-21.md) dokumentiert. Der zweistufige Ansatz wird erst mit echten, freigegebenen Crop-Daten umgesetzt.

## Voraussetzungen
- Echte, rechtlich nutzbare Bilder jeder Klasse mit manuell geprüften Begrenzungsrahmen im YOLO-Format.
- Nachvollziehbare Herkunft und Lizenz für jede Datenquelle sowie getrennte SHA-256-Bindung jeder Bilddatei und ihrer exakt zugehörigen YOLO-Labeldatei im Provenienzmanifest.
- Getrennte Trainings-, Validierungs- und Testdaten, möglichst nach Bienenstand, Datum und Kamera getrennt, um Datenüberschneidungen zu vermeiden.
- Jede Quelldatei wird vor dem Training auf tatsächliches JPEG-/PNG-/WebP-Format, vollständige Dekodierbarkeit, Einzelbildinhalt und sichere Bildabmessungen geprüft.
- iNaturalist-Bildquellen werden für die Sichtprüfung auf die größte gehostete Original-Variante normalisiert (maximal 2048 px Kantenlänge; nicht zwingend das Kamera-Original). Die tatsächlichen Pixelmaße werden in der Prüfoberfläche angezeigt und beim autorisierten Import protokolliert. Quadratische 75-px-Thumbnails werden nicht als Trainingsbilder akzeptiert.
- Die iNaturalist-Kandidatenaufnahme strebt 1.000 unterschiedliche Beobachtungen an: jeweils 200 für Asiatische Hornisse, Europäische Hornisse, Honigbiene, Hummeln und Wespen. Bei Hummeln und Wespen bleiben beide wissenschaftlichen Taxa getrennt; die Gruppen-Zuordnung dient ausschließlich der balancierten Stichprobenplanung. Nicht erreichbare Quoten werden als Datenlücke ausgewiesen.
- Der Trainingslauf protokolliert feste Seed-, Determinismus-, Batch-, Worker- und Early-Stopping-Einstellungen zur Reproduzierbarkeit.
- Genügend Beispiele je Klasse zur Leistungsbewertung. Das Skript prüft lediglich eine minimale, nicht leere Datenabdeckung – **keine wissenschaftlich ausreichende Datenmenge**.
- Ausreichende Rechenleistung. Kostenlose GitHub-Actions-Runner sind **kein verlässlicher Ersatz für GPU-Training**.

## Verwendung
```sh
python -m pip install -r training/requirements-training.txt
python training/train.py --validate-only

# Erst nach Rechteprüfung von Trainer, Checkpoint und Daten sowie einer
# bestätigten vollständigen Datensatzvalidierung:
Get-FileHash .\models\yolo11n.pt -Algorithm SHA256
python training/train.py --pretrained-model .\models\yolo11n.pt --pretrained-model-sha256 REPLACE_WITH_SHA256 --pretrained-model-source-url https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt --accept-agpl --epochs 60 --device 0 --batch 16 --workers 4 --seed 42
```

Fehlen echte Bilder, passende Labeldateien oder stimmen deren gespeicherte SHA-256-Werte nicht, schlägt die Prüfung absichtlich fehl. Es werden weder erfundene Bilder noch Platzhaltergewichte, angebliche 99 % Erkennungsgenauigkeit oder fingierte Testberichte erzeugt.

Vor reproduzierbarer Erkennung müssen die Modelldateien auf ihre Nutzungsrechte geprüft, in ein für Mobilgeräte/Browser geeignetes Format umgewandelt, per Prüfsumme abgesichert und unabhängig bewertet werden. Ungeprüfte Datensatzbilder dürfen nicht veröffentlicht werden.
