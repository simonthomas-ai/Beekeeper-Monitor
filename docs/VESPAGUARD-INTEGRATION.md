# VespaGuard: zwei Repositories, ein System

## Aktueller Partnerstand – 28.11.2026 (nach BeeKeeper3000 PR #155)

BeeKeeper3000 `main` steht auf `bf251e1ce5a7ccf227c2dc1bd8a7031ec90464af`. PR #155 ergänzt eine Dateikopf-Prüfung für JPEG, PNG und WebP vor `createImageBitmap`: maximal 8 MiB und 16 Megapixel, Abweisung ungültiger/inkonsistenter Header, bekannter Animationsflags und Mehrbild-JPEGs. Die dekodierte Bitmap-Größe wird weiterhin vor Canvas-Allokation geprüft und die Bitmap danach geschlossen. HEIC/HEIF ist bewusst ausgeschlossen und muss lokal als JPEG gespeichert werden. Dies reduziert das Risiko übergroßer Decoder-Allokationen, ersetzt aber keine Browser-Sicherheitsupdates oder physische Geräteabnahme.

Die PR-Prüfungen auf Head `1cf25e42cd4734687d9010fe03fb92e50899d6f0` waren erfolgreich: Quality Gates #46099702376 (vier Jobs), CodeQL #46099702361 (Python und JavaScript/TypeScript), 17 Mobile-PWA-Tests und 35 Bridge-Tests. Nach dem Merge als `bf251e1ce5a7ccf227c2dc1bd8a7031ec90464af` bestanden die Post-Merge-Läufe Quality Gates #46099848877 und CodeQL #46099848916; beide Jobsammlungen sind vollständig `completed/success`. Die Post-Merge-Quality-Gates bestätigen außerdem die Windows-Kamera-Runtime-Kompatibilität und Kamera-Runtime-Sicherheit. Die Actions-Artefaktlisten sind leer.

Der Monitor-`main`-Zweig verwendet derzeit noch den älteren Partnercommit `6adf0235c0f321eb42f57bd5966b46e1e400bcec`. Dieser PR-Zweig aktualisiert beide Cross-Repository-Workflows und den Pin-Regressionstest auf `bf251e1ce5a7ccf227c2dc1bd8a7031ec90464af`. Bis zum Merge bleibt der alte Pin auf Monitor-`main` unverändert. Die Änderung aktiviert weder Kamera-Inferenz noch Modellgewichte, öffentliche Artefakte oder Deployment.

Historischer Stand vom 27.11.2026 (nicht der aktuelle Partner-Pin): Geprüfter BeeKeeper3000-Partnerstand für die Cross-Repository-Workflows: `6adf0235c0f321eb42f57bd5966b46e1e400bcec` (Hauptzweig nach PR #150; der No-AI-Stationsdoctor-Test ist jetzt in Linux- und Windows-CI eingebunden). PR #148 ergänzt die begrenzte, beaufsichtigte No-AI-Feldtestfreigabe. PR #149 ergänzt `--no-model` für `station_doctor.py`: Der Schalter überstimmt sowohl ein übergebenes Manifest als auch `BEEKEEPER_MODEL_MANIFEST` und verhindert im No-AI-Preflight das Lesen einer Modelldatei oder synthetische ONNX-Inferenz. PR #151 ergänzt den expliziten Ursprung `manual_observation` für PWA-Metadatenexporte v2; der Bridge-Vertrag unterscheidet damit manuelle Sichtungen von Kameraereignissen. Der passende Monitor-Vertrag akzeptiert diese Ereignisse als `observer_report`, während die Hornissen-Warnregeln sie ausdrücklich ausschließen. Die PR-Prüfungen waren vollständig erfolgreich: Network Reference Tests #46021695536, Quality Gates #46021695347, Supply-chain/SBOM #46021695530, Windows-Station #46021695594 und CodeQL #46021695443. Nach dem Merge als `6adf0235c0f321eb42f57bd5966b46e1e400bcec` bestanden außerdem die Post-Merge-Läufe Quality Gates #46022027042, Network Reference Tests #46022026797, Supply-chain/SBOM #46022026815, Windows-Station #46022026800 und CodeQL #46022026701. Die Cross-Repository-Workflows und der Pin-Regressionstest werden jetzt auf diesen unveränderlichen Partnercommit umgestellt und prüfen ihn erneut. Die Änderung aktiviert weder KI-Inferenz noch produktive Alarme oder öffentliche Bereitstellung. Alle acht Fähigkeiten bleiben `enabled: false`, `status: not_validated`, `model: null`; Hornet3000 und Waspinator bleiben `rights_and_runtime_pending`. Es wurden keine Gewichte, produktiven Laufzeitfreigaben oder Deployments hinzugefügt. Dies ist eine **Integrationslandkarte**, keine Behauptung einer vollständig betriebsbereiten Hornissenerkennung.

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
- Die lokale Quelle–Bridge–Monitor-Strecke wird mit **205 synthetischen Metadatenereignissen** geprüft: Sie werden direkt in die SQLite-Outbox gelegt und über den drain-only Runtime-Pfad, Source API, Cursor-Bridge und Monitor-Empfänger geleitet. Der Test führt **keine Kamera-Frames und keine KI-Inferenz** aus; er belegt Outbox-/Transport-/Replay-Verhalten, nicht Erkennung. Siehe [BeeKeeper3000-Veröffentlichungsstatus](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/UPLOAD-STATUS.md).
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
