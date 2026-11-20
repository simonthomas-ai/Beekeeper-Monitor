# Local event ingestion and storage

This service serves the local station PWA and accepts **validated metadata only** from trusted local components. It does not accept or store photographs, audio, video, model files, GPS coordinates, API keys or arbitrary attachments. Camera events may additionally carry only a bounded source event ID, the literal `verification_status="unverified"`, and a boolean `prey_detected` flag.

## Run locally

Requirements: Python 3.12 or newer. The receiver uses only the Python standard library.

PowerShell:

```powershell
$env:VESPAGUARD_INGEST_TOKEN = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 } | ForEach-Object { [byte]$_ }))
$env:VESPAGUARD_INGEST_DB = "$env:LOCALAPPDATA\BeeKeeper-Monitor\events.sqlite3"
$env:VESPAGUARD_RETENTION_DAYS = "90"
$env:VESPAGUARD_MAX_EVENTS = "100000"
python -m integrations.local_ingest
```

Linux/macOS:

```sh
export VESPAGUARD_INGEST_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export VESPAGUARD_INGEST_DB="$HOME/.local/share/beekeeper-monitor/events.sqlite3"
export VESPAGUARD_RETENTION_DAYS=90
export VESPAGUARD_MAX_EVENTS=100000
python -m integrations.local_ingest
```

Then open `http://127.0.0.1:8765/` in the same browser. This local endpoint serves the static PWA and its authenticated station-event panel on the same origin as the API. The panel asks for the token each time; it is kept only in JavaScript memory and cleared on page exit. The public GitHub Pages copy does not connect to the local receiver.

Keep the token in a local secret manager or protected environment file. Never commit it. The service binds to `127.0.0.1:8765` and must not be directly exposed to the public internet. The default rate limit is 60 requests per client IP per 60 seconds; maximum active request workers are 16, the accept queue is bounded, socket reads time out after five seconds, request bodies have a ten-second total deadline, and the request body size is capped at 32 KiB. Per-IP state for the 60/60-second rate limit is itself bounded. Static serving is allowlisted; Python source, hidden files and private data directories are not served.

## API

All endpoints require `Authorization: Bearer <token>`.

- `POST /api/v1/events` — validate and durably insert an event. Returns 202 once the SQLite transaction commits. Repeating the exact same canonical event is idempotent.
- `GET /api/v1/events?limit=100` — list up to 500 most recent metadata events and return both `events` and `count`.
- `DELETE /api/v1/events/{event_id}` — explicitly delete one event by its 64-character SHA-256 identifier.

Events are validated against `integrations/event_contracts.py`. Only the required fields for each event type and the three documented camera metadata extensions are accepted. The receiver rejects unknown fields, coordinates, media, duplicate JSON keys, non-finite numbers and any verification status other than `unverified`. A source adapter cannot assert expert confirmation. The database has a maximum-row bound and expires records older than the configured retention period on writes. Configure backup and deletion policies appropriate to the deployment.

## Storage and privacy limits

- SQLite data is stored at `VESPAGUARD_INGEST_DB`; default path is `integrations/data/events.sqlite3`.
- On POSIX, the database is chmod'd to 0600. On Windows, enforce NTFS ACLs for the service account and administrators.
- This implementation does **not** provide database encryption at rest. Use BitLocker/FileVault/LUKS or an approved encrypted storage volume.
- The service has no public listener, user accounts, remote roles or central identity provider.
- Retention is local to this service. Backups, replicas, logs, browser IndexedDB and exports require separate retention/deletion handling.
- Event labels and device identifiers can still be personal or commercially sensitive information. Minimize them.
- A successful 202 means the local SQLite transaction committed; it does not establish remote replication or a legal retention basis.

## Verification

Run:

```sh
python -m unittest discover -s integrations -p 'test_*.py' -v
```

Run the companion bridge tests from the BeeKeeper3000 repository:

```sh
cd monitor-bridge
npm test
```

## Operational readiness

Before connecting real devices: generate unique random tokens, restrict filesystem access, enable full-disk encryption, test backups and restore, agree on a retention period, document data-controller roles and legal basis, and perform a deployment-specific security/privacy review. No GDPR compliance claim is made by this implementation.
