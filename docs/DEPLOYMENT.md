# Automatische Veröffentlichung und Betriebsprüfungen

## Aktueller Veröffentlichungsstatus – 21.11.2026

Die GitHub-Pages-URL ist die vorgesehene öffentliche Adresse, aber die Veröffentlichung des aktuellen `main`-Quellstands ist derzeit nicht nachgewiesen. `impressum.html` und `datenschutz.html` enthalten noch Platzhalter für Betreiberidentität, Anschrift und Kontakt. Der Pages-Workflow erkennt diese Angaben und bricht vor dem Upload des Veröffentlichungsartefakts absichtlich ab.

**Diese Sperre nicht umgehen und keine Betreiber- oder Rechtsdaten erfinden.** Erst nach Eintragung und Prüfung der echten Angaben darf ein Pages-Deployment erfolgreich sein. Ein früherer erfolgreicher Pages-Lauf belegt nicht, dass der aktuelle Stand veröffentlicht ist.

## Automatische Abläufe
- Jeder Push auf `main` startet `.github/workflows/pages.yml` zur Prüfung und Veröffentlichung der statischen PWA.
- `.github/workflows/browser.yml` prüft die Integration mit Chromium.
- `.github/workflows/site-health.yml` prüft täglich die öffentliche Adresse und fünf Dateien.
- `.github/workflows/sources.yml` prüft wöchentlich den Katalog der Forschungsquellen.
- `.github/workflows/training-data.yml` schlägt absichtlich fehl, solange echte beschriftete Trainingsbilder fehlen.

## Einmalige GitHub-Einstellung
Unter **Settings > Pages > Build and deployment > Source** muss **GitHub Actions** ausgewählt sein. Der Workflow kann diese Einstellung nicht garantieren. Veröffentlichungsfehler unter **Actions** prüfen.

## Öffentliche Adresse
https://simonthomas-ai.github.io/Beekeeper-Monitor/

## Funktionsgrenzen
Diese Veröffentlichung ist eine **PWA zur manuellen Beobachtung**, keine fertig trainierte KI. Zeitgesteuerte GitHub Actions laufen nach bestem Bemühen und ersetzen keinen dauerhaft laufenden Rechner. Kamera, Standortzugriff, Offline-Neustart und Sicherungsimport müssen auf echten iPhones geprüft werden. Automatische SMS, Server-Push, Triangulation, Unterstützung aller 24 EU-Sprachen, Modellinferenz und eine validierte Erkennungsgenauigkeit von 99 % sind noch nicht implementiert.

## Lokale Warnung bei Überschreiten eines Schwellwerts (freiwillig)
Die PWA kann vor unbestätigten `vespa_velutina`-Kandidaten aus dem lokalen Stationsempfänger (`camera_detection` / `acoustic_event`) warnen. Der einstellbare Konfidenzschwellwert liegt standardmäßig bei 100 % und mindestens bei 50 %. Die Funktion ist zunächst deaktiviert und arbeitet nur, solange die Seite geöffnet, über `http://127.0.0.1:8765/` verbunden und mit dem Empfängerschlüssel authentifiziert ist. Ein geschlossener Tab bedeutet: keine Warnung.

Mögliche Hinweise sind ein Banner, ein Ton und nach Einwilligung eine Systembenachrichtigung. Jedes Ereignis wird einmal gemeldet; Ereignisse älter als 15 Minuten werden ignoriert und eine fünfminütige Sperrzeit begrenzt Wiederholungen. Jede Warnung bleibt ausdrücklich ein **unbestätigter Verdacht eines nicht validierten Modells**, keine sichere Artbestimmung. Fernbenachrichtigungen und SMS benötigen einen gesondert geprüften und datenschutzrechtlich bewerteten Dienst.
