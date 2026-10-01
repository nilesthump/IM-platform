from review import *
run('classification',[PY,'-B','ci/classify.py','--base','273afa5eb492e1550119885484a68c85f27e0171','--head','b51e62a529ad0f06f31828f49a77734ea2ca010c'])
run('architecture-tests',[PY,'-B','-m','unittest','discover','-s','tests/architecture','-v'])
run('job-snapshot',['gh','api','repos/nilesthump/IM-platform/actions/runs/36828991394/jobs?per_page=100'])
run('diff-governance',['git','diff','--ignore-space-at-eol','273afa5','b51e62a','--','spec/progress/current.md','spec/tasks/done/LOOP1-GO-MSG-001.md','spec/progress/checkpoints/2026-10-01-loop1-go-msg-001-recovery-review.md'])
