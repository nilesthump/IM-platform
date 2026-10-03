# ADR-0006: Client UI architecture and screenshot acceptance

Status: Human-approved direction; candidate pending fresh independent Review and exact-head hosted CI; not yet effective on main.
Date: 2026-10-03
Approval source: spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/human-request.txt
Supplement: spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/human-supplement.txt

## Motivation and explicit decisions

The Human requests freezing three-platform UI architecture, Adaptive Glass Workspace design direction and screenshot-driven Architect acceptance before GUI implementation. The prompt explicitly chooses independent Desktop UI and React built-in state; Mobile ViewModel/StateFlow/Jetpack Navigation Compose. The subsequent Human clarification limits the UI-code execution ban to S2 and retains S4 reviewed sandbox Render Bundle. The worktree supplement authorizes autonomous managed allocation in Codex Settings directory when no assignment exists.

Canonical §6.5 records all normative decisions; subordinate architecture/design documents explain those requirements without creating another canonical source. Desktop full-component reuse rule in §6.1 is replaced by independent visual implementations sharing protocol/models/eligible hooks/tokens/UI semantics. No shared Button/MessageBubble/ChatWindow. Mobile Kotlin equivalent behavior remains unchanged; approved Navigation/Lifecycle/StateFlow dependencies are narrowly listed in canonical machine policy for future approved tasks. Web router and generic icon/accessibility/utility categories select no new named package. No state manager/AI API/Plugin runtime selected.

## Normative effect and compatibility

semantic_change=true. v1.1 retained. Canonical bytes/hash updated; accepted input aa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c is preserved as UI-amendment lineage in baseline.md; base client technology provenance remains ADR-0005. The base revision metadata and older ADR-0001..0005, original PDF546915, PR7/PR8 history and all prior FAIL/waiver/evidence remain immutable. §8.2 security checks/sandbox/Bridge and plugin contracts remain intact; S2 implements no renderer/download/install/runtime. No wire contract, ACK, compatibility, storage schema, security permission or backend changes. No product/data migration.

## Initial delivery and effective point

Documents: decisions/client-ui/architecture.md, decisions/client-ui/design-direction.md and spec/acceptance/client-gui.md. GUI tasks must require actual runtime screenshot manifest tied to candidate SHA, Architect review/fix/recapture/approval, independent semantic implementation Review and applicable exact-head hosted CI. Screenshot approval does not replace those checks or grant S2 PASS.

Freeze becomes effective only after fresh independent clean-candidate Review and applicable exact-head hosted CI, accepted integration and actual-main verification. Until then the accepted main remains last known good and product implementation must not consume the candidate as accepted authority. Reviewer must inspect canonical changes, subordinate documents, exact write scope, machine-policy dependency additions and preserved historical lineage. Record the effective SHA/CI/main and protected sync result truthfully, then task done; S1 PASS/S2 OPEN retained. No SEND/SYNC/WEB task activation.

## Minimality and rollback

Three documents plus bounded canonical/ADR/index/manifest and Human AGENTS supplement; no components, token engine, library installation, plugin runtime or AI. New approved engineering identifiers serve only the explicit Mobile state/navigation design; no Room/network/test framework permission. Before effectiveness repair the candidate while accepted main is unchanged; later corrections use Human-approved corrective ADR and fresh acceptance, never rewrite history/PDF/Recorder.
