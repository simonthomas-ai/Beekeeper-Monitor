# Data lifecycle, privacy boundaries and deployment checklist

Status: engineering documentation, not legal advice or a GDPR compliance certificate.
This document describes the current source tree as reviewed on 2026-11-20.
Every deployment owner must confirm the actual configuration, network topology,
browser behaviour, retention settings and applicable legal basis before a pilot.

## 1. Two distinct PWA modes

### Public static PWA (GitHub Pages)

The public site is a manual observation journal. It is not connected to a
station's localhost SQLite receiver and does not read the operator's local
station database. The application explicitly disables station-token entry when
opened from the public GitHub Pages origin.

Manual observations are stored in the browser's IndexedDB database
`beekeeper-monitor-v2`, object store `observations`. A record may contain:

- Observation type, timestamp and free-text note (up to 2,000 characters).
- An optional selected image stored as a data URL (up to 8 MB per source image).
- An optional one-time GPS coordinate and reported accuracy, only after the
  operator checks the location option and grants browser permission.

The application code does not send these records to a BeeKeeper server. The
JSON export contains all stored observations, including image data and location
when present. Browser storage is not encrypted by this application. Deleting a
record in the UI removes it from this browser database; clearing site data or
losing the browser profile can also remove it. Users should protect the device
account and exported backup files with operating-system encryption and access
controls.

The service worker caches only the static application shell. It does not add
the IndexedDB observation records to its application cache. The candidate photo
review galleries load externally hosted source images; a user's browser makes
those image requests to the respective source host. The source host's own
network logging and content licence terms are outside this application's
control. Review marks remain in the browser until exported.

The camera/microphone page is a user-started preview and microphone-level test.
It does not continuously record media. In the explicit camera shadow test, one
user-selected frame is converted to a bounded JPEG and staged in the existing
manual observation form; it is written to IndexedDB only when the user saves
that observation. The entry is labelled `Kamera-Shadow-Test (nicht bestimmt)`.
The PWA does not upload that frame to BeeKeeper3000 or the Monitor receiver.
Frames may still contain personal or sensitive content, so avoid people,
private areas and unnecessary location data, and protect/export/delete them as
described above. The active camera/microphone streams stop on page exit.

The separate manual field-classification workflow stores selected JPEG, PNG or
WebP image bytes and MIME types in `beekeeper-field-dataset-v1`, object store `images`. It stores the chosen seven-class
image labels, an app-addition timestamp, a random tab-session ID, optional pseudonymous
labeler ID, and the entered source/rights review. A separate pseudonymous
`reviewed_by` ID and `reviewed_at` timestamp are recorded only when the user
manually approves the image/labels and attests training use. The timestamp is
read from the local browser clock; it is not signed or independently trusted. It does not read GPS or transmit
images or labels. Records remain on-device until the user explicitly exports a ZIP.
The ZIP is available only after the user separately attests to image/label review
and training-use permission for every record and confirms awareness that original
images may contain EXIF metadata such as GPS, capture time and camera/device
identifiers. The application does not inspect or strip EXIF metadata; image bytes
remain unchanged for provenance checks. This status records the operator's
attestation and is not an independent verification or proof of image rights. The export contains image bytes and
`annotations.jsonl`; it is sensitive data and is outside the PWA's storage controls
after download. Deleting a record removes it from this field-capture database, but
does not remove an existing export or copies made elsewhere.

### Local station PWA and Monitor receiver

The local PWA is served at `http://127.0.0.1:8765/` by
`integrations/local_ingest.py`. It accepts station events only through an
authenticated bearer token over same-origin requests. The browser integration
keeps the entered token in JavaScript memory, clears the field after entry and
clears the active token on page exit or an authentication failure.

The local event store uses SQLite and accepts a strict metadata-only event
contract. It does not accept images, audio, GPS coordinates, arbitrary free
text, passwords or private keys. Event candidates remain explicitly
`unverified`; a model confidence score is not an expert species confirmation.
The local API exposes authenticated list, export and delete operations.
Export is capped at 500 events and 8 MiB. Delete targets one event ID and
requires the same bearer authentication.

Default Monitor store settings are 90 days retention and 100,000 rows;
the service runs expiry maintenance hourly. The active station configuration
may override those settings. Confirm the deployed `VESPAGUARD_RETENTION_DAYS`,
`VESPAGUARD_MAX_EVENTS` and maintenance interval before field use.

## 2. BeeKeeper source, bridge and camera outbox

