'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const rules = require('../alert-rules.js');

const NOW = Date.parse('2026-11-20T12:00:00Z');
const hex = (c) => c.repeat(64);
function row(id, over = {}, payload = {}) {
  return {
    event_id: hex(id),
    received_at: '2026-11-20T11:59:00Z',
    event: {
      kind: 'camera_detection',
      device_id: 'station-1',
      timestamp: '2026-11-20T11:59:00Z',
      payload: { label: 'vespa_velutina', confidence: 1, ...payload },
      ...over
    }
  };
}
const on = (extra = {}) => ({ enabled: true, ...extra });

test('disabled settings never alert', () => {
  assert.deepEqual(rules.selectAlerts([row('a')], { enabled: false }, new Set(), NOW).alerts, []);
  assert.deepEqual(rules.selectAlerts([row('a')], undefined, new Set(), NOW).alerts, []);
});

test('default threshold is 100 percent and rejects 99 percent', () => {
  const out = rules.selectAlerts([row('a', {}, { confidence: 0.99 }), row('b')], on(), new Set(), NOW);
  assert.equal(out.alerts.length, 1);
  assert.equal(out.alerts[0].id, hex('b'));
});

test('lower threshold is honoured and clamped to at least 50 percent', () => {
  const s = rules.normalizeSettings({ enabled: true, thresholdPercent: 10 });
  assert.equal(s.thresholdPercent, 50);
  const out = rules.selectAlerts([row('a', {}, { confidence: 0.8 })], on({ thresholdPercent: 80 }), new Set(), NOW);
  assert.equal(out.alerts.length, 1);
  assert.equal(rules.selectAlerts([row('a', {}, { confidence: 0.79 })], on({ thresholdPercent: 80 }), new Set(), NOW).alerts.length, 0);
});

test('only vespa_velutina camera or acoustic events qualify', () => {
  const rows = [
    row('a', {}, { label: 'vespa_crabro' }),
    row('b', {}, { label: 'apis_mellifera' }),
    row('c', { kind: 'hive_telemetry' }),
    row('d', { kind: 'acoustic_event' })
  ];
  const out = rules.selectAlerts(rows, on(), new Set(), NOW);
  assert.deepEqual(out.alerts.map((a) => a.id), [hex('d')]);
});

test('BeeKeeper3000 unverified velutina candidate triggers an opt-in warning', () => {
  const candidate = row('a', {}, {
    label: 'unverified_candidate:vespa_velutina',
    verification_status: 'unverified'
  });
  const result = rules.selectAlerts([candidate], on(), new Set(), NOW);
  assert.equal(result.alerts.length, 1);
  assert.match(rules.describe(result.alerts[0]), /unbestätigt/);
});

test('other bridge species and misleading prefixes never trigger velutina warnings', () => {
  for (const label of [
    'unverified_candidate:vespa_crabro',
    'unverified_candidate:vespa_velutina_other',
    'unverified_candidate:other_vespidae',
    'unverified_candidate:vespa_velutina:confirmed'
  ]) {
    const result = rules.selectAlerts([row('a', {}, { label })], on(), new Set(), NOW);
    assert.equal(result.alerts.length, 0, label);
  }
});

test('already seen, stale, future and malformed events are ignored', () => {
  const rows = [
    row('a'),
    row('b', { timestamp: '2026-11-20T11:00:00Z' }),
    row('c', { timestamp: '2026-11-20T13:00:00Z' }),
    row('d', { timestamp: 'kaputt' }, {}),
    { event_id: 'zzz', event: {} },
    null,
    row('e', {}, { confidence: 'hoch' }),
    row('f', {}, { confidence: 1.5 })
  ];
  rows[3].received_at = undefined;
  const out = rules.selectAlerts(rows, on(), new Set([hex('a')]), NOW);
  assert.deepEqual(out.alerts, []);
});

test('cooldown suppresses bursts but allows the first alert', () => {
  const rows = [row('a', { timestamp: '2026-11-20T11:58:00Z' }), row('b', { timestamp: '2026-11-20T11:59:00Z' })];
  const out = rules.selectAlerts(rows, on(), new Set(), NOW, undefined);
  assert.equal(out.alerts.length, 1);
  assert.equal(out.alerts[0].id, hex('a'));
  assert.equal(out.suppressedByCooldown, 1);
  const later = rules.selectAlerts(rows, on({ cooldownSeconds: 0 }), new Set(), NOW);
  assert.equal(later.alerts.length, 2);
  const cooling = rules.selectAlerts(rows, on(), new Set(), NOW, NOW - 60 * 1000);
  assert.equal(cooling.alerts.length, 0);
});

test('message always marks the finding as unconfirmed', () => {
  const [alert] = rules.selectAlerts([row('a')], on(), new Set(), NOW).alerts;
  const text = rules.describe(alert);
  assert.match(text, /unbestätigt/);
  assert.match(text, /100%/);
  assert.ok(text.startsWith('Verdacht'));
});

test('garbage settings fall back to safe defaults', () => {
  const s = rules.normalizeSettings({ enabled: 'yes', thresholdPercent: 'abc', maxAgeMinutes: -5, cooldownSeconds: null });
  assert.equal(s.enabled, false);
  assert.equal(s.thresholdPercent, 100);
  assert.equal(s.maxAgeMinutes, 1);
  assert.equal(s.cooldownSeconds, 300);
});
