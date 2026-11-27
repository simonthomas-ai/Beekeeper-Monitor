const { test, expect } = require('@playwright/test');

test('camera model selector lists candidates but none can be activated', async ({ page }) => {
  await page.goto('/');
  const selector = page.locator('#camera-model');
  await expect(selector).toBeVisible();
  await expect(page.locator('#camera-model-active')).toContainText('Aktives Modell: keines');
  await expect(page.locator('#camera-model-status')).toContainText('6 externe Kandidaten');
  const options = await selector.locator('option').evaluateAll(items =>
    items.map(item => ({ value: item.value, disabled: item.disabled }))
  );
  expect(options).toHaveLength(7);
  expect(options.slice(1).every(item => item.disabled)).toBe(true);
  await expect(selector).toHaveValue('');
});

test('camera model selector fails closed when the local catalog is unavailable', async ({ page }) => {
  await page.route('**/models/candidates.json', route => route.abort());
  await page.goto('/');
  await expect(page.locator('#camera-model')).toBeDisabled();
  await expect(page.locator('#camera-model-status')).toContainText('nicht verfügbar');
  await expect(page.locator('#camera-model-active')).toContainText('Aktives Modell: keines');
});

test('selector never fetches weights, remote runtime code or station/outbox events', async ({ page }) => {
  const requests = [];
  page.on('request', request => requests.push(new URL(request.url())));
  await page.goto('/');
  const selector = page.locator('#camera-model');
  await expect(page.locator('#camera-model-status')).toContainText('6 externe Kandidaten');

  const attemptedSelection = await selector.evaluate(element => {
    const candidate = [...element.options].find(option => option.value === 'hornet3000-yolov8s-onnx');
    if (!candidate) return { found: false, disabled: false };
    element.value = candidate.value;
    element.dispatchEvent(new Event('change', { bubbles: true }));
    return { found: true, disabled: candidate.disabled };
  });
  expect(attemptedSelection).toEqual({ found: true, disabled: true });
  await expect(page.locator('#camera-model-active')).toContainText('Aktives Modell: keines');
  await expect(page.locator('#station-events-status')).toContainText('Nicht verbunden');
  await expect(page.locator('#station-events-list li')).toHaveCount(0);

  const forbidden = requests.filter(url =>
    /\.(?:onnx|pt|wasm)(?:$|[?#])/i.test(url.pathname + url.search) ||
    /camera-onnx-runtime|hornet-onnx-decoder|\/api\/v1\/events|outbox/i.test(url.pathname)
  );
  expect(forbidden).toHaveLength(0);
  expect(requests.every(url => url.origin === 'http://127.0.0.1:8765')).toBe(true);
});
