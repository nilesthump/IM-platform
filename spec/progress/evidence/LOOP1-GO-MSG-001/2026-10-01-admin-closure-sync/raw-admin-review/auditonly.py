exec((__import__('pathlib').Path(__file__).parent/'check.py').read_text().split('cmds=')[0])
# Exact source/authority identity plus all preexisting research/FAIL archive identity.
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','183be639','--','research','spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-independent-review-f1764fd'],cwd=co).decode().splitlines();bad=[]
assert subprocess.run(['git','diff','--quiet','183be639..HEAD','--','research/prompts/P-MSG-IMPLEMENTATION-20261001','research/runs/R-MSG-IMPLEMENTATION-20261001','research/runs/R-MSG-FIX-20261001','spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-independent-review-f1764fd'],cwd=co).returncode==0
archive=co/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-independent-review-183be63'; originals=pathlib.Path('H:/.codex/worktrees/msg-rereview-20261001/evidence');aud=[]
for item in json.loads((archive/'archive-transport.json').read_text()):
 path=item['file'];data=(archive/path).read_bytes();assert hashlib.sha256(data).hexdigest()==item['sha256'];assert data==(originals/path).read_bytes();assert data==subprocess.check_output(['git','show','HEAD:'+str((archive/path).relative_to(co)).replace(chr(92),'/')],cwd=co);aud.append(path)
changed=subprocess.check_output(['git','diff','--name-only','183be639..HEAD'],cwd=co).decode().splitlines();assert all(x.startswith(('research/prompts/','research/runs/','spec/progress/evidence/LOOP1-GO-MSG-001/','spec/tasks/')) or x in ['spec/progress/current.md','spec/progress/checkpoints/2026-10-01-loop1-go-msg-001-accepted.md'] for x in changed)
(ev/'byte-audit.json').write_text(json.dumps(dict(prior_unchanged_files=len(paths),archive_original_working_head_identical_files=len(aud),changed_paths=changed),indent=2))
(ev/'final-command-results.json').write_text(json.dumps(rows,indent=2));print('PASS required hosted jobs, '+str(len(paths))+' prior files unchanged; '+str(len(aud))+' archive files original/working/HEAD identical',flush=True)
