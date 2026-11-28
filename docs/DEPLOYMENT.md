# Automatische Veröffentlichung und Betriebsprüfungen

## Aktueller Veröffentlichungsstatus – 27.11.2026

Die Repository-API meldet für das öffentliche Repository `simonthomas-ai/Beekeeper-Monitor` weiterhin `has_pages=true`. Der Inhalt und die Erreichbarkeit einer eventuell bereits veröffentlichten Pages-Seite wurden in dieser Prüfung nicht verifiziert. Deshalb darf weder von einer aktiven noch von einer abgeschalteten Alt-Veröffentlichung ausgegangen werden.

Der Workflow `.github/workflows/pages.yml` ist jetzt ausschließlich manuell auslösbar und führt nur noch lokale Prüfungen sowie das Staging nach `_site` aus. Er enthält keine Pages-Konfigurations-, Upload- oder Deploy-Aktion. Er kann somit aus diesem Repository heraus keine neue Pages-Veröffentlichung anlegen oder aktualisieren.

**Wichtig:** Das Entfernen des Deploy-Pfads schaltet eine bereits veröffentlichte GitHub-Pages-Seite nicht automatisch ab. Bis zur administrativen Prüfung und ausdrücklichen Freigabe muss Pages unter **Settings → Pages** deaktiviert/unpublished bleiben. Betreiberidentität, Anschrift, Kontakt, Impressum und Datenschutz sind vor jeder späteren Veröffentlichung real und rechtlich zu prüfen; keine Platzhalter erfinden.

## Automatische Abläufe

- **Aktueller Stand:** `.github/workflows/pages.yml` ist ausschließlich manuell auslösbar. Der Job `verify-only` prüft und staged lokal; sämtliche Pages-Upload-/Deploy-Aktionen wurden entfernt. Weder Push noch manueller Start veröffentlichen oder aktualisieren die Website.
- Pushes auf `main` starten Softwaretests, aber keine PWA-Buildvorschau. Der manuelle Workflow `.github/workflows/private-pwa.yml` staged die statischen Dateien ausschließlich auf dem ephemeren GitHub-Runner; er lädt weder ein Actions-Artefakt hoch noch veröffentlicht er eine Website.
- Der CC0-Rechercheworkflow lädt Bildbytes nur vorübergehend in den isolierten GitHub-Runner, um Dateiformat und technische Lesbarkeit zu prüfen. Die Originalbild-Arbeitsdateien werden vor Ende des Jobs entfernt.
- Der CC0-Rechercheworkflow veröffentlicht weder Originalbild-Artefakte noch Kandidaten-Metadaten-Artefakte. Er schreibt nur aggregierte Prüfergebnisse in die Actions-Zusammenfassung und entfernt danach die erzeugten CSV-, JSON- und HTML-Prüflisten.
- `.github/workflows/gallery-original-artifact-audit.yml` prüft nach einem erfolgreichen CC0-Lauf anhand genau dieser Run-ID, dass keine Kandidaten-Artefakte veröffentlicht wurden.
- Der lokale Prüfjob staged ausschließlich die freigegebenen statischen App-Dateien und `review/index.html` in `_site`; er lädt dieses Verzeichnis nicht hoch. Kandidatengalerien, Originalbilder, Bildmanifeste und Review-Identitäten werden nicht gestagt.
- Die lokalen Rechte-/SHA-256-Audits und ihre synthetischen Unit-Tests bleiben für eine spätere geschützte manuelle Prüfung verfügbar; sie sind keine öffentliche Veröffentlichung und keine Trainingsfreigabe.
- `.github/workflows/browser.yml` prüft die Integration mit Chromium.
- `.github/workflows/site-health.yml` ist nur manuell auslösbar; ein täglicher Online-Check ist deaktiviert. Bei manuellem Start prüft es die öffentliche Adresse und statische Assets.
- `.github/workflows/sources.yml` prüft wöchentlich den Katalog der Forschungsquellen.
- `.github/workflows/training-data.yml` schlägt absichtlich fehl, solange echte beschriftete Trainingsbilder fehlen.

## Unveränderliche CI-Container und Action-Pins

