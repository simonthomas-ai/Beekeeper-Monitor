# Erkennungsarchitektur – technischer Review (2026-11-21)

## Zweck und Freigabestatus

Dieses Dokument legt einen belastbaren Vergleichsplan für die Erkennung von *Vespa velutina* an realen Bienenstand-Kameras fest. Es ist eine Architektur- und Datenquellenbewertung, **keine Modellfreigabe**.

Aktueller Stand:
- Der Code enthält einen experimentellen YOLO-Mehrklassen-Baseline-Trainer.
- Es liegt im Repository kein vollständiger, rechtegeprüfter und fachlich freigegebener Datensatz unter `datasets/beekeeper/` vor.
- Es gibt keine durch dieses Projekt trainierten oder unabhängig am Feld geprüften Gewichte.
- Es werden keine externen Gewichte oder Bilder ungeprüft übernommen.
- Es wird keine Falle, kein Aktor und keine sonstige Bekämpfungshardware angesteuert. Der Zweck ist Erkennung, Dokumentation und menschliche Prüfung.

## Zu vergleichende Architekturen

### A. Ein-Stufen-Detektor (bestehende Baseline)

Ein YOLO-Detektor lokalisiert Insekten und ordnet jede Box einer der sieben Projektklassen zu:

1. `vespa_velutina`
2. `vespa_crabro`
3. `other_vespidae`
4. `apis_mellifera`
5. `bombus_spp`
6. `syrphidae`
7. `other_insect`

Vorteile: ein Modellartefakt, einfache Laufzeitintegration, gemeinsamer Box-/Klassenoutput und gute Eignung als reproduzierbare Vergleichsbasis.

Risiken: Artenunterschiede können bei kleinen, schnellen oder unscharfen Objekten zu fein sein; Hintergrund, Kameraoptik, Abstand und Beleuchtung können stark von Web-/Laborbildern abweichen. Die Klasse `other_insect` darf nicht als Ersatz für unbestimmte positive Arten verwendet werden.

### B. Zwei-Stufen-Pipeline (Kandidat, noch nicht implementiert)

1. Ein Detektor mit hoher Insekten-Recall lokalisiert Kandidaten und erzeugt normierte Crops.
2. Ein separater Crop-Klassifikator unterscheidet *V. velutina*, *V. crabro*, andere Vespidae sowie die relevanten Nichtziel-Insekten.
3. Eine zeitliche Track-/Eventlogik fasst mehrere Frames desselben Vorbeiflugs zusammen und protokolliert kurze Ereignisse, statt jede Einzelbox als unabhängige Sichtung zu zählen.

Eine 2025/2026 veröffentlichte Hochschularbeit beschreibt einen zweistufigen Ansatz zur Trennung des Hintergrund-/Lokalisierungsproblems von der anschließenden Insektenklassifikation. Das ist ein sinnvoller Vergleichskandidat, aber kein Beleg für die Genauigkeit dieses Projekts: Die berichtete Feldprüfung ist nur eingeschränkt auf *V. velutina* übertragbar, weil dort *V. crabro* als Feld-Proxy verwendet wurde.

**Entscheidung:** A bleibt Referenzmodell. B wird erst als paralleler Forschungszweig ergänzt, wenn reale, freigegebene Crop- und Klassenlabels vorliegen. Beide Ansätze müssen auf exakt denselben gruppengetrennten Holdout-Daten verglichen werden.

## Quellenbewertung und Rechte

### ISR / Roboflow – Vespa velutina v1

Quelle: https://universe.roboflow.com/institute-of-systems-and-robotics-isr/vespa-velutina-hihv9-upzpe/dataset/1

Die Projektseite listet 1.508 Bilder und CC BY 4.0. Für die veröffentlichte Version werden außerdem 3.618 verarbeitete Export-/Trainingsbeispiele und automatische Augmentationen beschrieben. Daraus folgt **nicht**, dass 3.618 unabhängige Originalaufnahmen existieren. Vor einer möglichen Aufnahme sind mindestens erforderlich:

- Export- und Lizenzangaben der konkret heruntergeladenen Version archivieren.
- Für jedes Originalbild Quelle, Urheber, genaue CC-BY-Version, Attribution und SHA-256 sichern.
- Originale von abgeleiteten/geaugmentierten Bildern unterscheiden und Augmentationen dem jeweiligen Original/Beobachtungscluster zuordnen.
- Ähnliche/identische Bilder über alle verfügbaren Quellen finden.
- Standort, Kamera, Datum, Beobachtung und Fotografen als Gruppen behandeln.
- Prüfen, ob Train/Val/Test wirklich unabhängig sind; bei Unsicherheit alle verwandten Bilder in nur einen Split legen.
- Das Dataset ist im Kern ein *V. velutina*-Datensatz und ersetzt nicht die sechs weiteren Projektklassen oder deren schwierige Negativbeispiele.

Status im Projekt: **Kandidat; nicht importiert und nicht freigegeben**. CC-BY-Anforderungen und Rechtekette sind je Datei/Export zu prüfen; eine Kennzeichnung auf der Plattform ersetzt nicht die Prüfung des ursprünglichen Fotografenrechts.

### Weitere Quellen und Modellartefakte

