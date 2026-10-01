import hashlib,json,subprocess,sys,time
from pathlib import Path
r=Path('H:/.codex/worktrees/s1-e2e-review-6346');e=Path('H:/.codex/evidence/s1-e2e-review-6346');original=Path('H:/IM-platform');rec=r/'tools/research/recorder.py';common=['--repo',str(r),'--research-root',str(e/'research'),'--run-id','R-E2E-REVIEW-6346']
# Independent preserve-only audit; no untracked content is printed.
a=original/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync'
inv=json.loads((a/'original-inventory.json').read_text(encoding='utf8'));rel=json.loads((a/'original-relocation.json').read_text(encoding='utf8-sig'))
files=inv['untracked'];assert len(files)==605,len(files)
failed=[]
for obj in files:
 path=original/obj['path']
 if str(path).replace('\\','/').lower()==rel['source'].replace('\\','/').lower():path=Path(rel['destination'])
 if not path.is_file() or path.stat().st_size!=obj['size'] or hashlib.sha256(path.read_bytes()).hexdigest()!=obj['sha256'].lower():failed.append(obj['path'])
assert not failed,failed
(e/'original605-byte-audit.json').write_text(json.dumps({'result':'PASS','original_files':605,'relocation_only':rel['destination'],'failed':failed,'method':'independent actual H:/IM-platform file bytes/size/hash against committed original inventory, no writes or ownership inference'},indent=2),encoding='utf8')
# Bind direct final observations, all required jobs; classification is checked independently.
jobnames={'classify','architecture','source_go','source_java','go','java','web','desktop','mobile','shared','compatibility','deploy','gate'}
bindings=[]
for label,rid in [('push',36831979992),('pr',36832052224)]:
 p=sorted(e.glob(label+'-run-*.json'))[-1];v=json.loads(p.read_text());jfile=sorted(e.glob(label+'-jobs-*.json'))[-1];jobs=json.loads(jfile.read_text())['jobs']
 assert v['head_sha']=='6346f39fc6786bba3cddbde7acc91bbad42446a1' and v['conclusion']=='success' and v['status']=='completed'
 assert {j['name'] for j in jobs}==jobnames and all(j['conclusion']=='success' and j['status']=='completed' for j in jobs)
 bindings.append({'run_id':rid,'event':v['event'],'sha':v['head_sha'],'required_jobs':{j['name']:j['conclusion'] for j in jobs},'run_evidence':p.name,'jobs_evidence':jfile.name})
sys.path.insert(0,str(r/'ci'));import classify
paths=classify.diff_paths('b442acd26777c481620a6bd917863cebfaf79b35','6346f39fc6786bba3cddbde7acc91bbad42446a1');matrix=classify.classify(paths);assert all(matrix.values())
assert {k for k,v in classify.classify(['tests/e2e/deleted.py']).items() if v}=={'go','deploy','architecture','source_go'}
(e/'final-ci-acceptance.json').write_text(json.dumps({'result':'PASS','runs':bindings,'full_pr_matrix':matrix,'selection_reason':'approved CI file changes select every current job; old_client/plugin/migration obligations run in compatibility, not phantom standalone jobs','virtual_merge_binding':json.loads(sorted(e.glob('hosted-binding-*.json'))[-1].read_text())},indent=2),encoding='utf8')
def recorder(cmd,extra):
 p=subprocess.run([sys.executable,'-B',str(rec),cmd]+common+extra,cwd=r,capture_output=True)
 (e/(cmd+'-stdout.txt')).write_bytes(p.stdout);(e/(cmd+'-stderr.txt')).write_bytes(p.stderr);assert p.returncode==0,(cmd,p.stderr.decode(errors='replace'))
 return json.loads(p.stdout) if cmd in ('finish-run','validate-run') else None
