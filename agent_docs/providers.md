# Provider probe preparation

Current evidence, 6 November 2026: the active Gemini 3.5 Flash-Lite field-decision adapter passes six targeted development checks and real typed Hindi review/save. The retained-recording backend task now passes real Gnani STT → Gemini extraction/clarification → Gnani TTS → explicit test confirmation/SQLite receipt without retries. The frozen evaluation remains five exact matches/one HTTP 503, with a separate successful recheck of that unavailable uncertainty case. Ankit has also completed the fresh browser microphone task and reported clear recording/playback; its saved receipt was independently verified. This is one-device feedback, not general speech-quality evidence. See [evaluation](../docs/EVALUATION.md). Historical reports below retain their original configuration and failures.


Ankit authorized necessary tests to finish the project using the reported free tier/existing credits. No paid overage or billing change is authorized. The dated probe entries below are historical and do not override the current authorization or readiness record.

## Frozen extraction evaluation — 6 November

The active configuration produced five exact matches from six single-attempt frozen cases, with one HTTP 503 and no semantic mismatches among the five returned patches. The initial runner stopped on case two; a separate batch sent only the four untouched cases. No failed case was retried, no prompt/expectations were changed and no Gnani requests were made. The uncertainty case was unverified in that run; a separate unchanged recheck subsequently passed. Full results and immutable evidence references are in [evaluation](../docs/EVALUATION.md).

## Account setup

