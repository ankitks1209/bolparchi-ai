// Real local HTTP + SQLite; only extraction uses the server's explicit fixtures.
// Intercept one save response AFTER the real server commits to exercise recovery.
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
const require = createRequire(import.meta.url);
const { chromium } = require(process.argv[2] || process.env.BOLPARCHI_PLAYWRIGHT || 'playwright');
const base = process.argv[3] || process.env.BOLPARCHI_BROWSER_URL || 'http://127.0.0.1:8766';
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage();
const errors = [], delivered = [];
page.on('pageerror', error => errors.push(error.message));
page.setDefaultTimeout(8000);
try {
  await page.goto(base);
  await page.getByText('Offline fixture mode · Scripted extraction, real local records. No AI requests.', { exact: true }).waitFor();
  // Keyboard enters the actual selected job rather than a scripted client state.
  await page.getByRole('button', { name: 'Start update', exact: true }).focus();
  await page.keyboard.press('Enter');
  for (const message of ['Motor kharab. Do motor chahiye. Kaam pending hai.', 'Kal shaam aana hai.', 'Do nahi, ek motor.']) {
    await page.getByLabel('Your update').fill(message);
    await page.getByRole('button', { name: 'Review update', exact: true }).click();
    await page.waitForFunction(() => !document.querySelector('#message').disabled && document.querySelector('#message').value === '');
  }
  assert.equal(await page.locator('[data-field="quantity"] .value').textContent(), '1');
  assert.equal(await page.locator('[data-field="follow_up"] .value').textContent(), 'kal shaam');
  await mkdir('artifacts/browser', { recursive: true });
  await page.screenshot({ path: 'artifacts/browser/real-update-desktop.png', fullPage: true });
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.screenshot({ path: `artifacts/browser/real-update-${width}.png`, fullPage: true });
  }
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.route('**/api/drafts/*/save', async route => {
    delivered.push(route.request().postDataJSON());
    const response = await route.fetch();
    assert.equal(response.status(), 200);
    assert.equal((await response.json()).code, 'saved');
    await route.abort('failed');
  });
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByRole('button', { name: 'Check save status', exact: true }).waitFor();
  assert.equal(await page.getByLabel('Your update').isDisabled(), true);
  assert.equal(await page.getByText('Saved to this device', { exact: true }).isVisible(), false);
  await page.reload();
  await page.getByText('Saved to this device', { exact: true }).waitFor();
  assert.equal(delivered.length, 1, 'Refresh looked up the stored receipt without another save');
  assert.equal(await page.locator('#receipt-id').textContent(), delivered[0].submission_id);
  await page.screenshot({ path: 'artifacts/browser/real-saved.png', fullPage: true });
  await page.unroute('**/api/drafts/*/save');
  await page.getByRole('button', { name: 'Choose another job', exact: true }).click();
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  for (const message of ['Motor kharab. Do motor chahiye. Kaam pending hai.', 'Kal shaam aana hai.']) {
    await page.getByLabel('Your update').fill(message);
    await page.getByRole('button', { name: 'Review update', exact: true }).click();
    await page.waitForFunction(() => !document.querySelector('#message').disabled && document.querySelector('#message').value === '');
  }
  let firstAttempt = true;
  const repeated = [];
  await page.route('**/api/drafts/*/save', async route => {
    repeated.push(route.request().postDataJSON());
    if (firstAttempt) { firstAttempt = false; return route.abort('failed'); }
    await route.continue();
  });
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByRole('button', { name: 'Check save status', exact: true }).click();
  await page.getByRole('button', { name: 'Retry same save', exact: true }).click({ timeout: 3000 });
  await page.getByText('Saved to this device', { exact: true }).waitFor();
  assert.equal(repeated.length, 2);
  assert.deepEqual(repeated[1], repeated[0], 'A request lost before arrival is retried with the same submission and review');
  assert.deepEqual(errors, []);
  console.log('PASS: real local HTTP + SQLite typed correction to explicit save; committed response dropped, receipt recovered on refresh, no second save delivery; keyboard entry and 1280/390/320 captures. Extraction fixtures only.');
} finally { await browser.close(); }
