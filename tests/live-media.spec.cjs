const {test, expect} = require('@playwright/test');

test('live media starts inactive and requires explicit clicks', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#live-media-status')).toContainText('ausgeschaltet');
  await expect(page.locator('#mic-level')).toHaveJSProperty('value', 0);
  await expect(page.locator('#live-camera')).toHaveJSProperty('srcObject', null);
});

test('all AI models remain visibly unavailable and no inference runtime is loaded', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#ai-readiness-status')).toContainText('KI-Erkennung: NICHT SCHARF');
  await expect(page.locator('#ai-readiness-status')).toContainText('kein freigegebenes Modellgewicht');
  await expect(page.locator('#modellstatus .modellkarten article')).toHaveCount(7);
  await expect(page.locator('#live-media')).not.toContainText('Kamera-KI starten');
  expect(await page.locator('script[src]').evaluateAll(scripts =>
    scripts.map(script => script.getAttribute('src'))
  )).not.toContain('./camera-onnx-runtime.js');
  expect(await page.locator('#live-media-status').textContent()).toContain('ausgeschaltet');
});

test('camera preview requests rear camera and stops every track', async ({page}) => {
  await page.addInitScript(() => {
    window.__mediaCalls = [];
    window.__stoppedTracks = 0;
    const track = {stop: () => { window.__stoppedTracks++; }, readyState: 'live'};
    const stream = {getTracks: () => [track]};
    Object.defineProperty(navigator, 'mediaDevices', {configurable:true, value:{
      getUserMedia: async constraints => { window.__mediaCalls.push(constraints); return stream; }
    }});
    Object.defineProperty(HTMLMediaElement.prototype, 'srcObject', {
      configurable:true, get() { return this.__stream || null; },
      set(value) { this.__stream = value; }
    });
    HTMLMediaElement.prototype.play = async function() {};
  });
  await page.goto('/');
  await page.locator('#start-camera').click();
  await expect(page.locator('#live-media-status')).toContainText('Kamera-Vorschau aktiv');
  expect(await page.evaluate(() => window.__mediaCalls)).toEqual([{video:{facingMode:{ideal:'environment'}},audio:false}]);
  await page.locator('#stop-media').click();
  await expect(page.locator('#live-media-status')).toContainText('ausgeschaltet');
  expect(await page.evaluate(() => window.__stoppedTracks)).toBe(1);
  await expect(page.locator('#live-camera')).toHaveJSProperty('srcObject', null);
});

test('shadow snapshot is explicit, unclassified and stored locally without inference', async ({page}) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'mediaDevices', {configurable:true, value:{
      getUserMedia: async () => ({getTracks: () => [{stop() {}}]})
    }});
    Object.defineProperty(HTMLMediaElement.prototype, 'srcObject', {
      configurable:true, get() { return this.__stream || null; },
      set(value) { this.__stream = value; }
    });
    Object.defineProperty(HTMLVideoElement.prototype, 'videoWidth', {configurable:true, get:() => 640});
    Object.defineProperty(HTMLVideoElement.prototype, 'videoHeight', {configurable:true, get:() => 480});
    Object.defineProperty(HTMLVideoElement.prototype, 'readyState', {configurable:true, get:() => 4});
    HTMLMediaElement.prototype.play = async function() {};
    HTMLCanvasElement.prototype.getContext = () => ({drawImage() {}});
    HTMLCanvasElement.prototype.toBlob = callback => callback(new Blob(
      [new Uint8Array([0xff, 0xd8, 0xff, 0xd9])], {type:'image/jpeg'}
    ));
  });
  await page.goto('/');
  await page.waitForFunction(() => window.BeekeeperLiveMedia?.ready === true);
  await expect(page.locator('#capture-shadow-frame')).toBeDisabled();
  await page.locator('#start-camera').click();
  await expect(page.locator('#capture-shadow-frame')).toBeEnabled();
  await page.locator('#capture-shadow-frame').click();
  await expect(page.locator('#camera-shadow-status')).toContainText('Einzelbild bereit');
  await expect(page.locator('#observation-type')).toHaveValue('Kamera-Shadow-Test (nicht bestimmt)');
  await expect.poll(() => page.locator('#photo').evaluate(input => input.files.length)).toBe(1);
  await expect(page.locator('#ai-readiness-status')).toContainText('KI-Erkennung: NICHT SCHARF');
  await page.getByRole('button', {name:'Auf diesem Gerät speichern'}).click();
  await expect(page.locator('#status')).toContainText('lokal gespeichert');
  const saved = await page.evaluate(() => new Promise(resolve => {
    const request = indexedDB.open('beekeeper-monitor-v2');
    request.onsuccess = () => {
      const db = request.result;
      const rows = db.transaction('observations', 'readonly').objectStore('observations').getAll();
      rows.onsuccess = () => { resolve(rows.result[0]); db.close(); };
    };
  }));
  expect(saved.type).toBe('Kamera-Shadow-Test (nicht bestimmt)');
  expect(saved.photo.type).toBe('image/jpeg');
  expect(saved.photo.content).toMatch(/^data:image\/jpeg;base64,/);
  expect(saved.location).toBeUndefined();
});

test('denied camera permission is reported without active preview', async ({page}) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'mediaDevices', {configurable:true, value:{
      getUserMedia: async () => { throw new DOMException('denied', 'NotAllowedError'); }
    }});
  });
  await page.goto('/');
  await page.locator('#start-camera').click();
  await expect(page.locator('#live-media-status')).toContainText('Freigabe abgelehnt');
  await expect(page.locator('#start-camera')).toBeEnabled();
  await expect(page.locator('#live-camera')).toHaveJSProperty('srcObject', null);
});

test('microphone meter uses local analyzer and stops its track', async ({page}) => {
  await page.addInitScript(() => {
    window.__micStopped = 0;
    window.__audioClosed = 0;
    const track = {stop: () => { window.__micStopped++; }};
    Object.defineProperty(navigator, 'mediaDevices', {configurable:true, value:{
      getUserMedia: async () => ({getTracks: () => [track]})
    }});
    class FakeAudioContext {
      createMediaStreamSource() { return {connect() {}}; }
      createAnalyser() { return {fftSize:1024, getByteTimeDomainData(data) { data.fill(128); }}; }
      async close() { window.__audioClosed++; }
    }
    window.AudioContext = FakeAudioContext;
  });
  await page.goto('/');
  await page.locator('#start-mic').click();
  await expect(page.locator('#live-media-status')).toContainText('Mikrofon-Pegel aktiv');
  await page.locator('#stop-media').click();
  await expect(page.locator('#live-media-status')).toContainText('ausgeschaltet');
  expect(await page.evaluate(() => [window.__micStopped, window.__audioClosed])).toEqual([1,1]);
});

test('microphone denial leaves no active level', async ({page}) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'mediaDevices', {configurable:true, value:{
      getUserMedia: async () => { throw new DOMException('denied', 'NotAllowedError'); }
    }});
  });
  await page.goto('/');
  await page.locator('#start-mic').click();
  await expect(page.locator('#live-media-status')).toContainText('Freigabe abgelehnt');
  await expect(page.locator('#mic-level')).toHaveJSProperty('value', 0);
});
