# Ergebnisbericht: 1.000 iNaturalist-Bildkandidaten in fünf Gruppen

Datum: 21.11.2026
GitHub Actions Lauf: https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44912374787
Commit: 30be6dbd0e127040ebbfd65190155594484dd4a3

## Ergebnis

Die automatisierte Discovery-Pipeline hat 1.000 Kandidaten-Datensätze erzeugt. Die Prüfung der CSV-Datei ergab 1.000 eindeutige Foto-IDs, 1.000 eindeutige Beobachtungs-IDs und ausschließlich iNaturalist-Originalvarianten der Bild-URLs. Alle Kandidaten bleiben UNREVIEWED.

| Review-Gruppe | Anzahl | Ziel |
|---|---:|---:|
| Asiatische Hornisse | 200 | 200 |
| Europäische Hornisse | 200 | 200 |
| Honigbiene | 200 | 200 |
| Hummeln | 200 | 200 |
| Wespen | 200 | 200 |
| **Gesamt** | **1.000** | **1.000** |

## Beibehaltene wissenschaftliche Taxa

| Taxon | Kandidaten |
|---|---:|
| Vespa velutina | 200 |
| Vespa crabro | 200 |
| Apis mellifera | 200 |
| Bombus terrestris | 100 |
| Bombus lapidarius | 100 |
| Vespula vulgaris | 100 |
| Vespula germanica | 100 |

Für Hummeln und Wespen werden die beiden Taxa innerhalb der jeweiligen 200er-Gruppe zunächst gleichmäßig berücksichtigt. Ein möglicher Mangel eines Taxons darf nur durch das andere Taxon derselben Gruppe aufgefüllt werden.

## Prüfresultate

- Discovery: erfolgreich.
- iNaturalist-Metadaten-Audit: 0 formale Metadatenfehler.
- Eindeutigkeit: 1.000 Foto- und 1.000 Beobachtungs-IDs.
- Bildvarianten: alle 1.000 URLs verweisen auf die iNaturalist-Originalvariante.
- Artenprüfmanifest: 1.000 Aufgaben.
- Annotationsaufgaben: 1.000 Aufgaben.
- Mobile Prüfgalerie: alle fünf Gruppen mit Filter und Gruppen-Zähler erzeugt.
- Separate CC0-Nachprüfung: 63 Vespa-velutina-Fotos geprüft; 63 API-Lizenzcode-Übereinstimmungen; 0 API-Fehler.

## Grenzen

Diese 1.000 Einträge sind Metadaten- und Bildquellenkandidaten, keine 1.000 freigegebenen Trainingsbilder. Für die übrigen CC-BY-Kandidaten ist die konkrete Lizenzversion zu verifizieren. Der Upload-Status der Kandidaten, die Berechtigung des Urhebers zur Lizenzvergabe, die visuelle Artbestimmung, die Bildqualität und die Bounding-Box-Annotation müssen unabhängig geprüft werden.

Die erzeugten Artefakte weisen daher **0 Trainingsfreigaben** und **0 erzeugte YOLO-Labels** aus. Es wurde kein Modell trainiert oder als einsatzbereit bewertet.
