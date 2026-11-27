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
