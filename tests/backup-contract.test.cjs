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
  const rows = [observation(), observation({ id: 'observation-2', type: 'Pollen' })];
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
