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

Keep the token in a local secret manager or protected environment file. Never commit it. The service binds to `127.0.0.1:8765` and must not be directly exposed to the public internet. The default rate limit is 60 requests per client IP per 60 seconds; the rate-limit table is bounded to 1,024 client addresses. Maximum active request workers are 16 with a bounded accept queue of 32. Socket inactivity timeout is five seconds and the complete request body must arrive within ten seconds; request bodies are capped at 32 KiB. Duplicate Authorization headers, duplicate/missing/invalid Content-Length headers, transfer/content encodings and non-JSON bodies are rejected. Static serving is allowlisted; resolved symlinks must remain inside the allowed web root; Python source, hidden files and private data directories are not served.

## API

All endpoints require `Authorization: Bearer <token>`.

- `POST /api/v1/events` — validate and durably insert an event. Returns 202 once the SQLite transaction commits. Repeating the exact same canonical event is idempotent.
- `GET /api/v1/events?limit=100` — list up to 500 most recent metadata events.
- `GET /api/v1/events/export?limit=500` — download a versioned JSON export of up to 500 most recent metadata events (8 MiB response cap). The export contains station identifiers and event metadata; protect it like the source database.
- `DELETE /api/v1/events/{event_id}` — explicitly delete one event by its 64-character SHA-256 identifier.

Events are validated against `integrations/event_contracts.py`. The contract accepts only four typed event kinds and exact field allowlists. Camera metadata may include only the bridge's bounded `origin_event_id`, literal `verification_status="unverified"`, and boolean `prey_detected` extensions. Coordinates, photographs, audio, base64, arbitrary free text, unknown keys, duplicate JSON keys and model/human approval claims are rejected. ISO-8601 timestamps must include an explicit timezone; offset timestamps from the source bridge are accepted. The database uses SQLite WAL, FULL synchronous writes and secure_delete. It has a maximum-row bound and expires records older than the configured retention period on writes. When the store is full, new events fail closed with HTTP 503; existing events and their idempotency keys are not silently evicted to make room. Expired records are also purged once at startup and then by a maintenance thread (default every 3600 seconds). Configure the interval with `VESPAGUARD_RETENTION_INTERVAL_SECONDS` (300–86400 seconds). Configure backup and deletion policies appropriate to the deployment.

## Backup, verification and restore

The project provides an explicit SQLite online-backup tool. It creates a transactionally consistent snapshot while the service is running, runs SQLite integrity/schema checks, and refuses to overwrite existing files. It does not encrypt backup contents or schedule automatic backups. On Windows, it also verifies the destination directory's NTFS ACL with Windows PowerShell before writing: the owner must be the current user, current user and SYSTEM must have FullControl, and only those principals plus optional BUILTIN\\Administrators may have allow entries. Any deny entry, broad group or ACL-query failure aborts the backup. This is access-control validation, not encryption; use BitLocker or another encrypted volume.

Run from the repository root:

PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\BeeKeeper-Monitor\backups" | Out-Null
python -m integrations.store_backup backup --source "$env:LOCALAPPDATA\BeeKeeper-Monitor\events.sqlite3" --destination "$env:LOCALAPPDATA\BeeKeeper-Monitor\backups\events-2026-11-20.sqlite3"
python -m integrations.store_backup verify --source "$env:LOCALAPPDATA\BeeKeeper-Monitor\backups\events-2026-11-20.sqlite3"
# Restore only to a NEW, non-existing destination path:
python -m integrations.store_backup restore --backup "$env:LOCALAPPDATA\BeeKeeper-Monitor\backups\events-2026-11-20.sqlite3" --destination "$env:LOCALAPPDATA\BeeKeeper-Monitor\restore-test\events.sqlite3"
```

Linux/macOS:

```sh
install -d -m 700 "$HOME/.local/share/beekeeper-monitor/backups"
python -m integrations.store_backup backup \
  --source "$HOME/.local/share/beekeeper-monitor/events.sqlite3" \
  --destination "$HOME/.local/share/beekeeper-monitor/backups/events-2026-11-20.sqlite3"
python -m integrations.store_backup verify \
  --source "$HOME/.local/share/beekeeper-monitor/backups/events-2026-11-20.sqlite3"
# Restore only to a NEW, non-existing destination path:
python -m integrations.store_backup restore \
  --backup "$HOME/.local/share/beekeeper-monitor/backups/events-2026-11-20.sqlite3" \
  --destination "$HOME/.local/share/beekeeper-monitor/restore-test/events.sqlite3"
```

Never test restore over the live database. Stop the service before any manually planned cutover, verify the restored file, compare event counts, and preserve the previous database until acceptance is complete. Backups contain potentially sensitive station metadata. Store them on BitLocker/FileVault/LUKS or another approved encrypted volume. On Windows apply NTFS ACLs to the backup directory and files; the utility does not set Windows ACLs. On POSIX it requires a service-owned private directory (0700) and produces private files (0600).

The utility does not create a backup schedule, rotate old backups, encrypt archives, copy them off-device or prove a disaster-recovery RPO/RTO. Those remain deployment-level operations.

## Storage and privacy limits

- SQLite data is stored at `VESPAGUARD_INGEST_DB`; default path is `integrations/data/events.sqlite3`.
- On POSIX, use a dedicated service-owned database directory with mode 0700; the database and any SQLite WAL/SHM files are restricted to mode 0600. The service refuses to use an existing group/world-accessible directory instead of silently changing its permissions.
- On Windows, enforce NTFS ACLs for the service account and administrators before first start; this service does not modify Windows ACLs.
- This implementation does **not** provide database encryption at rest. Use BitLocker/FileVault/LUKS or an approved encrypted storage volume.
- The service has no public listener, user accounts, remote roles or central identity provider.
- Retention runs at startup and periodically in this service. A manual SQLite backup/verify/restore utility is available as `python -m integrations.store_backup`; backups are not encrypted, scheduled or rotated. Replicas, logs, browser IndexedDB and exports require separate retention/deletion handling.
- Event labels and device identifiers can still be personal or commercially sensitive information. Minimize them.
- A successful 202 means the local SQLite transaction committed; it does not establish remote replication or a legal retention basis. The response cap is 8 MiB; the PWA export cap remains 8 MiB. The local token is not a substitute for TLS over a network; the listener remains loopback-only.

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
