'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const contract = require('../backup-contract.js');

function observation(overrides = {}) {
  return {
    id: 'observation-1',
    at: '2026-11-21T08:00:00.000Z',
    type: 'Asiatische Hornisse',
    note: 'Sichtung am Bienenstand',
    ...overrides
  };
}
function photo(type = 'image/jpeg') {
  return {
    name: 'beobachtung.jpg',
    type,
    content: `data:${type};base64,aGVsbG8=`
  };
}
function backupText(observations) {
  return JSON.stringify({
    format: 'beekeeper-monitor-v2',
    exportedAt: '2026-11-21T08:01:00.000Z',
    observations
  });
}

test('accepts a valid export and preserves observation records', () => {
  const rows = [
    observation(),
    observation({ id: 'observation-2', type: 'Pollen' }),
    observation({ id: 'observation-3', type: 'Kamera-Shadow-Test (nicht bestimmt)' })
  ];
  assert.deepEqual(contract.parseBackupText(backupText(rows)), rows);
});

test('accepts iPhone and modern browser image MIME types consistently', () => {
  for (const mime of ['image/heic', 'image/heif', 'image/avif', 'image/jpeg', 'image/png', 'image/webp']) {
    const row = observation({ photo: photo(mime) });
    assert.equal(contract.validObservation(row), true, mime);
    assert.equal(contract.parseBackupText(backupText([row])).length, 1, mime);
  }
});

test('rejects active SVG content and mismatched image MIME metadata', () => {
  assert.equal(contract.validObservation(observation({ photo: photo('image/svg+xml') })), false);
  assert.equal(contract.validObservation(observation({
    photo: { ...photo('image/jpeg'), content: 'data:image/png;base64,aGVsbG8=' }
  })), false);
});

test('rejects malformed base64 image data and unsupported image types', () => {
  assert.equal(contract.validObservation(observation({
    photo: { ...photo(), content: 'data:image/jpeg;base64,not base64!' }
  })), false);
  assert.equal(contract.isSupportedImageType('image/svg+xml'), false);
  assert.equal(contract.isSupportedImageType('image/heic'), true);
});

test('enforces the exact 8 MiB decoded image limit on restore', () => {
  const prefix = 'data:image/jpeg;base64,';
  const maxEncoded = Math.ceil(contract.MAX_PHOTO_BYTES / 3) * 4;
  const exactLimit = observation({
    photo: { name: 'max.jpg', type: 'image/jpeg', content: prefix + 'A'.repeat(maxEncoded - 1) + '=' }
  });
  const oneByteOver = observation({
    photo: { name: 'too-large.jpg', type: 'image/jpeg', content: prefix + 'A'.repeat(maxEncoded) }
  });
  assert.equal(contract.validObservation(exactLimit), true);
  assert.equal(contract.validObservation(oneByteOver), false);
});

test('rejects duplicate IDs instead of silently overwriting backup rows', () => {
  assert.throws(
    () => contract.parseBackupText(backupText([observation(), observation()])),
    /doppelte Beobachtungs-IDs/
  );
});

test('rejects invalid class, empty note, oversized note and invalid coordinates', () => {
  assert.equal(contract.validObservation(observation({ type: 'unbekannt' })), false);
  assert.equal(contract.validObservation(observation({ note: '   ' })), false);
  assert.equal(contract.validObservation(observation({ note: 'x'.repeat(2001) })), false);
  assert.equal(contract.validObservation(observation({
    location: { latitude: 91, longitude: 10, accuracyMeters: 5 }
  })), false);
  assert.equal(contract.validObservation(observation({
    location: { latitude: 51, longitude: 7, accuracyMeters: 0 }
  })), true);
});

test('rejects malformed and oversized backups before importing', () => {
  assert.throws(() => contract.parseBackupText('{broken'), /gültiges JSON/);
  assert.throws(() => contract.parseBackupText(backupText([]).replace('beekeeper-monitor-v2', 'other')), /Sicherungsformat/);
  assert.throws(() => contract.parseBackupText(' '.repeat(contract.MAX_BACKUP_BYTES + 1)), /30 MB/);
});

test('rejects too many observations and invalid backup entries', () => {
  const rows = Array.from({ length: contract.MAX_OBSERVATIONS + 1 }, (_, i) => observation({ id: `item-${i}` }));
  assert.throws(() => contract.parseBackupText(backupText(rows)), /zu viele Beobachtungen/);
  assert.throws(() => contract.parseBackupText(backupText([null])), /ungültige Beobachtung/);
});

test('exports only UTC month, observation type and count in the privacy-minimized summary', () => {
  const rows = [
    observation({
      id: 'private-id-one',
      at: '2026-11-21T08:00:00.000Z',
      note: 'PRIVATE NOTE ONE',
      photo: photo(),
      location: {latitude: 51.5, longitude: 7.4, accuracyMeters: 3}
    }),
    observation({
      id: 'private-id-two',
      at: '2026-11-22T09:30:00.000Z',
      type: 'Varroa',
      note: 'PRIVATE NOTE TWO',
      location: {latitude: 51.6, longitude: 7.5, accuracyMeters: 4}
    }),
    observation({
      id: 'private-id-three',
      at: '2026-11-30T23:59:00.000Z',
      note: 'PRIVATE NOTE THREE'
    }),
    observation({
      id: 'private-id-four',
      at: '2026-12-01T00:00:00.000Z',
      type: 'Pollen',
      note: 'PRIVATE NOTE FOUR'
    })
  ];

  const csv = contract.buildPrivacySummaryCsv(rows);
  assert.equal(csv,
    String.fromCharCode(0xfeff) + '"Monat (UTC)";"Beobachtungstyp";"Anzahl"' + String.fromCharCode(13, 10) +
    '"2026-11";"Asiatische Hornisse";"2"' + String.fromCharCode(13, 10) +
    '"2026-11";"Varroa";"1"' + String.fromCharCode(13, 10) +
    '"2026-12";"Pollen";"1"' + String.fromCharCode(13, 10)
  );
  for (const secret of [
    'private-id-', 'PRIVATE NOTE', 'data:image/', '51.5', '7.4',
    'reviewer:', 'latitude', 'longitude'
  ]) {
    assert.equal(csv.includes(secret), false, secret);
  }
});

test('rejects invalid rows and oversized inputs for the privacy summary', () => {
  assert.throws(
    () => contract.buildPrivacySummaryCsv([observation({type: '=HYPERLINK("https://example.invalid")'})]),
    /ungültige Beobachtung/
  );
  assert.throws(
    () => contract.buildPrivacySummaryCsv(null),
    /ungültige oder zu viele Beobachtungen/
  );
  assert.throws(
    () => contract.buildPrivacySummaryCsv(Array(contract.MAX_OBSERVATIONS + 1).fill(observation())),
    /ungültige oder zu viele Beobachtungen/
  );
});

