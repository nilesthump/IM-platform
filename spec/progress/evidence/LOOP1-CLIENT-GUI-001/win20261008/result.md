# Windows runtime recovery and scoped evidence (2026-10-08)

GUI remains review; S2 OPEN. This export is evidence and recovery metadata, not full Task acceptance. Source candidate `79ec62c73b6681b4a544869051722a85521b9b4e`; installed Desktop source `cc13ba1284e3c11a44203377b3ac7adb3d0e25d6`, installed SHA256 `6707f9d5d5b1c1d2fc195b5c9ef91f11fa86b195e20f83b0dc046864ae9f8b8c`. `git diff cc13ba1284e3c11a44203377b3ac7adb3d0e25d6 79ec62c73b6681b4a544869051722a85521b9b4e -- clients/desktop clients/shared` is empty. Gateway only changed under approved ADR0010.

## Environment and source binding

Windows 11 Home Chinese, 10.0.26200/build26200. Actual desktop Explorer parent17236 launched readers and installed client21720; final same-package restart46104. Window CSS1280x840 / physical1942x1273 at1.5 DPI; actual monitor2560x1600. Native notification raw candidate1 directly captures region2040,90,495x272. Standard native capture uses unedited fresh pixels, not a crop of the private full-monitor image. Official NSIS installed package proof is retained in earlier windows-api20261008 evidence.

Only controlled fixture accounts Avery4dada728-e56b-48a0-a84c-d8ae88507adc, Morganc927b63a-e841-4e3a-bbd9-59ca3a8b3f73, Riley825d00d7-a621-4307-b3ae-a501f65f8c14 and Conversation3511b34b-4d5d-46e9-a32e-e936eca78fce were queried. Passwords/tokens/keys are excluded. Credential readers read only owned current-slot metadata and refresh-slot presence/size; no refresh-token value read. Opaque Sync cursor and session-slot IDs are protocol metadata.

## Independent presentation and Gateway decisions

Original independent Architect report/coverage/receipts and separate addon are copied byte-exact. Original41 plus addon2 =43 approved raw images. Five workspace pages × four appearance tuples plus meaningful auth/Chat/Friends/native/restart states are bound in `architect/coverage-final.json` and `architect/addon-hashes.json`. Cold14Compact, Warm14Compact, Warm22Comfortable and Cold22Comfortable use selected Chat and correct Plugin substitutes. Addon accepts actual Windows notification center and restarted Cold14Comfortable Register. Historical original-report native-notification gap is superseded only by separate addon, never rewritten.

Original Gateway independent Review and exact push run37726202795 accept79ec within bounded repair: six selected jobs succeeded, seven correctly inactive. Authority f2f35f26089bc27d4bebe665327f36b2496ee4b8 was independently accepted with run37725245354 before product writes. Existing live-DB test disabled/skipped is disclosed; this Go run is not live-DB or full GUI acceptance. Full changed-range PR CI remains required.

## Runtime and reproducible sequence

Actual Explorer dispatch, strict Windows default TLS health200, current package Login, Settings and exact Tauri WSS now open; earlier exactOrigin403 is preserved elsewhere. Only owned Gateway was rebuilt/reloaded. Native actions use guarded actual-client coordinates/handles and shortcut restore. Method copies are historical executed scripts referencing private fixture/script paths; they are not a standalone public harness and must not be blindly rerun after cleanup.

Select controlled Morgan Chat; send controlled SEND text. For retry, explicitly Refresh current session using `methods/refresh-before-retry.ps1`, reselect/scroll Chat, briefly pause only label-checked owned Core, retry same pending request, capture actual SENDING and Failed/Retry, finally unpause; press real Retry after restoration. Raw SQLite read-only and scoped PostgreSQL receipts bind SENT identity/seq/outbox1, local contiguous4, unchanged reconnected identities. `convergence-derived.json` flattens only PS5 wrapper rows[].value and declares its source hashes. It does not infer durable ACK ordering or atomicity from screenshots.

Expire only controlled Avery session, invoke actual Refresh, capture Session expired and confirm current pointer/former owned credential absent. Relogin; wrong-password shows Invalid username or password. Register mismatch validation is shown with blank secret fields; no successful new registration claimed. Search/add controlled Riley, capture Friends2 and empty new Chat. Login Riley, capture separate account friends/history. Riley native pointer slot changed from9c16e1c5-dad8-482e-80da-09570205f352 to8add5cbc-7f7a-4cb3-9dbf-75f7a4f83ba6 between12:45 and12:53, then Logout removes latest pointer/slot. This is metadata evidence of a replaced owned credential slot; exact rotation cause and older-slot deletion require separate implementation review. Avery baseline and before-expiry have same slot, not a rotation claim.

