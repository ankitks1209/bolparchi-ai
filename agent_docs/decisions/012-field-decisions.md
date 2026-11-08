# ADR-012 — Account explicitly for every extraction field

Date: 6 November 2026. Status: implemented within the authorized missing-follow-up fix.

## Context

The direct-patch prompt omitted the final return-visit clause from a correctly
transcribed Hindi message. Rewording that prompt and comparing another model did
not resolve the observed omission. Required-field validation prevented saving an
incomplete new record, but cannot detect an omitted correction to an existing value.

## Decision

Keep Gemini 3.5 Flash-Lite and the existing transport. Use
`bolparchi-field-decisions-v2` with wire schema `bolparchi-field-decisions-v1`.
Require a decision for each of diagnosis, status, part, quantity and follow-up:
set, clear, not_mentioned or uncertain. Every stated fact requires a verbatim
supporting quote from the current message. Text values must be contiguous excerpts
of their quotes after whitespace normalization; status and quantity remain normalized.
Uncertainty holds the entire patch. No regex fills missing facts and no second
model judges or repairs the first response.

Python converts this internal response into the unchanged canonical set/clear/
spoken_job_id/needs_clarification patch and applies existing validation. Workflow,
confirmation, revision guards, immutable job identity and save authority are unchanged.
The current message and record remain untrusted data in the prompt.

`bolparchi/extraction.py` selects the active adapter, request builder and metadata
for the app, diagnostics, preparation and evaluation. The old direct-patch adapter
remains available for explicit historical comparisons, with no automatic fallback.
This supersedes ADR-009's prompt/schema selection, not its model choice.

## Evidence and alternatives

The first candidate rejected a real answer because part `मोटर` was supported by
the longer quote `एक मोटर चाहिए`. A failing regression established the corrected
substring rule; replay of that retained response passed without another request.
Six targeted development checks then passed, including the original Hindi message,
reordered Hinglish, genuine absence, removal, uncertainty and replacement of an old
follow-up. These are not held-out accuracy measurements. A real typed browser task
also retained the Hindi follow-up and quantity 1 through explicit receipt-backed saving.

Keeping prompt v4 retained a demonstrated omission. Changing models had no supporting
improvement evidence. Deterministic keyword completion would invent a second semantic
extractor and is not adopted.

## Consequences and limits

The wire response is larger. Preserving source phrases avoids invented translations,
but may be more verbose than a paraphrase. Quote membership is a structural check,
not proof that a quote supports a normalized value, that a clear instruction was
understood, or that not_mentioned is correct. Human review remains essential.
The frozen evaluation is unchanged and pending. A separate retained-audio run still
stopped on Gemini 503 after successful STT; no full voice completion is claimed.
