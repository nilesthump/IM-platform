# PR105 hosted failure repair

Branch `task/LOOP1-JAVA-AUTH-001`. Original candidate `2b8bcad24b5dddb82495a3e72b69ef045f73e899` passed regular-review8 and error-review7 before publication. [Push CI](https://github.com/nilesthump/IM-platform/actions/runs/44705751115) and [PR CI](https://github.com/nilesthump/IM-platform/actions/runs/44705841479) both failed Java and shared. S1/S2 remain accepted; S3 and this task stay open.

* Java: a logout committed immediately after the bind ACK could be consumed by the bind handler's second Session lookup. Its synthetic REVOKED then preempted the actual LOGOUT. The repair registers signed claims and reads authoritative session state while holding the socket's monitor. Revoke uses that same monitor to retire the binding and deliver the committed reason after the ACK. A rejected credential produces its ordinary rejected ACK; failed validation or send removes the provisional entry and internal errors propagate.
* A deterministic probe uses real PostgreSQL, the real Gateway and a test transport that commits a logout at ACK send. It then publishes the corresponding LOGOUT via real NATS after the handler returns. Compiling the original Gateway from 2b8bcad2 with this new probe failed at the expected wrong reason. The repaired Gateway sent LOGOUT and closed the transport. The canonical end-to-end HTTP logout cases and simultaneous refreshed-peer case also pass.
* Shared: the isolated smoke transport returned 101 for every Origin and had no double for Java Auth HTTPS/WSS. The isolated test now supplies the expected forbidden response and checks invocation of the Java probe on its configured endpoint. The real Java register/login/bind/logout transport assertions run as before in the deployment test. Existing cleanup, dual-failure, native exit and environment assertions remain active.

Local commands used bundled Python with `-Xutf8 -B`, the same disposable PostgreSQL/NATS configuration as the previous fix and a fresh external Maven build directory. Recorder run `R-NOV20-HOSTED-FIX` in `nov20-hosted-fix/research` has incomplete pre-Recorder startup reads. Verification output is in that external run directory.

- Exit 0 in 1.063 s: `python tools/verify_frozen_architecture.py`
- Exit 0 in 1.891 s: `python ci/check_architecture.py --scope all --json`
- Exit 0 in 31.515 s: `python -m unittest discover -s tests/architecture`
- Exit 0 in 7.61 s: `python -m unittest discover -s tests/ci`
- Exit 0 in 0.11 s: `python contracts/websocket/verify.py`
- Exit 0 in 6.312 s: `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1`
- Exit 0 in 115.062 s: `python tools/verify_java_auth.py --build-dir <external> --profile java`
- Exit 0 in 25.453 s: `python tools/verify_java_auth.py --build-dir <external> --profile go`
- Exit 0 in 40.953 s: `python tools/verify_java_auth.py --build-dir <external> --profile-switch`
- Exit 0 in 62.907 s: `python -m unittest discover -s tests/contract/group -p test_verification_failures.py`

Maven offline verify and classpath build succeeded. After narrowing the validation catch, the final build and Java 28-fixture suite passed again. Running Java deployment smoke without CI configuration returned 502 and exited 1; running the exact committed disposable configuration preparation followed by real `tests/infrastructure/smoke.ps1 -Profile java` passed. No schema, contract or dependency edits. This worktree is owned by /root/hosted_auth_fix. Next: fresh regular review, different fresh error audit on the same new SHA, exact-head hosted CI, protected integration, actual-main verification and safe synchronization. Last accepted main e4aee5ce2c4327904990d5c651267ca5eaae389d.
