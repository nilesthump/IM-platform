# Stage-one development evidence (not independent acceptance)

Candidate base: 8cd90a7; branch task/LOOP1-ARCH-REMEDIATION. Sole implementation writer /root/stage1_impl. Review pending.

Research Recorder: R-20260929T183826Z-8cd6416f-9684-4596-bc81-bc6f8ee8ce56. Exact command argv, output hashes, elapsed times and exit codes are in its events/blobs. Early recovery is explicitly incomplete; approval-and-recovery.md records the limitation.

- Original verifier with pwsh: PASS pre-edit. Windows PowerShell 5 script parse failed due UTF-8; pwsh resolves it. No source bytes were treated as corrupt.
- Atomic in-memory architecture edit first failed a no-op assertion on an already intact table row before file write; removed that assertion, rerun PASS.
- New integrity entry point `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1 -BaseCommit 8cd90a7`: PASS; 4 test methods include 20 semantic negative mutations, current valid control, layout-flexibility control, and temporary authority copies for hash/provenance corruption. Product tree and historical evidence not mutated.
- Recovery Development check initially reported 13 formatting/discoverability failures in the new control documents; corrected the documents to the existing schema rather than weakening the verifier. Rerun recorded below in Recorder.

Semantic checker binds deployment relationships to both deployment chapters; message authorization/commit/ACK sequence and relay edges to §5; artifact/instance distinction to §9; failure-to-fresh-review and CI edges to §12; governance checks to classification/Gate in §14; each stage prerequisite to §15. It replaces count-only table/diagram/historical-arrow assertions. It does not claim to prove all prose meaning or product source compliance: independent whole-document review remains required, and product enforcement is stage 3.

Current task remains active until candidate handoff; no stage, task or batch acceptance claimed here. Final verification and handoff details will be appended before commit.

## Final local results and handoff

- New integrity/hash/provenance and all negative controls: PASS (4 test methods, 20 targeted semantic mutations plus hash/PDF/provenance mutations), no skip.
- CTRL-002 Development: PASS after document-format corrections, unique Current Task and five queues.
- HTTP verifier: PASS, 9 paths/operations, 6 positive/21 negative fixtures, 15 mutation regressions.
- WSS verifier: PASS, 8 positive/10 negative cases, 18 schema and 26 behavior mutation controls.
- Sync/Plugin verifier: PASS, 79 outcome artifacts, 16 mutation controls; static contract vectors are not live product parity.
- Existing CI unittest suite: 21 tests PASS with four OS symlink-privilege subcase skips (WinError 1314). Non-OS simulated symlink checks pass. These skips are not claimed as executed tests; hosted Linux CI remains required.
- No product build/live integration executed in this architecture-only phase; these are required in stage 4, not claimed covered by old Auth CI.
- A UTF-8 decoding error interrupted a recovery edit after a canonical clarification write; rerun with explicit UTF-8 completed manifest hash and documents. Actual current SHA is 83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e. Recorder preserves both failed and successful commands.
- Coordinator additionally performed unrecorded read-only batch/§10 inspection (one quoting SyntaxError then successful retry); no write or tests. Complete timing/trace unavailable. Some direct final status/diff inspections are similarly outside the command recorder and are not represented as complete trace.

Task transitions to review for a fresh independent Agent on the committed candidate. All C ledger findings are candidate-repaired and pending independent review; I01 and D01 are deliberately ordered stage 4 and stage 2/3 work, not architecture exceptions. Batch/S1 Gate NOT PASSED. No new source ownership checker/product conformity is claimed in stage 1. The sole writer releases write ownership at handoff; no unknown original or Social worktree contents were accessed.
