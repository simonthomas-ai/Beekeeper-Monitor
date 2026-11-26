'use strict';
(() => {
  const DB = 'beekeeper-field-dataset-v1';
  const STORE = 'images';
  const MAX_IMAGE_BYTES = 8 * 1024 * 1024;
  const CLASSES = Object.freeze([
    'vespa_velutina', 'vespa_crabro', 'other_vespidae',
    'apis_mellifera', 'bombus_spp', 'syrphidae', 'other_insect'
  ]);
  const MIME_EXTENSIONS = Object.freeze({
    'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp',
  });
  const RIGHTS_BASES = Object.freeze([
    'CC0-1.0', 'CC-BY-4.0', 'LicenseRef-ExplicitPermission'
  ]);
  const RIGHTS_LICENSES = Object.freeze({
    'CC0-1.0': 'https://creativecommons.org/publicdomain/zero/1.0/',
    'CC-BY-4.0': 'https://creativecommons.org/licenses/by/4.0/'
  });
  const REVIEWER_ID = /^reviewer:[A-Za-z0-9][A-Za-z0-9._:-]{7,79}$/;
  const form = document.getElementById('field-dataset-form');
  if (!form) return;
  const status = document.getElementById('field-dataset-status');
  const rows = document.getElementById('field-dataset-entries');
  const exportButton = document.getElementById('field-dataset-export');
  if (!exportButton) return;
  const kindRadios = [...form.querySelectorAll('input[name="image-kind"]')];
  const classInputs = [...form.querySelectorAll('input[name="class-label"]')];
  const classGroup = document.getElementById('field-dataset-classes');
  const rightsBasis = document.getElementById('field-rights-basis');
  const rightsSource = document.getElementById('field-rights-source');
  const rightsEvidence = document.getElementById('field-rights-evidence');
  const attributionField = document.getElementById('field-rights-attribution-field');
  const attributionInput = document.getElementById('field-rights-attribution');
  const permissionField = document.getElementById('field-rights-permission-field');
  const permissionInput = document.getElementById('field-rights-permission-ref');
  const reviewerIdInput = document.getElementById('field-reviewer-id');
  let objectUrls = [];

  function id() {
    if (crypto.randomUUID) return crypto.randomUUID();
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    return [...bytes].map(value => value.toString(16).padStart(2, '0')).join('');
  }

  function captureSessionId() {
    const key = 'beekeeper-field-capture-session';
    try {
      let value = sessionStorage.getItem(key);
      if (!value) {
        value = id();
        sessionStorage.setItem(key, value);
      }
      return value;
    } catch {
      return id();
    }
  }

  const sessionId = captureSessionId();

  function database() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB, 1);
      request.onupgradeneeded = () => request.result.createObjectStore(STORE, {keyPath: 'id'});
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function all() {
    const db = await database();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readonly');
      const request = tx.objectStore(STORE).getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
      tx.oncomplete = () => db.close();
      tx.onerror = () => { db.close(); reject(tx.error); };
    });
  }

  async function put(record) {
    const db = await database();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      const request = tx.objectStore(STORE).put(record);
      request.onerror = () => reject(request.error || Error('Lokale Aufnahme konnte nicht gespeichert werden.'));
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = () => { db.close(); reject(tx.error || request.error || Error('Lokale Aufnahme konnte nicht gespeichert werden.')); };
      tx.onabort = () => { db.close(); reject(tx.error || request.error || Error('Lokale Aufnahme konnte nicht gespeichert werden.')); };
    });
  }

  async function remove(recordId) {
    const db = await database();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).delete(recordId);
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = () => { db.close(); reject(tx.error); };
    });
  }

  async function update(record) {
    await put(record);
    await render();
  }

  function selectedKind() {
    return kindRadios.find(input => input.checked)?.value || '';
  }

  function updateKind() {
    const positive = selectedKind() === 'positive';
    classGroup.hidden = !positive;
    for (const input of classInputs) input.disabled = !positive;
  }

  function labelsForForm() {
    if (selectedKind() === 'negative') return [];
    if (selectedKind() !== 'positive') throw Error('Bitte Bildtyp auswählen.');
    const labels = classInputs.filter(input => input.checked).map(input => input.value);
    if (!labels.length) throw Error('Für ein Bild mit Zielklassen mindestens eine Klasse auswählen.');
    if (labels.some(label => !CLASSES.includes(label))) throw Error('Unbekannte Bildklasse.');
    return labels;
  }

  function normalizeSource(value) {
    const source = typeof value === 'string' ? value.trim() : '';
    if (!source || source.length > 200) {
      throw Error('Bitte eine Bildquelle bis 200 Zeichen angeben.');
    }
    if (['eigene feldaufnahme', 'own field capture'].includes(source.toLowerCase())) {
      return 'Eigene Feldaufnahme';
    }
    let parsed;
    try {
      parsed = new URL(source);
    } catch {
      throw Error('Die Bildquelle muss „Eigene Feldaufnahme“ oder eine HTTPS-Adresse sein.');
    }
    if (parsed.protocol !== 'https:' || !parsed.hostname || parsed.username ||
        parsed.password || parsed.search || parsed.hash) {
      throw Error('Die Bildquelle muss eine HTTPS-Adresse ohne Zugangsdaten, Query oder Fragment sein.');
    }
    return source;
  }

  function normalizeReviewerId(value) {
    const reviewerId = typeof value === 'string' ? value.trim() : '';
    if (!reviewerId) return '';
    if (!REVIEWER_ID.test(reviewerId)) {
      throw Error('Die pseudonyme Kennung muss das Format reviewer:<opaque-id> verwenden. Keine Namen, E-Mail-Adressen oder URLs eintragen.');
    }
    return reviewerId;
  }

  function reviewProvenanceComplete(record) {
    if (!record || typeof record !== 'object') return false;
    const reviewerId = typeof record.reviewed_by === 'string' ? record.reviewed_by : '';
    const capturedAt = Date.parse(record.captured_at || '');
    const reviewedAt = Date.parse(record.reviewed_at || '');
    const hasTimezone = typeof record.reviewed_at === 'string' &&
      /(?:Z|[+-]\d{2}:\d{2})$/.test(record.reviewed_at);
    return REVIEWER_ID.test(reviewerId) && hasTimezone &&
      Number.isFinite(capturedAt) && Number.isFinite(reviewedAt) &&
      reviewedAt >= capturedAt;
  }

  function normalizeRights(rights, requiredStatus) {
    if (!rights || typeof rights !== 'object' || Array.isArray(rights)) {
      throw Error('Rechteangaben fehlen oder sind ungültig.');
    }
    const allowedFields = new Set([
      'source', 'basis', 'status', 'evidence_url', 'attribution',
      'permission_ref', 'publication_allowed'
    ]);
    if (Object.keys(rights).some(key => !allowedFields.has(key))) {
      throw Error('Unbekannte Rechtefelder dürfen nicht exportiert werden.');
    }
    if (Object.prototype.hasOwnProperty.call(rights, 'publication_allowed') &&
        rights.publication_allowed !== true) {
      throw Error('Eine explizite publication_allowed-Angabe muss true sein.');
    }
    const source = normalizeSource(rights.source);
    const basis = rights.basis;
    if (!RIGHTS_BASES.includes(basis)) {
      throw Error('Bitte eine der drei unterstützten Rechtebasen auswählen.');
    }
    if (!['pending_review', 'training_approved'].includes(rights.status) ||
        (requiredStatus && rights.status !== requiredStatus)) {
      throw Error('Die Rechteattestierung ist noch nicht abgeschlossen.');
    }
    const normalized = {source, basis, status:rights.status};
    const evidenceUrl = RIGHTS_LICENSES[basis];
    if (evidenceUrl) {
      if (rights.evidence_url !== evidenceUrl) {
        throw Error('Der kanonische Lizenznachweis fehlt oder stimmt nicht mit der Rechtebasis überein.');
      }
      normalized.evidence_url = evidenceUrl;
    }
    if (basis === 'CC-BY-4.0') {
      const attribution = typeof rights.attribution === 'string' ? rights.attribution.trim() : '';
      if (!attribution || attribution.length > 500) {
        throw Error('Für CC BY 4.0 ist eine Attribution bis 500 Zeichen erforderlich.');
      }
      normalized.attribution = attribution;
    }
    if (basis === 'LicenseRef-ExplicitPermission') {
      const permissionRef = typeof rights.permission_ref === 'string' ? rights.permission_ref.trim() : '';
      if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/.test(permissionRef)) {
        throw Error('Für eine individuelle Erlaubnis ist eine opake Referenz (max. 200 Zeichen) erforderlich.');
      }
      normalized.permission_ref = permissionRef;
    }
    return normalized;
  }

  function rightsContractComplete(rights) {
    try {
      normalizeRights(rights);
      return true;
    } catch {
      return false;
    }
  }

  function rightsFromForm() {
    const basis = rightsBasis.value;
    if (!RIGHTS_BASES.includes(basis)) {
      throw Error('Bitte eine unterstützte Rechtebasis auswählen.');
    }
    const rights = {
      source: normalizeSource(rightsSource.value),
      basis,
      status: 'pending_review'
    };
    if (RIGHTS_LICENSES[basis]) rights.evidence_url = RIGHTS_LICENSES[basis];
    if (basis === 'CC-BY-4.0') {
      const attribution = attributionInput.value.trim();
      if (!attribution || attribution.length > 500) {
        throw Error('Für CC BY 4.0 ist eine Attribution bis 500 Zeichen erforderlich.');
      }
      rights.attribution = attribution;
    }
    if (basis === 'LicenseRef-ExplicitPermission') {
      const permissionRef = permissionInput.value.trim();
      if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/.test(permissionRef)) {
        throw Error('Bitte eine opake Erlaubnis-Referenz ohne Namen, E-Mail oder URL angeben.');
      }
      rights.permission_ref = permissionRef;
    }
    return rights;
  }

  function updateRightsFields() {
    const basis = rightsBasis.value;
    const showAttribution = basis === 'CC-BY-4.0';
    attributionField.hidden = !showAttribution;
    attributionInput.disabled = !showAttribution;
    attributionInput.required = showAttribution;
    const showPermission = basis === 'LicenseRef-ExplicitPermission';
    permissionField.hidden = !showPermission;
    permissionInput.disabled = !showPermission;
    permissionInput.required = showPermission;
    const evidenceUrl = RIGHTS_LICENSES[basis];
    rightsEvidence.hidden = !evidenceUrl;
    setText(rightsEvidence, evidenceUrl
      ? 'Kanonischer Lizenznachweis wird automatisch in den Export übernommen: ' + evidenceUrl
      : '');
  }

  function labelsText(labels) {
    return labels.length ? labels.join(', ') : 'Negativbild (keine Zielklasse)';
  }

  function setText(element, value) {
    element.textContent = value;
  }

  function renderRecord(record) {
    const article = document.createElement('article');
    article.className = 'field-dataset-record';
    const image = document.createElement('img');
    image.alt = 'Lokale Aufnahme zur manuellen Klassifikation';
    image.loading = 'lazy';
    image.src = URL.createObjectURL(new Blob([record.image_bytes], {type:record.image_type}));
    objectUrls.push(image.src);
    article.append(image);

    const details = document.createElement('div');
    const title = document.createElement('strong');
    setText(title, labelsText(record.labels));
    const metadata = document.createElement('p');
    const rightsComplete = rightsContractComplete(record.rights);
    const approved = rightsComplete && record.review_status === 'approved' &&
      record.rights.status === 'training_approved' && reviewProvenanceComplete(record);
    setText(metadata, `${new Date(record.captured_at).toLocaleString('de-DE')} · ${approved ? 'Nutzerattestierung für Trainingsverwendung' : 'Prüfung ausstehend'} · Quelle: ${record.rights?.source || 'nicht angegeben'}`);
    const rights = document.createElement('p');
    setText(rights, rightsComplete
      ? `Rechteangabe (Nutzereingabe, nicht verifiziert): ${record.rights.basis} · Status: ${record.rights.status}`
      : 'Alte oder unvollständige Rechteangabe: Diese Aufnahme kann nicht exportiert werden. Bitte mit der strukturierten Rechteauswahl neu erfassen.');
    details.append(title, metadata, rights);

    if (!approved && rightsComplete) {
      const contentReview = document.createElement('input');
      contentReview.type = 'checkbox';
      contentReview.setAttribute('aria-label', 'Bildinhalt und sämtliche Klassen manuell geprüft');
      const contentReviewLabel = document.createElement('label');
      contentReviewLabel.append(contentReview, ' Ich habe Bildinhalt und sämtliche Klassen manuell geprüft.');
      const rightsReview = document.createElement('input');
      rightsReview.type = 'checkbox';
      rightsReview.setAttribute('aria-label', 'Ich attestiere, dass ich das Bild für Trainingszwecke verwenden darf');
      const rightsReviewLabel = document.createElement('label');
      rightsReviewLabel.append(rightsReview, ' Ich attestiere, dass ich das Bild für Trainingszwecke verwenden darf.');
      const reviewNote = document.createElement('p');
      reviewNote.className = 'note';
      setText(reviewNote, 'Die App prüft weder Bildinhalt noch Rechte. Diese Statusangabe hält nur deine persönliche Erklärung fest; sie ist kein unabhängiger Rechte- oder Fachnachweis.');
      const approve = document.createElement('button');
      approve.type = 'button';
      approve.textContent = 'Manuelle Prüfung und Nutzungsattestierung speichern';
      approve.disabled = true;
      const updateApprovalButton = () => {
        let reviewerReady = false;
        try {
          reviewerReady = Boolean(normalizeReviewerId(reviewerIdInput?.value));
        } catch {
          reviewerReady = false;
        }
        approve.disabled = !contentReview.checked || !rightsReview.checked || !reviewerReady;
      };
      contentReview.addEventListener('change', updateApprovalButton);
      rightsReview.addEventListener('change', updateApprovalButton);
      reviewerIdInput?.addEventListener('input', updateApprovalButton);
      approve.addEventListener('click', async () => {
        if (!contentReview.checked || !rightsReview.checked) {
          setText(status, 'Bitte Bild/Labels prüfen und die Nutzungsberechtigung ausdrücklich attestieren.');
          return;
        }
        let reviewerId;
        try {
          reviewerId = normalizeReviewerId(reviewerIdInput?.value);
          if (!reviewerId) throw Error('Für die Freigabe ist eine pseudonyme Prüfer-ID erforderlich.');
        } catch (error) {
          setText(status, 'Freigabe nicht möglich: ' + error.message);
          return;
        }
        if (!window.confirm('Du bestätigst persönlich, dass du Bild und alle Labels geprüft hast und das Bild für Trainingszwecke verwenden darfst. Die App überprüft weder diese Erklärung noch die Rechte unabhängig. Fortfahren?')) return;
        try {
          record.rights = normalizeRights({...record.rights, status:'training_approved'}, 'training_approved');
          record.review_status = 'approved';
          record.reviewed_by = reviewerId;
          record.reviewed_at = new Date().toISOString();
          await update(record);
          setText(status, 'Deine manuelle Prüfung und Nutzungsattestierung wurden gespeichert; die App hat sie nicht unabhängig verifiziert.');
        } catch (error) {
          setText(status, 'Freigabe fehlgeschlagen: ' + error.message);
        }
      });
      details.append(contentReviewLabel, rightsReviewLabel, reviewNote, approve);
    } else if (!rightsComplete) {
      const legacyNote = document.createElement('p');
      legacyNote.className = 'note';
      setText(legacyNote, 'Diese Altaufnahme verwendet das frühere Freitextformat. Sie kann lokal gelöscht und mit der strukturierten Rechteauswahl neu erfasst werden.');
      details.append(legacyNote);
    }

    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.textContent = 'Löschen';
    removeButton.addEventListener('click', async () => {
      if (!window.confirm('Diese Aufnahme dauerhaft von diesem Gerät löschen?')) return;
      try {
        await remove(record.id);
        setText(status, 'Aufnahme lokal gelöscht.');
        await render();
      } catch (error) {
        setText(status, 'Löschen fehlgeschlagen: ' + error.message);
      }
    });
    details.append(' ', removeButton);
    article.append(details);
    return article;
  }

  async function render() {
    for (const url of objectUrls) URL.revokeObjectURL(url);
    objectUrls = [];
    rows.replaceChildren();
    try {
      const records = (await all()).sort((a, b) => b.captured_at.localeCompare(a.captured_at));
      for (const record of records) rows.append(renderRecord(record));
      const pending = records.filter(record => !rightsContractComplete(record.rights) ||
        record.review_status !== 'approved' || record.rights.status !== 'training_approved' ||
        !reviewProvenanceComplete(record));
      exportButton.disabled = records.length === 0 || pending.length > 0;
      setText(document.getElementById('field-dataset-summary'),
        `${records.length} lokal${records.length === 1 ? 'e Aufnahme' : 'e Aufnahmen'} · ${pending.length} ohne abgeschlossene Nutzerprüfung`);
    } catch (error) {
      exportButton.disabled = true;
      setText(status, 'Lokaler Aufnahmespeicher nicht verfügbar: ' + error.message);
    }
  }

  function crc32(bytes) {
    let crc = 0xffffffff;
    for (const byte of bytes) {
      crc ^= byte;
      for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  function littleEndian(size, values) {
    const bytes = new Uint8Array(size * values.length);
    const view = new DataView(bytes.buffer);
    values.forEach((value, index) => size === 2
      ? view.setUint16(index * size, value, true)
      : view.setUint32(index * size, value >>> 0, true));
    return bytes;
  }

  function zip(files) {
    const encoder = new TextEncoder();
    if (files.length > 0xffff) throw Error('ZIP-Export abgebrochen: zu viele Dateien für das vereinbarte Archivformat.');
    let expectedLocalSize = 0;
    let expectedCentralSize = 0;
    for (const file of files) {
      const nameLength = encoder.encode(file.name).length;
      expectedLocalSize += 30 + nameLength + file.bytes.length;
      expectedCentralSize += 46 + nameLength;
    }
    if (expectedLocalSize > 0xffffffff || expectedCentralSize > 0xffffffff) {
      throw Error('ZIP-Export abgebrochen: der Bestand überschreitet die Größenbegrenzung des Archivformats.');
    }
    const localParts = [];
    const centralParts = [];
    let offset = 0;
    for (const file of files) {
      const name = encoder.encode(file.name);
      const bytes = file.bytes;
      const checksum = crc32(bytes);
      const localHeader = new Uint8Array([
        0x50,0x4b,0x03,0x04,
        ...littleEndian(2, [20, 0x0800, 0, 0, 0]),
        ...littleEndian(4, [checksum, bytes.length, bytes.length]),
        ...littleEndian(2, [name.length, 0])
      ]);
      const centralHeader = new Uint8Array([
        0x50,0x4b,0x01,0x02,
        ...littleEndian(2, [20, 20, 0x0800, 0, 0, 0]),
        ...littleEndian(4, [checksum, bytes.length, bytes.length]),
        ...littleEndian(2, [name.length, 0, 0, 0, 0]),
        ...littleEndian(4, [0, offset])
      ]);
      localParts.push(localHeader, name, bytes);
      centralParts.push(centralHeader, name);
      offset += localHeader.length + name.length + bytes.length;
    }
    const centralSize = centralParts.reduce((sum, part) => sum + part.length, 0);
    const end = new Uint8Array([
      0x50,0x4b,0x05,0x06, 0,0, 0,0,
      ...littleEndian(2, [files.length, files.length]),
      ...littleEndian(4, [centralSize, offset]), 0,0
    ]);
    return new Blob([...localParts, ...centralParts, end], {type:'application/zip'});
  }

  async function exportDataset() {
    if (!window.confirm('Der ZIP-Export enthält unveränderte Originalbilder. Diese können EXIF-Metadaten wie GPS-Koordinaten, Aufnahmezeit und Kamera-/Geräteinformationen enthalten. Die App lädt die Datei nicht hoch und entfernt diese Metadaten nicht. Vor jeder Weitergabe bitte lokal prüfen. Fortfahren?')) {
      setText(status, 'Export abgebrochen. Es wurde keine Datei heruntergeladen.');
      return;
    }
    const records = await all();
    if (!records.length) throw Error('Es gibt keine lokalen Aufnahmen zum Exportieren.');
    if (records.length >= 0xffff) throw Error('ZIP-Export abgebrochen: zu viele Aufnahmen für das Archivformat.');
    if (records.some(record => !rightsContractComplete(record.rights) ||
        record.review_status !== 'approved' || record.rights.status !== 'training_approved' ||
        !reviewProvenanceComplete(record))) {
      throw Error('Export gesperrt: Jede Aufnahme benötigt vollständige strukturierte Rechteangaben sowie manuelle Bild-/Labelprüfung und ausdrückliche Nutzungsattestierung.');
    }
    const files = [];
    const annotations = [];
    const imageDigests = new Set();
    let omittedLegacyReviewerIds = 0;
    if (!crypto.subtle?.digest) throw Error('Sichere lokale Bildprüfung ist in diesem Browser nicht verfügbar; Export abgebrochen.');
    for (const record of records) {
      if (!Array.isArray(record.labels) || record.labels.some(label => !CLASSES.includes(label))) {
        throw Error('Export abgebrochen: unbekannte oder ungültige Bildklassen.');
      }
      const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', record.image_bytes));
      const digestHex = [...digest].map(byte => byte.toString(16).padStart(2, '0')).join('');
      if (imageDigests.has(digestHex)) {
        throw Error('Export gesperrt: derselbe Bildinhalt wurde mehrfach erfasst. Entferne das Duplikat vor dem Export.');
      }
      imageDigests.add(digestHex);
      const path = `images/${record.id}.${extensionFor(record.image_type)}`;
      const annotation = {
        image: path,
        labels: record.labels,
        captured_at: record.captured_at,
        capture_session_id: record.capture_session_id,
        review_status: record.review_status,
        reviewed_by: record.reviewed_by,
        reviewed_at: record.reviewed_at,
        rights: normalizeRights(record.rights, 'training_approved')
      };
      if (record.labeler_id) {
        const labelerId = typeof record.labeler_id === 'string' ? record.labeler_id.trim() : '';
        if (REVIEWER_ID.test(labelerId)) annotation.labeler_id = labelerId;
        else omittedLegacyReviewerIds += 1;
      }
      annotations.push(JSON.stringify(annotation));
      files.push({name:path, bytes:new Uint8Array(record.image_bytes)});
    }
    files.push({name:'annotations.jsonl', bytes:new TextEncoder().encode(annotations.join('\n') + '\n')});
    const blob = zip(files);
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'beekeeper-field-dataset.zip';
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
    const legacyNote = omittedLegacyReviewerIds
      ? ` ${omittedLegacyReviewerIds} ältere nicht-pseudonyme Labeler-Kennung(en) wurden aus Datenschutzgründen nicht exportiert.`
      : '';
    setText(status, `${records.length} attestierte Aufnahme(n) exportiert. Bildinhalte und Rechte wurden nicht unabhängig verifiziert; die lokale Sammlung bleibt erhalten.${legacyNote}`);
  }

  for (const radio of kindRadios) radio.addEventListener('change', updateKind);
  rightsBasis.addEventListener('change', updateRightsFields);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    setText(status, 'Speichere Bild und manuelle Annotation lokal …');
    try {
      const file = document.getElementById('field-dataset-photo').files[0];
      if (!file || !Object.prototype.hasOwnProperty.call(MIME_EXTENSIONS, file.type.toLowerCase()) ||
          file.size < 1 || file.size > MAX_IMAGE_BYTES) {
        throw Error('Bitte ein JPEG-, PNG- oder WebP-Bild bis 8 MB auswählen. HEIC muss auf dem iPhone zuerst lokal als JPEG gespeichert werden.');
      }
      const labels = labelsForForm();
      const rights = rightsFromForm();
      const labelerId = normalizeReviewerId(document.getElementById('field-labeler-id').value);
      const record = {
        id: id(),
        image_bytes: await file.arrayBuffer(),
        image_type: file.type.toLowerCase(),
        labels,
        captured_at: new Date().toISOString(),
        capture_session_id: sessionId,
        review_status: 'pending_review',
        rights
      };
      if (labelerId) record.labeler_id = labelerId;
      await put(record);
      form.reset();
      classInputs.forEach(input => { input.checked = false; });
      updateKind();
      updateRightsFields();
      setText(status, 'Bild und strukturierte Rechteangaben lokal gespeichert. Noch ungeprüft; die App prüft keine Rechte. Für den Export sind eine separate Nutzerattestierung und manuelle Bild-/Labelprüfung nötig.');
      await render();
    } catch (error) {
      setText(status, 'Nicht gespeichert: ' + error.message);
    } finally {
      button.disabled = false;
    }
  });
  exportButton.addEventListener('click', async () => {
    exportButton.disabled = true;
    try {
      await exportDataset();
    } catch (error) {
      setText(status, 'Export fehlgeschlagen: ' + error.message);
    } finally {
      await render();
    }
  });
  updateKind();
  updateRightsFields();
  void render();
})();
