# Runtime file occupation cause

Read-only diagnostic request: 找出被占用的文件及占用原因. No process termination, ACL mutation, binary replacement or sandbox-policy change in this run. Existing task remains review/BLOCKED_EXTERNAL_ACCESS/S2OPEN.

Current fatal target:
C:/Users/21441/AppData/Local/OpenAI/Codex/runtimes/cua_node/2c9e75c4e9c71beb/bin/node_modules/@oai/sky/bin/windows/swift/x64/VCRUNTIME140_1.dll

Actual loaded module in codex-computer-use-swift.exe PID29164, start2026-10-07 19:38:25 Asia/Shanghai; parentPID53016 ChatGPT.exe in installed OpenAI.Codex_26.1002.6548.0 app. Module version14.42.34433.0, Microsoft C Runtime Library,49,152 mapped bytes. Earlier exact helper30244 was stopped during previous authorized minimal repair, then app-created29164 reloads the same module; new sandbox setup at19:38:25 fails opening it before requested git execution. Ordinary library loading is expected; conflict appears during sandbox runtime ACL validation.

Earlier fatal target:
C:/Users/21441/AppData/Local/OpenAI/Codex/runtimes/cua_node/2c9e75c4e9c71beb/bin/node_repl.exe

Previously executed/mapped by six actual Codex workers13072/30188/36416/37080/46072/49184. All stopped in previous authorized bounded repair; current inventory has no node_repl process. Error advanced toDLL. Therefore DLL is current blocker; executable is a confirmed earlier blocker.

Same liveDLL handle probes, OPEN_EXISTING, sharingRead|Write|Delete, no WriteFile/SetSecurityInfo calls:
- GENERIC_READ succeeds; GENERIC_READ|GENERIC_WRITE failsWin32error32.
- Exact-source flags FILE_FLAG_BACKUP_SEMANTICS: READ_CONTROL succeeds; READ_CONTROL|WRITE_DAC succeeds; MAXIMUM_ALLOWED failsWin32error32.
- Current user owns file with inheritedFullControl; CodexSandboxUsers hasReadAndExecute. Permission-specific open success distinguishes this conflict from missing ACL rights.

Local codex.exe --version reports0.162.0-alpha.2. Matching public tag source:
https://github.com/openai/codex/blob/rust-v0.162.0-alpha.2/codex-rs/windows-sandbox-rs/src/acl.rs#L529-L536
https://github.com/openai/codex/blob/rust-v0.162.0-alpha.2/codex-rs/windows-sandbox-rs/src/setup_provisioning/setup_runtime_bin.rs#L126-L137

Source inspection: runtime traversal grants each file with inheritance0. Root-only path opens MAXIMUM_ALLOWED before ACL/no-op inspection; the exact log context is open ACL target for root-only update. This asks for broader access than ACL work needs and locally reproduces the sharing violation on the running image. Fatal runtime validation propagates to setup refresh, blocking shell/native startup. Application auto-recreation of its helper repeats the occupation, explaining why stopping that helper did not solve the failure.

Evidence establishes the local loaded-module/open-mode conflict and strongly supports the matching-source access-mask defect. Installed setup helper was not debugger-instrumented/hash-matched to source; its actual CreateFile DesiredAccess is not independently captured. Do not present that unavailable binary-call detail as measured. Reports from other users are not this installation's evidence.

Correct fix direction follows current evidence: sandbox implementation should inspect with READ_CONTROL and request WRITE_DAC only when actually needed, retaining all ACL/deny/security checks. This diagnosis does not authorize patching installed binaries, deny-ACE workaround, disabling sandbox or widening permissions. Repeated helper restarts/reboots are not established repair. Next action supported corrected sandbox helper/runtime build or supported implementation repair; then normal sandbox+sky regression and existing fullGUI acceptance chain.

Private Recorder R-GUI-LOCK-CAUSE-20261007 at H:/.codex/gui-handoffs/20261007-lock-cause/research, prospective_resume with initial read-only startup/process/module inspection and web-source reads outside command capture disclosed. Old immutable evidence retained. /root owns new recovery/current/task/evidence only; no push/main sync, last acceptedmainffd6b63 and previous local5a22f35 retained.
