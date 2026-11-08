# 009 — Pin the working extraction model and preserve failed evidence

Date: 5 November 2026. Status: implemented under Ankit's authorization to run the tests and complete the submission build.

## Context

The configured Gemini 3.8 Flash repeatedly returned 503, including a new plain-generation diagnostic after the project dashboard showed a nonzero free-tier allowance. A separate 2.5 Flash diagnostic returned 404; Google's current documentation marks that model deprecated with restricted access. The model-list API advertised 3.5 Flash-Lite, which returned a successful plain response and a Python-validated extraction.

## Decision

Pin `gemini-3.5-flash-lite` through the existing REST v1beta generateContent adapter. Keep LOW thinking, the existing JSON schema and strict Python validation. No automatic model fallback, SDK, retry, billing change or save authority is added. A generation success establishes availability at that moment, not guaranteed uptime or extraction accuracy.

Use prompt `bolparchi-extraction-v4` and schema `bolparchi-extraction-v2`. A six-case development run found that uncertainty could be expressed as clearing quantity rather than holding the whole patch. Prompt v3 distinguished uncertainty from explicit removal; the targeted uncertainty recheck passed. V4 and schema field descriptions make follow-up semantics explicit, but the retained full Hindi transcript still lost its final follow-up clause. These changes have not established better accuracy. Preserve the failed runs and the remaining exact-output mismatch: an explicitly named part already present in the draft may be omitted from the returned patch, although the resulting record is unchanged. Do not alter expected results to hide these mismatches.

Keep development cases separate from `probes/acceptance_cases.json`, authored after v3 and frozen before its first execution; these cases were not used for v4/schema tuning. The first six-case evaluation stopped on HTTP 503 on case one; five cases were unattempted, so no semantic accuracy percentage is available. Report sample counts, exact patch matches, model version and latency; this small set is not general accuracy certification. Further tuning on these cases makes them development data and requires new evaluation examples.

## Alternatives and consequences

- Waiting for 3.8 leaves the live flow blocked despite an available extraction-capable model.
- 2.5 is deprecated and returned 404 for this key; a displayed quota row is not proof of usable inference.
- Silently switching models after an error would obscure the tested configuration and spend additional requests; keep selection explicit in source and evidence.
- Regex-based extraction would not demonstrate general language understanding and would fail the accepted scope.

Sources checked 5 November: [3.5 Flash-Lite model](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite), [thinking levels](https://aistudio.google.com/docs/thinking#thinking-levels), [2.5 deprecation](https://aistudio.google.com/docs/models/gemini-2.5-flash). Live reports remain in ignored `artifacts/provider-probes/`; current readiness is recorded in status.
