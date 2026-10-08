# Mobile header refinement 2026-10-07

Human exact request: moblie移除所有页面红框内容，只在settings保留主题切换窄入口. Original annotated screenshot saved byte-exact as human-reference.png, clearly not a new capture.

## Minimal implementation

Product source candidate1f8e6953da40c7ee58b40360b003d07230dda08a, task branch task/LOOP1-CLIENT-GUI-001-ui-update, assigned root H:/.codex/worktrees/gui-ui-update/IM-platform. Sole writer/root, only mobile UI Workspace.kt and existing two actual instrumentation classes changed. Removed anonymous logo/IM+ row and authenticated global logo/IM+/theme row. Page title, real connection/sync indicator, conversation back and nav semantics remain. Settings existing Appearance now contains a single small theme TextButton, both directions through existing appearance intent; same theme token behavior and font/density retention. Exact original project logo still used by application icon, same across themes. No Desktop/backend/dependency/schema/protocol/security/ACK change or new abstraction.

## Actual checks and captures

Command: python -Xutf8 -B tests/clients/gui/native.py gui-mobile --serial emulator-5590 --capture.
Result: PASS46, anonymous captureRun1791361291785, actual Android14/API34/x86_64 Android Studio IMClientSend34; cold/warm14/16/22 login/registration with no brand header/no theme button and no anonymous navigation. Existing secure-storage controls retained.

Command: python -Xutf8 -B tests/clients/gui/native.py gradle -PimSendInstrumentation=im.platform.client.ui.GuiAuthenticatedInstrumentation assembleDebug assembleDebugAndroidTest; install APKs; adb reverse tcp:8443 tcp:8443; GuiAuthenticatedInstrumentation phase ui-revision with owned synthetic Avery11701a/Rileyd2198b.
Result: PASS105, authenticated captureRun1791361446586. Real canonical registration/login/two friends/Go persisted SENT/return/logout; actual negative logo/IM+ and theme-entry assertions on Chat/Friends/AI/Plugin/conversation and positive theme-only Settings. Cold->warm->cold->warm verified at unchanged14/.8 preferences; warm22/comfort reachable and no brand/theme row outside Settings. Real default SDK TLS and wrong-hostname rejection PASS. 28 original screenshots total (12 anonymous+16 authenticated), remote SHA256 matched to pulled bytes. source/APK hashes and exact sizes320x640 in manifest.json.

Visual inspection: cold Chat/Friends/conversation/Settings/AI/Plugin and warm22 Settings. Header absent, page/back/state intact; Settings theme entry is narrow and readable without consuming separate global row. No edited/combined mock image. Existing earlier captures retained unchanged.

## Lifecycle

New owned actual Go/PG/NATS project im-gui-product-20261004-50508/session67137, existing valid24h approvedlocalhost/127.0.0.1 CA5C2B8129A44043C0912E4CE413B4799570E92733. Same previously approved readonly ephemeral emulator overlay/helper, no product TLS bypass/system Windows import. Interactive Go stdin lifetime could not route through command recorder; direct owned tool session start/ready/normal stop/label-bounded cleanup observations exposed and recorded as semantic event.

After screenshots full Android trust rollback PASS: exact mount/CA views restored, reboot, fresh init/zygote134CA hashes baseline-equal, paths/mount absent, Enforcing, uid2000; default SDK rejects same-live fixture with SSLHandshakeException. Only owned emulator5590 stopped; Go50508 normal cleanup and exact Docker labels empty. Windows actual desktop Root cleanup remains separately tracked access limitation; no fresh Windows trust write.

## Verification and remaining acceptance

Command: IM_GUI_ASSIGNED_ROOT=<assigned root> python -Xutf8 -B tests/clients/gui/check_sources.py --development.
Result: baseline and final PASS. All source/dependency/frozen/53architecture controls and development recovery, not hosted acceptance.

Windows current styles Human PASS retained (no Desktop source change). Fresh Mobile screenshot set awaits Human visual decision. Taskactive/S2OPEN; all required native/full matrix/Architect/fresh independent Review/exact-head CI/protected integration/verified main synchronization still pending. Mainffd6b63 and unknown/six snapshot screenshot moves untouched. Research Recorder R-GUI-MOBILE-HEADER-20261007 prospective_resume and initial read/private harness prep disclosed; local/Recorder PASS not Task/Gate PASS.
