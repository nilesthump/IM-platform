from review import *
run('byte-audit',[PY,'-B',OUT/'audit.py'])
run('coordinator-recorder',[PY,'-B',REC,'validate-run','--repo',ROOT,'--run-id','R-S1-RESUME-20261001-B'])
run('archived-review-recorder',[PY,'-B',REC,'validate-run','--repo',ROOT,'--research-root',ROOT/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-recovery-review-273afa5/research','--run-id','R-S1-RECOVERY-REVIEW-20261001-B'])
run('diff-check',['git','-c','core.whitespace=cr-at-eol','diff','--check','273afa5','b51e62a'])
run('hosted-list',['gh','api','repos/nilesthump/IM-platform/actions/runs?head_sha=b51e62a529ad0f06f31828f49a77734ea2ca010c&per_page=20'])
