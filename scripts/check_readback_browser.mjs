// Offline client playback checks. WAV is synthetic silence, not spoken AI output.
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
const { chromium } = createRequire(import.meta.url)(process.argv[2] || 'playwright');
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage();
page.setDefaultTimeout(4000);
const view = { draft_id: 'test-draft', revision: 1, content_hash: 'a'.repeat(64), proposal: { job_id: '104', diagnosis: 'motor fixed', status: 'completed' }, input: null, state: 'open', phase: 'review', can_confirm: true, can_cancel: true, can_retry: false, changed_fields: [], readback: 'Job 104: motor fixed. Kaam ho gaya. Confirm and save dabayein.', receipt: null, save_request: null };
const wav = Buffer.alloc(44 + 16000 * 2 * 3);
wav.write('RIFF', 0); wav.writeUInt32LE(wav.length - 8, 4); wav.write('WAVEfmt ', 8); wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(1, 22); wav.writeUInt32LE(16000, 24); wav.writeUInt32LE(32000, 28); wav.writeUInt16LE(2, 32); wav.writeUInt16LE(16, 34); wav.write('data', 36); wav.writeUInt32LE(wav.length - 44, 40);
let hold = false, release, fail = false, calls = 0;
const errors = []; page.on('pageerror', error => errors.push(error.message));
await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  if (path === '/api/jobs') return route.fulfill({ json: { jobs: [{ job_id: '104', appliance: 'Washing machine', customer_label: 'Demo Customer A' }], mode: 'fixtures', examples: [], speech: { readback: true } } });
  if (path.endsWith('/readback')) {
    calls++;
    assert.deepEqual(route.request().postDataJSON(), { revision: 1, content_hash: view.content_hash });
    if (fail) return route.fulfill({ json: { ok: false, code: 'speech_failed', message: 'Read-back could not be played. The text review is still available.', view } });
    if (hold) await new Promise(resolve => { release = resolve; });
    return route.fulfill({ contentType: 'audio/wav', body: wav });
  }
  return route.fulfill({ json: { ok: true, code: 'draft', view } });
});
try {
  await page.goto(process.argv[3] || 'http://127.0.0.1:8766');
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  await page.getByRole('button', { name: 'Listen to review', exact: true }).click();
  await page.getByRole('button', { name: 'Stop read-back', exact: true }).waitFor();
  assert.equal(await page.locator('#readback-text').textContent(), view.readback);
  await page.waitForFunction(() => !document.querySelector('#readback-audio').paused);
  await page.getByRole('button', { name: 'Open sidebar', exact: true }).click();
  assert.equal(await page.locator('#readback-audio').evaluate(audio => audio.paused), true);
  await page.getByRole('button', { name: 'Close sidebar', exact: true }).click();
  await page.getByRole('dialog', { name: 'Workspace' }).waitFor({ state: 'hidden' });
  assert.equal(await page.getByRole('button', { name: 'Stop read-back', exact: true }).isVisible(), false);
  await page.getByRole('button', { name: 'Listen to review', exact: true }).click();
  await page.waitForFunction(() => !document.querySelector('#readback-audio').paused);
  await page.getByLabel('Your update').fill('quantity correction');
  assert.equal(await page.locator('#readback-audio').evaluate(audio => audio.paused), true);
  await page.getByLabel('Your update').fill('');
  fail = true;
  await page.getByRole('button', { name: 'Listen to review', exact: true }).click();
  await page.getByText('Read-back could not be played. The text review is still available.', { exact: true }).waitFor();
  assert.equal(await page.getByRole('button', { name: 'Confirm and save', exact: true }).isEnabled(), true);
  fail = false; hold = true;
  await page.getByRole('button', { name: 'Listen to review', exact: true }).click();
  await page.getByText('Preparing read-back…', { exact: true }).waitFor();
  // Deliberately leave the response outstanding while the user changes the draft input.
  await page.getByLabel('Your update').fill('a newer correction');
  while (!release) await new Promise(resolve => setTimeout(resolve, 10));
  release();
  await page.waitForFunction(() => document.querySelector('#readback-audio').paused && !document.querySelector('#readback-audio').getAttribute('src'));
  assert.equal(calls, 4);
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  await page.screenshot({ path: 'artifacts/browser/readback-390.png', fullPage: true });
  assert.deepEqual(errors, []);
  console.log('PASS: synthetic read-back playback, text availability, stop on typing, failure keeps save usable, stale audio suppression, mobile layout. No provider requests.');
} finally { await browser.close(); }