recorder('record-event',['--event-type','review_finished','--data-json',json.dumps({'result':'PASS','candidate':'6346f39fc6786bba3cddbde7acc91bbad42446a1','independent_context':'/root/s1_e2e_review neither implemented nor fixed product','full_range':'b442acd26777c481620a6bd917863cebfaf79b35..6346f39fc6786bba3cddbde7acc91bbad42446a1','actualCI':[36831979992,36832052224],'required_conclusions':'13 success each; Linux29 zero symlink skips; strictTLS real E2E logs','original605':'independent hashes PASS','boundaries':'candidate acceptance only; no new administrative state, main merge, S1 closure or S2 work accepted'})])
summary=recorder('finish-run',['--result','PASS']);validation=recorder('validate-run',[])
# The following report/transport manifest are generated after Recorder finish and are explicitly outside its closed trace.
ledger=json.loads((e/'commands.json').read_text());cleanup=json.loads((e/'cleanup-commands.json').read_text());history=json.loads((e/'byte-preservation.json').read_text())
report='''# Independent S1 E2E candidate review

Result: PASS for exact `6346f39fc6786bba3cddbde7acc91bbad42446a1`, branch `task/LOOP1-E2E-001`. Full review range actual main `b442acd26777c481620a6bd917863cebfaf79b35..6346f39fc6786bba3cddbde7acc91bbad42446a1`.

Independent actor `/root/s1_e2e_review` neither implemented nor fixed candidate product. Reviewed clean detached committed checkout `H:/.codex/worktrees/s1-e2e-review-6346`; own evidence outside checkout. Initial and final actual status empty; Acceptance recovered unique E2E review task with zero diff. Recorder initial snapshot used original checkout while creation was recorded; clean acceptance is the isolated exact candidate, never the dirty original.

No actionable correctness, scope, architecture, security or minimality findings. Actual inherited MSG reviewed, not merely old PASS: Core owns authorization/session-write/transaction/seq/message/singleOutbox; Session and membership locks last through COMMIT; ACK follows actual COMMIT. Gateway forwards bound bearer/canonical frame and local NATS user fanout, no membership/persistence business. Rejected conflict preserves prior origin; private history requires present nonnegative integer afterSeq. Main assembly only selects roles and connects modules. No service internal cross-import or shared Auth business. Contract/schema/frozen hashes unchanged.

E2E adds only standard-library test harness+README, two-line existing deploy step, exact E2E classification and positive/deleted tests; no new job/dependency/service/framework. Fixture Oracle normalizes runtime UUIDs/timestamps while retaining exact keys/scalars and stable identities. SQL uses validated generated UUID identity in owned disposable DB. TLS CERT_REQUIRED/check_hostname remains enabled for HTTPS/WSS. Only public Caddy CA copied. UntrustedCA uses actual client certificate error; wrong hostname accepts only client SSLCertVerificationError codes62/64. Temporary owned Caddy fallback_sni localhost serves existing cert only during negative handshake; finally exact originalJSON restored/asserted before business. Current failure evidence and official option semantics justify this smallest test setup: https://caddyserver.com/docs/caddyfile/options#fallback-sni . No production proxy edit or relaxed positive trust.

Actual deferred constraint trigger fails COMMIT through TLS/WSS and must yield canonical MESSAGE_COMMIT_FAILED, no message/outbox/sequence advance or delivery; scoped by exact generated request+conversation and removed in finally. Independent SQL confirms hello identity/singleMessage/singleOutbox/seq before success observation; existing blockedCOMMIT test independently proves ACK timing. Receiving socket after ACK read adds no cross-socket ordering promise. Stable retry/conflict/nonmember/replacement/logout/staletoken executed; only named friend403 remains DEFERRED_BY_HUMAN, not PASS.

Local verification (exact argv, exits and elapsed seconds in commands.json; raw bytes and Recorder blobs retained):
'''
for item in ledger[:20]:
 if item['argv'][0] in ('docker',):continue
 report+='- `'+ ' '.join(item['argv'])+'`: exit '+str(item['exit_code'])+', '+str(item['elapsed_seconds'])+'s.\n'
