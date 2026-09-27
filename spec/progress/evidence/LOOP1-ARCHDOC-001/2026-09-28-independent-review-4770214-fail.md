# LOOP1-ARCHDOC-001 independent review: FAIL

- Reviewer: `/root/archdoc_review2`, fresh context, independent of implementation `/root/archdoc_fix1` and prior reviewer.
- Reviewed commit: `4770214e36844334048c357508d626326944b452` (`fix/LOOP1-ARCHDOC-001-native-markdown`). Review evidence branch: `review/LOOP1-ARCHDOC-001-fail-2`.
- Base/diff: accepted local `main` `abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a..4770214e36844334048c357508d626326944b452`; repair range `5f117a41bf2f906fcb0f490e0f87352ad19aadb7..4770214e36844334048c357508d626326944b452`.
- Clean method: managed fresh detached checkout `H:\.codex\worktrees\archdoc-clean-acceptance-2\IM-platform` at exact reviewed SHA. `git status --porcelain=v1` was empty before and after Acceptance. The review Recorder/evidence lived in a separate checkout. No candidate code was modified.
- Review Recorder: `R-20260927T165345Z-7f097083-6629-4c5b-9bee-8b844070b6c4`, prompt `P-a414172f-74f0-4715-8a4c-ded75496e225`.

## Blocking finding

The immutable PDF page 20, Fig 15-1, places **seven** visible `Gate PASS` labels under stages S0, S1, S2, S3, S4, S5 and S6. The canonical Markdown Mermaid figure at `spec/architecture/frozen-architecture.md:829-835` uses `Gate PASS` only as labels on its **six** S0→S1 through S5→S6 edges. There is no label for the final S6 Gate PASS. The user's explicit figure-label preservation requirement and Task acceptance for semantic faithfulness therefore fail. The surrounding S6 acceptance prose does not restore the missing figure label. Preserve the seven stage labels in a readable figure without changing the architecture's Gate meaning, then obtain a new independent review.

## Checks and scope

| Exact command, invoked through `tools/research/recorder.py run-command` | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `pwsh -NoProfile -File H:\.codex\worktrees\archdoc-clean-acceptance-2\IM-platform\tools\verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | 1132.603 ms | Local Acceptance verifier PASS on clean candidate; does not override semantic FAIL. |
| `pwsh -NoProfile -File H:\.codex\worktrees\archdoc-clean-acceptance-2\IM-platform\tools\verify-frozen-architecture.ps1 -BaseCommit abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a` | 0 | 783.1188 ms | Both actual hashes, authority metadata, scope and built-in structural negatives PASS. |
| `pwsh -NoProfile -File H:\.codex\worktrees\archdoc-clean-acceptance-2\IM-platform\tools\verify-loop1-ctrl-001.ps1` | 0 | 796.4635 ms | Baseline PASS. |
| `pdftoppm -f 1 -l 28 -r 110 -png H:\.codex\worktrees\archdoc-clean-acceptance-2\IM-platform\scalable-distributed-im-architecture.pdf spec/progress/evidence/LOOP1-ARCHDOC-001/_review2_tmp/page` | 0 | 2976.9022 ms | All 28 pages rendered for visual inspection; temporary images removed. |

- PDF SHA-256 is `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`; Markdown actual SHA-256 is `e31fe163be90667b5562c1873ba427795e449e4ae22458390d2b7920de00894b`. Manifest separates active Markdown hash from historical PDF provenance; ADR-0002 limits migration to representation and defers effectiveness until accepted merge/post-merge PASS.
- The 86 TOC links resolve to 86 unique explicit anchors immediately before Markdown headings. Nine Mermaid blocks and two `NATS --> PG` edges are present. The verifier rejects its in-memory old fenced layout, missing TOC entry and missing-diagram controls. The prior FAIL evidence file is unchanged.
- Visual comparison covered PDF pages 1–28, including nine figure locations (pages 5, 8, 9, 10, 11, 14, 17, 19, 20). The page text comparison was a heuristic audit because PDF line wrapping and table layout differ from native Markdown; no other definite normative/numeric change was established before this blocking finding. Mermaid rendering was unavailable in this checkout, so a fresh reviewer should verify final figure rendering after repair.
- Diff from accepted base has no changes in `contracts/`, backend, clients, plugins, `spec/domain/`, `spec/invariants/`, `spec/acceptance/`, or the PDF; prior historical evidence remains unchanged. No product code or public contract change was observed.
- Result: **FAIL**. Current task remains `review`; S0 Gate remains NOT YET PASSED. This clean-checkout verifier PASS is local evidence only and cannot accept the candidate.
