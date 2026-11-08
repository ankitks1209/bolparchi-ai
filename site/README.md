# Local BolParchi landing-page preview

A buildless, presentation-only site. Run from the repository root:

```sh
.venv/bin/python -m http.server 8772 --bind 127.0.0.1 --directory site
```

Open http://127.0.0.1:8772/. Serve **only this directory**, not the repository or `.env`. Stop the server with Ctrl-C. There are no dependencies, provider calls, analytics, signup forms or application write routes here. This page is not deployed.

Visual authority: [design system](../agent_docs/design-system.md). Content/story: [brief](../docs/landing-page-brief.md). The hero is a labelled HTML illustration with readable text; actual product captures are in the product section. The real working video remains pending; the page has no pretend play control.

## Asset provenance

- `assets/service-sheet.png`: unmodified `artifacts/unslop-final-20261106/review-desktop.png`, polished actual interface with **fixture providers**, 6 November. The image and its visible caption disclose fixture mode.
- `assets/voice-receipt.png`: unmodified `artifacts/human-voice-handoff-20261106/saved.png`, **real-provider** user-operated microphone task, fictional job 104, 6 November. This predates the final visual polish and is labelled accordingly. No audio, keys, customer contact information or database is included.
- `assets/mark.svg`: code-native adaptation of the existing paper mark for the favicon. The animated navigation mark reuses the app's CSS motif.

The user-facing local preview includes these captures for review. Publishing still requires Ankit's fresh approval of the concrete result. GitHub source may still show the older pushed build until the release update is committed and pushed; the page links only to that existing repository root.

## Verification

`checkLanding(tab)` from `scripts/check_landing_browser.mjs` runs with the existing CUA browser tab, never a separate browser driver. It checks drawer opening, keyboard wrap, Escape/focus return, section navigation, evidence disclosure, honest absent-video state, anchor targets and overflow. Repeat at desktop/mobile widths. Actual screenshots, media-error recovery and contrast checks are recorded in `artifacts/landing-20261107/` and summarized in status. Reduced-motion CSS is supplied; if the browser cannot emulate that preference, report source inspection separately from execution.
