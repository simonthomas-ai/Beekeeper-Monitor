# Sicherheitsnachtrag: experimentelle ONNX-Runtime bleibt gesperrt

Stand: 26.11.2026

## Befund

Die nicht in die PWA eingebundene Datei `camera-onnx-runtime.js` enthielt einen dynamischen Loader für
`onnxruntime-web` von `cdn.jsdelivr.net` sowie einen externen WASM-Pfad. Die statischen PWA- und
Browserprüfungen bestätigen, dass die Datei nicht von `index.html`, dem Service Worker oder dem
Pages-Staging geladen wird. Der Loader war damit derzeit nicht Teil des normalen PWA-Laufwegs, stellte
aber eine vermeidbare Remote-Code-Ausführungsmöglichkeit dar, falls die Datei versehentlich später
eingebunden würde.

## Änderung

- Der Runtime-Loader schlägt jetzt ausdrücklich fehl und lädt weder JavaScript noch WASM aus einem CDN.
- Die Statusformulierungen behaupten keine aktive oder freigegebene KI.
- `scripts/test_static.py` prüft die Abwesenheit des CDN-Loaders und der Aktivierungsbehauptung.
- Die PWA bleibt ohne Modellgewichte und ohne Inferenzruntime.

## Voraussetzungen für eine spätere Reaktivierung

Eine spätere Runtime darf erst nach separater Freigabe wieder eingebunden werden: lokal gebündelte und
exakt gepinnte Runtime samt WASM-Dateien, überprüfte Hashes und Lizenzen, nachvollziehbare Modellrechte,
passender ONNX-I/O-Vertrag, unabhängige Holdout-Auswertung sowie Browser- und Zielgeräteprüfungen.
Eine bloße CDN-Versionsnummer oder ein Modell-SHA-256 ersetzt diese Nachweise nicht.

Es wurden keine Modelle heruntergeladen, keine Trainingsdaten übernommen und kein Deployment ausgelöst.
