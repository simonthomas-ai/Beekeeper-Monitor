# KiCad Sensoradapter v0.1 (experimentell)

Die Datei `sensoradapter-v01.kicad_pcb` ist ein **bearbeitbarer PCB-Routingentwurf**, kein geprüfter fertigungstauglicher Bauplan. Sie verbindet zwei vierpolige 2,54-mm-Stiftleisten eins-zu-eins: Pin 1 3V3, Pin 2 GND, Pin 3 SDA, Pin 4 SCL. J1 wird **nicht direkt** auf die 40-polige Pi-Leiste gesteckt: Ein separat verdrahtetes, auf Durchgang geprüftes Kabel führt zu den physischen Pi-Pins 1, 6, 3 und 5. J2 führt zum ausdrücklich 3,3-V-kompatiblen BME280-Breakout.

**Vor Bestellung unbedingt:** PCB in KiCad öffnen, Bibliotheks-Footprints und Pad-Nummerierung kontrollieren, Netzliste mit dem [Pinplan](../../docs/SENSORPLATINE-V01.md) vergleichen, ERC/DRC ausführen, Abstände/Bohrungen/Montage prüfen, Schaltplan als separate KiCad-Datei ergänzen, Layout unabhängig überprüfen lassen. Es gibt **noch keine** validierte Schaltplandatei, keine Gerber, keinen Prototyp und keine CE-Konformität. Keinesfalls an 5 V oder an den Solarakku anschließen.
