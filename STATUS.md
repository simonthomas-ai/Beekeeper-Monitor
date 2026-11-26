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
