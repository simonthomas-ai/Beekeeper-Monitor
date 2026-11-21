# Internationale Hornissenerkennung – Integrationspruefung (November 2026)

## Ausgangslage VespaGuard

Beekeeper-Monitor ist eine PWA zur manuellen Beobachtung und zum Empfang unbestaetigter Stationsereignisse. Ein validiertes, direkt im Browser laufendes Erkennungsmodell fehlt. Gruene CI-Laeufe sind kein Nachweis fuer Feldgenauigkeit. Automatische externe Alarmierung und reale Hardwareabnahme sind offen. Quelle: README.md, docs/MODEL-ACCEPTANCE.md.

## Internationale Kandidaten (Quellen, Stand 2026-11)

| Kandidat | Nachgewiesener Ansatz | Lizenz / Zugang | Entscheidung |
| --- | --- | --- | --- |
| VespAI | Raspberry Pi 4, YOLOv5s, Kamera und Bildalarme, wissenschaftliche Feldversuche | CC BY-NC-SA 4.0; Autoren beschreiben Anfrageverfahren fuer Code/Validierungsdaten | Wissenschaftliche Referenz und Architekturvergleich; keine automatische Uebernahme ohne Rechte- und Zugangsklaerung |
| vespCV | Raspberry Pi 4/5, YOLOv11s, Bildspeicherung und E-Mail-Benachrichtigung | GPLv3 laut Projekt-README | Bridge-Prototyp in isoliertem Test pruefen; Copyleft-Pflichten vor Codeuebernahme klaeren |
| hornet3000 | Headless Raspberry Pi, YOLOv10n und Kameradaten | Archiviert seit 2025-06-07; Rechte fuer Gewichte und Datensatz separat pruefen | Nur technische Referenz, kein ungepruefter Import |
| BuzzCopper | ESP32, solar, offline Pufferung, spaetere Uebertragung | Veroeffentlichung von Hardware/Firmware/Modellen angekuendigt | Beobachten, keine noch nicht freigegebenen Artefakte verwenden |
| Politecnico di Milano 2025/26 | Raspberry Pi 5, zweistufige YOLO26-Pipeline; Feld-Praezision 82,6 % in beschriebener Studie | Lizenz fuer Software und Gewichte nicht belegt | Forschungsreferenz; keine unautorisierte Codeuebernahme |

Quellen:
- https://www.nature.com/articles/s42003-024-05979-z
- https://github.com/andrw3000/vespai
- https://github.com/vespCV/vespcv
- https://github.com/vespCV/hornet3000
- https://www.buzzcopper.org/about
- https://www.politesi.polimi.it/handle/10589/261248

## Sichere technische Integration

1. Ein eigenes, versioniertes **Detektor-Ereignisformat** verwenden: Quelle, Zeitstempel, Modellversion, Taxon, Konfidenz, Ereignis-ID und ausdruecklicher Status `unbestaetigter Verdacht`. Vorhandene Datenschutzgrenzen des lokalen Empfangsdienstes beibehalten.
2. Externe Detektoren ausschliesslich ueber einen isolierten, authentifizierten Adapter mit Testdaten anbinden; keine direkten Fremdmodelle im produktiven PWA-Build.
3. Modellgewichte, Trainingsbilder, Annotationen und Code **getrennt** auf Rechte, Herkunft, SHA-256 und Weitergabe pruefen. Open Source des Codes bedeutet nicht freie Nutzung der Daten oder Gewichte.
4. Vor Feldalarmierung: unabhaengige Testdaten aus anderen Standorten, Verwechslungen mit Vespa crabro, Wespen, Bienen und Schwebfliegen; Precision, Recall, False-Alarm-Rate, Kalibrierung, Laufzeit und Strombedarf messen.
5. Keine automatische Artbestaetigung, keine Nestbekaempfungsentscheidung und keine Behauptung von 99 % VespaGuard-Genauigkeit ohne eigene Feldvalidierung.

## Naechster technischer Schritt

Eine eigenstaendige Bridge-Adapter-Spezifikation mit Contract-Tests fuer vespCV-artige Ereignisse erstellen, ohne Fremdcode oder ungepruefte Modelle zu importieren. Freigabe erst nach Lizenz- und Feldpruefung.
