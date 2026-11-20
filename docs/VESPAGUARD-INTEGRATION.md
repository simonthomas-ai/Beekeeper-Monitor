# VespaGuard: zwei Repositories, ein System

Stand: 20.11.2026. Dies ist eine **Integrationslandkarte**, keine Behauptung einer vollständig betriebsbereiten Hornissenerkennung.

## Kanonische Rollen

- **Beekeeper-Monitor** (dieses Repository): öffentliche Offline-PWA, manuelle Sichtungen, lokale Stationsansicht, authentifizierter Loopback-Ereignisempfänger, SQLite-Speicherung, Export/Löschung und Browser-/Integrationstests.
- **[BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000)**: optionale lokale Kamera-/ONNX-Kandidatenpipeline, persistentes Quelljournal mit signierter Cursor-Paginierung, Node.js-Monitor-Bridge, optionale MeshCore-Transport- und Triangulationsmodule sowie Stations-/Windows-Werkzeuge.

Beide Repositories bleiben getrennt versioniert, bilden aber **ein gemeinsames Produkt**. Kein blindes Kopieren, keine gegenseitigen Git-Submodule und keine Löschung der ursprünglichen Repositories: So bleiben Lizenznachweise, Testhistorie und unabhängig testbare Komponenten erhalten.

## Datenfluss (lokal, opt-in)

```text
Kamera -> lokale ONNX-Kandidatenpipeline (BeeKeeper3000; Modell noch nicht freigegeben)
       -> lokales SQLite-Quelljournal / HTTP-Source-API
       -> Node.js-Bridge mit Cursor, Checkpoint und Retry
       -> authentifizierter Beekeeper-Monitor-Loopback-Eingang
       -> lokaler SQLite-Ereignisspeicher / Stationsansicht

Smartphone -> öffentliche Beekeeper-Monitor-PWA -> lokale manuelle Beobachtungen
```

Die Bridge überträgt nur minimierte Ereignismetadaten; keine Bild-/Audio-Rohdaten, Zugangsdaten oder GPS-Koordinaten. Eine automatische Artbestimmung wird immer als **unbestätigter Kandidat** geführt. Die öffentliche GitHub-Pages-PWA ist keine öffentlich erreichbare Backend- oder Stationsschnittstelle und kann nicht auf den localhost eines fremden Geräts zugreifen.

## Nachweise und Freigabegrenzen

- Die lokale Quelle–Bridge–Monitor-Strecke wurde softwareseitig mit **205 Testereignissen** inklusive Cursor-Seiten, Neustart und Replay-Deduplizierung geprüft. Siehe [BeeKeeper3000-Veröffentlichungsstatus](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/UPLOAD-STATUS.md).
- CI auf beiden Repositories prüft Softwareverhalten. **Nicht** nachgewiesen sind eine reale Kamera-/Modell-Erkennungsqualität, 99 % Trefferquote, echte iPhone-Hardware, Funkreichweite, Solar-/SIM-Betrieb oder eine feldvalidierte Nestlokalisierung.
- In BeeKeeper3000 fehlt weiterhin der vollständige ursprüngliche Hornet3000-C++-Quellbaum als veröffentlichter GitHub-Stand. Das ONNX-Beispielmanifest ist absichtlich ungültig; es gibt kein freigegebenes Modellgewicht.
- Vor jeder Veröffentlichung eines gemeinsamen Pakets müssen die Urheber-/Lizenzrechte der betroffenen Komponenten, Daten und Modellgewichte separat geklärt werden. Fehlende Root-Lizenzen sind keine Erlaubnis zur beliebigen Weiterverbreitung.

## Einheitliche technische Freigabe

1. Beekeeper-Monitor: Ein-Klick-Gesamttest, Browser/WebKit, lokale Integration und GitHub-Pages-Deployment prüfen.
2. BeeKeeper3000: Quality Gates, CodeQL, Supply-Chain/SBOM und Stations-/Bridge-Tests prüfen.
3. **Versionsübergreifend:** Source-API- und Receiver-Verträge auf Kompatibilität testen; bei Änderungen an Ereignisformat, Cursor oder Authentifizierung beide Repositories testen.
4. Kamera-/KI-Freigabe separat blockieren, bis echte, rechtmäßig nutzbare, fachlich überprüfte Trainings-/Testdaten und ein unabhängig validiertes Modell vorliegen.
5. Hardware- und Datenschutz-Abnahme gesondert dokumentieren. Keine automatische Weitergabe von Bildern, Audio oder präzisem GPS.

## Wichtige Dokumentation

- [BeeKeeper3000: Netzwerkarchitektur](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/NETWORK-ARCHITECTURE.md)
- [BeeKeeper3000: Monitor-Bridge](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/monitor-bridge/README.md)
- [BeeKeeper3000: Kamera-Pipeline](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/camera/README.md)
- [BeeKeeper3000: aktueller Veröffentlichungsstatus](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/UPLOAD-STATUS.md)

**Betriebsregel:** Nur nach bestandenen Tests zusammenführen; keine künstlichen Testdaten als reale Hornissensichtungen und keine grünen CI-Jobs als KI-Feldfreigabe ausgeben.
