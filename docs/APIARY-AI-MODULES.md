# KI-Module für die Imkerei – experimentell, nicht zur Diagnose freigegeben

Dieser Katalog beschreibt einen technischen **Integrationsvertrag**. Er ist weder ein KI-Modell noch eine Gewichtsdatei oder eine funktionsfähige Erkennungsimplementierung. Jedes Modul ist anfangs deaktiviert. Ergebnisse dürfen ohne unabhängige Belege und menschliche Prüfung niemals als bestätigt dargestellt werden.

| Modulkennung | Aufgabe | Eingabe | Kandidat / Status | Ausgabe | Grenze im praktischen Einsatz |
|---|---|---|---|---|---|
| `varroa_board` | Milben auf einer herausnehmbaren Bodeneinlage zählen | Scharfes Makrobild von oben mit Maßstab | VarroDetector-Kandidat; Rechte und Gewichte ungeprüft | Unbestätigte Anzahl und Markierungen | Eine Milbenanzahl entspricht ohne Probenahmeprotokoll nicht unmittelbar dem Befallsgrad |
| `varroa_on_bee` | Sichtbare Milben auf Bienen erkennen | Makrobild des Bienenkörpers | Gratheon `models-varroa-on-bee`, YOLO11n; Rechte und Gewichte ungeprüft | Unbestätigte Markierungen | Gemeldeter Varroa-Recall: 0,651; ein negatives Ergebnis schließt Befall nicht aus |
| `queen_on_comb` | Königin auf der Wabe lokalisieren | Scharfes Wabenfoto oder -video | Gratheon `models-queen-bee-detector`, YOLOv8n; Rechte und Gewichte ungeprüft | Unbestätigte Markierung | Gemeldeter Recall: 0,859; eine fehlende Erkennung bedeutet nicht, dass keine Königin vorhanden ist |
| `swarm_activity` | Ungewöhnliche Fluglochaktivität erkennen | Zeitgestempelte Zählwerte, Video und optional Stockgewicht | Kein validiertes Modell zur Schwarmvorhersage ausgewählt | Aktivitätsauffälligkeit, keine gesicherte Schwarmvorhersage | Orientierungsflüge und Wetter können Ergebnisse verfälschen |
| `pollen_flow` | Anfliegende Bienen mit Pollen zählen | Fluglochvideo | Neue beschriftete Trainingsdaten und Modell nötig | Anzahl der Pollenträger | Misst nicht unmittelbar die Pollenvorräte |
| `brood_pattern` | Sichtbares Brutbild beschreiben | Gut ausgeleuchtete Wabenbilder | Eigener Datensatz zur Bildsegmentierung erforderlich | Markierungen nur zur menschlichen Sichtung | Keine Krankheitsdiagnose |

## Vorgeschlagenes Standardmanifest für Module

```json
{
  "schema": "vespaguard.apiary-module.v1",
  "id": "queen_on_comb",
  "enabled": false,
  "release_status": "research_only",
  "task": "object_detection",
  "runtime": "onnxruntime-web-or-local-edge",
  "weights_sha256": null,
  "weights_license": null,
  "training_data_evidence": null,
  "independent_validation_evidence": null,
  "hardware_acceptance_evidence": null,
  "human_confirmation_required": true
}
```

Die JSON-Feldnamen und Werte sind technische Kennungen und bleiben deshalb unverändert. Dieses Manifest ist ein **Beispiel**, keine Modellfreigabe.

## Voraussetzungen vor der Aktivierung eines Moduls

1. Original-Repository, exakte Version bzw. Commit, Lizenzen für Code und Gewichte, Abhängigkeiten einschließlich Ultralytics-Bedingungen sowie Trainingsbilder und Urhebernennung je Bild prüfen. Die SHA-256-Prüfsumme der konkreten Modellgewichtsdatei dokumentieren.
2. Mit unabhängigen Testbildern von anderen Bienenständen, Geräten, Jahreszeiten und Beleuchtungsbedingungen bewerten. Für jede Klasse Präzision, Recall, Konfidenzintervalle sowie Fehlalarme und übersehene Fälle pro Betriebsstunde veröffentlichen. **Keine 99-%-Erkennungsquote ohne Belege behaupten.**
3. Erkennung standardmäßig lokal ausführen. Bilder, Ton oder GPS-Daten nur nach gesonderter Datenschutzprüfung und Einwilligung oder einer anderen dokumentierten Rechtsgrundlage an fremde APIs übertragen.
4. Ausschließlich unbestätigte Ereignisse (`unconfirmed`) ausgeben. Niemals automatisch Behandlungen, Königinnenwechsel oder Eingriffe bei Schwarmverdacht auslösen.
5. Echte iPhones, Android-Geräte und Raspberry Pis auf Reaktionszeit, Akkubelastung, Wiederanlauf nach Offlinebetrieb und Temperaturentwicklung prüfen.
6. Bestehende Hornissenerkennung und PWA nicht beeinträchtigen. Code und Gewichte erst nach dokumentierter und genehmigter Feldfreigabe integrieren.

## Kandidatenquellen (nicht übernommen)

- https://github.com/Gratheon/models-varroa-on-bee
- https://github.com/Gratheon/models-queen-bee-detector
- https://github.com/jodivaso/varrodetector
- https://gratheon.com/research/models/

Die genannten Forschungskennzahlen stammen von den jeweiligen Urhebern und sind **keine eigenen Leistungsmessungen von VespaGuard**.
