# Aktualisierung – 26.11.2026

## Aktueller Repository-Stand
- **Beekeeper-Monitor main:** `8ec2270a79056ed20bf5c6af65d8731c0fb75ea0` (PR #302, Auditstatus aktualisiert).
- **BeeKeeper3000 main:** `63bef0204c063c8b4b17af7b3b26a8021b259c2b` (PR #124, Provenienzkonverter gemergt).

## Neue Provenienzkonvertierung
- BeeKeeper3000 PR [#124](https://github.com/simonthomas-ai/BeeKeeper3000/pull/124) ist gemergt.
- Der lokale Konverter erstellt aus einem bereits validierten ZIP deterministisch `provenance.jsonl` und `training_data_sources.json`.
- Eine separate source-rights-Reviewdatei ist Pflicht. Die Nutzerattestierung `rights.status=training_approved` wird niemals automatisch zu `license_review_status=approved` hochgestuft.
- Lokale Feldaufnahmen verwenden `local-capture://<opaque-id>` und die SHA-256-Prüfsumme des exakt validierten ZIP-Snapshots. Öffentliche Quellen benötigen eine unveränderliche Revision und kanonische CC0-/CC-BY-Nachweise.
- BeeKeeper-PR-CI: Quality Gates #45761113773 und CodeQL #45761113708 erfolgreich; 15/15 neue synthetische Converter-/Manifest-Roundtriptests bestanden. Post-Merge-Hauptzweigläufe sind separat zu prüfen.

## Repository-übergreifende Ende-zu-Ende-Prüfung
- Monitor PR [#303](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/303) ergänzt den tatsächlichen PWA-ZIP-Export um den vollständigen synthetischen Pfad: ZIP-Validator → Provenienzkonverter → model-manifest-v2-Validator.
- Beide Monitor-Integrationsworkflows und der Partner-Pin-Test werden auf BeeKeeper3000 `63bef0204c063c8b4b17af7b3b26a8021b259c2b` festgelegt.
- PR #303 ist noch offen; erst nach erfolgreicher CI ist dieser Cross-Repository-Pfad bestätigt.

## Weiterhin gesperrt
- Keine realen Trainingsdaten/Annotationen im Repository; `datasets/beekeeper` und `training/reviewed-annotations.json` fehlen weiterhin.
- Keine freigegebenen Modellgewichte, keine automatische Hornissen-/Varroa-Inferenz und keine unabhängige Genauigkeits- oder Feldvalidierung.
- Source-rights-Review bleibt eine Betreiberangabe und ersetzt keinen externen Rechtsnachweis.
- Root-Projektlizenzen, DSGVO-Betreiberangaben, EXIF-/GPS-Bereinigung und Browserdatenverschlüsselung sind weiterhin offen.
- Branch Protection bleibt administrativ offen; die GitHub-Integration liefert für die klassische Protection-API HTTP 403 und die Ruleset-Abfrage keine Regeln.
- Öffentliche Pages-Veröffentlichung wurde nicht ausgelöst; der Deployment-Job bleibt gesperrt.

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
- Der Monitor-ZIP-Export bleibt `images/` + `annotations.jsonl`; der getrennte model-manifest-v2-`provenance.jsonl`-Konverter aus BeeKeeper3000 Issue [#120](https://github.com/simonthomas-ai/BeeKeeper3000/issues/120) fehlt weiterhin.

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
- Browserdaten in IndexedDB sind nicht zusätzlich verschlüsselt. Originalbilder können EXIF/GPS enthalten; der ZIP-Export entfernt diese Metadaten nicht und wird nur nach ausdrücklicher Nutzeraktion lokal erzeugt.
- Impressum und Datenschutz enthalten weiterhin nicht bestätigte Betreiber-/Kontaktplatzhalter.
- Pages-Deployment bleibt mit `if: false` deaktiviert; kein Deployment wurde ausgelöst. Ein bereits früher veröffentlichter Pages-Stand wird durch diese Workflow-Sperre nicht automatisch entfernt.
- `main`-Branch-Protection/Rulesets sind weiterhin administrativ offen. Sie können über die verbundene GitHub-Schnittstelle nicht geschrieben werden; siehe BeeKeeper3000 [#84](https://github.com/simonthomas-ai/BeeKeeper3000/issues/84) und Monitor [#210](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/210).

## Nächster sicherer Schritt

Den Provenienz-Konverter in BeeKeeper3000 Issue #120 implementieren. Er muss eine separate source-level-Rechteprüfung verlangen und darf die Nutzerattestierung `rights.status=training_approved` **nicht** automatisch in `license_review_status=approved` umdeuten. Danach ZIP → Validator → `provenance.jsonl` → model-manifest-v2-Validierung mit synthetischen Fixtures durchtesten. Reale Bilder, Einwilligungsdokumente, GPS und Trainingsdaten bleiben aus CI ausgeschlossen.

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
