// Opt-in real Gemini → browser review/correction → explicit local SQLite save.
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';

const [playwrightPath, optIn, base] = process.argv.slice(2);
if (optIn !== '--live' || !/^http:\/\/127\.0\.0\.1:\d+$/.test(base || '')) {
  throw new Error('Usage: node scripts/check_live_typed.mjs PLAYWRIGHT --live http://127.0.0.1:PORT');
}
const { chromium } = createRequire(import.meta.url)(playwrightPath);
const directory = `artifacts/live-typed/${new Date().toISOString().replaceAll(':', '-')}`;
await mkdir(directory, { recursive: true });
const report = { source: 'typed_fictional_messages', providers: 'live_gemini', steps: [], outcome: 'started' };
const checkpoint = () => writeFile(`${directory}/report.json`, JSON.stringify(report, null, 2) + '\n');
await checkpoint();
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage(); page.setDefaultTimeout(45000);
const errors = [], saves = [];
page.on('pageerror', error => errors.push(error.message));
page.on('request', r => { if (new URL(r.url()).pathname.endsWith('/save')) saves.push(r.postDataJSON()); });
try {
  await page.goto(base);
  assert.equal((await (await context.request.get(`${base}/api/jobs`)).json()).mode, 'live');
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  let draft;
  for (const [message, phase, quantity] of [
    ['Motor kharab. Do motor chahiye. Kaam pending hai.', 'clarify', 2],
    ['Kal shaam aana hai.', 'review', 2],
    ['Do nahi, ek motor.', 'review', 1],
  ]) {
    if (draft) await new Promise(resolve => setTimeout(resolve, 16000));
    await page.getByLabel('Your update').fill(message);
    const answer = page.waitForResponse(r => new URL(r.url()).pathname.endsWith('/message'));
    const started = Date.now();
    await page.getByRole('button', { name: 'Review update', exact: true }).click();
    const response = await answer;
    draft = (await response.json()).view;
    report.steps.push({ message, seconds: (Date.now() - started) / 1000, view: draft }); await checkpoint();
    assert.equal(response.status(), 200); assert.equal(draft.phase, phase);
    assert.equal(draft.proposal.quantity, quantity); assert.equal(draft.proposal.status, 'pending');
    assert.match(draft.proposal.part_needed, /motor|मोटर/i);
    assert.equal(draft.receipt, null); assert.equal(saves.length, 0);
    assert.equal(draft.can_confirm, phase === 'review');
  }
  assert.ok(draft.proposal.diagnosis && draft.proposal.follow_up);
  await page.waitForFunction(() => !document.querySelector('#save').disabled);
  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.screenshot({ path: `${directory}/review-${width}.png`, fullPage: true });
  }
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByText('Saved to this device', { exact: true }).waitFor();
  const path = `${base}/api/drafts/${draft.draft_id}`;
  const saved = (await (await context.request.get(path)).json()).view;
  assert.equal(saved.state, 'saved'); assert.equal(saved.proposal.quantity, 1);
  assert.equal(saves.length, 1); assert.equal(saved.receipt.submission_id, saves[0].submission_id);
  for (const width of [1280, 390]) {
    await page.setViewportSize({ width, height: 900 });
    await page.screenshot({ path: `${directory}/saved-${width}.png`, fullPage: true });
  }
  await page.reload();
  const reopened = (await (await context.request.get(path)).json()).view;
  assert.deepEqual(reopened.receipt, saved.receipt); assert.equal(saves.length, 1);
  assert.deepEqual(errors, []);
  report.steps.push({ step: 'saved_receipt_survives_refresh', view: saved });
  report.outcome = 'passed'; await checkpoint();
  console.log(`PASS live Gemini → clarification → correction → explicit SQLite receipt; 3 extraction requests. Evidence: ${directory}`);
} catch (error) {
  report.outcome = 'failed'; report.failure = String(error.message).slice(0, 1000); await checkpoint();
  await page.screenshot({ path: `${directory}/failure.png`, fullPage: true }).catch(() => {});
  throw error;
} finally { await browser.close(); }
