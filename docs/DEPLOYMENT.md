# Automatische Veröffentlichung und Betriebsprüfungen

## Aktueller Veröffentlichungsstatus – 21.11.2026

Die GitHub-Pages-URL ist die vorgesehene öffentliche Adresse, aber die Veröffentlichung des aktuellen `main`-Quellstands ist derzeit nicht nachgewiesen. `impressum.html` und `datenschutz.html` enthalten noch Platzhalter für Betreiberidentität, Anschrift und Kontakt. Der Pages-Workflow erkennt diese Angaben und bricht vor dem Upload des Veröffentlichungsartefakts absichtlich ab.

**Diese Sperre nicht umgehen und keine Betreiber- oder Rechtsdaten erfinden.** Erst nach Eintragung und Prüfung der echten Angaben darf ein Pages-Deployment erfolgreich sein. Ein früherer erfolgreicher Pages-Lauf belegt nicht, dass der aktuelle Stand veröffentlicht ist.

## Automatische Abläufe

- **Aktueller Stand:** `.github/workflows/pages.yml` ist ausschließlich manuell auslösbar und der Job `deploy` hat ausdrücklich `if: ${{ false }}`. Weder Push noch manueller Start veröffentlichen die Website.
- Pushes auf `main` starten Softwaretests, aber keine PWA-Buildvorschau. Die PWA-Buildvorschau wird nur über ein ausdrückliches `workflow_dispatch` im Workflow `.github/workflows/private-pwa.yml` erzeugt; sie veröffentlicht keine Website.
- Der CC0-Rechercheworkflow lädt Bildbytes nur vorübergehend in den isolierten GitHub-Runner, um Dateiformat und technische Lesbarkeit zu prüfen. Die Originalbild-Arbeitsdateien werden vor Ende des Jobs entfernt.
- Der CC0-Rechercheworkflow veröffentlicht weder Originalbild-Artefakte noch Kandidaten-Metadaten-Artefakte. Er schreibt nur aggregierte Prüfergebnisse in die Actions-Zusammenfassung und entfernt danach die erzeugten CSV-, JSON- und HTML-Prüflisten.
- `.github/workflows/gallery-original-artifact-audit.yml` prüft nach einem erfolgreichen CC0-Lauf anhand genau dieser Run-ID, dass keine Kandidaten-Artefakte veröffentlicht wurden.
- GitHub Pages übernimmt ausschließlich `review/index.html` als Statusseite. Kandidatengalerien, Originalbilder, Bildmanifeste und Review-Identitäten werden nicht in die öffentliche Website gestagt.
- Die lokalen Rechte-/SHA-256-Audits und ihre synthetischen Unit-Tests bleiben für eine spätere geschützte manuelle Prüfung verfügbar; sie sind keine öffentliche Veröffentlichung und keine Trainingsfreigabe.
- `.github/workflows/browser.yml` prüft die Integration mit Chromium.
- `.github/workflows/site-health.yml` prüft täglich die öffentliche Adresse und fünf Dateien.
- `.github/workflows/sources.yml` prüft wöchentlich den Katalog der Forschungsquellen.
- `.github/workflows/training-data.yml` schlägt absichtlich fehl, solange echte beschriftete Trainingsbilder fehlen.

## Unveränderliche CI-Container und Action-Pins

