# Design-system constraints

## Visual direction selected — 7 November 2026

After viewing the local landing-page preview, Ankit said “okay i like the visual” and asked about Brag for the working demo. Carry this neutral, tactile-paper direction into the video. This records the user's visual preference; it does not authorize publication or imply the pending video was reviewed. The specimen and checks below remain the implementation evidence.

## Landing-page specimen implemented — 7 November 2026

The local `site/` preview implements the proposed system below. Its hero uses a clearly labelled HTML illustration so Hindi fields and the quantity correction remain readable at mobile widths; unmodified actual interface captures appear in the product section. This deliberately separates explanation from evidence. The monochrome states, token scale, paper layering and nine-degree navigation logo are implemented. Desktop/mobile and narrow overflow checks passed; keyboard/drawer/evidence interactions and missing-image recovery were exercised. Source and provenance: [site README](../site/README.md). Captures: `artifacts/landing-20261107/`. This is a candidate for Ankit's visual feedback, not a claim of final preference approval. The working demo video remains pending.

## Proposed landing-page system — 7 November 2026

Ankit requested a design and landing page before producing the submission video, using Janus Tiu's supplied design-system template. This section adapts its structure to BolParchi's existing identity; it is a proposal for a rendered preview, not approval of an unseen page. The Retro Groovy example is not the selected palette. The app's existing service-sheet workflow remains the product surface; the proposed landing page explains that product to reviewers. Earlier advice below to avoid a promotional landing page applies to the technician's task screen, not this newly requested presentation page.

**Brief:** Build a Hindi/Hinglish repair-record product with a minimal white/charcoal identity, tactile paper surfaces and restrained morphism. Give the spoken correction and resulting service sheet the visual emphasis. Use the existing paper logo rather than a new mascot or stock illustration. Landing-page content and video sequencing live in [the landing-page brief](../docs/landing-page-brief.md); this file remains the authoritative visual reference.

### Color palette

| Token | Proposed value | Use |
| --- | --- | --- |
| Primary | `#202020` | Main action, focus ring and key emphasis |
| Secondary | `#F5F5F5` | Quiet supporting surfaces/actions with charcoal text |
| Background | `#F5F5F5` | Page canvas |
| Surface | `#FFFFFF` | Service sheet, inputs and navigation |
| Text primary | `#202020` | Headlines and body |
| Text secondary | `#666666` | Captions and supporting copy |
| Border subtle | `#E5E5E5` | Decorative rules, not the sole control boundary |
| Border control | `#808080` | Input/control boundaries |
| Success / warning / error ink | `#202020` | Distinct icon and explicit text distinguish each state |
| State surface | `#F5F5F5` | State messages with visible border/label |

Keep semantic tokens separate even where their values match. Monochrome must not collapse “Saved”, “Needs your review” and “Could not process” into indistinguishable messages. Do not reintroduce blue/green or adopt the template's orange/purple. Shadows and existing logo bevels may use neutral alpha variants; verify contrast on the actual rendered surfaces.

### Typography and spacing

- Retain `"Avenir Next", -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans Devanagari", sans-serif`. A Google Font is not mandatory: it would introduce a new asset/loading decision without a demonstrated need. Inspect both scripts on the preview device.
- Landing headings: weight 600–700, tight Latin tracking; body weight 400, controls 600. Do not apply tight Latin tracking to Devanagari. Body line height 1.5; headline 1.1–1.2.
- Size scale: 12 / 14 / 16 / 20 / 24 / 32 / 40 / 48 / 64px. The 64px extension is for the desktop hero; mobile hero starts at 40px and must wrap naturally. Record values remain at least 16px; avoid shrinking an entire screenshot until fields become illegible.
- Spacing: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96px. The 96px extension is for major desktop section separation; mobile sections use 48–64px. Structural widths, borders and existing logo geometry are explicit exceptions, not arbitrary spacing.
- Proposed landing content maximum 1120px, outer gutter 32px desktop / 16px mobile. Stack the hero on narrow screens, in reading order: promise, explanation, action, product evidence.

### Shape, shadows and components

- Radius: 8px small labels; 12px inputs/buttons; 16px sheet; 24px large media frame. Preserve the existing paper logo's asymmetric corner. Pills only where the content warrants them.
- Shadows: subtle `0 1px 2px rgba(0,0,0,.05)`; medium `0 4px 12px rgba(0,0,0,.08)`; strong `0 12px 32px rgba(0,0,0,.10)`. Reserve strong elevation for the hero sheet or open drawer; do not shadow every section.
- Primary buttons: charcoal/white, minimum 48px high, 12px vertical / 24px horizontal padding, 12px radius. Secondary buttons: white, charcoal text and visible control border. Clear hover/focus/pressed states; no layout shift or compulsory scale bounce.
- Inputs: minimum 48px high, 12–16px padding, persistent label, 2px charcoal focus outline with offset. Existing textarea and workflow semantics remain authoritative.
- Cards: use only for the service sheet, media frame or a genuinely grouped example. Start with 24px padding, a subtle border and one elevation level. Use open typography/rules for surrounding narrative.
- Hero artwork: an actual app capture, with a readable crop of the corrected quantity and follow-up if necessary. Explicitly label any separate animated explanation as an illustrative example. Do not manufacture live status, waveform activity or receipt evidence.

