# Fachfreigabe von Bilddaten

**Zweck:** Dieser Prüfschritt verhindert die versehentliche Aufnahme ungeprüfter Bildkandidaten in einen freigegebenen Trainingsmanifest-Export.

```bash
python scripts/approve_training_manifest.py data/research-candidates/velutina/manifest.json --output /tmp/approved-velutina.json
```

Die Freigabe verlangt eine explizite fachliche Artprüfung (`species_verified: true`), separate Zustimmung zur Trainingsverwendung (`human_approved_for_training: true`), Prüfername und Datum, zulässige Lizenz, Original-URL, SHA-256 und sicheren lokalen Dateinamen. Ungeprüfte oder doppelte Dateien werden zurückgewiesen. Der Prozess beendet sich mit Fehlerstatus, wenn nicht ausschließlich geprüfte Datensätze vorliegen.

**Wichtig:** Das Programm kann nicht selbst nachweisen, dass eine Person die Bilder tatsächlich geprüft hat. Es validiert nur die dokumentierten Angaben. Die Prüferidentität, Lizenzbedingungen, tatsächliche Datei-Hashes und Artenbestimmung müssen in einem separaten überprüfbaren Arbeitsablauf bestätigt werden. Der Export wird derzeit nicht automatisch an ein Training angeschlossen; es wurden keine Bilder fachlich freigegeben.
