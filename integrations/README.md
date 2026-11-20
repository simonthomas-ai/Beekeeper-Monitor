# Lokaler Ereignisempfänger

Dieser Empfänger speichert ausschließlich validierte Ereignis-Metadaten lokal in SQLite. Bilder, Audiodaten, GPS-/Koordinatenfelder, Freitext-Erweiterungen und personenbezogene Freifelder sind im Ereignisvertrag ausdrücklich nicht zulässig.

## Eigenschaften

- Standardmäßig ausschließlich `127.0.0.1:8765`; kein öffentlicher Listener.
- Bearer-Token mit mindestens 24 Zeichen; Vergleich in konstanter Zeit.
- Höchstens 32 KiB je Request, 16 parallele Worker, begrenzte Queue, 5-Sekunden Socket-Timeout und 10-Sekunden Gesamtdeadline für den Request-Body.
- 60 Requests pro Client-IP und Zeitfenster von 60 Sekunden; begrenzte Rate-Limit-Tabelle.
- Strikte JSON-Vertragsprüfung, UTC-Zeitstempel mit Zeitzone, keine unbekannten Payload-Felder oder doppelten JSON-Schlüssel.
- SQLite-WAL, volle Synchronisierung, idempotente SHA-256-Ereignis-IDs, konfigurierbare Aufbewahrung und Obergrenze für Datensätze.
- Authentifizierter Abruf (maximal 500 Ereignisse) und gezieltes Löschen anhand der Ereignis-ID.
- Keine Ausgabe von Payloads, Tokens oder fremdkontrollierten Headern in Serverlogs.

## Start unter Windows PowerShell

Aus dem Repository-Hauptverzeichnis:

```powershell
$bytes = New-Object byte[] 32
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$env:VESPAGUARD_INGEST_TOKEN = [Convert]::ToBase64String($bytes)
$env:VESPAGUARD_INGEST_DB = Join-Path $env:LOCALAPPDATA "BeeKeeper-Monitor\events.sqlite3"
$env:VESPAGUARD_RETENTION_DAYS = "90"
$env:VESPAGUARD_MAX_EVENTS = "100000"
python -m integrations.local_ingest
```

Der Token wird nur für die aktuelle PowerShell-Sitzung gesetzt und nicht in eine Datei geschrieben. Für einen automatischen Dienst ist ein Windows-Dienstkonto mit eingeschränkten NTFS-Rechten einzurichten; Token sicher als Dienstgeheimnis bereitstellen.

## API

Alle Endpunkte benötigen den gleichen Header:

```text
Authorization: Bearer <VESPAGUARD_INGEST_TOKEN>
```

Ereignis senden:

```powershell
$headers = @{ Authorization = "Bearer $env:VESPAGUARD_INGEST_TOKEN" }
$event = @{
  kind = "camera_detection"
  device_id = "cam-01"
  timestamp = [DateTime]::UtcNow.ToString("o")
  source = "local_camera"
  schema_version = 1
  payload = @{ label = "vespa_velutina"; confidence = 0.97 }
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8765/api/v1/events" -Headers $headers -ContentType "application/json" -Body $event
```

Ereignisse abrufen (1 bis 500):

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/v1/events?limit=100" -Headers $headers
```

Ein Ereignis löschen (ID aus der GET-Antwort verwenden):

```powershell
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:8765/api/v1/events/<64-stellige-event-id>" -Headers $headers
```

## Zulässige Payloads

| Typ | Erlaubte Felder |
| --- | --- |
| `camera_detection` | `label`, `confidence`; optional: `origin_event_id`, `verification_status="unverified"`, `prey_detected` |
| `acoustic_event` | `label`, `confidence` |
| `hive_telemetry` | `temperature_c`, `humidity_pct` |
| `varroa_count` | `mites`, `bees_examined` |

`device_id` und `source` sind kurze technische Kennungen, keine Namen, E-Mail-Adressen oder sonstigen Personenkennungen. Die optionale Quellereignis-ID ist eine druckbare ASCII-Kennung mit maximal 128 Zeichen; `verification_status` darf ausschließlich `unverified` sein, damit ein Adapter keine Expertenbestätigung vortäuscht. Stationen, die Peilungen oder Standorte übertragen müssen, benötigen einen separaten, ausdrücklich modellierten und zugriffsbeschränkten Vertrag. Dieses Schema nimmt keine Koordinaten an.

## Datenschutz- und Betriebsgrenzen

- SQLite ist hier **nicht automatisch verschlüsselt**. Datenbank, WAL/SHM-Dateien und Backups müssen über NTFS-ACLs und Datenträgerverschlüsselung (z. B. BitLocker) geschützt werden. Unter Linux muss das Verzeichnis nur für das Dienstkonto zugänglich sein.
- Die Löschfunktion entfernt Datensätze logisch aus SQLite. Sie garantiert keine forensische Überschreibung von SSD-Blöcken, WAL-Dateien, Dateisystem-Snapshots oder Backups.
- Standard-Aufbewahrung: 90 Tage; Standard-Obergrenze: 100.000 Datensätze. Beide Werte sind konfigurierbar. Die lokale Speicherung ersetzt keine dokumentierte Lösch- und Backup-Regel.
- Der Listener nutzt HTTP, weil er ausschließlich an Loopback gebunden ist. Für Zugriff von anderen Geräten ausschließlich ein abgesichertes VPN bzw. einen TLS-Reverse-Proxy mit eigener Authentifizierung verwenden; niemals Port 8765 direkt ins Internet freigeben.
- Der lokale Token schützt den Endpunkt, ist aber kein Ersatz für TLS bei Netzwerkzugriff. Keine Tokens in Quellcode, Logs, Tickets oder Screenshots speichern.

## Tests

```powershell
python -m compileall -q integrations
python -m unittest discover -s integrations -p "test_*.py" -v
```

Es werden nur Python-Standardbibliotheken verwendet. Die Tests nutzen temporäre Datenbanken und einen Loopback-Testserver.
