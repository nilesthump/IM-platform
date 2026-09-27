# LOOP1-ARCHDOC-001 candidate semantic-equivalence checklist

Source: immutable `scalable-distributed-im-architecture.pdf`, SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`, 28 pages. Candidate: `spec/architecture/frozen-architecture.md`. This is implementation-side evidence, not independent acceptance.

The candidate retains each page's complete UTF-8 `pdftotext -layout` text layer in an individually labeled Markdown block. A recorded exact comparison found 28/28 blocks byte-equal after CRLF-to-LF line-ending normalization. The separate diagram transcription records vector arrows omitted by text extraction. The PDF text blocks intentionally retain table spacing and repeated normative language rather than editorially rewriting it.

| PDF page | Architecture material checked against Markdown | Candidate status |
| --- | --- | --- |
| 1 | Title, v1.0, date, Loop 1 12-week budget, 8C/16GB/3TB, 5,000 authenticated WSS users, Loop 2 target, MUST/SHOULD/MAY definitions | Text exact |
| 2–4 | Table of contents, chapter/appendix labels and scope | Text exact |
| 5 | Executive summary, Loop 1 versus deferred work, Fig 0-1 system graph | Text exact; graph transcribed |
| 6 | Goals, non-goals, E2E/ACK/client/parity/capacity evidence, evidence-plus-ADR infrastructure rule | Text exact |
| 7 | F-01 through F-10, ACP/ADR approval flow, authority hierarchy | Text exact |
| 8 | Fig 3-1 components, Gateway/Core/Plugin Host responsibilities, Go/Java profiles, single-machine deployment | Text exact; graph transcribed |
| 9 | Fig 4-1 entities, Session slots/epoch, Friend/DIRECT uniqueness, Group idempotency, message identifiers | Text exact; graph transcribed |
| 10 | Transaction order, durable ACK, Outbox/NATS fan-out, sequence-row ADR condition, five red lines | Text exact; sequence transcribed |
| 11 | Web memory versus native SQLite, optimistic FAILED/SENT, three UNIQUE constraints, dual cursors and atomic convergence | Text exact; flow transcribed |
| 12 | Login fields, WSS state, Session cache/outbox, TLS/token/password/plugin/log security | Text exact |
| 13 | Plugin package tree, API surfaces, Render Bundle review/sandbox/immutability, WASM limits/AUTO_DISABLED | Text exact |
| 14 | Plugin lifecycle/upgrade/rollback, artifact versus instance state, Echo/Poll fixtures | Text exact; state graph transcribed |
| 15 | Monorepo tree and spec directory responsibilities | Text exact |
| 16 | Contracts as sole machine-verifiable authority, Go/Java observable equivalence, Golden Tests, expand/migrate/switch/contract | Text exact |
| 17 | Agent loop, task example, state queue, Git modes | Text exact; workflow transcribed |
| 18 | Mandatory recovery order, handoff/checkpoint, crash recovery | Text exact |
| 19 | Path-aware CI DAG/table, stages, compatibility matrix, isolated runner boundary | Text exact; DAG transcribed |
| 20 | S0–S6, Gate-driven progression, weeks as budget, execution-policy MUST/MAY | Text exact; progression transcribed |
| 21 | Fixed 5k load environment/scenarios, sequence-gap case, metrics and S6 PASS | Text exact |
| 22 | Release Manifest, immutable artifacts, DB migration, rollback and stop conditions | Text exact |
| 23 | Trace IDs, health probes, security checklist, P0–P3 alerts | Text exact |
| 24–25 | Full task roadmap tables, task IDs, dependencies, stage/gate and sequencing principles | Text exact |
| 26 | Agent first 0–2 hours, implementation loop and stop rules | Text exact |
| 27 | Appendix A Gate Checklist and PASS criteria | Text exact |
| 28 | Appendix B cross-cutting invariants and final declaration | Text exact |

## Normative and numeric protection

- Exact page-block comparison preserves all text-layer `MUST`, `MUST NOT`, `SHOULD`, `MAY`, `禁止`, `必须`, `不得`, `只有`, `允许`, `应`, and `可` in place; no editorial replacements were made inside these blocks.
- Exact page-block comparison likewise preserves numeric values, protocol versions, capacity targets, timing, state names, task IDs, and table cells as extracted. Long table cells and task IDs may wrap visually; the original lines remain intact rather than being guessed or rejoined.
- PDF vector edges are not emitted by `pdftotext`; the eight figure entries in the Markdown diagram section are separately transcribed from visual inspection. Figure 0-1 / 3-1's NATS → PostgreSQL arrow is retained as drawn despite tension with the text's PostgreSQL truth-source rule. It is not reinterpreted or repaired.

## Independent review still required

Fresh independent Review must compare every semantic section, especially diagrams, tables, normative strength and numbers, against the PDF visual pages; inspect the candidate commit and clean checkout; and record PASS/FAIL separately. This checklist alone does not establish semantic-equivalence PASS.
