from pathlib import Path
import subprocess,json,time,sys
ROOT=Path('H:/.codex/worktrees/s1-archive-review-b51');OUT=Path('H:/.codex/evidence/s1-archive-review-b51');PY=sys.executable;REC=ROOT/'tools/research/recorder.py';RESEARCH=OUT/'research';RID='R-S1-ARCHIVE-REVIEW-B51';PID='P-S1-ARCHIVE-REVIEW-B51'
def run(name,args,record=True):
 args=list(map(str,args)); command=[PY,str(REC),'run-command','--repo',str(ROOT),'--research-root',str(RESEARCH),'--run-id',RID,'--']+args if record else args
 t=time.monotonic();p=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (OUT/(name+'.stdout.txt')).write_bytes(p.stdout);(OUT/(name+'.stderr.txt')).write_bytes(p.stderr)
 ledger=json.loads((OUT/'commands.json').read_text()) if (OUT/'commands.json').exists() else []
 ledger.append(dict(name=name,argv=command,cwd=str(ROOT),exit=p.returncode,elapsed=time.monotonic()-t));(OUT/'commands.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8');print(name,p.returncode,round(ledger[-1]['elapsed'],3),p.stdout.decode('utf8',errors='replace')[-500:]);return p
if __name__=='__main__':
 prompt='Fresh independent administrative Review /root/s1_archive_review_b51 of exact b51e62a529ad0f06f31828f49a77734ea2ca010c, range 273afa5eb492e1550119885484a68c85f27e0171..b51e62a. No implementation or fixing by reviewer. Audit clean isolated checkout, administrative-only paths, preserved120 external review sources/301 earlier archive/605 unknown files and immutable history; own Recorder25 BLOCKED truthful at prior time. Local Acceptance/frozen/sourceall/WSS plus exact-head direct hosted jobs required. User now approve covers E2E three CI paths and b51 push; historical pending text is not fresh denial. No original/product/task edits, no push/merge; external evidence only. Startup before Recorder incomplete and Unicode/truncated reads re-read; prospective_resume, unavailable facts unavailable.'
 (OUT/'prompt.txt').write_text(prompt,encoding='utf8')
 run('clean-initial',['git','status','--porcelain=v1','--untracked-files=all'],False)
 run('head',['git','rev-parse','HEAD'],False)
 run('register',[PY,REC,'register-prompt','--repo',ROOT,'--research-root',RESEARCH,'--task-id','LOOP1-GO-MSG-001','--file',OUT/'prompt.txt','--source','delegated_visible','--prompt-id',PID],False)
 run('start',[PY,REC,'start-run','--repo',ROOT,'--research-root',RESEARCH,'--task-id','LOOP1-GO-MSG-001','--role','review','--capture-mode','prospective_resume','--pre-recorder-work','--prompt-id',PID,'--run-id',RID,'--experiment-group','full_governance','--fresh-context','true'],False)
 run('wss',[PY,'-B','contracts/websocket/verify.py'])
 run('acceptance',['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance'])
 run('frozen',['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'])
 run('sourceall',[PY,'-B','ci/check_architecture.py','--scope','all','--json'])