Hide/Open/Quit use actual native own IM+ tray menu; final new client46104 Quit succeeded. Reopen same installed package after old client21720 Quit; Login retains original Cold14/Comfortable density1.2. Native ToastHistory reports app im.platform.desktop/body Your workspace notifications are ready. Human confirms visibility; actual candidate1 independently depicts own IMPlus group and body at12:51. Earlier history12:04 is not claimed as the same exact notification timestamp. Native notification center toggles restored closed state; other user notifications were not cleared.

## Rollback and cleanup

Actual same-desktop CurrentUser Root remove targeted only approved5C2B8129A44043C0912E4CE413B4799570E92733, while still valid. Exact Root security confirmation verified fixture name/full thumbprint and clicked Yes. Fresh reopen and entirely new actual desktop reader find own CA absent/count74/all other Root thumbprints unchanged. The private complete other-root baseline is excluded; public scoped receipts contain comparison booleans only. Fresh default Windows TLS fails trust while request-scoped original-CA positive health200 proves same live service before expiry. No renewed CA or TLS bypass. Tool-launched Root74 versus actual desktop Root75 is empirical context difference; underlying mechanism remains UNKNOWN.

Core pause finally restored. Original appearance restored; final own clients, fixture processes, containers and volumes all absent. Test installation/controlled local history and own notification history retained; unknown user resources untouched. Helper/config original remains restored; only occupation-blocked helper/native-host regression is PENDING_VERIFICATION_AT_S2_GATE, not the completed real GUI/CA work.

## Preserved failures and exclusions

- Wrong page/unselected captures: cold22 Chat final blank, cold14 Chat actual blank, cold14 Plugin actual AI, Riley account-isolation-chat actual Settings; excluded by Architect and correct substitutes used.
- First Sending/Failed below fold and attempt2 blank after auto session Refresh cannot prove visible states. Nominal attempt2 SQLite sending is actually FAILED and copied under its truthful filename. Valid attempt3 Sending has simultaneous SQLite SENDING; its visual Failed is valid, but earlier SQLite FAILED12:26 is not a simultaneous attempt3 read.
- UIA notification searches found false and small-window probes capture_count0; they are unsuccessful probes, not native visual PASS. First targeted IMPlus image and candidates0/2 depict Codex sidebar and are excluded. Private full-monitor notification inspection contains incidental user data and is NEVER exported.
- Early taskbar tray false positives excluded. Initial unsuccessful tray Quit metadata was overwritten before sealing; original file is unavailable, not falsely reconstructed. New successful native menu binding/actual Quit receipts are original current files; byte-identical repeated tray image is not falsely labeled new pixel content.
- Gateway reload initial build/up succeeded, then PS5 Get-FileHash failed. Separate readonly metadata repair records exact binding without another restart. Original error retained in runtime chronology, not converted to successful command exit.
- Asynchronous Root removal initial1-second no-receipt observation was pending; security confirmation command exited1 after writing its receipt, separately checked successful removal. No duplicate removal or substituted command exit claimed.
- Root Recorder106 events manifest85a495a13ae0330f11b90ee0b6049bcedda3c3739dcb419ed222d4c3b6eea175 is sealed/validated structuralPASS with trace_completefalse. Direct reads/UI/captures/async actions, overwritten unsealed metadata and private incidental inspection gaps are explicit; no complete prospective runtime trace. This Fix run records export and recovery only; initial reads/script preparation direct and its registered dispatch is derived, not verbatim Human prompt.

## Verification and next exact action

Evidence Fix Agent local minimum baseline architecture all/frozen exit0,1579 generated files restored exact; original receipts in `baseline/`. Export verifies43 approved image hashes and scoped receipt hashes; derived convergence checksPASS. No product/dependency/contract/canonical/helper changes.

Next: integrate acceptedmain7088 inside assigned worktree preserving accepted ADR0009/Native done and current GUI state, fresh independent full candidate Review, exact full-range hosted CI, protected integration/actual-main verification and safe synchronization to H:/IM-platform. Main unknown31 status entries/781 files are preserved. Last accepted synchronizedmain7088ecd5c905dceadae8ed2f504d54d6585ca3dc; GUI branch task/LOOP1-CLIENT-GUI-001-resume remains review/draft PR24. This evidence commit is not Taskdone/S2PASS/main synchronization. Historical `prior-current.md` is byte-exact prior recovery, superseded by current discovery only.

Final recovery Development first run failed on three missing exact section headings and known ignored generated-output checker noise; headings repaired and checked isolate/restore rerun follows. Initial failure remains in Recorder.

Corrected Development through checked isolation passes exit0/53 architecture controls/recovery; all1579 generated outputs restored byte-exact. Original failures retained in sealed Recorder. Validation remains local, not independent Task acceptance.

Privacy scan initially rejected whole architecture stdout because its graph contains existing fixture-password literal. Public full stdout omitted, original private output and result hashes preserved. First22-event Recorder was structurally sealedPASS after that failed validation, so it is not evidence of completed export validation; linked fresh privacy-remediation run performs final validation. No secret value or architecture output is rewritten.
