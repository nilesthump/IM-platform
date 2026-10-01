exec((__import__('pathlib').Path(__file__).parent/'check.py').read_text().split('cmds=')[0])
def run(cmd,label):
 start=time.monotonic();p=subprocess.run([sys.executable,'tools/research/recorder.py','run-command','--research-root',str(root),'--run-id','R-MSG-CLOSURE-REVIEW-20261001','--',*cmd],cwd=co,capture_output=True,text=True,encoding='utf8');(ev/(label+'.txt')).write_text(p.stdout,encoding='utf8');(ev/(label+'-stderr.txt')).write_text(p.stderr,encoding='utf8');rows.append(dict(command=cmd,exit_code=p.returncode,elapsed_seconds=time.monotonic()-start,stdout=label+'.txt'));return p.stdout
for rid in ['36820491515','36820486384']:
 d=json.loads(run(['gh','run','view',rid,'--repo','nilesthump/IM-platform','--json','headSha,status,conclusion,jobs,event,url'],'hosted-'+rid));assert d['headSha']=='33b1522c7f315b7aeb25fc31c05756c2bc950a9c' and d['conclusion']=='success'
 required=['classify','source_go','source_java','architecture','gate']+(['go'] if d['event']=='pull_request' else [])
 for name in required:
  j=next(x for x in d['jobs'] if x['name']==name)
  fresh=json.loads(run(['gh','api','repos/nilesthump/IM-platform/actions/jobs/'+str(j['databaseId'])+'?administrative_review=20261001'],'job-'+str(j['databaseId'])))
  assert fresh['conclusion']=='success' or (name=='classify' and rid=='36820491515');run(['gh','run','view',rid,'--repo','nilesthump/IM-platform','--job',str(j['databaseId']),'--log'],'hosted-'+rid+'-'+name)
run(['git','status','--porcelain'],'final-clean')
# Exact source/authority identity plus all preexisting research/FAIL archive identity.
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','183be639','--','research','spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-independent-review-f1764fd'],cwd=co).decode().splitlines();bad=[]
for path in paths:
 old=subprocess.check_output(['git','show','183be639:'+path],cwd=co);now=subprocess.check_output(['git','show','HEAD:'+path],cwd=co)
 if old!=now:bad.append(path)
assert not bad
archive=co/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-independent-review-183be63'; originals=pathlib.Path('H:/.codex/worktrees/msg-rereview-20261001/evidence');aud=[]
for item in json.loads((archive/'archive-transport.json').read_text()):
 path=item['file'];data=(archive/path).read_bytes();assert hashlib.sha256(data).hexdigest()==item['sha256'];assert data==(originals/path).read_bytes();assert data==subprocess.check_output(['git','show','HEAD:'+str((archive/path).relative_to(co)).replace(chr(92),'/')],cwd=co);aud.append(path)
changed=subprocess.check_output(['git','diff','--name-only','183be639..HEAD'],cwd=co).decode().splitlines();assert all(x.startswith(('research/prompts/','research/runs/','spec/progress/evidence/LOOP1-GO-MSG-001/','spec/tasks/')) or x in ['spec/progress/current.md','spec/progress/checkpoints/2026-10-01-loop1-go-msg-001-accepted.md'] for x in changed)
(ev/'byte-audit.json').write_text(json.dumps(dict(prior_unchanged_files=len(paths),archive_original_working_head_identical_files=len(aud),changed_paths=changed),indent=2))
(ev/'final-command-results.json').write_text(json.dumps(rows,indent=2));print('PASS required hosted jobs, '+str(len(paths))+' prior files unchanged; '+str(len(aud))+' archive files original/working/HEAD identical',flush=True)
