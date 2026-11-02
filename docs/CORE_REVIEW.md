# Review and verification

Reviewed the supplied kaamsaathi-core.zip on October 15, 2026 (IST).

## Reproduced issues and changes

1. A dictionary supplied as diagnosis was converted into text and passed validation.
   Text types are now checked; malformed proposals are rejected explicitly.
2. `save(draft_id, None)` succeeded, but retrying it did not replay the original result.
   Submission IDs now receive application checks and constraints in new schemas.
3. A post-commit draft-view failure returned “nothing was recorded” despite a stored
   draft. Draft result preparation now occurs inside the transaction, and generic
   failures avoid an unsupported rollback claim.
4. COMMIT was outside the transaction exception handler. A commit failure could
   leave the connection in a transaction. Commit errors now trigger rollback when
   the transaction is still active; the retry path is tested.
5. The connection disabled SQLite's thread check but did not serialize shared use.
   A reentrant lock now protects Store transactions and draft reads.
6. Late edits could overwrite newer corrections. Callers can now supply an expected
   revision and receive `stale_update` without mutation.
7. A superscript digit passed `isdigit()` but failed integer conversion. Decimal
   digit checking now lets validation reject it without crashing normalization.

## Verified results

- Original supplied suite: 36 passed.
- Reviewed suite: 60 passed, including the 36 original tests unchanged.
- Text demo: explicit confirmation saves a one-motor request; retry returns `replayed`.
- No Gnani, extraction model, microphone, or synthesized speech calls were performed.

These tests establish behavior for the tested local cases, not speech accuracy,
production readiness, or a contest outcome. See CORE.md for integration limits.

## Packaging on 20 October 2026

The original review above is retained as historical evidence. The Python package
and test imports were renamed from `kaamsaathi` to `bolparchi` during project setup.
No product features were added during that rename.
