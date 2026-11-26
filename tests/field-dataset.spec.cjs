const {test, expect} = require('@playwright/test');
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const CLASS_SLUGS = [
  'vespa_velutina', 'vespa_crabro', 'other_vespidae',
  'apis_mellifera', 'bombus_spp', 'syrphidae', 'other_insect'
];

function extractStoredZip(buffer) {
  const endSignature = Buffer.from([0x50, 0x4b, 0x05, 0x06]);
  const endOffset = buffer.lastIndexOf(endSignature);
  expect(endOffset).toBeGreaterThanOrEqual(0);
  const count = buffer.readUInt16LE(endOffset + 10);
  let cursor = buffer.readUInt32LE(endOffset + 16);
  const files = new Map();
  for (let index = 0; index < count; index++) {
    expect(buffer.readUInt32LE(cursor)).toBe(0x02014b50);
    const size = buffer.readUInt32LE(cursor + 24);
    const nameLength = buffer.readUInt16LE(cursor + 28);
    const extraLength = buffer.readUInt16LE(cursor + 30);
    const commentLength = buffer.readUInt16LE(cursor + 32);
    const localOffset = buffer.readUInt32LE(cursor + 42);
    const name = buffer.toString('utf8', cursor + 46, cursor + 46 + nameLength);
    expect(buffer.readUInt32LE(localOffset)).toBe(0x04034b50);
    const localNameLength = buffer.readUInt16LE(localOffset + 26);
    const localExtraLength = buffer.readUInt16LE(localOffset + 28);
    const dataStart = localOffset + 30 + localNameLength + localExtraLength;
    files.set(name, buffer.subarray(dataStart, dataStart + size));
    cursor += 46 + nameLength + extraLength + commentLength;
  }
  return files;
}

async function addImage(page, name, bytes) {
  await page.locator('#field-dataset-photo').setInputFiles({
    name,
    mimeType: 'image/jpeg',
    buffer: Buffer.from(bytes)
  });
}

async function fillRights(page, {
  basis = 'LicenseRef-ExplicitPermission',
  source = 'Eigene Feldaufnahme',
  attribution = 'Example photographer (CC BY 4.0)',
  permissionRef = 'consent-record-test-001'
} = {}) {
  await page.locator('#field-rights-source').fill(source);
  await page.locator('#field-rights-basis').selectOption(basis);
  if (basis === 'CC-BY-4.0') {
    await page.locator('#field-rights-attribution').fill(attribution);
  }
  if (basis === 'LicenseRef-ExplicitPermission') {
    await page.locator('#field-rights-permission-ref').fill(permissionRef);
  }
}

async function attestEveryRecord(page) {
  const approval = page.getByRole('button', {name:'Manuelle Prüfung und Nutzungsattestierung speichern'});
  await expect(approval.first()).toBeVisible();
  while (await approval.count()) {
    const remaining = await approval.count();
    const row = approval.first().locator('xpath=../..');
    await row.getByRole('checkbox', {name:'Bildinhalt und sämtliche Klassen manuell geprüft'}).check();
    await row.getByRole('checkbox', {name:'Ich attestiere, dass ich das Bild für Trainingszwecke verwenden darf'}).check();
    page.once('dialog', dialog => dialog.accept());
    await approval.first().click();
    await expect(approval).toHaveCount(remaining - 1);
  }
}

