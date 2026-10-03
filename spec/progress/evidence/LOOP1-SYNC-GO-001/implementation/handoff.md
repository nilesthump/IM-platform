# Go Sync implementation handoff (local evidence only)

Base accepted actual main: 4d5fe1235e4f01111d78cc67b2880b52cac072f2.
Activation: a1fe74b, assigned managed root H:/.codex/worktrees/sync-resume/IM-platform,
branch task/LOOP1-SYNC-001. Actor /root/sync_go_implementation owns task changes.
Human exact reply "同意" authorized Go plan after prerequisite acceptance.
No independent Review, hosted acceptance, protected integration or main synchronization
is claimed by this implementation report. S1 PASS / S2 OPEN; client SYNC stays backlog.

## Changes and present justification

Two public POST handlers in Core sync.go; auth.go adds exactly two registrations and
a precise two-POST-path delegation before legacy query interception. Coordinator
authorized that narrow routing correction because canonical query errors must echo
a decoded valid body UUID, which the legacy query interceptor cannot do. Non-Sync
Auth query restriction is regression-tested unchanged. Gateway remains existing proxy.

User cursor is existing-key domain-separated HMAC over account UUID and internal
cursor position, opaque raw base64url; initial0, account-bound, replayable across Sessions,
no expiry or new key source. Internal persistent producer payloads remain unchanged.
Four allowed metadata kinds are projected; Session control events are excluded.
Known positions are checked against eligible persisted events before replay.
Existing social.go locks both canonical account rows before writeSocialEvent allocates
all current friend.changed/conversation.changed/membership.changed event IDs. There
is no current plugin.changed producer. Its projection is fixture-only using canonical
schema and existing user-row serialization; no speculative plugin product was added.
User read waits on same account row (FOR SHARE versus producer FOR UPDATE),
then reads at READ COMMITTED. Real blocked lower-ID producer and higher-ID commit
on another account prove no missed committed prefix.

Session read locks and membership locks hold through each readonly page transaction.
Transaction-local syncAuthenticate exactly copies existing authoritative auth checks,
ordering and catalogued errors without modifying existing Auth business. A second pool
connection while a transaction is held could starve a bounded pool; eight concurrent
readers with a single-connection pool pass. Session/token expiry, revocation and epoch
changes after blocking user-row waits are rejected before any page/cursor advancement.

Numeric JSON integers include mathematically integral decimals/exponents. Arbitrary
positive limits cap exactly at100; above-signed64 afterSeq authorizes then returns terminal.
A raw64KiB body cap would incorrectly reject valid70001-digit numbers. Automatic
approval rejected an unbounded io.ReadAll alternative due to memory/DoS risk; that
rejected command executed no edits. The accepted safer solution streams number tokens,
keeps first19 significant digits/counts/saturated exponent, preserves original lexical
grammar, zero/sign/integrality, and normalizes only the integer-domain comparison.
Transformed JSON remains bounded64KiB, strings unchanged, external whitespace collapsed
to a separator (never removed in a way that could legalize malformed1 2).
This necessary scanner is justified by the present arbitrary numeric contract and
actual long-number fixtures, not future JSON reuse. It could be simplified only after
a separately approved public numeric-domain change or equivalent bounded primitive.
No unbounded ReadAll, schema/body policy change or new dependency was introduced.

Each page queries limit+1 in one snapshot; Conversation messages start afterSeq+1,
are gap checked, and read has no Message/Outbox/ACK write. Existing private history
adapter/types/body remain unchanged. Infrastructure/corrupt source failure yields
non-2xx plain transport failure, never uncatalogued successful JSON/error code.

## Final local verification

Disposable PostgreSQL16-alpine container im-sync-go-pg-20261003,
localhost55439, canonical migrations/0001_initial.up.sql; NATS2.10-alpine
im-sync-go-nats-20261003 localhost44229. DB_TEST_ENABLE=1, PGHOST/PGPORT/PGUSER/
PGDATABASE present and NATS_URL actual; fixture-only password never product credentials.
No unset-DB integration skips counted as PASS.
Existing plugin-host/root packages have no Go test files, not hidden runtime acceptance.
Existing Human-deferred friend-add-authorization-denied remains DEFERRED, not canonical PASS.

