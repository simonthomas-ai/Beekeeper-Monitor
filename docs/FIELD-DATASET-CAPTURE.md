# Lokale Klassifikationsdaten erfassen und exportieren

**Status: lokaler, manueller Erfassungs- und Exportpfad; nicht trainiert oder feldvalidiert.** Die PWA erzeugt keine Vorhersagen, führt keine Inferenz aus und lädt keine Bilder oder Annotationen hoch. Der Export ist ein ZIP mit `images/` und `annotations.jsonl`; er ist kein Bounding-Box-Datensatz und keine automatische Rechte- oder Fachfreigabe.

## Browser- und iPhone-Ablauf

1. Öffne die PWA lokal unter `http://localhost:8000/` oder über eine private HTTPS-Vorschau. Für iPhone-Kamerazugriff ist HTTPS erforderlich. Die öffentliche Pages-Veröffentlichung bleibt separat deaktiviert.
2. Unter **Lokale Feldaufnahme und manuelle Bildklassifikation** wähle ein JPEG/JPG-, PNG- oder WebP-Bild bis 8 MB. HEIC wird bewusst abgelehnt; wandle es vor der Auswahl lokal auf dem Gerät in JPEG um.
3. Wähle ausdrücklich **Eine oder mehrere Zielklassen** und alle zutreffenden Klassen oder **Negativbild ohne Zielklasse**. Ein Negativbild wird mit `labels: []` exportiert.
4. Trage als Quelle entweder exakt **Eigene Feldaufnahme** oder eine credential-freie HTTPS-Fotoquellen-URL ein. URLs mit Zugangsdaten, Query-Parametern oder Fragmenten werden abgelehnt.
5. Wähle eine strukturierte Rechtebasis:
   - **CC0-1.0:** Der kanonische Nachweis `https://creativecommons.org/publicdomain/zero/1.0/` wird automatisch ergänzt.
   - **CC-BY-4.0:** Der kanonische Nachweis `https://creativecommons.org/licenses/by/4.0/` wird automatisch ergänzt; eine Attribution bis 500 Zeichen ist Pflicht.
   - **LicenseRef-ExplicitPermission:** Eine opake Referenz bis 200 Zeichen ist Pflicht. Keine Namen, E-Mail-Adressen, privaten Dokumente oder vertraulichen URLs eintragen.
6. Jedes Bild wird zunächst ungeprüft lokal gespeichert. Vor dem Export müssen Bildinhalt/Labels manuell geprüft und die Berechtigung zur Trainingsnutzung ausdrücklich attestiert werden. Diese Attestierung hält nur eine Nutzeraussage fest; sie ist keine unabhängige Rechtsprüfung.
7. **Attestierten Bestand als ZIP exportieren** startet den Download erst nach ausdrücklichem Klick. Die lokalen Originale bleiben im Browser, bis sie dort gelöscht werden.

Der Zeitstempel bezeichnet das Hinzufügen in der PWA und wird nicht aus EXIF abgeleitet. Die PWA liest für diesen Workflow keinen GPS-Standort und überträgt weder Bilder noch Labels an eine API, BeeKeeper3000 oder einen Modellanbieter. Browser- und Betriebssystem-Speicher sind durch die PWA nicht verschlüsselt. Schütze das Gerät und heruntergeladene ZIP-Dateien entsprechend. Bereits exportierte Kopien werden durch das Löschen lokaler Datensätze nicht entfernt.

## Exportvertrag

Jede Zeile von `annotations.jsonl` enthält Bildreferenz, Klassen, Erfassungszeit, zufällige Sitzungs-ID, Prüfstatus, strukturierte Rechteangaben sowie `reviewed_by` und `reviewed_at`. `reviewed_by` muss eine pseudonyme Kennung im Format `reviewer:<opaque-id>` sein; `reviewed_at` ist ein eigener zeitzonenbewusster Zeitpunkt der manuellen Prüfung und darf nicht vor `captured_at` liegen. `labeler_id` bleibt optional und bezeichnet getrennt die Labeler-Kennung. Namen, E-Mail-Adressen und URLs sind unzulässig. Diese Review-Metadaten belegen weder unabhängige Rechteprüfung noch entomologische Bestätigung. `reviewed_at` stammt aus der lokalen Browser-Uhr und ist nicht kryptografisch signiert oder als vertrauenswürdige Zeit bestätigt.

Beispiel für eine eigene Aufnahme mit dokumentierter individueller Erlaubnis:

```json
{
  "image": "images/<id>.jpg",
  "labels": ["vespa_velutina", "apis_mellifera"],
  "captured_at": "2026-11-26T08:00:00Z",
  "capture_session_id": "<zufällige Sitzungs-ID>",
  "review_status": "approved",
  "reviewed_by": "reviewer:field-reviewer-0001",
  "reviewed_at": "2026-11-26T08:30:00Z",
  "rights": {
    "source": "Eigene Feldaufnahme",
    "basis": "LicenseRef-ExplicitPermission",
    "permission_ref": "consent-record-2026-001",
    "status": "training_approved"
  }
}
```

