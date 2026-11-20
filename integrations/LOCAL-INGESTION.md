# Local event ingestion and storage

This service accepts **validated metadata only** from trusted local components. It does not accept or store photographs, audio, video, model files, GPS coordinates, API keys or arbitrary attachments.

## Run locally

Requirements: Python 3.12 or newer. The receiver uses only the Python standard library.

PowerShell:

```powershell
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$secretBytes = New-Object byte[] 32
$rng.GetBytes($secretBytes)
$rng.Dispose()
$env:VESPAGUARD_INGEST_TOKEN = [Convert]::ToBase64String($secretBytes)
$env:VESPAGUARD_INGEST_DB = "$env:LOCALAPPDATA\BeeKeeper-Monitor\events.sqlite3"
$env:VESPAGUARD_RETENTION_DAYS = "90"
$env:VESPAGUARD_MAX_EVENTS = "100000"
$env:VESPAGUARD_RETENTION_INTERVAL_SECONDS = "3600"
python -m integrations.local_ingest
```

Linux/macOS:

```sh
export VESPAGUARD_INGEST_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export VESPAGUARD_INGEST_DB="$HOME/.local/share/beekeeper-monitor/events.sqlite3"
export VESPAGUARD_RETENTION_DAYS=90
export VESPAGUARD_MAX_EVENTS=100000
export VESPAGUARD_RETENTION_INTERVAL_SECONDS=3600
python -m integrations.local_ingest
```

Then open `http://127.0.0.1:8765/` in the same browser. This local endpoint serves the static PWA and its authenticated station-event panel on the same origin as the API. The panel asks for the token each time; it is kept only in JavaScript memory and cleared on page exit. After connecting, the panel can download a versioned JSON export of up to 500 server-side station events or delete individual entries after confirmation. The public GitHub Pages copy does not connect to the local receiver.

Keep the token in a local secret manager or protected environment file. Never commit it. The service binds to `127.0.0.1:8765` and must not be directly exposed to the public internet. The default rate limit is 60 requests per client IP per 60 seconds; maximum active request workers are 16 and request body size is capped at 32 KiB. Static serving is allowlisted; Python source, hidden files and private data directories are not served.

## API

All endpoints require `Authorization: Bearer <token>`.

- `POST /api/v1/events` — validate and durably insert an event. Returns 202 once the SQLite transaction commits. Repeating the exact same canonical event is idempotent.
- `GET /api/v1/events?limit=100` — list up to 500 most recent metadata events.
- `GET /api/v1/events/export?limit=500` — download a versioned JSON export of up to 500 most recent metadata events (8 MiB response cap). The export contains station identifiers and event metadata; protect it like the source database.
- `DELETE /api/v1/events/{event_id}` — explicitly delete one event by its 64-character SHA-256 identifier.

Events are validated against `integrations/event_contracts.py`. The database has a maximum-row bound and expires records older than the configured retention period on writes. Expired records are also purged once at startup and then by a maintenance thread (default every 3600 seconds). Configure the interval with `VESPAGUARD_RETENTION_INTERVAL_SECONDS` (300–86400 seconds). Configure backup and deletion policies appropriate to the deployment.

## Storage and privacy limits

- SQLite data is stored at `VESPAGUARD_INGEST_DB`; default path is `integrations/data/events.sqlite3`.
- On POSIX, use a dedicated service-owned database directory with mode 0700; the database and any SQLite WAL/SHM files are restricted to mode 0600. The service refuses to use an existing group/world-accessible directory instead of silently changing its permissions.
- On Windows, enforce NTFS ACLs for the service account and administrators before first start; this service does not modify Windows ACLs.
- This implementation does **not** provide database encryption at rest. Use BitLocker/FileVault/LUKS or an approved encrypted storage volume.
- The service has no public listener, user accounts, remote roles or central identity provider.
- Retention runs at startup and periodically in this service. Backups, replicas, logs, browser IndexedDB and exports require separate retention/deletion handling; automatic encrypted backup/restore is not implemented.
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
