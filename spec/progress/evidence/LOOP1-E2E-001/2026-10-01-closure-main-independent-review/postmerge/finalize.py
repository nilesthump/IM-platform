from pathlib import Path
import json,hashlib
r=Path('H:/.codex/evidence/s1-closure-review/postmerge');s=json.loads(sorted(r.glob('summary-*.json'))[-1].read_text());assert s['result']=='PASS'
report='''# Independent actual-main verification

Product and exact hosted acceptance: PASS for dd24a9c65a36dd775ca68ae7847c2c283b6f348f. External PR4 status constraint: FAIL/deviation, disclosed separately; no assertion that all user constraints passed.

Independent /root/s1_closure_review neither implemented/fixed candidate nor merged any PR. New linked Recorder R-S1-MAIN-REVIEW-20261001 / P-S1-MAIN-REVIEW-20261001, separate postmerge directory. Previous review/run/manifest untouched. Clean exact detached H:/.codex/worktrees/s1-main-review; zero diff/status, Recovery Acceptance unique E2E done PASS, canonical/PDF hashes match, actual sourceall PASS. Tree identical accepted cb2cf431; no product/services retest necessary for identical tree; no services started.

Direct API verifies PR5 mergedAt2026-10-01T08:08:59Z, merge/main dd24a9c65a36dd775ca68ae7847c2c283b6f348f. Parents exactly[b442acd26777c481620a6bd917863cebfaf79b35,cb2cf431a59e0318a1163073a1c76432135c86d9]; tree7d54c2dc83f964dd159a608fbf2d6ec34d414043 matches independent accepted S1 candidate. Main push36834539666 exactdd24 direct13completedSUCCESS: classify,architecture,source_go,source_java,go,java,web,desktop,mobile,shared,compatibility,deploy,gate. No aggregate inference, old CI reuse, missing-job or running-job acceptance. Two pending snapshots retained then final actual13success.

PR4 is now closed/merged=true, merged_at2026-10-01T08:09:01Z, merge_commit_sha33b1522c7f315b7aeb25fc31c05756c2bc950a9c. Initial expectedOPEN/unmerged assertion failed and remains rawFAIL. Coordinator independently confirmed state and disclosed to human. Coordinator reports only PR5 --match-head cb2 merge, never a PR4 merge command or auto_merge enablement; GitHub indirect merge detection is consistent with PR4 head being an ancestor included by PR5. Official explanation supplied by Coordinator: https://github.blog/changelog/2023-09-26-more-details-provided-when-a-pull-request-is-merged-indirectly-or-is-still-processing-updates/ . This review directly establishes API state/tree ancestry, not access to every hidden GitHub operation. No reopen, undo, force or history rewrite. Earlier bounded PR4OPEN observations remain historical before PR5 merge, never retroactively edited.

Recorder finished FAIL19 events to retain the overall PR4 constraint deviation, structurally validate PASS. Public review_finished event records narrower actualmain product/CI PASS plus explicit deviation; Research result never determines product Stage acceptance. First oversized RESTcommit raw output and PR4assertion failure retained. Commands/raw/timestamps/elapsed in immutable Recorder; report/manifest generated afterward outside trace. No S2OPEN candidate or later revision accepted. Reviewer released with final clean candidate and no services.
''';(r/'independent-main-review.md').write_text(report,encoding='utf-8');files=[]
for p in sorted(r.rglob('*')):
 if p.is_file() and p.name!='final-manifest.json':
  b=p.read_bytes();files.append({'path':p.relative_to(r).as_posix(),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()})
f=r/'final-manifest.json';f.write_text(json.dumps({'candidate':s['sha'],'product_hosted_acceptance':'PASS','pr4_constraint':'FAIL_EXTERNAL_STATUS_DEVIATION','recorder_result':'FAIL','files':files,'post_finish_boundary':'report and immutable transport manifest only'},indent=2));print(len(files),hashlib.sha256(f.read_bytes()).hexdigest())
