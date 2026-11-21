# Urheberrecht, Quellenangaben und Rechtewahrung – Prüfstand 21.11.2026

> Technische Bestandsaufnahme, keine anwaltliche Rechtsberatung und keine Feststellung einer Rechtsverletzung.

## Bestätigte Befunde

- Im Hauptverzeichnis von `Beekeeper-Monitor` wurde keine `LICENSE`-Datei gefunden. Die README erklärt, dass noch keine Projektlizenz festgelegt ist und die Rechte bis dahin vorbehalten bleiben.
- `scripts/import_commons_candidates.py` übernimmt aus Wikimedia Commons Metadaten wie `LicenseShortName`, `LicenseUrl`, `Artist`, `Credit`, Quellseite und Quell-URL. Kandidaten werden ausdrücklich nicht automatisch für KI-Training freigegeben.
- Die öffentliche Startseite enthält eine belegte GitHub-Aktivitätsübersicht. GitHub-Jobzeiten sind weder Agentenstunden noch eine Aussage über die Urheberschaft am Projekt.
- Die aktuelle Dokumentation verweist bereits auf `docs/upstream-license-audit-2026-11-19.md` und `training/README.md`.

## Maßnahmen vor der Veröffentlichung oder Nutzung fremder Werke

1. **Rechtekette je Werk:** Urheber/Rechteinhaber, Originalquelle, Lizenzversion, Lizenzlink, Abrufdatum, Änderungen, ggf. Einwilligung und Nutzungskontext dokumentieren.
2. **Attribution:** Für CC-BY-Werke Urheber, Lizenzlink, Materialquelle und Bearbeitungen angemessen ausweisen. CC0-Material ebenfalls mit Quelle dokumentieren, auch wenn keine Attribution vorgeschrieben ist.
3. **Lizenzkompatibilität:** ShareAlike-, NonCommercial-, NoDerivatives-, Software- und Modelllizenzen separat prüfen. Nicht allein auf eine Kurzbezeichnung in API-Metadaten vertrauen.
4. **Bildrechte:** Auch Persönlichkeitsrechte, Marken und Rechte Dritter prüfen. Unklare Werke nicht als freigegeben markieren.
5. **Eigene Rechte:** Für eigene Quelltexte, Texte, Grafiken und Dokumentation Urheberschaft und Beitragsherkunft dokumentieren. Eine Repository-Lizenz nur nach ausdrücklicher Entscheidung der Berechtigten ergänzen.
6. **Belege sichern:** Fundstelle, Datum, URL, Originalwerk, Vergleich, Lizenz und Screenshots dokumentieren; bei möglicher Fremdnutzung erst danach rechtliche Schritte prüfen.

## Vorgehen bei möglicher unberechtigter Übernahme

- Zuerst prüfen, **wer** die Rechte hält und ob eine Lizenz oder andere Erlaubnis die Nutzung deckt.
- Nur bei belegter eigener Rechtsposition und konkreter Nutzung eine sachliche Anfrage auf Urheberbenennung, Lizenzklärung oder Entfernung vorbereiten.
- Keine automatisierten Abmahnungen, Zahlungsforderungen, DMCA-Meldungen oder öffentlichen Vorwürfe ohne gesonderte rechtliche Prüfung und ausdrückliche Freigabe des Rechteinhabers.
- Für komplexe Fälle in Deutschland anwaltlichen Rat einholen.

## Offene Entscheidungen

- Wer darf eine Lizenz für den selbst entwickelten Projektcode verbindlich vergeben?
- Welche Drittmaterialien sind tatsächlich im veröffentlichten Website-Artefakt enthalten?
- Sind sämtliche Bildgalerien mit konkreter Attribution, Lizenzlink und Bearbeitungshinweis versehen?
- Welche Modelle und Bibliotheken werden künftig ausgeliefert, und welche Copyleft-Pflichten entstehen daraus?

## Verlässliche Grundlagen

- Creative Commons BY 4.0: https://creativecommons.org/licenses/by/4.0/legalcode
- Creative Commons Lizenzhinweise: https://creativecommons.org/share-your-work/licensing-considerations/version4/
