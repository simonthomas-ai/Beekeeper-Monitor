# VespaGuard – Solartechnik für autarke Beobachtungsstationen

> **Planungsunterlage, noch kein feldgeprüfter Bauplan.** Die angegebenen Rechenbeispiele sind Annahmen und keine Messwerte. Akkuchemie, Laderegler, Sicherungen, Kabel und Gehäuse müssen vor der Installation für die konkrete Hardware dimensioniert und fachkundig geprüft werden.

## 1. Ziel: netzunabhängiger Betrieb

Eine autarke Station benötigt eine ausreichende Energieernte auch im Winter, eine sichere Energiespeicherung und einen geregelten Ausgang für Raspberry Pi, Kamera und gegebenenfalls Mobilfunk. Ein Raspberry Pi 5 mit dauerhafter Kamera-/KI-Verarbeitung kann erheblich mehr Energie benötigen als ein stromsparender Ereignissensor. Ein Budget von 150 € für eine komplette winterfeste Solaranlage **ist nicht zugesichert**.

## 2. Funktionsplan – keine direkte Akkuverdrahtung

```text
Solarmodul
   │  (passende PV-Leitung, Steckverbinder und Schutz nach Auslegung)
   ▼
geeigneter Solar-Laderegler für Akkutyp und Modulspannung
   │
   ▼
Akku mit passendem Batteriemanagement / Tiefentladeschutz
   │
   ├── abgesicherter Ausgang → geeigneter DC/DC-Wandler → Raspberry Pi
   │                                                     └── Kamera (USB/Netzwerk)
   └── optional abgesicherter Ausgang → passender Wandler → Mobilfunkgerät
```

**Niemals** Solarmodul oder ungeregelten Akku direkt an Raspberry-Pi-GPIO oder einen ungeeigneten USB-Eingang anschließen. Ein Laderegler ersetzt nicht automatisch eine geeignete Lastversorgung, Sicherung oder einen für den Akku erforderlichen Schutz.

## 3. Komponenten und Auswahlkriterien

| Bauteil | Worauf zu achten ist |
| --- | --- |
| Solarmodul | Nennleistung, Leerlaufspannung bei Kälte, Kurzschlussstrom, Montage, Verschattung |
| Laderegler | Kompatibilität mit PV-Eingang und Akkutyp, zulässige Spannungen/Ströme, Lastmanagement |
| Akku | Nutzbare Kapazität, Temperaturfreigaben, Lebensdauer, geeigneter Lade-/Entladeschutz |
| DC/DC-Wandler | Stabiler Ausgang entsprechend dem konkreten Rechner, ausreichende Spitzenlast und Wirkungsgrad |
| Sicherungen und Leitungen | Passend zu Leiterquerschnitt, Strom, Kurzschlussrisiko und Gerätehersteller |
| Gehäuse | Witterungs- und UV-Beständigkeit, Kondensation, Belüftung, Temperatur, Wartungszugang |
| Überwachung | Akkuspannung bzw. Ladezustand, Unterspannungsabschaltung, Neustartprotokoll |
| Optional Mobilfunk | Zusätzlicher Dauer- und Spitzenverbrauch, Empfang und Tarif |

Bei LiFePO4-Akkus ist insbesondere das **Laden unterhalb der vom Hersteller freigegebenen Temperatur** zu verhindern. Schutzfunktionen und Gehäuse müssen zum gewählten Produkt passen.

## 4. Dimensionierung: Rechenweg mit ausdrücklich hypothetischen Werten

### Täglicher Energiebedarf

`E_Tag (Wh) = P_mittel (W) × 24 h`

Beispiel A, **nur angenommen**: Eine optimierte Station verbraucht im Mittel 4 W.

`4 W × 24 h = 96 Wh/Tag`

Beispiel B, **nur angenommen**: Ein leistungsstärkeres System benötigt im Mittel 10 W.

