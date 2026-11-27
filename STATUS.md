# Aktueller Prüfstand – 27.11.2026 (Nachprüfung nach PR #339)

## Hauptzweige und letzte Änderungen
- Beekeeper-Monitor `main`: `6966c8c2c8b609327ff31f4cf09b5e2fffd6b3ab`; PR #339 ist als reine Statusdokumentation gemergt.
- BeeKeeper3000 `main`: `c59e1a143f96ac81b91156fba5b645294c7129da`; PR #133 pinnt den Monitor-Backup-ACL-Vertrag für Linux-Stationstests.
- Der Monitor pinnt BeeKeeper3000 auf genau `c59e1a143f96ac81b91156fba5b645294c7129da`.

## Aktuelle Post-Merge-CI
**Beekeeper-Monitor – Commit `6966c8c2`:**
- [Ein-Klick-Gesamttest #45936041847](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45936041847): completed / success. Browser, Safari WebKit, iPhone-WebKit-Emulation, Taxonomie, Field-Dataset-Export und Bridge-Integration erfolgreich.
- [CodeQL #45936041947](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45936041947): completed / success.
- Die Artefaktliste des Gesamttests ist leer; der optionale öffentliche Browser-Artefakt-Upload wurde übersprungen.
- Software-CI-Erfolg ist keine KI-Freigabe. Trainingsdaten und fachlich geprüfte Annotationen fehlen weiterhin; KI bleibt blockiert.

**BeeKeeper3000 – Commit `c59e1a14`:**
- [Quality Gates #45927046146](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45927046146): success.
- [Linux station installer validation #45927046082](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45927046082): success.
- [CodeQL #45927046112](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45927046112): success.
- Letzter erfolgreicher Supply-Chain-/SBOM-Lauf: [#45926170707](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45926170707) auf Vorgängercommit `fbea17e4`. Der aktuelle Partner-Commit ändert nur den Linux-Stationstest-Workflow; ein neuer SBOM-Lauf auf `c59e1a14` ist nicht belegt.

## Öffentliche Actions-Artefakte
Neun historische Artefakte wurden erneut über ihre jeweiligen Run-Artefaktlisten geprüft; alle meldeten `expired=false`:
- Fünf alte PWA-Vorschauen: `15124542124`, `15118529028`, `15115678841`, `15115577897`, `15108012720`.
- Vier Review-/CC0-Artefakte: `15108851881`, `15107897872`, `15058597151`, `15058522636`.
- Das Originalbild-Artefakt `15058597151` hat 161.230.685 Bytes.
- Die Inhalte wurden nicht heruntergeladen. Die erneute Einzelprüfung ist in [Issue #318](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/318) und [Issue #312](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/312) kommentiert. Eine Löschaktion ist über die verbundene GitHub-Schnittstelle nicht verfügbar; manuelle Bereinigung bleibt offen.

## Deployment – neue administrative Feststellung
- Repository-Metadaten melden `has_pages=true` für das öffentliche Monitor-Repository.
- `.github/workflows/pages.yml` ist weiterhin `workflow_dispatch`-only; der Deploy-Job ist explizit mit `if: false` gesperrt. In dieser Prüfung wurde kein Deployment ausgelöst.
- `has_pages=true` bedeutet, dass die Repository-Pages-Konfiguration vorhanden ist. Es beweist nicht, welche Inhalte aktuell veröffentlicht sind. Die veröffentlichte Website konnte in dieser Prüfung nicht verlässlich abgerufen werden.
- [Issue #340](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/340) dokumentiert die erforderliche manuelle Prüfung/Deaktivierung unter Settings → Pages.

## Sicherheit, Lizenz und Feldfreigabe
- Beide `main`-Branches melden `protected=false`; beide Ruleset-Listen sind leer. Der Branch-Protection-Endpunkt liefert für die verbundene Integration 403; keine administrative Regel wurde geändert.
- Root-`LICENSE` fehlt in beiden Repositories. BeeKeeper3000-`LICENSES.md` ist ein vorläufiges Inventar, keine Gesamtfreigabe.
- Sechs Monitor-Modellkandidaten bleiben `rights_and_runtime_pending`; keine Modellgewichte liegen in den geprüften Git-Bäumen.
- `datasets/beekeeper/`, vollständige Bild-Provenienz und fachlich geprüfte Annotationen fehlen. Keine unabhängigen Holdout-Metriken, Precision-/Recall-/Fehlalarmraten oder 99-%-Erkennungsleistung nachgewiesen.
- IndexedDB und lokale SQLite-Daten sind nicht zusätzlich anwendungsseitig verschlüsselt. Backup-ACL-Prüfungen ersetzen keine Verschlüsselung.
- BeeKeeper3000 PR #110 bleibt Draft; alle acht Fähigkeiten sind deaktiviert.

**Release-/Feldstatus: BLOCKIERT.** Software-Unit-/Browser-/Bridge-/Export-CI ist auf den genannten Commits erfolgreich. Modell-/Datensatzrechte, Datenbasis, unabhängige Validierung, Verschlüsselung/Wiederherstellung, rechtliche Betreiberfreigabe, Pages-Einstellung und administrative GitHub-Schutzregeln sind nicht abgeschlossen.

Keine privaten Bienenstanddaten, Fotos, GPS-Koordinaten oder Zugangsdaten übertragen. Keine unfreigegebenen Modellgewichte geladen, trainiert oder aktiviert. Kein öffentliches Deployment ausgelöst.

---

---

# Historischer Snapshot – 27.11.2026 (vor PR #338; durch den aktuellen Prüfstand oben ersetzt)

## Hauptzweige und integrierte Änderungen
- Beekeeper-Monitor: Basisstand `b8491b8ed25d5ab7c8028a5d52cc5e760c6fbac1`; PR #336 (öffentliche Testartefakte) und PR #337 (Windows-Backup-ACL-Prüfung) sind gemergt.
- BeeKeeper3000: `c59e1a143f96ac81b91156fba5b645294c7129da`; PR #132 und #133 sind gemergt. PR #133 pinnt den Monitor-Backup-ACL-Vertrag für Linux-Stationstests. Source-Journal-, Kamera-Outbox- und Monitor-Backups prüfen POSIX-Rechte bzw. Windows-NTFS-ACLs vor dem Schreiben. Der Windows-Runner prüft StateRoot, BackupRoot, Staging und den veröffentlichten Backup-Satz.
- Die Monitor-Cross-Repository-Workflows und der Pin-Regressionstest werden in diesem Stand auf genau `c59e1a143f96ac81b91156fba5b645294c7129da` aktualisiert.

## Verifizierte Post-Merge-CI
**Beekeeper-Monitor**
- [Gesamttest #45925964000](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45925964000): completed / success; Browser, Safari WebKit, iPhone-WebKit-Emulation, Bridge und Field-Dataset-Export gegen den BeeKeeper-Validator bestanden.
- [CodeQL #45925964049](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45925964049): success.
- [Repository-Integration #45925963998](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45925963998): success.
- [Integration Contracts #45925964016](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45925964016): success.
- Die KI-Freigabe bleibt ausdrücklich blockiert: `datasets/beekeeper` fehlt; Trainingsdaten und fachlich geprüfte Annotationen melden `failure`. Der Gesamttest unterscheidet diese Sperre korrekt von Software-CI.

**BeeKeeper3000**
- [Quality Gates #45926170647](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45926170647): success.
- [Windows Station #45926170682](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45926170682): success; synthetischer Backup-/Restore-Durchlauf für Source, Monitor und Kamera sowie Ablehnung einer für BUILTIN Users freigegebenen Ablage.
- [Supply Chain / SBOM #45926170707](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45926170707): success.
- [Network Reference Tests #45926170594](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45926170594): success.
- [CodeQL #45926170602](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45926170602): success.

Die ACL-Prüfungen sind **keine Verschlüsselung**. BitLocker/LUKS/FileVault, Schlüsselverwaltung, Backup-Aufbewahrung und ein Wiederherstellungstest auf echter Stationshardware bleiben erforderlich. IndexedDB und die lokalen SQLite-Daten sind nicht zusätzlich anwendungsseitig verschlüsselt.

## Release-, Lizenz- und Feldgrenzen
- Beide Root-`LICENSE`-Dateien fehlen; BeeKeeper3000 `LICENSES.md` ist ein vorläufiges Inventar, keine Gesamtfreigabe.
- Sechs Modellkandidaten stehen weiterhin auf `rights_and_runtime_pending`; im Repository-Baum liegen keine Modellgewichte. Keine KI-Inferenz, kein Training und keine 99-%-Erkennungsleistung sind freigegeben oder nachgewiesen.
- `pages.yml` bleibt mit `if: false` gesperrt. PWA-Vorschauen sind manuell ausgelöste, öffentlich lesbare Actions-Artefakte mit einem Tag Aufbewahrung; es wurde kein Pages-Deployment ausgelöst.
- Historische öffentliche Artefakte bleiben offen: fünf bekannte alte PWA-Artefakte, vier Review-/CC0-Artefakte und 20 PWA-Artefakte in historischen Stichproben bestätigt (exakte Gesamtzahl nicht enumeriert). Das Originalbild-Artefakt `15058597151` umfasst 161.230.685 Bytes. Keine Inhalte heruntergeladen; keine Löschaktion verfügbar.
- Beide `main`-Branches sind laut Branch-API ungeschützt; Ruleset-Listen sind leer. Branch Protection und Pages-Repository-Einstellung können mit den verbundenen Schreibaktionen nicht administrativ geändert werden.

## Nächste Schritte
1. Die neun konkret dokumentierten historischen PWA-/Review-/CC0-Artefakte manuell über GitHub Actions löschen und ihre Abwesenheit per API bestätigen; danach die übrige Historie vollständig inventarisieren.
2. Branch Protection/Rulesets und Pages-Einstellungen administrativ absichern.
3. Root-Lizenzen sowie Rechtekette der Modellgewichte und Trainingsbilder klären.
4. Lokale Datenbank-/Backup-Verschlüsselung, Löschabläufe und Wiederherstellung auf echter Hardware prüfen.
5. Erst nach freigegebenen Bildern und unabhängigen Annotationen Modelladapter und Feldvalidierung beginnen.

Keine privaten Bienenstanddaten, Fotos, GPS-Koordinaten oder Zugangsdaten übertragen. Keine unfreigegebenen Modellgewichte geladen oder aktiviert. Kein öffentliches Deployment ausgelöst.

---

# Historischer Prüfstand – 27.11.2026, 01:45 CET

Dieser Nachtrag basiert auf den aktuell abgefragten Hauptzweigen, Workflow-Jobs und Logs. Ältere Status-Snapshots weiter unten sind Historie und dürfen nicht als heutige Commit-/Freigabeaussage gelesen werden.

## Hauptzweige

- **Beekeeper-Monitor `main`:** `67c1dbbdf5ab1dccfc698c2d1ea932835162007`.
- **BeeKeeper3000 `main`:** `4676649d3d248f5b950ac1eaef7673bbd1af9f26`.
- Der Monitor pinnt BeeKeeper3000 unveränderlich auf genau diesen Partner-Commit.

## Tatsächlich geprüfte CI-Läufe

**Beekeeper-Monitor, Commit `67c1dbbdf5ab1dccfc698c2d1ea932835162007`:**
- [Ein-Klick-Gesamttest #45914218498](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45914218498): completed / success; alle drei Jobs (Gesamttest, Feld-Dataset-Export gegen BeeKeeper-Validator, BeeKeeper-Bridge-Integration) erfolgreich.
- [Repository-Integration #45914218238](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45914218238): completed / success.
- [CodeQL #45914218129](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45914218129): completed / success.
- Im Gesamttest bestanden Chromium, Safari/WebKit, iPhone-WebKit-Emulation, Node-/Python-Unit-Tests, PWA-Verträge, ZIP-Export-Roundtrip, Partner-Validator, Bridge-Replay und SQLite-Neustart.

**BeeKeeper3000, Commit `4676649d3d248f5b950ac1eaef7673bbd1af9f26`:**
- [Quality Gates #45907665077](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907665077): success.
- [Supply Chain / SBOM #45907665052](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907665052): success.
- [Windows-Station #45907665022](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907665022): success.
- [CodeQL #45907664994](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907664994): success.

## KI-Datenstatus aus dem tatsächlichen Monitor-Log

Der Software-Gesamttest ist grün; die KI-Datenfreigabe ist es nicht:
- Trainingsinventur: train 0 Bilder/0 Labels, val 0/0, test 0/0.
- `datasets/beekeeper/provenance.jsonl` fehlt.
- `training/train.py --validate-only` bricht mit `FileNotFoundError` ab: Dataset-Verzeichnis fehlt.
- `training/reviewed-annotations.json` fehlt; der Annotationsschritt meldet ausdrücklich BLOCKIERT.
- Der Laufbericht enthält `Echte Trainingsdaten: failure`, `Fachlich geprüfte Annotationen: failure` und `KI-STATUS: BLOCKIERT`. Diese Forschungs-/Freigabeschritte sind absichtlich keine Software-CI-Erfolgskriterien.

Es gibt sechs Modellkandidaten; alle stehen auf `rights_and_runtime_pending`. Keine freigegebenen Gewichte, kein rechtlich freigegebener Trainingsbestand, kein unabhängiger Holdout und keine gemessenen Precision-/Recall-/Fehlalarmraten. Die Modellverträge Klassifikation `[1,7]` und Detektion `[1,9,8400]` sind unterschiedliche Aufgaben; ein produktiv validierter Adapter fehlt. 99-%-Erkennung und Feldreife sind nicht nachgewiesen. PR [BeeKeeper3000 #110](https://github.com/simonthomas-ai/BeeKeeper3000/pull/110) bleibt Draft.

## Sicherheit, Datenschutz und Deployment

- Beide `main`-Branches melden über die Branch-API `protected=false`; beide Repository-Ruleset-Listen sind leer. Der Branch-Protection-Endpunkt selbst lieferte für diese Integration 403; Änderungen an Schutzregeln sind über die verfügbaren Aktionen nicht möglich.
- Beide Root-Dateien `LICENSE` fehlen (Contents-API 404). BeeKeeper3000 `LICENSES.md` bezeichnet sich ausdrücklich als vorläufiges Inventar und nicht als vollständige Release-Freigabe.
- `.github/workflows/pages.yml` ist `workflow_dispatch`-only; der Deploy-Job ist mit `if: false` gesperrt. In dieser Prüfung wurde kein Pages-Deployment ausgelöst. Die repositoryweite Pages-Einstellung konnte über den verfügbaren Fetch-Endpunkt nicht gelesen werden; daher wird sie hier nicht als deaktiviert oder aktiv bestätigt.
- Die Monitor-CI lud bei diesem Lauf noch ein öffentlich lesbares Actions-Artefakt `gesamttest-berichte` hoch: ID `15161278670`, 1.267 Bytes, Aufbewahrung ein Tag. Der Workflow enthielt dafür bisher `if: always()` und lief bei Push/PR. Diese Änderung macht den Upload nur noch nach ausdrücklichem `workflow_dispatch`; bis zum Merge gilt auf `main` noch die bisherige Regel.
- Zusätzlich waren Browser-/WebKit-Fehlertraces (manuell, nur bei Fehler) und die wöchentliche autonome Projektsteuerung (14 Tage) als öffentliche Artefakte konfiguriert. Diese PR setzt für Browser/WebKit ein Tag Aufbewahrung und begrenzt den autonomen Trace-Upload auf manuelles `workflow_dispatch` mit einem Tag; bis zum Merge gelten die bisherigen Workflow-Regeln.
- Historisch wurden 20 unterschiedliche PWA-Artefakte über mehrere Läufe einzeln bestätigt; die exakte aktive Gesamtzahl ist nicht vollständig enumeriert. Darunter befindet sich ein Originalbild-Artefakt mit rund 161 MB. Die Artefakte wurden nicht heruntergeladen oder gelöscht; die verfügbare GitHub-Aktion stellt keine Löschoperation bereit.
- Browser-IndexedDB und lokale SQLite-Daten sind nicht zusätzlich anwendungsseitig im Ruhezustand verschlüsselt. JSON-Backups können Fotos und GPS enthalten; Sicherungen benötigen Geräte-/Datenträgerverschlüsselung und restriktive Zugriffsrechte.
- Keine privaten Bienenstanddaten, Fotos, GPS-Koordinaten oder Zugangsdaten wurden übertragen. Keine Modellgewichte ausgeführt oder trainiert. Kein öffentliches Deployment ausgelöst.

## Noch offen

1. PR und CI-Prüfung dieser Änderung abschließen; öffentliche CI-Berichte nur nach manueller Auslösung erzeugen.
2. Historische öffentliche Actions-Artefakte über GitHub-Administration löschen und anschließend die Artefaktliste erneut prüfen.
3. Branch Protection/Rulesets und Pages-Einstellungen administrativ absichern.
4. Vollständige Rechtekette, Root-Lizenzen und Provenienz für Modelle und Bilder klären.
5. Lokale Datenbank-/Backup-Verschlüsselung und Löschabläufe auf echten Geräten testen.
6. Erst mit freigegebenen Bildern und unabhängigen Annotationen Modelladapter, Holdout-Metriken und Feldvalidierung beginnen.

**Freigabestatus: GESPERRT.** Software-CI-Erfolg ist kein Nachweis einer validierten KI, DSGVO-Freigabe oder Einsatzreife.
---

# Nachtrag 27.11.2026 – Partner-Pin auf aktuellen BeeKeeper3000-Hauptzweig

Ausgangsstand vor dieser Änderung: Beekeeper-Monitor `main` `afd13599528c4c7ded72df9babc35dcd844026d0`; BeeKeeper3000 `main` `4676649d3d248f5b950ac1eaef7673bbd1af9f26`. Der bisherige Cross-Repository-Pin `77bd1c012af502afa42b9a79bf9eff0deda37032` lag vier Commits hinter BeeKeeper3000. Der Commitvergleich umfasste vier Commits/sechs Dateien; Bridge-, Source-API-, Kamera-Manifest- und Datensatzvalidator-Schnittstellen blieben unverändert. Die Partner-Hauptzweigprüfungen (Quality Gates, CodeQL, SBOM, Windows-Station) waren erfolgreich. PR #334 aktualisiert beide Monitor-Workflows, den Pin-Regressionstest und die Integrationsdokumentation auf den aktuellen unveränderlichen Partnerstand. Keine Gewichte, Trainingsdaten oder privaten Daten wurden übernommen; kein Deployment ausgelöst.

---

# Korrektur – finaler Stand nach PR #330, 27.11.2026 00:00 CET

Die darunter archivierten Snapshots enthalten frühere PR-Zustände. Für den aktuellen Repository-Stand gilt:

- **Beekeeper-Monitor main:** `d674e625289d5b90524b1c786e787d5767e77952`.
- **BeeKeeper3000 main:** `4676649d3d248f5b950ac1eaef7673bbd1af9f26`.
- Monitor [PR #328](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/328) ist inzwischen gemergt (Statusdokumentation).
- Monitor [PR #329](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/329) ist gemergt: explizite Token-Berechtigungen auf Workflow-/Job-Ebene, kein `write-all`.
- Monitor [PR #330](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/330) ist gemergt: jeder `actions/checkout`-Schritt muss `persist-credentials: false` setzen. PR-CI vollständig erfolgreich; der Log bestätigt 21 Workflow-Audit-Tests mit `OK` und `PASS` für alle 42 Monitor-Workflowdateien.
- Monitor-Post-Merge-Checks für `d674e625` waren beim letzten Abruf noch in Initialisierung/in Bearbeitung; kein Post-Merge-Erfolg behauptet.
- BeeKeeper3000 [PR #130](https://github.com/simonthomas-ai/BeeKeeper3000/pull/130) ist gemergt: der selbstgehostete LLM-Council läuft nur noch auf `refs/heads/main`.
- BeeKeeper3000 [PR #131](https://github.com/simonthomas-ai/BeeKeeper3000/pull/131) ist gemergt: explizite Token-Berechtigungen und Verbot von `write-all`. PR- und Post-Merge-CI vollständig erfolgreich; 22 Workflow-Audit-Tests mit `OK`, alle 10 BeeKeeper-Workflowdateien bestanden.
- Der LLM-Council hat weiterhin lokale Ollama- und externe Provider deaktiviert. Kein Provider wurde aufgerufen.
- PWA-Historie: 224 Workflow-Läufe (212 erfolgreich, 12 fehlgeschlagen); 20 aktive PWA-Artefakte wurden einzeln bestätigt, exakte Gesamtzahl nicht enumeriert. Die 12 fehlgeschlagenen Läufe hatten keine Artefakte. Die alten Artefakte wurden nicht heruntergeladen oder gelöscht.
- Pages-Einstellung bleibt aktiviert (`has_pages=true`), der Deploy-Job bleibt mit `if: false` gesperrt und besitzt keine `pages:write`-/OIDC-Deploy-Rechte. Kein öffentliches Deployment ausgelöst.
- Beide Hauptzweige bleiben ungeschützt (`protected=false`); die verfügbaren GitHub-Aktionen erlauben keine Änderung von Branch Protection oder Pages-Einstellungen.

**KI-Freigabe unverändert blockiert:** sechs Modellkandidaten mit `rights_and_runtime_pending`; keine Gewichte, kein freigegebener Trainingsdatensatz, keine unabhängigen Annotationen oder Holdout-Metriken. Die Formverträge `[1,7]` und `[1,9,8400]` bleiben inkompatibel. Keine 99-%-Erkennungsleistung oder Feldreife nachgewiesen.

---

# Nachtrag – 26.11.2026, 23:55 CET

## Nach PR #131

- **BeeKeeper3000 main:** `4676649d3d248f5b950ac1eaef7673bbd1af9f26` (PR #131).
- [PR #131](https://github.com/simonthomas-ai/BeeKeeper3000/pull/131) wurde nach erfolgreicher PR-CI gemergt. Der vorhandene Workflow-Audit prüft jetzt auch in BeeKeeper3000 explizite Token-Berechtigungen auf Workflow- oder Job-Ebene und weist `write-all` einschließlich Job-Level-Overrides zurück.
- PR-CI: [Quality Gates #45907405776](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907405776), [Supply Chain / SBOM #45907405729](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907405729) und [CodeQL #45907405795](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907405795) sind erfolgreich.
- Der Quality-Gates-Log bestätigt 22 Workflow-Audit-Tests mit `OK` und `PASS` für alle 10 BeeKeeper3000-Workflowdateien.
- Post-Merge-Prüfungen für `4676649d` wurden gerade ausgelöst; noch kein Post-Merge-Erfolg behauptet.
- **Beekeeper-Monitor main:** `c2ad973231d734936df78bc1eeb4ff74b09037e8`; Gesamttest, Bridge, Feld-Dataset-Validator und beide CodeQL-Sprachen sind vollständig erfolgreich.
- Monitor [PR #328](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/328) ist weiterhin ein reiner Dokumentations-PR. Bridge, Feld-Dataset-Validator und CodeQL sind erfolgreich; der Gesamttest läuft noch. Noch nicht gemergt.
- Der PWA-Artefaktumfang ist oben korrigiert: 224 Workflow-Läufe (212 erfolgreich, 12 fehlgeschlagen), mindestens 20 aktive Artefakte über die Laufhistorie bestätigt, exakte Gesamtzahl nicht enumeriert.

# Korrektur – öffentliche PWA-Artefakte, 26.11.2026 23:50 CET

Die frühere Aufzählung von neun historischen Artefakten war unvollständig. Eine erneute Paginierung der Actions-Run-Historie zeigt **224 Läufe** des Workflows `.github/workflows/private-pwa.yml` (Run-Nummern 1–224), erstellt vom 21.11.2026 16:17:26 UTC bis 26.11.2026 20:39:49 UTC: **212 completed/success, 12 completed/failure**. Das ist eine Anzahl von Workflow-Läufen, nicht automatisch eine bestätigte Anzahl von Artefakten.

Über die Artefakt-API wurden **20 eindeutige PWA-Artefakte** über frühe, mittlere und aktuelle Läufe hinweg einzeln bestätigt; alle meldeten `expired=false`:
- Ältere Stichproben: `14715215560`, `14716389937`, `14718636138`, `14719580500`, `14721515981`, `14744707898`, `15087247299`.
- Die zuvor erfassten fünf: `15124542124`, `15118529028`, `15115678841`, `15115577897`, `15108012720`.
- Neuere acht: `15127033729`, `15127464985`, `15134318088`, `15135695760`, `15137419854`, `15142681903`, `15146326999`, `15151807914`.

Die acht neueren Artefakte laufen am 03.12.2026 ab; die ältesten Stichproben am 28.11.2026. **Die exakte Gesamtzahl aktiver PWA-Artefakte ist noch nicht vollständig enumeriert.** Die 12 fehlgeschlagenen Läufe (Nummern 96–98, 111–116, 121–123) wurden einzeln auf Artefakte geprüft und hatten keine. Ihre Logs zeigen vorübergehende Offline-PWA-Vertrags-/Staging-Abweichungen: fehlende explizite Publikation von `varroa.html`/`varroa-ui.js`, danach `hornet-onnx-decoder.js` bzw. `camera-onnx-runtime.js`, sowie veraltete statische Assertions der Pages-Kopierliste. Die aktuelle main-Gesamttestprüfung ist erfolgreich. Die Artefaktinhalte wurden nicht heruntergeladen oder inspiziert; daher wird keine Aussage getroffen, ob jedes historische Artefakt personenbezogene Daten enthält. Bei einem öffentlichen Repository sind Actions-Artefakte als öffentlich lesbar zu behandeln.

PR #327 hat den Workflow inzwischen auf manuelle Auslösung und 1 Tag Aufbewahrung begrenzt. Nach dem Merge wurde kein neuer PWA-Vorschau-Lauf gefunden. Die alten Artefakte sind davon nicht betroffen. Die verbundene GitHub-Schnittstelle bietet keine Artefakt-Löschaktion; es wurde nichts heruntergeladen oder gelöscht.

[Issue #318](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/318) wurde mit dieser korrigierten Reichweite aktualisiert. Der alte Abschnitt darunter enthält die frühere, unvollständige Neuner-Liste und ist nur noch als historischer Snapshot zu lesen.

---

# Nachtrag – 26.11.2026, 23:47 CET

## Nach PR #130

- **BeeKeeper3000 main:** `04200eb8612a00a0e16f79ac0984dcaa70ef612b` (PR #130).
- [PR #130](https://github.com/simonthomas-ai/BeeKeeper3000/pull/130) wurde nach erfolgreicher PR-CI gemergt. Der selbstgehostete LLM-Council-Job läuft jetzt nur noch bei `github.ref == refs/heads/main`; manuelle Dispatches auf Feature-Branches werden am Job-Gate gestoppt.
- Der PR-Testlauf [#45907095395](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45907095395) bestand Python-Kern-/LLM-Sicherheitstests, Kamera-Runtime, Bridge und Windows-Kompatibilität. Der Log bestätigt `test_self_hosted_council_only_runs_from_main` als `ok`; insgesamt 31 Tests im Python-Kernjob bestanden. Beide CodeQL-Sprachen waren erfolgreich.
- Post-Merge-Prüfungen auf `04200eb8` wurden ausgelöst und waren beim letzten Abruf noch queued; noch kein Post-Merge-Erfolg behauptet.
- **Beekeeper-Monitor main:** `c2ad973231d734936df78bc1eeb4ff74b09037e8`. Nach-Merge-Bridge und Feld-Dataset-Validator sind erfolgreich; Gesamttest und JavaScript-CodeQL laufen noch. Python-CodeQL ist erfolgreich.
- Keine externen LLM-Provider aktiviert oder aufgerufen; Ollama und sämtliche externen Provider bleiben in `llm-council/config.json` deaktiviert.

# Nachtrag – 26.11.2026, 23:45 CET

## Nach PR #329 und aktuelle offene Sicherheitsänderungen

- **Beekeeper-Monitor main:** `c2ad973231d734936df78bc1eeb4ff74b09037e8` (PR #329).
- **BeeKeeper3000 main:** `b841d2adb1586ab88a82cef67e8be4e1523a2f21`.
- Monitor [PR #329](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/329) wurde nach erfolgreicher PR-CI gemergt. Der Workflow-Audit prüft jetzt explizite Token-Berechtigungen auf Workflow- oder Job-Ebene und weist `write-all` auch bei Job-Level-Overrides zurück.
- Im PR-Gesamttest [#45906870050](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45906870050) waren alle drei Jobs erfolgreich. Der Log bestätigt 17 Tests aus `scripts.test_audit_workflow_action_pins` mit `OK`; der Audit meldete explizite Berechtigungen in allen 42 Monitor-Workflowdateien. CodeQL und Bridge-/Feld-Dataset-Validator-Checks waren ebenfalls erfolgreich.
- Die Post-Merge-Checks für `c2ad9732` wurden ausgelöst, waren beim letzten Abruf noch queued/in progress; noch kein Post-Merge-Erfolg behauptet.
- Monitor [PR #328](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/328) bleibt ein Dokumentations-PR. CodeQL, Python-/JavaScript-CodeQL, Bridge und Feld-Dataset-Validator sind erfolgreich; der Gesamttest ist noch in Bearbeitung. Er wurde nicht gemergt.
- BeeKeeper3000 [PR #130](https://github.com/simonthomas-ai/BeeKeeper3000/pull/130) ist offen: Der selbstgehostete LLM-Council-Job wird auf `refs/heads/main` beschränkt, damit ein manuell ausgewählter Feature-Branch nicht auf dem persistenten Windows-Runner ausgeführt wird. Python-, Kamera- und Bridge-Jobs waren erfolgreich; Windows-Kompatibilität und CodeQL waren noch in Bearbeitung. Noch kein Merge.
- In `llm-council/config.json` bleiben lokales Ollama und alle externen Provider deaktiviert. Kein Provider wurde in dieser Prüfung aufgerufen und kein Repository-/Nutzerinhalt an einen externen Modellanbieter übertragen.

# Aktuell verifizierter Stand – 26.11.2026, 23:40 CET

Dieser Nachtrag ersetzt für die aktuelle Lage die darunter archivierten Snapshots. Die GitHub-API wurde erneut direkt abgefragt; Status, CI und KI-Freigabe bleiben getrennt.

## Hauptzweige und abgeschlossene Post-Merge-Prüfungen

- **Beekeeper-Monitor main:** `ba20e5627afdabedba3692666ca4564fc56781f2`.
- **BeeKeeper3000 main:** `b841d2adb1586ab88a82cef67e8be4e1523a2f21`.
- Monitor PR #327 ist gemergt: öffentliche PWA-Vorschau nur noch manuell, Aufbewahrung 1 Tag; keine Website-Veröffentlichung.
- BeeKeeper3000 PR #129 ist gemergt: Waspinator-AGPL-3.0-Quelle/Modellmetadaten dokumentiert; Gewichte und Bildrechte bleiben ungeklärt und der Kandidat bleibt nicht integriert.

**Monitor auf main `ba20e562`:**
- [Gesamttest #45900540463](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900540463): completed / success.
- [CC0-Quellenprüfung #45900540474](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900540474): completed / success.
- [CodeQL #45900540516](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900540516): completed / success.
- [CC0-Artefakt-Rücklese #45901791020](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45901791020): completed / success; die Artefaktliste dieses Laufs ist leer.
- Der Gesamttest trennt Softwareerfolg von KI-Freigabe: `TRAINING: failure`, `ANNOTATIONS: failure`; Trainingsbilder und freigegebene Annotationen fehlen weiterhin.

**BeeKeeper3000 auf main `b841d2ad`:**
- [Quality Gates #45900617855](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900617855): completed / success.
- [CodeQL #45900617816](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900617816): completed / success.
- [Supply Chain / SBOM #45900617790](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900617790): completed / success.
- Der SBOM-Umfang bleibt partiell; nicht enthalten sind u. a. vollständige geerbte C++-Quellen, Firmware, Modellgewichte und Datensätze.

## Neue Workflow-Berechtigungsprüfung

- Die Inventur aller 42 Monitor-Workflows und 10 BeeKeeper3000-Workflows fand explizite Token-Berechtigungen auf Workflow- oder Job-Ebene; der KiCad-ERC-Workflow verwendet Job-Level `contents: read`.
- Die Suche fand keine Verwendung von `permissions: write-all` und keine `pull_request_target`-Trigger.
- Monitor PR [#329](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/329) ergänzt einen Regressionstest, der explizite Workflow-/Job-Berechtigungen und verbotene `write-all`-Overrides künftig prüft.
- PR #329 ist **nicht gemergt**. Die ersten Actions-Läufe starteten auf einem älteren Branch-Commit und blieben bei der Runner-/Container-Initialisierung stehen. Danach wurde der Branch aktualisiert; für den aktuellen Head `26103f559d6adbad15b1cfdc70cf3d96c137183e` lagen zum Snapshot noch keine Check-Runs vor. Die lokalen synthetischen Testfälle für erlaubte/fehlende/zu weitreichende Berechtigungen wurden separat geprüft; das ersetzt keinen GitHub-CI-Lauf.

## Historische öffentliche Actions-Artefakte – weiterhin offen

Die neun bekannten Artefakte wurden einzeln erneut über ihre Run-Artefaktlisten geprüft; alle meldeten `expired=false`. Sie wurden nicht heruntergeladen oder gelöscht.

| Run | Artefakt-ID | Inhalt | Größe | Ablauf (UTC) |
|---|---:|---|---:|---|
| [#45835039321](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45835039321) | 15124542124 | alte PWA-Vorschau | 65.655 B | 2026-12-03 14:02:46 |
| [#45823611579](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45823611579) | 15118529028 | alte PWA-Vorschau | 65.655 B | 2026-12-03 12:51:51 |
| [#45817855487](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45817855487) | 15115678841 | alte PWA-Vorschau | 65.655 B | 2026-12-03 12:14:54 |
| [#45816613770](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45816613770) | 15115577897 | alte PWA-Vorschau | 65.655 B | 2026-12-03 12:06:51 |
| [#45803405754](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405754) | 15108012720 | alte PWA-Vorschau | 65.655 B | 2026-12-03 10:39:53 |
| [#45803405634](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405634) | 15108851881 | iNaturalist-Reviewqueue | 89.737 B | 2026-12-10 10:42:29 |
| [#45803405656](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405656) | 15107897872 | Insekten-Reviewqueue | 163.198 B | 2026-12-10 10:42:12 |
| [#45689841927](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45689841927) | 15058597151 | Originalbilder | 161.230.685 B | 2026-12-09 20:03:37 |
| [#45689841927](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45689841927) | 15058522636 | CC0-Prüflisten | 169.351 B | 2026-12-09 20:03:42 |

Die verbundene GitHub-Aktionsschnittstelle stellt keine Artefakt-Löschoperation bereit. Manuelle Löschung und API-Rücklese bleiben offen. Der neue CC0-Lauf #45901791020 hat keine Artefakte erzeugt.

## Weiterhin unveränderte Release-Blocker

- Beide Repositories sind öffentlich; GitHub meldet `license=null`; beide Root-`LICENSE`-Dateien fehlen.
- Beide `main`-Branches melden `protected=false`; Pages-Einstellung des Monitors ist weiterhin aktiviert (`has_pages=true)), der Pages-Deploy-Job bleibt aber mit `if: false` gesperrt. Kein öffentliches Pages-Deployment wurde ausgelöst.
- Monitor `models/candidates.json`: sechs Kandidaten, alle `rights_and_runtime_pending`; keine Modellgewichte und kein freigegebener Datensatz im Repository.
- BeeKeeper-Klassifikatorvertrag `[1,7]` und Monitor-Detektionsvertrag `[1,9,8400]` bleiben inkompatibel; kein produktiv validierter Adapter.
- Browser-IndexedDB und lokale SQLite-Daten sind nicht anwendungsseitig im Ruhezustand verschlüsselt; JSON-Backups können Fotos und GPS enthalten. Betriebssystem-/Datenträgerverschlüsselung und restriktive Dateirechte sind erforderlich.
- BeeKeeper3000 LLM Council: lokale Ollama- und alle externen Provider sind in der aktuellen Konfiguration deaktiviert. Der Workflow läuft auf einem selbstgehosteten Windows-Runner; kein externer Provider wurde in dieser Prüfung aufgerufen.
- Keine unabhängig annotierten Holdoutdaten, keine gemessenen Precision-/Recall-/Fehlalarmraten, kein Nachweis von 99 % Erkennung und keine vollständige reale Kamera-/Dauerlaufabnahme.

**Status:** Software-CI für die beiden aktuellen Hauptzweige ist für die genannten Läufe erfolgreich. Modell-/Datensatzrechte, Datenbasis, lokale Verschlüsselung, Branch-Schutz, historische Artefakte und reale Feldabnahme bleiben offen. Kein Modell aktiviert, keine sensiblen Standort- oder Kameradaten übertragen, kein öffentliches Deployment ausgelöst.

---

# Aktuell verifizierter Stand – 26.11.2026, GitHub-API-Snapshot 21:48 UTC

Dieser Snapshot ergänzt und ersetzt für den aktuellen Stand den darunter archivierten 20:36-CET-Snapshot. Er trennt PR-Prüfungen von noch laufenden Post-Merge-Prüfungen und von der KI-Feldfreigabe.

## Hauptzweige und integrierte Änderungen

- **Beekeeper-Monitor `main`:** `ba20e5627afdabedba3692666ca4564fc56781f2` (PR #327).
- **BeeKeeper3000 `main`:** `b841d2adb1586ab88a82cef67e8be4e1523a2f21` (PR #129).
- Beide Repositories sind öffentlich; GitHub meldet weiterhin `license=null`; beide Root-Dateien `LICENSE` fehlen.
- Beide `main`-Branches melden weiterhin `protected=false`; Branch-Schutz und Rulesets wurden nicht geändert.
- Beekeeper-Monitor meldet `has_pages=true`; BeeKeeper3000 `has_pages=false`.
- Beekeeper-Monitor `.github/workflows/pages.yml` bleibt `workflow_dispatch`-only und der Deploy-Job bleibt mit `if: ${{ false }}` gesperrt. Kein Pages-Deployment wurde ausgelöst; die repositoryweite Pages-Einstellung ist nicht deaktiviert und eine frühere Live-Veröffentlichung bleibt unbestätigt.

## Neue Änderungen dieser Runde

- **Monitor PR #327:** [PR](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/327), Merge-Commit `ba20e5627afdabedba3692666ca4564fc56781f2`. Die öffentliche PWA-Buildvorschau wird nicht mehr bei jedem Push erzeugt; sie ist nur noch manuell über `workflow_dispatch` auslösbar. Wenn manuell ausgelöst, bleibt das Actions-Artefakt öffentlich lesbar, wird aber nach einem Tag entfernt. `scripts/test_static.py` prüft diese Trigger- und Aufbewahrungsregeln.
- **Monitor-CI-Korrektur:** Der erste PR-Lauf scheiterte an einer veralteten Testannahme `retention-days: 7`. Der Test wurde auf die neue Ein-Tages-Regel und manuelle Auslösung umgestellt. Der korrigierte Lauf [Gesamttest #45900200445](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900200445), [CodeQL #45900200436](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900200436) und [CC0-Artefakt-Policy #45900200503](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900200503) war erfolgreich.
- **BeeKeeper3000 PR #129:** [PR](https://github.com/simonthomas-ai/BeeKeeper3000/pull/129), Merge-Commit `b841d2adb1586ab88a82cef67e8be4e1523a2f21`. `LICENSES.md` dokumentiert jetzt ausdrücklich den Waspinator-Kandidaten: Upstream-Repository und Modellmetadaten deklarieren AGPL-3.0; die vollständige Rechtekette der Trainingsbilder/Attributionsdatei ist nicht unabhängig geklärt. Der Kandidat bleibt checksum-only und ist nicht im Runtime-Manifest.
- **BeeKeeper3000 PR-Prüfungen:** [Quality Gates #45900483768](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900483768), [Supply Chain / SBOM #45900483837](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900483837) und [CodeQL #45900483750](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900483750) waren vor dem Merge erfolgreich.

## Post-Merge-Prüfungen (Snapshot 21:48 UTC)

- **Monitor auf `ba20e562`:** Gesamttest [#45900540463](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900540463), CC0-Quellenprüfung [#45900540474](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900540474) und CodeQL [#45900540516](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45900540516) waren bei letzter Abfrage noch in Bearbeitung. Die gesonderten Trainingsdaten- und Readiness-Prüfungen waren erfolgreich, melden aber fehlende echte Daten.
- **BeeKeeper3000 auf `b841d2ad`:** Quality Gates [#45900617855](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900617855), CodeQL [#45900617816](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900617816) und Supply Chain / SBOM [#45900617790](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45900617790) waren bei letzter Abfrage noch in Bearbeitung.
- Der Push auf Monitor `ba20e562` hat keinen PWA-Vorschau-Workflow ausgelöst; das bestätigt die neue manuelle Triggerregel. Das letzte zuvor erzeugte PWA-Artefakt war `15151807914`, öffentlich lesbar, 65.783 Bytes, Ablauf 2026-12-03 20:40 UTC.

## Weiterhin offene Freigabeblocker

- Neun historische öffentliche Actions-Artefakte bleiben vorhanden und meldeten bei Einzelabfrage `expired=false`: fünf alte PWA-Artefakte und vier Review-/CC0-Artefakte. Die manuelle Löschung ist offen; die verbundene GitHub-Aktionsschnittstelle bietet keine Artefakt-Löschoperation. Keines dieser neun historischen Artefakte wurde heruntergeladen oder gelöscht.
- Die rekursiven Hauptzweig-Bäume beider Repositories enthalten keine ONNX-/PT-/TFLite-/NCNN-Modellgewichte und kein `datasets/beekeeper/`.
- Monitor `models/candidates.json` enthält sechs revisionsgebundene Kandidaten; alle stehen auf `rights_and_runtime_pending`.
- `training/reviewed-annotations.json` und echte, pro Bild lizenz-/SHA-256-geprüfte Trainingsdaten fehlen. Im letzten Gesamttest waren `TRAINING: failure` und `ANNOTATIONS: failure`; die Software-CI blieb nur deshalb grün, weil diese Freigabestatus getrennt ausgewiesen werden.
- BeeKeeper-Klassifikationsvertrag `[1,7]` und Monitor-Detektionsvertrag `[1,9,8400]` bleiben inkompatibel; kein produktiv validierter Adapter.
- Der Waspinator-Quellcode und Modellmetadaten deklarieren AGPL-3.0. Das klärt nicht automatisch Rechte an allen Trainingsbildern oder die Weitergabe der Gewichte; keine Runtime-Freigabe.
- Browser-IndexedDB und lokale SQLite-Daten sind nicht anwendungsseitig im Ruhezustand verschlüsselt. JSON-Backups können optionale Bilder und GPS enthalten. Der spezielle Feld-ZIP-Export entfernt Metadaten; die Löschung lokaler Daten entfernt keine bereits exportierten Kopien.

**Status:** Softwaretests sind für den PR #327 vollständig erfolgreich; die Post-Merge-Läufe auf den neuen Hauptzweigen waren zum Snapshot noch nicht abgeschlossen. Keine Modellgewichte aktiviert, keine privaten Bienenstanddaten übertragen und kein öffentliches Deployment ausgelöst. Keine KI-Genauigkeit oder Feldreife behauptet.

---

## Historischer Snapshot – 26.11.2026, 20:36 CET

Dieser datierte Snapshot wurde direkt gegen GitHub-Hauptzweige, Workflow-Läufe, Job-Logs, Repository-Metadaten und Actions-Artefaktlisten geprüft. Er ist keine fachliche, rechtliche oder Feldfreigabe. Ältere Prüfprotokolle bleiben weiter unten unverändert erhalten.

## Repository- und Hauptzweigstatus

- **Beekeeper-Monitor `main`:** `abe574a46171f4135b5ff9ad7937692670061bc5` (Commit vom 26.11.2026, 18:47 UTC).
- **BeeKeeper3000 `main`:** `77bd1c012af502afa42b9a79bf9eff0deda37032`.
- Beide Repositories sind öffentlich; GitHub meldet `license=null`. Eine Root-Datei `LICENSE` ist in beiden aktuellen Hauptzweigen nicht vorhanden.
- Beide `main`-Branches melden `protected=false`; die abgefragten Repository-Rulesets-Listen sind leer. Branch-Schutz wurde nicht verändert.
- Beekeeper-Monitor meldet `has_pages=true`; BeeKeeper3000 `has_pages=false`.
- `.github/workflows/pages.yml` ist nur über `workflow_dispatch` auslösbar; der Job `deploy` enthält `if: ${{ false }}`. In dieser Prüfung wurde kein Pages-Deployment ausgelöst. Die repositoryweite Pages-Einstellung ist damit nicht deaktiviert; eine frühere Live-Veröffentlichung wurde nicht unabhängig bestätigt.
- Beide Cross-Repository-Workflows und ihr Pin-Regressionstest verwenden den unveränderlichen BeeKeeper3000-Commit `77bd1c012af502afa42b9a79bf9eff0deda37032`. Eine alte abweichende Pin-Angabe in `docs/FIELD-DATASET-CAPTURE.md` wird mit diesem PR korrigiert.

## Aktuelle CI-Nachweise

**Beekeeper-Monitor auf `abe574a46171f4135b5ff9ad7937692670061bc5`:**
- [Ein-Klick-Gesamttest #45878772708](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45878772708): erfolgreich; alle drei Jobs abgeschlossen (Gesamttest, BeeKeeper3000-Bridge und Feld-Dataset-Export/Validator).
- [CodeQL #45878772726](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45878772726): erfolgreich; JavaScript/TypeScript und Python abgeschlossen.
- [CC0-Publication-Policy #45878772779](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45878772779): Workflow erfolgreich; der Schritt zur Prüfung einer konkreten Upstream-CC0-Run-ID war bei diesem Push-Ereignis übersprungen und wird nicht als Artefakt-Rücklese gewertet.
- [Gesonderte CC0-Artefakt-Rücklese #45862208690](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45862208690): erfolgreich; die Actions-Artefaktliste dieses Laufs war leer.
- [PWA-Buildvorschau #45878772663](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45878772663): erfolgreich; öffentliches Actions-Artefakt `vespaguard-pwa-preview`, ID `15146326999`, 65.783 Bytes, Ablauf 2026-12-03 18:48:06 UTC. Laut Workflow enthält es statische App-Dateien und einen Sichtbarkeitshinweis; es ist kein Pages-Deployment.
- Die Logs des Gesamttests zeigen erfolgreiche statische, Node-Unit-, Browser-, WebKit-, iPhone-WebKit-, Import-, Taxonomie-, Modellkatalog-, Bridge- und ZIP-Validator-Prüfungen.
- **Wichtige getrennte Freigabestatus aus demselben Log:** `TRAINING: failure` und `ANNOTATIONS: failure`. Das ist kein grüner Trainingsnachweis: `datasets/beekeeper/` und `training/reviewed-annotations.json` fehlen; der Bericht setzt den KI-Status ausdrücklich auf BLOCKIERT.

**BeeKeeper3000 auf `77bd1c012af502afa42b9a79bf9eff0deda37032`:**
- [Quality Gates #45795479713](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479713): erfolgreich; Kamera-Runtime-Sicherheit, Windows-Kompatibilität, Python-Kern und Monitor-Bridge abgeschlossen.
- [Supply Chain / SBOM #45795479697](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479697): erfolgreich; pip-audit meldete in den geprüften Bereichen keine bekannten Schwachstellen. Die Logs warnen zugleich, dass vollständige Hash-Pins empfohlen sind.
- [CodeQL #45795479682](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479682): erfolgreich.
- [Windows-Station #45795479670](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479670): erfolgreich.
- Die SBOM-Abdeckung bleibt partiell; geerbte C++-Quellen, Betriebssystem-/Firmwarebestand, Modellgewichte und Datensätze sind nicht vollständig erfasst. Erfolgreiches CodeQL belegt nicht automatisch null offene Code-Scanning-Alerts.

## Historische öffentliche Actions-Artefakte – manuelle Löschung offen

Alle neun folgenden Artefakte wurden am 26.11.2026 erneut einzeln über ihre Run-Artefaktlisten abgefragt; alle meldeten `expired=false`. Sie wurden nicht heruntergeladen oder gelöscht.

**Fünf alte PWA-Artefakte (statische App-Dateien; der historische Name „private“ war irreführend):**

| Run | Artefakt-ID | Größe | Ablauf (UTC) |
|---|---:|---:|---|
| [#45835039321](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45835039321) | 15124542124 | 65.655 B | 2026-12-03 14:02:46 |
| [#45823611579](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45823611579) | 15118529028 | 65.655 B | 2026-12-03 12:51:51 |
| [#45817855487](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45817855487) | 15115678841 | 65.655 B | 2026-12-03 12:14:54 |
| [#45816613770](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45816613770) | 15115577897 | 65.655 B | 2026-12-03 12:06:51 |
| [#45803405754](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405754) | 15108012720 | 65.655 B | 2026-12-03 10:39:53 |

**Vier alte Review-/CC0-Artefakte:**

| Run | Artefakt-ID | Name | Größe | Ablauf (UTC) |
|---|---:|---|---:|---|
| [#45803405634](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405634) | 15108851881 | inaturalist-balanced-review-queue | 89.737 B | 2026-12-10 10:42:29 |
| [#45803405656](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405656) | 15107897872 | insect-photo-review-queue | 163.198 B | 2026-12-10 10:42:12 |
| [#45689841927](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45689841927) | 15058597151 | original-velutina-images | 161.230.685 B | 2026-12-09 20:03:37 |
| [#45689841927](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45689841927) | 15058522636 | ki-cc0-quellen-prueflisten | 169.351 B | 2026-12-09 20:03:42 |

Die aktuellen Review-/Discovery-Workflows verhindern neue Kandidaten-/Review-Artefaktuploads. Die neun Altartefakte erfordern weiterhin manuelle Löschung und anschließende API-Rücklese. Die verbundene GitHub-Schnittstelle bietet keine Artefakt-Löschaktion; keine Umgehung wurde versucht.

## KI, Modelle, Datensätze und Rechte

- `models/candidates.json` enthält sechs revisionsgebundene Kandidaten; alle stehen auf `rights_and_runtime_pending`.
- Die rekursive Tree-Prüfung des aktuellen Monitor-Hauptzweigs fand keine ONNX-/PyTorch-/TensorFlow-/TFLite-Modellgewichte und kein `datasets/beekeeper/`.
- `datasets/beekeeper/provenance.jsonl` und `training/reviewed-annotations.json` fehlen; der Trainingslauf endet daher ausdrücklich blockiert.
- BeeKeeper3000-Trainervertrag: RGB/NCHW `[1,3,224,224]`, Klassifikationslogits `[1,7]`. Der Monitor-Detektionsdecoder erwartet `[1,9,8400]` mit Detektions-/Bounding-Box-Vertrag. Diese Aufgaben und Tensorverträge sind nicht austauschbar; ein produktiver validierter Adapter fehlt.
- BeeKeeper3000 [PR #110](https://github.com/simonthomas-ai/BeeKeeper3000/pull/110) ist weiterhin nicht in `main` integriert.
- Beide Root-Lizenzen fehlen. BeeKeeper3000s `LICENSES.md` bezeichnet sich selbst als vorläufiges Engineering-Inventar, nicht als vollständige Release-Freigabe. Modellgewichte, Bildquellen und Datensätze benötigen separate Rechte-/Attributionsnachweise.
- PyTorch 2.15.0 bleibt wegen zusammengesetztem Lizenz-Ausdruck und fehlendem PyPI-Provenienznachweis laut aktuellem Lizenzinventar für produktives Training gesperrt.

## Sicherheit, Datenschutz und Feldfreigabe

- Die experimentelle `camera-onnx-runtime.js` ist ein deaktivierter Research-Stub; `loadRuntime()` bricht fail-closed ab. Es wird keine externe ONNX-/WASM-Runtime nachgeladen und keine Kamera-Inferenz freigegeben.
- Browser-IndexedDB ist nicht anwendungsseitig verschlüsselt; der normale JSON-Backup-Export enthält alle gespeicherten Beobachtungen einschließlich optionaler Bilddaten und GPS-Standort. Der spezielle Feld-ZIP-Export erzeugt neu kodierte PNG-Kopien ohne EXIF; die Originalbytes bleiben lokal im Browser.
- Auch der lokale SQLite-Ereignisspeicher bietet keine Verschlüsselung im Ruhezustand. Das dokumentierte Backup-Werkzeug verschlüsselt Backups nicht und plant/rotiert sie nicht automatisch. Betriebssystem-/Datenträgerverschlüsselung, restriktive Dateirechte sowie eigene Aufbewahrungs- und Löschregeln sind vor realem Betrieb erforderlich. Die Loopback-API akzeptiert dagegen nur begrenzte Ereignismetadaten und weist Bilder, Audio und GPS zurück.
- Betreiber-/Impressums-/Datenschutzfreigabe, Lösch-/Aufbewahrungstests auf realer Hardware, unabhängige Holdout-Validierung, Precision-/Recall-/Fehlalarmmessung und Kamera-/Dauerlauftests fehlen.
- Keine 99-%-Erkennungsrate nachgewiesen; keine KI- oder Feldfreigabe.

## Offene priorisierte Vorgänge

- Monitor [#308](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/308), [#312](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/312), [#318](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/318): historische öffentliche Actions-Artefakte löschen und API-seitig verifizieren.
- Monitor [#93](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/93): Pages-/Datenschutz-/Feldpilot-Release-Gate.
- BeeKeeper3000 [#84](https://github.com/simonthomas-ai/BeeKeeper3000/issues/84): Branch-Schutz für beide Hauptzweige.
- BeeKeeper3000 [#68](https://github.com/simonthomas-ai/BeeKeeper3000/issues/68): technisches Release-Gate für Kamera, Modelle, Datenrechte und Feldabnahme.


# Historischer Statusverlauf

# Deployment-Klarstellung – 26.11.2026, 15:42 UTC (nach PR #321)

- **Beekeeper-Monitor main vor dieser Dokumentationskorrektur:** `af7afd96b6c64bf61580dd5666fc205e16181fa6`; **BeeKeeper3000 main:** `77bd1c012af502afa42b9a79bf9eff0deda37032`.
- Die aktuelle GitHub-Repository-Metadatenabfrage meldet für Beekeeper-Monitor `has_pages=true`, für BeeKeeper3000 `has_pages=false`.
- Im Monitor-`.github/workflows/pages.yml` ist der Deployment-Job weiterhin mit `if: ${{ false }}` gesperrt. In dieser Prüfung wurde kein Pages-Deployment ausgelöst.
- **Wichtige Unterscheidung:** Die Workflow-Sperre deaktiviert nicht automatisch die repositoryweite Pages-Einstellung und entfernt keine ältere Veröffentlichung. Ob ein früherer Pages-Stand noch öffentlich ausgeliefert wird, konnte nicht unabhängig bestätigt werden. Bis zur manuellen Prüfung unter Repository Settings → Pages ist ein älterer öffentlicher Stand als möglich zu behandeln.
- Der aktuelle Build [#45852434471](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45852434471) erzeugte nur das öffentlich lesbare Actions-Artefakt `vespaguard-pwa-preview` (ID `15134318088`, 65.783 Bytes, Ablauf 2026-12-03 15:46:48 UTC). Das ist kein Pages-Deployment. Die Workflow-Stagingliste enthält statische App-Dateien, keine Feldbilder, GPS-Exporte oder Modellgewichte.
- Vor einer Freigabe müssen Pages-Einstellung und gegebenenfalls vorhandene alte Veröffentlichung separat geprüft und ausdrücklich deaktiviert/entfernt werden. Diese Änderung selbst veröffentlicht nichts.

---

# Aktueller Nachtrag – 26.11.2026 (nach PR #320)

## Hauptzweige und integrierte Änderungen
- **Beekeeper-Monitor `main`:** `9115ebb2706c7e335aaee7da144af73933732883`.
- **BeeKeeper3000 `main`:** `77bd1c012af502afa42b9a79bf9eff0deda37032`.
- Monitor PR [#319](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/319) und PR [#320](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/320) sind gemergt.
- PR #320 ergänzt `training/requirements-ci-validation.txt` mit `Pillow==13.0.0` und `PyYAML==6.0.3`, verwendet diese Pins in CC0-/Readiness-/Trainingsdaten-Workflows und führt `pip-audit==2.10.1` verpflichtend im Gesamttest aus. Der Gesamttest nutzt dafür eine isolierte, gepinnte Python-Umgebung statt unversionierter System-Pillow-/PyYAML-Pakete.
- Der erste Auditlauf meldete 42 Advisories für Pillow 12.3.0; der gemeldete Fix war 13.0.0. Die aktualisierte Abhängigkeit wurde im PR-Gesamttest und im nachfolgenden Hauptzweiglauf erfolgreich auditiert.

## CI-Nachweise nach PR #320
- PR-Gesamttest [#45840609187](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45840609187): erfolgreich, einschließlich Python-Abhängigkeitsaudit, Browser-, Safari-WebKit- und iPhone-WebKit-Emulation.
- PR-CodeQL [#45840609351](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45840609351): erfolgreich.
- PR-Artefakt-Policy [#45840609144](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45840609144): erfolgreich.
- Nach-Merge-CodeQL [#45841088202](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45841088202): erfolgreich.
- Nach-Merge-Gesamttest [#45841088098](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45841088098): erfolgreich; alle drei Jobs (Gesamttest, ZIP-/Validator-Export und BeeKeeper-Bridge) sowie alle Browser-, Safari- und iPhone-WebKit-Prüfungen abgeschlossen.
- Nach-Merge-PWA-Build [#45841088048](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45841088048): erfolgreich; öffentlich lesbares statisches Vorschauartefakt `vespaguard-pwa-preview`, ID `15127464985`, 65.783 Bytes, Ablauf 2026-12-03 14:38:47 UTC. Kein Pages-Deployment.
- Nach-Merge-CC0-Discovery [#45841088036](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45841088036): bei Erstellung dieses Nachtrags in Bearbeitung. Install der gepinnten Abhängigkeiten sowie alle Offline-, Rechte-, Hash- und Artefakt-Policy-Tests waren erfolgreich. Noch keine Trainingsfreigabe.
- Readiness [#45841088078](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45841088078) und Trainingsdaten-Inventur [#45841088075](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45841088075): Validator-Jobs erfolgreich; Log meldet weiterhin fehlendes `datasets/beekeeper` und blockiertes Training.

## Öffentliche Actions-Artefakte – manuelle Bereinigung offen
- Fünf historische `vespaguard-private-pwa`-Artefakte sind noch nicht abgelaufen: IDs `15124542124`, `15118529028`, `15115678841`, `15115577897`, `15108012720`. Sie stammen aus fünf erfolgreichen Läufen des alten `private-pwa.yml`. Die geprüfte Staging-Liste enthält nur statische App-Dateien, Manifest/Icon und zwei Wissensseiten; kein Feldbild, GPS-Export oder Modellgewicht. Das Artefakt war dennoch öffentlich lesbar, der Name „private“ war falsch. Manuelle Löschung und API-Rücklese: [Issue #318](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/318).
- Vier historische Review-/CC0-Artefakte bleiben zusätzlich öffentlich zugänglich: `original-velutina-images` (ID `15058597151`), `ki-cc0-quellen-prueflisten` (ID `15058522636`), `inaturalist-balanced-review-queue` (ID `15108851881`) und `insect-photo-review-queue` (ID `15107897872`). Details: [#308](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/308) und [#312](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/312).
- Neue PWA-Vorschauen heißen korrekt `vespaguard-pwa-preview`, weisen auf öffentliche Lesbarkeit hin und laufen nach sieben Tagen ab. Artefakte sind keine Website-Veröffentlichung.
- Die verbundene GitHub-Schnittstelle bietet keine Artefakt-Löschaktion; nichts wurde heruntergeladen oder gelöscht.

## Weiterhin offene Freigaben
- Beide Repositories sind öffentlich; GitHub meldet `license=null` und beide Root-`LICENSE`-Dateien fehlen.
- Beide `main`-Branches melden `protected=false`; Rulesets sind leer. Administrativer Branch-Schutz bleibt offen.
- [BeeKeeper3000 PR #110](https://github.com/simonthomas-ai/BeeKeeper3000/pull/110) bleibt Draft: 2 Commits voraus / 15 zurück; acht Modellfähigkeiten deaktiviert, Kandidaten `rights_and_runtime_pending`.
- Rekursive Tree-Abfragen fanden keine Modellgewichte und keinen freigegebenen Trainingsdatensatz. `datasets/beekeeper/`, `provenance.jsonl` und `training/reviewed-annotations.json` fehlen.
- Der BeeKeeper-Trainer liefert einen Siebenklassen-Klassifikator (`[1,7]`-Logits); der Monitor-Kameraadapter erwartet Detektionen mit Bounding-Boxes. Ein getesteter Adapter fehlt.
- IndexedDB ist nicht zusätzlich anwendungsseitig verschlüsselt. Der Feld-ZIP-Export bereinigt EXIF; allgemeine JSON-Sicherungen können Originalbilder und GPS enthalten.
- GitHub Pages bleibt deaktiviert; keine öffentliche Website wurde durch diese Änderungen veröffentlicht. Betreiber-/Impressums-/Datenschutzfreigabe, unabhängige Holdout-Validierung, Precision/Recall-/Fehlalarmmessung und reale Hardware-Dauerläufe fehlen.
- Keine 99-%-Erkennungsrate nachgewiesen. Keine Fremdgewichte oder Trainingsdaten aktiviert.

---

# Aktueller Nachtrag – 26.11.2026 (nach PR #317)

## Verifizierter Stand beider Hauptzweige
- **Beekeeper-Monitor `main`:** `32b200002c193ae8f2c833f3bb0340346819f3c4`. PR [#317](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/317) ist gemergt. Die PWA-Vorschau heißt jetzt `vespaguard-pwa-preview`, weist ausdrücklich auf öffentliche Lesbarkeit hin und hat 7 Tage Aufbewahrung.
- **BeeKeeper3000 `main`:** `77bd1c012af502afa42b9a79bf9eff0deda37032`.
- Beide Repositories sind öffentlich; die GitHub-API meldet für beide `license=null`. Eine Root-`LICENSE` fehlt jeweils.
- Beide `main`-Branches melden `protected=false`; Rulesets sind leer. Administrativer Status ist in [BeeKeeper3000 #84](https://github.com/simonthomas-ai/BeeKeeper3000/issues/84) dokumentiert. Die verbundene GitHub-Schnittstelle bietet hier keine sichere Mutationsaktion; keine Umgehung.

## Nachweise auf aktuellem Monitor-main
- Ein-Klick-Gesamttest [#45836454835](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45836454835): Workflow erfolgreich; alle drei Jobs (Gesamttest, ZIP-/Validator-Export, BeeKeeper-Bridge) abgeschlossen.
- CodeQL [#45836454992](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45836454992): erfolgreich.
- PWA-Buildvorschau [#45836454799](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45836454799): erfolgreich, Artefakt `vespaguard-pwa-preview`, ID `15125422107`, 65.783 Bytes, Ablauf 2026-12-03 14:11:22 UTC. Das Artefakt ist öffentlich lesbar und enthält laut Workflow/Buildlog nur statische App-Dateien; es ist kein Pages-Deployment.
- Trainingsdaten-Inventur [#45836454860](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45836454860): Validator-Job erfolgreich abgeschlossen, meldet aber ausdrücklich fehlendes Dataset und blockiertes Training.
- CC0-Discovery [#45836454885](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45836454885) wurde inzwischen erfolgreich abgeschlossen; die Artefakt-API liefert für diesen Lauf eine leere Liste. Der nachgelagerte Policy-Audit [#45836983225](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45836983225) war ebenfalls erfolgreich.

## Öffentliche Actions-Artefakte – manuelle Bereinigung bleibt offen
- Der historische, irreführend `vespaguard-private-pwa` genannte Build ist noch vorhanden: Run [#45803405754](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405754), Artefakt-ID `15108012720`, 65.655 Bytes, Ablauf 2026-12-03 10:39:53 UTC. Der geprüfte Workflow beschreibt statische App-Dateien, keine Feldaufnahmen. Löschprüfung separat in [Issue #318](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/318).
- Vier historische Kandidaten-/Review-Artefakte bleiben ebenfalls vorhanden und öffentlich zugänglich: `original-velutina-images` (ID `15058597151`), `ki-cc0-quellen-prueflisten` (ID `15058522636`), `inaturalist-balanced-review-queue` (ID `15108851881`) und `insect-photo-review-queue` (ID `15107897872`). Details und manuelle Löschanforderung: [#308](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/308) und [#312](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/312).
- Die vier Kandidatenartefakte wurden nicht heruntergeladen oder geprüft; sie sind keine Trainingsfreigabe. Die verbundene Schnittstelle kann Artefakte auflisten, bietet aber keine Löschaktion. Kein Download, keine Löschung und keine History-Umschreibung versucht.

## BeeKeeper3000 – aktueller CI- und Integrationsstand
- Quality Gates [#45795479713](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479713), CodeQL [#45795479682](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479682), Supply Chain/SBOM [#45795479697](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479697) und Windows-Station [#45795479670](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479670) waren auf `77bd1c012` erfolgreich.
- Die Quality-Gates-Logs zeigen 22 lokale Medienimporttests und 36 MeshCore-/NMEA-Protokoll-, Empfangs-, Speicher- und Transporttests erfolgreich. Die Supply-Chain-Prüfung erzeugt getrennte SBOMs für MeshCore, NMEA und deklarierte Trainingsabhängigkeiten; sie ist keine vollständige Produkt-SBOM.
- [PR #110](https://github.com/simonthomas-ai/BeeKeeper3000/pull/110) bleibt offen und ist nicht mergebereit: 2 Commits voraus / 15 hinter `main`; der PR-Head-Commit hat keine Statuschecks. Sein Capability-Katalog enthält acht deaktivierte Fähigkeiten und zwei Kandidaten mit `rights_and_runtime_pending`. Keine Inferenzaktivierung.
- Der Trainer exportiert einen Multilabel-Klassifikator mit `[1,7]`-Logits; der vorhandene Kameraadapter erwartet Objektdetektionen mit Bounding-Boxes. Die Verträge sind nicht austauschbar und benötigen einen getrennten, getesteten Adapter.

## KI-, Daten-, Lizenz- und Einsatzfreigabe
- Rekursive Git-Tree-Abfragen beider aktuellen Hauptzweige fanden keine Modellgewichte (ONNX/PyTorch/TensorFlow/TFLite/vergleichbar) und weder `datasets/beekeeper/` noch `training/reviewed-annotations.json`.
- Der aktuelle Monitor-Gesamttest protokolliert in den Logs `STATIC: success`, `BROWSER: success`, `MODEL: success`, aber `ANNOTATIONS: failure`; die fehlende Datensatzprüfung wird als `BLOCKIERT` ausgewiesen. Der grüne Software-Workflow ist keine KI-Freigabe.
- BeeKeeper3000-`LICENSES.md` ist ein vorläufiges Inventar. Die geerbte Hornet3000-Quelle ist dort auf eine begrenzte GPL-3.0-or-later-Teilmenge bezogen; daraus folgt keine Gesamtlizenz für das Repository. PyTorch 2.15.0 hat einen ungeklärten Provenienznachweis und einen zusammengesetzten Lizenz-Ausdruck. Gewichte, Bilder und Datensätze benötigen separate Rechteprüfung.
- Browser-IndexedDB ist nicht zusätzlich anwendungsseitig verschlüsselt. Der Feld-ZIP-Export erzeugt bereinigte PNG-Kopien; allgemeine JSON-Sicherungen können weiterhin Originalbilder und genaue GPS-Daten enthalten.
- GitHub Pages bleibt mit `if: false` deaktiviert; kein öffentliches Deployment ausgelöst. Betreiber-/Impressums-/Datenschutzfreigabe, unabhängige Holdout-Validierung, Precision/Recall/Fehlalarmmessung und reale Kamera-/Hardware-Dauerläufe fehlen.
- Keine 99-%-Erkennungsrate nachgewiesen. Keine Modellgewichte, Trainingsdaten oder privaten Feldaufnahmen aktiviert bzw. übertragen.

---

# Aktueller Nachtrag – 26.11.2026, 14:48 UTC

## Verifizierte Repository-Stände
- **Beekeeper-Monitor:** `b3a9d499a5dc1542fa74190768d915ba907d6250`. PR [#316](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/316) ist gemergt. 22 zuvor nicht gehärtete Workflow-Dateien setzen nun bei jedem Checkout `persist-credentials: false`; der Regressionstest prüft alle Workflow-YAML-Dateien statt einer Teil-Allowlist. Alle 12 PR-getriggerten Workflow-Läufe auf dem geprüften PR-Head waren erfolgreich, darunter Gesamttest, CodeQL, KiCad-ERC und CC0-Artifact-Policy.
- **BeeKeeper3000:** `77bd1c012af502afa42b9a79bf9eff0deda37032`. Quality Gates, CodeQL und Supply-Chain/SBOM auf diesem Stand waren erfolgreich. Die Supply-Chain-Abdeckung bleibt ausdrücklich partiell (u. a. keine vollständige Produkt-SBOM für geerbten C++-Code, Firmware, Modelle oder Datensätze).
- [PR #317](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/317) ist offen: Der bisherige PWA-Artefaktname `vespaguard-private-pwa` war irreführend, weil das Repository öffentlich ist. Die vorgeschlagene Korrektur benennt das Artefakt `vespaguard-pwa-preview`, weist im Artefakt auf öffentliche Lesbarkeit hin und begrenzt die Aufbewahrung auf 7 Tage. Zum Zeitpunkt dieses Nachtrags liefen Gesamttest und CodeQL noch; der CC0-Policy-Lauf war erfolgreich.

## Öffentliche Actions-Artefakte – aktueller Befund
- Die aktuellen Discovery-Workflows veröffentlichen keine ungeprüften Kandidaten-Queues mehr. Der CC0-Hauptzweiglauf [#45823611443](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45823611443) war erfolgreich und die Artefakt-API lieferte eine leere Liste.
- Vier historische Artefakte sind weiterhin vorhanden und öffentlich zugänglich, bis sie manuell gelöscht werden oder ablaufen: `original-velutina-images` (ID `15058597151`), `ki-cc0-quellen-prueflisten` (ID `15058522636`), `inaturalist-balanced-review-queue` (ID `15108851881`) und `insect-photo-review-queue` (ID `15107897872`). Die vollständigen Run-/Größen-/Ablaufdaten stehen in [Issue #312](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/312); #308 dokumentiert die zwei älteren CC0-Artefakte. Keine davon wurde heruntergeladen oder gelöscht.
- Der aktuell noch vorhandene alte PWA-Build `vespaguard-private-pwa` (Artefakt-ID `15118529028`, 65.655 Bytes) ist ebenfalls für Leser des öffentlichen Repositories zugänglich und läuft am 03.12.2026 ab. Er enthält statische App-Dateien, keine Feldaufnahmen. PR #317 korrigiert die irreführende Bezeichnung für künftige Builds.

## Weiterhin gesperrte Freigaben
- GitHub Pages bleibt im Workflow mit `if: false` deaktiviert; keine öffentliche Veröffentlichung wurde ausgelöst.
- Beide Root-`LICENSE`-Dateien fehlen. BeeKeeper3000-`LICENSES.md` ist ein vorläufiges Inventar, keine Gesamtlizenz. Modell-/Gewichts-/Bildrechte bleiben einzeln ungeklärt.
- `datasets/beekeeper` und `training/reviewed-annotations.json` fehlen. Der Hauptzweig-Gesamttest protokolliert `TRAINING: failure`, `ANNOTATIONS: failure` und `KI-STATUS: BLOCKIERT`.
- Der BeeKeeper-Kameraadapter erwartet Bounding-Box-Detektionen; der Trainingsklassifikator exportiert `[1,7]`-Logits. PR [#110](https://github.com/simonthomas-ai/BeeKeeper3000/pull/110) ist weiterhin Draft und laut Commitvergleich 2 Commits voraus / 15 hinter `main`.
- Branch-Protection/Rulesets für beide `main`-Zweige sind laut offenem Governance-Issue [BeeKeeper3000 #84](https://github.com/simonthomas-ai/BeeKeeper3000/issues/84) weiterhin nicht gesetzt. Die verfügbare GitHub-Aktionsschnittstelle bietet keine Branch-Protection-Mutation; nicht umgangen.
- Keine unabhängige Precision-/Recall-/Fehlalarm- oder Standort-Holdout-Validierung und keine reale Hardware-/Dauerlaufabnahme nachgewiesen.

Der nachfolgende 10:45-UTC-Status ist ein historischer Snapshot und nicht mehr der aktuelle Hauptzweigstand.

## Historischer Statussnapshot – Aktualisierung – 26.11.2026, 10:45 UTC

## Geprüfte Hauptzweigstände
- **Beekeeper-Monitor:** `00af387cac734fb591990d752b19036237ee8148`. PR [#311](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/311) ist gemergt. Die sechs öffentlichen Kandidatengalerien sowie der davon abhängige veraltete iNaturalist-Lizenzscraper und sein täglicher Workflow sind aus dem aktuellen Quellbaum entfernt.
- **BeeKeeper3000:** `77bd1c012af502afa42b9a79bf9eff0deda37032`. PR [#127](https://github.com/simonthomas-ai/BeeKeeper3000/pull/127) ist gemergt; Supply-Chain-Inventar und Tests wurden ergänzt.

## Nach Merge bestätigte CI
- Monitor PR-Gesamttest [#45802805309](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45802805309): **success**; CodeQL [#45802805467](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45802805467): **success**; CC0-Publication-Policy [#45802805347](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45802805347): **success**.
- Monitor nach Merge: Ein-Klick-Gesamttest [#45803405659](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405659), CodeQL [#45803405776](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405776), privater Nicht-Deployment-PWA-Build [#45803405754](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405754) und CC0-Publication-Policy [#45803405749](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405749): **success**. Bridge-Integration und Browser-ZIP-Export gegen BeeKeeper3000 waren erfolgreich.
- BeeKeeper3000 auf `77bd1c012`: Quality Gates [#45795479713](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479713), CodeQL [#45795479682](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479682), Supply Chain/SBOM [#45795479697](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479697) und Windows-Station [#45795479670](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45795479670): **success**.
- Im Monitor-Gesamttest bleiben die fachlichen Gates ausdrücklich getrennt: `IMPORTTESTS: success`, aber `TRAINING: failure` und `ANNOTATIONS: failure`. Der Ergebnisbericht setzt `KI-STATUS: BLOCKIERT`. Die Software-CI-Gesamtampel ist keine Trainings- oder KI-Freigabe.

## Öffentliche Review-Artefakte
- Aktueller Monitor-Quellbaum enthält keine der sechs Kandidatengalerien mehr; `scripts/check_live_photo_licenses.py` und `.github/workflows/photo-license-audit.yml` wurden ebenfalls entfernt. Die veralteten Gallery-Regressionen wurden korrigiert; Import-/Static-Tests bestanden.
- Das historische Actions-Artefakt aus Run [#45689841927](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45689841927) besteht weiterhin aus zwei nicht abgelaufenen Artefakten: `original-velutina-images` (161.230.685 Bytes) und `ki-cc0-quellen-prueflisten` (169.351 Bytes), Ablauf 09.12.2026. Es wurde nicht heruntergeladen oder gelöscht. Die verbundene GitHub-Schnittstelle bietet keine Artifact-Delete-Aktion; manuelle Löschung ist in [Issue #308](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/308) nachzuverfolgen. Keine Git-Historie umgeschrieben; Entscheidung dazu siehe [Issue #310](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/310).
- Andere Discovery-Workflows erzeugen weiterhin kurzlebige **Drittquellen-Metadaten**: Main-Läufe [#45803405634](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405634) und [#45803405656](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45803405656) haben die Artefakte `inaturalist-balanced-review-queue` (89.737 Bytes) und `insect-photo-review-queue` (163.198 Bytes) erzeugt. Die Workflow-Dateien weisen CSV/JSON-Review-Metadaten und generierte Galerien aus, keine privaten Beekeeper-Feldbilder, präzisen Bienenstand-GPS-Daten oder Modellgewichte. Da das Repository öffentlich ist, sind diese Artefakte für Repository-Leser zugänglich. Folgeprüfung: [Issue #312](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/312).

## KI, Modelle und Rechte
- Sechs Modellkandidaten besitzen unveränderliche Quellrevisionen, stehen aber alle auf `rights_and_runtime_pending`. Die Git-Trees beider Hauptzweige enthalten keine ONNX-, PyTorch-, TensorFlow- oder vergleichbaren Modellgewichte.
- Der BeeKeeper-Kameraadapter erwartet Objektdetektionen mit Bounding-Boxes; der neue Trainingsklassifikator exportiert `[1,7]`-Logits. Die Verträge sind nicht kompatibel. [PR #110](https://github.com/simonthomas-ai/BeeKeeper3000/pull/110) ist weiterhin Draft, 2 Commits voraus und 15 hinter `main`.
- `datasets/beekeeper` und `training/reviewed-annotations.json` fehlen. Keine unabhängige Precision-/Recall-, Fehlalarm-, Standort-Holdout- oder Feldvalidierung; keine belegte 99-%-Erkennung.
- Beide Repository-Wurzeln haben keine `LICENSE`. BeeKeeper3000-`LICENSES.md` ist ein vorläufiges Inventar, keine Projektlizenz. Upstream-Repository-Lizenzen belegen nicht automatisch Rechte an konkreten Modellgewichten oder Bildern.

## Datenschutz, Sicherheit und Deployment
- Browserdaten in IndexedDB sind nicht zusätzlich anwendungsseitig verschlüsselt. Der Feld-ZIP-Export erzeugt lokal neu codierte PNG-Kopien und entfernt EXIF/GPS-, XMP- und eingebettete Text-/Zeit-Metadaten; allgemeine JSON-Sicherungen können weiterhin Originalbilder und genaue GPS-Daten enthalten. Kein automatischer Upload der lokalen Feldaufnahme.
- Impressum und Datenschutzhinweise enthalten weiterhin nicht bestätigte Betreiber-/Kontaktangaben.
- Monitor-Repository meldet `has_pages=true`; der Pages-Workflow ist manuell auslösbar, aber der Deployment-Job bleibt `if: false`. Die Deployment-Abfrage lieferte keine Einträge; der Live-Stand konnte nicht unabhängig verifiziert werden. Kein öffentliches Deployment ausgelöst.
- Beide `main`-Branches melden `protected=false`, die Ruleset-Abfragen liefern `[]`. Die verbundene GitHub-Schnittstelle bietet keine administrative Schreibaktion für Branch Protection; keine Umgehung vorgenommen.

## Nächste Prioritäten
1. Historische Bild-/Prüflisten-Artefakte aus Run #45689841927 manuell löschen lassen und die Entscheidung zur alten Git-Historie treffen.
2. Die übrigen öffentlichen Review-Metadaten-Artefakte gemäß Issue #312 klassifizieren und ihren Zugriff bewusst festlegen.
3. Beide Hauptbranches administrativ schützen.
4. PR #110 auf aktuellen Stand bringen, ohne Inferenz zu aktivieren; Klassifikations- und Detektionsvertrag sauber trennen.
5. Rechtlich freigegebene, fachlich annotierte Daten und unabhängige Feldvalidierung bereitstellen.

---

# Aktualisierung – 26.11.2026, 05:04 UTC

## Aktueller Repository-Stand

- **Beekeeper-Monitor main:** `84223a6f8a90444c1329516fcc22780b615cbf05` (PR [#301](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/301) gemergt).
- **BeeKeeper3000 main:** `031c91370da85c6fa42dd8992b6adfc20ddf06c7` (PR [#123](https://github.com/simonthomas-ai/BeeKeeper3000/pull/123) gemergt).

## Neue Review-Provenienz im Feldexport

- Jede manuell freigegebene Aufnahme benötigt jetzt eine getrennte pseudonyme `reviewed_by`-Kennung und einen eigenen zeitzonenbewussten `reviewed_at`-Zeitpunkt.
- Der Prüfzeitpunkt stammt aus der lokalen Browser-Uhr; er ist nicht signiert oder vertrauenswürdig bestätigt.
- Die Felder dokumentieren manuelle Bild-/Labelprüfung, **keine** unabhängige Rechteprüfung oder entomologische Bestätigung.
- Der BeeKeeper-Validator verlangt diese Felder und gibt den aus den tatsächlich gelesenen Bildbytes berechneten SHA-256-Wert sowie Rechte-/Review-Metadaten zurück.
- Der Monitor-ZIP-Export enthält `images/` (seit dem geplanten Datenschutz-Update als bereinigte PNG-Kopien) + `annotations.jsonl`. Der getrennte model-manifest-v2-`provenance.jsonl`-Konverter ist in BeeKeeper3000-Commit `63bef0204c063c8b4b17af7b3b26a8021b259c2b` implementiert; Issue [#120](https://github.com/simonthomas-ai/BeeKeeper3000/issues/120) wurde am 26.11.2026 technisch geschlossen. Die source-rights-Prüfung bleibt eine separate Betreiberangabe.

## Tatsächlich geprüfte PR-CI

- Monitor Ein-Klick-Gesamttest [#969](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45758818718): **erfolgreich**.
- Monitor Repository-Integration [#77](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45758818710): **erfolgreich**.
- Monitor CodeQL [#25](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45758818715): JavaScript/TypeScript und Python **erfolgreich**.
- Im Monitor-Feldexportjob: 20 BeeKeeper-Datensatz-Unit-Tests, 10 Playwright-Tests und der Python-Roundtrip **erfolgreich**.
- BeeKeeper3000 PR #123: Quality Gates [#211](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45757989411) und CodeQL [#403](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45757989434) **erfolgreich vor dem Merge**. Ein separater Post-Merge-Hauptzweiglauf war über die verbundene Abfrage nicht verfügbar.

Der Monitor-Gesamttest meldet getrennt:
- `STATIC`, `BROWSER`, `MODEL`, `IMPORTTESTS`, `TAXONOMY`: **success**.
- `TRAINING`, `ANNOTATIONS`: **failure / BLOCKIERT**.
- `datasets/beekeeper` und `training/reviewed-annotations.json` fehlen.
- 23 offene Freigabepunkte. Die erfolgreiche Software-CI ist keine KI-, Rechts- oder Feldfreigabe.

## Weiterhin offene Betriebs- und Rechtsgates

- Alle sechs Modellkandidaten sind nur revisionsgebundene Metadaten mit `rights_and_runtime_pending`; keine Gewichte heruntergeladen oder aktiviert.
- Repository-Lizenzdateien fehlen im Root beider Projekte. `LICENSES.md` ist ein vorläufiges Inventar; Repository-Lizenzen beweisen keine Rechte an konkreten Gewichten oder Trainingsbildern.
- Browserdaten in IndexedDB sind nicht zusätzlich verschlüsselt. Der Feld-ZIP-Export re-encodiert Bilder lokal als PNG und entfernt EXIF/GPS-, XMP- und eingebettete Text-/Zeit-Metadaten aus Exportkopien; Originalbytes bleiben lokal. Andere JSON-Exporte können weiterhin sensible Fotos oder GPS-Daten enthalten.
- Impressum und Datenschutz enthalten weiterhin nicht bestätigte Betreiber-/Kontaktplatzhalter.
- Pages-Deployment bleibt mit `if: false` deaktiviert; kein Deployment wurde ausgelöst. Ein bereits früher veröffentlichter Pages-Stand wird durch diese Workflow-Sperre nicht automatisch entfernt.
- `main`-Branch-Protection/Rulesets sind weiterhin administrativ offen. Sie können über die verbundene GitHub-Schnittstelle nicht geschrieben werden; siehe BeeKeeper3000 [#84](https://github.com/simonthomas-ai/BeeKeeper3000/issues/84) und Monitor [#210](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/210).

## Nächster sicherer Schritt

Der Provenienz-Konverter aus BeeKeeper3000 Issue #120 ist implementiert und per synthetischem Cross-Repository-Roundtrip geprüft. Als nächste Schritte bleiben die Metadatenbereinigung des PWA-ZIP-Exports, reale rechtlich geprüfte Daten, Betreiberfreigaben und die unabhängige KI-Validierung. Reale Bilder, Einwilligungsdokumente, GPS und Produktions-Trainingsdaten bleiben aus CI ausgeschlossen.

---

# Abnahmestand

## Aktualisierung – 26.11.2026

- [x] Monitor-main: aktueller Commit `0be54780d250b2444a5eef82b41c3615f4a94b73` (STATUS-Aktualisierung nach PR #297). Post-Merge-Gesamttest #948 auf Merge-Commit `dd8c7a4650352c0713ce563b2c1d84ea43da3d33` und Gesamttest #949 auf aktuellem main: erfolgreich. Privater PWA-Build #196/#197, CodeQL #4/#5 und Repository-Integration #58: erfolgreich. [Gesamttest #949](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45749834482) · [PWA #197](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45749834413) · [CodeQL #5](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45749834437) · [Repository-Integration #58](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45749756118).
- [x] BeeKeeper3000-main: Commit `2d32e037bcbfec7e60e9f952cc3309001edf12f5`. Quality Gates #192, Network Tests #422, CodeQL #384 und Supply-Chain/SBOM #165 liefen erfolgreich.
- [x] Der Cross-Repository-Feldexport-Job im PR-Lauf #947 und in den Post-Merge-Gesamttests #948/#949 bestand gegen BeeKeeper3000-Commit `2d32e037bcbfec7e60e9f952cc3309001edf12f5`: SHA-Pin geprüft, 18 Validator-Unit-Tests, tatsächlicher PWA-ZIP-Export und Python-Fixture-Roundtrip erfolgreich. PR #297 ist in Monitor-main übernommen.
- [x] Manueller Gerätetest: Kamera- und Mikrofonzugriff auf einem echten iPhone wurden am 20.11.2026 bestätigt. Das ist **kein** KI-Inferenz-, Artenbestimmungs- oder Genauigkeitstest.
- [ ] Kein freigegebenes Modellgewicht, kein vollständiger freigegebener Trainingsbestand und keine unabhängig geprüften KI-Ergebnisse. Training und KI-Feldfreigabe bleiben gesperrt.
- [ ] Öffentliche Pages-Veröffentlichung bleibt deaktiviert. Impressum und Datenschutzhinweise enthalten noch nicht bestätigte Betreiber-/Kontaktangaben.
- [ ] Die Hauptbranches beider Repositories sind weiterhin ungeschützt; Branch-Protection- und Ruleset-Schreibrechte sind über die verbundene GitHub-Integration nicht verfügbar.


## Aktualisierung – 23.11.2026

- [x] Lokaler Feldaufnahme-Workflow in der PWA: manuelle Mehrfachklassifikation nach den sieben unveränderten Taxonomie-Slugs oder explizites Negativbild (`labels: []`); JPEG/JPG, PNG, WebP bis 8 MB.
- [x] Bilder bleiben lokal in IndexedDB. Jede Aufnahme startet ungeprüft; ZIP-Export (`images/` + `annotations.jsonl`) erfordert getrennte manuelle Bild-/Labelprüfung und ausdrückliche Nutzerattestierung. Freitextquelle und Rechte-/Nutzungsangabe sind Nutzereingaben, keine Belege oder unabhängige Rechteprüfung.
- [x] ZIP-Format-Roundtrip mit Mehrfachlabel- und Negativbildfixtures gegen `training/multilabel_dataset.py` im BeeKeeper3000-Hauptzweig geprüft. PR #297 ist gemergt; der Monitor pinnt jetzt unveränderlich BeeKeeper3000-Commit `2d32e037bcbfec7e60e9f952cc3309001edf12f5`. Dessen öffentlicher `scripts/import_mobile_export.py` verarbeitet weiterhin ein separates Metadatenereignis-Format.
- [x] Browser-Tests: vollständiger Chromium-Lauf 34/34; Feldexport gegen den Branch-Validator 4/4 in Chromium und 4/4 in WebKit/iPhone-Emulation; lokale/Partner-Fixtures 7/7. PWA-Static-/Offline-Deployment-Verträge erfolgreich.
- [x] Grundlegender Kamera- und Mikrofonzugriff auf einem echten iPhone am 20.11.2026 bestätigt; dies prüft keine KI-Erkennung. [ ] Vollständiger iPhone-Feldaufnahme-/ZIP-Export-Roundtrip und Langzeittest sind noch nicht belegt; HEIC wird abgelehnt.
- [ ] Kein realer freigegebener annotierter Bildbestand, kein Training, keine Modellgewichte und keine eigene KI-Inferenz. Erkennungsqualität und Feldfreigabe bleiben offen.
- [ ] Öffentlicher Pages-Deploy bleibt deaktiviert; keine Veröffentlichung oder Live-Feldaufnahme aus diesem Statusbericht abgeleitet.

## Aktualisierung – 22.11.2026

- [x] npm-Abhaengigkeiten reproduzierbar fixiert: `package-lock.json` (Lockfile v3) enthaelt `@playwright/test`, `playwright` und `playwright-core` exakt in Version 1.65.1. Installationspruefung mit `npm ci` und `npm ls --all` erfolgreich.
- [x] npm-Sicherheitspruefung in Gesamttest, Chromium- und WebKit-Workflow aufgenommen. Der abschliessende PR-Testlauf [44997049189](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44997049189) meldete **0 bekannte npm-Schwachstellen**; der Gate-Level ist high.
- [x] Woechentliche Dependabot-Updates fuer npm und GitHub Actions aktiviert.
- [x] Playwright 1.65.1 und versionsgleiche Browser-Container in den Browser-Workflows getestet. Im PR-Gesamttest [#878](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45009893327) waren Chromium, Safari/WebKit (18), iPhone-WebKit-Emulation (18), Bildimport-/Lizenzregressionen, Taxonomie, Modell-/Freigabegates und die repo-übergreifende Bridge-Integration erfolgreich.
- [x] Echter Originalbild-Artefaktpfad in GitHub Actions geprueft: [Artefaktlauf #24](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45009893249). 94 von 94 Originaldateien bestanden Bytezahl-/SHA-256-Pruefung; 94 Manifestzeilen; 938 Galerieeintraege ueber sechs Seiten; keine generischen Urheber-Platzhalter.
- [x] Repo-uebergreifende BeeKeeper3000-Bridge-, Offline-Outbox- und HTTP-Recovery-Pruefungen im PR-Gesamttest #878 erfolgreich.
- [x] PR [#267](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/267): GBIF-Galerie- und Review-Importer-Regressionen sind verpflichtender Bestandteil des Gesamttests.
- [x] PR [#268](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/268): GBIF-Review-Queue wird aus demselben begrenzten Byte-Snapshot geparst und gehasht; doppelte CSV-/JSON-Schlüssel und fehlerhafte Zeilen werden abgewiesen.
- [x] PR [#269](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/269): Pages-Auditor prüft lokale Originale per No-Follow-Datei-Handle; Manifest-/Galerieeingaben sind größenbegrenzt und streng geparst. 22 Auditor-Regressionstests erfolgreich.
- [x] GBIF-Regressionen erfolgreich: Discovery 12/12, Galerie 12/12, Review-Importer 21/21.
- [x] BeeKeeper3000 PR [#99](https://github.com/simonthomas-ai/BeeKeeper3000/pull/99) und PR [#103](https://github.com/simonthomas-ai/BeeKeeper3000/pull/103) integriert: Datenschutzsperre deckt camelCase-/Trennzeichen-Aliase, NFKC-Kompatibilitätszeichen und verbleibende nicht-ASCII-basierte Feldnamen ab; Hauptzweig-CodeQL erfolgreich.
- [x] BeeKeeper3000 PR [#104](https://github.com/simonthomas-ai/BeeKeeper3000/pull/104) integriert: lokale Medien-Dateiidentität einschließlich Nachprüfung nach dem Lesen; Windows-Pfad-/Junction-Behandlung korrigiert. Linux- und Windows-Medienimporttests erfolgreich.
- [x] BeeKeeper3000 PR [#105](https://github.com/simonthomas-ai/BeeKeeper3000/pull/105) integriert: checksum-geprüfter NMEA-0183-GNSS-/Heading-Adapter, lokale Koordinatenhaltung, unbestätigte Bearing-Ereignisse und MeshCore-Signaturintegration.
- [x] BeeKeeper3000 PR [#107](https://github.com/simonthomas-ai/BeeKeeper3000/pull/107) integriert: NMEA-Parser- und Fake-Serial-Regressionssuite läuft zusätzlich unter Windows; Linux-/Windows-Qualitätsprüfungen und CodeQL erfolgreich.
- [x] Cross-Repository-Workflow erstmals per Monitor PR [#271](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/271) auf einen unveränderlichen BeeKeeper3000-Commit gepinnt; die Versionsbindung wird bewusst nach erfolgreichen Partner-CI-Läufen aktualisiert.
- [x] BeeKeeper3000 PR [#101](https://github.com/simonthomas-ai/BeeKeeper3000/pull/101) ist integriert: lokaler, ausdrücklich ausgewählter Bild-/Videoimport mit Pfad-/Symlink-, Dateiidentitäts-, Größen-, Pixel-, Frame- und Dauergrenzen. Nur sechs unbestätigte Metadatenfelder gehen in die lokale SQLite-Outbox; kein Medien-Upload und keine automatische Synchronisierung.
- [x] BeeKeeper3000 main commit `3b4f8953c7e82ce96010f5095577830ce90e8361` hat nach Merge Quality Gates [#45016389940](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45016389940) und CodeQL [#45016389962](https://github.com/simonthomas-ai/BeeKeeper3000/actions/runs/45016389962) erfolgreich bestanden; enthalten sind Linux-/Windows-Medien- und NMEA-Tests sowie Python-/JavaScript-CodeQL.
- [x] Monitor PR [#275](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/275) ist gemergt: der Cross-Repository-Workflow pinnt jetzt unveränderlich BeeKeeper3000 main `3b4f8953c7e82ce96010f5095577830ce90e8361`. HTTP-/Bridge-/Replay-Integration [#45016601041](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45016601041) und der vollständige PR-Gesamttest [#45016601035](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45016601035) erfolgreich.
- [x] Post-merge-Prüfung für Monitor main commit `9b7a623e477cdd2d01c604a5c75eb383153cdb2a` erfolgreich: Gesamttest [#45016761916](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45016761916), Repository-Integration [#45016761891](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45016761891), privater PWA-Build [#45016761905](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45016761905) sowie BeeKeeper3000-Bridge-Integration; alle vier Checks erfolgreich.
- [x] Offene Dependabot-PRs in beiden Repositories geprüft: am 22.11.2026 keine offenen Dependabot-PRs. Neue Bot-PRs müssen weiterhin einzeln mit ihren eigenen CI-Läufen geprüft werden.
- [ ] Oeffentlicher Pages-Deploy bleibt deaktiviert. Impressum und Datenschutzhinweise enthalten weiterhin offene Betreiber-/Kontaktangaben; keine Veroeffentlichung ohne vollstaendige rechtliche Pruefung und ausdrueckliche Freigabe.
- [ ] **KI-Status bleibt BLOCKIERT:** Das reale Trainingsdatenverzeichnis `datasets/beekeeper` fehlt; `training/reviewed-annotations.json` mit fachlich bestaetigten Annotationen fehlt ebenfalls. Keine freigegebenen Modellgewichte, keine gemessene Erkennungsgenauigkeit und keine Feldfreigabe.


Letzte Bestandsaufnahme: 22.11.2026. Aktuelle Hauptzweig-Commits: BeeKeeper3000 `7c1379793eed98900dfea22968f6e0c3dab42d07`; Beekeeper-Monitor `702f55e642c077d42537983c5c0f45bee450e2be`. Der letzte hier einzeln nachgeprüfte [Gesamttest #896](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45034307634) gehört zum PR-Commit `bb23a922069c2ad6a8e684c0d6fe1c9f0496648d`: beide Jobs erfolgreich. Ein separater erfolgreicher Workflowlauf für den nachfolgenden Monitor-Merge-Commit `702f55e` ist damit **nicht** belegt. Die Bridge-Integration ist absichtlich auf den zuvor geprüften BeeKeeper3000-Commit `3b4f8953c7e82ce96010f5095577830ce90e8361` gepinnt; das ist nicht der aktuelle BeeKeeper3000-Hauptzweig. Die Trainingsdaten- und Annotationsschritte nutzen `continue-on-error`; ihre grünen Schrittanzeigen belegen keine Freigabe. Feld-, KI-, Datenschutz- und Rechtsfreigaben bleiben offen.

> Die folgenden früheren Abnahmenachweise dokumentieren die jeweils genannten Teststände. Sie sind keine automatische Aussage über den aktuellen Live-Deployment- oder Feldstatus.

## Aktuelle Aktualisierung – 21.11.2026

- [x] PWA-Sicherungsimport gehärtet: PR [#202](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/202) in `main` übernommen. Der Import validiert die Sicherung vor dem Schreiben, lehnt doppelte IDs und aktive SVG-Inhalte ab und übernimmt neue Datensätze in einer einzigen IndexedDB-Transaktion. Vorhandene Datensätze werden nicht überschrieben.
- [x] PR [#203](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/203): exakt dekodierte 8-MiB-Bildgrenze beim Restore und präzisierte Deployment-/Statusdokumentation.
- [x] PR [#204](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/204): veraltete Chromium-/WebKit-Assertions an die neuen Statusmeldungen angepasst.
- [x] Validator und Regressionstests für PNG, JPEG, WebP, GIF, AVIF, HEIC und HEIF ergänzt; der Import begrenzt die dekodierte Bildgröße auf 8 MiB.
- [ ] Aktuelle GitHub-Pages-Veröffentlichung für den neuesten `main`-Stand ist **nicht nachgewiesen**. `impressum.html` und `datenschutz.html` enthalten weiterhin Betreiber-/Kontakt-Platzhalter. Der Veröffentlichungsworkflow sperrt solche Inhalte absichtlich. Die README-Adresse ist daher nur die vorgesehene URL; sie belegt nicht, dass der aktuelle Quellstand live ist.
- [ ] Post-Merge-Verifikation für PR #204: Die vorherigen Läufe [Browser #44903499784](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44903499784) und [WebKit/iPhone #44903499890](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44903499890) scheiterten ausschließlich an veralteten Text-Erwartungen in `tests/browser.spec.cjs` (3 Assertions je Engine). PR #204 aktualisiert diese Erwartungen. Ein neuer erfolgreicher Lauf auf dem anschließenden `main`-Commit ist noch nicht dokumentiert.
- [ ] Modell-Readiness bleibt bewusst blockiert: Der Gesamttest [#44903499860](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44903499860) meldete 0 Bilder/Labels in train/val/test, kein Provenienzmanifest und keine fachlich freigegebenen Annotationen. Die Trainingsfreigabe darf nicht durch Beispieldaten oder abgeschwächte Gates künstlich grün gemacht werden.
- [ ] Schutzregeln für `main` bleiben ein offener Administrationspunkt; siehe [BeeKeeper3000 Issue #84](https://github.com/simonthomas-ai/BeeKeeper3000/issues/84), das beide Projekt-Repositories betrifft.

## Historischer Software- und Feldstatus

Die nachfolgenden Häkchen beziehen sich auf die dokumentierten Läufe und Tests vom 20.11.2026 und frühere Nachweise. Sie ersetzen nicht die offenen Freigabegates weiter unten.

## Automatisierte Softwareprüfung
- [x] Reale lokale Softwarestrecke Quelle → Node-Bridge → authentifizierter Monitor-HTTP-Eingang → SQLite-Speicher per End-to-End-Test geprüft
- [x] 205 Ereignisse über Cursor-Seiten 100/100/5 zugestellt
- [x] Bridge-Neustart mit gespeichertem Cursor geprüft; keine zusätzliche Zustellung
- [x] Vollständiger Replay geprüft; 205 Wiederholungen führten weiterhin zu nur 205 gespeicherten Ereignissen
- [x] Prüft, dass Bild-, Audio- und GPS-Daten nicht an den Monitor weitergereicht werden und KI-Kandidaten unbestätigt bleiben
- [x] Python-/Integrations-, Browser- und WebKit-/iPhone-Emulationstests im GitHub-CI erfolgreich
- [x] Historischer PWA-Deployment-Workflow auf GitHub Pages war für einen früheren Stand erfolgreich; nicht als Nachweis für den aktuellen `main`-Stand verwenden
- [x] Per-Bild-Provenienz-Gate: SHA-256, Quellen-URL, konkrete Medienlizenz, Attribution, Gruppen-Split, geprüfte Art- und Boxannotation
- [x] Trainingsfreigabe blockiert unbekannte, NC-/ND- oder unvollständig belegte Medienrechte
- [x] Trainingsvalidierung prüft sieben Klassen, Bild-/Label-Abgleich, Bounding-Box-Grenzen und Split-Leckage
- [x] Lokale, abschaltbare Schwellwert-Warnung für Velutina-Kandidaten (Regeln per Node-Test geprüft; nur bei geöffneter, verbundener Seite; immer als unbestätigter Verdacht gekennzeichnet)

## Derzeitige Detektor-Aufgabe

Der aktuelle Kameradetektor ist als **ein experimenteller siebenklassiger Insekten-Detektor** für den Velutina-Einsatz konzipiert:

1. vespa_velutina
2. vespa_crabro
3. other_vespidae
4. apis_mellifera
5. bombus_spp
6. syrphidae
7. other_insect

Die sieben Kategorien sind eine vorläufige technische Taxonomie. Die Softwareverträge, Manifestprüfung und Trainings-Gates sind implementiert. Das ist **kein Nachweis einer einsatzfähigen KI**.

- [ ] Vollständiger, lizenziell freigegebener und menschlich annotierter siebenklassiger Bildbestand
- [ ] Unabhängig geprüfte Modellgewichte mit geklärter Lizenz und reproduzierbarem SHA-256
- [ ] Unabhängiger Testbestand aus unbekannten Standorten, Kameras und Aufnahmebedingungen
- [ ] Je Klasse Präzision, Recall, Konfusionsmatrix und Konfidenzintervalle
- [ ] Falschalarme und übersehene Tiere pro Stations-/Betriebszeit messen
- [ ] Schwellwerte anhand eines separaten Validierungsbestands kalibrieren
- [ ] Entomologische Prüfung der schwierigen Verwechslungsklassen

Varroa, Drohnenbrut, Pollen, Schwarm und Königin sind andere Bildaufgaben. Sie gehören nicht in diesen siebenklassigen Insekten-Detektor und benötigen je eine eigene Datengrundlage, Modellfreigabe und Abnahme.

## Noch nicht auf realen Geräten oder im Feld abgenommen

- [ ] Installer auf einem echten Raspberry Pi / Debian-Gerät installiert, aktualisiert und zurückgerollt
- [ ] Windows-Station mit realer Kamera und freigegebenem ONNX-Modell im Dauerbetrieb geprüft
- [ ] Kamerawinkel, Entfernung, Beleuchtung, Regen, Gegenlicht, Nachtbetrieb und saisonale Bedingungen erfasst
- [ ] PWA auf echten iPhones und Android-Geräten installiert und bedient
- [ ] Offline-Protokollierung, Wiederanlauf und Wiederherstellung auf realen Geräten geprüft
- [ ] Restore-Drill auf einer produktionsähnlichen Kopie aller Stationsdaten einschließlich Bridge-Checkpoint durchgeführt
- [ ] MeshCore mit echten Geräten, Antennen und mehreren Stationen über eine dokumentierte Feldstrecke geprüft
- [ ] Funkreichweite, Airtime, Energiebedarf und zulässige Funkparameter am Einsatzort geprüft
- [ ] Triangulation anhand bekannter, vermessener Zielpositionen und kalibrierter Peilungen validiert
- [ ] Unabhängiger Datenschutz- und Sicherheitstest abgeschlossen
- [ ] Rollen, Speicherfristen, Export/Löschung, Backups, Zugriffe und Vorfallabläufe organisatorisch geprüft
- [ ] Codeberg-Synchronisierung eingerichtet und getestet
- [ ] Pilotbetrieb an mehreren voneinander unabhängigen Standorten abgeschlossen und ausgewertet

## Installations- und Betriebshinweise

BeeKeeper3000 enthält einen Windows-Launcher und einen Linux/systemd-Basisinstaller für Monitor, Quelljournal und Bridge. Die GitHub-CI validiert die Skripte, die Struktur, den Windows-Backup-/Restore-Test mit synthetischen Daten sowie die Linux-Voraussetzungs- und Service-Hardening-Prüfungen.

Diese CI-Ergebnisse sind keine Installation auf dem Nutzer-PC, keinem echten Raspberry Pi und kein physischer Restore-Drill. Kamera und MeshCore werden durch den Linux-Basisinstaller absichtlich nicht automatisch aktiviert.

**Gesamtstatus:** Die lokale Software- und Monitor-Übertragung ist automatisiert geprüft. Kamera-/KI-Qualität, reale Stationen, MeshCore, Triangulation, Datenschutz-Feldfreigabe und Pilotbetrieb bleiben offen. Die Anwendung darf bis zur Abnahme nur als Beobachtungs- und Suchhinweissystem, nicht als bestätigende Artbestimmung oder Grundlage für Nestzerstörung verwendet werden.
