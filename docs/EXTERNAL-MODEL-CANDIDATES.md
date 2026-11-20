# Externe Modelle: Prüfmatrix (20.11.2026)

**Keine Modellfreigabe.** Diese Quellen sind Kandidaten für technische und rechtliche Due Diligence, keine einsatzfähigen Beekeeper-Monitor-Modelle.

| Kandidat | Rolle | Verifizierbare Quelle | Freigabehindernis |
|---|---|---|---|
| VespAI (YOLOv5s) | Wissenschaftliche Baseline Velutina/Crabro | https://pmc.ncbi.nlm.nih.gov/articles/PMC10991484/ und https://github.com/andrw3000/vespai | CC BY-NC-SA 4.0, Daten-/Gewichtezugang und abgeleitete Lizenzpflichten; Autorenzustimmung prüfen |
| Waspinator | Raspberry-Pi-5-Detektor als Integrationskandidat | https://github.com/gitDew/waspinator | Repo-, Modellgewichte- und Ultralytics-Abhängigkeitslizenzen getrennt prüfen; keine automatische Fallensteuerung übernehmen |
| vespCV | Raspberry-Pi-4/5-Kamera und Benachrichtigung als Referenz | https://github.com/vespCV/vespcv | Code- und Gewichte-Lizenz, Datensatz und reale Hardwareleistung prüfen |
| hornet3000 | YOLOv10n/Pi-4-Referenz | https://github.com/vespCV/hornet3000 | Archiviert; GPL-3.0 und Datensatz-/Gewichterechte separat prüfen |
| ISR Roboflow | Externer Datensatz und Benchmark | https://universe.roboflow.com/institute-of-systems-and-robotics-isr/vespa-velutina-hihv9-upzpe | CC BY 4.0 laut Datensatzseite; pro Bild Herkunft/Attribution und Modell/API-Lizenz separat prüfen |

## Entscheidungsvorgehen

1. **Keine externen Gewichte ungeprüft laden oder verteilen.** Herkunft, Version, Modell-SHA256, Lizenztext, Abhängigkeiten und Datenrechte protokollieren.
2. **Erst ein Zwei-Arten-Pilot** (V. velutina, V. crabro + negative Insektenbilder) auf einer definierten Kamera- und Köderstationsgeometrie; sieben Klassen bleiben separates, nicht erfülltes Projektziel.
3. **Unabhängige Daten** nach Standort, Datum und Kamera trennen; je Klasse Precision, Recall, F1, Konfusionsmatrix, Falschalarme pro 24 Stunden und verpasste Tiere berichten. Keine 99%-Aussage ohne eigenen Test.
4. **Lokal und datensparsam**: Kameraauswertung möglichst auf Pi/Station, nur unbestätigte Ereignisse an Monitor; Audio nicht als Artbeweis einsetzen.
5. **Keine Aktorik**: Fallen, Nestzerstörung oder andere Eingriffe nie allein durch KI auslösen.
6. **Integration nur hinter Freigabe-Gate**: `python3 scripts/check_field_release.py` verlangt Belege für Rechte, Modell, Geräte, Datenschutz und Feldpilot. Formale Manifestvollständigkeit ersetzt keine unabhängige Prüfung.

## Andere Funktionen: Nicht alles benötigt ein KI-Modell

- SMS, Telegram, Offline-Wiederanlauf, GPS, Triangulation, Authentifizierung, Löschung und Backups sind deterministische Software-/Hardwarefunktionen mit eigenen Integrationstests.
- Audio-Erkennung erfordert eigene kontrollierte akustische Daten und Feldvalidierung; ohne diese **nicht** als bestätigende Artidentifikation einsetzen.
- Varroa, Schwarm, Königin, Pollen und Drohnenbrut brauchen eigene definierte Aufgaben, Bilddaten und Abnahmekriterien.
