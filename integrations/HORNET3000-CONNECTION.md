# Hornet3000 / BeeKeeper3000 connection

The companion adapter is maintained in [simonthomas-ai/BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000/tree/main/monitor-bridge). The Monitor receiver accepts validated metadata over a dedicated local Bearer token.

## Data flow

1. Hornet3000 serves `GET /api/events?limit=100`, authenticated with its own `X-API-Key`.
2. The BeeKeeper3000 Node.js bridge reads source events and forwards metadata only.
3. The Monitor receiver accepts `POST /api/v1/events` with a separate ingestion token.
4. The receiver validates the strict event contract and commits the event to local SQLite before returning HTTP 202.
5. The local API can list events and explicitly delete one event by its SHA-256 ID.

Transferred fields include device/station ID, observation timestamp, unverified candidate label, confidence, source status and prey flag. Image, audio, GPS coordinates, camera credentials and source API keys are excluded. Species labels are marked `unverified_candidate:`; model output is not expert verification.

## Receiver setup

See [LOCAL-INGESTION.md](./LOCAL-INGESTION.md) for requirements, secure token generation, database location, retention, local API routes and limitations.

Start from the Monitor repository root:

```sh
export VESPAGUARD_INGEST_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export VESPAGUARD_INGEST_DB="$HOME/.local/share/beekeeper-monitor/events.sqlite3"
python -m integrations.local_ingest
```

The default bind address is `127.0.0.1:8765`. Open `http://127.0.0.1:8765/` in the same browser to use the local PWA and its authenticated station-event panel. The token is entered per session and is not persisted. Do not expose the plain-HTTP listener to the public internet.

## Bridge setup

Configure `monitor-bridge/.env.example` in BeeKeeper3000:

- `HORNET3000_URL` — default `http://127.0.0.1:8787`
- `HORNET3000_API_KEY` — distinct Hornet3000 API key
- `BEEKEEPER_MONITOR_INGEST_URL` — default `http://127.0.0.1:8765/api/v1/events`
- `BEEKEEPER_MONITOR_INGEST_TOKEN` — the receiver token above
- `POLL_INTERVAL_MS` — default 10000

The bridge currently polls the most recent 100 source events and persists a bounded set of forwarded IDs. This does **not** guarantee lossless catch-up if more than 100 events arrive between polls; the source API needs a cursor/sequence contract before the bridge can guarantee complete delivery. Track this in [BeeKeeper3000 issue #7](https://github.com/simonthomas-ai/BeeKeeper3000/issues/7).

## Security and privacy boundary

- Generate a unique token for every installation. Never reuse the Hornet3000 API key.
- Keep the receiver bound to loopback. Remote deployment requires an authenticated VPN and a reviewed HTTPS reverse proxy.
- The receiver has bounded request workers, socket timeouts, size/content-type checks and an in-memory per-IP rate limit.
- SQLite event rows contain metadata only. POSIX permissions are restricted to owner read/write; configure NTFS ACLs on Windows.
- Database encryption at rest is not implemented. Use full-disk or encrypted-volume protection.
- The PWA has a local station-event panel that reads and deletes server-side metadata events through the same-origin localhost API. Browser IndexedDB and server-side SQLite remain separate stores.
- Retention of exports, backups, reverse-proxy logs and source-side events requires a separate policy.
- This design does not establish GDPR compliance.

## Acceptance boundary

The receiver tests cover valid transport, authentication failures, input validation, durable storage, duplicate insertion, authenticated retrieval/deletion, local PWA serving and denial of private source paths. A live installation with the actual Hornet3000 API and hardware is still required. The source API polling limit, bridge lossless catch-up, backup/restore, encrypted storage and deployment-specific privacy review remain release gates.
