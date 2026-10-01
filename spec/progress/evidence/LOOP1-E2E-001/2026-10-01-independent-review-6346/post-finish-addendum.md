# Post-finish evidence clarification

This addendum is generated after Recorder R-E2E-REVIEW-6346 finished/validated and does not modify its closed evidence or the first report/manifest.

The report enumerates initial registration and cleanup failures. A third external finalization-only failure also remains preserved: finalize.py used invalid Python codec spelling utf8-sig and exited1 before the original605 audit or finish. An explicit instrumentation_warning event documents it. The retained corrected copy finalize-corrected.py uses utf-8-sig, independently checks all605 bytes, binds final direct13jobsx2 and closes/validates Recorder successfully. It runs directly so finish cannot be nested inside a recorder run-command that would append after run_finished. No candidate repair or product failure occurred. The initial failed script/Recorder command remain intact.

First final-manifest.json SHA256e554b001793c733a672b87a5439f20e157c2d9997decade52c77594a0985bd39 covers212 files present then and excludes itself to avoid recursive hashing. final-transport-manifest.json adds this clarification and hashes the original manifest as an ordinary artifact. Transport generation itself is explicitly outside the finished trace. Candidate acceptance remains exact6346 only; any later administrative state/merge/main needs applicable independent acceptance.
