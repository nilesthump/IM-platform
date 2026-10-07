# Android requested UI acceptance captures 2026-10-07

Human: Windows desktop ui样式本轮通过，测试Android并给验收截图. Windows styles accepted for this round; scope is visual style, not native notification/tray/CI/whole-task approval. Installed repaired product candidate3f9034978a1e5fd13f62271a7ce18e1f774b514a; capture checkout0663073f7dc239a9ae190224fd176a311f8ccece. No product source changes this round.

## Actual execution

Assigned managed root H:/.codex/worktrees/gui-ui-update/IM-platform; branch task/LOOP1-CLIENT-GUI-001-ui-update, sole writer/root; main untouched. Existing actual Android Studio AVD IMClientSend34, emulator-5590, Android14/API34/x86_64, 320x640 actual pixels. Built from current tree using existing Gradle8.9/JDK17/SDK35 and declared test runners. Preserved current source/APK hashes and all25 original screenshots in manifest.json. Images from Instrumentation.uiAutomation.takeScreenshot PNG, pulled without editing and SHA256 matched on device.

Command: python -Xutf8 -B tests/clients/gui/native.py gui-mobile --serial emulator-5590 --capture.
Result: PASS46 actual anonymous/login/register/navigation-hide/Keystore/appearance controls; captureRun1791359906735. Cold/Warm14/16/22, densityCompact .8 / Comfort1.2 at22; twelve raw screenshots.

Command: python -Xutf8 -B tests/clients/gui/native.py gradle -PimSendInstrumentation=im.platform.client.ui.GuiAuthenticatedInstrumentation assembleDebug assembleDebugAndroidTest; install app/test APK; adb -s emulator-5590 reverse tcp:8443 tcp:8443; am instrument -w -e phase ui-revision -e avery gui_avery_1841ad -e riley gui_riley_57c6b3 im.platform.client.test/im.platform.client.ui.GuiAuthenticatedInstrumentation.
Result: PASS66; fresh captureRun1791360047143; default SDK HTTPS and wrong hostname rejection PASS. Canonical register success, actual login with two friends, initially list without selected detail, real SENT/database delivery, top-left back/list, no navigation in detail, Cold14 compact and Warm22 comfort, logout hides navigation. Thirteen raw screenshots; authenticated.txt contains original public fixture results. Actual Go/Postgres/NATS runtime39112, no fake backend/auth or edited images.

Visual inspection: cold chat/friends/conversation and warm22 chat/conversation plus registration reviewed. Rows contiguous/full phone width, no nav in detail, visible top-left back, both themes readable. Large-font conversation title wraps to fit narrow emulator; no acceptance of all remaining native/Sync matrix inferred.

## Trust lifecycle and cleanup

Reused explicitly approved short-lived CA5C2B8129A44043C0912E4CE413B4799570E92733, exact same localhost/127.0.0.1 scope and readonly ephemeral emulator overlay/helper. Existing older evidence immutable; fresh private state. Install/inherited CA set verified; default real Android SDK TLS/hostname checked. Overlay removed, owned paths removed, reboot; fresh init/zygote134CA sets byte-exact baseline, no owned target mount, Enforcing, adbd uid2000. Fresh rollback instrumentation rejects same-live fixture with SSLHandshakeException. No TLS bypass/product policy change. Original private rollback-check failure due already-absent reboot-cleared reverse listener preserved; idempotent listener observation corrected, rerun PASS.

Only owned emulator-5590 stopped after proof. Owned Go39112 runtime normal stop PASS exact project label cleanup; independent Docker label listings no containers/volumes remain. Windows real desktop Root CA remains a separately tracked cleanup limitation: tools cannot observe the actual desktop store; do not claim Windows rollback from tool-side absence. No root import repeated.

## Guards, decisions and next exact action

Assigned-root/source/dependency/frozen authority53architecture controls/recovery development guard PASS. Boot recorder command inherited emulator lifetime and completed after shutdown; its487s duration is lifecycle wait, not launch time. Research Recorder R-GUI-ANDROID-20261007 uses prospective_resume, prep/read/native runtime input disclosed. Local tests/render captures/Recorder are not independent Task/Stage acceptance.

Windows this-round visual style Human PASS recorded; Android captured set awaits Human visual acceptance. Taskactive/S2OPEN; native proof gaps, Architect scope/full matrix, fresh independent Review, exact-head hosted CI and protected integration/verified main synchronization remain. Retain worktree; unknown main work and six snapshot screenshot moves untouched.
