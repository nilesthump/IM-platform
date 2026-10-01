import json,subprocess,sys,time
from pathlib import Path
r=Path('H:/.codex/worktrees/s1-e2e-review-6346');e=Path('H:/.codex/evidence/s1-e2e-review-6346');owner='R-E2E-REVIEW-6346';rec=r/'tools/research/recorder.py';common=['--repo',str(r),'--research-root',str(e/'research'),'--run-id',owner];ledger=[]
def run(args):
 t=time.monotonic();p=subprocess.run([sys.executable,'-B',str(rec),'run-command']+common+['--']+args,cwd=r,capture_output=True);n=len(ledger)+1
 (e/f'cleanup-{n}-stdout.txt').write_bytes(p.stdout);(e/f'cleanup-{n}-stderr.txt').write_bytes(p.stderr)
 ledger.append({'argv':args,'exit_code':p.returncode,'elapsed_seconds':round(time.monotonic()-t,3)});(e/'cleanup-commands.json').write_text(json.dumps(ledger,indent=2))
 assert p.returncode==0,args
 return p.stdout
p=subprocess.run([sys.executable,'-B',str(rec),'record-event']+common+['--event-type','instrumentation_warning','--data-json',json.dumps({'decision':'Independent reviewer external launcher failed only at conservative cleanup short-container-ID versus full-ID equality. All product checks exited0; retain original failure. Resolve each actual binding via docker inspect full Id before bounded cleanup. No product/evidence modification.'})],cwd=r,capture_output=True);assert p.returncode==0
volumes=[]
for name in ['loop1-e2e-review-pg-6346','loop1-e2e-review-nats-6346']:
 obj=json.loads(run(['docker','inspect',name]))[0];assert obj['Config']['Labels'].get('im.owner')==owner
 for mount in obj.get('Mounts',[]):
  if mount['Type']=='volume':
   v=mount['Name'];run(['docker','volume','inspect',v]);ids=run(['docker','ps','-aq','--filter','volume='+v]).decode().split()
   actual=[json.loads(run(['docker','inspect',cid]))[0]['Id'] for cid in ids]
   assert actual==[obj['Id']],actual;volumes.append(v)
 run(['docker','rm','-f',name])
for v in volumes:run(['docker','volume','rm',v])
assert not run(['docker','ps','-aq','--filter','label=im.owner='+owner]).strip()
assert not run(['git','-c','core.excludesFile=.git/info/exclude','status','--porcelain=v1','--untracked-files=all']).strip()
print('Cleanup PASS: exactowner/fullID/unique-volume-binding checked; own containers/volume absent; exact candidate clean.')
