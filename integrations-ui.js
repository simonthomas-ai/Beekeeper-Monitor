'use strict';
(() => {
  const form = document.getElementById('station-events-form');
  const tokenInput = document.getElementById('station-events-token');
  const status = document.getElementById('station-events-status');
  const list = document.getElementById('station-events-list');
  const exportButton = document.getElementById('station-events-export');
  if (!form || !tokenInput || !status || !list) return;

  const isLocalGateway =
    location.protocol === 'http:' &&
    location.port === '8765' &&
    ['127.0.0.1', 'localhost', '[::1]'].includes(location.hostname);

  let activeToken = '';

  function setStatus(message) {
    status.textContent = message;
  }

  function clearList() {
    list.replaceChildren();
  }

  async function api(path, options = {}) {
    if (!isLocalGateway) throw new Error('Die lokale Stationsschnittstelle ist nur über http://127.0.0.1:8765 erreichbar.');
    if (!activeToken) throw new Error('Bitte zuerst den lokalen Empfangsschlüssel eingeben.');
    const response = await fetch(path, {
      ...options,
      mode: 'same-origin',
      credentials: 'omit',
      cache: 'no-store',
      redirect: 'error',
      headers: {
        ...(options.headers || {}),
        Authorization: 'Bearer ' + activeToken
      }
    });
    if (response.status === 401) {
      activeToken = '';
      throw new Error('Schlüssel abgewiesen. Bitte erneut verbinden.');
    }
    if (!response.ok) throw new Error('Lokaler Server meldet HTTP ' + response.status);
    return response.json();
  }

  async function exportEvents() {
    if (!isLocalGateway || !activeToken) throw new Error('Bitte zuerst mit dem lokalen Empfangsschlüssel verbinden.');
    const response = await fetch('/api/v1/events/export?limit=500', {
      mode: 'same-origin', credentials: 'omit', cache: 'no-store', redirect: 'error',
      headers: { Authorization: 'Bearer ' + activeToken }
    });
    if (response.status === 401) {
      activeToken = '';
      throw new Error('Schlüssel abgewiesen. Bitte erneut verbinden.');
    }
    if (!response.ok) throw new Error('Export fehlgeschlagen: HTTP ' + response.status);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'beekeeper-station-events.json';
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 30000);
    setStatus('Stationsdaten exportiert. Die Datei enthält sensible Stationsmetadaten; sicher speichern.');
  }

  function renderRows(rows) {
    clearList();
    if (!Array.isArray(rows) || rows.length === 0) {
      const empty = document.createElement('li');
      empty.textContent = 'Keine Stationsereignisse vorhanden.';
      list.append(empty);
      return;
    }

    for (const row of rows) {
      if (!row || typeof row.event_id !== 'string' || !/^[a-f0-9]{64}$/.test(row.event_id)) continue;
      const event = row.event && typeof row.event === 'object' ? row.event : {};
      const payload = event.payload && typeof event.payload === 'object' ? event.payload : {};
      const label = typeof payload.label === 'string' ? payload.label : String(event.kind || 'Ereignis');
      const device = typeof event.device_id === 'string' ? event.device_id : 'unbekannte Station';
      const timestamp = typeof event.timestamp === 'string' ? event.timestamp : row.received_at;
      const confidence = Number.isFinite(payload.confidence)
        ? ' · Konfidenz ' + Math.round(payload.confidence * 100) + '%'
        : '';
      const li = document.createElement('li');
      const text = document.createElement('span');
      const parsed = Date.parse(timestamp || '');
      const when = Number.isFinite(parsed) ? new Date(parsed).toLocaleString('de-DE') : 'Zeit unbekannt';
      text.textContent = when + ' · ' + device + ' · ' + label + confidence + ' · ' +
        String(event.verification_status || payload.verification_status || 'nicht fachlich bestätigt');
      li.append(text, document.createTextNode(' '));

      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = 'Servereintrag löschen';
      remove.addEventListener('click', async () => {
        if (!window.confirm('Diesen Ereigniseintrag dauerhaft aus dem lokalen Stationsspeicher löschen?')) return;
        remove.disabled = true;
        try {
          await api('/api/v1/events/' + row.event_id, { method: 'DELETE' });
          setStatus('Servereintrag gelöscht.');
          await refresh();
        } catch (error) {
          remove.disabled = false;
          setStatus('Löschen fehlgeschlagen: ' + error.message);
        }
      });
      li.append(remove);
      list.append(li);
    }
  }

  async function refresh() {
    setStatus('Lade lokale Stationsereignisse …');
    const data = await api('/api/v1/events?limit=100');
    if (!data || !Array.isArray(data.events)) throw new Error('Ungültige Antwort des lokalen Servers.');
    renderRows(data.events);
    setStatus(data.count + ' lokale Stationsereignisse geladen. Unbestätigte Kandidaten sind keine Artbestimmung.');
  }

  if (exportButton) {
    exportButton.disabled = true;
    exportButton.addEventListener('click', async () => {
      exportButton.disabled = true;
      try { await exportEvents(); }
      catch (error) { setStatus('Export fehlgeschlagen: ' + error.message); }
      finally { exportButton.disabled = !activeToken; }
    });
  }

  if (!isLocalGateway) {
    tokenInput.disabled = true;
    form.querySelector('button[type="submit"]').disabled = true;
    setStatus('Nicht verbunden: Öffne die lokale Installation über http://127.0.0.1:8765/. Die öffentliche GitHub-Pages-Seite greift nicht auf lokale Stationsdaten zu.');
    return;
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const candidate = tokenInput.value;
    tokenInput.value = '';
    if (candidate.length < 24) {
      setStatus('Der Empfangsschlüssel muss mindestens 24 Zeichen lang sein.');
      return;
    }
    activeToken = candidate;
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    try {
      await refresh();
      if (exportButton) exportButton.disabled = false;
    } catch (error) {
      activeToken = '';
      if (exportButton) exportButton.disabled = true;
      clearList();
      setStatus('Verbindung fehlgeschlagen: ' + error.message);
    } finally {
      button.disabled = false;
    }
  });

  window.addEventListener('pagehide', () => { activeToken = ''; });
})();
