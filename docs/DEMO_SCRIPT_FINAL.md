# BolParchi AI — Final demo script (2:30-2:45)

Facts only from site/index.html, SOLUTION_PITCH.md, docs/EVALUATION.md, docs/DEMO_SCRIPT_3MIN.md. Fictional data. No invented numbers. Keep "illustration" labels visible on screen. Add a "trimmed waiting time" line only if waiting is trimmed.

## Preview command (local only, no publish/deploy)

```sh
.venv/bin/python -m http.server 8772 --bind 127.0.0.1 --directory site
```

Open http://127.0.0.1:8772/. Serve only that directory. Stop with Ctrl-C.

## Landing page sections in scroll order

1. Hero: "Your repair update. A clear service record." — ILLUSTRATION (HTML service sheet, labelled "Illustrative service sheet").
2. Strip: "For the details that matter after a visit." — text only.
3. "A small correction. A different part request." — ILLUSTRATION (Hinglish quote + Motor quantity 1, labelled "An illustrative Hinglish update").
4. Steps: Bolo. / Dekho. / Confirm karo. — text only.
5. "It's a draft. Until you say so." — text only.
6. "The details, in plain sight." — REAL CAPTURES (service-sheet.png: fixture interface job 104; voice-receipt.png: real-provider receipt before polish, labelled as such).
7. "Voice assistance. Explicit confirmation." — text pipeline (Prisma / Gemini / Timbre / Python + SQLite).
8. Closing: "Bolo. Dekho. Confirm karo." — text only.

## Intro (~30s, narration over landing page, hero through correction)

| Section | Scroll cue | Narration | s |
|---|---|---|---|
| Hero | Top of page | "I am Ankit. Repair technicians speak a short Hindi update after a visit, and the shop still needs a clear record of the visit. I built BolParchi for that handoff, for technicians in small shops." | 12 |
| Correction | Scroll to Motor 1 | "Say two motors, correct to one, and the sheet keeps quantity one. This page example is an illustration with fictional data for review." | 12 |
| Bolo Dekho Confirm | Steps row | "Bolo, record it in your own words. Dekho, check the sheet and answer what is missing. Confirm karo, save the reviewed record only after you agree." | 10 |

## Live demo (~70s, no narration)

1. Select fictional job 104, Washing machine.
2. Record: "Motor kharab hai. Do motor... sorry, ek motor chahiye. Kaam pending hai."
3. Show transcript; quantity keeps correction as 1.
4. Show follow-up question; answer: "Kal shaam aana hai."
5. Show complete sheet with all five fields.
6. Press Listen to review; show read-back text on screen; do not claim audio quality not captured.
7. Press Confirm and save once; show saved values and receipt.

## Outro (~55s, narration over lower landing page, ending on closing card)

| Section | Scroll cue | Narration | s |
|---|---|---|---|
| Details in plain sight | Fixture sheet | "This is the real interface with fictional data, job 104. Gnani Prisma makes the transcript. Gnani Timbre reads the review back, and I can still correct it." | 15 |
| Voice assistance | Pipeline row | "Gemini proposes the patch, one decision per field. Python checks it, keeps the job fixed, and only my Confirm saves it with a receipt." | 14 |
| Evidence | Stay on pipeline | "424 offline tests pass. Frozen test: six cases, five exact matches, one provider 503, zero wrong patches among the five. One user and one device, no technician study yet, and provider availability can vary." | 15 |
| Closing card | Bolo Dekho Confirm karo | "BolParchi: speak, clarify, confirm. I directed the work and ran the acceptance tasks. Codex and Cline assisted. Source is linked from this page." | 15 |

Narration total: ~195 words at ~130 wpm (~90s with intro + outro).
