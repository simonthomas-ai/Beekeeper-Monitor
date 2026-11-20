'use strict';
/*
 * Schwellwert-Warnung für Verdachtsfälle der Asiatischen Hornisse.
 * Reine Regel-Logik (ohne DOM), damit sie mit Node getestet werden kann.
 * Jede Warnung ist ein UNBESTÄTIGTER Verdacht eines nicht validierten Modells,
 * keine Artbestimmung und keine Grundlage für Bekämpfungsmaßnahmen.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.BeekeeperAlertRules = api;
})(typeof self !== 'undefined' ? self : this, function () {
  const TARGET_LABEL = 'vespa_velutina';
  const KINDS = new Set(['camera_detection', 'acoustic_event']);
  const EVENT_ID = /^[a-f0-9]{64}$/;
  const DEFAULTS = Object.freeze({
    enabled: false,
    thresholdPercent: 100,
    maxAgeMinutes: 15,
    cooldownSeconds: 300
  });
  const EPSILON = 1e-9;

  function clamp(value, min, max, fallback) {
    if (value === null || value === '' || typeof value === 'boolean') return fallback;
    const n = Number(value);
    return Number.isFinite(n) ? Math.min(max, Math.max(min, n)) : fallback;
  }

  function normalizeSettings(input) {
    const s = input && typeof input === 'object' ? input : {};
    return {
      enabled: s.enabled === true,
      thresholdPercent: clamp(s.thresholdPercent, 50, 100, DEFAULTS.thresholdPercent),
      maxAgeMinutes: clamp(s.maxAgeMinutes, 1, 1440, DEFAULTS.maxAgeMinutes),
      cooldownSeconds: clamp(s.cooldownSeconds, 0, 86400, DEFAULTS.cooldownSeconds)
    };
  }

  /** Liefert {id, device, confidence, timestampMs, kind} oder null. */
  function candidateFromRow(row) {
    if (!row || typeof row.event_id !== 'string' || !EVENT_ID.test(row.event_id)) return null;
    const event = row.event && typeof row.event === 'object' ? row.event : null;
    const payload = event && event.payload && typeof event.payload === 'object' ? event.payload : null;
    if (!event || !payload || !KINDS.has(event.kind)) return null;
    if (payload.label !== TARGET_LABEL) return null;
    if (typeof payload.confidence !== 'number' || !Number.isFinite(payload.confidence)) return null;
    if (payload.confidence < 0 || payload.confidence > 1) return null;
    const parsed = Date.parse(typeof event.timestamp === 'string' ? event.timestamp : row.received_at || '');
    return {
      id: row.event_id,
      kind: event.kind,
      device: typeof event.device_id === 'string' ? event.device_id : 'unbekannte Station',
      confidence: payload.confidence,
      timestampMs: Number.isFinite(parsed) ? parsed : null
    };
  }

  /**
   * Wählt die Ereignisse, für die gewarnt werden soll.
   * seenIds: Set bereits gemeldeter IDs. lastAlertMs: Zeitpunkt der letzten Warnung.
   * Rückgabe: {alerts, suppressedByCooldown}; alerts ist nach Zeit aufsteigend sortiert.
   */
  function selectAlerts(rows, settingsInput, seenIds, nowMs, lastAlertMs) {
    const settings = normalizeSettings(settingsInput);
    const result = { alerts: [], suppressedByCooldown: 0 };
    if (!settings.enabled || !Array.isArray(rows)) return result;
    const seen = seenIds instanceof Set ? seenIds : new Set();
    const threshold = settings.thresholdPercent / 100 - EPSILON;
    const maxAgeMs = settings.maxAgeMinutes * 60 * 1000;
    const cooldownMs = settings.cooldownSeconds * 1000;

    const fresh = [];
    for (const row of rows) {
      const c = candidateFromRow(row);
      if (!c || seen.has(c.id)) continue;
      if (c.confidence < threshold) continue;
      if (c.timestampMs === null || nowMs - c.timestampMs > maxAgeMs || c.timestampMs - nowMs > 5 * 60 * 1000) continue;
      fresh.push(c);
    }
    fresh.sort((a, b) => a.timestampMs - b.timestampMs);

    let last = Number.isFinite(lastAlertMs) ? lastAlertMs : -Infinity;
    for (const c of fresh) {
      if (nowMs - last < cooldownMs) { result.suppressedByCooldown += 1; continue; }
      result.alerts.push(c);
      last = nowMs;
    }
    return result;
  }

  function describe(alert) {
    return 'Verdacht auf Asiatische Hornisse (unbestätigt) · Station ' + alert.device +
      ' · Konfidenz ' + Math.round(alert.confidence * 100) + '%';
  }

  return { TARGET_LABEL, DEFAULTS, normalizeSettings, candidateFromRow, selectAlerts, describe };
});
