# BolParchi AI — Solution Pitch

Repair technicians describe a visit in a short Hindi/Hinglish voice message. The shop still needs a clear record: fault, job status, part, quantity, next visit. Someone has to replay the audio, spot what is missing, and type it in. BolParchi exists for that handoff.

Built for appliance-repair technicians in small shops. The owner inspects the same record in the prototype. V1 uses fictional jobs only; no staff roles, no integrations.

The technician selects a known job, speaks or types the update, reviews the sheet, hears it read back, and presses Confirm and save. That button is the only write path. The job stays fixed for the draft, the app asks one relevant question when details are missing, and corrections update the draft and cancel prior approval. Recordings are capped at 30 seconds, held in memory, and an uncertain save stays locked until its outcome is known.

Gnani Prisma transcribes the recording (REST /stt/v3, default Prisma v2.5, Hindi input). Gemini 3.5 Flash-Lite (REST v1beta, LOW thinking, prompt bolparchi-field-decisions-v2, wire schema v1) proposes a structured patch with one decision per field. Python validates it, keeps the selected job fixed, and asks the follow-up. Gnani Timbre v2.5 (Nalini voice, 48 kHz mono PCM WAV) reads the reviewed record aloud. The model never saves; only Confirm creates the SQLite record and receipt.

Evidence, small and exact: 424 offline tests pass. One live typed browser task completed three Gemini extractions, real Timbre playback, and a confirmed save with quantity 1 (receipt 56956688-5940-45ce-8d73-9aebf1f66e15, from messages ending in quantity correction "Do nahi, ek motor"). One retained human recording passed STT, extraction, read-back, and saved receipt. One fresh microphone task passed with clear playback reported and receipt 5bb647c0 verified for quantity 1 and follow-up kal shaam. Frozen evaluation: six cases attempted once each, five exact patch matches, one HTTP 503, zero semantic mismatches among returned patches; a separate unchanged recheck of the unavailable uncertainty case passed. A previous prompt omitted a stated follow-up and validation blocked the save; human review remains essential. These are scoped runs, not general accuracy or availability.

Limits: fictional data, one user and one device, no technician study, no time-savings claim, intermittent provider 503s, no public demo or uncut video yet.

I, Ankit Singh, own product decisions, architecture review, and acceptance, and I ran the live microphone task. Codex assisted implementation, tests, and docs under my review. Source: github.com/ankitks1209/bolparchi-ai.
