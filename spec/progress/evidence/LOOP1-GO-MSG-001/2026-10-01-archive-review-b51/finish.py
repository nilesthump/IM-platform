from review import *
import hashlib
run('authored-diff-check',['git','-c','core.whitespace=cr-at-eol','diff','--check','273afa5','b51e62a','--','spec/progress/current.md','spec/tasks/done/LOOP1-GO-MSG-001.md','spec/progress/checkpoints/2026-10-01-loop1-go-msg-001-recovery-review.md','spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-recovery-review-273afa5/post-recorder-closure.md'])
warning={'reason':'Startup occurred before Recorder; raw PowerShell authority outputs had Unicode decoding/truncation and guessed nonexistent contracts/errors/README.md; relevant authority re-read with bundled Python UTF8. One later non-recorded read of own hosted-list failed GBK decoding and was rerun explicitUTF8. Raw source CRCRLF git diff --check exit2 retained; no immutable normalization; authored prose check separately. No hidden/complete prospective trace claim.'}
run('warning',[PY,REC,'record-event','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--event-type','instrumentation_warning','--data-json',json.dumps(warning)],False)
run('review-finished',[PY,REC,'record-event','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--event-type','review_finished','--data-json',json.dumps({'result':'PASS','reviewed_sha':'b51e62a529ad0f06f31828f49a77734ea2ca010c','range':'273afa5..b51e62a','independent_reviewer':'/root/s1_archive_review_b51','scope':'administrative only','hosted_run':36828991394,'jobs':'5requiredSUCCESS/8correctinactiveSKIPPED','S1_gate':'OPEN'})],False)
run('finish',[PY,REC,'finish-run','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--result','PASS'],False)
run('validate',[PY,REC,'validate-run','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID],False)
s=json.loads((RESEARCH/'runs'/RID/'summary.json').read_text(encoding='utf8'))
report='''# Independent administrative review: b51e62a

Result: PASS, bounded administrative candidate and exact-head hosted CI. S1 Gate remains OPEN; no E2E or S2 implementation accepted by this report.

Reviewer: fresh /root/s1_archive_review_b51, who neither implemented nor fixed candidate. Exact SHA b51e62a529ad0f06f31828f49a77734ea2ca010c, recovery/s1-handoff-20261001; range 273afa5eb492e1550119885484a68c85f27e0171..b51e62a. Clean detached isolated checkout H:/.codex/worktrees/s1-archive-review-b51; initial/final git status empty, verified exact HEAD. Original H:/IM-platform not used as clean Acceptance checkout and never edited by reviewer.

Mandatory recovery resolved unique LOOP1-GO-MSG-001 done/status done, E2E backlog and S1 OPEN. Canonical frozen SHA83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e and historical PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 verified; §3/10 SRC01..07/11, applicable ADRs, domain/invariants/acceptance/contracts, minimality/execution/review read. ADR0001 expired. Human approve now authorizes prior explicit questions; candidate's earlier pending wording truthfully describes historical handoff and is not a new denial.

All154 changed paths are current Task/current/checkpoint/evidence and this Coordinator prompt/run only. No product, frozen, public contracts, migration, deploy or workflow/classifier changed. Existing runtime graph and ownership unchanged; sourceall checks actual Go/Java boundaries. No new product abstraction/dependency/service/config/database object/public symbol; raw nested .gitattributes * -text is minimally justified by demonstrated immutable byte transport. Task histories and checkpoint preserve bounded acceptance rather than claim S1 PASS.

Byte audits PASS:120 archived files byte-identical to H:/.codex/evidence/s1-recovery-review-20261001-b,301 prior review originals conform to manifest,605 original unknown-owned files preserved including prior approved22byte relocation,4739 prior immutable Git objects identical to273. Coordinator25-event run honestly finishedBLOCKED with structural validationPASS; archived Review27-event finishedPASS/validationPASS. Historical FAIL and partial runs untouched. No product live rerun claim; accepted product183 remains unchanged.

Local exact commands (full argv, exit, duration, stdout/stderr and Recorder raw hashes in commands.json):
- pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance: exit0,7.344s, clean task/recovery PASS.
- pwsh -NoProfile -File tools/verify-frozen-architecture.ps1: exit0,5.203s, frozen and34 controls PASS.
- bundled Python -B ci/check_architecture.py --scope all --json: exit0,.485s, applicable source/dependency/governance PASS.
- bundled Python -B contracts/websocket/verify.py: exit0,.156s,8positive/10negative scenarios,18schema/26behavior mutations rejected.
- bundled Python -B -m unittest discover -s tests/architecture -v: exit0,4.938s wrapper,34 tests/no skips.
- Byte audit exit0,.469s; both candidate-related Recorder validations exit0.

Exactpush run36828991394 completed/success, headb51e62a confirmed by direct run API. All13 job APIs independently inspected: classify110261022961, architecture110261190935, source_go110261191076, source_java110261191210, gate110261374140 completed/success;8 remaining jobs completed/skipped correctly inactive. Independent ci/classify.py --base273afa5 --headb51e62a selects only architecture/source_go/source_java; classify/gate unconditional. Hosted direct verification exit0,6.687s; per API command duration stored hosted-direct-summary.json. No missing/failed/cancelled/anomalously skipped required jobs. PR virtual-merge binding N/A: no new candidate PR; historical PR4 binding does not cover candidate. PR4 unmerged; no merge performed.

Known verification limitations: git diff --check exit2 on byte-preserved raw stdout/stderr CRCRLF/trailing whitespace; this was disclosed by Coordinator and sources match byte-for-byte. Authored task/current/checkpoint/postclosure prose separate whitespace check PASS. Startup before Recorder has incomplete trace, Unicode/truncation and guessed missing read disclosed; later own JSON GBK read failure retried UTF8. Never rewrite raw evidence to clean it. Recorder prospective_resume with unavailable hidden metadata, not full prospective coverage. Own final report/manifest generated after Recorder finish and explicitly outside finished trace. Recorder structural PASS is not Task or Stage PASS.

Next exact action: Coordinator archives these evidence bytes, prospectively binds Human-approved E2E paths, activates dependency-satisfied E2E through fresh sole Implementation Agent, then fresh independent Review/fix and exact hosted CI. New S1 PR and merge only after applicable acceptance; retain PR4 unmerged; verify actual main then record S1PASS/S2OPEN and stop. No architecture conflict found. Reviewer created no live services, altered no original files and released writer ownership; clean isolated checkout retained for durable reproducibility.
'''
report+='\nOwn Recorder '+RID+' finishedPASS/validatePASS, '+str(s['event_count'])+' events.\n'
(OUT/'independent-review-report.md').write_text(report,encoding='utf8')
manifest=[dict(path=str(p.relative_to(OUT)).replace('\\','/'),size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json']
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');print('Report and manifest written; final post-Recorder closure explicitly disclosed')
