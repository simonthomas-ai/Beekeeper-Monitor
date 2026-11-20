# Manueller ONNX-Export von VarroDetector – bis zur Prüfung gesperrt

Originalquelle: https://github.com/jodivaso/varrodetector (`model/weights/best.pt`, laut GitHub am 20.11.2026 genau 9.596.067 Byte). Die Repository-Angaben nennen AGPL-3.0. **Das belegt noch nicht**, dass Modellgewichte, Trainingsdaten und Abhängigkeiten unter den vorgesehenen Nutzungs- und Weitergabebedingungen verwendet werden dürfen.

## Sicherheitswarnung
PyTorch-Dateien mit der Endung `.pt` können beim Laden unsichere Pickle-Inhalte ausführen. Dieses Exportprogramm **nicht** in GitHub Actions, auf einem Produktionsserver, einem Imkertelefon oder einem vertrauenswürdigen Arbeitsrechner ausführen. Eine Ausführung kommt ausschließlich in einer kurzlebigen, netzwerkisolierten Umgebung **nach manueller Herkunfts- und Rechtsprüfung** infrage.

Der gesonderte GitHub-Workflow darf die Originaldatei als **inaktive Bytes** herunterladen und ihre Integrität prüfen. Das ist **keine** Erlaubnis, die Datei zu deserialisieren oder das Modell auszuführen.

## Vorgehen nach Freigabe
Den SHA-256-Prüfwert der **tatsächlich heruntergeladenen Datei** dokumentieren. Erst danach innerhalb der isolierten Umgebung folgenden Befehl verwenden:

```sh
python3 scripts/export_varroa_onnx.py --weights /reviewed/best.pt \
  --sha256 <64-stelliger-verifizierter-sha256> \
  --reviewed-source-and-license --imgsz 640 \
  --output-record /reviewed/export-record.json
```

Dafür müssen gesondert geprüfte, versionsgebundene Ultralytics-/PyTorch-Abhängigkeiten installiert sein. Der Export ist **keine Freigabe für den Feldeinsatz**. Das ONNX-Modell benötigt geprüfte Ausgabebedeutung, Bildvorverarbeitung, Nachverarbeitung/NMS, unabhängige Milbenzählungen und Kameratests unter realen Bedingungen. Weder ONNX- noch `.pt`-Gewichte sind im Repository eingecheckt.
