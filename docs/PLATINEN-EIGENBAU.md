# VespaGuard – Eigenbau ab Null: Leiterplatten, Stücklisten, Bezugsquellen und EU-Konformität

**Entwurfsstand – nicht produktionsfreigegeben, nicht zertifiziert.** Diese Anleitung trennt einen selbst entwickelbaren Niedervolt-Sensor-/Überwachungsadapter von der sicherheitskritischen Solar-Lade- und Akkutechnik. Ein funktionierender und rechtlich konformer Gesamtaufbau muss vor Einsatz geprüft werden.

## 1. Architektur und sinnvolle Grenze des Eigenbaus

```text
PV-Modul (fertig, dokumentiert)
  → PV-Laderegler (fertig, passend zum Akku)
  → Akku mit BMS/Temperaturschutz (fertig, dokumentiert)
  → abgesicherte, geregelte DC-Versorgung (fertiges geeignetes Modul)
  → Raspberry Pi Zero 2 W oder Pi 5 + Kamera
                         ↕
            eigene Sensor-/Statusplatine
            (nur Kleinspannung, galvanisch/elektrisch
             passend ausgelegte Signale)
```

**Nicht als Erstprojekt selbst ätzen:** MPPT-Leistungsteil, Lithium-Ladeelektronik, Akku-BMS oder USB-C-PD-Hochstromversorgung. Hier sind Fehler brandgefährlich. Diese Baugruppen werden als fertige, für den Einsatzzweck geeignete Geräte mit technischen Unterlagen beschafft.

## 2. Funktionsumfang der eigenen Platine, Version 0.1

- Temperatur-/Feuchtemessung im Gehäuse per geeignetem I²C-Sensormodul.
- Digitale Status-/Alarm-Eingänge von geeigneten potentialfreien oder passend aufbereiteten Signalen.
- Optionale Spannungs-/Stromüberwachung **über ein geeignetes fertiges, galvanisch/elektrisch korrekt angeschlossenes Messmodul**; keine ungeschützte Verbindung der Batteriespannung zu GPIO.
- Steckverbindungen zur Sensorik; Zugentlastung und Verpolschutz für externe Leitungen.
- Keine Netzspannung, kein Akku-Ladestrompfad und keine PV-Leistungstracks auf der eigenen Platine.

**Vor der Layoutfreigabe:** Konkrete Sensor-Teilenummern, Betriebsspannung, GPIO-Pegel, Steckverbinderbelegung, Leitungswege, ESD-/Überspannungs- und Kurzschlussschutz spezifizieren. Ohne diese Festlegungen ist ein angeblich fertiger Gerber- oder Pinplan nicht belastbar.

## 3. Stückliste (BOM) – Grundgerüst

| Pos. | Menge | Baugruppe | Bezugsquelle / Nachweis | Status |
| --- | ---: | --- | --- | --- |
| 1 | 1 | Raspberry Pi Zero 2 W **oder** Raspberry Pi 5 | Raspberry Pi / autorisierte Händler; EU-DoC für konkrete Variante prüfen | Auszuwählen |
| 2 | 1 | Kompatibles Kameramodul + korrektes Kabel | Raspberry Pi / autorisierte Händler; Datenblatt | Auszuwählen |
| 3 | 1 | PV-Modul | Fachhändler; Modul-Datenblatt und relevante Konformitätsunterlagen | Winterauslegung offen |
| 4 | 1 | Solar-Laderegler | z. B. Victron SmartSolar MPPT 75/10; Herstellerhandbuch/Kompatibilität prüfen | Kandidat, keine Freigabe |
| 5 | 1 | Geschützter LiFePO4-Akku | Akkufachhandel; BMS, UN 38.3/Transport, Temperaturgrenzen und Produktdokumentation prüfen | Kapazität offen |
| 6 | 1 | DC/DC-/USB-C-Versorgung für Pi | Elektronikfachhandel; korrekte Spannung und Strom-/PD-Funktion | Kritischer Kompatibilitätstest |
| 7 | 1 | Wetterfestes Gehäuse mit Kabeldurchführungen | Industrie-Elektrohandel; IP-/UV-/Temperaturdaten | Auszuwählen |
| 8 | 1 | Sensor-Adapter-Leiterplatte | KiCad-Layout; Leiterplattenfertiger nach Fertigungsdaten | Noch zu entwickeln |
| 9 | nach Layout | I²C-Sensor, Stecker, Schutzbeschaltung, Leiterplattenbefestigung | Mouser, DigiKey, Farnell, Reichelt; exakte Hersteller-Teilenummern und Datenblätter | Noch zu spezifizieren |
| 10 | nach Auslegung | Sicherungen, Halter, Leitungen, PV-Stecker, Montage | Elektro-/Solarfachhandel; elektrische Daten | Fachprüfung erforderlich |

**Preis- und Verfügbarkeitsangaben sind bewusst nicht festgeschrieben.** Vor Bestellung: Angebot, Datenblatt, Herstelleridentität, RoHS-/REACH-Informationen und ggf. EU-Konformitätserklärung je exakter Artikelnummer dokumentieren.

## 4. Platinen entwickeln und fertigen

