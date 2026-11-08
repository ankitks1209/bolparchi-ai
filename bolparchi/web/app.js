// The server owns draft state and receipts. The browser retains only save identity.
import { Recorder } from '/recorder.js';
const $ = id => document.getElementById(id);
const SAVE_KEY = 'bolparchi.pending-save.v1';
const fieldLabels = { diagnosis: 'Diagnosis', status: 'Status', part_needed: 'Part needed', quantity: 'Quantity', follow_up: 'Follow-up' };
let jobs = [], draft = null, pendingSave = null, busy = false, cancelling = false, refreshNeeded = false;
let mode = 'unknown';
let requestEpoch = 0;
let speech = {}, playbackEpoch = 0, playbackController = null, playbackUrl = null, playbackActive = false;
let captureState = 'idle', recordTarget = null;
const recorder = new Recorder({
  onState(state, seconds) { captureState = state; $('record-time').textContent = `0:${String(Math.floor(seconds)).padStart(2, '0')} / 0:30`; render(); },
  onComplete(blob) {
    const target = recordTarget; recordTarget = null;
    if (!target || draft?.draft_id !== target.draft_id || draft?.state !== 'open') return;
    action(`/drafts/${target.draft_id}/audio?expected_revision=${target.revision}`, blob);
  },
  onError(message) { recordTarget = null; notice(message); render(); $('message').focus(); },
});
function discardRecording() { recordTarget = null; recorder.cancel(); }

