# GUI Acceptance Specification

Status: Human-approved protocol candidate pending independent freeze acceptance. Applies to future GUI implementation tasks; this architecture task has no running GUI and MUST NOT fabricate screenshots.

## Required acceptance chain

GUI implementation -> actual runtime screenshots -> Architect Review -> bounded fixes -> new screenshots -> Architect Approval -> fresh independent candidate Review plus applicable exact-head hosted CI -> protected integration/main verification -> GUI Task PASS. These reviews may share evidence but cannot erase one another's distinct obligations. Architect approval accepts presentation; independent Review accepts implementation/authority/minimality; CI accepts applicable executable checks. None alone establishes S2 Gate PASS. No done transition before the repository's full acceptance/integration requirements.

Screenshots are Task acceptance requirements, not optional design feedback. Each GUI Task MUST name its destination/runtime matrix and evidence paths before implementation. Capture actual client runtime, not mockups/edited images. Record task ID, candidate SHA, source/build provenance, platform/runtime version, account/test fixture identity without secrets, screen/state, viewport/window/device dimensions, theme and typography/spacing setting, exact reproduction steps and image filename/hash. Images must contain no real credentials, token displays or private user data; use controlled fixtures.

## Minimum coverage matrix

| Client | Required runtime evidence |
| --- | --- |
| Web | Login, Chat, Friends, AI Placeholder, Plugin Page in real browser |
| Desktop | Main window, Chat, Friends, Offline History, Notification/Tray, Theme in real Tauri client |
| Mobile | Login, Chat, Friends, Offline History, Sync state, Theme in real Android Studio emulator |

Both Cold AI and Warm Creative must demonstrate unchanged layout/semantics; cover supported typography/spacing extremes where layout is affected. For destinations shared across platforms, represent each platform's actual host layout. Desktop notification/tray evidence must include the actual native surface and reproduction steps, not just an in-app drawing. Mobile evidence names emulator/device/API; host-only tests/mock screens do not replace it.

Each scoped screen must include meaningful relevant loading/empty/error and success states. Auth includes refresh/logout/session-expired without exposing credentials. Chat includes actual SENDING/SENT/FAILED, retry identity and convergence behavior under executable protocol/storage evidence; screenshot alone cannot prove durable ACK, deduplication or atomicity. Offline/Sync includes a controlled disconnect/reconnect case; Web must not claim persisted/offline history. Theme/preferences must survive their permitted local lifecycle with no business-data persistence implication.

If a bounded GUI task does not implement every matrix surface, its Task Spec must explicitly state its slice and the remaining tasks before activation. Omitted evidence never counts as whole-client acceptance. For unavailable Plugin/AI functionality, screenshots must truthfully show reserved entry/placeholder/unavailable state. No fake working controls or fake AI/plugin data.

## Architect decision and repair cycle

Architect Review records exact candidate SHA, screenshot manifest/hash, decision PASS/FAIL, concrete per-screen findings, checked information hierarchy/navigation/readability/theme/configuration rules, and reviewer identity. On FAIL keep task unfinished, fix in allowed_paths and capture again. Prior screenshots/findings remain immutable; approval identifies the latest accepted screenshot set and build. Any later visual/state/code change affecting approved evidence requires new captures and renewed approval. Unchanged unaffected images may be referenced with hash and reason, never relabeled as fresh captures.

A fresh independent Reviewer inspects actual Repository/protocol/state/native ownership, source imports, minimality, public contracts and security boundaries. It must verify all new sensitive dependencies have accepted canonical/ADR authority; screenshot quality never legalizes a framework or contract change. Applicable CI must match the exact reviewed candidate SHA and correct required jobs; missing/failed/cancelled/anomalously skipped jobs cannot PASS.

## Evidence and closure

Store capture manifest, original images, Architect decisions, fix iterations, independent Review and hosted acceptance under spec/progress/evidence/<GUI_TASK_ID>/. Include commands, exit codes/durations, known failures and last known good SHA in task handoff; current.md links concise recovery state and the latest stable checkpoint. Bind visual evidence to the integrated product tree and record task branch/commit/sync result/main SHA before claiming completion. No Photoshop/generated visuals as runtime proof, no CI substitute, no stage advancement from a single GUI task.
