# Abnahmestand

Letzte Bestandsaufnahme: 21.11.2026.

> Die folgenden früheren Abnahmenachweise dokumentieren die jeweils genannten Teststände. Sie sind keine automatische Aussage über den aktuellen Live-Deployment- oder Feldstatus.

## Aktuelle Aktualisierung – 21.11.2026

- [x] PWA-Sicherungsimport gehärtet: PR [#202](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/202) in `main` übernommen. Der Import validiert die Sicherung vor dem Schreiben, lehnt doppelte IDs und aktive SVG-Inhalte ab und übernimmt neue Datensätze in einer einzigen IndexedDB-Transaktion. Vorhandene Datensätze werden nicht überschrieben.
- [x] Validator und Regressionstests für PNG, JPEG, WebP, GIF, AVIF, HEIC und HEIF ergänzt; der Import begrenzt die dekodierte Bildgröße auf 8 MiB.
- [ ] Aktuelle GitHub-Pages-Veröffentlichung für den neuesten `main`-Stand ist **nicht nachgewiesen**. `impressum.html` und `datenschutz.html` enthalten weiterhin Betreiber-/Kontakt-Platzhalter. Der Veröffentlichungsworkflow sperrt solche Inhalte absichtlich. Die README-Adresse ist daher nur die vorgesehene URL; sie belegt nicht, dass der aktuelle Quellstand live ist.
- [ ] Neue Regressionstests aus PR #202 müssen in den zugehörigen GitHub-Actions-Läufen erfolgreich nachgewiesen werden. Die in dieser Bestandsaufnahme verfügbaren Status-Endpunkte lieferten für den Merge-Commit keine auslesbaren Checks; daher wird kein grüner Lauf behauptet.
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
