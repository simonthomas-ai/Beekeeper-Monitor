const {test, expect} = require('@playwright/test');

test('live media starts inactive and requires explicit clicks', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#live-media-status')).toContainText('ausgeschaltet');
  await expect(page.locator('#mic-level')).toHaveJSProperty('value', 0);
  await expect(page.locator('#live-camera')).toHaveJSProperty('srcObject', null);
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
