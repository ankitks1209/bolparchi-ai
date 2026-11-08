# BolParchi video reference and production brief

Prepared 7 November 2026. Reference analysis and proposed storyboard, not a rendered video or an approved new tool installation. Product scope remains in [spec.md](spec.md), visual tokens in [the design system](../agent_docs/design-system.md), and submission requirements in [SUBMISSION.md](SUBMISSION.md).

## Reference evidence

Ankit supplied `Screen Recording 2026-11-07 at 11.41.03 AM.mov` and asked whether its style could be recreated. The local recording is 45.84 seconds, with one video and one audio track. It includes Instagram browsing/chrome around the creative. Its duration is not necessarily the complete original advertisement's duration.

Sampled visual evidence is retained privately under ignored `artifacts/video-style-reference-20261107/`. Reviewed frames at 0, 5.73, 17.19, 22.92, 28.65, 34.38 and 40.11 seconds establish the following observations. This is not a frame-by-frame timing or audio analysis; the audio has not been listened to or transcribed.

| Recording time | Visible evidence | Useful adaptation |
| --- | --- | --- |
| 0s | Instagram portfolio grid, then a selected reel | Exclude browser/social chrome from our export |
| 5.73s | Large white rounded panel, short centered phrase, purple edge treatment; Intro / Problem / Use Case / Call to Action markers | A consistent stage and short phrases; retain BolParchi's approved neutral palette |
| 17.19s | Product identity over a landscape scene inside the same panel | A distinct product reveal; use our paper logo and service sheet |
| 22.92s | Translucent input panel over the landscape | Restrained layered surfaces and close attention to one interaction |
| 28.65s | Individual words at staggered vertical positions | Word-by-word entrance with controlled settling; exact easing remains unmeasured |
| 34.38s | Angled phone showing a QR-scanning interface | Gentle perspective for introductory product shots; keep evidence footage readable |
| 40.11s | Short blurred closing phrase; final chapter active | Brief focus transition into a legible closing line |

The visible portfolio account is `sultanmotions`; the work includes Sleeko/HowDo branding. These are reference observations, not our assets or credits. Do not reuse their footage, logos, landscape, soundtrack or voice in our export without appropriate permission/assets. We can implement comparable motion techniques with original BolParchi content. A frame-identical copy is not promised from sparse frames without original source, fonts and timing information.

Ankit reports the toolchain as Claude Code + Remotion + WhisperX + Hyperframes + Fish Audio/ElevenLabs. Treat that as user-supplied provenance, not independently established authorship. His message ends “And give this video to claude as a”; do not invent the missing instruction.

## Proposed tool choice

Use one primary renderer for the first proof. **Hyperframes remains the preferred starting candidate**, consistent with the earlier guide and Brag discussion. Brag can guide the opening/closing story; a custom composition should retain the longer real demonstration. [Brag's official repository](https://github.com/latent-spaces/brag) documents its Hyperframes pipeline, Node 22+, FFmpeg and CLI requirements. No installation or render has occurred.

[Remotion](https://www.remotion.dev/docs/) is an alternative for a React-based composition, with video/audio, captions and rendering support. Using both renderers is not necessary to reproduce the visible treatment. Change the recommendation only if a small render proof exposes a concrete limitation.

[WhisperX](https://github.com/m-bain/whisperX) supplies transcription and word-level alignment. It is optional for this short, scripted piece: manually time and review captions initially, particularly Hinglish and corrections. Caption the words actually heard, not an idealized script.

For narration, first consider Ankit's own voice or the existing Gnani Timbre integration after a listening test. Keep actual technician speech and actual product read-back in the evidence segment. Fish Audio/ElevenLabs are optional alternatives, with no account, voice choice, license or spend assumed. Narration must not cover the moment being demonstrated.

The existing local inspection found Node 24.18.0, but no FFmpeg/Hyperframes on PATH. Review concrete versions and install scope before requesting approval under AGENTS.md. Do not run external setup commands merely because a reference recommends them.

## Proposed 60-second master

1920×1080, 30fps, based on the approved landing-page identity. These are editorial allocations to test against actual captured timings, not claims about provider latency. Preserve the uncut source recording and disclose shortened waits. If clarity cannot fit 60 seconds, retain a readable full walkthrough and produce a separate short cut.

| Time | Picture and motion | Audio / message |
| --- | --- | --- |
| 0–4s | Upright paper mark tilts; title resolves into focus | “A repair update. In your own words.” |
| 4–9s | A short illustrative speech line becomes a service-sheet outline | Introduce Hindi/Hinglish visit updates; label illustration |
| 9–22s | Actual final-build recording: selected fictional job, recording control, spoken correction | Real “Do motor… sorry, ek motor chahiye” within the complete update |
| 22–34s | Actual extraction review; close-up on quantity 1, missing follow-up question and entered answer | Explain the correction and request for missing information without inventing model output |
| 34–44s | Actual reviewed sheet and Listen to review action | Audible excerpt of actual Gnani read-back; narration stops |
| 44–53s | Actual Confirm and save action, then saved values and receipt | “Reviewed by you. Saved after confirmation.” |
| 53–60s | Paper logo settles; simple source/provider credit | “Bolo. Dekho. Confirm karo.” Local prototype; fictional jobs |

Motion targets for the proof: short phrase entrances, restrained blur-to-focus, smooth easing and a subtle panel tilt. Use flat, readable product footage during important actions. A proposed neutral chapter rail can read Bolo / Dekho / Confirm; it is an editorial overlay, not application UI. Keep text within safe margins and inspect at phone viewing size. Use the same type and palette as the landing page.

## Next concrete deliverables

1. An 8–10-second local motion proof: logo → spoken correction → service sheet. Use labelled illustrative content until actual footage is available.
2. Review timing and readability, then capture the complete real workflow on the final app build. Existing human acceptance proves a scoped run but is not an uncut submission video.
3. Assemble the 60-second edit with captions, balanced audio, actual footage, credits and a poster. Inspect the rendered export and compare it against the storyboard.
4. Connect the completed video to the local landing page, then review the concrete public post/submission separately. Publication remains subject to Ankit's fresh explicit approval.
