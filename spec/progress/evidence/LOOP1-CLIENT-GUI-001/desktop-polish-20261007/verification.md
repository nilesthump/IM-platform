# Human Desktop UI refinements, 2026-10-07

Scope: four current Human requirements; only existing Desktop UI/presentation and one focused test. No mobile/business/contracts/ACK/security/native transport/dependency changes.

1. Hide scrollbars for app and descendants via standard scrollbar-width/WebKit pseudo-element; existing overflow:auto/native wheel scrolling retained. This interprets middle-button scrolling as mouse wheel scrolling; keyboard accessibility remains available.
2. Earlier rail Offline represented realtime connection, not login. Rail now uses current live Session Online vs local-history-only Offline, green dot only with Session. Chat heading/sync keep actual realtime connection/Offline saved-history signals, never falsify transport readiness.
3. Window control hover/focus uses grey tint matching Human Image3, preserving close-button red and existing Minimize/Maximize/Restore title/icon behavior.
4. Replace native bottom-edge resize with a small custom pointer-captured handle. Height=startHeight+startY-currentY, bounded42..150CSSpx. Up expands/down shrinks; keyboard Up/Down follows same intent. One pure function used by real handler supplies focused regression seam; no new abstraction/framework. Initial72CSSpx. Lost capture/cancel releases resize state.

Baseline source/architecture/frozen/recovery development verification PASS. Frontend TypeScript/bundle PASS; existing canonical auth/registration/recency/lifecycle/appearance controls PASS. Focused direction test first reproduces bad direction (52 vs expected92), then corrected function PASS7 controls: up/down/stationary/both clamps/recovery from both limits. Native Windows NSIS package PASS, installed official UNK->NSS marker whole-file byte comparison PASS. Existing exact installed path updated; only verified owned appPID6940 stopped for replacement, Explorer selected updated exe for Human ordinary desktop-context launch. No automated native screenshot/click claimed.

Initial private edit-script preparation TypeError and absent-script/test failures retained; these happened before product changes and are not red regression evidence. Direct sign edit/install/artifact copy/Explorer handoff outside wrapped commands disclosed. Four supplied images copied byte-exact and hash-bound as Human references, not new tool screenshots. Original six recovery screenshot moves untouched. Private exact NSIS archived. Current same local project39112/session58647 and manually imported root kept for requested Human inspection; after inspection cleanup project and same real desktop-context root/rejection required. Host tool trust/context discrepancy remains unproven mechanism; no repeated import/security bypass.

Taskactive/S2OPEN; full latest visual acceptance/fresh independent Review/exact-head hosted CI/protected integration/main synchronization remain pending. Local checks and Recorder validation are not Task/Gate PASS.

Final guard first attempt architecture/frozen PASS but recovery found5current.md format omissions after concise rewrite. Restored exact command/result/evidence/backtick SHA/checkpoint formatting; no product changes. Failure retained, repair recheck follows.

Repaired final source/architecture/frozen/recovery development guard PASS exit0; output isolation restored all own ignored build/dependency files. No unexplained product failure remains. User latest installed visual feedback pending; this is local verification only.
