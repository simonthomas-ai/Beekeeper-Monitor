# Abnahmestand

## Automatisierte Softwareprüfung – 20.11.2026

- [x] Reale lokale Softwarestrecke Quelle → Node-Bridge → authentifizierter Monitor-HTTP-Eingang → SQLite-Speicher per End-to-End-Test geprüft
- [x] 205 Ereignisse über Cursor-Seiten 100/100/5 zugestellt
- [x] Bridge-Neustart mit gespeichertem Cursor geprüft; keine zusätzliche Zustellung
- [x] Vollständiger Replay geprüft; 205 Wiederholungen führten weiterhin zu nur 205 gespeicherten Ereignissen
- [x] Prüft, dass Bild-, Audio- und GPS-Daten nicht an den Monitor weitergereicht werden und KI-Kandidaten unbestätigt bleiben
- [x] Python-/Integrations-, Browser- und WebKit-/iPhone-Emulation-Tests im GitHub-CI erfolgreich
- [x] PWA-Deployment-Workflow auf GitHub Pages erfolgreich

## Noch nicht vor Ort abgenommen

- [ ] GitHub Pages auf einem echten iPhone geöffnet und Bedienung geprüft
- [ ] PWA-Installation auf echten iPhones und Android-Geräten getestet
- [ ] Offline-Protokollierung und Datenwiederherstellung nach Neustart auf realen Geräten geprüft
- [ ] Hornissen-Modell mit unabhängigen Daten validiert
- [ ] Varroa-Modell mit unabhängigen Daten validiert
- [ ] Drohnenbrut-Modell mit unabhängigen Daten validiert
- [ ] Pollen-Modell mit unabhängigen Daten validiert
- [ ] Schwarm-Modell mit unabhängigen Daten validiert
- [ ] Königinnen-Modell mit unabhängigen Daten validiert
- [ ] Unabhängiger Datenschutz- und Sicherheitstest abgeschlossen
- [ ] Codeberg-Synchronisierung eingerichtet und getestet

**Wichtige Abgrenzung:** Die automatisierten Tests belegen die Software-HTTP-Strecke und die getesteten Browserabläufe, nicht die Installation auf einem realen Telefon, den Betrieb einer Kamera, eine validierte automatische KI-Erkennung oder den Funkbetrieb mit MeshCore/LoRa. Die aktuelle App ist weiterhin ein lokales Beobachtungsprotokoll und keine validierte automatische KI-Erkennung.
