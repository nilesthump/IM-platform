import pathlib, subprocess, hashlib, json, time, sys, shutil, os
ROOT=pathlib.Path('H:/.codex/worktrees/social-merge-continue/IM-platform')
ORIGINAL=pathlib.Path('H:/IM-platform')
EV=ROOT/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync'
PY=sys.executable
REC=ROOT/'tools/research/recorder.py'
RUN='R-MSG-SYNC-HANDOFF-20261001'
EV.mkdir(parents=True,exist_ok=True)
(EV/'.gitattributes').write_bytes(b'* -text\n')
def command(argv,cwd=ROOT,label=None,check=True):
    start=time.monotonic(); p=subprocess.run([str(x) for x in argv],cwd=cwd,capture_output=True)
    name=label or 'command-'+str(time.time_ns())
    (EV/(name+'-stdout.txt')).write_bytes(p.stdout); (EV/(name+'-stderr.txt')).write_bytes(p.stderr)
    data={'argv':[str(x) for x in argv],'cwd':str(cwd),'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}
    with (EV/'command-results.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(data,ensure_ascii=False)+'\n')
    if check and p.returncode:raise RuntimeError(name+': '+p.stderr.decode('utf-8','replace'))
    return p.stdout

def inventory():
    status=command(['git','status','--porcelain=v1','-uall'],ORIGINAL,'original-initial-status').decode('utf-8')
    head=command(['git','rev-parse','HEAD'],ORIGINAL,'original-initial-head').decode().strip()
    branch=command(['git','branch','--show-current'],ORIGINAL,'original-initial-branch').decode().strip()
    names=command(['git','ls-files','--others','--exclude-standard','-z'],ORIGINAL,'original-untracked-names').decode('utf-8').split('\0')
    rows=[]
    for n in filter(None,names):
        p=ORIGINAL/n
        rows.append({'path':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'ownership':'unknown or other agent; preserved; no inference'})
    tracked=command(['git','ls-tree','-r','--name-only','HEAD'],ROOT,'source-tree').decode().splitlines()
    collisions=[r['path'] for r in rows if r['path'] in tracked]
    data={'branch':branch,'head':head,'status':status,'tracked_changes':[s for s in status.splitlines() if not s.startswith('?? ')],'untracked':rows,'collision_with_33b1522':collisions,'source_head':command(['git','rev-parse','HEAD'],ROOT,'source-initial-head').decode().strip()}
    (EV/'original-inventory.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    assert not data['tracked_changes'], 'unknown tracked changes require reconciliation'
    prior=EV/'coordinator-inherited-notes';prior.mkdir(exist_ok=True)
    for n in ['spec/progress/current.md','spec/tasks/done/LOOP1-GO-MSG-001.md']:
        shutil.copyfile(ROOT/n,prior/pathlib.Path(n).name)
    command(['git','diff','--binary','--','spec/progress/current.md','spec/tasks/done/LOOP1-GO-MSG-001.md'],ROOT,'inherited-notes-diff')
    print(json.dumps({'original_branch':branch,'original_head':head,'untracked_files':len(rows),'collisions':collisions},ensure_ascii=False))

def archive():
    sources=[(pathlib.Path('H:/.codex/worktrees/msg-closure-review-20261001/evidence'),EV/'raw-admin-review')]
    supplement=pathlib.Path('H:/.codex/worktrees/msg-admin-confirmation-20261001/evidence')
    if supplement.exists():sources.append((supplement,EV/'fresh-ci-confirmation'))
    rows=[]
    for src,dst in sources:
        assert src.is_dir()
        for p in sorted(src.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(src);target=dst/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            data=p.read_bytes()
            if target.exists():assert target.read_bytes()==data, 'refuse immutable archive overwrite: '+str(target)
            else:target.write_bytes(data)
            assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(data).digest()
            rows.append({'source':str(p),'archive':target.relative_to(ROOT).as_posix(),'size':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    (EV/'archive-byte-manifest.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for dst in [EV/'raw-admin-review',EV/'fresh-ci-confirmation']:
        if not dst.exists():continue
        research=dst/'research'
        if research.exists():
            for run in (research/'runs').glob('R-*'):
                command([PY,'-B',REC,'validate-run','--repo',ROOT,'--research-root',research,'--run-id',run.name],label='validate-'+run.name)
    print('byte-preserved archive files:',len(rows))

if __name__=='__main__':
    {'inventory':inventory,'archive':archive}[sys.argv[1]]()