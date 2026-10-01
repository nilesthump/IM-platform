import importlib.util, pathlib, json, hashlib, sys
p=pathlib.Path(__file__).with_name('im-platform-s1-sync-coordinator.py')
s=importlib.util.spec_from_file_location('helper',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
prior=json.loads((m.EV/'original-inventory.json').read_text(encoding='utf-8'))
reloc=json.loads((m.EV/'original-relocation.json').read_text(encoding='utf-8'))
for row in prior['untracked']:
    dest=pathlib.Path(reloc['destination']) if row['path']=='spec/progress/evidence/LOOP1-CI-001/review2-negative-probe.py' else m.ORIGINAL/row['path']
    assert dest.is_file(),str(dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest().lower()==row['sha256'].lower(),str(dest)
status=m.command(['git','status','--porcelain=v1','-uall'],m.ORIGINAL,'original-postsync-status').decode()
head=m.command(['git','rev-parse','HEAD'],m.ORIGINAL,'original-postsync-head').decode().strip()
branch=m.command(['git','branch','--show-current'],m.ORIGINAL,'original-postsync-branch').decode().strip()
assert not [s for s in status.splitlines() if not s.startswith('?? ')], 'tracked original modifications'
for rel in ['spec/progress/current.md','spec/tasks/done/LOOP1-GO-MSG-001.md']:
    data=m.command(['git','show',head+':'+rel],m.ROOT,'original-content-'+pathlib.Path(rel).name)
    # tracked checkout may use CRLF; compare normalized text for Markdown only
    assert (m.ORIGINAL/rel).read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n')
current=(m.ORIGINAL/'spec/progress/current.md').read_text(encoding='utf-8')
assert 'Current Task: LOOP1-GO-MSG-001' in current and 'Current Task State: done' in current and 'Gate Status: OPEN' in current
hits=list((m.ORIGINAL/'spec/tasks').glob('*/LOOP1-GO-MSG-001.md'))
assert len(hits)==1 and hits[0].parent.name=='done'
assert 'status: done' in hits[0].read_text(encoding='utf-8')
assert (m.ORIGINAL/'spec/tasks/backlog/LOOP1-E2E-001.md').is_file()
value={'result':'PASS','branch':branch,'head':head,'preserved_original_files':len(prior['untracked']),'relocation':reloc,'tracked_changes':False,'MSG_queue':'done uniquely','E2E_queue':'backlog','S1_gate':'OPEN','unknown_ownership':'not resolved; contents preserved; no claim of clean original checkout'}
(m.EV/'original-sync-verification.json').write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(value,ensure_ascii=False))