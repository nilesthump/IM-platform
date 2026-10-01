# Fresh fix of independent SQLite FAIL

Starting ee82e9ff459558907998d5e68e7097386e2b7f14; fresh sole Fix /root/s2_sqlite_fix1, neither original implementer nor failed Reviewer. Branch task/LOOP1-CLIENT-SQLITE-001-ts-kotlin. Task remains review, no selfacceptance/egress/original directory edits.

## Findings and minimality

P1: minSdk34 replaces unaccepted minSdk26 engineering binding. Targeted UPSERT/conflict-DO-NOTHING requireSQLite3.24; targetless conflict-DO-UPDATE requires3.35. API26=3.18, API30=3.28, API31-33=3.32; API34=3.39/3.42. Strongest current SQL requirement3.35. Current CREATE TABLE/UNIQUE/CHECK, ordinary SELECT/INSERT/UPDATE/DELETE/EXISTS/COALESCE/MAX/CAST, PRAGMA user_version/transactions are older; recursive CTE UPDATE3.8.3. No newer constructs, product RETURNING, JSON/virtual/generated/STRICT/window features used. Actual minimum34 config/README/CI/verifier aligned; verifier rejects newer substitutes, checks boot1/CEtrue and requires install+cleared-data full runs. Built-in SDKSQLite and current authority/responsibilities unchanged. minSDK26 was never accepted; no frozen minimumOS constraint found. This corrects an engineering binding without changing canonical public protocol compatibility/contracts.
Sources: https://developer.android.com/reference/android/database/sqlite/package-summary ; https://www.sqlite.org/lang_upsert.html ; https://www.sqlite.org/lang_with.html .

P2: TS string iteration codepoints and Kotlin built-in codePointCount match unchanged canonical4096character maxLength. Actual two-platform assertions accept4096 U+1F600, reject4097 for local/Sync, preserve durable rows/cursor/contiguous and reopened history. No new library/parser/adapter/contract.

Evidence: independent-failed-review.zip byte-preserves60 public files, original FAIL/report/result/audit/finished Recorder and manifest; failed-review-archive-manifest.json records every hash. All22 original gzip archives preserve persisted blobs; historical-persisted-blob-manifest.json separately records compressed/persisted/raw hashes. Original C-790638b6-f9e9-42ae-81e6-5273a8292b19.stderr and C-f29009bd-da24-409d-b2d5-a13e63b1a61a.stdout raw-vs-persisted differences explained. No old history/events/hashes/FAIL rewritten.

## Actual local verification

Command: bundledPython -B tools/verify_client_sqlite.py --scope desktop through external fix1/tool.py desktop.
Result: both TS package builds PASS; cargo locked atomic rollback/read-only unit1PASS, no ignored; actualSQLx canonical13cases106assertionsPASS. Unchanged native source reused released Review target cache, current crate rebuilt with fresh fixture databases; not claimed independent/new-empty native compilation.
Command: bundledPython -B tools/verify_client_sqlite.py --scope mobile --serial emulator-5584 through external fix1/tool.py android.
Result: explicit cached verified Gradle8.9/JDK17 fallback build62tasks41sPASS, not official wrapper acceptance. Fresh owned hidden IMStorageFixMinimum34 AVD, stableAPI34 GoogleAPIs x86_64 image revision14/memory2048MB. boot_completed1/user0CEtrue; actualSDK34/sqlite3.39.2. First install13cases105assertionsPASS; pm-clear Success and full second13/105PASS. Both INSTRUMENTATION_CODE -1. Pixel_8_Pro/sharedADB untouched. Only proved owned5584 stopped, AVD retained externally. No privateADB/AVDuserdata/SDK/build caches committed.
Command/results of clean committed source/recovery/frozen/architecture/CI/contracts follow checks.md. Local results not independent acceptance; Task remains review/S2OPEN.

## Retained failures/instrumentation

Original independent API37 directory first-run FAIL, unchanged-APK retry13/97PASS and pm-clear NotificationManager/system-crash limitation remain byte-identical FAIL evidence. No invented directory product repair, no preview retry. Stable minimum fresh install/clear local evidence separately recorded.
Startup WindowsPowerShell5 lacked Get-FileHash; PowerShell7 retry live recovery failed ignored node_modules scan. Both retained; clean source checkout required, no checker/GString weakening. External preserve helper field/quote errors retained. SDKmanager warned schemaXML4 vs supported3 for historicalAPI37 metadata; actual official34 image installed.
Prior wrapper download failure retained, actual hosted clean pinned wrapper mandatory. Known Windows4symlink skips require real LinuxCI. Initial/setup passive reads/web/external helper preparation outside Recorder explicitly incomplete prospective_resume; exact8184byte assignment SHA b9743dcc3d5b565cf36a6cfb9e9b6873208285fc1775f1bb7c67705d925bf6a2. R-SQLITE-FIX1-20261002 parents failed R-SQLITE-REVIEW-20261002, related Coordinator run. Finished validated external manifest returned after final clean commit.

## Recovery boundary

Last independently accepted actualmaina28752967ddd471cd281aece7ea9b343521356e8; S1PASS/S2OPEN. Historical GString FAIL/WAIVED_BY_HUMAN immutable/not reopened. Original744files/withdrawn implementation untouched.
Next NEW independent Review fulla287..final candidate and applicable real exactHEAD hosted jobs before administrative done. Human directs SQLite completion, authorized PR/merge, safely sync H:/IM-platform preserving unknown files, record progress, STOP before next implementation. No SEND/SYNC/WEB activation. Task PASS is not S2 Gate PASS.
