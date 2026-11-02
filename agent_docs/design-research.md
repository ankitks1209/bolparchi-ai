# Minimal UI research and skill trial

Reviewed 27 October 2026. Ankit rejected both the blue Field sheet and green Focused sheet. The current brief is minimalist, neutral and polished. The replacement preview is a proposal, not an approved production design.

## Website shortlist

| Reference | What to borrow for BolParchi | Scope of inspection |
| --- | --- | --- |
| [Linear's interface refresh](https://linear.app/now/behind-the-latest-design-refresh) | Let job details lead; reduce decorative icons and dividers; keep action placement predictable | Official design explanation and public article rendered in Chrome |
| [Vercel Geist buttons](https://vercel.com/geist/button) | Neutral surfaces, compact controls, clear primary/secondary hierarchy and complete button states | Official component documentation rendered in Chrome |
| [Raycast](https://www.raycast.com/) | Concise action labels and keyboard-oriented interaction; use as an interaction reference | Public landing page rendered in Chrome; no authenticated app inspection |

These are design judgments, not performance rankings. Public pages loaded and a visible control was hovered on each; no frame-time, latency or real-device performance benchmark was run. Reference screenshots are local inspection evidence in ignored `artifacts/design-preview/reference-*.png`.

Recommendation: use Vercel's neutral control treatment with Linear's restrained hierarchy. BolParchi still needs readable Hindi/Hinglish, visible selected job, corrections, and confirmation/recovery states. Smoothness should come from prompt input feedback, stable layout and small interruptible transitions. Avoid adding animation to every section.

## GitHub skill shortlist

| Repository and inspected source | Fit | Trial decision |
| --- | --- | --- |
| [anthropics/skills: frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) | Brief-led typography, composition and visual critique | Applied its design-planning and restraint guidance to the neutral specimen |
| [vercel-labs/agent-skills: web-design-guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md) and its [rules](https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md) | Concrete accessibility, interaction and responsive review | Applied relevant checks manually; found and fixed hover feedback and number alignment; verified reduced motion |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable), current [skill entry](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/SKILL.md) | Broader design system with critique, distill and polish commands | Inspected only. Current entry invokes a launcher which can download a binary; full installation also includes hooks. Evaluate that tooling separately before adopting |

The first two were trialled as reviewed instructions in this session, not installed as auto-discovered skills. No installer, package, hook, external script or subagent was run. Existing six explicit-only project skills remain unchanged. Upstream `main` content was reviewed on the date above; no source version has been pinned for installation. Inspect exact files, license and dependencies at a chosen commit if adopting later.

Adaptation matters: the project's sentence case remains; Vercel's title-case preference does not replace it. Missing required data and unresolved saving still disable incompatible controls under the product spec, even where generic form guidance differs. No React migration, replacement product spec, mandatory branding or automatic hook follows from this trial.

## Trial output and evidence

The new neutral specimen removes the colored background, enclosing service card, colored correction badge, brand icon and tagline. It uses one open column, simple label/value rows, a collapsible transcript, an outlined record action and one filled confirmation action. White/charcoal in light mode has a neutral dark counterpart. These choices are proposed adaptations, not copied product screens.

Browser verification: 12 layout/state combinations across outer widths 1280/390/320; recording simulation disables confirmation; unresolved state locks correction input; missing follow-up disables confirmation; readback opens visible text; confirmation explicitly reports nothing saved. Keyboard focus remained visible; reduced-motion mode reports a zero transition duration. No JavaScript page errors observed. Desktop/mobile/dark captures inspected. Eight token pairs measured: minimum text contrast 5.74:1, control boundary 3.95:1.

Evidence: ignored `artifacts/design-preview/minimal-checks.json`, `minimal-contrast.json`, `minimal-*.png`. Inline source: chat visualization directory, `bolparchi-minimal.html`. No real recording, extraction or save path is connected. Accessibility checks are partial; this is not a full audit or technician usability test.

Next comparison should use this same fictional job, corrections and error states so a prettier screenshot cannot hide missing behavior. Ankit selects the visual direction before it is carried into the real Update view.