The Linux base installer currently configures the source event journal for
30-day retention and 250,000 rows. It also configures the Monitor event store
for 90 days and 100,000 rows. These are deployment defaults, not universal
values for every manual installation. Source API, Monitor receiver and bridge
are intended for loopback use by default; remote access requires a private VPN
and a separately reviewed TLS reverse proxy.

The optional camera outbox stores a bounded set of metadata events and
persistent duplicate-suppression timestamps in SQLite. It does not accept
media or coordinates. Pending events remain until durably acknowledged by the
Monitor receiver. The default outbox capacity is 10,000 rows; a full outbox
stops the camera runtime visibly rather than silently deleting pending events.
Acknowledged events are removed from the pending queue; cooldown state remains
until its species/prey key is updated. Include this database in station backups.

The Node bridge transfers only event metadata and omits media and exact GPS
coordinates. The MeshCore radio packet uses signed compact metadata and a
station hash; the receiving station resolves coordinates through its local
station registry. Do not place precise apiary or nest coordinates in public
records or radio packets.

## 3. Backups and deletion

The Windows station backup runner snapshots the source, Monitor and optional
camera databases, copies the bridge checkpoint when present, and creates a
SHA-256 manifest. DPAPI secrets are deliberately excluded. A backup therefore
contains sensitive station metadata and must be stored on encrypted media with
restricted NTFS ACLs. The backup's manifest detects accidental corruption; it
does not encrypt the backup or prove that a second physical device can restore
it. A device-level restore rehearsal is required before a pilot.

The Monitor supports authenticated per-event deletion and time-based retention.
The BeeKeeper3000 source journal now provides an authenticated per-event
deletion endpoint (`DELETE /api/events?id=<event-id>`) with a bounded
tombstone that blocks delayed replay during the configured source retention
horizon. This removes the event from the source SQLite journal only. It does
**not** automatically delete a Monitor copy, an event already fetched by an
in-flight bridge page, an export/backup, or a previously transmitted radio
packet. Conversely, deleting a Monitor event does not remove the source
journal copy.

Before collecting personal or sensitive observations, define an operator
procedure across both systems: identify the stable event ID, delete from the
source API, delete the corresponding Monitor event using the authenticated
Monitor endpoint, allow in-flight bridge requests to settle and verify the
event does not reappear, then account for existing exports/backups under the
approved backup-retention/destruction policy. A radio packet already sent
cannot be recalled; the tombstone only prevents a delayed source API replay
within its retention horizon. The source deletion ledger is bounded and fails
closed if its configured capacity is reached. Retention and deletion must
therefore be governed across every copy, not only one database.

## 4. Data classification and handling

| Data | Current handling | Deployment requirement |
|---|---|---|
| Insect candidate label, confidence, time, station ID | Local metadata event; unverified until reviewed | Restrict access; retain only as long as operationally justified |
| Manual notes | Browser IndexedDB; free text | Do not enter names, health details, passwords or unnecessary personal data |
| Photo | Optional browser-local data URL; JSON export includes it | Protect device and exports; check image rights and remove EXIF/location metadata before any authorized reuse |
| Exact GPS | Optional browser observation only; prohibited from station event contract and MeshCore packet | Keep private; never publish exact apiary/nest coordinates without an explicit reviewed need |
| Station ID / radio station hash | Technical identifier | Pseudonymise public identifiers and protect the local coordinate registry |
| API tokens / signing keys | Environment/config files; excluded from backups | OS ACLs, rotation, separate credentials, no logs/repository commits |
| Backup/checkpoint | Local protected directory; metadata-bearing | Encrypt media, access-control, retention and restore tests |

## 5. Pilot governance gate

Before a closed pilot, document and approve:

1. Who determines purpose and means for each station, PWA dataset and shared
   network; who acts as processor or independent controller; and who can access
   each database, map layer, export and backup.
2. The applicable legal basis, notices, purpose limitation, minimisation,
   retention, data-subject rights and incident procedure for the actual use case.
3. Whether a data-protection impact assessment is necessary, especially where
   precise locations, household/workplace cameras or identifiable people may be
   captured. Keep image capture outside the current metadata-only event path.
4. A deletion process covering browser copies, source journal, Monitor store,
   radio propagation, exports and backup expiry. State which copies cannot be
   selectively recalled once distributed.
5. Device encryption, account isolation, offline update, key rotation, recovery
   objectives, and verified restoration on the actual Windows/Raspberry Pi
   station hardware.
6. Exact retention values and resource limits for each deployed service, with
   monitoring and operator-visible warnings before capacity is reached.

No GDPR certification or legal compliance determination is claimed by this
repository. The defaults and controls above reduce exposure but do not replace
a deployment-specific assessment by the responsible organisation.
