# BolParchi AI — 2.5-minute demo script

Read aloud in simple words. Timings are speaking cues, not measured app performance. All facts below come from docs/SUBMISSION.md, docs/EVALUATION.md, README.md, and agent_docs/status.md. Fictional data only. No invented numbers.

## 0:00-0:20 — Problem

"Repair technicians finish a visit and speak a short update in Hindi or Hinglish. The shop still needs a clear record: the fault, job status, part, quantity, and next visit. Someone has to replay the message, find what is missing, and type it in. I built BolParchi for that handoff. It is for technicians in small repair shops. The owner checks the same record. Bolo. Dekho. Confirm karo."

## 0:20-1:30 — Live demo

[Select fictional job 104, Washing machine.]

"I select job 104. The job stays fixed for this draft. Now I speak."

[Record: "Motor kharab hai. Do motor... sorry, ek motor chahiye. Kaam pending hai."]

"The app shows my words and keeps the correction as one motor. It asks one question because the next visit is missing. I answer."

[Answer: "Kal shaam aana hai."]

"Now the sheet is complete. I can still correct it. I press Listen to review to hear it back. Nothing is saved yet. The screen says: nothing is saved until you confirm. I press Confirm and save once. The app shows the saved values and the receipt. That is the only way anything saves."

## 1:30-2:05 — How it works

"Gnani Prisma turns my recording into text. Gemini proposes a structured patch, one decision for each field. Python checks it, keeps job 104 fixed, and asks the missing question. Gnani Timbre reads the reviewed record aloud. The model only proposes. It cannot save. Only my Confirm creates the record and receipt in SQLite. Recordings are capped at 30 seconds and held in memory. If a save outcome is uncertain, editing stays locked until we know."

## 2:05-2:25 — Evidence and limits

"Small and exact. 424 offline tests pass. One live typed task did three extractions, real read-back, and saved quantity 1. One retained recording passed transcription, extraction, read-back, and saving. One fresh microphone task passed with clear playback and receipt 5bb647c0 for quantity 1. Frozen test: six cases, five exact matches, one provider 503, no wrong patches among the five. Limits: fictional data, one user and one device, no technician study, provider 503s happen, no time saved claimed."

## 2:25-2:30 — Close

"BolParchi: speak, clarify, confirm. I own the product and decisions; Codex assisted the build under my review."
