# Beekeeper Monitor

**Internationale Forschung und Technik:** [Internationale Hornissendetektoren: Technikvergleich und Integrationsprüfung](docs/INTERNATIONAL-HORNET-DETECTORS-2026.md). Die beschriebenen Fremdsysteme sind keine bereits freigegebenen VespaGuard-KI-Modelle.

Offline-fähige Beobachtungs-PWA für Imker zur Erfassung und Sichtung von Hinweisen auf die Asiatische Hornisse (*Vespa velutina*). Teil des gemeinsamen VespaGuard-Systems zusammen mit [BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000).

**Wichtig:** Projekt im Aufbau. Es gibt kein lokales, freigegebenes oder feldvalidiertes KI-Erkennungsmodell und keine nachgewiesene Erkennungsgenauigkeit. Die automatische KI-Inferenz ist in diesem Build deaktiviert; die App zeigt nur Modellkandidaten und Freigabevoraussetzungen an. Sie ist ein Beobachtungs- und Suchhinweissystem, keine bestätigende Artbestimmung und keine Grundlage für Nestzerstörung. Details: [STATUS.md](STATUS.md) und [iPhone-Kameratest](docs/IPHONE-HTTPS-KAMERATEST.md).

**Öffentliche Bereitstellung:** Der GitHub-Pages-Deploy ist derzeit deaktiviert. Die frühere URL https://simonthomas-ai.github.io/Beekeeper-Monitor/ ist kein Nachweis einer erreichbaren oder freigegebenen Live-Anwendung. Für Tests die PWA lokal starten; keine öffentliche Bereitstellung ohne gesonderte Freigabe.

## Was es heute kann

- Installierbare PWA (`manifest.webmanifest`, Service Worker) mit Offline-Protokollierung im Browser
- Kamera- und Mikrofonzugriff für manuelle Beobachtung (`live-media.js`)
- KI-freier Kamera-Shadow-Test mit explizit übernommenem Einzelbild, unklassifiziertem Beobachtungstyp und lokaler IndexedDB-Speicherung; keine Daueraufnahme, Erkennung oder Übertragung
- Lokale manuelle Bildklassifikation für Feldaufnahmen: sieben Taxonomie-Slugs, Mehrfachlabels oder explizites Negativbild; JPG/JPEG, PNG, WebP; ZIP-Export (`images/` + `annotations.jsonl`) erst nach manueller Labelprüfung und ausdrücklicher Nutzerattestierung. Rechteangaben werden strukturiert erfasst, sind aber kein automatisch geprüfter Nachweis; jede manuelle Freigabe benötigt zusätzlich eine pseudonyme Prüfer-ID und einen separaten Prüfzeitpunkt
- Lokaler Empfangsdienst für Stationsereignisse: authentifiziert, nur Loopback, SQLite-Speicher mit Deduplizierung, Aufbewahrungsfrist, Export und Löschung ([integrations/](integrations/README.md))
- Datenschutz-Grenze: nur validierte Metadaten, keine Bilder, kein Audio, keine GPS-Koordinaten; Bridge-Ereignisse bleiben unbestätigte Kandidaten
- Abschaltbare lokale Warnung (Banner, Ton, Systembenachrichtigung) bei Velutina-Verdacht ab einstellbarer Konfidenz, nur bei geöffneter und verbundener Seite; immer als unbestätigter Verdacht gekennzeichnet
- Sichtbare Bereitschaftsanzeige für alle sieben dokumentierten KI-Module; Modellgewichte und automatische Inferenz sind nicht verfügbar
- Prüfpipeline für Trainingsdaten: Lizenz- und Provenienz-Gates pro Bild, sieben Klassen, Split-Leckage-Prüfung ([training/](training/README.md))

## Noch nicht vorhanden

- Freigegebenes Erkennungsmodell, valide Erkennungsleistung und Feldfreigabe
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
python -m unittest scripts.test_audit_workflow_action_pins -v
python scripts/audit_workflow_action_pins.py
python -m unittest training.test_audit_gallery_rights -v
python -m unittest training.test_verify_inaturalist_photo_metadata training.test_discover_cc0_candidates training.test_audit_inaturalist_candidates training.test_download_original_inaturalist_images training.test_prepare_visual_review_gallery -v
python -m unittest discover -s integrations -p 'test_*.py'
npm ci && npx playwright install --with-deps && npm run test:e2e   # Node.js 22, reproduzierbare Browser-Tests (Playwright)
npm audit --audit-level=high   # bekannte hohe/kritische npm-Advisories pruefen
```

Die npm-Abhaengigkeiten sind ueber `package-lock.json` fixiert; lokale und automatisierte Installationen verwenden `npm ci`. Dependabot prueft npm- und GitHub-Actions-Abhaengigkeiten woechentlich. Die GitHub-Actions-Workflows in `.github/workflows/` prüfen unter anderem WebKit-/iPhone-Emulation und Trainingsdaten-Gates. Der öffentliche GitHub-Pages-Deploy ist derzeit deaktiviert; ein grüner CI-Lauf bedeutet weder öffentliche Bereitstellung noch Modell- oder Feldfreigabe.

## Dokumentation

| Thema | Datei |
| --- | --- |
| Abnahmestand und offene Punkte | [STATUS.md](STATUS.md) |
| Zusammenspiel mit BeeKeeper3000 | [docs/VESPAGUARD-INTEGRATION.md](docs/VESPAGUARD-INTEGRATION.md) |
| Deployment und Betrieb | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| Datenlebenszyklus und Datenschutz | [docs/DATA-LIFECYCLE-AND-PRIVACY.md](docs/DATA-LIFECYCLE-AND-PRIVACY.md) |
| Modellabnahme | [docs/MODEL-ACCEPTANCE.md](docs/MODEL-ACCEPTANCE.md) |
| Trainingsdaten und Lizenzen | [training/README.md](training/README.md) |
| Lokale Klassifikations-Feldaufnahme | [docs/FIELD-DATASET-CAPTURE.md](docs/FIELD-DATASET-CAPTURE.md) |

## Lizenz

Für dieses Repository ist noch keine Lizenz festgelegt. Bis dahin gelten alle Rechte als vorbehalten. Fremde Datensätze, Modelle und Bilder haben jeweils eigene Lizenzen, siehe [docs/upstream-license-audit-2026-11-19.md](docs/upstream-license-audit-2026-11-19.md) und [training/](training/).
