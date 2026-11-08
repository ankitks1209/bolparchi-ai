# BolParchi submission draft

Updated 7 November 2026. Draft for Ankit's review; not submitted or published. Real-provider retained-audio backend acceptance has passed. One user-operated browser microphone task has passed with clear recording/playback reported by Ankit, and final UI polish has passed scoped checks. Ankit likes the local landing-page visual; carry that direction into the demo. The actual demo video and final source update remain pending.

## Verified submission requirements

The [official challenge page](https://www.gnani.ai/internship) and [participation terms](https://www.gnani.ai/great-indian-ai-internship-registration-form), rechecked 7 November alongside Ankit's screen recording, state a final deadline of **10 November 2026, 11:59 PM IST**. Use the explicit date; the page's countdown was inconsistent with the current date. Timestamped extraction and implications are in [the recording notes](challenge-recording-notes.md).

Prepare a working application video, written project explanation, named Gnani models/APIs and participant contributions. Post the working video publicly on LinkedIn or X, tag Gnani AI and include `#GnaniAI` and `#GreatIndianAIInternshipChallenge`; nominate one post per platform in the final submission. Use the submission instructions in the registration email. A public source repository alone does not complete the entry. The public-video requirement does not by itself require deploying this local app.

Publication and final submission wait for Ankit's review and explicit approval. No engagement automation or claims of guaranteed selection.

The post must be public **before** final submission. The current FAQ says the submission form is sent by email and there is no participant workspace, although the terms retain a workspace reference. Use the actual emailed instructions and clarify any conflict; a registration confirmation is not a final-entry receipt.

Verified engagement on nominated posts before the cutoff drives the eligible-project interview shortlist; no numeric weighting was found. Awards are separate, including one for the best 60-second demo. Keep the main edit targeted at **60 seconds** and retain uncut evidence; this is our recommended category strategy, not a universal duration rule. Brag may provide short opening/closing graphics or a separate teaser, but recreated UI cannot establish live provider/save success. Misleading demos, paid promotion, purchased engagement, bots and engagement exchanges are prohibited.

## Project explanation

**BolParchi — Bolo. Dekho. Confirm karo.**

Repair technicians often describe a visit in a short voice message. The business still needs a clear record of the fault, job status, required part, quantity and next visit. BolParchi turns a Hindi/Hinglish update into a service sheet, asks for missing details and lets the technician correct and confirm it.

Gnani Prisma transcribes the recording. Gemini proposes a structured patch. Python validates it, keeps the selected job fixed and asks one relevant follow-up question. Gnani Timbre reads the reviewed record aloud. Only the user's Confirm and save action can create the durable SQLite record and receipt. Corrections invalidate previous approval, and an uncertain save stays locked until its outcome is known.

The prototype uses fictional repair jobs and runs locally. Recordings are limited to 30 seconds and held in application memory; provider retention is separate. Provider keys stay on the server. This is a controlled workflow with model-assisted extraction, not an autonomous model with write tools.

## Technology and contribution disclosure

- Gnani Prisma REST `/stt/v3`, default Prisma v2.5, Hindi input; actual successful response version must be recorded for the final walkthrough.
- Gnani Timbre v2.5, Nalini voice, Hindi PCM WAV read-back.
- Gemini 3.5 Flash-Lite, REST v1beta, LOW thinking, prompt `bolparchi-field-decisions-v2`, wire schema `bolparchi-field-decisions-v1`, Python-validated JSON patch.
- Python, FastAPI/Uvicorn, SQLite and native browser HTML/CSS/JavaScript with AudioWorklet capture.
- Ankit owns the product decisions, architecture review and acceptance. Codex assisted implementation, tests and technical documentation. Ankit should review this contribution description and be prepared to explain the flow and tradeoffs himself.

Source: [ankitks1209/bolparchi-ai](https://github.com/ankitks1209/bolparchi-ai). Current results and limitations belong in [EVALUATION.md](EVALUATION.md); do not quote a test count from an older recording.

## Proposed 60-second demo

| Time | Real action and explanation |
| --- | --- |
| 0–7s | Show fictional job 104. Explain: a repair update should become an inspectable record. |
| 7–22s | Record: “Motor kharab hai. Do motor… sorry, ek motor chahiye. Kaam pending hai.” Show the actual transcript and quantity 1. |
| 22–35s | Show the missing follow-up question. Answer: “Kal shaam aana hai.” Show the complete service sheet. |
| 35–47s | Play a short portion of the real Timbre review. Explain that corrections remain possible and nothing is saved yet. |
| 47–57s | Press Confirm and save once. Show the saved quantity and receipt. |
| 57–60s | Name Prisma, Timbre and Gemini; show the repository and prototype limitations. |

These are target timings, not measured performance. Retain an uncut real run. If shortening processing waits for the public edit, label the time cuts; never replace a failed provider call with fixture output. Audio replay used in automated testing must be labelled replay, not a fresh microphone task.

## Before publishing

- Verify registration eligibility/details and locate the final-submission email/form. Personal-email access does not waive current-enrolment or age requirements.
- Use the verified microphone device and capture a new real task on the polished build; retain the original human acceptance evidence.
- Final Unslop polish is implemented and checked; retain its attribution in project documentation and capture the actual final interface.
- Confirm the latest checks and record the exact commit used for the demo.
- Review the result with a technician or shop owner if available; otherwise state that user validation remains pending. Do not invent time savings.
- Review the video, explanation, model names, limitations and contribution statement with Ankit.
- Obtain Ankit's approval for the actual public post; then add its URL to the final submission and keep the submission receipt.
