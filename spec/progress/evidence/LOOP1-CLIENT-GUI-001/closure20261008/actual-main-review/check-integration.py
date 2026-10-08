from pathlib import Path
import hashlib,json,subprocess
r=Path('H:/.codex/worktrees/g/IM-platform');p=Path('H:/.codex/gui-handoffs/20261008-gui-actual-main-audit');e=r/'spec/progress/evidence/LOOP1-CLIENT-GUI-001/integration20261008'
h=lambda b:hashlib.sha256(b).hexdigest();j=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
a=j(e/'integration-verification.json')
for x in a['acceptedMainFilesVerified']:
 f=r/x['path'];assert h(f.read_bytes())==x['sha256']
 actual=subprocess.check_output(['git','show','7088ecd5c905dceadae8ed2f504d54d6585ca3dc:'+x['path']],cwd=r)
 assert actual.replace(b'\r\n',b'\n')==f.read_bytes().replace(b'\r\n',b'\n'),x['path']
for x in j(e/'premerge-bindings.json')['records']:
 actual=subprocess.check_output(['git','show',x['sourceCommit']+':'+x['sourcePath']],cwd=r)
 assert actual==(e/x['file']).read_bytes() and h(actual)==x['sha256'],x['file']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()=='b14bf1070ba26ac368488e2c6ea15a7936e2de89'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=r,text=True).strip()
assert len(list((r/'spec/tasks').glob('*/LOOP1-CLIENT-GUI-001.md')))==1
assert len(list((r/'spec/tasks').glob('*/LOOP1-CLIENT-NATIVE-ARCH-001.md')))==1
out={'result':'PASS','exactReviewedSHA':'b14bf1070ba26ac368488e2c6ea15a7936e2de89','acceptedMainFilesVerified':len(a['acceptedMainFilesVerified']),'priorSnapshotsByteExact':True,'currentTaskUniqueReview':True,'nativePrerequisiteUniqueDone':True,'clean':True}
(p/'integration-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

