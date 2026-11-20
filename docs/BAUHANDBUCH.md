# VespaGuard – Bauhandbuch für eine lokale Beobachtungsstation

> **Stand: 20. November 2026.** Dieses Dokument ist eine deutschsprachige Planungs- und Sicherheitsanleitung, **kein fertig getesteter Schaltplan**. Es gibt derzeit kein unabhängig validiertes KI-Erkennungsmodell. Ein Hornissenverdacht darf nicht als bestätigte Artbestimmung oder als Grundlage für eine Nestentfernung verwendet werden.

## 1. Ziel und Grenzen

Eine Station soll Insekten am Bienenstand beobachten und – nach gesonderter Modellfreigabe – unbestätigte Ereigniskandidaten lokal protokollieren. Die öffentliche PWA ist ein Beobachtungsprotokoll. Die Kamera-/ONNX-Pipeline von BeeKeeper3000 ist experimentell. Die lokale Ereignisübertragung ist softwareseitig getestet, nicht aber die komplette Hardware im Feld.

## 2. Systemaufbau

```text
Kamera → lokaler Rechner (z. B. Raspberry Pi oder Windows)
                │
                ├─ optionale lokale ONNX-Auswertung (nur mit geprüftem Modell)
                ├─ lokale Ereigniswarteschlange
                ↓
       BeeKeeper3000-Quell-API → authentifizierte Monitor-Bridge
                ↓
       lokaler Beekeeper-Monitor-Empfangsdienst → SQLite
                ↓
       lokale Stationsansicht (nur 127.0.0.1)
```

**Datenschutzgrenze:** Die Bridge übermittelt keine Bilder, Audiodaten oder GPS-Koordinaten. Die öffentliche GitHub-Pages-Webseite verbindet sich nicht mit dem privaten lokalen Empfangsdienst.

## 3. Komponentenliste zur Planung (keine freigegebene Stückliste)

| Komponente | Zweck | Status |
| --- | --- | --- |
| Raspberry Pi 4 oder 5 beziehungsweise vorhandener Windows-Rechner | Lokale Verarbeitung | Eignung im Dauerbetrieb noch zu testen |
| Kompatible USB- oder Netzwerk-Kamera | Bildaufnahme | Auflösung, Bildrate und Wettereignung vor Ort prüfen |
| Geeignetes Netzteil, Kabel und Speicher | Versorgung und lokale Datenhaltung | Nach Herstellerangaben dimensionieren |
| Optionales USB-Mikrofon | Experimentelle akustische Beobachtung | Keine validierte Audio-Artbestimmung |
| Wettergeschütztes Gehäuse und sichere Kabeldurchführungen | Schutz am Bienenstand | Wärmeabfuhr, Kondenswasser und Wartungszugang prüfen |
| Optional: Akku, Solarmodul und Laderegler | Netzunabhängiger Betrieb | Erst nach gemessener Leistungsaufnahme auslegen |
| Optional: Mobilfunkmodem mit SIM | Künftige externe Benachrichtigung | SMS-Funktion derzeit nicht als fertig implementiert belegt |

**Keine pauschale Preis-, Laufzeit- oder Autarkiezusage.** Die Auswahl muss mit tatsächlichen Verbrauchsmessungen, Kameraanforderungen und Standortbedingungen abgeglichen werden.

## 4. Elektrische Sicherheit und Verkabelung

1. Den Rechner ausschließlich mit einer für das konkrete Modell spezifizierten, geeigneten Stromversorgung betreiben.
2. Kamera und optionales Mikrofon zunächst über ihre vorgesehenen USB-/Netzwerkschnittstellen verbinden; keine unbekannten GPIO-Pins beschalten.
3. Akku und Solarversorgung **nicht direkt** an GPIO, USB oder ungeregelte Eingangspins anschließen. Einen zum Akkutyp passenden, abgesicherten Lade- und Spannungsregler nach Herstellerunterlagen auswählen.
4. Vor Außenmontage Überstromschutz, Zugentlastung, Feuchteschutz, Kondensation und Temperaturbereich prüfen.
5. Erst nach dokumentierten Strom-, Temperatur- und Wiederanlauftests unbeaufsichtigt betreiben.

Ein verbindlicher Pin-für-Pin-Schaltplan ist erst sinnvoll, wenn die konkreten Geräte, Spannungen, Steckverbinder und Schutzschaltungen feststehen.

## 5. Software und Inbetriebnahme

1. Die tatsächlichen Installationshinweise von [BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000) lesen.
2. Die [experimentelle Kamera-Pipeline](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/camera/README.md) nur mit einem rechtlich und fachlich geprüften Modell betreiben. Das Beispielmanifest enthält absichtlich **kein einsatzfähiges Modell**.
3. Die [Monitor-Integration](VESPAGUARD-INTEGRATION.md) anhand der dokumentierten lokalen Sicherheitsgrenzen konfigurieren.
4. Die [Deployment-Anleitung](DEPLOYMENT.md) und die [Datenschutzdokumentation](DATA-LIFECYCLE-AND-PRIVACY.md) beachten.
5. Kamera, Offline-Betrieb, Neustart, Export, Löschung und Ereignisübertragung einzeln prüfen und Ergebnisse protokollieren.

## 6. Abnahme vor einem echten Feldeinsatz

- [ ] Kamera und Rechner auf realer Hardware geprüft
- [ ] Netzteil, Leitungen, Sicherungen und Gehäuse sicher ausgelegt
- [ ] Leistungsaufnahme und Akku-/Solarlaufzeit real gemessen
- [ ] Verhalten bei Regen, Sonne, Kälte und Hitze geprüft
- [ ] Lokaler Betrieb ohne Internet und Wiederanlauf geprüft
- [ ] Datenexport, Wiederherstellung und Löschung geprüft
- [ ] Rechte und Herkunft aller verwendeten Modelle und Bilddaten dokumentiert
- [ ] Unabhängige Erkennungsprüfung mit realen, getrennten Testdaten abgeschlossen
- [ ] Fehlalarme und übersehene Tiere im Feld dokumentiert
- [ ] Datenschutz- und Sicherheitsprüfung abgeschlossen

Die verbindlichen offenen Punkte stehen in [STATUS.md](../STATUS.md) und in der [Kamera-Abnahme von BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/docs/CAMERA-ACCEPTANCE.md).

## 7. Nächste technische Ausbaustufen

Ein konkreter, bebilderter Verdrahtungsplan, eine belastbare Stückliste mit Preisen und eine Solar-/Akkudimensionierung benötigen zuerst eine festgelegte Hardwarevariante sowie gemessene Lastwerte. GPS-Triangulation, SMS und automatische KI-Erkennung sind **keine** durch dieses Handbuch freigegebenen Funktionen.