### Motion and consistency rules

1. The paper mark stays upright at rest and tilts nine degrees when its navigation drawer opens. Navigation links must have real destinations; preserve keyboard focus, Escape/backdrop dismissal and reduced motion.
2. Carry the app's 260ms drawer timing and `cubic-bezier(.2,.8,.2,1)` into matching interactions. Limit other transitions to purposeful opacity/translation around 160–260ms. No scroll hijacking or perpetual floating cards.
3. Repeat the same tokens across landing page, app references and video title/caption cards. Product footage retains the actual UI.
4. Use sentence case and concrete actions. No invented usage counts, endorsements, time savings or universal accuracy claims.
5. Inspect desktop/mobile, long Hinglish/Devanagari, keyboard focus, reduced motion, media fallback and overflow before calling the page verified. Target at least 4.5:1 normal text and 3:1 large text/control boundaries.

## Final polish completed — 6 November 2026

Applied a focused Unslop pass after Ankit's successful microphone task, preserving the neutral palette, paper identity and animated logo. Changes and attribution to Damir Sokolovsky (CC BY 4.0) are in [the polish review](unslop-review.md). Desktop/mobile review, error/recovery/clarification/correction/save and keyboard/sidebar checks passed with fixture providers. No runtime workflow behavior changed. The dated plan below is historical; the polish is now implemented, while the actual submission video remains pending.

## Original final-polish plan — 5 November 2026