test('stores multi-label and negative images locally and exports the reviewed contract', async ({page}) => {
  const requests = [];
  page.on('request', request => requests.push({url:request.url(), method:request.method()}));
  await page.goto('/');
  await expect(page.locator('#field-dataset-classes input[name="class-label"]')).toHaveCount(7);
  expect(await page.locator('#field-dataset-classes input[name="class-label"]').evaluateAll(inputs =>
    inputs.map(input => input.value)
  )).toEqual(CLASS_SLUGS);

  const positiveBytes = [0xff, 0xd8, 0xff, 0x11, 0x22, 0xff, 0xd9];
  await addImage(page, 'field-positive.jpg', positiveBytes);
  await page.locator('input[name="image-kind"][value="positive"]').check();
  await page.locator('input[name="class-label"][value="vespa_velutina"]').check();
  await page.locator('input[name="class-label"][value="apis_mellifera"]').check();
  await fillRights(page);
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-status')).toContainText('lokal gespeichert');
  await expect(page.locator('#field-dataset-summary')).toContainText('1 lokale Aufnahme');
  await expect(page.locator('#field-dataset-export')).toBeDisabled();
  const positiveRow = page.locator('.field-dataset-record').first();
  await positiveRow.getByRole('checkbox', {name:'Bildinhalt und sämtliche Klassen manuell geprüft'}).check();
  await positiveRow.getByRole('checkbox', {name:'Ich attestiere, dass ich das Bild für Trainingszwecke verwenden darf'}).check();
  page.once('dialog', dialog => dialog.accept());
  await positiveRow.getByRole('button', {name:'Manuelle Prüfung und Nutzungsattestierung speichern'}).click();
  await expect(page.locator('#field-dataset-summary')).toContainText('0 ohne abgeschlossene Nutzerprüfung');

  const negativeBytes = [0xff, 0xd8, 0xff, 0x33, 0x44, 0xff, 0xd9];
  await addImage(page, 'field-negative.jpg', negativeBytes);
  await page.locator('input[name="image-kind"][value="negative"]').check();
  await fillRights(page);
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-status')).toContainText('Noch ungeprüft');
  await expect(page.locator('#field-dataset-export')).toBeDisabled();
  await attestEveryRecord(page);
  await expect(page.locator('#field-dataset-export')).toBeEnabled();
  page.once('dialog', dialog => {
    expect(dialog.message()).toContain('EXIF-Metadaten');
    dialog.accept();
  });

  const downloadPromise = page.waitForEvent('download');
  await page.locator('#field-dataset-export').click();
  const download = await downloadPromise;
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const zipBuffer = Buffer.concat(chunks);
  if (process.env.BEEKEEPER_MULTILABEL_VALIDATOR) {
    const zipPath = path.join(os.tmpdir(), `beekeeper-monitor-${Date.now()}.zip`);
    fs.writeFileSync(zipPath, zipBuffer);
    const python = process.platform === 'win32' ? 'python' : 'python3';
    try {
      execFileSync(python, ['-c',
        'import importlib.util,sys; p=sys.argv[1]; s=importlib.util.spec_from_file_location("beekeeper_multilabel_dataset",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); rows=m.validate_dataset_archive(sys.argv[2]); assert len(rows)==2; assert rows[0]["labels"] or rows[1]["labels"]',
        process.env.BEEKEEPER_MULTILABEL_VALIDATOR, zipPath
      ], {stdio:'pipe', env:{...process.env, PYTHONDONTWRITEBYTECODE:'1'}});
    } finally {
      fs.unlinkSync(zipPath);
    }
  }
  const files = extractStoredZip(zipBuffer);
  expect([...files.keys()].filter(name => name.startsWith('images/'))).toHaveLength(2);
  const lines = files.get('annotations.jsonl').toString('utf8').trim().split('\n').map(line => JSON.parse(line));
  expect(lines).toHaveLength(2);
  const positive = lines.find(line => line.labels.length);
  const negative = lines.find(line => line.labels.length === 0);
  expect(positive.labels).toEqual(['vespa_velutina', 'apis_mellifera']);
  expect(negative.labels).toEqual([]);
  for (const line of lines) {
    expect(line).toMatchObject({
      captured_at: expect.stringMatching(/Z$/),
      capture_session_id: expect.any(String),
      review_status: 'approved',
      rights: {
        source:'Eigene Feldaufnahme',
        basis:'LicenseRef-ExplicitPermission',
        permission_ref:'consent-record-test-001',
        status:'training_approved'
      }
    });
    expect(line).not.toHaveProperty('location');
    expect(line).not.toHaveProperty('station_id');
    expect(files.has(line.image)).toBeTruthy();
  }
  expect(files.get(positive.image)).toEqual(Buffer.from(positiveBytes));
  expect(files.get(negative.image)).toEqual(Buffer.from(negativeBytes));
  expect(requests.some(request => request.method !== 'GET' && request.method !== 'HEAD')).toBeFalsy();
});

