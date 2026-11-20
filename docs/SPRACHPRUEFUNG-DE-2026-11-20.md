# Sprachprüfung: Website und GitHub-Dokumentation

**Stand: 20.11.2026.** Bestandsaufnahme anhand der Dateilisten beider Hauptbranches und gezielter Textprüfung. **Keine vollständige automatisierte Übersetzungsprüfung sämtlicher Datei-Inhalte.**

## Umfang
- `simonthomas-ai/Beekeeper-Monitor`: 42 Markdown-/HTML-Dateien in der ermittelten Dateiliste, davon 34 Markdown-Dateien.
- `simonthomas-ai/BeeKeeper3000`: 50 Markdown-/HTML-Dateien in der ermittelten Dateiliste, davon 49 Markdown-Dateien.
- Insgesamt **92 Markdown-/HTML-Dateien** als Ausgangspunkt. Diese Zahl schließt Quellcode, JSON, Übersetzungsressourcen und andere Textdateien **nicht** ein.
- Die Hauptseite `index.html` des Monitors hat `lang="de"` und deutschsprachige Überschriften und Bedienhinweise. Einzelne Produktnamen und technische Bezeichner sind bewusst englisch.

## Nachweislich noch zu übersetzende Fachtexte
| Repository | Datei | Befund | Priorität |
|---|---|---|---|
| Beekeeper-Monitor | `docs/APIARY-AI-MODULES.md` | Englischsprachiger Modulkatalog mit technischen Tabellen | Hoch |
| BeeKeeper3000 | `docs/CAMERA-ACCEPTANCE.md` | Englischsprachiges Kamera- und Modellabnahmeprotokoll | Hoch |
| BeeKeeper3000 | `network/SOURCE-API.md` | Englischsprachige Anleitung für die Quell-API | Hoch |

## Bereits eingereichte bzw. integrierte Übersetzungen
- Monitor PR #113: Veröffentlichung, Varroa-Export, Training und deutsche Dokumentationsübersicht.
- BeeKeeper3000 PR #76: Niederspannungsverdrahtung; bei letzter Prüfung **noch offen**.
- BeeKeeper3000 PR #77: Hardware-Referenzentwürfe; integriert.
- BeeKeeper3000 PR #78: Linux-/Windows-Station; integriert.
- BeeKeeper3000 PR #79: Kamera-/Netzwerkübersicht; integriert.
- BeeKeeper3000 PR #80: Modellbewertung und Herkunftsregister; integriert.
- BeeKeeper3000 PR #81: MeshCore-Funkadapter; integriert.

## Prüfvorgaben für alle weiteren Übersetzungen
1. Sichtbare Benutzertexte, Überschriften, Bildbeschriftungen, Bauanleitungen, Sicherheitshinweise und Fehlermeldungen verständlich auf Deutsch übertragen.
2. **Nicht übersetzen:** Programm-IDs, Dateipfade, Befehle, API-Feldnamen, JSON-Schlüssel, Funktionsnamen, standardisierte Lizenzkennungen und andere maschinenlesbare Schnittstellen.
3. Keine erfundenen Messergebnisse, Modellfreigaben, 99-%-Erkennungsversprechen oder nachbaureifen Schaltpläne behaupten.
4. Interne Links, Markdown-Tabellen, Mermaid-Diagramme, Beispielbefehle und CI-Prüfungen nach Änderungen kontrollieren.
5. Noch verbleibende englische Dateien einzeln sichten. Die Dateiliste allein belegt **nicht**, dass eine Datei vollständig englisch oder deutsch ist.
6. Website, mobile PWA, README-Dateien, Hilfetexte und Bedienmeldungen separat auf sichtbare englische Texte untersuchen. Die GitHub-Oberfläche selbst lässt sich durch Übersetzung des Repository-Inhalts **nicht** vollständig auf Deutsch umstellen.

## Nächste Umsetzung
Die drei oben nachgewiesenen englischen Fachtexte übersetzen, anschließend die restlichen Markdown-Dateien beider Repositories und die sichtbaren Oberflächentexte systematisch durchgehen. Diese Bestandsaufnahme ist eine Arbeitsliste und **kein Abschlussnachweis für 100 % Deutsch**.


## Nachprüfung der sichtbaren Web- und PWA-Texte (20.11.2026)

Gezielt auf dem aktuellen Hauptbranch eingesehen:
- Monitor: `index.html`, `app.js`, `alert-ui.js`, `integrations-ui.js`, `live-media.js`, `manifest.webmanifest`, `review/all.html`, `review/apis.html`, `review/velutina.html`.
- BeeKeeper3000: `mobile-pwa/index.html`, `mobile-pwa/app.mjs`, `mobile-pwa/manifest.webmanifest`.

**Ergebnis der Stichprobe:** Formularbeschriftungen, Speicher-/Exportmeldungen, Warnhinweise, Browserberechtigungen und Galeriebedienung sind überwiegend bereits deutsch. Die Bildprüfseiten tragen `lang="de"`; die mobile Meldestelle ebenfalls. Wissenschaftliche Artnamen, JSON-Schlüssel, Browser-API-Bezeichner und Produktnamen bleiben absichtlich unverändert. Die Einträge `Service Worker` und `Bluetooth LE` der mobilen Funktionsliste werden in einem separaten Pull Request sprachlich angepasst.

**Noch zu prüfen:** Die vier weiteren einzelnen Bildprüfseiten (`review/crabro.html`, `review/bombus.html`, `review/vespula.html`, `review/photos.html`), sämtliche nicht durch diese Stichprobe abgedeckten JavaScript-Zweige, die offline zwischengespeicherte PWA nach einem Service-Worker-Update und die tatsächlich auf GitHub Pages veröffentlichte Fassung. Die PWA muss nach Veröffentlichung auf iPhone, Android und Desktop im Browser getestet werden. Ein statischer Quelltextcheck belegt keine erfolgreiche Installation, keine funktionierende Offline-Nutzung und keine korrekte Laufzeitdarstellung.

**Befund zu technischen Fehlermeldungen:** Einige Browserfehler können den vom Browser gelieferten englischen Fehlernamen (`err.name`) anhängen. Das ist ein Diagnosewert und kein bewusst übersetzter Bedienhinweis. Eine spätere benutzerfreundliche Fehlerzuordnung darf keine wichtigen Fehlerdetails verschlucken.

**Nicht verwechseln:** Deutschsprachige Bedienoberfläche, funktionierende Kamera-/KI-Erkennung und DSGVO-Konformität sind voneinander unabhängige Abnahmekriterien. Diese Sprachprüfung bestätigt ausschließlich eingesehene Texte.
