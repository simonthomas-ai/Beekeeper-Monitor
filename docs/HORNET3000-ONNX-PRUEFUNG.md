# hornet3000 ONNX – technische Vorprüfung (21.11.2026)

**Status: Kandidat nachgewiesen; Import und Inferenz NICHT freigegeben.**

## Verifizierte Upstream-Daten

- Quelle: [vespCV/hornet3000](https://github.com/vespCV/hornet3000), geprüfter `main`-Commit `78f51980ee99e45748e78e54dd1312cff846a5ac` (20.05.2025).
- ONNX: `yolov8sModel/best.onnx`, Git-Tree-Größe **44.737.849 Bytes**, Git-Blob `97fb748affc642238c1135768a53098f594de0d1`.
- Derselbe Blob ist auch unter `yolov8sModel/weights/best.onnx` und `yolov8sModel/best8.onnx` verzeichnet; die Dateinamen allein sind keine unterschiedlichen Modelle.
- Zusätzlich vorhanden: YOLOv10n `yolov10nModel/weights/best.pt`, 5.779.236 Bytes, Git-Blob `5c4481640f213fabd61b40edf8b05fa13822fe45`.
- Die Upstream-README beschreibt die Asiatische Hornisse als Klasse 0 beim früheren Modell und eine YOLOv8s-Modellvariante. **Klassenbelegung des ONNX-Modells nicht ungeprüft aus der alten Modellbeschreibung übernehmen.**
- Eine Git-Blob-ID ist **keine SHA-256-Prüfsumme**. SHA-256 der ONNX-Datei, Eingabe-/Ausgabetensoren, Klassennamen und Lizenz der konkreten Gewichte sind noch nicht geprüft.

## Abgleich mit vorhandener VespaGuard-Software

- [scripts/apiary_onnx_adapter.py](../scripts/apiary_onnx_adapter.py) lädt ONNX nur bei bestandenem Modulmanifest und gibt bewusst **nur Rohtensorformen** zurück, keine bestätigten Arten.
- Der Adapter skaliert Bilder direkt auf die Eingabedimension; ob das ONNX-Modell **Letterbox** erwartet, ist unbekannt. Ein falscher Resize-Modus kann die Detektionsqualität verändern.
- [BeeKeeper3000/camera/model_manifest.py](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/camera/model_manifest.py) verlangt einen echten SHA-256-Hash, überprüfte Nutzungsrechte, explizite Klassen und unterstützte NMS-Ausgabeformate. **Rohes YOLOv8-Ausgabeformat darf nicht ohne Anpassung als NMS-Matrix6 deklariert werden.**
- Ein Modellimport darf erst nach Feststellung von Inputname, Inputshape, Outputnamen/-shapes, Postprocessing, Klassenindex und Lizenz erfolgen.
- Upstream-README nennt einen Trainingsdatensatz von waarnemingen.nl und einen angestrebten Zielwert von 95 %. Das ist **keine eigene Feldvalidierung von VespaGuard**.

## Sichere nächste Schritte

1. Exakte Datei anhand des festgehaltenen Upstream-Commits außerhalb des Produktivsystems abrufen und heruntergeladene Bytes per SHA-256 dokumentieren.
2. ONNX-Graph **ohne Ausführung fremden PyTorch-Codes** in isolierter Umgebung statisch auf Ein-/Ausgaben, Metadaten und Operatoren untersuchen. Bei unklaren oder externen Datenreferenzen abbrechen.
3. Modell-/Datensatz-/Code-Lizenzen separat prüfen und dokumentieren; bei fehlendem Nachweis keine Freigabe.
4. Nur bei passendem Outputformat einen experimentellen, standardmäßig deaktivierten Adapter entwickeln und mit echten, rechtlich nutzbaren Testbildern unabhängig bewerten.
5. Weder produktiven Alarm noch automatisches öffentliches Deployment aktivieren.

**Ergebnis:** ONNX-Binärdatei im Upstream nachgewiesen; Kompatibilität noch nicht bestätigt, Modell nicht importiert.


## Verifizierter ONNX-Graph (GitHub Actions, 21.11.2026)

Prueflauf: https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44937623603
Status: erfolgreich, SHA-256 `1df95cedd08426dc218f8aa9e02667e068c0bda218c29a44032638fab005276f`.
Eingabe: `images` FLOAT `[1,3,640,640]`. Ausgabe: `output0` FLOAT `[1,9,8400]`.
ONNX IR 9, Opset 19, 233 Knoten; keine NMS-Operatoren in der Operatorenliste.
Metadaten `names`: `{0: 'amel', 1: 'vcra', 2: 'vespsp', 3: 'vvel', 4: 'vzon'}`.
Damit ist **Vespa velutina Klasse 3** fuer diese konkrete ONNX-Datei, nicht Klasse 0.
Die neun Ausgabekanaele entsprechen plausibel vier Boxwerten plus fuenf Klassenscores;
die genaue Dekodierung, Koordinatenbehandlung, Schwellwerte und NMS muessen anhand
einer kontrollierten Inferenz geprueft werden. Keine reale Erkennungsleistung nachgewiesen.

Die ONNX-Metadaten nennen `AGPL-3.0 License` (Ultralytics). Das ersetzt keine
Lizenz- und Herkunftspruefung des konkreten Gewichtsartefakts. Kein Produktivbetrieb
oder oeffentlicher Modellvertrieb freigegeben.
