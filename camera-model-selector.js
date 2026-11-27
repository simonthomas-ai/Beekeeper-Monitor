'use strict';
(function attach(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && root.document && typeof root.fetch === 'function') {
    api.mount(root.document, root.fetch.bind(root));
  }
})(typeof window !== 'undefined' ? window : null, function createCameraModelSelector() {
  const CATALOG_STATUS = 'candidates_only_no_execution';
  const PENDING_STATUS = 'rights_and_runtime_pending';
  const TASKS = new Set(['hornet_detection', 'varroa_sticky_board', 'varroa_on_bee']);
  const EXECUTION_FIELDS = ['enabled', 'active', 'inference_enabled', 'deployable', 'sha256', 'license_approved'];

  function invalid(reason) {
    return { ok: false, reason, options: [] };
  }

  function inspectCatalog(data) {
    if (!data || typeof data !== 'object' || Array.isArray(data)) return invalid('invalid_object');
    if (data.schema_version !== 1 || data.status !== CATALOG_STATUS) return invalid('unsupported_catalog');
    if (!Array.isArray(data.models) || data.models.length < 1 || data.models.length > 30) return invalid('invalid_model_list');

    const ids = new Set();
    const options = [];
    for (const model of data.models) {
      if (!model || typeof model !== 'object' || Array.isArray(model)) return invalid('invalid_candidate');
      if (typeof model.id !== 'string' || !/^[a-z0-9-]{1,80}$/.test(model.id) || ids.has(model.id)) {
        return invalid('invalid_candidate_id');
      }
      ids.add(model.id);
      if (typeof model.task !== 'string' || !TASKS.has(model.task)) return invalid('invalid_task');
      if (typeof model.upstream !== 'string' || !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(model.upstream)) {
        return invalid('invalid_upstream');
      }
      if (typeof model.commit !== 'string' || !/^[0-9a-f]{40}$/.test(model.commit)) return invalid('invalid_revision');
      if (typeof model.path !== 'string' || model.path.startsWith('/') || model.path.includes('\\') ||
          model.path.split('/').some(part => !part || part === '.' || part === '..')) {
        return invalid('unsafe_model_path');
      }
      if (!['onnx', 'pt'].includes(model.format) || !model.path.endsWith('.' + model.format)) {
        return invalid('invalid_format');
      }
      if (!Number.isSafeInteger(model.bytes) || model.bytes <= 0 || model.bytes >= 500000000) {
        return invalid('invalid_size');
      }
      if (typeof model.git_blob !== 'string' || !/^[0-9a-f]{40}$/.test(model.git_blob)) {
        return invalid('invalid_blob_fingerprint');
      }
      if (model.review_status !== PENDING_STATUS || EXECUTION_FIELDS.some(key => Object.hasOwn(model, key))) {
        return invalid('candidate_not_fail_closed');
      }
      options.push({
        value: model.id,
        label: model.id + ' — ' + model.task + ' · ' + model.format.toUpperCase() +
          ' · gesperrt: Rechte und Laufzeit offen',
        disabled: true
      });
    }
    return {
      ok: true,
      options,
      statusText: 'Kein Modell aktiv. ' + options.length +
        ' externe Kandidaten im Katalog; alle gesperrt (Rechte, Runtime und Feldvalidierung offen).'
    };
  }

  function mount(documentRef, fetcher) {
    const select = documentRef && documentRef.getElementById('camera-model');
    const status = documentRef && documentRef.getElementById('camera-model-status');
    const active = documentRef && documentRef.getElementById('camera-model-active');
    if (!select || !status || typeof fetcher !== 'function') return Promise.resolve(false);

    const reset = (message, unavailable) => {
      const placeholder = documentRef.createElement('option');
      placeholder.value = '';
      placeholder.textContent = 'Kein freigegebenes Modell verfügbar';
      placeholder.disabled = true;
      placeholder.selected = true;
      select.replaceChildren(placeholder);
      select.value = '';
      select.disabled = unavailable;
      status.textContent = message;
      if (active) active.textContent = 'Aktives Modell: keines – keine Modellgewichte geladen.';
    };

    reset('Modellkatalog wird lokal geladen; es ist kein Modell aktiv.', true);

    let catalogUrl;
    try {
      const baseUrl = new URL(documentRef.baseURI);
      catalogUrl = new URL('./models/candidates.json', baseUrl);
      if (catalogUrl.origin !== baseUrl.origin) throw new Error('cross_origin_catalog');
    } catch {
      reset('Modellkatalog nicht verfügbar – Auswahl gesperrt. Aktives Modell: keines.', true);
      return Promise.resolve(false);
    }

    let request;
    try {
      request = fetcher(catalogUrl.href, {
        credentials: 'same-origin',
        cache: 'no-store',
        redirect: 'error'
      });
    } catch {
      reset('Modellkatalog nicht verfügbar – Auswahl gesperrt. Aktives Modell: keines.', true);
      return Promise.resolve(false);
    }

    return Promise.resolve(request)
      .then(response => {
        if (!response || !response.ok || typeof response.json !== 'function') {
          throw new Error('catalog_fetch_failed');
        }
        return response.json();
      })
      .then(data => {
        const view = inspectCatalog(data);
        if (!view.ok) throw new Error('catalog_rejected');
        const placeholder = documentRef.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Kein freigegebenes Modell verfügbar';
        placeholder.disabled = true;
        placeholder.selected = true;
        select.replaceChildren(placeholder);
        for (const item of view.options) {
          const option = documentRef.createElement('option');
          option.value = item.value;
          option.textContent = item.label;
          option.disabled = true;
          select.append(option);
        }
        select.value = '';
        select.disabled = false;
        status.textContent = view.statusText;
        if (active) active.textContent = 'Aktives Modell: keines – keine Modellgewichte geladen.';
        return true;
      })
      .catch(() => {
        reset('Modellkatalog nicht verfügbar – Auswahl gesperrt. Aktives Modell: keines.', true);
        return false;
      });
  }

  return { inspectCatalog, mount };
});
