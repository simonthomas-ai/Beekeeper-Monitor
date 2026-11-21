# Beekeeper Monitor

**Internationale Forschung und Technik:** [Internationale Hornissendetektoren: Technikvergleich und Integrationsprüfung](docs/INTERNATIONAL-HORNET-DETECTORS-2026.md). Die beschriebenen Fremdsysteme sind keine bereits freigegebenen VespaGuard-KI-Modelle.

Offline-fähige Beobachtungs-PWA für Imker zur Erfassung und Sichtung von Hinweisen auf die Asiatische Hornisse (*Vespa velutina*). Teil des gemeinsamen VespaGuard-Systems zusammen mit [BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000).

**Wichtig:** Projekt im Aufbau. Es gibt noch kein validiertes KI-Erkennungsmodell und keine nachgewiesene Erkennungsgenauigkeit. Die App ist ein Beobachtungs- und Suchhinweissystem, keine bestätigende Artbestimmung und keine Grundlage für Nestzerstörung. Details: [STATUS.md](STATUS.md).

Live: https://simonthomas-ai.github.io/Beekeeper-Monitor/

## Was es heute kann

- Installierbare PWA (`manifest.webmanifest`, Service Worker) mit Offline-Protokollierung im Browser
- Kamera- und Mikrofonzugriff für manuelle Beobachtung (`live-media.js`)
- Lokaler Empfangsdienst für Stationsereignisse: authentifiziert, nur Loopback, SQLite-Speicher mit Deduplizierung, Aufbewahrungsfrist, Export und Löschung ([integrations/](integrations/README.md))
- Datenschutz-Grenze: nur validierte Metadaten, keine Bilder, kein Audio, keine GPS-Koordinaten; Bridge-Ereignisse bleiben unbestätigte Kandidaten
- Abschaltbare lokale Warnung (Banner, Ton, Systembenachrichtigung) bei Velutina-Verdacht ab einstellbarer Konfidenz, nur bei geöffneter und verbundener Seite; immer als unbestätigter Verdacht gekennzeichnet
- Prüfpipeline für Trainingsdaten: Lizenz- und Provenienz-Gates pro Bild, sieben Klassen, Split-Leckage-Prüfung ([training/](training/README.md))

## Noch nicht vorhanden

- Freigegebenes Erkennungsmodell und Erkennung im Browser
- Benachrichtigung ohne geöffnete Seite (SMS, Server-Push); dafür braucht es einen separat geprüften Dienst
- Abnahme auf echten Geräten und im Feld

## Lokal ausprobieren

Statische PWA (ohne Empfangsdienst):

```sh
python -m http.server 8000
```

Dann `http://localhost:8000/` öffnen. Der Service Worker erfordert `localhost` oder HTTPS.

Lokaler Empfangsdienst: Start, Token und Umgebungsvariablen stehen in [integrations/README.md](integrations/README.md).

## Tests

```sh
python scripts/check_sources.py
python scripts/test_static.py
python -m unittest training.test_audit_gallery_rights -v
python -m unittest training.test_verify_inaturalist_photo_metadata training.test_discover_cc0_candidates training.test_audit_inaturalist_candidates training.test_download_original_inaturalist_images training.test_prepare_visual_review_gallery -v
python -m unittest discover -s integrations -p 'test_*.py'
npm install && npx playwright install --with-deps && npm run test:e2e   # Browser-Tests (Playwright)
```

Die GitHub-Actions-Workflows in `.github/workflows/` führen diese Prüfungen sowie WebKit-/iPhone-Emulation, Trainingsdaten-Gates und das Deployment nach GitHub Pages aus.

## Dokumentation

| Thema | Datei |
| --- | --- |
| Abnahmestand und offene Punkte | [STATUS.md](STATUS.md) |
| Zusammenspiel mit BeeKeeper3000 | [docs/VESPAGUARD-INTEGRATION.md](docs/VESPAGUARD-INTEGRATION.md) |
| Deployment und Betrieb | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| Datenlebenszyklus und Datenschutz | [docs/DATA-LIFECYCLE-AND-PRIVACY.md](docs/DATA-LIFECYCLE-AND-PRIVACY.md) |
| Modellabnahme | [docs/MODEL-ACCEPTANCE.md](docs/MODEL-ACCEPTANCE.md) |
| Trainingsdaten und Lizenzen | [training/README.md](training/README.md) |

## Lizenz

Für dieses Repository ist noch keine Lizenz festgelegt. Bis dahin gelten alle Rechte als vorbehalten. Fremde Datensätze, Modelle und Bilder haben jeweils eigene Lizenzen, siehe [docs/upstream-license-audit-2026-11-19.md](docs/upstream-license-audit-2026-11-19.md) und [training/](training/).
