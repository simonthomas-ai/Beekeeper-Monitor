# Wikimedia-Commons-Import für VespaGuard

Der Importer erstellt **Forschungskandidaten**, keine automatisch freigegebenen Trainingsbilder. Standardmäßig werden **nur Metadaten** abgerufen; Bilder werden ausschließlich mit `--download` heruntergeladen.

```bash
python scripts/import_commons_candidates.py --class-name velutina --limit 20
python scripts/import_commons_candidates.py --class-name crabro --limit 20
# Optional: Bilder ausdrücklich herunterladen
python scripts/import_commons_candidates.py --class-name velutina --limit 20 --download
```

Ausgabe: `data/research-candidates/<klasse>/manifest.json` mit Bildquelle, Lizenz, Urheberhinweis, Bild-URL, vorgeschlagener Klasse und Freigabestatus. Bei tatsächlichem Download werden SHA-256-Prüfsummen gespeichert.

**Sicherheit und Qualität:** Nur ausgewählte Commons-Lizenznamen (CC0, CC BY 2.0/3.0/4.0, Public Domain) und Bild-MIME-Typen werden angenommen. Die Lizenz- und Urhebermetadaten müssen vor Weiterverwendung manuell geprüft werden; HTML-Felder nicht ungefiltert in Webseiten darstellen. Eine Commons-Kategorie garantiert keine korrekte Artbestimmung. `human_approved_for_training` bleibt immer `false`. Dateigröße ist auf 12 MB begrenzt. Die API-Abfrage berücksichtigt in dieser ersten Version nur die ersten bis zu 100 Kategorieeinträge; kein vollständiger Korpus, keine Audio-Daten, keine Modelltrainingsfunktion.

**Hinweis:** Die Lizenzbedingungen können weitere Pflichten enthalten, insbesondere Namensnennung, Link zur Lizenz und Kennzeichnung von Änderungen. Für Public-Domain-Angaben müssen länderspezifische Rechte geprüft werden. Downloads dürfen nicht ungeprüft ins öffentliche Repository committed werden.