test('requires opaque pseudonymous labeler IDs and exports only the accepted format', async ({page}) => {
  await page.goto('/');
  await addImage(page, 'labeler-check.jpg', [0xff, 0xd8, 0xff, 0x31, 0xff, 0xd9]);
  await page.locator('input[name="image-kind"][value="negative"]').check();
  await fillRights(page);
  const labeler = page.locator('#field-labeler-id');
  for (const invalid of ['Simon Thomas', 'simon@example.org', 'https://example.org/reviewer']) {
    await labeler.fill(invalid);
    await page.locator('#field-dataset-form button[type="submit"]').click();
    await expect(page.locator('#field-dataset-status')).toContainText('reviewer:<opaque-id>');
    await expect(page.locator('#field-dataset-summary')).toContainText('0 lokale Aufnahmen');
  }
  await labeler.fill('reviewer:field-0001');
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-status')).toContainText('lokal gespeichert');
  await attestEveryRecord(page);
  await expect(page.locator('#field-dataset-export')).toBeEnabled();
  page.once('dialog', dialog => {
    expect(dialog.message()).toContain('EXIF-Metadaten');
    dialog.accept();
  });
  const downloadPromise = page.waitForEvent('download');
  await page.locator('#field-dataset-export').click();
  const download = await downloadPromise;
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const files = extractStoredZip(Buffer.concat(chunks));
  const lines = files.get('annotations.jsonl').toString('utf8').trim().split('\\n').map(line => JSON.parse(line));
  expect(lines).toHaveLength(1);
  expect(lines[0].labeler_id).toBe('reviewer:field-0001');
});

test('requires explicit EXIF metadata confirmation before ZIP export', async ({page}) => {
  await page.goto('/');
  await addImage(page, 'privacy-check.jpg', [0xff, 0xd8, 0xff, 0x21, 0xff, 0xd9]);
  await page.locator('input[name="image-kind"][value="negative"]').check();
  await fillRights(page);
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-summary')).toContainText('1 lokale Aufnahme');
  await attestEveryRecord(page);
  await expect(page.locator('#field-dataset-summary')).toContainText('0 ohne abgeschlossene Nutzerprüfung');
  await expect(page.locator('#field-dataset-export')).toBeEnabled();
  page.once('dialog', dialog => {
    expect(dialog.message()).toContain('EXIF-Metadaten');
    dialog.dismiss();
  });
  await page.locator('#field-dataset-export').click();
  await expect(page.locator('#field-dataset-status')).toContainText('Export abgebrochen');
});

test('requires an explicit image kind and at least one class for positive images', async ({page}) => {
  await page.goto('/');
  await addImage(page, 'unlabelled.jpg', [0xff, 0xd8, 0xff, 0xd9]);
  await page.locator('input[name="image-kind"][value="positive"]').check();
  await fillRights(page);
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-status')).toContainText('mindestens eine Klasse auswählen');
  await expect(page.locator('#field-dataset-summary')).toContainText('0 lokale Aufnahmen');
  await expect(page.locator('#field-dataset-export')).toBeDisabled();
});

test('rejects HEIC and exposes the structured bounded rights fields', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#field-rights-source')).toHaveAttribute('required', '');
  await expect(page.locator('#field-rights-source')).toHaveAttribute('maxlength', '200');
  await expect(page.locator('#field-rights-basis')).toHaveAttribute('required', '');
  await expect(page.locator('#field-rights-attribution')).toHaveAttribute('maxlength', '500');
  await expect(page.locator('#field-rights-permission-ref')).toHaveAttribute('maxlength', '200');
  await page.locator('#field-dataset-photo').setInputFiles({
    name:'iphone-photo.heic', mimeType:'image/heic', buffer:Buffer.from([1,2,3])
  });
  await page.locator('input[name="image-kind"][value="negative"]').check();
  await fillRights(page);
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-status')).toContainText('JPEG-, PNG- oder WebP-Bild');
  await expect(page.locator('#field-dataset-summary')).toContainText('0 lokale Aufnahmen');
});


