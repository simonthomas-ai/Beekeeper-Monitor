'use strict';
(() => {
  const rules = window.BeekeeperAlertRules;
  const section = document.getElementById('hornet-alert');
  if (!rules || !section) return;

  const enabledBox = document.getElementById('alert-enabled');
  const thresholdInput = document.getElementById('alert-threshold');
  const permissionButton = document.getElementById('alert-permission');
  const testButton = document.getElementById('alert-test');
  const statusEl = document.getElementById('alert-status');
  const listEl = document.getElementById('alert-list');
  const SETTINGS_KEY = 'beekeeper-alert-settings-v1';
  const SEEN_KEY = 'beekeeper-alert-seen-v1';
  const LAST_KEY = 'beekeeper-alert-last-v1';
  const MAX_SEEN = 500;

  function load(key, fallback) {
    try {
      const raw = window.localStorage.getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    } catch (_) { return fallback; }
  }
  function save(key, value) {
    try { window.localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* Speicher evtl. gesperrt */ }
  }

  let settings = rules.normalizeSettings(load(SETTINGS_KEY, null));
  const stored = load(SEEN_KEY, []);
  const seen = new Set(Array.isArray(stored) ? stored.filter(id => typeof id === 'string').slice(-MAX_SEEN) : []);
  let lastAlertMs = Number(load(LAST_KEY, NaN));

  function setStatus(message) { statusEl.textContent = message; }

  function permissionText() {
    if (!('Notification' in window)) return 'Dieser Browser unterstützt keine Systembenachrichtigungen; es gibt nur Hinweis im Fenster und Ton.';
    if (Notification.permission === 'granted') return 'Systembenachrichtigungen sind erlaubt.';
    if (Notification.permission === 'denied') return 'Systembenachrichtigungen sind im Browser blockiert; es gibt nur Hinweis im Fenster und Ton.';
    return 'Systembenachrichtigungen noch nicht erlaubt.';
  }

  function render() {
    enabledBox.checked = settings.enabled;
    thresholdInput.value = String(settings.thresholdPercent);
    setStatus((settings.enabled
      ? 'Warnung aktiv ab ' + settings.thresholdPercent + ' % Konfidenz. '
      : 'Warnung ausgeschaltet. ') + permissionText());
  }

  function persistSettings() { save(SETTINGS_KEY, settings); }

  function beep() {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      const ctx = new Ctx();
      const start = ctx.currentTime;
      for (let i = 0; i < 3; i += 1) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.frequency.value = 880;
        gain.gain.value = 0.15;
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(start + i * 0.35); osc.stop(start + i * 0.35 + 0.2);
      }
      window.setTimeout(() => ctx.close().catch(() => {}), 1500);
    } catch (_) { /* Ton ist optional */ }
  }

  async function notify(title, body, tag) {
    if (!('Notification' in window) || Notification.permission !== 'granted') return;
    const options = { body, tag, icon: './icon.svg', requireInteraction: true };
    try {
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.getRegistration();
        if (registration) { await registration.showNotification(title, options); return; }
      }
      new Notification(title, options);
    } catch (_) { /* Banner im Fenster bleibt als Rückfall */ }
  }

  function banner(text) {
    const li = document.createElement('li');
    li.textContent = new Date().toLocaleTimeString('de-DE') + ' · ' + text;
    listEl.prepend(li);
    while (listEl.children.length > 20) listEl.lastElementChild.remove();
  }

  enabledBox.addEventListener('change', () => {
    settings = rules.normalizeSettings({ ...settings, enabled: enabledBox.checked });
    persistSettings(); render();
  });
  thresholdInput.addEventListener('change', () => {
    settings = rules.normalizeSettings({ ...settings, thresholdPercent: thresholdInput.value });
    persistSettings(); render();
  });
  permissionButton.addEventListener('click', async () => {
    if (!('Notification' in window)) { render(); return; }
    try { await Notification.requestPermission(); } catch (_) { /* ignorieren */ }
    render();
  });
  testButton.addEventListener('click', () => {
    const text = 'TEST: So würde eine Warnung aussehen (kein echter Fund).';
    banner(text); beep(); notify('Beekeeper Monitor – Test', text, 'hornet-test');
  });

  window.BeekeeperAlerts = {
    isEnabled: () => settings.enabled,
    /** Wertet geladene Stationsereignisse aus und warnt einmal pro Ereignis. */
    process(rows) {
      const now = Date.now();
      const { alerts, suppressedByCooldown } = rules.selectAlerts(rows, settings, seen, now, lastAlertMs);
      for (const alert of alerts) {
        seen.add(alert.id);
        const text = rules.describe(alert);
        banner(text); notify('Möglicher Hornissenfund (unbestätigt)', text, 'hornet-' + alert.id.slice(0, 16));
      }
      if (alerts.length > 0) {
        lastAlertMs = now; beep();
        save(SEEN_KEY, Array.from(seen).slice(-MAX_SEEN)); save(LAST_KEY, lastAlertMs);
        setStatus(alerts.length + ' neue Warnung(en). Das ist ein unbestätigter Verdacht, keine Artbestimmung.');
      } else if (suppressedByCooldown > 0) {
        setStatus(suppressedByCooldown + ' weitere Meldung(en) wegen Wartezeit zwischen Warnungen zurückgehalten.');
      }
    }
  };

  render();
})();
