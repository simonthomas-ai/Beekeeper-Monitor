# Reproduzierbare Trainingsdaten-Aufteilung

Der Workflow verwendet **ausschließlich bereits fachlich freigegebene Bildmanifeste**. Er lädt keine Bilder herunter und trainiert kein Modell.

```bash
python scripts/split_approved_dataset.py /tmp/approved-velutina.json --output /tmp/velutina-split.json --seed 42
```

Jeder Eintrag muss zusätzlich `observation_group` enthalten: eine stabile Kennung für zusammengehörige Aufnahmen desselben Beobachtungsvorgangs. Die Aufteilung erfolgt nach Artklasse und Beobachtungsgruppe, sodass keine Gruppe gleichzeitig in Training, Validierung und Test vorkommt. Mindestens drei voneinander unabhängige Gruppen je Klasse sind technisch erforderlich; für eine belastbare Genauigkeitsmessung reichen drei Gruppen ausdrücklich nicht aus.

**Noch offene Qualitätsanforderungen:** Verschiedene Beobachtungsgruppen können trotzdem denselben Fotografen, Bienenstand, Standort oder Bildvarianten enthalten. Vor Modelltraining müssen diese Beziehungen zusätzlich geprüft und gegebenenfalls in übergeordnete Gruppen zusammengeführt werden. Eine Bild-Hash-Prüfung erkennt keine nahezu identischen Aufnahmen. Für eine seriöse Modellbewertung sind ausreichend große, unabhängig erhobene Testgruppen und fachliche Artbestimmungen nötig.

**Status:** Nur Programmcode und Unit-Tests; keine echten Trainingsbilder kuratiert und keine KI trainiert.
