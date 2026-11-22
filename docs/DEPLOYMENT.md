# Automatische Veröffentlichung und Betriebsprüfungen

## Aktueller Veröffentlichungsstatus – 21.11.2026

Die GitHub-Pages-URL ist die vorgesehene öffentliche Adresse, aber die Veröffentlichung des aktuellen `main`-Quellstands ist derzeit nicht nachgewiesen. `impressum.html` und `datenschutz.html` enthalten noch Platzhalter für Betreiberidentität, Anschrift und Kontakt. Der Pages-Workflow erkennt diese Angaben und bricht vor dem Upload des Veröffentlichungsartefakts absichtlich ab.

**Diese Sperre nicht umgehen und keine Betreiber- oder Rechtsdaten erfinden.** Erst nach Eintragung und Prüfung der echten Angaben darf ein Pages-Deployment erfolgreich sein. Ein früherer erfolgreicher Pages-Lauf belegt nicht, dass der aktuelle Stand veröffentlicht ist.

## Automatische Abläufe
- **Aktueller Stand:** `.github/workflows/pages.yml` ist ausschließlich manuell auslösbar und der Job `deploy` hat `if: ${{ false }}`. Weder Push noch manueller Start veröffentlichen die Website. Der öffentliche Link darf nicht als aktuell funktionsfähig beworben werden.\n- Jeder Push auf `main` startet lediglich den privaten PWA-Artefakt-Build und den Gesamttest; diese veröffentlichen keine Website.
- Der Pages-Build übernimmt die lokalen Originalbilder aus dem neuesten erfolgreichen Lauf von `.github/workflows/ki-cc0-quellen.yml`; bei einem `workflow_run` wird exakt das Artefakt des auslösenden erfolgreichen Laufs verwendet.
- Das Artefakt enthält nur `velutina-original-images-manifest.csv` und `images/velutina/`. Fehlerberichte und temporäre Prüfdaten werden nicht veröffentlicht. Bei normalem Push oder manueller Ausführung wird die jüngste erfolgreiche CC0-Ausführung auf `main` ausgewählt.
- Vor dem Pages-Upload prüft `scripts/audit_gallery_rights.py` sämtliche sechs Galerie-JSONs, Quellen-/Urhebermetadaten, Manifestbindung, Pfadgrenzen, Symlinks, Dateigrößen und SHA-256 der tatsächlichen Originalbytes. `velutina.html` und `all.html` müssen exakt dieselbe lokale Bildmenge wie das Manifest referenzieren; fehlende, veränderte oder zusätzliche Dateien brechen den Build ab.
- Der Audit belegt die technische Byte-Integrität und Konsistenz der gespeicherten Metadaten, ist aber keine unabhängige rechtliche Lizenzprüfung und keine Trainingsfreigabe.
- `.github/workflows/browser.yml` prüft die Integration mit Chromium.
- `.github/workflows/site-health.yml` prüft täglich die öffentliche Adresse und fünf Dateien.
- `.github/workflows/sources.yml` prüft wöchentlich den Katalog der Forschungsquellen.
- `.github/workflows/training-data.yml` schlägt absichtlich fehl, solange echte beschriftete Trainingsbilder fehlen.

## Unveränderliche CI-Container und Action-Pins

