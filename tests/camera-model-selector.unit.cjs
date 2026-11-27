'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const catalog = require('../models/candidates.json');
const { inspectCatalog, mount } = require('../camera-model-selector.js');

class FakeElement {
  constructor() {
    this.children = [];
    this.dataset = {};
    this.disabled = false;
    this.value = '';
    this.textContent = '';
    this.selected = false;
  }
  replaceChildren(...items) { this.children = [...items]; }
  append(item) { this.children.push(item); }
}

function fakeDocument(baseURI = 'https://vespaguard.example/app/') {
  const elements = {
    'camera-model': new FakeElement(),
    'camera-model-status': new FakeElement(),
    'camera-model-active': new FakeElement()
  };
  return {
    baseURI,
    elements,
    getElementById(id) { return elements[id] || null; },
    createElement() { return new FakeElement(); }
  };
}

test('existing candidate catalog renders only disabled options', () => {
  const view = inspectCatalog(catalog);
  assert.equal(view.ok, true);
  assert.equal(view.options.length, 6);
  assert.ok(view.options.every(option => option.disabled));
  assert.ok(view.options.every(option => option.label.includes('gesperrt')));
  assert.match(view.statusText, /Kein Modell aktiv/);
});

test('rejects a catalog that claims executable or approved status', () => {
  const changed = structuredClone(catalog);
  changed.status = 'approved';
  assert.equal(inspectCatalog(changed).ok, false);

  const enabled = structuredClone(catalog);
  enabled.models[0].enabled = true;
  assert.equal(inspectCatalog(enabled).ok, false);

  const approved = structuredClone(catalog);
  approved.models[0].review_status = 'approved';
  assert.equal(inspectCatalog(approved).ok, false);
});

test('rejects unsafe candidate paths and malformed revisions', () => {
  const unsafe = structuredClone(catalog);
  unsafe.models[0].path = '../weights/model.onnx';
  assert.equal(inspectCatalog(unsafe).ok, false);

  const unpinned = structuredClone(catalog);
  unpinned.models[0].commit = 'main';
  assert.equal(inspectCatalog(unpinned).ok, false);
});

test('mount loads only the same-origin candidate catalog and keeps all choices disabled', async () => {
  const documentRef = fakeDocument();
  let request;
  const mounted = await mount(documentRef, async (url, options) => {
    request = { url, options };
    return { ok: true, json: async () => catalog };
  });
  assert.equal(mounted, true);
  assert.equal(request.url, 'https://vespaguard.example/app/models/candidates.json');
  assert.equal(request.options.credentials, 'same-origin');
  assert.equal(request.options.redirect, 'error');
  assert.equal(documentRef.elements['camera-model'].disabled, false);
  assert.equal(documentRef.elements['camera-model'].value, '');
  assert.equal(documentRef.elements['camera-model'].children.length, 7);
  assert.ok(documentRef.elements['camera-model'].children.slice(1).every(option => option.disabled));
  assert.match(documentRef.elements['camera-model-status'].textContent, /6 externe Kandidaten/);
  assert.match(documentRef.elements['camera-model-active'].textContent, /Aktives Modell: keines/);
});

test('catalog fetch failure disables the selector and never reports an active model', async () => {
  const documentRef = fakeDocument();
  const mounted = await mount(documentRef, async () => { throw new Error('offline'); });
  assert.equal(mounted, false);
  assert.equal(documentRef.elements['camera-model'].disabled, true);
  assert.equal(documentRef.elements['camera-model'].children.length, 1);
  assert.match(documentRef.elements['camera-model-status'].textContent, /nicht verfügbar/);
  assert.match(documentRef.elements['camera-model-active'].textContent, /Aktives Modell: keines/);
});

test('missing UI elements do not trigger a catalog request', async () => {
  let requested = false;
  const result = await mount({ getElementById: () => null }, async () => { requested = true; });
  assert.equal(result, false);
  assert.equal(requested, false);
});
