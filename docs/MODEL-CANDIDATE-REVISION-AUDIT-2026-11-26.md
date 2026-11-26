# Modellkandidaten: unveränderliche Quellrevisionen und Rechtevorbehalt

**Auditdatum:** 2026-11-26  
**Status:** Metadatenprüfung; keine Gewichte heruntergeladen, keine Inferenz und keine Freigabe.

## Prüfumfang

Für die sechs bereits registrierten Kandidaten wurden die GitHub-Repository-Metadaten, der jeweilige Commit-Tree und der Eintrag des Modellpfads geprüft. Die vorhandene Git-Blob-ID und die Dateigröße stimmten für jeden Pfad mit dem Katalog überein. Für die vier zuvor nicht gepinnten Einträge wurde der zum Prüfzeitpunkt aktuelle Default-Branch-Commit als unveränderliche Referenz eingetragen.

Eine Git-Blob-ID ist eine Git-Objekt-ID (SHA-1 über das Git-Objektformat), **kein SHA-256 der heruntergeladenen Modellbytes**. Es wurden keine Binärdateien heruntergeladen oder deserialisiert. Die Pins belegen eine reproduzierbare Quellrevision und einen passenden Tree-Eintrag, nicht Modellintegrität zur Laufzeit, Modellleistung oder Nutzungsrechte.

## Revisionsgebundene Kandidaten

| Kandidat | Upstream-Repository | Commit | Modellpfad | Git-Blob | Größe |
|---|---|---|---|---|---:|
| hornet3000-yolov8s-onnx | [vespCV/hornet3000](https://github.com/vespCV/hornet3000) | `78f51980ee99e45748e78e54dd1312cff846a5ac` | `yolov8sModel/best.onnx` | `97fb748affc642238c1135768a53098f594de0d1` | 44,737,849 |
| hornet3000-yolov10n | [vespCV/hornet3000](https://github.com/vespCV/hornet3000) | `78f51980ee99e45748e78e54dd1312cff846a5ac` | `yolov10nModel/weights/best.pt` | `5c4481640f213fabd61b40edf8b05fa13822fe45` | 5,779,236 |
| vespcv-yolo11 | [vespCV/vespcv](https://github.com/vespCV/vespcv) | `a14b2d356355aad48f36c336f7eaaf344ba9b09f` | `models/yolo112025-04-23default_e200_p20_b-1_augment/weights/best.pt` | `69d6e77e25d17907d1b21d807449313b925845f7` | 19,174,547 |
| vespai-yolov5 | [andrw3000/vespai](https://github.com/andrw3000/vespai) | `004f3d8930d19affd04f5d112224107c5d81eec4` | `models/yolov5-params/yolov5s-21all.pt` | `83164c4e9714fee9e60d1e67fa4c9c2568674b7b` | 14,369,205 |
| varrodetector | [jodivaso/varrodetector](https://github.com/jodivaso/varrodetector) | `31c2cebd289ebfd558153d73ccc52c05f76067d8` | `model/weights/best.pt` | `3ae15dc3efc69376d7c6a6f0730aa3e91d559768` | 9,596,067 |
| gratheon-varroa | [Gratheon/models-varroa-on-bee](https://github.com/Gratheon/models-varroa-on-bee) | `ec7488ab85524a2ce897e16491ef5ab96c4bf06b` | `yolo11n.pt` | `45b273b46165267f2d4c90df94468b547f43cf67` | 5,613,764 |

## Beobachtete Repository-Lizenzdateien

Die folgenden Angaben beschreiben ausschließlich die im jeweiligen Repository vorhandene `LICENSE`-Datei zum Prüfzeitpunkt. Sie beweisen **nicht**, dass genau diese Lizenz auf die konkrete Modellgewichtedatei, die Trainingsbilder, Annotationen oder abgeleitete Artefakte anwendbar ist.

| Repository | Beobachteter Repository-Lizenztext | Offene Frage |
|---|---|---|
| vespCV/hornet3000 | GPL-3.0 | Geltung für jedes konkrete Gewicht und Trainingsmedium separat belegen |
| vespCV/vespcv | GPL-3.0 | Geltung für konkretes Gewicht und Datensatz separat belegen |
| andrw3000/vespai | CC BY-NC-SA 4.0; Lizenzdatei nennt zusätzlich AGPL-3.0 für enthaltenen Modellcode | Nicht-kommerzielle Bedingung beachten; Gewicht-/Datensatzrechte separat klären |
| jodivaso/varrodetector | AGPL-3.0 | Geltung für konkretes Gewicht und Trainingsdaten separat belegen |
| Gratheon/models-varroa-on-bee | AGPL-3.0 | Geltung für konkretes Gewicht und Trainingsdaten separat belegen |

## Freigabestatus und nächste Nachweise

Alle sechs Einträge haben in `models/candidates.json` ausdrücklich `review_status: rights_and_runtime_pending`. Die CI erzwingt nun für jeden Kandidaten einen vollständigen 40-stelligen Commit-Pin und verweigert fehlende Pins, einen anderen Freigabestatus oder Aktivierungs-/Lizenzfreigabefelder.

Vor irgendeiner Übernahme sind weiterhin erforderlich:

1. Autoritative Erklärung der Rechte am konkreten Gewicht und seiner Trainingsdaten.
2. Vollständige Datensatzherkunft einschließlich Einzelbildlizenzen, Attributionen und Nutzungszweck.
3. Download in isolierter Umgebung, tatsächlicher SHA-256, Dateiformat und Integritätsprüfung.
4. Sichere Modellinspektion und bestätigte Ein-/Ausgabe-/Klassenreihenfolge.
5. Unabhängige Holdout- und Hardwarevalidierung mit Fehlalarm-/Auslassungsmetriken.

Bis dahin bleiben sämtliche Kandidaten reine Metadaten. Kein Kandidat darf in den produktiven Kamera- oder Alarmweg gelangen.