Die Browser- und Gesamttests verwenden `@playwright/test` 1.65.1 zusammen mit dem passenden Microsoft-Playwright-Container. Der OCI-Image-Index für `mcr.microsoft.com/playwright:v1.65.1-noble` ist zusätzlich mit dem geprüften Registry-Digest `sha256:1507cbfc550a63a6b7396791ca4f00df17beb56342d2447b3f106c306f525579` fixiert. Dadurch wird nicht nur der Versionsname, sondern genau der registrierte Container-Inhalt verwendet. Quelle: [Microsoft Artifact Registry – Playwright-Tags](https://mcr.microsoft.com/en-us/product/playwright/tags).

Der verpflichtende Workflow-Audit `scripts/audit_workflow_action_pins.py` prüft sowohl externe `uses:`-Referenzen auf vollständige 40-stellige Commit-SHAs als auch Workflow-`image:`-Referenzen auf einen SHA-256-OCI-Digest. Lokale Actions sind zulässig; Docker-Actions müssen ebenfalls Digest-gepinnt sein. Neue Browser-/Build-Container und Dependabot-Änderungen müssen diesen Audit bestehen, bevor sie übernommen werden.


## Sichtbarkeit der PWA-Buildvorschau

Das Repository ist öffentlich. Das Actions-Artefakt `vespaguard-pwa-preview` ist deshalb für alle Personen mit Repository-Leserechten herunterladbar und **nicht privat**. Es enthält nur statische PWA-Dateien und einen Hinweistext; keine Benutzerfotos, Bienenstand-GPS-Daten, Secrets oder Modellgewichte. Die Aufbewahrung ist auf 1 Tag begrenzt. Das Artefakt ist kein Pages-Deployment und erzeugt keine gehostete Website.

## Öffentliche CI-Testartefakte

Das Repository ist öffentlich; Actions-Artefakte sind daher nicht privat. Die Browser-/WebKit-Fehlerdiagnosen werden nur bei fehlgeschlagenen, manuell gestarteten Läufen gespeichert und nach einem Tag entfernt. Der Gesamttest-Bericht und der Bericht der autonomen Projektsteuerung werden nur nach ausdrücklichem `workflow_dispatch` hochgeladen und ebenfalls einen Tag aufbewahrt. Der wöchentliche autonome Lauf veröffentlicht damit keine Browser-Traces als Artefakt.

Andere Workflows erzeugen getrennte technische Artefakte wie Taxonomie-CSV, KiCad-Prüfberichte, Provenienzberichte und SBOMs. Diese sind ebenfalls öffentlich und haben eigene Aufbewahrungsfristen. Vor jeder Erweiterung ihrer Inhalte ist zu prüfen, dass keine Benutzerbilder, GPS-Daten, Tokens, privaten Notizen oder sonstigen personenbezogenen Daten enthalten sind.

## Originalbild-Prüfung und Datenzugriff

Der CC0-Workflow darf Originalbilder nur transient auf dem GitHub-Runner prüfen. Er speichert keine Originalbytes in Actions-Artefakten, im Repository oder auf Pages. Die erzeugten Kandidatenlisten und Galerien enthalten öffentliche Quellenmetadaten und werden nach der aggregierten Zusammenfassung ebenfalls aus dem Runner-Arbeitsverzeichnis entfernt.

Die technische Bildprüfung belegt ausschließlich, dass eine Datei lesbar war und bestimmte Format-/Größengrenzen erfüllte. Sie bestätigt weder die tatsächliche Urheberschaft noch die individuelle Medienlizenz, die Artbestimmung, eine Bounding-Box-Annotation oder eine Trainingsfreigabe.

Die früheren öffentlichen Artefakte `original-velutina-images` und `ki-cc0-quellen-prueflisten` sind Altbestände aus vorangegangenen Läufen. Sie dürfen nicht als freigegebener Datensatz verwendet werden. Ihre manuelle Löschung aus der Actions-Artefaktverwaltung ist gesondert nachzuweisen; das Ende neuer Uploads löscht bereits vorhandene Artefakte nicht rückwirkend.

Für eine spätere interne Prüfung müssen konkrete Originalmedien nach individueller Rechteprüfung in einem zugriffsgeschützten lokalen Verzeichnis bereitgestellt werden. Keine privaten Fotos, genauen Apiary-Koordinaten oder vertraulichen Rechtebelege in öffentliche Issues, Repositories oder Actions-Artefakte hochladen.

## Einmalige GitHub-Einstellung
Unter **Settings > Pages > Build and deployment > Source** muss **GitHub Actions** ausgewählt sein. Der Workflow kann diese Einstellung nicht garantieren. Veröffentlichungsfehler unter **Actions** prüfen.

## Öffentliche Review-Daten

Die früheren Originalbild- und Kandidatenlisten-Artefakte sind keine Trainingsfreigabe. Neue CC0-Läufe veröffentlichen keine solchen Artefakte. Die öffentliche Review-URL zeigt nur eine Statusseite; die Kandidatengalerien bleiben bis zur unabhängigen Rechte- und Fachprüfung privat. Die sechs früher eingecheckten Kandidatengalerien sind aus dem aktuellen Quellbaum entfernt; ältere öffentliche Commits enthalten sie weiterhin. Eine History-Umschreibung erfordert eine gesonderte Eigentümerentscheidung (Issue #310).

## Öffentliche Adresse (derzeit NICHT als erreichbar bestätigt)\nhttps://simonthomas-ai.github.io/Beekeeper-Monitor/\n\nDie Unterseite `/varroa.html` ist im Repository und im privaten Build vorhanden, aber öffentlich erst nach einem erfolgreichen Pages-Deployment erreichbar. Ein HTTP-404 ist bis dahin erwartbar. Vor einem öffentlichen Testbetrieb müssen die tatsächlichen Betreiber-/Kontaktangaben und Datenschutzhinweise geprüft und ergänzt werden. Danach kann der Pages-Workflow kontrolliert wieder aktiviert werden.

## Funktionsgrenzen
Diese Veröffentlichung ist eine **PWA zur manuellen Beobachtung**, keine fertig trainierte oder feldvalidierte KI. Automatische Modellausführung ist in diesem Build deaktiviert: Es fehlen lokal verfügbare, freigegebene Gewichte und unabhängige Validierung. Die frühere experimentelle Hornet3000-Laufzeit wird nicht geladen oder veröffentlicht. Zeitgesteuerte GitHub Actions laufen nach bestem Bemühen und ersetzen keinen dauerhaft laufenden Rechner. Kamera, Standortzugriff, Offline-Neustart und Sicherungsimport müssen auf echten iPhones geprüft werden. Automatische SMS, Server-Push, Triangulation, Unterstützung aller 24 EU-Sprachen und eine validierte Erkennungsgenauigkeit von 99 % sind noch nicht implementiert.

## Lokale Warnung bei Überschreiten eines Schwellwerts (freiwillig)
Die PWA kann vor unbestätigten `vespa_velutina`-Kandidaten aus dem lokalen Stationsempfänger (`camera_detection` / `acoustic_event`) warnen. Der einstellbare Konfidenzschwellwert liegt standardmäßig bei 100 % und mindestens bei 50 %. Die Funktion ist zunächst deaktiviert und arbeitet nur, solange die Seite geöffnet, über `http://127.0.0.1:8765/` verbunden und mit dem Empfängerschlüssel authentifiziert ist. Ein geschlossener Tab bedeutet: keine Warnung.

Mögliche Hinweise sind ein Banner, ein Ton und nach Einwilligung eine Systembenachrichtigung. Jedes Ereignis wird einmal gemeldet; Ereignisse älter als 15 Minuten werden ignoriert und eine fünfminütige Sperrzeit begrenzt Wiederholungen. Jede Warnung bleibt ausdrücklich ein **unbestätigter Verdacht eines nicht validierten Modells**, keine sichere Artbestimmung. Fernbenachrichtigungen und SMS benötigen einen gesondert geprüften und datenschutzrechtlich bewerteten Dienst.
