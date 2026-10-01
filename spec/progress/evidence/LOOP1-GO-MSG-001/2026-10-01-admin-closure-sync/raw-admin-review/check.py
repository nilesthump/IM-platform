import subprocess,time,json,sys,pathlib,hashlib
co=pathlib.Path('H:/.codex/worktrees/msg-closure-review-20261001/IM-platform');ev=co.parent/'evidence';root=ev/'research';rows=[]
cmds=[['git','status','--porcelain'],['git','rev-parse','HEAD'],['git','diff','--name-status','183be639..HEAD'],['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance'],['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'],[sys.executable,'-B','ci/check_architecture.py','--scope','all','--json']]
for name in ['R-MSG-IMPLEMENTATION-20261001','R-MSG-INDEPENDENT-REVIEW-20261001','R-MSG-FIX-20261001','R-MSG-REREVIEW-20261001','R-MSG-COORDINATOR-20261001']:
 cmds.append([sys.executable,'tools/research/recorder.py','validate-run','--run-id',name])
for rid in ['36820491515','36820486384']:
 cmds.append(['gh','run','view',rid,'--repo','nilesthump/IM-platform','--json','headSha,status,conclusion,jobs,event,url'])
for i,cmd in enumerate(cmds):
 start=time.monotonic();p=subprocess.run([sys.executable,'tools/research/recorder.py','run-command','--research-root',str(root),'--run-id','R-MSG-CLOSURE-REVIEW-20261001','--',*cmd],cwd=co,capture_output=True,text=True,encoding='utf8');elapsed=time.monotonic()-start
 (ev/f'check-{i}-stdout.txt').write_text(p.stdout,encoding='utf8');(ev/f'check-{i}-stderr.txt').write_text(p.stderr,encoding='utf8');rows.append(dict(command=cmd,exit_code=p.returncode,elapsed_seconds=elapsed,stdout=f'check-{i}-stdout.txt',stderr=f'check-{i}-stderr.txt'));print(i,p.returncode,round(elapsed,3),p.stdout[-400:],p.stderr[-150:],flush=True)
(ev/'command-results.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
