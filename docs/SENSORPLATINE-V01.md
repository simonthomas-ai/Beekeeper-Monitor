# VespaGuard Sensorplatine v0.1 – konkreter Schaltplanentwurf

**Status: ungetesteter Entwurf, nicht für Fertigung oder Außeneinsatz freigegeben.** Die Platine misst nur Umgebungstemperatur und relative Feuchte. Sie enthält **keine** Solar-Lade-, Akku-, Motor- oder Hochstromelektronik. Für eine bestückbare Leiterplatte fehlen noch geprüfte CAD-Dateien, Design-Review und Prototypmessungen.

## 1. Festgelegte Funktion und elektrische Grenzen

- Host: Raspberry Pi Zero 2 W **oder** Raspberry Pi 5 mit 40-poligem GPIO-Anschluss.
- Logikpegel: ausschließlich **3,3 V**. GPIO sind nicht 5-V-tolerant.
- Sensor: **Bosch BME280**, Temperatur/Feuchte/Luftdruck, I²C-Betrieb; kein BMP280 (misst keine Luftfeuchte).
- Platine wird aus der abgesicherten 3,3-V-Schiene des Raspberry Pi versorgt; **keine** externe 5-V- oder Batteriespannung.
- Erstes Layout als **Adapter für ein fertig bestücktes BME280-3,3-V-Breakout**; die nackte LGA-Sensorbestückung und Pull-up-Dimensionierung sind ein späteres, gesondertes Design.
- Breakout muss nach Datenblatt 3,3-V-Versorgung **und** 3,3-V-I²C-Signalpegel unterstützen. Module mit 5-V-Pull-ups dürfen nicht angeschlossen werden.

## 2. Netztabelle (Schaltplan als überprüfbare Spezifikation)

| Netz | Pi GPIO 40-polig, physischer Pin | BME280-Breakout | Bemerkung |
| --- | --- | --- | --- |
| 3V3 | Pin 1 | VCC / VIN nur bei bestätigter 3,3-V-Kompatibilität | Kein 5 V |
| GND | Pin 6 | GND | Gemeinsames Bezugspotenzial |
| I2C_SDA | Pin 3, GPIO2 | SDA / SDI | I²C1 SDA |
| I2C_SCL | Pin 5, GPIO3 | SCL / SCK | I²C1 SCL |

Der Pi stellt auf diesen I²C-Leitungen bereits Pull-ups bereit. Zusätzliche Breakout-Pull-ups müssen auf Gesamtabmessung, Buskapazität und Pegel geprüft werden. Beim BME280 im I²C-Modus müssen CSB auf HIGH und SDO für die gewünschte Adresse korrekt beschaltet sein; bei vielen Breakouts ist das bereits festgelegt. Typische 7-Bit-Adressen sind **0x76 oder 0x77** – vor Softwarekonfiguration mit dem tatsächlichen Modul prüfen.

**ASCII-Verbindungsschema (nur Signalebene):**

```text
Raspberry Pi 40-Pin              BME280-Breakout (3,3-V-I²C)
Pin 1  (3V3)  -----------------> VCC
Pin 6  (GND)  -----------------> GND
Pin 3  (GPIO2 / SDA1) --------> SDA
Pin 5  (GPIO3 / SCL1) --------> SCL
```

**Nicht** Pi-Pin 2 (5 V) an den Sensor anschließen. Vor dem Einschalten jede Verbindung mit einem Durchgangsprüfer kontrollieren. GPIO-Belegung bei HATs/anderen Erweiterungen auf Konflikte prüfen.

## 3. Bauteilliste v0.1 (Prototyp)

