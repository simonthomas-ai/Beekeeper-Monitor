# KI-Training mit echten Daten

Diese Trainingspipeline erstellt **einen Objektdetektor für sieben Klassen**, nicht sechs unabhängig validierte Modelle. Ein Objektdetektor kann nicht jede imkerliche Aufgabe lösen: Schwarmvorhersage und Brutbewertung benötigen gegebenenfalls andere Architekturen sowie zeitliche und weitere Kontextdaten.

## Voraussetzungen
- Echte, rechtlich nutzbare Bilder jeder Klasse mit manuell geprüften Begrenzungsrahmen im YOLO-Format.
- Nachvollziehbare Herkunft und Lizenz für jede Datenquelle sowie getrennte SHA-256-Bindung jeder Bilddatei und ihrer exakt zugehörigen YOLO-Labeldatei im Provenienzmanifest.
- Getrennte Trainings-, Validierungs- und Testdaten, möglichst nach Bienenstand, Datum und Kamera getrennt, um Datenüberschneidungen zu vermeiden.
- Jede Quelldatei wird vor dem Training auf tatsächliches JPEG-/PNG-/WebP-Format, vollständige Dekodierbarkeit, Einzelbildinhalt und sichere Bildabmessungen geprüft.
- Der Trainingslauf protokolliert feste Seed-, Determinismus-, Batch-, Worker- und Early-Stopping-Einstellungen zur Reproduzierbarkeit.
- Genügend Beispiele je Klasse zur Leistungsbewertung. Das Skript prüft lediglich eine minimale, nicht leere Datenabdeckung – **keine wissenschaftlich ausreichende Datenmenge**.
- Ausreichende Rechenleistung. Kostenlose GitHub-Actions-Runner sind **kein verlässlicher Ersatz für GPU-Training**.

## Verwendung
```sh
python -m pip install -r training/requirements-training.txt
python training/train.py --validate-only
python training/train.py --epochs 60 --device 0 --batch 16 --workers 4 --seed 42
```

Fehlen echte Bilder, passende Labeldateien oder stimmen deren gespeicherte SHA-256-Werte nicht, schlägt die Prüfung absichtlich fehl. Es werden weder erfundene Bilder noch Platzhaltergewichte, angebliche 99 % Erkennungsgenauigkeit oder fingierte Testberichte erzeugt.

Vor reproduzierbarer Erkennung müssen die Modelldateien auf ihre Nutzungsrechte geprüft, in ein für Mobilgeräte/Browser geeignetes Format umgewandelt, per Prüfsumme abgesichert und unabhängig bewertet werden. Ungeprüfte Datensatzbilder dürfen nicht veröffentlicht werden.
