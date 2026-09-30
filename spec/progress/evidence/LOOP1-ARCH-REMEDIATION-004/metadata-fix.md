# Fresh Stage004 metadata correction (not self-acceptance)

Base2a080785c88f83187a19ee826ad9d469a5a7aaea, branch task/LOOP1-ARCH-REMEDIATION. Fresh Fix /root/stage4_metadata_fix does not accept or push. Prior independent product Review PASS87c0ee2 is preserved. Root recovery metadata check identified FAIL; new independent post-fix Review and exact-head hosted acceptance remain required.

## Audit and exact correction

Scanned46 unique current entry/task/acceptance/governance/handoff/batch/checkpoint documents, including ten metadata paths changed by003 closure6cdd981 through HEAD. Strict Path UTF-8 and subprocess encoding=utf-8. Only task004 Inputs line17 and Execution Constraints line23 contained confirmed corruption. metadata-audit.json records exact locations and lines. Compared6cdd981:spec/tasks/active/LOOP1-ARCH-REMEDIATION-004.md and approved v1.1: §3/§10/§11/§12-14 and §3/§10 SRC-01 through SRC-07/§11. Restored seven section signs U+6402 (UTF-8 e6 90 82) -> U+00A7 (c2 a7); no blanket Chinese replacement or semantic change.

Task004 owner/Next Action and current.md now reflect actual Fix/new Review/hosted sequence, unique004 review; obsolete predecessor-wait removed. Corrective point appended without erasing previous PASS. Existing004 allowed paths cover both current documents and new task-linked evidence/Recorder. No added scope.

## Verification

| Exact command | Exit | Duration ms | Result |
| --- | --- | --- | --- |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe spec/progress/evidence/LOOP1-ARCH-REMEDIATION-004/verify-metadata-fix.py` | 0 | 484.0 | PASS |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe ci/check_architecture.py --scope all --json` | 0 | 532.0 | PASS |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 5281.0 | PASS |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest discover -s tests/ci -v` | 0 | 2500.0 | PASS |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | 5969.0 | PASS |
| `git diff --check -- spec/tasks/review/LOOP1-ARCH-REMEDIATION-004.md spec/progress/current.md` | 0 | 32.0 | PASS |

All-source scan zero violations, frozen verifier34 architecture tests zero skips.27 CI tests PASS with four historical Windows symlink privilege subcase skips. Evidence-only verify-metadata-fix.py checks exact references, two corrupted UTF-8 mutants rejected, unique004review/recovery and protected backend/contracts/deploy/ci/tools/tests/spec-architecture unchanged relative87c0ee2. Go tree `d012c02bb8ee577f3e7cbced3a8fef92cc30315a` identical. No changed-product live tests asserted; previous real integration/role/TLS Review evidence remains preserved and new Review/hosted pending. Recovery Development is explicitly non-acceptance; clean Acceptance will run after candidate commit.

## Instrumentation

Run R-20260930T151119Z-4ec8a9af-7a99-4f82-bc02-b3daeac138d3 prospective_resume exposes startup reads before tracing. Prompt is explicitly agent delegation summary, not complete Human prompt. Direct bounded edit is documented here; validations routed through command Recorder. Finished16events validate-run PASS is instrumentation only. Run-local blobs/** -text protects saved bytes during Git transport. Raw hash audit detected two existing Recorder UTF-8 decoding mismatches in Chinese Windows outputs; details below. These finished artifacts remain unchanged; do not claim raw-output integrity PASS. Other blobs match recorded hashes, and all saved blob working/index bytes will be checked. New independent Review reruns required acceptance from clean head.

[
  {
    "blob": "blobs/C-4d95083f-997d-49a2-a39e-18b31c501697.stdout.txt",
    "recorded_raw_sha256": "f610015d69ac709f7eed7845de02261bb29a121ec560ea03a117f68374516f85",
    "saved_sha256": "a16b612816741d49fcb75bdce8358d68e0ab10e0fa32e1c591fd58fd3070d956"
  },
  {
    "blob": "blobs/C-460e034c-9de3-445d-8895-366fd8921f4a.stderr.txt",
    "recorded_raw_sha256": "2b655c771565a9ab972a391dd9922b7630e2caf0f4124c75d55a7483d2b4a29e",
    "saved_sha256": "05f973f03da06539c85effa77b89b0ad6063a2ed3ef1a0d4cf2615dadd181b86"
  }
]

## Corrective command failures (preserved)

Evidence raw-hash assertion first failed because two raw-vs-saved captures differ; run was finished and validated, never rewritten. First staging attempt incorrectly assumed prompt registry was a JSON file rather than a directory and failed pathspec atomically. Consequently index comparison and commit failed, then clean Acceptance failed because changes were not committed. These were ordinary local command failures, not PASS or stop reasons; corrected exact prompt directory staging follows.

Capture C-4d95083f-997d-49a2-a39e-18b31c501697 stdout: command `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe ci/check_architecture.py --scope all --json`; raw SHA f610015d69ac709f7eed7845de02261bb29a121ec560ea03a117f68374516f85; saved SHA a16b612816741d49fcb75bdce8358d68e0ab10e0fa32e1c591fd58fd3070d956; U+FFFD count 0; secret_redaction_applied=True. Existing Recorder decodes UTF-8 errors=replace; Windows command output invalid UTF-8 is replaced before saved text. No redaction or transport repair explains this mismatch.

Capture C-460e034c-9de3-445d-8895-366fd8921f4a stderr: command `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest discover -s tests/ci -v`; raw SHA 2b655c771565a9ab972a391dd9922b7630e2caf0f4124c75d55a7483d2b4a29e; saved SHA 05f973f03da06539c85effa77b89b0ad6063a2ed3ef1a0d4cf2615dadd181b86; U+FFFD count 60; secret_redaction_applied=False. Existing Recorder decodes UTF-8 errors=replace; Windows command output invalid UTF-8 is replaced before saved text. No redaction or transport repair explains this mismatch.

validate-run verifies schema/event chain/manifest, not original raw-output equality. New metadata documents are UTF-8/LF with no replacement character; only exact task references restored. Protected trees remain identical.
