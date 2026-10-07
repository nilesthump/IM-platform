# Final Mobile arrow refinement

Human exact final instruction: 只保留一个←，移除"Chat"，←放大为原来1.5倍。这是本轮最后一个修改要求，完成后直接进行下一步，不再由我确认验收结果。

Product commit `710826740c287333389937c1eeefaf472e68a43d` changes only existing Mobile Workspace presentation and existing actual instrumentation. Arrow uses current MaterialTheme labelLarge font size times1.5; at preferences14/22, label12/20 becomes18/30sp. Same closeConversation action; accessibility description Back to chats retained without visible Chat text. Desktop unchanged; no library, contract, session or TLS policy change.

## Local verification

- `python -Xutf8 -B tests/clients/gui/native.py gradle '-PimSendInstrumentation=im.platform.client.ui.GuiAuthenticatedInstrumentation' assembleDebug assembleDebugAndroidTest`: exit0 build PASS. Earlier unquoted PowerShell argument split failure retained in Recorder; repaired shell quoting, no product workaround.
- Actual API34 x86_64 IMClientSend34/emulator-5590, 320x640, `GuiAuthenticatedInstrumentation` phase ui-revision: exit0 PASS107, fresh default SDK HTTPS and hostname-negative controls; real Go/PG/NATS fixture im-gui-product-20261004-38684 host18443 forwarded device8443; Avery/Morgan/Riley synthetic accounts only. Authentication, registration, real durable SENT, arrow-only/no Chat negative checks, return list, Settings-only theme/font/density retention and logout covered. Cold14/.8 and Warm22/1.2 screenshots visually inspected by implementer as local verification, not independent Architect acceptance.
- Sixteen original unedited native screenshots pulled from captureRun1791363374546, every remote/local SHA256 identical; exact original PNGs/APK/source hashes in manifest. Previous anonymous46 and unaffected header28 screenshots remain original prior evidence, not relabeled new captures.
- Complete Android temporary readonly CA rollback: init/zygote134CA hash sets equal baseline, own mounts/files absent, uid2000/Enforcing, reverse removed, fresh SDK SSLHandshakeException to same still-live fixture. Owned emulator stopped; owned Go fixture stopped and cleanup verified separately. No Windows trust change this iteration; actual desktop-context exactCA cleanup remains unverified from tools.

## Acceptance scope

Human explicitly eliminates another Human visual confirmation step and directs next workflow. This is recorded as instruction, not invented complete Architect/Task/Gate PASS. Independent Architect and unified candidate review begin next; exact-head hosted CI/protected integration/main verified synchronization pending. Full Windows native Chat/Friends/notification/tray proof remains affected by supported host setup/approval-channel failure. Prior Human Windows style PASS and real login reports preserved; synthetic compiled-browser screenshots never substitute native proof.

Branch task/LOOP1-CLIENT-GUI-001-ui-update; main H:/IM-platform SHAffd6b63ac9396e577f0bb5c3d3ac02ee4915d597 untouched, unknown work and six archive screenshot moves preserved. No task done or S2PASS asserted.

Final source/architecture/frozen/recovery development guards exit0 PASS (53 architecture tests). Owned Docker project38684 container and volume label lists both empty, adb devices empty. Recorder R-GUI-MOBILE-BACK-20261007 finishedPASS/validate-run and validate-repository PASS; unsupported event type attempt exposed and corrected through public API. Interactive runtime/capture/metadata command gaps explicitly disclosed. Research structural PASS is not independent Task acceptance.
