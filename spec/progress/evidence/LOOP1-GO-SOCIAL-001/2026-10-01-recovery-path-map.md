# Preserved Social recovery and exact future file map

New base accepted actual279c1dc, integrationPR2/mainCI36764254107PASS. Old worktree/task branch clean5b35735 unchanged; original Human stop/chat01a0ecc1 final confirms pause/no Review/no Social hostedCI. Old implementation2a6eaa1 tracked files only inspected. No unknown original file contents consumed or old governance copied. New worktree branch taskLOOP1-GO-SOCIAL-001-v1.1 protects old branch/history.

| Actual path | Responsibility/necessary modification after readiness | Verification/old source |
| --- | --- | --- |
| backend/go/core/auth.go | Existing private handler adds GETfriends/PUTfriend only; existing search/auth/errors remain | old2a6eaa1 auth.go two-route diff; publichandler canonical tests |
| backend/go/core/social.go | Adapt old tracked social.go package main to private Core/approved helpers; normalized pair lock/unique DIRECT/two memberships/Sync/Outbox same tx | concurrency/DBunique/rollback/canonical outcomes |
| backend/go/core/social_test.go | Adapt old tracked social_test.go private transaction/concurrency/rollback probes to Core tests; retain substantive controls | real disposable migratedPG/NATS/race, no skip |
| backend/go/tests/social_test.go | Actual blackbox test package reuses auth helpers; canonical search/friend/authorization fixtures | same frozen fixtures, independent negative controls |
| Existing core/http.go/outbox.go/gateway/shared/main.go | No currently necessary edit; no duplicate assembly/auth/router/dispatcher or fullCore service inGateway/shared | source/import/frozen/authWSSfallback regressions |

This is an inspected future adaptation map, not a claim old products were already reused in new checkout. Oldsocial.go/social_test.go depend on rootpackage-main authService/private helpers, so whole-tree cherry-pick would violate accepted layout. Existing search is already accepted. No product file copied or rewritten yet: required403 input is unresolved, must not build speculative permissions to make a fixture pass. Actual canonical negative friend-add-authorization-denied: authenticated principal not permitted to mutate A; request PUT/v1/friends/B with <insufficient-scope-token>, expected403AUTHORIZATION_DENIED/no effects. Current JWT six claims/owner implicit in bearer subject supplies no declared scope/owner-request field. Fresh reviewer must find existing approved constructible context or confirm smallest decision. Preserve contract/fixture bytes; no waiver/no fake execution.
