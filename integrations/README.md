# Local Station Integration

The local receiver serves the station PWA and accepts validated metadata from local integrations. It is intentionally separate from the public GitHub Pages deployment.

## Data boundary

Accepted event kinds are `camera_detection`, `manual_observation`, `acoustic_event`, `hive_telemetry`, and `varroa_count`. Every kind has a strict payload allowlist. The BeeKeeper3000 camera bridge may send a bounded source event ID, `verification_status="unverified"`, and a boolean prey flag. The mobile PWA uses `manual_observation` with `verification_status="observer_report"`; its confidence is an observer estimate, not model confidence or expert confirmation. Manual observations are excluded from the automatic hornet-alert rule. Arbitrary fields, GPS coordinates, images, audio, base64 content and free-form personal information are rejected.

A bridge event remains an unverified candidate. It cannot claim that an expert confirmed a species, approved training data or verified a license. Station identifiers and source labels must be technical identifiers, not names or contact details.

## Start the local receiver (PowerShell)

Run from the repository root:

```powershell
$secretBytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($secretBytes)
$rng.Dispose()
$env:VESPAGUARD_INGEST_TOKEN = [Convert]::ToBase64String($secretBytes)
$env:VESPAGUARD_INGEST_DB = "$env:LOCALAPPDATA\BeeKeeper-Monitor\events.sqlite3"
$env:VESPAGUARD_RETENTION_DAYS = "90"
$env:VESPAGUARD_MAX_EVENTS = "100000"
python -m integrations.local_ingest
```

Open `http://127.0.0.1:8765/`. The token is required for the station event panel, API and export. Do not store it in the repository, browser local storage, screenshots or logs.

The server is loopback-only. Remote stations must use a reviewed TLS VPN/reverse-proxy deployment; never forward port 8765 directly from the internet. On Windows, apply restrictive NTFS ACLs to the service account, database directory and backup directory, and enable BitLocker or another approved encrypted volume.

## API

All event API endpoints require `Authorization: Bearer <token>`.

| Method | Path | Behaviour |
| --- | --- | --- |
| POST | `/api/v1/events` | Validate and persist one metadata event; HTTP 202 only after SQLite commit |
| GET | `/api/v1/events?limit=100` | Read 1–500 latest records; response includes `events` and `count` |
| GET | `/api/v1/events/export?limit=500` | Authenticated versioned JSON export, up to 500 records and 8 MiB |
| DELETE | `/api/v1/events/{sha256}` | Delete a single event by its 64-character lowercase SHA-256 ID |

The POST request is limited to 32 KiB, has a five-second socket inactivity timeout and a ten-second total body deadline. The server caps active workers and queue length, applies per-IP rate limits with bounded in-memory state, rejects ambiguous Authorization/Content-Length headers and blocks unsupported transfer/content encodings. API responses are capped at 8 MiB.

SQLite uses WAL, full synchronous writes, secure_delete, private POSIX file modes and a bounded record count. Delivery is idempotent: an identical canonical event has the same SHA-256 ID. At capacity, the receiver rejects new events with HTTP 503 rather than silently evicting live records or accepting data it cannot preserve.

## Backup and restore

Use the existing backup utility:

```powershell
python -m integrations.store_backup backup --source "$env:LOCALAPPDATA\BeeKeeper-Monitor\events.sqlite3" --destination "$env:LOCALAPPDATA\BeeKeeper-Monitor\backups\events-backup.sqlite3"
python -m integrations.store_backup verify --source "$env:LOCALAPPDATA\BeeKeeper-Monitor\backups\events-backup.sqlite3"
python -m integrations.store_backup restore --backup "$env:LOCALAPPDATA\BeeKeeper-Monitor\backups\events-backup.sqlite3" --destination "$env:LOCALAPPDATA\BeeKeeper-Monitor\restore-test\events.sqlite3"
```

Backup and restore targets must be new files. The utility does not encrypt or schedule backups. Protect them using an encrypted volume and restrictive access controls. Test restores to a new location; never restore over a live database.

## Tests

```powershell
python -m compileall -q integrations
python -m unittest discover -s integrations -p "test_*.py" -v
```

GitHub Actions runs the integration, storage and backup suite on pull requests using Python 3.12 and 3.13.

## Operational limits

- SQLite and exports are not application-layer encrypted.
- Logical deletion is not forensic erasure of SSD blocks, WAL remnants, snapshots or backups.
- Retention is local to this database; browser IndexedDB, exports, backups, replicas and logs need separate policies.
- No legal compliance or GDPR compliance claim is made.
- No real camera, iPhone browser, LoRa/MeshCore radio or field trial is implied by passing unit tests.

## Externe Kameraerkennung (experimenteller Adapter)

`integrations/external_detector_adapter.py` bildet die Metadaten eines **bereits separat geprueften** Fremddetektors auf den bestehenden `HiveEvent`-Vertrag ab. Es werden keine Fremdmodelle, Trainingsbilder, Bilddaten, Audiodaten oder GPS-Koordinaten eingebunden. Die Funktion startet keinen Server und sendet keine Ereignisse von selbst.

Eingabevertrag: genau `taxon`, `confidence` (Zahl von 0 bis 1), `timestamp` (ISO-8601 mit Zeitzone), `event_id` (kurze technische Kennung). Die Artbezeichnungen muessen zuvor explizit auf die sieben bekannten Klassen abgebildet werden. Jede Erkennung bleibt `verification_status=unverified`. Unbekannte Felder und Arten werden verworfen.

Beispiel fuer **Struktur und API, nicht fuer eine echte Messung**:

```python
from integrations.external_detector_adapter import adapt_detection
record = {"taxon": "vespa_velutina", "confidence": 0.8,
          "timestamp": "2026-11-21T17:00:00Z", "event_id": "example-001"}
event = adapt_detection(record, device_id="station_01", source="external_camera")
print(event.to_json())
```

Ein realer Adapter muss vor der Verwendung fuer vespCV/VespAI/Waspinator deren konkrete Ausgabe, Labels, Lizenzbedingungen und Modellversion nachweislich pruefen. Die bestehende authentifizierte Bridge bleibt der einzige vorgesehene Transportweg. Tests: `python -m unittest integrations.test_external_detector_adapter -v`.
