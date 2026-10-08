# Mobile hosted failure: observed cache repair, independent acceptance pending

Fresh exclusive Fix Agent `/root/gui_mobile_ci_fix` resumes clean assigned `H:/.codex/worktrees/g/IM-platform`, branch `task/LOOP1-CLIENT-GUI-001-resume`, base `6f21e00f8731020e6344545e1383854a5354b6e9`. GUI remains unique review/S2 OPEN; no self-acceptance, main synchronization or Task completion.

## Original mandatory hosted FAIL

Exact full PR run37733952699 at6f selects14 actual instances:12success, MobileFAIL and gateFAIL; none skipped. Byte-exact independent failure receipt and final GitHub metadata are in hosted-fail/. Earlier local/source Review744 and metadata Review6f remain their historical scoped PASS; earlier11success/Windows-pending snapshot is preserved beside the final12success result. Windows6fPASS cannot accept a later head. Only occupation-blocked helper regression is deferredS2Gate; this Mobile failure is a current repair requirement.

## Actual reproduction and cause

Owned isolated API34 Google APIs x86_64 emulator `IMGuiFix20261008` / emulator-5592,320x640/dpi160, Windows emulator36.5.11/image revision14, all animation scales0. Hosted was Linux emulator37.2.12. Unmodified capture matrixPASS46, three unmodified no-capturePASS46 and complete SQLite→SEND→Sync→GUI predecessor sequencePASS were preserved; these early passes did not erase the hosted failure.

A temporary failure-only static-label probe then reproduced the SAME `Actual Compose control missing: Confirm password` at warm-register-16. Original cached accessibility root still exposes `Open your workspace` / `New here? Create an account`, and has no Confirm password. Without retrying or changing the result, clearing UiAutomation cache exposes actual `Create your account` / `Confirm password`, visible bounds[52,338][191,362], and Already have an account. Both roots belong to im.platform.client and have no scroll container. The original failure screenshot visibly shows the registration field, without keyboard/viewport obstruction. The test failed on a stale accessibility tree; the product had rendered the correct form. Original FAIL, diagnostic source and raw screenshot/APK binding are immutable in reproduced-cache-failure/. Derived diagnostic.diff is explicitly reconstructed from6f source and original probe source, not an original command output.

## Minimal repair and verification

Only `GuiInstrumentation.kt` adds `actualRoot()` to clear the accessibility cache before reading the real active root, matching existing GuiAuthenticatedInstrumentation, and routes its observations/scroll actions through it. No retry limit, sleep, required label, registration mismatch assertion, secure-storage assertion, font/theme matrix or PASS predicate changed. Temporary failure probe/harness/artifact workflow edits were removed after identifying the cause; no debug framework remains. No production source, framework/dependency, canonical/public contract, security boundary, database, native Desktop, helper or Windows trust changed.

The same capture scenario passes46 and three exact no-capture runs pass46 each. App APK SHA256 `6bbcd0bcec1216d9f8239c03c5b8e7e62c7ee3197b0c7aa903c1695200c03d30` is identical before/after; repaired test APK and source hashes,12 raw images and exact no-capture outputs are in after-fix/binding.json. The old approved Windows43 / Android presentation sets are unaffected because production bytes are unchanged. New captures are diagnostic regression evidence, not a new Architect or full Task acceptance claim. Original screenshot pixels were not edited.

Commands, exits, durations and raw private-output hashes: commands.json. Initial clean baseline architecture/frozen/53controls/Acceptance PASS;1579 known generated files restored byte-exact, baseline/clean-acceptance-result.json. Canonical a6b1670 unchanged. Post-fix architecture/frozen/53controls/Development PASS;1582 known owned generated files restored byte-exact, post-fix-baseline/local-verification.json (unclean source/evidence ownership explicitly recorded). Fresh independent clean Acceptance is required before publishing/integrating this candidate.

## Cleanup, instrumentation and next action

cleanup.json verifies owned reverse bindings empty, original cold16/standard appearance restored, sole fixture credential slot absent, own emulator stopped/disconnected. Only the new private AVD disk is retained for reproduction; no system trust changed and existing emulators/unknown files were untouched. Existing harness process-only test CA fixtures closed and adb reverse removed in finally; no Windows CA import/renewal or real service launched. Main7088/31unknown status entries/781protected files remain untouched.

Recorder R-MOBILE-CI-FIX-20261008 is prospective_resume with incomplete pre-Recorder trace. Direct startup reads, preparation, image inspection and a file-ending correction are disclosed. Registered prompt is an agent-authored continuation summary that was incorrectly tagged source human; immutable original and semantic correction retained, not a verbatim Human prompt claim. Research validation is structural evidence only. Private whole hosted Mobile log is not exported; public evidence is limited to original allowlisted receipts, static labels/geometry, controlled anonymous pixels and hashes. No editable/password values were output by diagnostics.

Next: fresh independent Review of exact committed repair and these bindings, full-range exact-head hosted CI including real Linux API34 and both Desktop jobs, then protected integration/actual-main checks/safe synchronization. No Taskdone or S2PASS before the complete chain.