test('exports canonical CC-BY evidence and required attribution', async ({page}) => {
  await page.goto('/');
  await addImage(page, 'cc-by-photo.jpg', [0xff, 0xd8, 0xff, 0x51, 0xff, 0xd9]);
  await page.locator('input[name="image-kind"][value="negative"]').check();
  await fillRights(page, {
    basis:'CC-BY-4.0',
    source:'https://example.org/photos/cc-by-photo',
    attribution:'Example photographer (CC BY 4.0)'
  });
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-summary')).toContainText('1 lokale Aufnahme');
  await attestEveryRecord(page);
  await expect(page.locator('#field-dataset-export')).toBeEnabled();
  page.once('dialog', dialog => dialog.accept());
  const downloadPromise = page.waitForEvent('download');
  await page.locator('#field-dataset-export').click();
  const download = await downloadPromise;
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const files = extractStoredZip(Buffer.concat(chunks));
  const [row] = files.get('annotations.jsonl').toString('utf8').trim().split('\\n').map(JSON.parse);
  expect(row.rights).toMatchObject({
    source:'https://example.org/photos/cc-by-photo',
    basis:'CC-BY-4.0',
    evidence_url:'https://creativecommons.org/licenses/by/4.0/',
    attribution:'Example photographer (CC BY 4.0)',
    status:'training_approved'
  });
  expect(row.rights).not.toHaveProperty('publication_allowed');
});

test('exports the canonical CC0 evidence URL without adding publication permission', async ({page}) => {
  await page.goto('/');
  await addImage(page, 'cc0-photo.jpg', [0xff, 0xd8, 0xff, 0x61, 0xff, 0xd9]);
  await page.locator('input[name="image-kind"][value="negative"]').check();
  await fillRights(page, {basis:'CC0-1.0', source:'Eigene Feldaufnahme'});
  await page.locator('#field-dataset-form button[type="submit"]').click();
  await expect(page.locator('#field-dataset-status')).toContainText('lokal gespeichert');
  await expect(page.locator('#field-dataset-summary')).toContainText('1 lokale Aufnahme');
  await attestEveryRecord(page);
  await expect(page.locator('#field-dataset-export')).toBeEnabled();
  page.once('dialog', dialog => dialog.accept());
  const downloadPromise = page.waitForEvent('download');
  await page.locator('#field-dataset-export').click();
  const download = await downloadPromise;
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const files = extractStoredZip(Buffer.concat(chunks));
  const [row] = files.get('annotations.jsonl').toString('utf8').trim().split('\\n').map(JSON.parse);
  expect(row.rights).toMatchObject({
    source:'Eigene Feldaufnahme',
    basis:'CC0-1.0',
    evidence_url:'https://creativecommons.org/publicdomain/zero/1.0/',
    status:'training_approved'
  });
  expect(row.rights).not.toHaveProperty('publication_allowed');
});

test('rejects source URLs that may carry credentials or tracking/query data', async ({page}) => {
  await page.goto('/');
  await addImage(page, 'invalid-source.jpg', [0xff, 0xd8, 0xff, 0x71, 0xff, 0xd9]);
  await page.locator('input[name="image-kind"][value="negative"]').check();
  for (const source of [
    'http://example.org/photo',
    'https://user:password@example.org/photo',
    'https://example.org/photo?token=example',
    'https://example.org/photo#private'
  ]) {
    await fillRights(page, {source});
    await page.locator('#field-dataset-form button[type="submit"]').click();
    await expect(page.locator('#field-dataset-status')).toContainText('HTTPS-Adresse ohne Zugangsdaten, Query oder Fragment');
    await expect(page.locator('#field-dataset-summary')).toContainText('0 lokale Aufnahmen');
  }
});

test('blocks export when the same image bytes were captured twice', async ({page}) => {
  await page.goto('/');
  const bytes = [0xff, 0xd8, 0xff, 0x31, 0xff, 0xd9];
  for (const name of ['copy-one.jpg', 'copy-two.jpg']) {
    await addImage(page, name, bytes);
    await page.locator('input[name="image-kind"][value="negative"]').check();
    await fillRights(page);
    await page.locator('#field-dataset-form button[type="submit"]').click();
    await expect(page.locator('#field-dataset-summary')).toContainText(name === 'copy-one.jpg' ? '1 lokale Aufnahme' : '2 lokale Aufnahmen');
  }
  await attestEveryRecord(page);
  await expect(page.locator('#field-dataset-export')).toBeEnabled();
  page.once('dialog', dialog => dialog.accept());
  await page.locator('#field-dataset-export').click();
  await expect(page.locator('#field-dataset-status')).toContainText('derselbe Bildinhalt wurde mehrfach erfasst');
});
