# VespaGuard – Audit-Snapshot 27.11.2026, 08:56 CET

Dieser Snapshot dokumentiert den direkt über GitHub geprüften Stand. Er ersetzt ältere Statusabschnitte nicht; historische Artefaktzählungen und ältere Commit-Angaben sind nicht als aktueller Stand zu lesen.

## Geprüfte Hauptzweige

- **Beekeeper-Monitor `main`:** `03b83a2122441bcebc48a273def1ebc0c47c49b5` (07:33:35 UTC). Der Cross-Repository-Pin zeigt auf BeeKeeper3000 `62f36a6f4b4f61a5cd671b63c710c328d9019128`.
- **BeeKeeper3000 `main`:** `62f36a6f4b4f61a5cd671b63c710c328d9019128` (07:28:23 UTC).
- Beide Repositories sind öffentlich; GitHub meldet für beide `main`-Branches `protected=false` und für beide Repositories leere Ruleset-Listen.
- Monitor-Metadaten melden `has_pages=true`; BeeKeeper3000 meldet `has_pages=false`.

## CI – tatsächliche Läufe und Logbefunde

### Beekeeper-Monitor `03b83a21`

- [Ein-Klick-Gesamttest #45959292880](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45959292880): Workflow completed / success; alle drei Jobs (Gesamttest, Bridge-Integration und Field-Dataset-Export) erfolgreich.
- [Repository-Integration #45959292861](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45959292861): success.
- [CodeQL #45959292821](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45959292821): success.
- Der Bridge-Job bestätigt den exakten Partner-Pin `62f36a6f...`, Outbox-/Restart-/HTTP-Recovery-Tests und den Übergang Quelle → Bridge → Monitor-Vertrag → Warnregel. 33 Bridge-Tests: 33 bestanden, 0 fehlgeschlagen.
- Der Field-Dataset-Job bestand 20 BeeKeeper-Datensatzvalidator-Tests, 15 Provenienzkonverter-Tests und 13 Playwright-Exporttests. Verwendet wurden synthetische Fixtures, keine Produktionsbilder.
- **Wichtige Trennung:** Der Gesamtworkflow ist grün, aber die Forschungsprüfungen sind fehlgeschlagen:
  - Inventur: 0 Bilder/0 Labels in train, val und test; Provenienzmanifest fehlt.
  - `TRAINING`: failure – `datasets/beekeeper` fehlt.
  - `ANNOTATIONS`: failure – `training/reviewed-annotations.json` fehlt.
  - Der Gesamttest bleibt erfolgreich, weil Trainings-/Annotationsprüfungen absichtlich nicht die Software-CI blockieren. Das Release-Gate protokolliert weiterhin keine KI-Freigabe.

### BeeKeeper3000 `62f36a6f`

- [Quality Gates #45958691480](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45958691480): success.
- [Windows Station #45958691630](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45958691630): success.
- [CodeQL #45958691623](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45958691623): success.
- [Supply Chain / SBOM #45958691565](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45958691565): success; sechs SBOM-/Vulnerability-Artefakte erzeugt. Diese sind öffentliche Abhängigkeitsberichte, keine Bienenstandbilder oder Modellgewichte.
- Linux-Kamera-Runtime: 86 Tests bestanden. Windows-Kamera-Runtime: 86 Tests gelaufen; zwei plattformspezifische Dateisemantiktests wurden dort erwartungsgemäß übersprungen. Zusätzliche Windows-Medien- und NMEA-Tests liefen erfolgreich.

## Offene Pull Requests in BeeKeeper3000

- [PR #138 – actions/checkout 4.4.0 → 7.0.1](https://github.com/simonthomas-ai/BeeKeeper3000/pull/138): alle sieben sichtbaren Checks erfolgreich. Die Änderung betrifft nur den selbstgehosteten LLM-Council-Workflow. Der eigentliche selbstgehostete Windows-Runner wurde mit dieser PR nicht ausgeführt; Runner-/Node-Kompatibilität ist daher nicht belegt. Nicht ungeprüft mergen.
- [PR #139 – opencv-python-headless 4.14.0.94 → 5.1.0.95](https://github.com/simonthomas-ai/BeeKeeper3000/pull/139): alle 23 sichtbaren Checks erfolgreich. Wegen Major-Upgrade und nicht vollständig inventarisierter nativer Wheel-/FFmpeg-Notices bleibt die PR offen. Das bestehende Review auf der PR dokumentiert diesen Grund.
- Beide PRs basieren noch auf dem älteren Base-SHA `c064465a...`, nicht auf dem aktuellen BeeKeeper3000-`main` `62f36a6f...`; vor einer späteren Freigabe müssen sie aktualisiert und erneut geprüft werden.
- Monitor hat derzeit keine offenen Pull Requests.

## Deployment und Modell-UI

- `.github/workflows/pages.yml` ist ein manueller `verify-only`-Workflow: kein Pages-Upload, keine Deploy-Aktion und keine Veröffentlichung durch diesen Workflow.
- Die Repository-Einstellung bleibt dennoch `has_pages=true`. Eine ältere oder branchbasierte Live-Seite ist mit der verfügbaren API nicht verifiziert; das Sperren des Workflows schaltet eine bestehende Veröffentlichung nicht automatisch ab.
- Die Monitor-`index.html` enthält Live-Kamera-Vorschau und Shadow-Test, aber keinen Modell-Auswahlschalter. `camera-onnx-runtime.js` ist ein deaktivierter Forschungsstub und wird nicht in die PWA eingebunden.
- BeeKeeper3000 `camera/model-capabilities.json` listet acht Fähigkeiten; alle sind `not_validated`, `enabled=false`, `model=null`. Kandidaten bleiben `rights_and_runtime_pending`.

## Sicherheit, Datenschutz und Lizenzen

- Action-Pins, explizite Workflow-Berechtigungen und `persist-credentials: false` werden im Monitor-Audit getestet. CodeQL ist auf den geprüften Hauptzweigen erfolgreich.
- Beide Hauptbranches sind ungeschützt. Der BeeKeeper3000-Hauptzweig enthält nun `scripts/Set-VespaGuardBranchProtection.ps1`: Dry-Run ist Standard, `-Apply` ist ausdrücklich opt-in und prüft erforderliche Checks vor und nach dem Schreiben. Die Schutzregeln wurden in dieser Prüfung nicht aktiviert. Der Branch-Protection-API-Aufruf über die verbundene Integration antwortete mit HTTP 403; keine Umgehung versucht.
- Root-`LICENSE` fehlt in beiden Repositories. BeeKeeper3000 `LICENSES.md` ist ein vorläufiges Inventar.
- Die sechs Monitor-Kandidaten plus Waspinator sind nicht freigegeben. Die dokumentierten Quelllizenzen (u. a. GPL-3.0, AGPL-3.0, CC BY-NC-SA 4.0) beweisen nicht automatisch Rechte an Gewichten, einzelnen Trainingsbildern oder abgeleiteten Modellen. Kein Kandidatengewicht wurde in den aktuellen Git-Bäumen gefunden.
- PWA-Beobachtungen liegen lokal in IndexedDB; optionale Fotos und GPS können darin enthalten sein. JSON-Exporte können solche Inhalte mitnehmen. Der Feld-Dataset-ZIP-Export erzeugt lokal neu kodierte PNG-Kopien und entfernt Bildmetadaten, bleibt nach dem Download aber sensible Datei.
- Stationsevents sind im Bridge-/Receiver-Vertrag metadata-only; Bilder, Audio und exakte GPS-Koordinaten werden nicht weitergeleitet.
- SQLite und IndexedDB sind nicht anwendungsseitig verschlüsselt. Backup-ACLs sind Zugriffsschutz, keine Verschlüsselung. Verschlüsselte Datenträger, Schlüsselverwaltung und Restore auf echter Hardware bleiben erforderlich.
- Historische öffentliche Actions-Artefakte sind in den offenen Issues [#308](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/308), [#310](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/310), [#312](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/312) und [#318](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/318) dokumentiert. Die aktuelle Monitor-Gesamttest-Artefaktliste ist leer. Die Detail-Endpunkte für einzelne alte Artefakte waren in dieser Abfrage nicht verfügbar; deshalb wird hier keine neue aktuelle Gesamtzahl behauptet.

## Einsatzbereitschaft

**Software:** Die geprüften Browser-, Bridge-, Export-, Runtime-, Windows- und SBOM-CI-Jobs sind erfolgreich.

**KI:** Nicht freigegeben. Kein Trainingsbestand, keine fachlich geprüften Annotationen, keine freigegebenen Gewichte, kein unabhängiger Holdout, keine belegten 99 % Erkennungsleistung.

**Feldbetrieb:** Nicht abgenommen. Es fehlen echte Modell-Inferenz auf Zielhardware, Dauerlauf, Strom-/Offline-/Restore-Abnahme, unabhängige Feldmetriken sowie Betreiber-/Datenschutzfreigabe.

## Nächste Schritte

1. Monitor-Pages-Einstellung administrativ prüfen und gegebenenfalls deaktivieren; eine vorhandene Veröffentlichung separat verifizieren.
2. Branch Protection für beide `main`-Zweige mit dem vorhandenen Dry-Run-/Apply-Skript nach lokalem Admin-Preflight aktivieren.
3. Historische öffentliche Artefakte manuell bereinigen und deren Abwesenheit anschließend über GitHub bestätigen.
4. PR #138 auf einem echten kompatiblen selbstgehosteten Runner prüfen; PR #139 erst nach vollständiger Prüfung der nativen Wheel-/FFmpeg-Notices und erneuter CI bewerten.
5. Bild-/Gewichtsrechte und vollständige per-Bild-Provenienz klären; erst danach getrennte Hornissen- und Varroa-Adapter entwickeln.
6. Verschlüsselung und Wiederherstellung auf echter Hardware sowie unabhängige Feldvalidierung durchführen.

Keine privaten Bienenstanddaten, Fotos, GPS-Koordinaten oder Zugangsdaten übertragen. Keine unfreigegebenen Gewichte geladen oder ausgeführt. Kein öffentliches Deployment ausgelöst.
