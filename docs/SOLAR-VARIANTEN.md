# Zwei autarke VespaGuard-Stationen: Stücklisten und Anschlusskonzept

**Stand: Entwurf zur technischen Prüfung.** Keine der Varianten ist als winterfest, betriebssicher oder mit KI-Modell im Feld validiert. Konkrete Modul-/Akku-Nennwerte dürfen erst nach Messungen und Standortauslegung bestellt werden. Ergänzend: [Solar-Grundlagen im offenen PR #123](https://github.com/simonthomas-ai/Beekeeper-Monitor/pull/123).

## A – Energiesparende Ereignisstation

| Stückzahl | Baugruppe | Auswahl / Abnahme |
|---|---|---|
| 1 | Raspberry Pi Zero 2 W | Passendes Netzteilprofil; Kameraanschluss und verfügbare Rechenleistung prüfen |
| 1 | Kompatible Pi-Kamera mit Kabel | Mechanik, Treiber, Tag-/Nachtbild und Erkennungsleistung testen |
| 1 | MicroSD-Karte | Schreibbelastung reduzieren, Ausfall-/Wiederanlauf testen |
| 1 | PV-Modul | Wp erst aus gemessenen Wh/Tag und Winterertrag festlegen |
| 1 | Solar-Laderegler | Passend zur PV-Leerlaufspannung bei Kälte und zum Akkutyp |
| 1 | Akku mit geeigneten Schutzfunktionen | Wh anhand Autonomieziel und Temperaturfenster dimensionieren |
| 1 | Abgesicherter geregelter 5-V-Versorgungspfad | Passende Pi-Eingangsspezifikation, Spitzenstrom, Leitungsverluste |
| 1 | UV- und wettergeeignetes Gehäuse | Kondensationsschutz, Kabeldurchführungen, Wartungszugang |
| nach Bedarf | Halterungen, Leitungen, Sicherung, Dichtungen | Nach elektrischer und mechanischer Auslegung |
| optional | Mikrofon und Mobilfunk | Zusätzliche Leistungsaufnahme messen; lokale Datenschutzregeln beachten |

**Einsatzprofil:** Zeitgesteuerte Aufnahme oder Ereignisauslösung. Dauerhafte lokale KI-Inferenz auf dem Zero 2 W ist nicht zugesichert.

## B – Leistungsstation mit Raspberry Pi 5

| Stückzahl | Baugruppe | Auswahl / Abnahme |
|---|---|---|
| 1 | Raspberry Pi 5 | Herstellerkonforme Stromversorgung (5,1 V/5 A empfohlen), Kühlung und Gehäuse |
| 1 | Kompatible Kamera | Kameraanschluss, Flachbandkabel und Softwaretreiber prüfen |
| 1 | Speicher | Ausfallrobuste Schreibstrategie, optional SSD mit zusätzlichem Strombedarf |
| 1 | Kühlung | Temperatur- und Leistungsdrosselung bei Sommerhitze testen |
| 1 | PV-Modul | Standortbezogene Winterdimensionierung, größere Reserven wahrscheinlich |
| 1 | Laderegler | Passend zu Modul, Akku und Ladeschutz |
| 1 | Akku mit Schutz und Temperaturüberwachung | Kapazität und zulässige Ladetemperatur nach Hersteller |
| 1 | Geregelter, abgesicherter 5,1-V-Versorgungspfad | 5-A-Fähigkeit plus Spannungsabfall und Spitzenlast prüfen |
| 1 | Wetterfestes Gehäuse mit thermischem Konzept | Keine unkontrollierte Feuchtigkeit oder Überhitzung |
| optional | Mikrofon / LTE-Modem | Energiebedarf, Spitzenlast und Funkempfang gesondert prüfen |

**Einsatzprofil:** Höhere lokale Rechenleistung für Bildanalyse; Modellgenauigkeit, Echtzeitfähigkeit und Autonomie müssen experimentell nachgewiesen werden.

## Anschlusskonzept (für beide Varianten)

```text
PV-Modul
  │
  ▼
PV-geeigneter Laderegler ── Akku mit zum Akkutyp passendem Schutz
  │                              │
  └────────── geregelter, abgesicherter Lastpfad
                                      │
                             DC/DC-Versorgung
                                      │
                          Raspberry Pi + Kamera
                                      │
                          optional Mikrofon/LTE
```

**Wichtig:** Dies ist ein Blockschaltbild, **kein Verdrahtungs- oder Pinplan**. Sicherungen müssen so platziert und bemessen sein, dass Leitungen und Komponenten bei Kurzschluss geschützt sind; Akkuschutz, Verpolschutz, Leitungsquerschnitte und Abschaltkonzept sind für die gewählten Geräte festzulegen. Akku/PV niemals direkt an GPIO anschließen. Bei Lithiumakkus die zulässige Ladetemperatur beachten.

## Auslegungsrechnung mit veränderbaren Eingangsgrößen

1. Tatsächliche mittlere Leistung der vollständigen Station einschließlich Wandlerverlusten und LTE-Spitzen **messen**: `P_mittel` in W.
2. Tagesenergie: `E_Tag = P_mittel × 24 h`.
3. Für drei Tage ohne ausreichende Solarernte: `C_Akku,Wh ≥ E_Tag × 3 / (nutzbarer Anteil × Entlade-Wirkungsgrad)`.
4. Winter-PV: `P_PV,Wp ≥ E_Tag / (standortbezogene Winter-Volllaststunden × PV-Systemwirkungsgrad)`. Für mehrtägige Dunkelphasen reicht diese Gleichung allein nicht; Speicher und zulässige Ausfallwahrscheinlichkeit separat modellieren.
5. Sicherheits- und Alterungsreserven ergänzen, Spannungswandler- und Ladereglergrenzen bei Hitze/Kälte prüfen.

**Rechenbeispiel, keine Messung:** Bei 3 W mittlerer Leistung benötigt Variante A 72 Wh/Tag; bei 9 W benötigt Variante B 216 Wh/Tag. Für drei Tage und angenommen 80 % nutzbare Akkukapazität sowie 90 % Entladewirkungsgrad ergibt das mindestens 300 Wh bzw. 900 Wh Nennenergie. Für reale Winterbedingungen kann erheblich mehr nötig sein.

## Abnahme vor dem Außeneinsatz

- [ ] Konkrete Hardwareversionen und Herstellerdatenblätter hinterlegt
- [ ] Leerlauf-, KI-, Kamera- und Funk-Spitzenlast mit Messgerät erfasst
- [ ] Standortbezogene monatliche Winter-Solarerträge und Verschattung dokumentiert
- [ ] Elektrische Schutzmaßnahmen und Leitungsführung fachkundig geprüft
- [ ] Unterspannung, Neustart und lokale Datenintegrität getestet
- [ ] Kondensation, Frost, Hitze und Montage geprüft
- [ ] Erkennungsmodell separat mit echten, lizenzierten Daten validiert
- [ ] Datenschutz- und Benachrichtigungsfunktionen getestet

## Noch offene Entscheidungen

Vor einem **konkreten** Pin-/Kabelplan müssen insbesondere Akkuchemie, Laderegler, Wandler, PV-Modul und tatsächliche Pi-/Kameralast feststehen. Eine willkürliche Verdrahtung wäre gefährlich und würde eine nicht belegte Betriebsfähigkeit suggerieren.
