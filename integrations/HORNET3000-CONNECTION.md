# Hornet3000 / BEEKEEPER3000 connection

This monitor already contains a small authenticated local ingestion endpoint in `integrations/local_ingest.py`. The companion adapter is maintained in [simonthomas-ai/BeeKeeper3000](https://github.com/simonthomas-ai/BeeKeeper3000/tree/main/monitor-bridge).

## What is connected

- Source: Hornet3000 Wächter `GET /api/events?limit=100`, authenticated by `X-API-Key`.
- Adapter: Node.js 20+ service in the BEEKEEPER3000 repository.
- Receiver: this repository's `POST /api/v1/events`, authenticated by a separate Bearer token.
- Data sent: event ID, timestamp, station/device ID, unverified species candidate, confidence, source status and prey flag.
- Explicitly excluded: image files, audio, GPS coordinates, camera credentials and source API keys.

Species labels arrive prefixed with `unverified_candidate:`; do not treat model output as verified species identity.

## Start the receiver locally

From the Beekeeper-Monitor checkout, use a dedicated random token (at least 24 characters):

```bash
export VESPAGUARD_INGEST_TOKEN='GENERATE_A_UNIQUE_RANDOM_SECRET'
python -m integrations.local_ingest
```

It listens on `127.0.0.1:8765`. It validates and logs event metadata; it does not currently write events into the PWA IndexedDB or render them in the browser dashboard.

## Start the adapter

Configure the variables in `monitor-bridge/.env.example` in the BEEKEEPER3000 checkout:

- `HORNET3000_URL` — default `http://127.0.0.1:8787`
- `HORNET3000_API_KEY` — existing Hornet3000 API key
- `BEEKEEPER_MONITOR_INGEST_URL` — default `http://127.0.0.1:8765/api/v1/events`
- `BEEKEEPER_MONITOR_INGEST_TOKEN` — same dedicated receiver token
- `POLL_INTERVAL_MS` — default 10000

Then run `npm test` and `npm start` in `monitor-bridge/`.

## Deployment boundary

This documents a compatible local metadata transport. A successful end-to-end installation still requires both services running on the same host/private network, correct local secrets, and a live acceptance test. For remote hosts use HTTPS plus a private VPN/reverse proxy. Never expose either plain HTTP listener to the public internet.

The monitor's PWA currently has no server-event persistence/display route. That must be implemented and tested separately before describing detections as visible in the monitor dashboard.
