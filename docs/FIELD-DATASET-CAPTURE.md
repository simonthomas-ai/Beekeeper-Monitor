# Lokale Klassifikationsdaten erfassen und exportieren

Dieser PWA-Workflow erstellt einen **manuell annotierten Bildklassifikationsbestand** für die spätere Prüfung. Er erzeugt keine Vorhersagen und trainiert kein Modell. Er ist vom Kamera-Shadow-Beobachtungseintrag und vom bestehenden Bounding-Box-Trainingspfad getrennt; der Export ist nicht direkt als Bounding-Box-Trainingsbestand verwendbar. Vor einem Training muss ein eigener Datenadapter und eine passende Klassifikations- oder Multi-Label-Modellaufgabe fachlich freigegeben werden.

## Browser- und iPhone-Ablauf

1. Öffne die PWA lokal unter `http://localhost:8000/` oder über eine private HTTPS-Vorschau. Für die iPhone-Kamera ist HTTPS nötig. Die öffentliche Pages-Veröffentlichung ist unabhängig davon deaktiviert.
2. Unter **Lokale Feldaufnahme und manuelle Bildklassifikation** nimm ein Bild auf oder wähle eine lokale JPEG/JPG-, PNG- oder WebP-Datei bis 8 MB. Diese Endungen entsprechen dem BeeKeeper-Feldtest-Validator.
3. Wähle ausdrücklich **Eine oder mehrere Zielklassen** und alle zutreffenden Klassen oder **Negativbild ohne Zielklasse**. Das Negativbild wird als leere Klassenliste `[]` exportiert; es ist keine unbekannte/fehlende Auswahl.
4. Trage Bildquelle/Herkunft und Rechte-/Nutzungsangabe als Freitext ein (Quelle max. 200, Angabe max. 120 Zeichen; keine URL- oder SPDX-Pflicht). Das sind **Nutzereingaben, keine Belege und keine Rechtsprüfung**. Ein optionaler `labeler_id` soll nur ein Pseudonym sein, kein Name oder Kontaktmerkmal.
5. Jedes Bild wird zunächst als ungeprüft gespeichert. Vor dem Export müssen Bild und Labels manuell geprüft sowie die Berechtigung zur Trainingsnutzung ausdrücklich attestiert werden. Diese Attestierung zeichnet nur die Erklärung der Person auf; die App prüft sie nicht unabhängig und macht aus einer Eingabe keinen Rechtebeleg.
6. **Attestierten Bestand als ZIP exportieren** erzeugt auf ausdrücklichen Klick ein Archiv, das `images/` und `annotations.jsonl` enthält. Der lokale Bestand bleibt nach dem Download erhalten; lösche ihn bei Bedarf manuell aus der PWA.

In iOS Safari kann `capture="environment"` die Kamera oder die Fotoauswahl anbieten; die genaue Auswahloberfläche hängt von Gerät und Browser ab. Stelle für direkte iPhone-Aufnahmen **Einstellungen → Kamera → Formate → Maximale Kompatibilität** ein, damit neue Fotos als JPEG aufgenommen werden. Bestehende HEIC-Fotos werden klar abgelehnt; wandle sie vor der Auswahl lokal in der iPhone-Kurzbefehle-App mit „Bild konvertieren“ → JPEG um und speichere das JPEG in „Dateien“. Diese Schritte sind nicht auf einem echten iPhone abgenommen. Die PWA liest keinen GPS-Standort und sendet weder Bilder noch Labels an eine API, BeeKeeper3000 oder einen Modellanbieter. Der Zeitstempel bezeichnet das Hinzufügen zur PWA und wird nicht aus EXIF abgeleitet. Vermeide Personen, private Bereiche und unnötige Standortdetails. Browser- und Betriebssystem-Speicher sind nicht durch die PWA verschlüsselt.

## Exportvertrag

Jede Zeile von `annotations.jsonl` beschreibt ein Bild und enthält:

```json
{
  "image": "images/<id>.jpg",
  "labels": ["vespa_velutina", "apis_mellifera"],
  "captured_at": "2026-11-23T06:00:00.000Z",
  "capture_session_id": "<zufällige Sitzungs-ID>",
  "review_status": "approved",
  "rights": {
    "source": "Eigene Feldaufnahme",
    "basis": "Nutzerangabe; nicht unabhängig geprüft",
    "status": "training_approved"
  }
}
```