Final product:
- gofmt all authored Go; go build ./...; go vet ./...: PASS.
- go test -count=1 ./... enabled: PASS, Core8.561s/tests19.633s.
- go test -race -count=1 ./... enabled: PASS, Core11.217s/tests79.662s.
- tools/verify_sync_runtime.py final: PASS. Actual Compose TLS proxy/Gateway/Core/
  PostgreSQL, trusted generated public CA and untrusted-CA denial;208 User metadata
  records,205 actual WSS durable-ACK Messages, each over3pages<=100, terminal/replay,
  foreign cursor/auth/query/version/correlation/no-store/read-only. Actual206th WSS
  commit after terminal is observed. Literal70001-digit coefficients and70000-digit
  exponents traverse real HTTPS for bothlimits, normalize1 exactly, hugeafterSeq empty.
  Every owned Compose project container/volume inspected then removed.
- Core PG fixtures separately prove205 events and205 commitMessage messages over3pages,
  terminal/new commit for BOTHstreams, cursor cross-Session replay, fabricated/foreign/
  unknown positions, member isolation, huge inputs, all4kinds, no Session event, auth
  negatives; malformed/canonical UUID error precedence for bothroutes and oldAuth.
- Streaming original grammar controls:001/1./1e+/lone-/garbage/1 2 rejected;
  huge zero/-zero/exponents, integral decimals vsfractional, escaped strings, EOF/
  delimiters, bounded transformed output and rejected oversized nonnumeric buffer.
- Frozen verification: PASS currentcanonical ef90846/PDF provenance unchanged.
- Architecture --scope all: PASS zero violations; tests/architecture53 PASS.
- Existing public HTTP Auth9operations/6positive/21negative/15mutations PASS.
- Existing WSS18cases/44mutations PASS; Sync/Plugin79outcome artifacts/16mutations PASS.
- Sync OpenAPI binding verifier PASS; tests/contract/test_sync_transport4groups PASS.
- Authored whitespace check with core.whitespace=cr-at-eol PASS.
- Clean committed existing tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance will be
  recorded by private final observer after commit, without modifying this candidate.

## Preserved failures and trace limits

Startup baseline architecture failed solely on new activation task missing literal
allowed_paths; corrected within task plus exact dependency LOOP1-CLIENT-SEND-001.
Initial compile failed after replacing sync.go old private adapter; restored original
adapter before runtime checks. Initial TLS harness lookup nestedtokens/auth.bind extra
field failed and was corrected; cleanup passed on both failed deployments.
A fullrace oldSocial wait-control misidentified new Sync SQL in parallel package tests;
new Sync query alias plus exact own polling prevents collision, oldSocial source/test
unchanged and final fullrace PASS. WinError1455 pagefile startup exhaustion during
parallel Compose/Go transient is preserved; final real commands reran successfully.
Automatic denial and safealternative retained. All prior failed commands remain in
sealed Research Recorder. Startup/selected read-only tool gaps and initial paraphrased
visible delegation prompt are disclosed as incomplete prospective_resume trace.
Exact Human prompt is preserved; no Recorder PASS substitutes independent acceptance.

## Next exact action / ownership

Commit clean REVIEW candidate; Coordinator starts fresh independent Review and exact
applicable hosted CI, then protected merge/actual-main audit and verified synchronization
to H:/IM-platform preserving original781unknown entries. Implementation makes no main
writes and does not mark done. If accepted, Coordinator reassesses existing client SYNC
runtime prerequisite and proceeds to Desktop/Mobile SYNC, completes it and stops.

## Tool versions and owned test service handoff

Go1.26.6 windows/amd64; PostgreSQL16.15 x86_64 Alpine; NATS2.10.29.
Two task-owned PG/NATS containers remain running for independent Reviewer reuse at
55439/44229; Coordinator removes these exact owned resources after acceptance.
Ephemeral strictTLS Compose projects were inspected and cleaned by their verifier.

## First clean candidate recovery check

Existing Acceptance PASS at08dc1bf2a6ecd5b2e58f70f1036f7875701e9b27,
review/currentTask unique, zero status/diff. Archive prompt-directory selection was
corrected afterward by copying the two exact primary prompt files and refreshing only
the archive manifest. Final metadata candidate is checked again privately; product
bytes unchanged. This same-context observer is never independent Review.