Die Browser- und Gesamttests verwenden `@playwright/test` 1.65.1 zusammen mit dem passenden Microsoft-Playwright-Container. Der OCI-Image-Index für `mcr.microsoft.com/playwright:v1.65.1-noble` ist zusätzlich mit dem geprüften Registry-Digest `sha256:1507cbfc550a63a6b7396791ca4f00df17beb56342d2447b3f106c306f525579` fixiert. Dadurch wird nicht nur der Versionsname, sondern genau der registrierte Container-Inhalt verwendet. Quelle: [Microsoft Artifact Registry – Playwright-Tags](https://mcr.microsoft.com/en-us/product/playwright/tags).

Der verpflichtende Workflow-Audit `scripts/audit_workflow_action_pins.py` prüft sowohl externe `uses:`-Referenzen auf vollständige 40-stellige Commit-SHAs als auch Workflow-`image:`-Referenzen auf einen SHA-256-OCI-Digest. Lokale Actions sind zulässig; Docker-Actions müssen ebenfalls Digest-gepinnt sein. Neue Browser-/Build-Container und Dependabot-Änderungen müssen diesen Audit bestehen, bevor sie übernommen werden.

## Originalbild-Deployment und Integritätsprüfung

Die Originalbilddateien werden im CC0-Rechercheworkflow bytegenau geladen und in einem Manifest mit Photo-ID, Beobachtungs-ID, Quellen-URL, iNaturalist-Beobachtername und -Login, separatem CC0-Attributionssatz, rohem Lizenzhinweis, Lizenzmetadaten, Dateiformat, Abmessungen, Bytezahl und SHA-256 dokumentiert. Der Beobachter wird aus dem Beobachtungsdatensatz übernommen und beim CC0-Einzelabgleich erneut anhand des Logins gebunden; der Text `no rights reserved` wird nicht als Fotografenname verwendet. Die Galerie verweist für diese Bilder auf relative lokale Pfade unter `review/images/velutina/`; bei fehlgeschlagenem Download gibt es für diese Kandidaten keinen stillen Remote-Fallback.

`creator` ist hier aus Kompatibilitätsgründen das von iNaturalist empfohlene CC0-Attributionssubjekt (Beobachtername oder Login), kein eigenständiger Beleg dafür, wer das Foto tatsächlich aufgenommen hat. Die Galerie bezeichnet diese Angabe deshalb ausdrücklich als iNaturalist-Beobachter/Attributionsbasis.

Der Pages-Workflow lädt die zugehörige erfolgreiche Actions-Artefaktversion und führt denselben Audit gegen das fertig gestagte `_site` aus. Damit reicht nicht nur ein gültiger Hash im CSV: die tatsächlich publizierte Datei muss dieselbe Bytezahl und denselben SHA-256 besitzen, und beide Galerien müssen die Manifestdaten exakt widerspiegeln. Ein fehlender oder abgelaufener Artefaktnachweis sperrt die Veröffentlichung bei lokalen Bildreferenzen, statt eine fehlerhafte oder uneinheitliche Galerie auszuliefern.

Die bestehenden Sperren für unvollständige Impressums- und Datenschutzhinweise bleiben davon unabhängig bestehen und werden nicht umgangen.

## Einmalige GitHub-Einstellung
Unter **Settings > Pages > Build and deployment > Source** muss **GitHub Actions** ausgewählt sein. Der Workflow kann diese Einstellung nicht garantieren. Veröffentlichungsfehler unter **Actions** prüfen.

## Nachgewiesener Originalbild-Artefaktpfad – 22.11.2026

Der nicht veröffentlichende Workflow `.github/workflows/gallery-original-artifact-audit.yml` lädt den letzten erfolgreichen CC0-Quellenlauf auf `main`, übernimmt dessen Actions-Artefakt `original-velutina-images` und prüft es gemeinsam mit den sechs eingecheckten Review-Galerien. Der erfolgreiche Hauptzweiglauf [44997072834](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44997072834) verwendete den erfolgreichen Quellenlauf [44923213005](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44923213005).

Prüfergebnis: **94 Originaldateien**, **94 Manifestzeilen**, alle Bytezahlen und SHA-256-Werte stimmen; die sechs Galerien enthalten insgesamt **936 Datensätze**. `velutina.html` und `all.html` referenzieren die Manifestmenge exakt. Der Artefakt-Digest wurde beim Download zusätzlich von GitHub Actions geprüft.

Dieser Nachweis bestätigt die technische Übereinstimmung des konkreten Artefakts mit dem geprüften Galerie-Quellstand. Er ist weder unabhängige Rechtsprüfung noch Trainingsdatenfreigabe. Der Pages-Deploy bleibt deaktiviert; die Prüfung veröffentlicht keine Dateien.

## Öffentliche Adresse (derzeit NICHT als erreichbar bestätigt)\nhttps://simonthomas-ai.github.io/Beekeeper-Monitor/\n\nDie Unterseite `/varroa.html` ist im Repository und im privaten Build vorhanden, aber öffentlich erst nach einem erfolgreichen Pages-Deployment erreichbar. Ein HTTP-404 ist bis dahin erwartbar. Vor einem öffentlichen Testbetrieb müssen die tatsächlichen Betreiber-/Kontaktangaben und Datenschutzhinweise geprüft und ergänzt werden. Danach kann der Pages-Workflow kontrolliert wieder aktiviert werden.

## Funktionsgrenzen
Diese Veröffentlichung ist eine **PWA zur manuellen Beobachtung**, keine fertig trainierte KI. Zeitgesteuerte GitHub Actions laufen nach bestem Bemühen und ersetzen keinen dauerhaft laufenden Rechner. Kamera, Standortzugriff, Offline-Neustart und Sicherungsimport müssen auf echten iPhones geprüft werden. Automatische SMS, Server-Push, Triangulation, Unterstützung aller 24 EU-Sprachen, Modellinferenz und eine validierte Erkennungsgenauigkeit von 99 % sind noch nicht implementiert.

## Lokale Warnung bei Überschreiten eines Schwellwerts (freiwillig)
Die PWA kann vor unbestätigten `vespa_velutina`-Kandidaten aus dem lokalen Stationsempfänger (`camera_detection` / `acoustic_event`) warnen. Der einstellbare Konfidenzschwellwert liegt standardmäßig bei 100 % und mindestens bei 50 %. Die Funktion ist zunächst deaktiviert und arbeitet nur, solange die Seite geöffnet, über `http://127.0.0.1:8765/` verbunden und mit dem Empfängerschlüssel authentifiziert ist. Ein geschlossener Tab bedeutet: keine Warnung.

Mögliche Hinweise sind ein Banner, ein Ton und nach Einwilligung eine Systembenachrichtigung. Jedes Ereignis wird einmal gemeldet; Ereignisse älter als 15 Minuten werden ignoriert und eine fünfminütige Sperrzeit begrenzt Wiederholungen. Jede Warnung bleibt ausdrücklich ein **unbestätigter Verdacht eines nicht validierten Modells**, keine sichere Artbestimmung. Fernbenachrichtigungen und SMS benötigen einen gesondert geprüften und datenschutzrechtlich bewerteten Dienst.
