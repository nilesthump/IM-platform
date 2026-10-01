exec(open('H:/.codex/evidence/s1-recovery-review-20261001-b/review.py',encoding='utf-8-sig').read().split('prompt=')[0])
ledger=json.loads((OUT/'commands.json').read_text());
run('byte-audit',[PY,REC,'run-command','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--',PY,OUT/'audit.py'])
run('sync-recorder',[PY,REC,'run-command','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--',PY,REC,'validate-run','--repo',ROOT,'--run-id','R-MSG-SYNC-HANDOFF-20261001'])
run('old-fail-recorder',[PY,REC,'run-command','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--',PY,REC,'validate-run','--repo',ROOT,'--research-root',ROOT/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync/raw-admin-review/research','--run-id','R-MSG-CLOSURE-REVIEW-20261001'])
run('gh-run-current',[PY,REC,'run-command','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--','gh','api','repos/nilesthump/IM-platform/actions/runs/36826506799'])
run('gh-jobs-current',[PY,REC,'run-command','--repo',ROOT,'--research-root',RESEARCH,'--run-id',RID,'--','gh','api','repos/nilesthump/IM-platform/actions/runs/36826506799/jobs?per_page=100'])