| Pos. | Anzahl | Bauteil | Beschaffungs-/Prüfkriterium |
| --- | ---: | --- | --- |
| J1 | 1 | 2×20-polige Raspberry-Pi-GPIO-Buchsenleiste, 2,54 mm | Mechanische Höhe, korrekte Pin-1-Markierung und Footprint |
| J2 | 1 | 1×4-poliger Steckverbinder, 2,54 mm | Passend zum konkret ausgewählten Breakout und Kabel |
| U1 | 1 | BME280-Breakout mit 3,3-V-I²C-Pegeln | Exakte Hersteller-Artikelnummer und Schaltung prüfen |
| PCB1 | 1 | 2-Lagen-FR-4-Leiterplatte | Designregeln des Fertigers, Lötstopplack, Beschriftung |
| M1 | nach Mechanik | Abstandshalter / Befestigung | Kurzschlussfreiheit, wettergeschützte Montage |

**Hinweis:** Die Stückliste ist erst nach Auswahl der konkreten Breakout-Platine und Stecker *bestellfertig*. Ein BME280-Breakout ist nicht mit dem nackten BME280-Chip gleichzusetzen.

## 4. Layout-Vorgaben

- J1 Pin 1 deutlich kennzeichnen; Steckrichtung, HAT-Abstand, Raspberry-Pi-Gehäuse und Kamera-Flachbandkabel prüfen.
- Sensor möglichst außerhalb der warmen Rechnerluft platzieren; sonst werden Temperaturwerte verfälscht.
- Für den ersten Prototyp I²C-Leitungen kurz halten und keine ungeschützten langen Außenleitungen führen.
- Keine externen PV-/Akku-Leitungen auf der Sensorplatine; Schutz vor Feuchte und ESD durch geeignete Montage.
- Vor Freigabe: Schaltplan-ERC, PCB-DRC, Netzlistenvergleich, Footprint- und Polaritätsprüfung, Fertiger-Review.

## 5. Prüfprotokoll für einen realen Prototyp

1. Vor Anschluss am Pi: Sichtprüfung, Durchgangstest, Kurzschlussprüfung 3V3–GND.
2. Sensor anschließen und I²C am Pi aktivieren; mit `i2cdetect -y 1` die erwartete Adresse ermitteln. Achtung: I²C-Scans nur auf einem dafür geeigneten Bus durchführen.
3. BME280-Chip-ID und Messwerte mit einer dokumentierten Treiberbibliothek lesen; nicht allein aus einer I²C-Adresse auf einen BME280 schließen.
4. Werte über mehrere Temperaturen/Feuchtebereiche mit Referenzmessgerät vergleichen.
5. Unterspannung, Neustart und mehrtägigen Dauerbetrieb prüfen.
6. Erst danach Gerber-/Bohrdaten, BOM und Messprotokoll als reproduzierbare Version veröffentlichen.

## 6. Bezugsquellen und technische Unterlagen

- [Bosch Sensortec BME280 – Produktseite und Datenblatt](https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/)
- [Raspberry Pi – offizielle GPIO-Dokumentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [KiCad – Schaltplan und PCB-Layout](https://www.kicad.org/)
- Bauteil-Distributoren: [Mouser](https://www.mouser.de/), [DigiKey](https://www.digikey.de/), [Farnell](https://de.farnell.com/), [Reichelt](https://www.reichelt.de/)
- PCB-Fertigung: [Aisler](https://aisler.net/), [Eurocircuits](https://www.eurocircuits.com/)

## 7. Konformität und Freigabestatus

Der Entwurf ist **nicht CE-geprüft oder zugelassen**. Auch bei Verwendung gekennzeichneter Fertigmodule sind EMV, Sicherheit, Funk, RoHS, Produktverantwortung und die tatsächlich anwendbaren EU-Vorschriften für das Gesamtsystem zu bewerten. Chemisches Ätzen ist für diesen ersten Prototyp nicht notwendig; ein Leiterplattenfertiger kann die nach Review erzeugten Gerber-Daten fertigen.

**Nächster Meilenstein:** Exakte Herstellerartikelnummern für J1, J2 und U1 auswählen, Schaltplan und Footprints in KiCad umsetzen und nach unabhängigem Review einen ersten Prototypen prüfen.
