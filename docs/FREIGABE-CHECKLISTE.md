# Freigabe-Checkliste für VespaGuard / Beekeeper-Monitor

**Status: NICHT FREIGEGEBEN** · Stand: 21.11.2026

Diese Liste unterscheidet automatisiert geprüfte Software-Eigenschaften von noch erforderlichen Betreiberentscheidungen, rechtlichen Bewertungen und Feldtests. Ein grüner CI-Lauf ist **keine** DSGVO-Zertifizierung und **kein** Nachweis für eine zuverlässige automatische Artbestimmung. Die Checkliste ist eine Arbeitsgrundlage, keine Rechtsberatung.

## 1. Technische Prüfungen

- [x] GitHub-Qualitätslauf mit Bildrechten, Herkunftsnachweisen, iNaturalist-Metadaten und Originalbild-/Review-Tests erfolgreich: [Lauf 44934936918](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44934936918).
- [x] Automatisierte Tests für lokale Ereignisverträge, Datenminimierung, Speicherung, Backup und Löschung erfolgreich: [Lauf 44935062700](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44935062700).
- [x] Software-Bridge-/Offline-Tests zwischen BeeKeeper3000 und Monitor erfolgreich: [Lauf 44934708750](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44934708750).
- [x] Verpflichtende Freigabesperre und Bridge-Integration im zentralen Gesamttest erfolgreich: [Lauf 44935646531](https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44935646531), geprüfter Commit `b2e46709edb864590363d6ec9c6237c3fecab1fa`. Dies ist ein historischer Software-Nachweis, keine Freigabe der aktuellen oder einer späteren Version.
- [ ] Alle für die **endgültige Freigabeversion** erforderlichen CI-Jobs erneut erfolgreich ausführen und Commit-IDs dokumentieren.
- [ ] Tatsächliche Offline-Nutzung, Kamera-/Mikrofonberechtigungen, Ausfälle und Wiederanlauf auf den vorgesehenen Geräten im Feld testen.
- [ ] Backups auf einem zweiten realen Gerät wiederherstellen und Wiederherstellungsprotokoll ablegen.
- [ ] Modellgewichte, Bilddatensätze, Lizenzbedingungen, Provenienz und getrennte Validierungsdaten unabhängig prüfen; Erkennungsqualität mit belastbaren Kennzahlen und Fehlerraten belegen. Bis dahin: **keine validierte automatische Vespa-velutina-Erkennung**.

## 2. Verantwortlichkeit und Recht

- [ ] Verantwortliche natürliche oder juristische Person sowie zuständige Kontaktstelle verbindlich bestimmen.
- [ ] [Impressum](../impressum.html): soweit rechtlich erforderlich, echten Namen, ladungsfähige Anschrift, Kontakt und ggf. Registerangaben bestätigen; **keine Platzhalter veröffentlichen**.
- [ ] [Datenschutzhinweise](../datenschutz.html): verantwortliche Stelle, tatsächliche Verarbeitungszwecke, Rechtsgrundlagen nach Art. 6 DSGVO, Empfänger, Hosting und ggf. Drittlandübermittlungen für den konkreten Betrieb ergänzen.
- [ ] Rollen der Stationsbetreiber, gemeinsamer Betreiber und Dienstleister klären; erforderliche Auftragsverarbeitungsverträge prüfen.
- [ ] Datenschutz-Folgenabschätzung anhand der tatsächlichen Kamerabereiche, Standorte und Personenbezüge prüfen und Entscheidung dokumentieren.
- [ ] Anforderungen für lokale Speicher-/Endgerätezugriffe (§ 25 TDDDG) je Betriebsmodus bewerten.
- [ ] Verfahren für Betroffenenanfragen, Datenschutzvorfälle, Zugriffsrechte und Sicherheitsmeldungen schriftlich festlegen.
- [ ] Vor öffentlichem Betrieb eine einzelfallbezogene rechtliche Prüfung und Betreiberfreigabe dokumentieren.

## 3. Datenlebenszyklus und Betrieb

- [ ] Tatsächliche Konfiguration jeder Station festhalten: Monitor standardmäßig 90 Tage/100.000 Ereignisse, BeeKeeper-Quelle im Linux-Installer 30 Tage/250.000 Ereignisse; Abweichungen und Wartungsintervall prüfen.
- [ ] Löschablauf über Browser-IndexedDB, Quelljournal, Monitor-SQLite, Kamera-Outbox, Bridge, Exporte und Backups dokumentieren und praktisch testen.
- [ ] Grenzen klar benennen: Löschung in einer Datenbank entfernt nicht automatisch Kopien in anderen Systemen, bereits gesendete Funkpakete oder exportierte Backups.
- [ ] Verschlüsselung, Zugriffsrechte und Löschfristen für Geräte, Sicherungen und Exportdateien prüfen.
- [ ] Genaue GPS-Koordinaten von Bienenständen und Nestern nicht ohne gesonderte Freigabe veröffentlichen.
- [ ] Externe Bildquellen, Abrufe durch Browser, Bildlizenzen und mögliche Datenweitergaben für den tatsächlichen Betrieb prüfen.
- [ ] Verantwortliche Person, Prüfnachweise, Datum und Ergebnis für jede Freigabeentscheidung dokumentieren.

## 4. Freigabeentscheidung

**Derzeit: GESPERRT.** Die oben genannten offenen Punkte sind nicht durch grüne Softwaretests erledigt.

| Entscheidung | Verantwortlich | Datum | Nachweis |
| --- | --- | --- | --- |
| Technische Pilotfreigabe | Noch zu bestimmen | Offen | CI, Geräte-/Restore-/Feldtest |
| Datenschutz-/Rechtsprüfung | Noch zu bestimmen | Offen | Abgenommene Dokumente, Verarbeitungsverzeichnis, ggf. DSFA |
| Bild- und Modellfreigabe | Noch zu bestimmen | Offen | Lizenz-/Datensatznachweise, Validierungsbericht |
| Öffentliche Veröffentlichung | Noch zu bestimmen | Offen | Ausdrückliche Freigabe; kein automatisches Deployment |

**Verbindliche Sperre:** Keine öffentliche Bereitstellung, keine unüberprüften KI-Genauigkeitsversprechen und keine produktive Erhebung personenbezogener Daten allein aufgrund erfolgreicher CI-Tests.

Weitere technische Details: [Datenlebenszyklus und Datenschutz](DATA-LIFECYCLE-AND-PRIVACY.md).