`labeler_id` kann als pseudonymer Wert ergänzt werden. Zulässige Klassen-Slugs stammen exakt aus `training/class_schema.py`: `vespa_velutina`, `vespa_crabro`, `other_vespidae`, `apis_mellifera`, `bombus_spp`, `syrphidae`, `other_insect`. Mehrere Slugs pro Bild sind erlaubt. Für ein Negativbild ist `labels` ein leeres Array. Der Vertrag enthält keine Bounding-Boxes, GPS- oder Stations-ID-Felder. Exportdateien bleiben in der Verantwortung der Person, die sie speichert und weitergibt; der Export ist keine automatische rechtliche Freigabe des Gesamtbestands.

Ein konkretes Beispiel mit einer Mehrfach- und einer Negativannotation:

```jsonl
{"image":"images/3a9fd4b4-1.jpg","labels":["vespa_velutina","apis_mellifera"],"captured_at":"2026-11-23T08:00:00+01:00","capture_session_id":"field-session-pseudonym","labeler_id":"reviewer-pseudonym","review_status":"approved","rights":{"source":"Eigene Feldaufnahme","basis":"Nutzerangabe; nicht unabhängig geprüft","status":"training_approved"}}
{"image":"images/c5e72cb1-2.jpg","labels":[],"captured_at":"2026-11-23T08:05:00+01:00","capture_session_id":"field-session-pseudonym","review_status":"approved","rights":{"source":"Eigene Feldaufnahme","basis":"Nutzerangabe; nicht unabhängig geprüft","status":"training_approved"}}
```

Der gemeinsam bearbeitete BeeKeeper-Feldtest-Branch `simonthomas-ai-feldtest-vorbereitung` enthält `training/multilabel_dataset.py`; der am 23.11.2026 geprüfte Worktree-Stand war `a4340f4144837cd6b1056b5dbab7b8a0dbb8069c` plus uncommittete Änderungen. Dessen aktuelle `validate_dataset_archive()`-Implementierung akzeptiert `rights.source` als nichtleeren Freitext bis 200 Zeichen, `rights.basis` als nichtleeren Freitext bis 120 Zeichen, `rights.status="training_approved"` und `review_status="approved"` sowie JPG/JPEG, PNG und WebP. Eine vorhandene `RIGHTS_BASES`-Konstante wird in der aktuellen Validatorfunktion nicht als Allowlist angewendet. Der Validator liegt in einem unveröffentlichten Arbeitsbranch, nicht in BeeKeeper3000 `main`; die Kompatibilität muss bei Änderungen dieses Branches erneut geprüft werden. Der öffentliche `scripts/import_mobile_export.py` auf `main` importiert ein separates Metadatenereignis-Format und ist **kein** Bilddatensatz-Importer.

Das ZIP-Fixture `test_accepts_safe_zip_export` in diesem Partner-Worktree wurde gegen denselben Validator ausgeführt und akzeptiert die vereinbarte Form mit Freitext sowie `rights.status="training_approved"`. Das bestätigt nur den gerade geprüften Session-Worktree, nicht einen Commit oder Merge nach BeeKeeper3000 `main`.

Der Monitor-Prüfer kontrolliert lokal eine ZIP-Datei gegen denselben Zielformatvertrag:

```sh
python scripts/validate_field_dataset_zip.py /sicherer/pfad/beekeeper-field-dataset.zip
python -m unittest tests.test_field_dataset_zip -v
```

Der Cross-Repo-Fixturetest ruft den konkreten Session-Branch-Validator auf, wenn sein Dateipfad gesetzt ist:

```powershell
$env:BEEKEEPER_MULTILABEL_VALIDATOR = 'C:\Pfad\zum\BeeKeeper3000\training\multilabel_dataset.py'
python -m unittest tests.test_beekeeper_importer_roundtrip -v
```

Der Test übergibt eine Mehrfachlabel- und eine Negativbildannotation (`[]`) an BeeKeepers `validate_dataset_archive()`. Der Monitor-Prüfer lehnt unbekannte Slugs, ungeprüfte Einträge, fehlende Bilder, Mehrfachannotierung desselben Bildes, Pfadmanipulation, Bounding-Boxes, GPS, Stations-ID und nicht vertragskonforme Zusatzdateien ab. Das belegt keine tatsächlichen Rechte, fachliche Labelrichtigkeit oder Trainingsfreigabe eines Gesamtbestands.

## Tests und Grenzen

Der Browser-Test prüft Mehrfachlabels, explizite Negativbilder, die manuelle Nutzerattestierung und den Inhalt des ZIP-Vertrags. `python scripts/test_static.py` und `python scripts/check_pwa_deployment_contract.py` prüfen die PWA- und Offline-Shell-Einbindung. Das belegt keine fachliche Labelgenauigkeit, Bildrechte, echte Geräteabnahme, Modellgüte oder Feldfreigabe. Es gibt keinen bereits vorhandenen, durch diesen Workflow annotierten Bestand.
