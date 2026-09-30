# Final hosted candidate failure: repair required

Exact reviewed closure92306df501b83986d40f870113b84a5f4eb6a980 was normally pushed; ls-remote confirmed same SHA. Actual hostedrun36738064831 completed failure: all13 jobs executed,11 success, Go and consequentGate failure. No job skip/cancellation/missing. source_go,architecture,source_java and actual roleTLS deploy passed. Full external jobs/steps: hosted-ci-36738064831.json.

Go nonrace passed. Go race TestPostgresAuthSessionAndWSS failed auth_test.go:211: expected replacement revocation, received session.revoked with reason REVOKED. Actual log is preserved in Coordinator run blob C-a27093df-f5a4-48d1-bc53-e283551af1dc.stdout.txt. Retrieving logs exit0 is not CI PASS. Current safety watch uses a generic REVOKED reason and may win the CoreOutbox/NATS notification; this is a diagnosis to verify, not an architectural decision or permission to relax test expectations.

Fresh Fix must reproduce delayed notification/watch interaction and fix grounded existing semantics while preserving Core ownership, readonlyGateway, no per-messagePG, existing tests and canonical contracts. Then a NEW independent Reviewer and NEW exact-head hosted CI. Task004 stays review; batch andS1 not passed. Previous local independentPASS and prior accepted stages remain historical facts, not hosted acceptance of this candidate.

Coordinator resumed pretrace is explicitly incomplete; registered prompt is the exact visible resume message, not the full original four-stage instruction. Recorder R-20260930T153615Z-e6579dbc-ca28-461a-b8ff-7e0f6cd4c1e6 closes FAIL for this unsuccessful hosted acceptance attempt. No product/authority/history changed by this Coordinator round.
