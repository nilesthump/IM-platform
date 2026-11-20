# Committed message delivery

Fresh regular review passed and the separate specialist review failed on 86ebf3510450013943c22311abb5d5a00c526457, from accepted base 18597c06f15c6ba5d50e055a88890a54f737fd52. The original reports are 86ebf35-regular-pass.md and 86ebf35-specialist-fail.md. The latter includes the per-file catch and fallback inventory. Fix owner /root/fix4 used the assigned H:/.codex/worktrees/java-im/IM-platform on task/LOOP1-JAVA-IM-001.

The Gateway now checks the committed envelope and its six payload fields against MessageCreated, including canonical UUIDs, a positive integer sequence, a timestamp with offset and TEXT length measured in Unicode code points. Shape or timestamp violations fail before any peer operation. The validated event is serialized once before fan-out. A serializer fault propagates through the existing worker IOException boundary with its cause. Only socket writes receive transport-specific recovery. A disconnected transport is removed and closed, allowing other peers to receive the event. An unexpected IllegalStateException on an open peer propagates. Session revocation already serializes outside its socket-write catch and its resource scope retains teardown failures. Binding ACK, rejections and synchronous sends propagate serialization failures. No other production catch or fallback changed.

MessageDeliveryProbe runs from MessageOutcomeProbe on a real bound peer. It removes each required payload field and tests invalid scalar types, noncanonical identifiers, timestamps, a non-TEXT kind, excess text length and an additional field. A structurally valid node injects a serialization exception with a sentinel cause. Checks require an observable failure, no frame and an intact binding. A disconnected second socket is removed and closed while the first receives the complete 4096-code-point supplementary-character frame.

Local verification in research run R-20261120T125234Z-5dcffe59-1a76-45de-bc51-51643784e5af:

| Command | Exit | Time |
| --- | --- | --- |
| python -Xutf8 -B tools/verify_frozen_architecture.py | 0 | 0.094 s |
| python -Xutf8 -B ci/check_architecture.py --scope all --json | 0 | 1.187 s |
| python -Xutf8 -B -m unittest discover -s tests/architecture | 0 | 21.250 s, 99 tests, 1 skip |
| python -Xutf8 -B -m unittest discover -s tests/ci | 0 | 4.859 s, 41 tests, 4 skips |
| python -Xutf8 -B contracts/websocket/verify.py | 0 | 0.094 s |
| mvn -B -f backend/java/pom.xml -Dim.build.dir=EXTERNAL verify dependency:build-classpath -Dmdep.outputFile=EXTERNAL/classpath.txt | 0 | 4.953 s, five tests |
| python -Xutf8 -B tools/verify_java_im.py --build-dir EXTERNAL | 0 | 71.719 s, PostgreSQL and NATS, Java to Go to Java |

The external build directory was %TEMP%/java-im-fix4-build. The initial setup attempted to reuse the coordinator's already associated prompt ID. A fresh registration of the same visible prompt linked to the parent run resolved the error. Startup inspection preceded the prospective_resume run. Local verification is development evidence. Fresh regular and specialist reviews, exact-head hosted acceptance, protected integration and actual-main synchronization remain pending. Last accepted main remains 18597c06f15c6ba5d50e055a88890a54f737fd52.