`10 W × 24 h = 240 Wh/Tag`

### Akku für sonnenarme Tage

`C_nenn (Wh) ≥ E_Tag × Tage_Autonomie / (nutzbarer_Entladeanteil × Wirkungsgrad)`

Beispiel für **drei Tage**, angenommene 80 % nutzbare Akkukapazität und 90 % Systemwirkungsgrad:

| Mittlere Last | Tagesbedarf | Erforderliche Nennenergie (gerundet) |
| --- | ---: | ---: |
| 4 W | 96 Wh | 400 Wh |
| 10 W | 240 Wh | 1.000 Wh |

Das sind keine Kaufempfehlungen; Alterung, Kälte, Lastspitzen und Sicherheitsreserve können größere Speicher erforderlich machen.

### Solarmodul für den Standort

`P_PV (Wp) ≥ E_Tag / (äquivalente_Volllaststunden_pro_Tag × Gesamtwirkungsgrad)`

Nur zur Veranschaulichung, **angenommene** 2 Volllaststunden und 75 % Gesamtwirkungsgrad:

- 96 Wh/Tag: mindestens rechnerisch 64 Wp
- 240 Wh/Tag: mindestens rechnerisch 160 Wp

**Achtung:** Zwei Volllaststunden sind keine belastbare Winterannahme für einen deutschen Bienenstand. Für ganzjährigen Betrieb müssen standortbezogene monatliche Einstrahlungsdaten, Verschattung, Modulneigung und längere Schlechtwetterphasen berücksichtigt werden. Ein aus dem Jahresmittel ausgelegtes System kann im Winter ausfallen.

## 5. Strom sparen

- Bildverarbeitung bedarfsgesteuert statt permanent betreiben, soweit das Beobachtungsziel dies zulässt.
- Kamerabildrate und Auflösung nur so hoch wie für die später nachzuweisende Modellqualität erforderlich wählen.
- Mobilfunk nur bei Bedarf aktivieren und seinen Spitzenstrom separat messen.
- Lokale Ereignisse bei Netzausfall puffern; keine unbestätigten Meldungen als bestätigte Artbestimmung verschicken.
- Unterspannung kontrolliert behandeln; Datenbank- und Speicherkonsistenz nach Abschaltung und Neustart prüfen.

## 6. Vor der Montage zu messen und zu prüfen

- [ ] Konkretes Raspberry-Pi-/Kameramodell und Versorgungsspezifikationen dokumentiert
- [ ] Mittlere und maximale Leistungsaufnahme mit Kamera und optionalem Funk **gemessen**
- [ ] Standort, Modulneigung, Winterverschattung und monatliche Erträge ermittelt
- [ ] Akku, Laderegler, Wandler, Sicherungen und Kabel passend dimensioniert
- [ ] Akku-Ladetemperaturen und Tiefentladeschutz geprüft
- [ ] Mindestens mehrere reale Schlechtwettertage und Wiederanlauf getestet
- [ ] Wasserschutz, Kondensation, Hitze und sichere Montage geprüft
- [ ] Datenschutz, lokale Datensicherung und Benachrichtigungsgrenzen dokumentiert

## 7. Weiterführende Projektunterlagen

- [Deutsches VespaGuard-Bauhandbuch](BAUHANDBUCH.md)
- [Projektstatus und offene Feldtests](../STATUS.md)
- [BeeKeeper3000: experimentelle Kamera-Pipeline](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/camera/README.md)
- [BeeKeeper3000: Hardware- und Kamera-Abnahme](https://github.com/simonthomas-ai/BeeKeeper3000/blob/main/docs/CAMERA-ACCEPTANCE.md)

**Nächster Prüfschritt:** Eine konkrete Geräteauswahl festlegen, reale Lastwerte messen und mit lokalen Winter-Einstrahlungsdaten einen belastbaren elektrischen Schaltplan sowie eine vollständige Stückliste erstellen.
