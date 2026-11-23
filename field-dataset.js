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
  const form = document.getElementById('field-dataset-form');
  if (!form) return;
  const status = document.getElementById('field-dataset-status');
  const rows = document.getElementById('field-dataset-entries');
  const exportButton = document.getElementById('field-dataset-export');
  const kindRadios = [...form.querySelectorAll('input[name="image-kind"]')];
  const classInputs = [...form.querySelectorAll('input[name="class-label"]')];
  const classGroup = document.getElementById('field-dataset-classes');
  const rightsBasis = document.getElementById('field-rights-basis');
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

  function extensionFor(type) {
    const extension = MIME_EXTENSIONS[type.toLowerCase()];
    if (!extension) throw Error('Nicht unterstütztes Bildformat.');
    return extension;
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
    const approved = record.review_status === 'approved' && record.rights.status === 'training_approved';
    setText(metadata, `${new Date(record.captured_at).toLocaleString('de-DE')} · ${approved ? 'Nutzerattestierung für Trainingsverwendung' : 'Prüfung ausstehend'} · Quelle: ${record.rights.source}`);
    const rights = document.createElement('p');
    setText(rights, `Rechteangabe (Nutzereingabe, nicht verifiziert): ${record.rights.basis} · Status: ${record.rights.status}`);
    details.append(title, metadata, rights);

    if (!approved) {
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
        approve.disabled = !contentReview.checked || !rightsReview.checked;
      };
      contentReview.addEventListener('change', updateApprovalButton);
      rightsReview.addEventListener('change', updateApprovalButton);
      approve.addEventListener('click', async () => {
        if (!contentReview.checked || !rightsReview.checked) {
          setText(status, 'Bitte Bild/Labels prüfen und die Nutzungsberechtigung ausdrücklich attestieren.');
          return;
        }
        if (!window.confirm('Du bestätigst persönlich, dass du Bild und alle Labels geprüft hast und das Bild für Trainingszwecke verwenden darfst. Die App überprüft diese Erklärung nicht. Fortfahren?')) return;
        try {
          record.review_status = 'approved';
          record.rights.status = 'training_approved';
          await update(record);
          setText(status, 'Deine manuelle Prüfung und Nutzungsattestierung wurden gespeichert; die App hat sie nicht unabhängig verifiziert.');
        } catch (error) {
          setText(status, 'Freigabe fehlgeschlagen: ' + error.message);
        }
      });
      details.append(contentReviewLabel, rightsReviewLabel, reviewNote, approve);
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
      const pending = records.filter(record => record.review_status !== 'approved' ||
        record.rights.status !== 'training_approved');
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
    const records = await all();
    if (!records.length) throw Error('Es gibt keine lokalen Aufnahmen zum Exportieren.');
    if (records.length >= 0xffff) throw Error('ZIP-Export abgebrochen: zu viele Aufnahmen für das Archivformat.');
    if (records.some(record => record.review_status !== 'approved' ||
        record.rights.status !== 'training_approved' ||
        !record.rights.basis || record.rights.basis === 'not_assessed')) {
      throw Error('Export gesperrt: Für jede Aufnahme sind manuelle Bild-/Labelprüfung und ausdrückliche Attestierung der Trainingsnutzung erforderlich.');
    }
    const files = [];
    const annotations = [];
    const imageDigests = new Set();
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
        rights: record.rights
      };
      if (record.labeler_id) annotation.labeler_id = record.labeler_id;
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
    setText(status, `${records.length} attestierte Aufnahme(n) exportiert. Bildinhalte und Rechte wurden nicht unabhängig verifiziert; die lokale Sammlung bleibt erhalten.`);
  }

  for (const radio of kindRadios) radio.addEventListener('change', updateKind);
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
      const source = document.getElementById('field-rights-source').value.trim();
      const basisInput = rightsBasis.value.trim();
      if (!source || source.length > 200) throw Error('Bitte die Bildquelle als Text (maximal 200 Zeichen) angeben.');
      if (!basisInput || basisInput.length > 120) throw Error('Bitte die Rechte-/Nutzungsangabe als Text (maximal 120 Zeichen) angeben.');
      const record = {
        id: id(),
        image_bytes: await file.arrayBuffer(),
        image_type: file.type.toLowerCase(),
        labels,
        captured_at: new Date().toISOString(),
        capture_session_id: sessionId,
        review_status: 'pending_review',
        rights: {
          source,
          basis: basisInput,
          status: 'pending_review'
        }
      };
      const labeler = document.getElementById('field-labeler-id').value.trim();
      if (labeler) record.labeler_id = labeler;
      await put(record);
      form.reset();
      classInputs.forEach(input => { input.checked = false; });
      updateKind();
      setText(status, 'Bild und Angaben lokal gespeichert. Noch ungeprüft; die App prüft keine Rechte. Für den Export sind eine separate Nutzerattestierung und manuelle Bild-/Labelprüfung nötig.');
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
  void render();
})();