report+='''
Go normal/race use DB_TEST_ENABLE=1, actual isolated PostgreSQL16 at127.0.0.1:55661 DBs1_e2e_review and NATS2.10 at127.0.0.1:42661, unchanged canonical0001 migrated via owned PostgreSQL client. Both zero runtime SKIP. Actual ACK-blockedCOMMIT/rollback/identity/dup/outorder/Sync/GROUP500/Auth/Social/Session/revocationfallback and delayedorigin tests executed. Local architecture34 and CI29 pass; exactly4 Windows symlink subcase skips reported and independently covered by both hosted Linux29 (no skips), never hidden as integration PASS. gofmt stdout empty.

Cleanup: strictTLS harness owned Compose cleanup PASS. Reviewer regression cleanup first conservatively aborted because docker ps returns shortIDs while inspect returns fullIDs; preserve original review.py failure and commands21-23. New cleanup.py resolves all real fullIDs, confirms exact owner label and exclusive volume binding, removes only those two containers/anonymous volume, then asserts absent services and clean candidate. No product candidate fix. Initial register-prompt --run-id before run creation produced exit2 after prompt persisted; subsequent start succeeded, current prompt/run linkage valid. Both instrumentation/setup failures are public warning events, not erased.

Hosted independent direct API acceptance: push36831979992 and PR36832052224 exact6346 each all13 required jobs completedSUCCESS: classify, architecture, source_go, source_java, go, java, web, desktop, mobile, shared, compatibility, deploy, gate. CI path modifications correctly select all current obligations; old_client/plugin/migration are represented by compatibility, no nonexistent standalone-job claim. Direct job JSON and full logs retained; LinuxCI29 with zero symlinkSKIP and actual strictTLS fixture/revocation/cleanup PASS. Not inferred from gate/overall status.

PR5 https://github.com/nilesthump/IM-platform/pull/5 head6346/baseb442. Virtual merge2dbe328b310e0b3328681d8cb629bd5c6fd40147 parents exactly[b442acd26777c481620a6bd917863cebfaf79b35,6346f39fc6786bba3cddbde7acc91bbad42446a1], tree87ca7df8c0a9284f64af00ce06f5289bcea91662 equals exact candidate tree. New PR only; PR4 not merged. This review does not accept later administrative state commits or actual main merge; those require applicable independent acceptance. No task queue mutation, S1 closure, S2 implementation, push or merge by Reviewer.

Preservation: all4988 existing research/evidence blobs atactivation match candidate by Git blobOID; frozenMarkdown SHA83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e and historicalPDF SHA546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 match authority. Independent original H:/IM-platform605 file sizes/SHA256 PASS against historical inventory using only human-approved one-file relocation, no writes or ownership inference. Existing301 archive and historicalFAIL/partial remain within unchanged history; current4 failed E2E/rawCRCRLF preserved in candidate.

Recorder R-E2E-REVIEW-6346 / P-E2E-REVIEW-6346 external research root, prospective_resume, pre_recorder_work=true/pre_recorder_trace_complete=false: earlier read-only preparation/formal startup incomplete, never full prospective. FinishedPASS/validated structurally; Research PASS distinct from this exact Task candidate acceptance and Stage Gate. This report and final transport manifest are generated after finish, outside immutable Recorder trace. External artifacts only; Coordinator may archive exact bytes, later administrative commits need fresh review/exactCI.
'''
(e/'independent-review.md').write_text(report,encoding='utf8',newline='\n')
(e/'recorder-validation.json').write_text(json.dumps({'finish':summary,'validation':validation,'post_finish_boundary':'report/manifest generation only outside finished trace; product untouched'},indent=2),encoding='utf8')
manifest=[]
for p in sorted(e.rglob('*')):
 if p.is_file() and p.name!='final-manifest.json':manifest.append({'path':p.relative_to(e).as_posix(),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(e/'final-manifest.json').write_text(json.dumps({'candidate':'6346f39fc6786bba3cddbde7acc91bbad42446a1','result':'PASS','artifact_count':len(manifest),'post_finish_boundary':'immutable report/manifest transport closure outside finished Recorder trace','files':manifest},indent=2),encoding='utf8')
print('PASS exact6346 independent review / direct requiredCI13x2 /605original /4988historical. Recorder finished/validated.')
print('Manifest SHA256',hashlib.sha256((e/'final-manifest.json').read_bytes()).hexdigest(),'files',len(manifest))