Beispiel für eine externe CC-BY-4.0-Quelle:

```json
{
  "image": "images/<id>.jpg",
  "labels": [],
  "captured_at": "2026-11-26T08:05:00Z",
  "capture_session_id": "<zufällige Sitzungs-ID>",
  "review_status": "approved",
  "reviewed_by": "reviewer:field-reviewer-0001",
  "reviewed_at": "2026-11-26T08:35:00Z",
  "rights": {
    "source": "https://example.org/photos/example",
    "basis": "CC-BY-4.0",
    "evidence_url": "https://creativecommons.org/licenses/by/4.0/",
    "attribution": "Name der Urheberperson (CC BY 4.0)",
    "status": "training_approved"
  }
}
```

Der Export setzt bewusst **kein** `publication_allowed`. Eine Attestierung zur Trainingsnutzung erteilt nicht automatisch eine Erlaubnis zur öffentlichen Weitergabe. Die drei Rechtebasen sind eine begrenzte technische Eingabe-Allowlist, keine rechtliche Aussage über das konkrete Bild. Die Referenz für eine individuelle Erlaubnis muss auf einen lokal verwahrten Nachweis verweisen; der Nachweis selbst gehört nicht in das Manifest oder CI.

Zulässige Klassen-Slugs: `vespa_velutina`, `vespa_crabro`, `other_vespidae`, `apis_mellifera`, `bombus_spp`, `syrphidae`, `other_insect`. Mehrere Slugs pro Bild sind möglich. Ein Negativbild verwendet ein leeres Array. Der Vertrag enthält keine Bounding-Boxes, GPS- oder Stations-ID-Felder.

### Altaufnahmen

Vor dem strukturierten Rechtevertrag gespeicherte Freitextangaben wie `Nutzerangabe` werden nicht stillschweigend umgedeutet. Solche Altaufnahmen können nicht exportiert werden; erfasse sie nach Prüfung erneut mit der strukturierten Auswahl oder lösche sie lokal.

## Repository-übergreifende Prüfung

Der Monitor prüft den Browser-ZIP-Export in `tests/field-dataset.spec.cjs`. Im Ein-Klick-Gesamttest wird derselbe Browser-Export gegen den unveränderlich gepinnten BeeKeeper3000-Validator aus Commit `031c91370da85c6fa42dd8992b6adfc20ddf06c7` geprüft. Dieser Stand erzwingt zusätzlich pseudonyme `labeler_id`-Kennungen im Format `reviewer:<opaque-id>` und enthält den fail-closed Modellmanifest-v2-Rechtevalidator. Er lehnt außerdem Modellquellen-, Lizenznachweis- und Validierungsbericht-URLs mit Query oder Fragment ab, damit keine signierten URLs oder privaten Referenzen in Provenienzmetadaten gelangen. Der Monitor-ZIP-Export enthält weiterhin `images/` und `annotations.jsonl`; der getrennte `provenance.jsonl`-Konverter aus BeeKeeper3000 Issue #120 fehlt noch. Der Job führt zusätzlich Validator-Unit-Tests und den Python-Fixture-Roundtrip aus. Die Testbilder sind künstliche Byte-Fixtures; es werden keine privaten Fotos, realen Rechteunterlagen oder Trainingsdaten in CI hochgeladen.

Lokaler Cross-Repo-Fixturetest:

```powershell
$env:BEEKEEPER_MULTILABEL_VALIDATOR = 'C:\Pfad\zum\BeeKeeper3000\training\multilabel_dataset.py'
python -m unittest tests.test_beekeeper_importer_roundtrip -v
```

Die Tests prüfen das Dateiformat und die technische Rechtefeld-Validierung. Sie beweisen weder die Echtheit einer Erlaubnis noch die korrekte Artbestimmung, Trainingsqualität oder Modellleistung. Ein grüner CI-Lauf ist keine KI- oder Feldfreigabe.

## Grenzen und Freigaben

- Kein freigegebenes Modellgewicht wird durch diesen Workflow geladen oder aktiviert.
- Der Siebenklassen-Datensatzvertrag ist Klassifikation mit mehreren Labels, nicht Objektdetektion mit Bounding-Boxes.
- Eine ausreichende Anzahl unabhängiger Fotografen-/Sitzungs-/Quellgruppen ist vor einem Split erforderlich.
- Vor einem Training müssen Bildrechte, Datenschutz, fachliche Annotationen und unabhängige Holdout-Daten separat geprüft werden.
- Es gibt derzeit keine nachgewiesene 99-%-Erkennungsrate und keine automatische Hornissen- oder Varroa-Feldfreigabe.
