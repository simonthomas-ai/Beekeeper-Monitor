# Import vorhandener Modellgewichte – sichere Kandidatenliste

Stand: 21.11.2026 · **Kein Modell für den produktiven Einsatz freigegeben.**

Ziel: Bereits trainierte Modelle mit echten Gewichten wiederverwenden, statt Trainingsläufe ohne Datenbasis vorzutäuschen. Die Aufnahme in diese Liste bedeutet **nicht**, dass die Binärdatei heruntergeladen, ausgeführt, konvertiert oder rechtlich freigegeben wurde.

| Modell | Aufgabe | Quelle / Gewichtsdatei | Format | Vorprüfung |
|---|---|---|---|---|
| VarroDetector | Varroa auf Bodeneinlage | [jodivaso/varrodetector](https://github.com/jodivaso/varrodetector), `model/weights/best.pt` | PyTorch .pt | Gewichtsdatei laut vorheriger GitHub-API-Inventur vorhanden; AGPL-3.0-Projektlizenz; nicht importiert |
| Gratheon Varroa on Bee | Varroa auf Bienen | [Gratheon/models-varroa-on-bee](https://github.com/Gratheon/models-varroa-on-bee), `yolo11n.pt` | PyTorch .pt | Gewichtsdatei laut vorheriger GitHub-API-Inventur vorhanden; AGPL-3.0-Projektlizenz; nicht importiert |
| VespAI | Vespa velutina | [andrw3000/vespai](https://github.com/andrw3000/vespai) | Noch zu prüfen | Nicht-kommerzielle Lizenz-/Zugangsbedingungen; keine bestätigte übernehmbare Gewichtsdatei |
| vespCV | Hornissendetektion | [vespCV/vespcv](https://github.com/vespCV/vespcv) | Noch zu prüfen | GPLv3-Projekt; Gewichte und deren Rechte separat prüfen |
| hornet3000 | Hornissendetektion | [vespCV/hornet3000](https://github.com/vespCV/hornet3000) | Noch zu prüfen | Archiviertes Projekt; Gewichte und deren Rechte separat prüfen |

## Verbindlicher Importablauf

1. Exakten Upstream-Commit und den tatsächlichen Download-Endpunkt der Gewichtsdatei ermitteln; Größe, Git-Blob-ID und **SHA-256 der heruntergeladenen Bytes** festhalten.
2. Projektlizenz, Lizenz der konkreten Gewichte, Trainingsdatenrechte, Drittkomponenten und Weitergabepflichten getrennt prüfen. Ungeklärte Rechte bedeuten **Import gesperrt**.
3. Binärdateien nur in isolierter Umgebung mit eingeschränkten Berechtigungen und ohne Geheimnisse verarbeiten. **Keine fremden PyTorch-.pt-Dateien direkt in CI, Browser oder Produktivstation mit uneingeschränktem Pickle laden.**
4. Falls notwendig kontrolliert nach ONNX exportieren. Ausgabeformat, Klassenreihenfolge, Bildvorverarbeitung, Prüfsumme und Modellmanifest mit dem vorhandenen Kamera-Adapter abgleichen.
5. Unabhängige Bilder und reale Zielgeräte prüfen. Je Klasse Precision/Recall, Fehlalarme, Latenz und Grenzfälle dokumentieren. Varroa auf Bodeneinlagen ist eine **andere Aufgabe** als Varroa auf Bienen.
6. Bis zur Abnahme ausschließlich experimentelle, **unbestätigte** Detektionen zulassen; keine automatischen Maßnahmen und keine behauptete 99-%-Erkennungsrate.

## Status der Integration

- **Kandidaten identifiziert:** ja.
- **Echte Binärgewichte im VespaGuard-/BeeKeeper3000-Repository:** derzeit nicht nachgewiesen.
- **Lizenzprüfung der konkreten Gewichte abgeschlossen:** nein.
- **Sicherer ONNX-Export und Laufzeitvertrag bestätigt:** nein.
- **Unabhängige Feldvalidierung:** nein.
- **Produktivfreigabe:** **GESPERRT**.

Weitere Nachweise: [Varroa-Gewichte](VARROA-WEIGHTS-AVAILABILITY.md), [internationale Hornissendetektoren](INTERNATIONAL-HORNET-DETECTORS-2026.md) und [Freigabe-Checkliste](FREIGABE-CHECKLISTE.md).

## Tatsächliche GitHub-Dateiverzeichnisse erneut geprüft (21.11.2026)

Die GitHub-Tree-API bestätigt die folgenden **Dateieinträge** einschließlich Git-Blob-ID. **Git-Blob-SHA-1 ist nicht die SHA-256-Prüfsumme der heruntergeladenen Datei.** Binärdateien wurden bei dieser Prüfung nicht heruntergeladen, ausgeführt oder in VespaGuard kopiert.

| Upstream | Pfad | Bytes | Git-Blob-ID |
|---|---|---:|---|
| jodivaso/varrodetector | `model/weights/best.pt` | 9596067 | `3ae15dc3efc69376d7c6a6f0730aa3e91d559768` |
| Gratheon/models-varroa-on-bee | `yolo11n.pt` | 5613764 | `45b273b46165267f2d4c90df94468b547f43cf67` |
| vespCV/vespcv | `models/yolo112025-04-23default_e200_p20_b-1_augment/weights/best.pt` | 19174547 | `69d6e77e25d17907d1b21d807449313b925845f7` |
| vespCV/hornet3000 | `yolov10nModel/weights/best.pt` | 5779236 | `5c4481640f213fabd61b40edf8b05fa13822fe45` |
| vespCV/hornet3000 | `yolov8sModel/best.onnx` | 44737849 | `97fb748affc642238c1135768a53098f594de0d1` |
| andrw3000/vespai | `models/yolov5-params/yolov5s-21all.pt` | 14369205 | `83164c4e9714fee9e60d1e67fa4c9c2568674b7b` |
| andrw3000/vespai | `models/classifier-runs/basic-model/weights/best.pt` | 1099604 | `8ab278841ed328075509721707acefc69181c432` |

**Korrektur gegenüber der ersten Kandidatenliste:** Für VespAI, vespCV und hornet3000 sind tatsächlich Gewichtsdateien im Upstream-Repository nachweisbar. Bei hornet3000 gibt es auch direkt ONNX-Dateien. Deren Kompatibilität, Herkunft, Lizenzen und Klassen müssen dennoch geprüft werden.

**Nächste technische Priorität:** ONNX-Modell aus hornet3000 anhand eines unveränderlichen Upstream-Commits und einer SHA-256-Dateiprüfung in einer isolierten Prüfstrecke inspizieren; weder produktive Aktivierung noch automatische Veröffentlichung.
