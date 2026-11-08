// Explicit live-provider acceptance using a replay of a supplied human recording.
// This verifies the app's native recorder with a replay stream, not a fresh microphone.
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const [playwrightPath, optIn, base, recording] = process.argv.slice(2);
if (optIn !== '--live' || !recording || !/^http:\/\/127\.0\.0\.1:\d+$/.test(base || '')) {
  throw new Error('Usage: node scripts/check_live_browser.mjs PLAYWRIGHT --live http://127.0.0.1:PORT RECORDING');
}
const encoded = (await readFile(resolve(recording))).toString('base64');
const { chromium } = createRequire(import.meta.url)(playwrightPath);
const directory = `artifacts/live-browser/${new Date().toISOString().replaceAll(':', '-')}`;
await mkdir(directory, { recursive: true });
const report = { source: 'human_recording_replayed_into_native_browser_recorder', providers: 'live', steps: [], outcome: 'started' };
const checkpoint = async () => writeFile(`${directory}/report.json`, JSON.stringify(report, null, 2) + '\n');
await checkpoint();
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage();
page.setDefaultTimeout(45000);
const errors = [], saves = [];
page.on('pageerror', error => errors.push(error.message));
page.on('request', request => { if (new URL(request.url()).pathname.endsWith('/save')) saves.push(request.postDataJSON()); });
await page.addInitScript(({ encoded }) => {
  navigator.mediaDevices.getUserMedia = async () => {
    const audio = new AudioContext({ sampleRate: 16000 });
    const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
    const buffer = await audio.decodeAudioData(bytes.buffer);
    if (buffer.duration > 25) { await audio.close(); throw new Error('Replay too long'); }
    const source = audio.createBufferSource(); source.buffer = buffer;
    const destination = audio.createMediaStreamDestination(); source.connect(destination);
    await audio.resume(); source.start(audio.currentTime + 0.5);
    // Keep this test-only graph alive until the native recorder releases its track.
    window.replayGraph = { audio, source, destination, duration: buffer.duration };
    return destination.stream;
  };
}, { encoded });
try {
  await page.goto(base);
  const config = await (await context.request.get(`${base}/api/jobs`)).json();
  assert.equal(config.mode, 'live', 'Never report fixtures as live acceptance');
  assert.equal(config.speech.recording, true); assert.equal(config.speech.readback, true);
  await page.getByRole('button', { name: 'Start update', exact: true }).click();
  await page.getByRole('button', { name: 'Record update', exact: true }).click();
  await page.getByText('Recording…', { exact: true }).waitFor();
  await page.waitForFunction(() => {
    const value = document.querySelector('#record-time').textContent;
    const seconds = Number(value.split(' / ')[0].split(':')[1]);
    return seconds >= Math.ceil(window.replayGraph.duration + 1);
  });
  const audioResponse = page.waitForResponse(r => new URL(r.url()).pathname.endsWith('/audio'));
  await page.getByRole('button', { name: 'Stop and review', exact: true }).click();
  const received = await audioResponse;
  const first = (await received.json()).view;
  report.steps.push({ step: 'recording_to_review', view: first }); await checkpoint();
  assert.equal(received.status(), 200); assert.equal(first.phase, 'review');
  assert.equal(first.proposal.quantity, 1); assert.equal(first.proposal.status, 'pending');
  assert.ok(first.proposal.diagnosis && first.proposal.follow_up);
  assert.match(first.proposal.part_needed, /motor|मोटर/i);
  assert.equal(first.receipt, null); assert.equal(saves.length, 0);
  const path = `/api/drafts/${first.draft_id}`;
  for (const [message, phase] of [['Follow-up hata do.', 'clarify'], ['Kal shaam aana hai.', 'review']]) {
    // Deliberately pace generation below five requests per minute.
    await new Promise(resolve => setTimeout(resolve, 16000));
    await page.getByLabel('Your update').fill(message);
    const answer = page.waitForResponse(r => new URL(r.url()).pathname.endsWith('/message'));
    await page.getByRole('button', { name: 'Review update', exact: true }).click();
    const result = (await (await answer).json()).view;
    report.steps.push({ step: message, view: result }); await checkpoint();
    assert.equal(result.phase, phase); assert.equal(result.proposal.quantity, 1);
    if (phase === 'clarify') assert.equal(result.can_confirm, false);
  }
  const review = (await (await context.request.get(base + path)).json()).view;
  assert.equal(review.can_confirm, true); assert.equal(saves.length, 0);
  const speech = page.waitForResponse(r => new URL(r.url()).pathname.endsWith('/readback'));
  await page.getByRole('button', { name: 'Listen to review', exact: true }).click();
  const spoken = await speech;
  assert.equal(spoken.status(), 200);
  const spokenBytes = await spoken.body();
  assert.equal(spokenBytes.subarray(0, 4).toString(), 'RIFF');
  await writeFile(`${directory}/readback.wav`, spokenBytes);
  await page.waitForFunction(() => !document.querySelector('#readback-audio').paused);
  await page.getByRole('button', { name: 'Stop read-back', exact: true }).click();
  report.steps.push({ step: 'live_readback_played', bytes: spokenBytes.length }); await checkpoint();
  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.screenshot({ path: `${directory}/review-${width}.png`, fullPage: true });
  }
  assert.equal(saves.length, 0, 'Audio, extraction and read-back must not save');
  await page.getByRole('button', { name: 'Confirm and save', exact: true }).click();
  await page.getByText('Saved to this device', { exact: true }).waitFor();
  const saved = (await (await context.request.get(base + path)).json()).view;
  assert.equal(saved.state, 'saved'); assert.equal(saved.proposal.quantity, 1);
  assert.equal(saves.length, 1); assert.equal(saved.receipt.submission_id, saves[0].submission_id);
  await page.reload();
  // Confirm server durability without sending another save or provider request.
  const persisted = (await (await context.request.get(base + path)).json()).view;
  assert.deepEqual(persisted.receipt, saved.receipt);
  assert.equal(saves.length, 1); assert.deepEqual(errors, []);
  report.steps.push({ step: 'explicit_save_and_receipt', view: saved });
  report.outcome = 'passed'; await checkpoint();
  console.log(`PASS live recorded-audio replay → STT/extraction → correction/clarification → TTS playback → explicit save. Evidence: ${directory}`);
} catch (error) {
  report.outcome = 'failed'; report.failure = String(error.message).slice(0, 1000); await checkpoint();
  await page.screenshot({ path: `${directory}/failure.png`, fullPage: true }).catch(() => {});
  throw error;
} finally { await browser.close(); }
