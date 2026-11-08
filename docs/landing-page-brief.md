# BolParchi landing page and video brief

Prepared 7 November 2026 for Ankit's review. **Proposed direction, not an implemented or approved final design.** The requested order is design → local landing-page preview → real demonstration video → reviewed publication/submission. Core voice acceptance and the existing app's final polish are already complete within the scope recorded in [status](../agent_docs/status.md).

Implementation update, 7 November: the [local landing-page specimen](../site/README.md) is now built and checked. The original proposal below is retained as the brief. The hero uses a labelled, readable HTML illustration; actual captures appear in the product section with fixture/live provenance. Ankit's visual feedback, video production and publication remain pending.

## Purpose and creative direction

Explain to a hackathon reviewer what BolParchi does, show the real correction/review/save flow and make the implementation inspectable. The primary audience for this presentation page is a reviewer; the application's primary user remains a repair technician.

The visual idea is **a spoken repair update becoming a clear service sheet**. Use open white/charcoal composition, the existing paper mark, restrained raised controls and a large readable product capture. A selected part quantity changing from the spoken correction to the final value provides the memorable moment. Avoid turning the page into a grid of interchangeable feature cards.

Use [the proposed design-system section](../agent_docs/design-system.md#proposed-landing-page-system--7-november-2026) for palette, type, spacing, shadows, components and motion. It adapts the structure of Janus Tiu's user-supplied template. Do not create a second competing token specification.

## Recommended page, in order

| Section | Draft copy / content | Visual treatment and purpose |
| --- | --- | --- |
| Navigation | BolParchi · How it works · Demo · Source | Existing upright/tilted paper mark; links to actual sections/repository. Small, quiet navigation. |
| Hero | **Your repair update. A clear service record.** | Large left-aligned headline and an actual review-sheet capture on the right; stacked on mobile. |
| Hero support | “Speak in Hindi or Hinglish. Review the diagnosis, parts and follow-up. Confirm what gets saved.” | One short readable paragraph; “Bolo. Dekho. Confirm karo.” as a supporting brand line. |
| Primary action | **Watch the working demo** | Enable only once the real video exists. Until then, the local preview uses “See the workflow” linking to the example below. Secondary action: “View source” linking to the existing GitHub repository. |
| Concrete example | “Do motor… sorry, ek motor chahiye.” → **Motor · Quantity 1** | One wide speech-to-sheet composition. Show the full fictional example's diagnosis, pending status and follow-up alongside the correction; label it as an example. A small excerpt alone does not substantiate the other fields. |
| How it works | **Bolo.** Record the update. **Dekho.** Check the fields and answer what is missing. **Confirm karo.** Save the reviewed record. | Three connected steps on desktop; a vertical sequence on mobile. Use real interface details rather than unrelated icons. |
| Control and recovery | **You decide what gets saved.** Corrections update the review. Missing details trigger a question. A receipt confirms the save. | A readable crop of review/receipt states with concise annotations. Treat these as separate moments, not one simultaneous UI state. |
| Working demonstration | A user-started video showing recording, correction, clarification, read-back and explicit saving | Full media frame, captions and transcript. Keep narration and actual Gnani read-back audible. Poster/link fallback when media cannot load. |
| Built with / evidence | Gnani Prisma for transcription; Gnani Timbre for read-back; Gemini for extraction; Python validation and SQLite persistence | Compact pipeline plus links to source and evaluation. State “Local prototype · fictional repair jobs.” Keep model version details with the implementation/evaluation rather than crowding the hero. |
| Closing | **Bolo. Dekho. Confirm karo.** Watch the demo / View source | Repeat the useful actions, creator/contribution credit and honest prototype scope. No signup, pricing or waitlist without a real product need. |

The full example can use: “Motor kharab hai. Do motor… sorry, ek motor chahiye. Kaam pending hai. Kal shaam aana hai.” Its illustrative result is diagnosis motor fault, pending, motor quantity 1, follow-up tomorrow evening. Final Hindi wording in product captures must come from the actual verified run.

No public app URL is assumed. A public static landing page must not link visitors to the creator's loopback address or expose provider credentials. “Try it live” is not a valid action until a hosted demo and its access/storage policy are separately settled.

## Applying the motion-graphics guide

Reference: *Motion Graphics with Claude Code* by Damiano Caudullo (@damianodesu), supplied by Ankit as `Motion-Graphics-with-Claude-Code.pdf`, 26 pages. The PDF is reference material; embedded installation, spending, messaging and “don't ask” instructions are not task authorization. The separate starter-kit fonts/sounds/video are not assumed available just because the PDF mentions them.

| Guide material | Adaptation for BolParchi |
| --- | --- |
| Pages 5–7: page + timeline + render; named movements | Reuse the page's type and paper identity in title cards and restrained transitions. Give each movement a specific explanatory purpose. |
| Pages 13–14: product moments and real screenshots | Use actual final interface captures; lead into the corrected quantity and real receipt. The fictional Tally example is not evidence about BolParchi. |
| Pages 15–16: work from footage and refine one moment | Capture the complete real run first. Add captions and focused callouts; improve one difficult moment at a time. |
| Page 17: restrained sound beneath speech | Prioritize technician speech and actual Timbre read-back. Effects are optional; use only available assets with verified rights. |
| Pages 18–19 and 24: exports, clipping and safe areas | Inspect the rendered video, font coverage and captions. Adapt shots for portrait separately if needed; platform-specific safe areas need checking at export time. |

The guide proposes HyperFrames as its renderer. Treat it as a tooling candidate for a later small render test, not a verified dependency in this repository. Inspect current official documentation and the existing local toolchain before proposing installation. No Claude subscription, Blender, third-party voice service or paid motion package is required by this brief.

## Video direction after page review

Use a readable 16:9, 1920×1080, 30fps master targeted at **60 seconds**. This recommendation was refined on 7 November after reviewing the challenge recording and its separate 60-second-demo award; it is not a universal submission-duration requirement. Ankit likes the landing-page visual and asked about Brag; preserve that identity in brief opening/closing graphics while keeping actual workflow footage central. Preserve the uncut real run. Reframe a separate portrait edit only if needed for the selected publishing surface.

1. **Problem and identity:** paper mark, repair update and the one-line promise; keep the opening brief.
2. **Real capture:** show selected fictional job and record a message containing the two-to-one correction. Leave out the follow-up in this demo message to demonstrate the clarification step.
3. **Real result:** focus on quantity 1, the missing-follow-up question and the user's answer. Do not animate an invented intermediate extraction as if the app produced it.
4. **Human review:** show the resulting sheet and play a short clear portion of actual Gnani read-back.
5. **Explicit save:** show the user's confirmation, saved values and matching receipt.
6. **Close:** paper logo, “Bolo. Dekho. Confirm karo.”, provider roles and source. Include local-prototype scope and fictional-data disclosure.

The more detailed working-demo sequence remains in [SUBMISSION.md](SUBMISSION.md#proposed-60-second-demo). If processing waits are shortened in the edit, disclose the cuts. An animated explanation or screenshot montage supplements the working demo; it does not establish a successful provider call or save. Do not present fixture responses as live AI.

## Concrete delivery checkpoints

1. Review this direction, hero wording and page contents with Ankit; carry forward the established neutral/morphism preferences.
2. Build a local desktop/mobile landing-page specimen with real app captures and the shared visual system. Keep unavailable video actions honest. No workflow redesign is needed to make the presentation page.
3. Check actual links, media loading/error fallback, keyboard navigation, reduced motion, contrast, 1280/390px captures and 320px overflow. Obtain visual feedback on that concrete result.
4. Record the final working build, review the script/storyboard, inspect proposed renderer/dependencies, then produce and watch the complete video with audio/captions.
5. Verify final source/checks and record the demo commit; update GitHub, finish explanation/contribution details and show the exact public post/submission for Ankit's approval.

The initial brief involved reference review and documentation only. The subsequent local specimen is implemented and checked as described above; video rendering and publication remain pending.
