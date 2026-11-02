// Offline browser checks: HTTP fixtures exercise the client, not extraction quality.
// Use an existing Playwright installation; this script installs nothing.
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
const require = createRequire(import.meta.url);
const { chromium } = require(process.argv[2] || process.env.BOLPARCHI_PLAYWRIGHT || 'playwright');
const base = process.argv[3] || process.env.BOLPARCHI_BROWSER_URL || 'http://127.0.0.1:8766';
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(error.message));
const jobs = [{ job_id: '104', appliance: 'Washing machine', customer_label: 'Demo Customer A', status: 'open' }];
const examples = ['Motor kharab. Do motor chahiye. Kaam pending hai.', 'Kal shaam aana hai.', 'Do nahi, ek motor.'];
let draft;
let saveCalls = [];
let loseSave = false;
let failExtraction = false;
let failJobs = false;
let emptyJobs = false;
let pendingReceipt = false;
let rejectSave = false;
let holdMessage = false;
let releaseMessage;
let loseBeforeSave = false;
function initial() {
  return { draft_id: 'browser-draft', revision: 1, content_hash: 'a'.repeat(64), proposal: { job_id: '104' }, input: null, state: 'open', phase: 'clarify', question: 'Kya problem mili?', readback: null, can_confirm: false, can_retry: false, can_cancel: true, changed_fields: [], receipt: null, save_request: null };
}
const result = (code = 'draft', ok = true, data = {}) => ({ ok, code, message: code, data, view: structuredClone(draft) });
await page.route('**/api/**', async route => {
  const request = route.request();
  const path = new URL(request.url()).pathname;
  const body = request.postDataJSON() || {};
  let response;
  if (path === '/api/jobs') {
    if (failJobs) return route.abort('failed');
    response = { jobs: emptyJobs ? [] : jobs, mode: 'fixtures', examples };
  } else if (path === '/api/drafts') {
    draft = initial(); response = result('created');
  } else if (path.endsWith('/message') || path.endsWith('/retry')) {
    const message = body.message || draft.input.transcript;
    draft.input = { turn_id: `turn-${draft.revision}`, transcript: message, state: 'applied', patch: null };
    draft.can_retry = false;
    if (failExtraction) {
      draft.phase = 'extraction_error'; draft.can_retry = true; draft.can_confirm = false;
      draft.input.state = 'error'; response = result('extraction_failed', false);
    } else if (message.includes('105')) {
      draft.input.patch = { spoken_job_id: '105' }; draft.input.state = 'mismatch';
      draft.phase = 'job_mismatch'; draft.can_confirm = false;
      draft.question = 'Message mein job 105 hai. Selected job 104 par lagayein ya message hata dein?';
      response = result('mismatch');
    } else {
      let changes = message === examples[0] ? { diagnosis: 'motor kharab', status: 'pending', part_needed: 'motor', quantity: 2 } : message === examples[1] ? { follow_up: 'kal shaam' } : { quantity: 1 };
      Object.assign(draft.proposal, changes); draft.changed_fields = Object.keys(changes);
      draft.revision++; draft.content_hash = String(draft.revision).repeat(64);
      draft.can_confirm = Boolean(draft.proposal.follow_up);
      draft.phase = draft.can_confirm ? 'review' : 'clarify';
      draft.question = draft.can_confirm ? null : 'Follow-up kab karna hai?';
      draft.readback = draft.can_confirm ? 'Job 104. Motor kharab. Ek motor chahiye. Kaam pending. Kal shaam.' : null;
      response = result('updated');
    }
  } else if (path.endsWith('/mismatch')) {
    assert.equal(body.action, 'discard'); draft.phase = 'review'; draft.can_confirm = true;
    draft.input.state = 'discarded'; draft.question = null; response = result('discarded');
  } else if (path.endsWith('/save')) {
    if (rejectSave) {
      rejectSave = false;
      return route.fulfill({ json: result('stale_confirmation', false) });
    }
    saveCalls.push(body);
    if (loseBeforeSave) return route.abort('failed');
    assert.equal(body.revision, draft.revision);
    assert.equal(body.content_hash, draft.content_hash);
    draft.state = pendingReceipt ? 'save_unresolved' : 'saved'; draft.phase = draft.state;
    draft.can_confirm = false; draft.can_cancel = false;
    draft.save_request = { submission_id: body.submission_id, attempts: 1 };
    if (!pendingReceipt) draft.receipt = { submission_id: body.submission_id, proposal: structuredClone(draft.proposal), saved_at: '2026-10-29T10:00:00+00:00' };
    if (loseSave) return route.abort('failed');
    response = result(pendingReceipt ? 'unresolved' : 'saved', !pendingReceipt, { receipt: draft.receipt });
  } else if (path.endsWith('/save-status')) {
    const hasReceipt = Boolean(draft.receipt) && !pendingReceipt;
    response = result(hasReceipt ? 'saved' : 'unresolved', hasReceipt, { receipt: draft.receipt });
  } else if (path.endsWith('/cancel')) {
    draft.state = 'cancelled'; draft.phase = 'cancelled'; draft.can_cancel = false;
    response = result('cancelled');
  } else response = result();
  if (holdMessage && path.endsWith('/message')) await new Promise(resolve => { releaseMessage = resolve; });
  await route.fulfill({ json: response });
});
try {
  await page.goto(base);
  await page.getByRole('button', { name: 'Start update', exact: true }).click({ timeout: 3000 });
  await page.getByLabel('Your update').fill(examples[0]);
  await page.getByRole('button', { name: 'Review update', exact: true }).click();
  await page.getByText('Follow-up kab karna hai?', { exact: true }).waitFor();
  assert.equal(saveCalls.length, 0);
  assert.equal(await page.getByRole('button', { name: 'Confirm and save', exact: true }).isEnabled(), false);
  await page.getByLabel('Your update').fill(examples[1]);
  await page.getByRole('button', { name: 'Review update', exact: true }).click();
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).waitFor();
  await page.getByLabel('Your update').fill(examples[2]);
  assert.equal(await page.getByRole('button', { name: 'Confirm and save', exact: true }).isEnabled(), false, 'Unsubmitted corrections block saving the previous review');
  await page.getByRole('button', { name: 'Review update', exact: true }).click();
  await page.locator('[data-field="quantity"] .value').getByText('1', { exact: true }).waitFor();
  assert.equal(saveCalls.length, 0);
  await mkdir('artifacts/browser', { recursive: true });
  await page.screenshot({ path: 'artifacts/browser/update-desktop.png', fullPage: true });
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `No overflow at ${width}`);
    await page.screenshot({ path: `artifacts/browser/update-${width}.png`, fullPage: true });
  }
  await page.setViewportSize({ width: 1280, height: 900 });
  failExtraction = true;
  await page.getByLabel('Your update').fill('Motor correction');
  await page.getByRole('button', { name: 'Review update', exact: true }).click();
  await page.getByRole('button', { name: 'Retry extraction', exact: true }).waitFor();
  assert.equal(await page.locator('#transcript').textContent(), 'Motor correction');
  failExtraction = false;
  await page.getByRole('button', { name: 'Retry extraction', exact: true }).click();
  await page.getByLabel('Your update').fill('Job 105');
  await page.getByRole('button', { name: 'Review update', exact: true }).click();
  await page.getByRole('button', { name: 'Discard message', exact: true }).click();
  rejectSave = true;
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByText('The server rejected this save. Review the latest record before confirming again.', { exact: true }).waitFor({ timeout: 3000 });
  assert.equal(await page.getByRole('button', { name: 'Confirm and save', exact: true }).isEnabled(), true);
  assert.equal(await page.getByLabel('Your update').isEnabled(), true);
  loseSave = true; pendingReceipt = true;
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByRole('button', { name: 'Check save status', exact: true }).waitFor();
  assert.equal(saveCalls.length, 1);
  assert.equal(await page.getByLabel('Your update').isDisabled(), true);
  await page.reload();
  await page.getByRole('button', { name: 'Check save status', exact: true }).waitFor();
  assert.equal(saveCalls.length, 1, 'Refresh must not redeliver a save');
  assert.equal(await page.getByLabel('Your update').isDisabled(), true);
  await page.screenshot({ path: 'artifacts/browser/save-unresolved.png', fullPage: true });
  pendingReceipt = false;
  draft.state = 'saved'; draft.phase = 'saved';
  draft.receipt = { submission_id: saveCalls[0].submission_id, proposal: structuredClone(draft.proposal), saved_at: '2026-10-29T10:00:00+00:00' };
  await page.getByRole('button', { name: 'Check save status', exact: true }).click();
  await page.getByText('Saved to this device', { exact: true }).waitFor();
  assert.equal(saveCalls.length, 1);
  assert.equal(await page.locator('#receipt-id').textContent(), saveCalls[0].submission_id);
  await page.screenshot({ path: 'artifacts/browser/saved.png', fullPage: true });
  failJobs = true;
  await page.reload();
  await page.getByRole('button', { name: 'Reload jobs', exact: true }).waitFor();
  assert.equal(await page.getByRole('button', { name: 'Start update', exact: true }).isDisabled(), true);
  failJobs = false; emptyJobs = true;
  await page.getByRole('button', { name: 'Reload jobs', exact: true }).click();
  await page.getByText('No jobs are available. Reload after adding fictional jobs to the local app.', { exact: true }).waitFor();
  emptyJobs = false;
  await page.getByRole('button', { name: 'Reload jobs', exact: true }).click();
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  await page.getByLabel('Your update').fill('x'.repeat(2001));
  assert.equal(await page.getByRole('button', { name: 'Review update', exact: true }).isDisabled(), true);
  await page.getByLabel('Your update').fill(examples[0]);
  holdMessage = true;
  await page.getByRole('button', { name: 'Review update', exact: true }).click();
  await page.getByText('Working on your update…', { exact: true }).waitFor();
  assert.equal(await page.getByRole('button', { name: 'Cancel update', exact: true }).isEnabled(), true, 'An open draft can be cancelled while extraction is pending');
  await page.getByRole('button', { name: 'Cancel update', exact: true }).click();
  await page.locator('#sheet').getByText('Update cancelled', { exact: true }).waitFor();
  const lateResponse = page.waitForResponse(response => response.url().endsWith('/message'));
  releaseMessage(); holdMessage = false;
  await lateResponse;
  assert.equal(await page.locator('#sheet').getByText('Update cancelled', { exact: true }).isVisible(), true, 'A late response cannot reopen cancelled UI');
  assert.equal(await page.getByLabel('Your update').isDisabled(), true);
  await page.getByRole('button', { name: 'Choose another job', exact: true }).click();
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  for (const message of [examples[0], examples[1]]) {
    await page.getByLabel('Your update').fill(message);
    await page.getByRole('button', { name: 'Review update', exact: true }).click();
    await page.waitForFunction(() => !document.querySelector('#message').disabled && document.querySelector('#message').value === '');
  }
  draft.proposal.diagnosis = 'मोटर की जाँच में आवाज़ और कंपन मिला। '.repeat(20).slice(0, 500);
  draft.proposal.part_needed = '<img src=x onerror=alert(1)>'.repeat(5).slice(0, 120);
  await page.getByLabel('Your update').fill(examples[2]);
  await page.getByRole('button', { name: 'Review update', exact: true }).click();
  await page.waitForFunction(() => !document.querySelector('#message').disabled && document.querySelector('#message').value === '');
  await page.setViewportSize({ width: 320, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'Long Hindi and part labels must wrap');
  assert.equal(await page.locator('#fields img').count(), 0, 'Provider text cannot inject HTML');
  await page.screenshot({ path: 'artifacts/browser/long-fields-320.png', fullPage: true });
  await page.getByLabel('Your update').focus();
  assert.equal(await page.getByLabel('Your update').evaluate(element => getComputedStyle(element).outlineStyle), 'solid');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  assert.equal(await page.getByRole('button', { name: 'Confirm and save', exact: true }).evaluate(element => getComputedStyle(element).animationName), 'none');
  const storageCalls = saveCalls.length;
  await page.evaluate(() => { window.originalStorageSet = Storage.prototype.setItem; Storage.prototype.setItem = () => { throw new Error('storage blocked'); }; });
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByText('Browser storage is unavailable. Enable storage for this local page before saving so a lost response can be recovered.', { exact: true }).waitFor();
  assert.equal(saveCalls.length, storageCalls, 'No save request before retaining its identity');
  await page.evaluate(() => { Storage.prototype.setItem = window.originalStorageSet; });
  loseBeforeSave = true;
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  for (let index = 0; index < 2; index++) await page.getByRole('button', { name: 'Retry same save', exact: true }).click();
  await page.getByRole('button', { name: 'Check save status', exact: true }).waitFor();
  assert.equal(saveCalls.length, storageCalls + 3, 'Client delivery is bounded');
  assert.deepEqual(saveCalls.at(-1), saveCalls.at(-3));
  await page.reload();
  await page.getByRole('button', { name: 'Check save status', exact: true }).waitFor();
  assert.equal(await page.getByRole('button', { name: 'Retry same save', exact: true }).isVisible(), false, 'Refresh does not reset the client send allowance');
  assert.equal(await page.getByLabel('Your update').isDisabled(), true);
  assert.deepEqual(errors, []);
  console.log('PASS: fixture HTTP browser checks — clarification/correction, unsent edit guard, extraction retry, mismatch discard, rejected/uncertain saves, refresh/receipt, jobs loading/error/empty, cancellation + late result, input limits, long Hindi fields/HTML escaping, focus/reduced motion, storage failure, three-send cap across refresh, 1280/390/320 layouts.');
} finally {
  await browser.close();
}
