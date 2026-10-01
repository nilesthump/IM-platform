from pathlib import Path
import subprocess,json,time,hashlib,sys
ROOT=Path('H:/.codex/worktrees/s1-recovery-review-20261001-b')
OUT=Path('H:/.codex/evidence/s1-recovery-review-20261001-b')
PY=sys.executable
REC=ROOT/'tools/research/recorder.py'
RESEARCH=OUT/'research'
RID='R-S1-RECOVERY-REVIEW-20261001-B'
PID='P-S1-RECOVERY-REVIEW-20261001-B'
ledger=[]
def run(name,args,cwd=ROOT):
 t=time.monotonic(); p=subprocess.run([str(x) for x in args],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (OUT/(name+'.stdout.txt')).write_bytes(p.stdout); (OUT/(name+'.stderr.txt')).write_bytes(p.stderr)
 row=dict(name=name,argv=[str(x) for x in args],cwd=str(cwd),exit=p.returncode,elapsed=time.monotonic()-t)
 ledger.append(row); (OUT/'commands.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8');print(name,p.returncode,row['elapsed'],p.stdout.decode('utf-8',errors='replace')[-1000:]);return p
prompt='Fresh independent administrative recovery Review delegated by /root. Exact SHA 273afa5eb492e1550119885484a68c85f27e0171; range 33b1522c7f315b7aeb25fc31c05756c2bc950a9c..273afa5. I neither implemented nor fixed candidate. Audit clean detached state, administrative scope, preserved original605 files and301 review originals, queue/current/checkpoint and immutable Recorder/archive bytes. Local independent Acceptance and exact-head actual selected hosted jobs required. No product changes, original checkout edits, push or PR merge. Startup reads occurred before Recorder; prospective_resume incomplete preparation trace. This file contains public delegated task scope; hidden prompts unavailable.'
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
run('clean-initial',['git','status','--porcelain=v1','--untracked-files=all'])
run('head',['git','rev-parse','HEAD'])
run('prompt',[PY,REC,'register-prompt','--repo',ROOT,'--research-root',RESEARCH,'--task-id','LOOP1-GO-MSG-001','--file',OUT/'prompt.txt','--source','delegated_visible','--prompt-id',PID])
run('start',[PY,REC,'start-run','--repo',ROOT,'--research-root',RESEARCH,'--task-id','LOOP1-GO-MSG-001','--role','review','--capture-mode','prospective_resume','--pre-recorder-work','--prompt-id',PID,'--run-id',RID,'--experiment-group','full_governance','--fresh-context','true'])
