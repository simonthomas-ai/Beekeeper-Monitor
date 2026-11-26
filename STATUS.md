# Abnahmestand

## Aktualisierung – 26.11.2026

- [x] Monitor-main: Commit `122811dd322aeb1b955a8e7179c01634e50db317`. Der Push-Gesamttest #946, der private PWA-Build #195 und CodeQL #2 liefen erfolgreich: [Gesamttest](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45746689512), [PWA](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45746689475), [CodeQL](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/45746689485).
- [x] BeeKeeper3000-main: Commit `2d32e037bcbfec7e60e9f952cc3309001edf12f5`. Quality Gates #192, Network Tests #422, CodeQL #384 und Supply-Chain/SBOM #165 liefen erfolgreich.
- [x] Der Cross-Repository-Feldexport-Job im Monitor-Gesamttest #946 bestand: 18 Validator-Unit-Tests, der tatsächliche PWA-ZIP-Export gegen den gepinnten BeeKeeper3000-Validator und den Python-Fixture-Roundtrip. Dieser Lauf verwendete noch den älteren Pin `1f484025600951c359a573a410bb3b239cfbe6ae`; ein separater PR aktualisiert die Integration auf den aktuellen Bee-main-Commit.
- [x] Manueller Gerätetest: Kamera- und Mikrofonzugriff auf einem echten iPhone wurden am 20.11.2026 bestätigt. Das ist **kein** KI-Inferenz-, Artenbestimmungs- oder Genauigkeitstest.
- [ ] Kein freigegebenes Modellgewicht, kein vollständiger freigegebener Trainingsbestand und keine unabhängig geprüften KI-Ergebnisse. Training und KI-Feldfreigabe bleiben gesperrt.
- [ ] Öffentliche Pages-Veröffentlichung bleibt deaktiviert. Impressum und Datenschutzhinweise enthalten noch nicht bestätigte Betreiber-/Kontaktangaben.
- [ ] Die Hauptbranches beider Repositories sind weiterhin ungeschützt; Branch-Protection- und Ruleset-Schreibrechte sind über die verbundene GitHub-Integration nicht verfügbar.


## Aktualisierung – 23.11.2026

- [x] Lokaler Feldaufnahme-Workflow in der PWA: manuelle Mehrfachklassifikation nach den sieben unveränderten Taxonomie-Slugs oder explizites Negativbild (`labels: []`); JPEG/JPG, PNG, WebP bis 8 MB.
- [x] Bilder bleiben lokal in IndexedDB. Jede Aufnahme startet ungeprüft; ZIP-Export (`images/` + `annotations.jsonl`) erfordert getrennte manuelle Bild-/Labelprüfung und ausdrückliche Nutzerattestierung. Freitextquelle und Rechte-/Nutzungsangabe sind Nutzereingaben, keine Belege oder unabhängige Rechteprüfung.
- [x] ZIP-Format-Roundtrip mit Mehrfachlabel- und Negativbildfixtures gegen `training/multilabel_dataset.py` im BeeKeeper3000-Hauptzweig geprüft. Der aktuelle Monitor-Cross-Repo-Lauf #946 verwendete den damals gepinnten Commit `1f484025600951c359a573a410bb3b239cfbe6ae`; ein PR aktualisiert die Pins auf den aktuellen BeeKeeper3000-main-Commit `2d32e037bcbfec7e60e9f952cc3309001edf12f5`. Dessen öffentlicher `scripts/import_mobile_export.py` verarbeitet weiterhin ein separates Metadatenereignis-Format.
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