function stopReadback() {
  playbackEpoch++;
  playbackController?.abort(); playbackController = null;
  const audio = $('readback-audio'); audio.pause(); audio.removeAttribute('src'); audio.load();
  if (playbackUrl) URL.revokeObjectURL(playbackUrl);
  playbackUrl = null; playbackActive = false; $('playback-status').textContent = '';
}
async function listen() {
  if ($('listen').disabled) return;
  stopReadback(); const epoch = playbackEpoch;
  playbackActive = true; playbackController = new AbortController();
  const timer = setTimeout(() => playbackController?.abort(), 45000);
  $('playback-status').textContent = 'Preparing read-back…'; $('readback-details').open = true; render();
  try {
    const response = await fetch(`/api/drafts/${draft.draft_id}/readback`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-BolParchi-Request': '1' }, body: JSON.stringify({ revision: draft.revision, content_hash: draft.content_hash }), signal: playbackController.signal, cache: 'no-store' });
    if (!response.ok || !response.headers.get('Content-Type')?.startsWith('audio/wav')) throw new Error('speech_failed');
    const blob = await response.blob();
    if (epoch !== playbackEpoch || inputDirty() || busy || !draft?.can_confirm) return;
    playbackUrl = URL.createObjectURL(blob); $('readback-audio').src = playbackUrl;
    await $('readback-audio').play();
    if (epoch === playbackEpoch) $('playback-status').textContent = mode === 'fixtures' ? 'Playing a fixture test tone.' : 'Playing the current review.';
  } catch {
    if (epoch === playbackEpoch) { stopReadback(); notice('Read-back could not be played. The text review is still available.'); }
  } finally { clearTimeout(timer); render(); }
}

function notice(text = '') { $('notice').textContent = text; $('notice').hidden = !text; }
async function api(path, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 45000);
  try {
    const response = await fetch(`/api${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers: body === undefined ? {} : { 'Content-Type': body instanceof Blob ? 'audio/wav' : 'application/json', 'X-BolParchi-Request': '1' },
      body: body === undefined ? undefined : body instanceof Blob ? body : JSON.stringify(body), cache: 'no-store', signal: controller.signal,
    });
    if (!response.ok) throw new Error('request_failed');
    return await response.json();
  } finally { clearTimeout(timer); }
}
function inputDirty() { return $('message').value.length > 0; }
let sidebarClosing = false;
function renderSidebar() {
  const active = Boolean(draft || pendingSave);
  const jobId = draft?.proposal?.job_id || pendingSave?.job_id;
  const job = jobs.find(item => item.job_id === jobId);
  $('sidebar-job').textContent = active ? `Job ${jobId || '—'} · ${job?.appliance || 'Service update'}` : 'No job selected';
  $('sidebar-state').textContent = !active ? 'Choose a job to begin.' : saveLocked() ? 'Save unconfirmed · keep this tab open' : draft?.state === 'saved' && matchingReceipt() ? 'Saved · receipt verified' : draft?.state === 'cancelled' ? 'Update cancelled' : 'Draft · not saved';
  $('nav-jobs').hidden = active;
  $('nav-update').hidden = !draft || ['saved', 'cancelled'].includes(draft.state);
  $('nav-review').hidden = !draft;
  $('nav-receipt').hidden = !(draft?.state === 'saved' && matchingReceipt());
  $('nav-examples').hidden = mode !== 'fixtures' || !draft || draft.state !== 'open' || saveLocked();
  $('sidebar-mode').textContent = mode === 'fixtures' ? 'Local / Fixture walkthrough' : mode === 'live' ? 'Local / Live providers' : 'Local / Connecting';
  $('sidebar-toggle').disabled = captureState !== 'idle';
}
function closeSidebar(target = null) {
  if (!$('sidebar').open || sidebarClosing) return;
  sidebarClosing = true; $('sidebar').classList.add('closing');
  const finish = () => {
    $('sidebar').close(); $('sidebar').classList.remove('closing'); sidebarClosing = false;
    $('sidebar-toggle').setAttribute('aria-expanded', 'false');
    if (target && !target.closest('[hidden]')) {
      if (target.tabIndex < 0) target.tabIndex = -1;
      target.focus({ preventScroll: true }); target.scrollIntoView({ block: 'start' });
    } else $('sidebar-toggle').focus({ preventScroll: true });
  };
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) finish();
  else setTimeout(finish, 200);
}
$('sidebar-toggle').addEventListener('click', () => {
  if ($('sidebar-toggle').disabled || $('sidebar').open) return;
  stopReadback(); render(); $('sidebar').showModal(); $('sidebar-toggle').setAttribute('aria-expanded', 'true');
});
$('sidebar-close').addEventListener('click', () => closeSidebar());
$('sidebar').addEventListener('cancel', event => { event.preventDefault(); closeSidebar(); });
$('sidebar').addEventListener('keydown', event => {
  if (event.key !== 'Tab') return;
  const controls = [...$('sidebar').querySelectorAll('button:not([disabled])')].filter(button => !button.hidden);
  const first = controls[0], last = controls.at(-1);
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});
$('sidebar').addEventListener('click', event => {
  const box = $('sidebar').getBoundingClientRect();
  if (event.target === $('sidebar') && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) closeSidebar();
});
for (const [button, target] of [['nav-jobs', 'picker-title'], ['nav-update', 'input-title'], ['nav-review', 'review-title'], ['nav-receipt', 'receipt']]) {
  $(button).addEventListener('click', () => closeSidebar($(target)));
}
$('nav-examples').addEventListener('click', () => {
  $('examples').querySelector('details').open = true; closeSidebar($('examples').querySelector('summary'));
});
function saveLocked() { return Boolean(pendingSave) || ['saving', 'save_unresolved'].includes(draft?.state); }
function retainedSave(value) {
  if (value === null) sessionStorage.removeItem(SAVE_KEY);
  else sessionStorage.setItem(SAVE_KEY, JSON.stringify(value));
  pendingSave = value;
}
function matchingReceipt() {
  return draft?.receipt && (!pendingSave || draft.receipt.submission_id === pendingSave.submission_id);
}
function showFields() {
  $('fields').replaceChildren();
  for (const [key, label] of Object.entries(fieldLabels)) {
    const row = document.createElement('div'); row.className = 'field'; row.dataset.field = key;
    const term = document.createElement('dt'); term.textContent = label;
    const value = document.createElement('dd');
    const text = document.createElement('span'); text.className = 'value';
    text.textContent = draft?.proposal?.[key] ?? 'Not provided';
    if (draft?.proposal?.[key] == null) text.classList.add('empty');
    value.append(text);
    if (draft?.changed_fields?.includes(key) && draft.state === 'open') {
      const badge = document.createElement('span'); badge.className = 'changed'; badge.textContent = 'Updated'; value.append(badge);
    }
    row.append(term, value); $('fields').append(row);
  }
}
function render() {
  renderSidebar();
  const active = Boolean(draft || pendingSave);
  $('picker').hidden = active; $('sheet').hidden = !active;
  $('page-heading').hidden = active;
  if (!active) return;
  const jobId = draft?.proposal?.job_id || pendingSave?.job_id;
  const job = jobs.find(item => item.job_id === jobId);
  $('job-number').textContent = jobId || '—';
  $('job-title').textContent = job?.appliance || 'Service update';
  $('customer').textContent = job?.customer_label || 'Fictional service job';
  const locked = saveLocked();
  const saved = draft?.state === 'saved' && matchingReceipt();
  const cancelled = draft?.state === 'cancelled';
  const capturing = captureState !== 'idle';
  const disabled = busy || capturing || locked || saved || cancelled || refreshNeeded || !draft;
  $('voice-controls').hidden = !speech.recording || saved || cancelled;
  $('record').hidden = capturing; $('record').disabled = disabled || inputDirty();
  $('stop-recording').hidden = captureState !== 'recording';
  $('discard-recording').hidden = !capturing;
  $('capture-status').textContent = { idle: 'Ready to record', permission: 'Waiting for microphone permission…', recording: 'Recording…', finishing: 'Preparing recording…' }[captureState];
  $('voice-note').textContent = speech.recording ? (mode === 'fixtures' ? 'Speech fixture mode: transcription is scripted; read-back uses a test tone.' : 'Audio is transcribed by Gnani; text is extracted by Gemini. Fictional updates only.') : 'Voice is unavailable in this session. Type your update.';
  $('message').disabled = disabled;
  $('submit-message').disabled = disabled || !inputDirty() || [...$('message').value].length > 2000;
  $('count').textContent = `${[...$('message').value].length.toLocaleString('en-IN')} / 2,000`;
  $('save').disabled = disabled || !draft?.can_confirm || inputDirty();
  $('listen').hidden = !speech.readback || !draft?.readback || saved || cancelled;
  $('listen').disabled = disabled || inputDirty() || playbackActive || !draft?.can_confirm;
  $('stop-readback').hidden = !playbackActive;
  $('readback-details').hidden = !draft?.readback;
  $('readback-text').textContent = draft?.readback || '';
  $('cancel').disabled = cancelling || locked || !draft?.can_cancel;
  $('cancel').hidden = saved || cancelled;
  $('another').hidden = !saved && !cancelled;
  $('save-controls').hidden = locked || saved || cancelled;
  $('check-save').hidden = !locked || saved;
  $('check-save').disabled = busy;
  $('retry-save').hidden = !pendingSave || draft?.state !== 'open' || (pendingSave.requests_sent || 1) >= 3;
  $('retry-save').disabled = busy;
  $('retry').hidden = !draft?.can_retry || locked || saved || cancelled;
  $('retry').disabled = busy || inputDirty();
  $('refresh').hidden = !(refreshNeeded || ['processing', 'transcribing'].includes(draft?.phase)) || locked;
  $('refresh').disabled = busy;
  for (const id of ['apply-mismatch', 'discard-mismatch']) {
    $(id).hidden = draft?.phase !== 'job_mismatch' || locked;
    $(id).disabled = busy || inputDirty();
  }
  $('examples').hidden = mode !== 'fixtures';
  for (const button of $('example-buttons').children) button.disabled = disabled;
  $('record-state').textContent = saved ? 'Saved · receipt verified' : cancelled ? 'Cancelled' : locked ? 'Save unconfirmed' : 'Draft · not saved';
  $('receipt').hidden = !saved;
  if (saved) {
    $('receipt-id').textContent = draft.receipt.submission_id;
    $('receipt-time').textContent = draft.receipt.saved_at || '';
  }
  const states = {
    clarify: ['One detail at a time', draft?.question],
    clarify_message: ['Please clarify your message', draft?.question],
    job_mismatch: ['The message names a different job', draft?.question],
    extraction_error: ['We couldn’t extract this update', 'Your message and draft are kept. Retry extraction when the service is available. Typing also uses the same service.'],
    processing: ['Reviewing your update…', 'Your record has not been saved.'],
    transcribing: ['Transcribing your recording…', 'Your previous usable message is kept until a new transcript is ready.'],
    speech_error: ['We couldn’t transcribe this recording', draft?.prefer_typing ? 'Please type your update below. You can also try recording again.' : 'Try recording again or type your update. Your previous usable message is kept.'],
    review: ['Ready for your review', 'Check all five fields, then confirm. You can still type a correction.'],
    saved: ['Record saved', 'The server returned the receipt for this update.'],
    cancelled: ['Update cancelled', 'This draft did not change the job.'],
  };
  let [title, message] = states[draft?.phase] || ['Current draft', 'Review your details before saving.'];
  if (locked) [title, message] = [busy ? 'Checking this save…' : 'Save not yet confirmed', 'Editing is locked while this save may complete. Check status to look for its receipt.'];
  else if (busy) [title, message] = ['Working on your update…', 'Nothing is saved until you confirm.'];
  else if (refreshNeeded) [title, message] = ['Connection interrupted', 'Refresh the draft to see whether the update reached the server. Your typed text is kept.'];
  $('state-title').textContent = title; $('state-message').textContent = message || '';
  $('review-help').textContent = inputDirty() ? 'Review your typed changes before confirming this record.' : 'Nothing is saved until you confirm the full record.';
  $('transcript-details').hidden = !draft?.input?.transcript;
  $('transcript').textContent = draft?.input?.transcript || '';
  $('reference').textContent = `Draft ${draft?.draft_id || pendingSave?.draft_id} · Revision ${draft?.revision || pendingSave?.revision} · ${draft?.content_hash || pendingSave?.content_hash}${pendingSave ? ` · Submission ${pendingSave.submission_id}` : ''}`;
  showFields();
}
function adopt(response) {
  if (response.view) draft = response.view;
  if (draft?.save_request && !pendingSave) {
    retainedSave({ draft_id: draft.draft_id, submission_id: draft.save_request.submission_id, revision: draft.revision, content_hash: draft.content_hash, job_id: draft.proposal.job_id });
  }
  if (pendingSave && matchingReceipt() && draft.state === 'saved') retainedSave(null);
  else if (pendingSave && response.code === 'not_saved' && draft?.state === 'open') {
    retainedSave(null); notice('The server confirmed this attempt was not saved. Review the record before trying again.');
  } else if (pendingSave && ['stale_confirmation', 'incomplete', 'pending_input', 'unknown_job', 'invalid_input'].includes(response.code) && draft?.state === 'open') {
    retainedSave(null); notice('The server rejected this save. Review the latest record before confirming again.');
  }
}
async function loadJobs() {
  $('start').disabled = true; $('job').disabled = true; $('reload-jobs').hidden = true;
  $('jobs-status').textContent = 'Loading fictional jobs…';
  try {
    const data = await api('/jobs'); jobs = data.jobs; mode = data.mode; speech = data.speech || {};
    $('mode').textContent = mode === 'fixtures' ? 'Offline fixture mode · Scripted extraction, real local records. No AI requests.' : 'Live provider mode · Updates are sent to Gemini. Fictional data only.';
    $('job').replaceChildren(...jobs.map(job => {
      const option = document.createElement('option'); option.value = job.job_id;
      option.textContent = `${job.job_id} · ${job.appliance}`; return option;
    }));
    $('start').disabled = jobs.length === 0; $('job').disabled = jobs.length === 0;
    $('jobs-status').textContent = jobs.length ? 'The selected job stays fixed for this update.' : 'No jobs are available. Reload after adding fictional jobs to the local app.';
    $('reload-jobs').hidden = jobs.length > 0;
    $('example-buttons').replaceChildren(...(data.examples || []).map(message => {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = message;
      button.addEventListener('click', () => { stopReadback(); $('message').value = message; render(); $('message').focus(); }); return button;
    }));
  } catch {
    $('jobs-status').textContent = 'Could not load jobs. Check the local server and reload.';
    $('reload-jobs').hidden = false;
    $('mode').textContent = 'Local server unavailable · No successful connection yet.';
  }
  render();
}
async function action(path, body, { clearInput = false, interrupt = false } = {}) {
  if (busy && !interrupt) return;
  stopReadback();
  busy = true; notice(); render(); const epoch = ++requestEpoch;
  try {
    const response = await api(path, body);
    if (epoch !== requestEpoch) return;
    adopt(response);
    if (clearInput && draft?.input?.transcript === body.message) $('message').value = '';
    if (!response.view) notice(response.message || 'The action was rejected. Refresh the current draft.');
    else if (!response.ok && $('notice').hidden && !['unresolved', 'pending'].includes(response.code)) notice(response.message || 'The action could not be completed.');
    refreshNeeded = false;
  } catch {
    if (epoch !== requestEpoch) return;
    if (!pendingSave) refreshNeeded = Boolean(draft);
    notice(pendingSave ? 'The save response was interrupted. Keep this tab and check status; it may already have saved.' : 'The server could not be reached. Your text is kept.');
  } finally { if (epoch === requestEpoch) { busy = false; render(); if (draft?.prefer_typing) $('message').focus(); } }
}
$('start').addEventListener('click', async () => {
  if (busy) return;
  $('start').disabled = true;
  await action('/drafts', { job_id: $('job').value });
  $('start').disabled = jobs.length === 0;
  if (draft) $('message').focus(); else $('jobs-status').textContent = 'Could not start this update. Try again.';
});
$('message').addEventListener('input', () => { stopReadback(); render(); });
$('listen').addEventListener('click', listen);
$('stop-readback').addEventListener('click', () => { stopReadback(); render(); });
$('readback-audio').addEventListener('ended', () => { stopReadback(); render(); });
$('readback-audio').addEventListener('error', () => { if (playbackActive) { stopReadback(); notice('Read-back could not be played. The text review is still available.'); render(); } });
window.addEventListener('pagehide', stopReadback);
window.addEventListener('pagehide', discardRecording);
document.addEventListener('visibilitychange', () => { if (document.hidden) { stopReadback(); discardRecording(); render(); } });
$('record').addEventListener('click', () => {
  if ($('record').disabled) return;
  stopReadback(); notice(); recordTarget = { draft_id: draft.draft_id, revision: draft.revision }; recorder.start();
});
$('stop-recording').addEventListener('click', () => recorder.stop());
$('discard-recording').addEventListener('click', () => { discardRecording(); render(); $('message').focus(); });
$('message-form').addEventListener('submit', event => {
  event.preventDefault();
  if ($('submit-message').disabled) return;
  action(`/drafts/${draft.draft_id}/message`, { message: $('message').value, expected_revision: draft.revision }, { clearInput: true });
});
$('retry').addEventListener('click', () => action(`/drafts/${draft.draft_id}/retry`, { turn_id: draft.input.turn_id, expected_revision: draft.revision }));
for (const [id, decision] of [['apply-mismatch', 'apply'], ['discard-mismatch', 'discard']]) {
  $(id).addEventListener('click', () => action(`/drafts/${draft.draft_id}/mismatch`, { turn_id: draft.input.turn_id, action: decision, expected_revision: draft.revision }));
}
$('cancel').addEventListener('click', async () => {
  if ($('cancel').disabled) return;
  discardRecording();
  cancelling = true;
  try { await action(`/drafts/${draft.draft_id}/cancel`, { expected_revision: draft.revision }, { interrupt: true }); }
  finally { cancelling = false; render(); }
});
$('refresh').addEventListener('click', () => action(`/drafts/${draft.draft_id}`));
$('save').addEventListener('click', async () => {
  if ($('save').disabled) return;
  try {
    retainedSave({ draft_id: draft.draft_id, submission_id: crypto.randomUUID(), revision: draft.revision, content_hash: draft.content_hash, job_id: draft.proposal.job_id, requests_sent: 1 });
  } catch { notice('Browser storage is unavailable. Enable storage for this local page before saving so a lost response can be recovered.'); return; }
  await action(`/drafts/${pendingSave.draft_id}/save`, { submission_id: pendingSave.submission_id, revision: pendingSave.revision, content_hash: pendingSave.content_hash });
});
$('check-save').addEventListener('click', () => action(`/drafts/${pendingSave.draft_id}/save-status`, { submission_id: pendingSave.submission_id }));
$('retry-save').addEventListener('click', async () => {
  if ($('retry-save').disabled || $('retry-save').hidden) return;
  try { retainedSave({ ...pendingSave, requests_sent: (pendingSave.requests_sent || 1) + 1 }); }
  catch { notice('Could not retain the save identity. Keep this tab and use Check save status.'); return; }
  await action(`/drafts/${pendingSave.draft_id}/save`, { submission_id: pendingSave.submission_id, revision: pendingSave.revision, content_hash: pendingSave.content_hash });
});
$('another').addEventListener('click', () => { draft = null; $('message').value = ''; refreshNeeded = false; notice(); loadJobs(); });
$('reload-jobs').addEventListener('click', loadJobs);
async function boot() {
  try {
    const stored = sessionStorage.getItem(SAVE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (!parsed.draft_id || !parsed.submission_id || !parsed.content_hash || !Number.isInteger(parsed.revision)) throw new Error('invalid_save_reference');
      pendingSave = parsed;
    }
  } catch { $('mode').textContent = 'Browser storage could not be read. Save recovery may be unavailable.'; }
  await loadJobs();
  if (pendingSave) {
    await action(`/drafts/${pendingSave.draft_id}`);
    if (pendingSave) await action(`/drafts/${pendingSave.draft_id}/save-status`, { submission_id: pendingSave.submission_id });
  }
}
boot();
