# LOOP1-ARCHDOC-001 native Markdown fix: semantic checklist

Source PDF: `scalable-distributed-im-architecture.pdf`, SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`, 28 pages. Repaired Markdown SHA-256: `e31fe163be90667b5562c1873ba427795e449e4ae22458390d2b7920de00894b`.

`semantic-audit.py` reruns `pdftotext -layout -enc UTF-8` and finds all 28 PDF page text layers exactly equal to the preserved reviewed-candidate extraction, after newline normalization. The repaired document has 86 matching clickable index links and explicit targets, 25 native Markdown tables, nine Mermaid figures, and no page-fenced layout. This check is development evidence; independent review remains required.

| PDF page | Repaired native Markdown coverage |
| --- | --- |
| 1 | Exact title, v1.0, Loop 1 scope, date, capacity, audience, and MUST / MUST NOT / SHOULD / MAY definitions. |
| 2–4 | Full numbered chapter/section and appendix contents rebuilt as clickable links with original page numbers. |
| 5 | Executive summary, four principles, in/out scope table, Fig 0-1. |
| 6 | Goals, Loop 1 success evidence, Loop 2 exclusions, infrastructure/ADR condition. |
| 7 | F-01–F-10 table, frozen-change protocol, authority-order list. |
| 8 | Fig 3-1, deployment responsibilities, Go/Java profiles, Loop 1 single-machine rules. |
| 9 | Fig 4-1, Session epoch/slot rules, Friend/DIRECT uniqueness, group idempotency, message identity table. |
| 10 | Fig 5-1 sequence, transaction order, durable ACK, Outbox/NATS delivery, correctness red lines. |
| 11 | Web/native storage table, optimistic states, SQLite constraints, Fig 6-1 two-cursor convergence. |
| 12 | Login fields, WSS state machine, Session cache, transport/token/password/plugin/log rules. |
| 13 | Package tree, API capability table, Render Bundle and WASM security/immutability. |
| 14 | Fig 9-1 artifact/instance lifecycle and standalone exception/upgrade boxes, install/rollback, Echo/Poll. |
| 15 | Monorepo tree and spec-directory responsibility table. |
| 16 | Contract authority, Go/Java parity table, Golden Tests and migration sequence. |
| 17 | Fig 12-1 Agent workflow, task example, state queue and Git mode. |
| 18 | Recovery order table, handoff fields, checkpoint and crash-recovery rules. |
| 19 | Fig 14-1 drawn CI arrow topology, path rules, pipeline levels, matrix, runner boundary. |
| 20 | Fig 15-1 S0–S6 and seven Gate PASS labels, unchanged English MAY/MUST/MUST NOT policy, milestone table. |
| 21 | 5,000-connection environment, six load scenarios, metrics, S6 PASS. |
| 22 | Release Manifest, immutable release rules, migration table, rollback and stop conditions. |
| 23 | Trace IDs, probes, security list and P0–P3 priorities. |
| 24–25 | Complete first and later task tables; PDF-wrapped task IDs and cell words are rejoined, preserving rows, duplicates, stage, Gate and dependencies. |
| 26 | First-hours checklist, PLAN/IMPLEMENT/TEST/REVIEW/HANDOFF, stop conditions. |
| 27 | Appendix A Gate checklist and common PASS conditions. |
| 28 | Appendix B invariant table and final frozen-baseline declaration. |

Visual figure comparison used rendered PDF pages 5, 9, 10, 11, 14, 17, 19 and 20; Fig 3-1 on page 8 repeats Fig 0-1's deployment topology and was checked against the retained PDF text and prior independent visual transcription. Fig 0-1 and Fig 3-1 each explicitly retain the drawn NATS → PostgreSQL arrow. Its meaning remains ambiguous; the Markdown notes that ambiguity and does not change the PostgreSQL/NATS authority statements. For Fig 14-1, the Mermaid follows the drawn horizontal path sequence and the matrix's two output arrows even though the drawing is unusual. Fig 9-1's exception and upgrade boxes remain unconnected, as drawn.

Implementation-side semantic audit found no intentional architecture, contract, invariant, ACK, compatibility, security, or numeric change. The prior independent FAIL evidence remains unchanged. A new independent reviewer must decide acceptance from a clean committed checkout.