1. In [KiCad](https://www.kicad.org/) ein Projekt mit Schaltplan, Footprints, PCB und BOM anlegen.
2. Stromversorgung der eigenen Platine auf einen **bereits abgesicherten Niedervolt-Zweig** begrenzen. GPIO-Signale nicht direkt mit höheren Spannungen verbinden.
3. Sensoren und Steckverbinder anhand ihrer Originaldatenblätter auswählen; Pinbelegung und maximal zulässige Spannung dokumentieren.
4. ERC (Schaltplan) und DRC (Leiterplatte) ausführen; Leiterbahnbreiten, Abstände, Montagebohrungen, Kriechstrecken und Steckverbinder nach Einsatzumgebung berechnen.
5. Design-Review durch zweite fachkundige Person durchführen, insbesondere Verpolung, Kurzschluss, ESD, Feuchtigkeit und Masseführung.
6. Fertigungsdaten erzeugen: Gerber für Kupfer/Lötstopp/Bestückungsdruck, Excellon-Bohrdaten, BOM, ggf. Pick-and-Place und Montagezeichnung.
7. **Bevorzugt professionell fertigen lassen** statt chemisch selbst ätzen. Mögliche Leiterplattenfertiger: [Aisler](https://aisler.net/), [Eurocircuits](https://www.eurocircuits.com/), [JLCPCB](https://jlcpcb.com/). Mindestbreiten und Lagenaufbau nach gewähltem Fertiger prüfen.
8. Falls eigenes Ätzen gewünscht: Nur mit geeigneter Schutzausrüstung, Belüftung, Sicherheitsdatenblättern, korrekter Chemikalienlagerung und Entsorgung über zuständige Sammelstelle. **Keine Ätzlösung in den Abfluss.** Für wiederholbare Qualität und Sicherheit ist die professionelle Fertigung vorzuziehen.
9. Erste Platine strombegrenzt mit Labornetzteil prüfen; zunächst ohne Pi und ohne Solar-/Akkusystem, dann mit Testsignalen. Prüfergebnisse protokollieren.

## 5. Stromversorgung – besonders wichtig beim Pi 5

Raspberry Pi empfiehlt für den Pi 5 eine **5-V-/5-A-fähige Versorgung** (offizielles 27-W-USB-C-Netzteil). Eine beliebige 5-V-Buck-Schaltung mit USB-C-Stecker ist **nicht automatisch gleichwertig**: USB-PD-Erkennung, Kabel, Spannungsabfall und verfügbare USB-Peripherieleistung müssen passen.

- [Offizielle Raspberry-Pi-Stromversorgungsanforderungen](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi 5 EU-Konformitätserklärung](https://pip-assets.raspberrypi.com/categories/894-approvals/documents/RP-004946-CF/rpi-5-EU_Declaration-of-Conformity-DoC.pdf)

## 6. EU-Konformität, Zulassung und Verantwortung

Eine **CE-Kennzeichnung ist keine allgemeine staatliche Einzelzulassung**. Die für das fertige Produkt verantwortliche Person/Organisation muss die zutreffenden Vorschriften bestimmen, technische Unterlagen erstellen und ggf. eine EU-Konformitätserklärung ausstellen. Je nach tatsächlicher Ausstattung und Bereitstellung können unter anderem EMV, Funkanlagenrichtlinie (bei Funk), RoHS, WEEE-/ElektroG-Pflichten, Batterierecht und weitere Anforderungen relevant sein. Die Niederspannungsrichtlinie ist bei einer ausschließlich mit Kleinspannung betriebenen Platine nicht automatisch anwendbar; andere Sicherheits- und Produktvorschriften können trotzdem greifen.

**Nachweisordner je Komponente und Gesamtgerät:**
- Hersteller, exakte Artikelnummer, Datenblatt, Chargen-/Versionsbezug
- Relevante EU-Konformitätserklärung und Prüfberichte, soweit verfügbar
- RoHS-/Materialerklärungen, Funkfrequenzen und Antennenfreigaben bei LTE/WLAN
- Schaltplan, PCB-Revision, BOM, Layout-/Fertigungsdaten, Softwareversion
- Risikoanalyse: Akku, Kurzschluss, Überhitzung, Wasser, EMV, Funk, Montage
- Ergebnisse der Funktions-, Temperatur-, Unterspannungs-, EMV- und Feldprüfungen
- Anleitung, Warnhinweise, Kennzeichnung und Verantwortlichkeit

**Nur eine geprüfte Kombination** darf als erprobt bezeichnet werden. Die CE-Kennzeichnung eines Raspberry Pi, Akkus oder Ladereglers überträgt sich nicht automatisch auf die gesamte selbstgebaute Station.

## 7. Projektverweise

- [Deutsches Bauhandbuch](BAUHANDBUCH.md)
- [Solar-Auslegung](SOLAR-AUTARKIE.md)
- [Zwei Solarvarianten](SOLAR-VARIANTEN.md)
- [Projektstatus](../STATUS.md)

## 8. Offene Schritte für eine tatsächlich fertigungsfähige Leiterplatte

1. Sensor-/Steckverbinder-Funktionsumfang und exakte Bauteile festlegen.
2. Schaltplan, Footprints und Netzliste in KiCad erstellen.
3. ERC/DRC, externe Designprüfung, Gerber/Bohrdaten und verbindliche BOM erstellen.
4. Prototyp bestellen, elektrisch testen und Ergebnisse veröffentlichen.
5. Erst danach Gesamtgerät hinsichtlich anwendbarer EU-Anforderungen prüfen.

**Stand:** Ein detailliertes Entwicklungs- und Beschaffungsverfahren liegt vor; **noch keine geprüften Gerber-Dateien, keine konkrete freigegebene Leiterplatte, keine fertige Gesamtgeräte-Zulassung**.
