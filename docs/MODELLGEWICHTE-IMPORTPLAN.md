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
