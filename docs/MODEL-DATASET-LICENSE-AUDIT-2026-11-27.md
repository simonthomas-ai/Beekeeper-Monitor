# Modell- und Datensatz-Lizenzprüfung – 27.11.2026

## Umfang und Aussagegrenzen

Geprüft wurden ausschließlich öffentliche Lizenzdateien, README-/Konfigurationsdateien und Git-Baum-Metadaten an den unten angegebenen unveränderlichen Upstream-Commits. Es wurden keine Modellgewichte, Datensatzarchive, Fotos oder Attributionsdateien heruntergeladen oder ausgeführt. Die Prüfung bestätigt die im jeweiligen Quellprojekt veröffentlichten Erklärungen; sie ist keine juristische Freigabe und keine unabhängige Prüfung der Rechte einzelner Bilder.

Die sechs Kandidaten in `models/candidates.json` des Beekeeper-Monitor stehen weiterhin auf `rights_and_runtime_pending` und sind deaktiviert. Der zusätzliche Waspinator-Kandidat steht im deaktivierten BeeKeeper3000-Fähigkeitskatalog (PR #110, Draft).

## Kandidaten im Beekeeper-Monitor

| Kandidat | Gepinnte Quelle | Lizenzdatei am Pin | Aufgaben-/Datenbefund | Freigabe |
|---|---|---|---|---|
| Hornet3000 YOLOv8s / YOLOv10n | [vespCV/hornet3000 @ 78f51980](https://github.com/vespCV/hornet3000/tree/78f51980ee99e45748e78e54dd1312cff846a5ac) | [LICENSE](https://github.com/vespCV/hornet3000/blob/78f51980ee99e45748e78e54dd1312cff846a5ac/LICENSE): GPL-3.0 | README nennt waarnemingen.nl/Observation.org mit „alle deelbare licenties“ und einen Kaggle-Datensatz. Es wurde kein per-Bild-Provenienz-/Attributionsmanifest am Pin nachgewiesen. README-Zielwert 95 % Accuracy und höchstens 5 % False Positives ist eine Projektzielangabe, kein unabhängiger Benchmark. | Gesperrt |
| VespCV YOLO11 | [vespCV/vespcv @ a14b2d35](https://github.com/vespCV/vespcv/tree/a14b2d356355aad48f36c336f7eaaf344ba9b09f) | [LICENSE](https://github.com/vespCV/vespcv/blob/a14b2d356355aad48f36c336f7eaaf344ba9b09f/LICENSE): GPL-3.0 | `config/data.yaml` nennt fünf Klassen (`amel`, `vcra`, `vespsp`, `vvel`, `vzon`). In den geprüften README-/Konfigurationsdateien wurde kein per-Bild-Rechte-/Provenienzmanifest gefunden. Der Klassenvertrag ist nicht automatisch mit dem Monitor-Klassenvertrag identisch. | Gesperrt |
| VespAI YOLOv5 | [andrw3000/vespai @ 004f3d89](https://github.com/andrw3000/vespai/tree/004f3d8930d19affd04f5d112224107c5d81eec4) | [LICENSE](https://github.com/andrw3000/vespai/blob/004f3d8930d19affd04f5d112224107c5d81eec4/LICENSE): Repository-Erklärung CC BY-NC-SA 4.0; darin enthaltene Modellcode-Komponente AGPL-3.0 | README beschreibt Rohlabels aus Plainsight und Gewichte über mehrere Datensätze, aber kein maschinenlesbares per-Bild-Rechte-/Provenienzmanifest. Die NC-/SA-Bedingungen schließen eine ungeprüfte kommerzielle oder beliebige Weitergabe aus. | Gesperrt |
| Varrodetector | [jodivaso/varrodetector @ 31c2cebd](https://github.com/jodivaso/varrodetector/tree/31c2cebd289ebfd558153d73ccc52c05f76067d8) | [LICENSE](https://github.com/jodivaso/varrodetector/blob/31c2cebd289ebfd558153d73ccc52c05f76067d8/LICENSE): AGPL-3.0 | README beschreibt ein YOLO-Nano-Modell, trainiert auf hunderten Bildern, nennt aber kein vollständiges per-Bild-Datensatzrechte- oder Provenienzmanifest. Externe Beispielbilder/Handbücher sind kein Nachweis der Trainingsdatenrechte. | Gesperrt |
| Gratheon Varroa-on-bee | [Gratheon/models-varroa-on-bee @ ec7488ab](https://github.com/Gratheon/models-varroa-on-bee/tree/ec7488ab85524a2ce897e16491ef5ab96c4bf06b) | [LICENSE](https://github.com/Gratheon/models-varroa-on-bee/blob/ec7488ab85524a2ce897e16491ef5ab96c4bf06b/LICENSE): AGPL-3.0 | README behauptet Roboflow Universe `varroa-j8231/varroa8k`, Version 1, CC BY 4.0. Das ist eine Upstream-Angabe; ein vollständiges per-Bild-Manifest wurde im geprüften Baum nicht gefunden. Das README berichtet für die Varroa-Klasse P=0,858, R=0,651, mAP50=0,747 und mAP50-95=0,280; diese Zahlen wurden nicht unabhängig reproduziert. | Gesperrt |
| Gratheon-Aufgabe | gleicher Pin | AGPL-3.0 Quellprojekt; Dataset-Angabe CC BY 4.0 | Varroa **auf Bienen** ist fachlich und datentechnisch eine andere Aufgabe als Varroa-Fall auf Klebebrettern. Die beiden Varroa-Kandidaten dürfen nicht als austauschbare Modelle behandelt werden. | Getrennte Freigabe nötig |

## Zusätzlicher Kandidat in BeeKeeper3000

| Kandidat | Gepinnte Quelle | Lizenzbefund | Offene Punkte |
|---|---|---|---|
| Waspinator YOLO26n | [gitDew/waspinator @ 7251be99](https://github.com/gitDew/waspinator/tree/7251be99a69dfc38f82abb062e22a0062ff5c58c) | [LICENSE.txt](https://github.com/gitDew/waspinator/blob/7251be99a69dfc38f82abb062e22a0062ff5c58c/LICENSE.txt): AGPL-3.0; Modellmetadaten nennen ebenfalls AGPL-3.0. | `models/attributions.txt` ist 4.040.560 Bytes groß und wurde nicht zeilenweise geprüft. Kein vollständiges maschinenlesbares per-Bild-Rechte-/Weitergabemanifest verifiziert. README beschreibt automatische Fallen-/Capture-Funktionen; solche Aktorik bleibt ausdrücklich außerhalb einer freigegebenen VespaGuard-Funktion. |

## Technische und rechtliche Trennung

- Eine Lizenz für Repository-Quellcode ist nicht automatisch die Lizenz der Gewichte, Trainingsbilder, Annotationen, externen Abhängigkeiten oder abgeleiteten Gewichte.
- „Shareable“/„teilbare Lizenz“ ist keine konkrete SPDX-Lizenz und kein Ersatz für eine dokumentierte Rechtekette pro Bild.
- CC BY 4.0 erfordert korrekte Attribution und die Prüfung jeder Quelle; CC BY-NC-SA 4.0 enthält zusätzlich Nichtkommerzialitäts- und ShareAlike-Bedingungen.
- GPL-3.0 und AGPL-3.0 haben unterschiedliche Pflichten; insbesondere AGPL-Netzwerkbereitstellung und Weitergabe müssen vor Integration separat rechtlich bewertet werden.
- Ein SHA-256-Hash belegt nur Byte-Identität, nicht Urheberschaft, Lizenz, Erlaubnis zur Modellableitung oder fachliche Qualität.
- Upstream-Metriken und Demo-Videos sind keine unabhängige Feldvalidierung. Es fehlen ein standort-/zeitlich getrennter Holdout, fachlich doppelt geprüfte Annotationen, Konfidenzintervalle und Fehlalarme pro Kamerastunde.

## Verbindliche Sperren und nächste Freigabeschritte

1. Keine Gewichte importieren, laden, konvertieren, trainieren oder aktivieren, solange Rechte und Datenherkunft offen sind.
2. Für jede Bildquelle: unveränderliche Quelle/Revision, Bildhash, konkrete Lizenz/Erlaubnis, Attribution, Nutzungs- und Weitergaberechte sowie getrennte menschliche Rechteprüfung dokumentieren.
3. Für jedes Modell: exakter Gewichts-Hash, Quellrevision, Lizenztext/Evidenz, Preprocessing, Klassenmapping, Tensorvertrag und abgeleitete Modellpflichten prüfen.
4. Für Varroa-Fall und Varroa-auf-Biene getrennte Aufgaben-/Datensatz-/Validierungspläne verwenden.
5. Vor Feldfreigabe unabhängige Standort-/Zeit-Holdouts, Precision, Recall, AP, Fehlalarme pro Kamerastunde, Ausfallraten und fachliche Abnahme nachweisen.

**Ergebnis: Keine der geprüften externen Kandidaten-/Datensatzkombinationen ist für Training, Runtime, Weitergabe oder Feldbetrieb freigegeben.** Diese Datei dokumentiert die Quellangaben und Lücken; sie ersetzt keine Rechtsberatung oder unabhängige Datenprüfung.