Ankit explicitly selected [Unslop by Damir Sokolovsky](https://github.com/heydamir/unslop) for the **last UI polish pass**, after core provider/workflow validation and submission preparation. The skill is already installed locally. Do not start a redesign while resolving the core release blockers. Preserve the neutral white/charcoal palette, subtle morphism, service-sheet identity and functional upright/tilted sidebar logo. Begin with an audit of the actual desktop/mobile views; use focused polish unless evidence justifies a larger change. Retain attribution when copying/adapting the skill. Recheck interaction states, accessibility and the full test suite after polish, before recording the final submission video. This records the agreed order; no Unslop edits have been applied yet.

## Current interface

Status: the local typed/recorded Update screen is implemented; final visual acceptance remains open. Ankit rejected the blue Field sheet and green Focused sheet and requested a minimalist neutral direction. After seeing the working screen, he requested more visual character. The revision keeps monochrome rows and adds a job-number stamp, layered paper surface, small sheet-shaped brand mark and raised charcoal actions. See [design research](design-research.md) for earlier proposals and [working system](working-system.md) for review checkpoints.

Current implementation: `bolparchi/web/index.html`, `style.css` and `app.js`. Avenir Next is used when installed, with system/Devanagari fallbacks and no downloaded font. Decorative gradients/shadows have opaque surfaces underneath; status and control labels do not rely on shadows or colour. The introductory heading hides once a job is selected so the actual record gets priority. This is a revised candidate, not a claim that Ankit approved the final composition.

1 November logo interaction: Ankit requested a sidebar toggle, straight when closed and tilted when open. The sheet mark opens a neutral frosted left drawer in 260 ms and tilts nine degrees; closing returns it upright. The drawer shows current job/state and in-page shortcuts to update, review, receipt or fixture examples as available. It never changes the selected job, submits text or saves. Dialog semantics and keyboard wrapping keep focus inside; Escape, backdrop and the logo close it, returning focus appropriately. Reduced motion removes animation. The toggle is unavailable during capture so recording controls remain reachable; opening it stops read-back. Desktop/390/320 screenshots and interaction checks passed. Final visual acceptance remains Ankit's choice.

Voice controls extend the same neutral sheet: a raised full-width Record update control, textual timer/status, separate Stop and review/Discard controls, and secondary read-back playback with visible text. Fixture transcription/test-tone limits are labelled. The 1 November Chrome checks cover microphone denial, cancellation/late permission, empty-speech focus, obsolete playback and 1280/390/320 layouts. Captures were inspected for wrapping, readable fields, visible controls and the existing monochrome direction; the narrow sheet remains vertically scrollable. This is not human microphone validation or final technician usability acceptance.

The revised working screen's five representative text/control pairs were calculated against their background endpoints: minimum normal-text ratio 4.82:1, control-edge ratio 3.62:1, and white on the lightest charcoal button 11.55:1. Values and targets are retained in ignored `artifacts/browser/contrast.json`. This is a scoped colour check, not a full accessibility audit.

## Product shape

Latest preference, 27 October: Ankit requested a mix of morphism and minimalism and selected closer field spacing in the preview. Interpreted for this iteration as a neutral frosted sheet with soft raised recording controls, compact rows and a clear filled confirmation action. This interpretation is a preview, not final visual acceptance. The surface uses an opaque fallback when backdrop filtering is unavailable; input labels and control boundaries remain explicit. No blue or green accent was reintroduced.

Three views: Jobs, Update job, Saved record. Prioritize the selected job, input control, draft fields and next useful action. Keep the engineering trace panel collapsed in normal use. Use Roman-script Hinglish with English fallback; every spoken message must have visible text.

Use consistent spacing, typography, colors and reusable control styles. Avoid invented metrics, placeholder navigation or decorative dashboards that do not help the technician finish the task. Choose visual tokens once during the UI task and document them here after approval.

## Visual brief and decision record

The main screen's job is to help a technician turn a visit update into a reviewed record for the visibly selected job. Its hierarchy should make the job, current input/question, resulting fields and next action easy to find.

Proposed personality: practical, clear and reassuring. Avoid a promotional landing page, an admin console full of unrelated metrics or a chat transcript that hides the current record. These are task-based design criteria, not a claim that a specific palette is inherently good or bad.

| Choice | Candidate direction | Status |
| --- | --- | --- |
| Composition | Modern service sheet: visible job header, readable field rows and highlighted corrections | Selected by Ankit for the first preview on 24 October; final composition unreviewed |
| Alternative composition | Focused mobile assistant: one question/action with an always-accessible full review | Available for comparison |
| Alternative composition | Compact workbench: job list alongside the active update | Available for comparison; density needs mobile testing |
| Memorable element | A legible service-record sheet with one strong recording control | Included in the selected direction; exact treatment awaits preview |
| Palette and type | Neutral white/charcoal; readable Latin and Devanagari coverage | Minimalist direction requested; blue and green proposals rejected; exact tokens unapproved |
| Shape and motion | Subtle field grouping, deliberate borders, restrained action feedback | Not selected; no decorative motion required |

If Ankit offers references, record the specific property to borrow: density, hierarchy, typography or interaction. A whole reference product is not a template to copy. Without references, show small concrete alternatives. Record the selection and rationale here after feedback; do not relabel a recommendation as approved.

## Tokens and component structure for the first UI slice

Earlier preview candidates, both rejected by Ankit; retained as historical evidence:

| Candidate | Composition | Light palette and type |
| --- | --- | --- |
| Field sheet | Input/transcript beside review on desktop, stacked on mobile | Background #edf0f5, paper #ffffff, ink #18253b, muted #526079, accent #214ea5, control border #738198; system sans |
| Focused sheet | Centered review above correction input | Background #edf3ef, paper #ffffff, ink #20392f, muted #50685d, accent #1f654b, control border #72877a; Avenir Next with system fallback |

Both include dark counterparts, 46px secondary/confirm controls and a minimum 56px recording control. Checked 48 foreground/background and boundary pairs across both themes: text minimum 5.25:1 and control boundaries minimum 3.42:1. Native keyboard focus was retained. Browser inspection covered outer widths 1280/390/320, correction content in Hindi and Roman Hinglish, simulated clarification/extraction failure/unresolved-save states, and design navigation. No production usability, screen-reader, audio or persistence claim follows from this preview. Screenshots and check results are in ignored `artifacts/design-preview/`. The inline source remains in the chat's visualization directory.

Use the existing planned plain HTML/CSS/JavaScript frontend. Create a shared stylesheet of CSS custom properties with the first implementation; its exact path follows the actual static-assets layout. Do not create an unused React-style `src/` tree or empty token file during planning.

Current neutral candidate: paper #ffffff/#171717, ink #202020/#ededed, muted #666666/#aaaaaa, decorative rule #e5e5e5/#393939, control border #808080/#858585, state surface #f5f5f5/#242424 (light/dark). System sans, 16px record values, 14px field labels, minimum 44px actions. Eight measured pairs meet text/control targets (minimum 5.74:1 and 3.95:1 respectively). The new composition uses open rows and a collapsible transcript rather than an enclosing colored card. It is still a proposal; see the research note for trial results and limitations.

- Name tokens by purpose: surface, text, muted text, border, accent, focus, success, warning and error; use variants only when needed. A fixed color-count limit must not prevent accessible states.
- Define type sizes/line heights, spacing, control sizes, radii and motion durations centrally. Candidate spacing scale: 4, 8, 12, 16, 24, 32 and 48 CSS pixels. Final values belong in the rendered specimen.
- Use shared tokens for repeated colors/spacing; allow justified structural values such as zero, percentages and one-off geometry. Do not add meaningless tokens merely to satisfy a blanket ban on numbers.
- Compare font candidates using real Roman Hinglish, Devanagari, digits and long field values. System fonts are acceptable if they meet the visual/readability goal. Any new font asset requires checking coverage, licensing and loading behavior.
- Build shared control/field/state styles, view-specific composition and a small API/state boundary. CSS presentation does not decide whether a record is saved.

## Visual critique

A recognizable product identity should come from the repair task and clear hierarchy. Uniform shadowed cards, unnecessary gradients, decorative badges, arrows on every button and animation on every section need a purpose before inclusion. Cream/serif, dark/neon, rounded corners and common fonts are not universally forbidden; judge the actual composition and user preference.

Keep one dominant visual idea. The review card may group job details like a service sheet, while the recording action remains easy to locate. Distinguish changed values with text/structure as well as color. Keep history and engineering traces subordinate to the current record.

Motion should explain an action or state transition. Recording indicators must correspond to actual recording; cancel/stop should visibly end it. Respect reduced-motion preferences. A page-load reveal is optional, not a required mark of craft.

Use sentence case and specific actions: “Record update”, “Stop recording”, “Confirm and save”, “Check save status”. Draft copy examples for review: “We couldn't transcribe this recording. Try again or type your update.” and “We haven't confirmed whether this saved. Check status before making changes.” Avoid technical provider/error codes in the primary user message.

## Required states

Recording, processing, clarification, ready for review, saving, saved, failure and unresolved save must be distinguishable in text. Show one obvious primary action per state. Highlight corrections. Disable incompatible actions while processing/saving; unresolved save keeps editing locked. Preserve useful text/draft after failures and explain recovery plainly.

| View | States to design and exercise |
| --- | --- |
| Jobs | Loading, no available jobs, load error/offline, selectable jobs |
| Update | No message yet, recording, processing, clarification, mismatch hold, extraction failure, review, cancelled, microphone denied, TTS failure |
| Save/Saved | Saving, known rejection, unresolved outcome with Check status, successful receipt, receipt-fetch failure |

An offline indicator may describe connectivity; it must not imply an offline save queue or successful persistence. Loading indicators must reflect actual work; use skeletons only where they help explain loading content. Immediate local input feedback is useful, but optimistic success is forbidden for saves. Full behavior remains defined in the spec.

## Accessibility and inspection

- Use contrast-safe colors and never encode status only by color or audio.
- Measure proposed text/background combinations against the intended accessibility target (at least 4.5:1 for normal text and 3:1 for large text); check control boundaries/focus separately. These are review targets, not an existing compliance claim.
- Use keyboard-operable buttons with visible focus and labels; expose processing/status changes accessibly.
- Use large tap targets; use 44 CSS pixels as the initial target for primary controls.
- Check narrow mobile and desktop layouts with long part names, multi-line Hinglish and error text. Confirm controls remain visible and text wraps.
- Capture at least one narrow viewport (for example 390 CSS pixels) and one desktop viewport (for example 1280), plus an overflow check at 320 pixels. Use content-driven breakpoints rather than treating those examples as device support guarantees.
- Verify the actual flow in a browser, including one relevant error/recovery path. Check console/network failures. Screenshots support visual review but do not prove behavior.
- Microphone denial must have a useful next action; STT failure can offer typing; extraction failure cannot falsely advertise typing as an independent fallback.

If a UI request changes confirmation, state transitions or input behavior, use TDD for that behavior; the formatting-only exception does not apply.

For the first screen, show Ankit the real rendered result and solicit what feels wrong before carrying its treatment to the other views. Routine fixes within the selected direction do not need renewed approval. If rendering or browser access is unavailable, record exactly what could not be verified and keep visual acceptance pending.

## Enforcement status

Available now: repository guidance, pytest/Ruff and the UI-polish review procedure. The first working typed screen has actual Chrome interaction tests and inspected desktop/390/320 captures, including long Hindi/part text, visible focus and reduced motion. Tests separate HTTP fixtures from real local HTTP/SQLite; all extraction is scripted. Saved receipts and locked-save states were inspected. This is not a screen-reader audit or general accessibility certification. Automated screenshot-diff regression, axe CI and a custom token linter are not installed. Add tooling only for a demonstrated need with the required dependency approval. Screenshot baselines must be reviewed, not blindly regenerated to hide regressions.
