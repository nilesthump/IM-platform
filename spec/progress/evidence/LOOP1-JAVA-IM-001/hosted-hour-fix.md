# Hosted Java failure and WSS verifier repair

Branch `task/LOOP1-JAVA-IM-001`, previously reviewed candidate `7ff6d1ed68dd30ec033b3e6f7f11c608cb216728`, accepted main `18597c06f15c6ba5d50e055a88890a54f737fd52`. Owner /root/hostedfix. S3 OPEN, task in review.

| Independent record on 7ff6d1ed | Result |
| --- | --- |
| Fresh regular review (7ff6d1e-regular-pass.md) | PASS, original SHA-256 fecf775ad29efaadcc9d6514d2d48fd0407152b4bafdadf544cd909c40006dcf |
| Different fresh specialist (7ff6d1e-specialist-pass.md) | PASS, original SHA-256 edb7084713b9432e66aa3bcd9ffcd7b90d068592e68bc50749971ab85ace269c |
| [Push Java job](https://github.com/nilesthump/IM-platform/actions/runs/44747421689/job/136326612081) | FAIL, ubuntu26/20261116.202 |
| [PR107 Java job](https://github.com/nilesthump/IM-platform/actions/runs/44747485726/job/136327024889) | FAIL, ubuntu26/20261116.88 |

Both Actions API run objects name the exact reviewed SHA. Both Java logs show the live IM runner failed at MessageOutcomeProbe.java:104 and /usr/lib/python3.14/subprocess.py. The hosted logs identify the interpreter minor series. The external Windows reproduction used CPython 3.14.3 and local CPython 3.13.14. Of all eight original schema-derived probe inputs, only 2026-01-01T24:00:00Z differed. The earlier interpreter rejected it, and 3.14.3 accepted it as the following day's midnight. The Java probe rejected the oracle-labelled positive and failed. The hourly range in RFC 3339 §5.6 is 00–23, and the wire schema declares date-time.

Human decision: “授权修正验证器，00–23 保持有效，24:00:00 拒绝”. Recorder R-20261120T140058Z-42474367-714e-468e-b2ed-4818eba96fac, decision HD-d155f1f5-6994-467e-aa3c-3fdfb7fde24f. Reusing the coordinator's prompt registration was refused because it already belonged to a run. Registered the original visible request and new Human decision for the fix run.

The WSS verifier checks the source hour at midnight so CPython's normalization cannot change the wire result. The existing Invalid boundary reports rejected wire data. Numeric offsets, fractional seconds, calendar and basic/week-date spellings are covered. Explicit expected outcomes in the offline suite exercise the oracle independently of Java. The live runner passes the additional wire inputs through both committed ACK and fan-out checks. This change leaves schema and golden fixture bytes intact.

| Local command in the assigned worktree | Result |
| --- | --- |
| python -Xutf8 -B tools/verify_frozen_architecture.py | PASS |
| python -Xutf8 -B ci/check_architecture.py --scope all --json | PASS, zero violations |
| python -Xutf8 -B -m unittest discover -s tests/architecture | PASS, 99 tests, one skip |
| python -Xutf8 -B contracts/websocket/verify.py | PASS on 3.13.14 and 3.14.3, 23 schema and 26 behavior controls rejected |
| python -Xutf8 -B tools/verify_java_im.py --build-dir EXTERNAL | PASS on 3.14.3, 74.240 s, real PostgreSQL/NATS Java → Go → Java, ADR-0004 deferral |
| python -Xutf8 -B ci/classify.py --paths contracts/websocket/verify.py | Selects Java and all full compatibility jobs. The Java workflow invokes the live IM runner. |

The cross-version sweep of 2,268 date/separator/hour/time/offset combinations produced identical ordered verdicts on both interpreters (1,458 valid, results digest 17fd8fad8e18555be0aac0d9e55fb4e1bf996c40b6a57982616854e34506e7c4). An initial negative-control setup failed locally because the ACK factory validates during construction. The corrected test mutates a valid ACK and both interpreters pass. Fresh independent regular review, different fresh specialist, exact-head acceptance, protected integration and actual-main synchronization are pending on the replacement.
