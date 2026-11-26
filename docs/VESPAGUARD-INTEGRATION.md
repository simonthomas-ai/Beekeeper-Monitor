# VespaGuard: zwei Repositories, ein System

Stand: 26.11.2026. Geprüfter BeeKeeper3000-Partnerstand für die Cross-Repository-Workflows: `77bd1c012af502afa42b9a79bf9eff0deda37032`. Der bisherige Pin `63bef0204c063c8b4b17af7b3b26a8021b259c2b` liegt drei Commits dahinter. Der Commitvergleich ergab ausschließlich Änderungen an Supply-Chain-/Trainingsabhängigkeitsprüfung, Lizenz-/Provenienzdokumentation und Regressionstests; die vom Monitor verwendeten Bridge- und Datensatzvalidator-Schnittstellen blieben unverändert. Beide Integrationsworkflows und ihr Pin-Regressionstest werden gemeinsam auf den neuen unveränderlichen Commit aktualisiert. Dies ist eine **Integrationslandkarte**, keine Behauptung einer vollständig betriebsbereiten Hornissenerkennung.

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

- BeeKeeper3000 PR [#105](https://github.com/simonthomas-ai/BeeKeeper3000/pull/105) ergänzt den optionalen NMEA-0183-Adapter für checksum-geprüfte GGA/RMC-Fixes und HDT/HDM/HDG-Heading-Sätze. Exakte GNSS-Koordinaten bleiben lokal; das ausgehende Ereignis enthält nur eine unbestätigte Peilung. PR [#107](https://github.com/simonthomas-ai/BeeKeeper3000/pull/107) ergänzt den Fake-Serial-/Parser-Test in den Windows-Qualitätslauf. Linux- und Windows-Softwaretests sind erfolgreich; ein physischer GNSS-Empfänger, Kompass, Kalibrierung oder vermessene Referenzpeilung sind **nicht** abgenommen.
- BeeKeeper3000 PR [#101](https://github.com/simonthomas-ai/BeeKeeper3000/pull/101) ist in `main` integriert (`05257986edff26d2e05b0826693f4d8bad8ec0a6`): Der explizite lokale Bild-/Videoimport besitzt Pfad-/Symlink-, Dateiidentitäts-, Größen-, Pixel-, Frame- und Zeitgrenzen. Er legt ausschließlich das bestehende sechs-feldrige unbestätigte Metadatenereignis lokal ab; es gibt keinen Medien-Upload und keine automatische Synchronisierung. Linux-/Windows-Kamera-, Bridge-, Netzwerk-, SBOM-/Abhängigkeits- und CodeQL-Prüfungen waren erfolgreich. Reale Zielcodecs, Kamerageräte und Modellabnahme bleiben offen.
- Die lokale Quelle–Bridge–Monitor-Strecke wurde softwareseitig mit **205 Testereignissen** inklusive Cursor-Seiten, Neustart und Replay-Deduplizierung geprüft. Siehe [BeeKeeper3000-Veröffentlichungsstatus](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/UPLOAD-STATUS.md).
- CI auf beiden Repositories prüft Softwareverhalten. **Nicht** nachgewiesen sind eine reale Kamera-/Modell-Erkennungsqualität, 99 % Trefferquote, echte iPhone-Hardware, Funkreichweite, Solar-/SIM-Betrieb oder eine feldvalidierte Nestlokalisierung.
- In BeeKeeper3000 fehlt weiterhin der vollständige ursprüngliche Hornet3000-C++-Quellbaum als veröffentlichter GitHub-Stand. Das ONNX-Beispielmanifest ist absichtlich ungültig; es gibt kein freigegebenes Modellgewicht.
- Vor jeder Veröffentlichung eines gemeinsamen Pakets müssen die Urheber-/Lizenzrechte der betroffenen Komponenten, Daten und Modellgewichte separat geklärt werden. Fehlende Root-Lizenzen sind keine Erlaubnis zur beliebigen Weiterverbreitung.

## Einheitliche technische Freigabe

- Der Datenschutz-Filter wurde mit BeeKeeper3000 PR [#103](https://github.com/simonthomas-ai/BeeKeeper3000/pull/103) weiter gehärtet: NFKC-Normalisierung, Ablehnung nicht-ASCII-basierter technischer Feldnamen und Regressionen gegen Vollbreitenzeichen, kombinierende Zeichen und Homoglyphen.
- BeeKeeper3000 PR [#104](https://github.com/simonthomas-ai/BeeKeeper3000/pull/104) bindet lokale Medien-Snapshots an Dateiidentität und prüft die Identität nach dem Lesen erneut. Linux- und Windows-Medienimporttests sind bestanden; POSIX-spezifische ctime-Prüfung wird auf Windows korrekt übersprungen.
- Der BeeKeeper3000-Hauptzweig enthält zusätzlich den gemeinsamen Adapter-Lifecycle mit Pflichtprüfungen für Discovery, Fähigkeiten, Berechtigungen, begrenzte Aufrufe, sauberes Stoppen und Wiederverbindung. PR [#99](https://github.com/simonthomas-ai/BeeKeeper3000/pull/99) ergänzt die fail-closed Sperre für sensible camelCase-/Trennzeichen-Aliase (z. B. `apiKey`, `privateKey`, `imageUrl`, `gpsCoordinates`, `streamUrl`) und ist in den Hauptzweig übernommen. Dies stärkt die Metadaten-Grenze, ersetzt aber keine reale Datenschutz- oder Feldabnahme.

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