1. Create/sign in to the [Gnani API dashboard](https://app.gnani.ai/) and check whether challenge credits are available. Prisma and Timbre need an API key from that dashboard; see the [official quick start](https://docs.gnani.ai/api/introduction/quick-start).
2. Create/sign in to [Google AI Studio](https://aistudio.google.com/) and create a Gemini API key using the [official key instructions](https://ai.google.dev/gemini-api/docs/api-key). Confirm the account's actual allowance before enabling billing or making requests.
3. Keep key values out of chat, source files and reports. Local names are `GNANI_API_KEY` and `GEMINI_API_KEY`. The Gemini adapter accepts a key explicitly; the live probe reads the environment or an explicit `--env-file`. There is no implicit `.env` loading or shell evaluation. Key presence alone does not authorize calls.

On 24 October Ankit filled the root `.env` template privately. Key presence and owner-only read/write permissions were checked without displaying the value; Git ignores the file. The diagnostic request explicitly parsed this assignment as data, without executing shell content. Do not print this file or include it in inspection commands. The current offline demo still does not load it or call Gnani.

## First live Timbre probe — 24 October 2026

One initial sandbox attempt failed at DNS before reaching Gnani; approved network access then allowed two live TTS requests, both HTTP 200. Each sent the short fictional question `कितने मोटर चाहिए?` with the documented Timbre v2.5/Nalini/hi-IN request. No automatic retries occurred. The second request was a targeted format diagnosis after the first failed strict WAV validation; its latency was 1.004 seconds, a single observation rather than a benchmark. Credit consumption was not returned or independently checked.

The second response contained 138,284 bytes with `audio/wav`, 48 kHz mono 16-bit PCM, but both RIFF/data length fields were `0xffffffff`. The payload contained 69,120 frames (1.44 seconds). Correcting only those two length fields to the received byte counts produced a locally validated playable WAV. The original second response, normalized WAV and redacted result report are in ignored `artifacts/provider-probes/` as `gnani-tts-response.bin`, `gnani-tts.wav` and `gnani-tts-result.json`. The first response body was not retained. No audible pronunciation check is claimed.

Observed failure adjustment: retain a bounded successful audio response before decoding; distinguish finite WAV lengths from streaming placeholders, and normalize only a validated supported PCM container after complete receipt. Do not repeat a billed request solely to diagnose locally retained bytes. This initial diagnostic did not add an adapter; the later tested implementation is documented below.

## First human-recorded Prisma probe — 24 October 2026

Ankit supplied `New Recording.m4a` for the requested fictional update. Local audio inspection found 86,348 bytes, AAC/M4A, mono, 44.1 kHz, estimated duration 10.168889 seconds. One multipart request to `/stt/v3` with `language_code=hi-IN` returned HTTP 200 in 5.508 seconds, `success=true`, model `gnani-prisma-v2.5` and this transcript:

> मोटर खराब है, 2 मोटर, सॉरी, एक मोटर चाहिए, काम पेंडिंग है, कल शाम आना है।

The text preserves the requested two-to-one correction and the pending/follow-up content. This comparison is against the suggested recording script; no independent listening/word-error-rate check is claimed. One successful short recording does not establish general accuracy or latency. No extraction or save was performed. There were no retries, and actual credit consumption remains unknown.

The supplied recording was copied to ignored `artifacts/provider-probes/human-stt-input.m4a`; the redacted result, source hash and timing are in `gnani-stt-result.json` beside it. Preserve private recordings outside Git. The completed human-recording probe supersedes the earlier missing-input blocker; browser capture and workflow integration remain pending.

## Gnani adapter implementation — 27 October 2026

`GnaniSpeech` now sends multipart STT requests with fixed `hi-IN`/`verbatim` settings and returns the original successful transcript. It rejects malformed JSON, duplicate keys, false/nonboolean success, non-string/empty transcripts and text over the existing 2,000-character message limit. Oversize text is rejected, never truncated. Only documented file extensions are accepted, with a fixed generated filename; encoded input bytes are preserved. Format names do not prove valid media. Codec/duration validation and browser capture limits remain pending.

TTS uses the previously probed `timbre-v2.5`/Nalini/hi-IN configuration and validates 48 kHz mono 16-bit PCM WAV output. It repairs only `0xffffffff` RIFF/data length fields, requires the unknown-length data chunk to occupy the remaining payload, and rejects malformed finite sizes, duplicate chunks, unsupported PCM settings and partial frames. A prematurely ended unknown-length stream can still contain whole frames; container validation cannot prove semantic/audio completeness or pronunciation.

Both adapters use the shared 30-second socket-operation timeout, refuse redirects and do not retry. Resource guards: input defaults to 10 MiB (configurable up to 32 MiB), STT response 256 KiB, TTS response 16 MiB. These are local memory bounds, not published provider limits or a decision about the browser's recording duration. Each response read allows one additional detection byte. Text synthesis uses the existing 2,000-character message bound; the current application read-back fits within it.

The 56 new tests use synthetic audio and response fixtures. A separate offline replay of the retained 138,284-byte live response through `GnaniSpeech.synthesize` produced the exact previously normalized WAV, with PCM samples unchanged and SHA-256 `45e22aba0fd4ca00e280aaf7ec72ade926c721345cfca12a7eaba0ad019dc3a4`. The injected replay transport made zero network calls. Evidence: ignored `artifacts/provider-probes/gnani-adapter-replay-20261027.json`. No fresh Gnani call or listening assessment occurred in this task.

## Gemini adapter and first attempts — 27 October 2026

Implemented `bolparchi/gemini.py` and `scripts/probe_gemini.py` without new dependencies. The adapter uses the documented generateContent responseFormat.text JSON schema, LOW thinking and no tools. It accepts only a complete single candidate, ignores thought parts, validates the patch in Python, and returns only allowlisted metadata. Redirects are refused, response reads capped at 256 KiB plus one byte, and each socket operation has a 30-second timeout (not a total deadline). Transport errors are redacted and never retried automatically.

Ankit explicitly authorized up to six fictional free-tier requests. The sandbox attempt stopped with `network_error` in 0.023 seconds. With network permission, the next attempt returned HTTP 503 in 14.019 seconds; the runner stopped. No successful output, modelVersion or usage data was returned to the application. This does not prove that the key, model or schema is accepted, nor establish why the service failed. There were two attempts total, zero successful extractions; no calls followed 503. Billing settings were not changed; actual provider usage is unknown.

Ignored reports: `gemini-20261027T131857356955Z.json` and `gemini-20261027T131945464506Z.json` under `artifacts/provider-probes/`. They contain safe outcome codes and timing, not raw error bodies or keys. The remaining development cases have no live evidence. All 57 new adapter/probe tests are offline, including confirmed SQLite saving through Workflow with fixture responses.

On resuming, one further network-enabled check within the remaining allowance returned HTTP 503 in 3.067 seconds. Report: `gemini-20261027T160904371393Z.json`. Total now three attempts, zero successes; the second and third attempts both returned 503. Stop repeating the same call after these consecutive failures. Before another generation request, investigate service/model/account availability using read-only diagnostics and safe outcome codes. Do not infer invalid credentials, change models, enable billing or expose raw private error bodies from the status code alone.

## Documented contracts

### Gemini diagnosis — 28 October 2026

After the repeated generation failures, a single read-only models.get request with the configured key returned HTTP 200, the expected model name and generateContent support. The [official model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) also lists the configured model and LOW thinking; the [models API reference](https://ai.google.dev/api/models) defines this metadata operation. The public status page did not yield a readable incident summary in the available browser tool, so no global outage/all-clear conclusion is claimed.

One subsequent unchanged fictional correction probe returned HTTP 503. A bounded, redacted diagnostic extracted only provider status `UNAVAILABLE` and a fixed `capacity_or_demand` category from the error; no raw message, credentials or body was retained. This supports a generation-side capacity/demand diagnosis, not an assertion of invalid credentials or validated extraction schema. No further call followed. Read-only metadata success does not establish generation quota, billing status or semantic accuracy.

Ignored reports: `artifacts/provider-probes/gemini-model-check-20261028.json` and `gemini-generation-check-20261028.json`. Conservatively count five of the six approved attempts used: the earlier sandbox failure, three HTTP 503 generation responses and this metadata GET. One request remains under that accounting; do not spend it on another identical call without evidence of recovery or an approved diagnostic change. No billing, model or dependency change occurred.

| Probe | Documented starting point | Still to verify live |
| --- | --- | --- |
| Prisma STT | POST `https://api.vachana.ai/stt/v3`; multipart `audio_file`, `language_code=hi-IN`; `X-API-Key-ID` header. JSON success/transcript response. | One human recording and account access verified above; varied speakers, noise, limits/error behavior and browser input remain unverified |
| Timbre TTS | POST `https://api.vachana.ai/api/v1/tts/inference`; `X-API-Key-ID`; `timbre-v2.5`, voice `Nalini`, Hindi, mono PCM WAV at 48 kHz. Binary audio response. | WAV handling tested offline and against a retained response; audible pronunciation and integrated playback remain unverified |
| Gemini extraction | Candidate `gemini-3.8-flash`, REST `v1beta` generateContent; `x-goog-api-key`; LOW thinking and structured JSON output. No SDK dependency. | Access, responseFormat/schema acceptance, exact parsed fields, usage, latency and failure behavior |

Sources: [Prisma REST](https://docs.gnani.ai/api/STT/speech-to-text), [Timbre REST](https://docs.gnani.ai/api/TTS/tts-inference), [Gemini model](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [generateContent reference](https://ai.google.dev/api/generate-content), [structured output](https://ai.google.dev/gemini-api/docs/structured-output).

Rechecked 31 October: the [Prisma REST reference](https://docs.gnani.ai/api/STT/speech-to-text) lists WAV, MP3, OGG, FLAC, AAC and M4A with a **30-second maximum**, superseding the earlier 60-second note. The accepted browser contract is mono 16 kHz/16-bit PCM WAV, at most 960,044 bytes. This byte ceiling is derived from our canonical PCM format, not a published provider upload-size limit. Browser capture and server validation are implemented and tested with a Chrome synthetic device; human acoustic quality and other devices remain unverified. Synthetic audio must not be reported as a human microphone test.

The model page lists LOW/MEDIUM/HIGH thinking; MINIMAL is unsupported. The JSON schema does not establish semantic correctness, and Google's structured-output documentation says string length constraints require application-side enforcement. The local validator enforces them. Account testing must pin the observed successful model/API/prompt/schema combination before production integration.

## Offline preparation

From the repository root:

```sh
.venv/bin/python -m scripts.prepare_provider_probes
```

This creates ignored `artifacts/provider-probes/` JSON files: six extraction requests, hand-labelled expectations, the generated schema, a Timbre request and a manifest. It reads no secrets and performs no network requests. Request payloads are provisional; successful local generation is not evidence of API acceptance.

The six cases cover correction, explicit removal, completed status, native-script quantity, spoken-job mismatch and ambiguity. They are development probes, not a held-out evaluation set. Review semantically equivalent text separately from exact scalar/operation matches. A model's correct proposal does not establish that the application saved correctly.

## Live command and next session

### Latest result — 1 November 2026

The rendered [official free-tier status](https://aistudio.google.com/status?tier=free) reported all free-tier systems operational. After that new recovery evidence, the final approved fictional correction request still returned HTTP 503 in 7.855 seconds. Report: `artifacts/provider-probes/gemini-20261101T182137344275Z.json`. No retry followed. **All six original attempts are consumed** (one sandbox failure, one metadata GET, four generation failures); zero successful extraction responses. Public status does not establish account-specific inference access. The [troubleshooting guide](https://ai.google.dev/gemini-api/docs/troubleshooting) also distinguishes metadata access from project tier/billing eligibility; no account restriction or root cause is inferred from this 503 alone.

Ankit subsequently approved up to two additional requests for the prepared diagnostic. Executed:

```sh
.venv/bin/python -m scripts.diagnose_gemini --live --max-requests 2 --env-file .env
```

This command first asks the same model for exactly READY, with LOW thinking and 256 output tokens, without a schema/system prompt. Only a complete matching response permits the second request: the existing structured quantity-correction fixture. Both share a two-request maximum; any provider error or unexpected plain response stops the run. No automatic retry, model change, billing change or live Gnani request is involved. A started-attempt report is written before networking and updated afterward. Outcomes can narrow the investigation, but two calls under changing service load cannot conclusively attribute a failure to the schema.

Actual result: plain generation returned HTTP 503 in 5.663 seconds. Stopped after **one request**; structured extraction was not attempted. Report: `artifacts/provider-probes/gemini-isolation-20261101T182744000377Z.json`. This reproduces the failure without the app's extraction prompt/schema; it does not determine whether account access, model availability or capacity is responsible. Across approvals, seven attempts are counted: one sandbox failure, one metadata GET and five generation 503 responses. The second diagnostic request remains unused, conditional on a success that did not occur; it is not an allowance for an automatic retry or changed model. Next check project access/quota and model availability without another generation call.

STT/TTS access has earlier live evidence. Adapters, guarded STT-to-extraction orchestration and browser capture/playback now have offline tests. The local runner can connect Gnani only with a separate explicit speech request allowance; no fresh provider calls occurred during browser voice implementation. The Gemini command is:

```sh
.venv/bin/python -m scripts.probe_gemini --live --max-requests 1 --env-file .env
```

The original probe command does not run without --live; its default limit is one and maximum is six per invocation. It stops on the first provider error, saves a redacted timestamped report after each result and never receives Store or a save tool. Environment GEMINI_API_KEY takes precedence over the explicitly supplied file. All six approved attempts are now conservatively counted (including the metadata GET). Earlier generation failures were diagnosed as UNAVAILABLE with a capacity/demand indication; no paid tier, billing change, model substitution or further request is authorized by that failure.

Normal pytest remains offline; no live provider-marked pytest tests exist. Successful real extraction and a complete real Gnani/Gemini browser task remain unverified. Response ordering and browser behavior have fixture-backed evidence; they do not establish acoustic or extraction quality. The next live session should establish one accepted extraction before expanding the development cases, with a separately reported held-out evaluation later.
