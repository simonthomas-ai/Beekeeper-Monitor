# Hornet3000 / BeeKeeper3000 connection

The companion adapter is maintained in [BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000/tree/main/monitor-bridge). The current reference path uses a separately runnable source journal, the cursor-aware BeeKeeper bridge and the authenticated local Monitor receiver.

## Current software data flow

1. A trusted local detector/producer submits one metadata-only candidate to the BeeKeeper source API: `POST http://127.0.0.1:8787/api/events`, authenticated with `X-API-Key`.
2. The source API validates the strict event contract and commits the event to its SQLite journal before acknowledging it.
3. The Node.js bridge reads `GET /api/events?limit=100&cursor=start` and subsequent signed-cursor pages, authenticated with the separate source API key.
4. The bridge forwards the metadata to `POST /api/v1/events`, authenticated with a different Monitor Bearer token.
5. The Monitor validates the event, stores it in local SQLite and returns HTTP 202 only after the durable insert/duplicate check.
6. The local PWA can list, export and explicitly delete stored station events.

The bridge catches up multiple pages, retries transient errors, uses idempotent event IDs and only advances its persistent cursor after a complete page has been acknowledged by the Monitor. It defaults to `BRIDGE_REQUIRE_CURSOR=true` and refuses the older latest-100-only API instead of silently accepting possible event loss.

## Important production boundary

This is a functioning **software reference path**, not yet a complete retrofit of the inherited Hornet3000 Wächter 1.6.0 product:

- The complete original C++ daemon/source archive is not present in the published BeeKeeper3000 repository.
- No camera or AI classifier is automatically wired to submit observations to the source API. A trusted producer still has to be connected and tested.
- The MeshCore signed radio receiver and its local bearing/triangulation store are separate from the HTTP source journal. They are not automatically bridged into the Monitor event list.
- No actual camera, radio hardware, LoRa coverage, multi-station field triangulation or nationwide deployment has been tested.
- The application does not declare GDPR compliance. Apply the privacy, retention and operator procedures appropriate to the actual deployment.

The accepted event schema is deliberately metadata-only. It does not transfer photos, audio, file paths, precise GPS, camera credentials or untrusted expert-verification claims. MeshCore station coordinates remain receiver-local; the MeshCore store can calculate a local search hypothesis from at least three compatible bearing stations, but that result is not yet synced to the Monitor. A signature authenticates a key, not a biological species identification.

## 1. Start the local Monitor receiver

From the Beekeeper-Monitor repository root, provision a dedicated token and a private data directory. Keep the token out of source control and service logs.

Linux/macOS:

```sh
export VESPAGUARD_INGEST_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export VESPAGUARD_INGEST_DB="$HOME/.local/share/beekeeper-monitor/events.sqlite3"
mkdir -p "$HOME/.local/share/beekeeper-monitor"
chmod 700 "$HOME/.local/share/beekeeper-monitor"
python -m integrations.local_ingest
```

Windows PowerShell (run in a persistent service environment, not only a temporary shell):

```powershell
$env:VESPAGUARD_INGEST_TOKEN = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$env:VESPAGUARD_INGEST_DB = "$env:LOCALAPPDATA\BeeKeeper-Monitor\events.sqlite3"
New-Item -ItemType Directory -Force (Split-Path $env:VESPAGUARD_INGEST_DB) | Out-Null
python -m integrations.local_ingest
```

The receiver binds to `127.0.0.1:8765`. Open `http://127.0.0.1:8765/` in the same machine's browser to use the local PWA and authenticated station-event panel. The token is entered per session and is not saved in browser storage. Set restrictive NTFS ACLs for the service account and use BitLocker or an encrypted volume; SQLite is not application-encrypted.

## 2. Start the BeeKeeper source journal

From the BeeKeeper3000 repository root, generate two independent random secrets. The API key authenticates producer and bridge requests; the cursor secret signs pagination state. Do not reuse the Monitor token.

Linux/macOS:

```sh
export HORNET3000_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export HORNET3000_CURSOR_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export HORNET3000_EVENT_DB="$HOME/.local/share/beekeeper3000/source-events.sqlite3"
mkdir -p "$HOME/.local/share/beekeeper3000"
chmod 700 "$HOME/.local/share/beekeeper3000"
python -m network.source_api
```

Windows PowerShell:

```powershell
$env:HORNET3000_API_KEY = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$env:HORNET3000_CURSOR_SECRET = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$env:HORNET3000_EVENT_DB = "$env:LOCALAPPDATA\BeeKeeper3000\source-events.sqlite3"
New-Item -ItemType Directory -Force (Split-Path $env:HORNET3000_EVENT_DB) | Out-Null
python -m network.source_api
```

The source service binds only to `127.0.0.1:8787`. It uses the Python standard library and a local SQLite database. Configure private filesystem permissions and full-disk encryption. Do not expose the plain-HTTP service publicly.

A producer must POST strict JSON metadata containing exactly `id`, `observed_at` (timezone-aware ISO-8601), `station_id`, `species`, `confidence` (0..1) and `prey_detected` to `/api/events` with `X-API-Key`. The API rejects media, GPS, paths, secrets and human-verification claims. An exact duplicate is acknowledged idempotently; reusing an ID with changed content is rejected.

## 3. Configure and start the bridge

Use `monitor-bridge/.env.example` as the variable template in BeeKeeper3000. Set:

- `HORNET3000_URL=http://127.0.0.1:8787`
- `HORNET3000_API_KEY` to the source API key
- `BEEKEEPER_MONITOR_INGEST_URL=http://127.0.0.1:8765/api/v1/events`
- `BEEKEEPER_MONITOR_INGEST_TOKEN` to the Monitor token
- `BRIDGE_REQUIRE_CURSOR=true`
- `BRIDGE_STATE_FILE` to a private, persistent local path

With Node.js 20 or newer, start it from the BeeKeeper3000 repository root:

```sh
npm --prefix monitor-bridge start
```

Do not run it with cursor mode disabled in production. Legacy mode exists only as an explicitly accepted local demonstration fallback and can lose older events.

## Security and privacy boundary

- Use a unique source API key, cursor secret and Monitor Bearer token for every installation.
- Keep both Python services on loopback. Remote federation requires a separately reviewed authenticated VPN/TLS gateway; do not expose plain HTTP.
- Source API and Monitor receiver enforce request size, time, worker, rate and storage bounds.
- SQLite data, backups and exports contain sensitive station metadata. Use encrypted storage and restrict service-account access.
- Browser IndexedDB and server-side SQLite are different stores with separate deletion/export behavior.
- Define and test retention/deletion for source journals, bridge state, Monitor DB, browser storage, backups and external proxy logs.
- Do not publish exact nest coordinates or station locations in public dashboards by default.

## Verification and acceptance

Automated tests cover source API cursor pagination/restart/retention, bridge retries/checkpointing, strict metadata validation, Monitor storage and PWA/browser behavior. These checks do not replace a live source-producer-to-bridge-to-Monitor test on the actual station.

Before deployment, connect the real local producer, verify event appearance after source and bridge restart, simulate Monitor outage/backlog recovery, check retention-expiry handling, and test the configured radio/hardware. The current MeshCore receiver/store separately supports local bearing collection and triangulation; a three-station field-validated nest search and forwarding of the derived search hypothesis into Monitor remain open tasks.
