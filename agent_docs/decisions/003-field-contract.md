# ADR-003: Shared field contract and explicit extraction boundary

Date: 21 October 2026. Status: accepted implementation start plus Ankit's delegated choice of the proposed v1 limits/ambiguity behavior.

Context: the accepted spec requires strict model patches, immutable selected jobs and dependent clears. The reviewed core previously allowed job changes, conflicting set/clear operations and orphaned quantities. Text limits and ambiguity representation were open questions. Ankit authorized beginning the plan and asked Codex to choose suitable defaults after the concrete proposal.

Decision: FIELD_SPECS supplies field types, unconditional required rules, ranges, choices, patterns, patchability and text limits. Generate the extraction schema from it; keep part/quantity and pending/follow-up conditions in Python. Limit diagnosis/follow-up to 500 Unicode code points and part labels to 120 after whitespace normalization; preserve input messages unchanged up to 2,000 code points. Never silently truncate.

The extraction envelope contains exactly `set`, `clear`, `spoken_job_id`, `needs_clarification`. Sparse set values have strict JSON types and cannot be null or blank. A clarification flag holds the whole message; a different spoken job holds the whole patch. Pure application raises distinct errors for these cases. The upcoming orchestration must preserve the transcript and implement clarification/mismatch resolution with draft/revision/turn/open-state checks.

Selected jobs must exist when creating a draft; patching or clearing job_id is rejected. Confirmation still rechecks job existence. Set/clear overlap and setting quantity while clearing a part are rejected before mutation. Clearing a part clears quantity; replacing it preserves quantity for review.

Alternatives: unlimited text, silently truncated text, partial application of ambiguous messages, duplicated schemas, or breaking the reviewed normalizer's historical convenience inputs. Bounded text with explicit clarification keeps proposals reviewable. Legacy `normalize`/`apply_changes` preserve number-word normalization and None-as-no-change; model output uses the strict `validate_extraction`/`apply_extraction` boundary. Normalization alone is not model-output validation.

Consequences: no new dependency or database migration. Existing receipt, transaction and duplicate protections remain. FIELD_SPECS and schema generation do not establish provider compatibility; live probes must verify that. No UI, real extractor, cancellation, async guard or mismatch-release flow is claimed by the pure helpers.