Die Browser- und Gesamttests verwenden `@playwright/test` 1.65.1 zusammen mit dem passenden Microsoft-Playwright-Container. Der OCI-Image-Index für `mcr.microsoft.com/playwright:v1.65.1-noble` ist zusätzlich mit dem geprüften Registry-Digest `sha256:1507cbfc550a63a6b7396791ca4f00df17beb56342d2447b3f106c306f525579` fixiert. Dadurch wird nicht nur der Versionsname, sondern genau der registrierte Container-Inhalt verwendet. Quelle: [Microsoft Artifact Registry – Playwright-Tags](https://mcr.microsoft.com/en-us/product/playwright/tags).

Der verpflichtende Workflow-Audit `scripts/audit_workflow_action_pins.py` prüft sowohl externe `uses:`-Referenzen auf vollständige 40-stellige Commit-SHAs als auch Workflow-`image:`-Referenzen auf einen SHA-256-OCI-Digest. Lokale Actions sind zulässig; Docker-Actions müssen ebenfalls Digest-gepinnt sein. Neue Browser-/Build-Container und Dependabot-Änderungen müssen diesen Audit bestehen, bevor sie übernommen werden.


## Sichtbarkeit der PWA-Buildvorschau

Der Workflow `.github/workflows/private-pwa.yml` erstellt die statische Vorschau ausschließlich in einem ephemeren GitHub-Runner-Verzeichnis. Er enthält keinen `actions/upload-artifact`-Schritt und keine Pages-Upload- oder Deploy-Aktion. Nach Ende des Jobs wird das Runner-Verzeichnis verworfen. Es entsteht dadurch weder ein herunterladbares PWA-Actions-Artefakt noch eine gehostete Website.

Das öffentliche Repository macht normale Actions-Logs und Step Summaries für Repository-Leser sichtbar. Der Workflow darf deshalb weiterhin keine Benutzerfotos, GPS-Daten, Secrets, privaten Notizen oder nicht freigegebenen Modellgewichte in Logs schreiben. Bereits vorhandene historische Actions-Artefakte werden durch diese Änderung nicht gelöscht; ihre manuelle Bereinigung ist separat nachzuweisen.

## Öffentliche CI-Testartefakte

Das Repository ist öffentlich; Actions-Artefakte sind daher nicht privat. Die Browser-/WebKit-Fehlerdiagnosen werden nur bei fehlgeschlagenen, manuell gestarteten Läufen gespeichert und nach einem Tag entfernt. Der Ein-Klick-Gesamttest lädt keine Browser-Traces, Screenshots oder Taxonomie-Exporte als Artefakt hoch; sein bereinigter Ergebnisbericht bleibt in `GITHUB_STEP_SUMMARY` und den normalen Actions-Logs. Der Bericht der autonomen Projektsteuerung wird nur nach ausdrücklichem `workflow_dispatch` hochgeladen und ebenfalls einen Tag aufbewahrt. Der wöchentliche autonome Lauf veröffentlicht damit keine Browser-Traces als Artefakt.

Andere Workflows erzeugen getrennte technische Artefakte wie Taxonomie-CSV, KiCad-Prüfberichte, Provenienzberichte und SBOMs. Diese sind ebenfalls öffentlich und haben eigene Aufbewahrungsfristen. Vor jeder Erweiterung ihrer Inhalte ist zu prüfen, dass keine Benutzerbilder, GPS-Daten, Tokens, privaten Notizen oder sonstigen personenbezogenen Daten enthalten sind.

## Originalbild-Prüfung und Datenzugriff

Der CC0-Workflow darf Originalbilder nur transient auf dem GitHub-Runner prüfen. Er speichert keine Originalbytes in Actions-Artefakten, im Repository oder auf Pages. Die erzeugten Kandidatenlisten und Galerien enthalten öffentliche Quellenmetadaten und werden nach der aggregierten Zusammenfassung ebenfalls aus dem Runner-Arbeitsverzeichnis entfernt.

Die technische Bildprüfung belegt ausschließlich, dass eine Datei lesbar war und bestimmte Format-/Größengrenzen erfüllte. Sie bestätigt weder die tatsächliche Urheberschaft noch die individuelle Medienlizenz, die Artbestimmung, eine Bounding-Box-Annotation oder eine Trainingsfreigabe.

Die früheren öffentlichen Artefakte `original-velutina-images` und `ki-cc0-quellen-prueflisten` sind Altbestände aus vorangegangenen Läufen. Sie dürfen nicht als freigegebener Datensatz verwendet werden. Ihre manuelle Löschung aus der Actions-Artefaktverwaltung ist gesondert nachzuweisen; das Ende neuer Uploads löscht bereits vorhandene Artefakte nicht rückwirkend.

Für eine spätere interne Prüfung müssen konkrete Originalmedien nach individueller Rechteprüfung in einem zugriffsgeschützten lokalen Verzeichnis bereitgestellt werden. Keine privaten Fotos, genauen Apiary-Koordinaten oder vertraulichen Rechtebelege in öffentliche Issues, Repositories oder Actions-Artefakte hochladen.

## Administrative Pages-Einstellung

Die Repository-API meldet `has_pages=true`. Die Einstellung ist unabhängig vom Workflow. Wenn keine öffentliche Website beabsichtigt ist, muss ein Repository-Administrator unter **Settings → Pages** die Veröffentlichung deaktivieren/unpublishen und anschließend den Status erneut über die Repository-/Pages-Einstellungen prüfen. Die verbundene GitHub-Automation kann diese administrative Einstellung nicht ändern.

## Öffentliche Review-Daten

Die früheren Originalbild- und Kandidatenlisten-Artefakte sind keine Trainingsfreigabe. Neue CC0-Läufe veröffentlichen keine solchen Artefakte. Das lokale Staging enthält nur eine Review-Statusseite; eine öffentliche Veröffentlichung dieser Seite ist in diesem Audit nicht bestätigt. Kandidatengalerien bleiben bis zur unabhängigen Rechte- und Fachprüfung unveröffentlicht. Die sechs früher eingecheckten Kandidatengalerien sind aus dem aktuellen Quellbaum entfernt; ältere öffentliche Commits enthalten sie weiterhin. Eine History-Umschreibung erfordert eine gesonderte Eigentümerentscheidung (Issue #310).

## Öffentliche Adresse und Alt-Veröffentlichung

Vorgesehene URL: https://simonthomas-ai.github.io/Beekeeper-Monitor/

Die Erreichbarkeit und der Inhalt einer bestehenden Pages-Veröffentlichung wurden nicht verifiziert. Ein deaktivierter Workflow oder ein fehlender neuer Deploy-Lauf beweist nicht, dass eine ältere Veröffentlichung offline ist. Vor einer späteren Freigabe müssen Pages-Status, tatsächliche Betreiberangaben, Impressum, Datenschutz, Artefakte und öffentliche Inhalte administrativ geprüft werden.

## Funktionsgrenzen
Diese Veröffentlichung ist eine **PWA zur manuellen Beobachtung**, keine fertig trainierte oder feldvalidierte KI. Automatische Modellausführung ist in diesem Build deaktiviert: Es fehlen lokal verfügbare, freigegebene Gewichte und unabhängige Validierung. Die frühere experimentelle Hornet3000-Laufzeit wird nicht geladen oder veröffentlicht. Zeitgesteuerte GitHub Actions laufen nach bestem Bemühen und ersetzen keinen dauerhaft laufenden Rechner. Kamera, Standortzugriff, Offline-Neustart und Sicherungsimport müssen auf echten iPhones geprüft werden. Automatische SMS, Server-Push, Triangulation, Unterstützung aller 24 EU-Sprachen und eine validierte Erkennungsgenauigkeit von 99 % sind noch nicht implementiert.

## Lokale Warnung bei Überschreiten eines Schwellwerts (freiwillig)
Die PWA kann vor unbestätigten `vespa_velutina`-Kandidaten aus dem lokalen Stationsempfänger (`camera_detection` / `acoustic_event`) warnen. Der einstellbare Konfidenzschwellwert liegt standardmäßig bei 100 % und mindestens bei 50 %. Die Funktion ist zunächst deaktiviert und arbeitet nur, solange die Seite geöffnet, über `http://127.0.0.1:8765/` verbunden und mit dem Empfängerschlüssel authentifiziert ist. Ein geschlossener Tab bedeutet: keine Warnung.

Mögliche Hinweise sind ein Banner, ein Ton und nach Einwilligung eine Systembenachrichtigung. Jedes Ereignis wird einmal gemeldet; Ereignisse älter als 15 Minuten werden ignoriert und eine fünfminütige Sperrzeit begrenzt Wiederholungen. Jede Warnung bleibt ausdrücklich ein **unbestätigter Verdacht eines nicht validierten Modells**, keine sichere Artbestimmung. Fernbenachrichtigungen und SMS benötigen einen gesondert geprüften und datenschutzrechtlich bewerteten Dienst.
