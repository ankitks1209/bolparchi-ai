// Native synthetic microphone + real local HTTP/SQLite. Server speech/extraction are fixtures.
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
const { chromium } = createRequire(import.meta.url)(process.argv[2] || 'playwright');
const base = process.argv[3] || 'http://127.0.0.1:8766';
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'] });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, permissions: ['microphone'] });
const page = await context.newPage(); page.setDefaultTimeout(8000);
const errors = [], saves = [];
page.on('pageerror', error => errors.push(error.message));
page.on('request', request => { if (new URL(request.url()).pathname.endsWith('/save')) saves.push(request.postDataJSON()); });
try {
  await page.goto(base);
  await page.getByText('Offline fixture mode · Scripted extraction, real local records. No AI requests.', { exact: true }).waitFor();
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  await page.getByRole('button', { name: 'Record update', exact: true }).click();
  await page.getByText('Recording…', { exact: true }).waitFor();
  await page.waitForFunction(() => document.querySelector('#record-time').textContent !== '0:00 / 0:30');
  const received = page.waitForResponse(response => new URL(response.url()).pathname.endsWith('/audio'));
  await page.getByRole('button', { name: 'Stop and review', exact: true }).click();
  const response = await received, recorded = (await response.json()).view;
  assert.equal(response.status(), 200);
  assert.equal(recorded.input.transcript, 'Motor kharab. Do motor chahiye. Kaam pending hai.');
  assert.equal(recorded.phase, 'clarify');
  assert.equal(recorded.receipt, null);
  const path = `/api/drafts/${recorded.draft_id}`;
  for (const message of ['Kal shaam aana hai.', 'Do nahi, ek motor.']) {
    await page.getByLabel('Your update').fill(message);
    await page.getByRole('button', { name: 'Review update', exact: true }).click();
    await page.waitForFunction(() => !document.querySelector('#message').disabled && document.querySelector('#message').value === '');
  }
  assert.equal(await page.locator('[data-field="quantity"] .value').textContent(), '1');
  assert.equal(await page.locator('[data-field="follow_up"] .value').textContent(), 'kal shaam');
  await page.getByRole('button', { name: 'Listen to review', exact: true }).click();
  await page.getByText('Playing a fixture test tone.', { exact: true }).waitFor();
  await page.waitForFunction(() => !document.querySelector('#readback-audio').paused);
  await page.getByRole('button', { name: 'Stop read-back', exact: true }).click();
  assert.equal(await page.locator('#readback-audio').evaluate(audio => audio.paused), true);
  const reviewed = (await (await context.request.get(base + path)).json()).view;
  assert.equal(reviewed.state, 'open'); assert.equal(reviewed.receipt, null);
  assert.equal(saves.length, 0, 'Recording, extraction and listening never send a save');
  await mkdir('artifacts/browser', { recursive: true });
  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.screenshot({ path: `artifacts/browser/voice-real-${width}.png`, fullPage: true });
  }
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByText('Saved to this device', { exact: true }).waitFor();
  const saved = (await (await context.request.get(base + path)).json()).view;
  assert.equal(saved.state, 'saved'); assert.equal(saved.proposal.quantity, 1);
  assert.equal(saved.receipt.submission_id, saves[0].submission_id); assert.equal(saves.length, 1);
  await page.screenshot({ path: 'artifacts/browser/voice-real-saved.png', fullPage: true });
  assert.deepEqual(errors, []);
  console.log('PASS: native synthetic microphone → real WAV HTTP upload → fixture STT/extraction → clarification/correction → real test-tone playback → explicit save and SQLite receipt. No automatic save, no provider requests; 1280/390/320 captures.');
} finally { await browser.close(); }
