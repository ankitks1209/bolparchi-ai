// Browser-owned synthetic microphone device; no real user audio or provider calls.
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
const { chromium } = createRequire(import.meta.url)(process.argv[2] || 'playwright');
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'] });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, permissions: ['microphone'] });
const page = await context.newPage(); page.setDefaultTimeout(6000);
await page.addInitScript(() => {
  const original = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
  window.testStreams = [];
  navigator.mediaDevices.getUserMedia = async constraints => {
    if (window.denyMic) throw new DOMException('test denial', 'NotAllowedError');
    if (window.holdMic) await new Promise(resolve => { window.releaseMic = resolve; });
    const stream = await original(constraints); window.testStreams.push(stream); return stream;
  };
});
let view = { draft_id: 'voice-draft', revision: 1, content_hash: 'a'.repeat(64), proposal: { job_id: '104' }, input: null, state: 'open', phase: 'clarify', can_confirm: false, can_cancel: true, can_retry: false, changed_fields: [], question: 'Kya kharabi mili?', receipt: null, save_request: null };
let audioCalls = 0, empty = false, loseAudio = false;
const errors = []; page.on('pageerror', error => errors.push(error.message));
await page.route('**/api/**', async route => {
  const url = new URL(route.request().url());
  if (url.pathname === '/api/jobs') return route.fulfill({ json: { jobs: [{ job_id: '104', appliance: 'Washing machine', customer_label: 'Demo Customer A' }], mode: 'fixtures', examples: [], speech: { recording: true, readback: false, max_seconds: 30 } } });
  if (url.pathname.endsWith('/audio')) {
    audioCalls++;
    if (loseAudio) { view.phase = 'transcribing'; view.can_confirm = false; return route.abort('failed'); }
    const body = route.request().postDataBuffer();
    assert.equal(body.toString('ascii', 0, 4), 'RIFF'); assert.equal(body.readUInt32LE(24), 16000);
    assert.equal(body.readUInt16LE(22), 1); assert.equal(body.readUInt16LE(34), 16);
    assert.equal(body.readUInt32LE(40), body.length - 44); assert.ok(body.length > 44 && body.length <= 960044);
    assert.equal(url.searchParams.get('expected_revision'), String(view.revision));
    if (empty) {
      view.phase = 'speech_error'; view.can_confirm = false; view.empty_speech_attempts = (view.empty_speech_attempts || 0) + 1;
      view.prefer_typing = view.empty_speech_attempts >= 2; view.offer_typing = true;
    } else {
      view.revision++; view.phase = 'review'; view.can_confirm = true;
      view.proposal = { job_id: '104', diagnosis: 'motor fixed', status: 'completed' };
      view.input = { transcript: 'Motor fixed', turn_id: 'voice-turn', state: 'applied' };
      view.readback = 'Job 104: motor fixed. Kaam ho gaya.';
    }
  }
  await route.fulfill({ json: { ok: true, code: 'draft', view } });
});
async function record() {
  await page.getByRole('button', { name: 'Record update', exact: true }).click();
  await page.getByText('Recording…', { exact: true }).waitFor();
  // Wait for a nonempty audio block; no human microphone is used.
  await page.waitForFunction(() => document.querySelector('#record-time').textContent !== '0:00 / 0:30');
  await page.getByRole('button', { name: 'Stop and review', exact: true }).click();
  await page.getByRole('button', { name: 'Record update', exact: true }).waitFor();
}
try {
  await page.goto(process.argv[3] || 'http://127.0.0.1:8766');
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  await record();
  assert.equal(audioCalls, 1);
  assert.equal(await page.locator('#transcript').textContent(), 'Motor fixed');
  assert.equal(await page.getByRole('button', { name: 'Confirm and save', exact: true }).isEnabled(), true);
  assert.equal(await page.evaluate(() => testStreams.every(stream => stream.getTracks().every(track => track.readyState === 'ended'))), true);
  await page.getByRole('button', { name: 'Record update', exact: true }).click();
  await page.getByText('Recording…', { exact: true }).waitFor();
  await page.getByRole('button', { name: 'Discard recording', exact: true }).click();
  assert.equal(audioCalls, 1);
  assert.equal(await page.evaluate(() => testStreams.every(stream => stream.getTracks().every(track => track.readyState === 'ended'))), true);
  await page.evaluate(() => { window.denyMic = true; });
  await page.getByRole('button', { name: 'Record update', exact: true }).click();
  await page.getByText('Microphone access was denied. Allow it in your browser, or type your update.', { exact: true }).waitFor();
  assert.equal(await page.getByLabel('Your update').isEnabled(), true);
  await page.evaluate(() => { window.denyMic = false; window.holdMic = true; });
  await page.getByRole('button', { name: 'Record update', exact: true }).click();
  await page.getByText('Waiting for microphone permission…', { exact: true }).waitFor();
  await page.getByRole('button', { name: 'Discard recording', exact: true }).click();
  await page.evaluate(() => { window.holdMic = false; window.releaseMic(); });
  await page.waitForFunction(() => testStreams.length === 3 && testStreams.every(stream => stream.getTracks().every(track => track.readyState === 'ended')));
  assert.equal(audioCalls, 1);
  empty = true;
  await record(); await record();
  await page.waitForFunction(() => document.activeElement.id === 'message');
  assert.equal(await page.locator('#transcript').textContent(), 'Motor fixed');
  loseAudio = true;
  await record();
  await page.locator('#refresh').click();
  await page.getByText('Transcribing your recording…', { exact: true }).waitFor();
  assert.equal(await page.locator('#refresh').isVisible(), true, 'An outstanding transcription stays manually refreshable after a lost response');
  view.phase = 'speech_error';
  await page.locator('#refresh').click();
  await page.screenshot({ path: 'artifacts/browser/voice-desktop.png', fullPage: true });
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.screenshot({ path: `artifacts/browser/voice-${width}.png`, fullPage: true });
  }
  assert.deepEqual(errors, []);
  console.log('PASS: synthetic microphone → native AudioWorklet → 16 kHz mono WAV; stop/upload, discard, permission denial, late permission cleanup, two-empty typing focus, transcript preservation, 1280/390/320 layouts. HTTP/provider responses are fixtures.');
} finally { await browser.close(); }
