# Echte Trainingsdaten für Vespa velutina – Quellen und Freigabe

Stand: 21. November 2026. Diese Datei dokumentiert **Recherchequellen**, keine bereits heruntergeladenen, geprüften oder trainierten Datensätze.

## Geeignete Kandidaten

| Quelle | URL | Eignung | Lizenz- und Qualitätsprüfung |
| --- | --- | --- | --- |
| iNaturalist | https://www.inaturalist.org/ | Artenbezogene Beobachtungen und Fotos; ggf. Audiodateien | Beobachtungs-, Foto- und Audio-Lizenzen sind getrennt; jede Datei einzeln prüfen; Research Grade ersetzt keine fachliche Sichtung |
| GBIF | https://www.gbif.org/ | Nachvollziehbare Vorkommensdaten und teils verknüpfte Medien | Lizenz **des Mediums** getrennt prüfen, Originalquelle dokumentieren, Download-DOI und Filter archivieren |
| Wikimedia Commons – V. velutina nigrithorax | https://commons.wikimedia.org/wiki/Category:Vespa_velutina_nigrithorax | Fotos zur manuellen Kuratierung und zu Vergleichstests | Einzeldatei-Lizenz, Urheber, Attribution, Artbestimmung und eventuelle Bearbeitungsauflagen prüfen |
| Umweltbundesamt | https://www.umweltbundesamt.de/asiatische-hornisse | Fachliche Merkmale und Artabgrenzung, **nicht** automatisch Bildtrainingsdaten | Text als Referenz; Bilder nicht ohne entsprechende Nutzungsrechte übernehmen |
| LANUV NRW | https://linfos.naturschutzinformationen.nrw.de/neobiota/de/arten/tiere/190771/kurzbeschreibung | Regionale Artmerkmale und Verwechslungshinweise | Fachreferenz, kein pauschales Recht zum Bilddownload |

## Verpflichtende Prüfkette vor jedem Training

1. **Artbestimmung:** *Vespa velutina nigrithorax* getrennt von *Vespa crabro*, anderen Wespen, Bienen und Hummeln führen. Fehlbestimmungen manuell überprüfen.
2. **Lizenz pro Mediendatei:** Nur nachweislich passende Nutzungsrechte verwenden. Für unkomplizierte Nachnutzung CC0/CC BY bevorzugen; CC BY-SA nur nach Prüfung der Verpflichtungen; CC BY-NC und unlizenzierte Dateien nicht pauschal als frei verwendbare Trainingsdaten behandeln.
3. **Provenienz:** Original-URL, Beobachtungs-/Medien-ID, Autor, konkrete Lizenz und Version, Abrufdatum, Artbestimmung und prüfende Person dokumentieren.
4. **Duplikate:** Identische und nahezu identische Bilder, Serien desselben Tiers und Varianten desselben Fotos nicht auf Trainings- und Testdaten verteilen.
5. **Unabhängige Testdaten:** Nach Beobachtungsort, Fotograf, Zeitpunkt und Quelle gruppieren, um Datenleckagen zu vermeiden. Klassenweise Präzision, Recall, Konfusionsmatrix und Falschalarme angeben.
6. **Praxisvalidierung:** Nacht/Tag, Licht, Bewegungsunschärfe, Entfernung, verschiedene Kameras und Nichtzielarten gesondert prüfen.
7. **Audio:** Keine artspezifische Erkennung behaupten, solange rechtmäßig verwendbare, eindeutig annotierte Hornissenaufnahmen und Blindtests fehlen.
8. **Datenschutz:** Exakte Fundorte und personenbezogene Metadaten nicht ohne Rechtsgrundlage öffentlich machen; EXIF-Daten kontrollieren.

## Wissenschaftlicher Bezug

- Leitlinien zur wissenschaftlichen Nutzung von iNaturalist: https://doi.org/10.1093/biosci/biag135
- Bürgerwissenschaftliche Verwechslungsmuster bei *Vespa velutina* in Spanien: https://doi.org/10.1111/jen.70144
- Fachmerkmale des Umweltbundesamts: https://www.umweltbundesamt.de/asiatische-hornisse

**Nachweisstatus:** Keine der hier genannten Medien wurde in diesem Arbeitsschritt heruntergeladen oder auf Eignung für Modelltraining freigegeben. Es wurden keine Modellgewichte erzeugt, keine Trainingsläufe gestartet und keine Genauigkeitswerte gemessen.
