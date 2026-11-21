# iNaturalist-Bildauflösung – Fehleranalyse und Korrektur (21.11.2026)

## Befund

Die iNaturalist-Prüfgalerien enthielten für die Kandidaten-Fotos die URL-Variante
square.jpg. Für Observation **414481366** / Photo **763034625** war dies
https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/square.jpg.
Die iNaturalist Open-Data-Dokumentation bezeichnet square als 75 × 75 px.
Damit war die verwendete Vorschau für Artprüfung und Bounding-Box-Annotation
nicht ausreichend.

Die sechs veröffentlichten Galeriedateien enthielten zusammen 500 URL-Einträge:
250 in der Gesamtsicht sowie je 50 in fünf Einzelgalerien. In der Gesamtsicht
sind es 250 eindeutige Kandidaten; die Einzelseiten sind dieselben 250 Datensätze
nach Art gruppiert.

## Korrektur

- Alle vorhandenen iNaturalist-Galerie-URLs wurden von square.jpg auf
  original.jpg umgestellt.
- Die Discovery-Pipeline normalisiert den API-Bildlink jetzt auf original.
- Die Verifikationspipeline gibt ebenfalls den normalisierten Bildlink aus.
- Die Galerie-Erzeugung normalisiert ältere Kandidaten-CSV-Dateien und zeigt
  nach dem Laden naturalWidth × naturalHeight an.
- Der autorisierte Import normalisiert bekannte iNaturalist-Thumbnail-URLs vor
  dem Abruf. Im Manifest werden die angeforderte und die tatsächlich verwendete
  URL sowie die gespeicherten Pixelabmessungen erfasst.
- Der Metadaten-Audit weist erkannte iNaturalist-Varianten außer original
  zurück.
- Renderer für die zusätzliche Vespa-Review-Galerie akzeptieren nur noch
  nachweisbare original-Varianten.

## Qualitäts- und Freigabegrenzen

iNaturalist beschreibt original als größte bereitgestellte Variante mit bis zu
2048 px auf der längsten Kante. Das ist nicht notwendigerweise die unveränderte
Kamera-Originaldatei. Der tatsächliche Download muss weiterhin auf Pixelmaße,
Schärfe, Kompression, Zuschnitt und Bildinhalt geprüft werden.

Die Korrektur verbessert die Bildquelle der Prüfgalerien. Sie genehmigt weder
Lizenzrechte noch Artbestimmung, Annotation oder Training. Die bestehende
Training-Freigabe bleibt gesperrt, bis Rechte, Bildqualität, Art und Boxen
individuell geprüft sind. Es wurden keine KI-Gewichte trainiert oder freigegeben.

## Regressionstests

- iNaturalist-URL-Varianten: square, small, medium, large → original.
- Unsichere Hosts, abweichende Photo-IDs und URL-Manipulationen werden abgewiesen.
- Review-Galerie-Ausgabe darf keine iNaturalist-square-URL enthalten.
- Import manifestiert Quelle und tatsächliche Pixelabmessungen.
- Candidate audit meldet niedrige iNaturalist-Varianten als Fehler.