- VespAI ist eine hilfreiche Feld-/Systemreferenz. Das zugehörige Code-/Validierungsdatenmaterial wird mit CC BY-NC-SA 4.0 und Zugangsbedingungen beschrieben. Nicht automatisch in die CC0/CC-BY-Trainingsbasis aufnehmen.
- Das öffentliche Waspinator-Projekt enthält einen YOLO26-Detektor für *V. velutina* und *V. crabro*. Der Code ist AGPL-3.0; die eingebetteten Modelldateien tragen eine AGPL-Kennzeichnung. Im geprüften Modellverzeichnis ist keine ausreichende per-Bild-Datenprovenienz hinterlegt. Deshalb weder Gewichte noch Labels importieren, bis Rechte, Herkunft und Trainingsdaten nachgewiesen sind.
- GBIF-/iNaturalist-Treffer sind Such-/Metadatenkandidaten, keine pauschal freigegebenen Fotos. Medienlizenz, Urheber und Attribution müssen je Bild kontrolliert werden; die Lizenz des Beobachtungsdatensatzes ist nicht automatisch die Lizenz der Bilddatei.
- Wissenschaftliche Papers und deren publizierte Kennzahlen dienen nur der Methodikplanung. Sie sind keine Projektmetriken und erlauben keine Übernahme fremder Bilder, Gewichte oder Annotationen ohne gesonderte Rechteprüfung.

## Feldorientierter Datensatzplan

### Aufnahmebedingungen

Die Daten müssen mit den späteren Stationskameras aufgenommen oder deren Eigenschaften realistisch abdecken:

- Tag, Dämmerung, Nacht und Gegenlicht
- trockene, nasse und reflektierende Hintergründe
- unterschiedliche Kamera-/Objektivtypen, Auflösungen und Bildraten
- mehrere Entfernungen, Objektgrößen und Anflugwinkel
- Bewegung, Bewegungsunschärfe, Teilverdeckung und kurze Vorbeiflüge
- ruhige sowie stark belebte Bienenstände
- echte negative Beispiele: Honigbienen, Hummeln, Schwebfliegen, andere Wespen, Europäische Hornissen und sonstige Insekten

Ein Paper zu einem portablen Feldsystem berichtet, dass schnelle beziehungsweise sehr kurze Hornissenereignisse im Feld übersehen werden können. Daher müssen Recall und Fehlalarmrate auch nach Ereignisdauer, Entfernung und Bewegungsunschärfe ausgewertet werden. Einzelbilder aus demselben Vorbeiflug dürfen nicht über die Splits verteilt werden.

### Split-Regeln

- Train/Val/Test nach Standort, Beobachtung, Kamera und Fotografengruppe trennen; keine Frames desselben Vorbeiflugs in mehreren Splits.
- Das Testset bleibt bis zum Abschluss der Modell-/Schwellwertauswahl unangetastet.
- Zusätzlich einen externen Feld-Holdout mit bisher ungesehenen Standorten/Kameras aufbauen.
- Für jedes Bild und Label bleiben SHA-256, Quelle, Lizenz, Reviewer-Pseudonym, Zeitstempel und Gruppenzugehörigkeit erhalten.
- Automatisch erzeugte Augmentationen werden nicht als unabhängige Beobachtungen gezählt und bleiben im Split ihres Originals.

## Vergleichs- und Abnahmemetriken

Mindestens pro Klasse und zusätzlich nach Aufnahmekondition erfassen:

- Precision, Recall, F1, AP/mAP und vollständige Confusion Matrix.
- PR-Kurven und dokumentierte Konfidenzschwellen; Schwellen ausschließlich auf Val auswählen.
- Fehlalarme pro Kamerastunde und pro Standorttag, nicht nur Bildgenauigkeit.
- Recall für kurze Events, getrennt nach Ereignisdauer, Abstand, Bildgröße, Beleuchtung und Unschärfe.
- Ereignis-Deduplikation: Mehrere aufeinanderfolgende Frames eines Tieres nicht als mehrere unabhängige Sichtungen zählen.
- Konfidenzintervalle und Anzahl unabhängiger Standorte/Beobachtungen offen ausweisen.
- Laufzeit, Speicher, Temperatur und FPS auf den tatsächlichen Zielgeräten testen.

Die bestehende Pipeline validiert aktuell formal Klassenabdeckung, Labelgeometrie, Datei- und Provenienz-Hashes sowie Ultralytics-Klassenmetriken. Sie berechnet noch keine belastbare Feld-Fehlalarmrate pro Kamerastunde, keine unabhängigen Standort-Konfidenzintervalle und keine separate Event-Recall-Kurve. Diese Punkte bleiben vor Produktivfreigabe offen.

## Nächster Implementierungsschritt nach Eingang echter Daten

1. Quellen-/Lizenzprüfung und Quarantäne pro Medium.
2. CVAT-Review der Art und Bounding Boxes durch fachkundige Prüfer.
3. Duplikat-/Near-Duplicate-Analyse und gruppenbasierte Split-Freigabe.
4. Baseline A mit identischem Holdout trainieren und auswerten.
5. Crop-Datensatz aus denselben geprüften Boxen erstellen; Kandidat B trainieren.
6. A gegen B auf identischen Bildern, Events und Standorten vergleichen.
7. Nur nach unabhängiger Feldvalidierung und Rechtefreigabe einen signierten Modellmanifest-/ONNX-Release erstellen.

**Freigaberegel:** Keine reale automatische Artbestimmung und keine automatische Nest-/Bekämpfungsentscheidung allein aufgrund einer Modellkonfidenz. Unklare Fälle bleiben im menschlichen Review.
