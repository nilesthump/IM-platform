import hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,encoding='utf-8').strip()
base='87c0ee2b15eabb4ec56bf93f487e2e62ba43e7eb'
protected=['backend','contracts','deploy','ci','tools','tests','spec/architecture','spec/domain','spec/invariants']
objects={p:git('rev-parse','HEAD:'+p) for p in protected}
for p,obj in objects.items():
    assert obj==git('rev-parse',base+':'+p),(p,'protected tree changed')
tasks=list((ROOT/'spec/tasks').glob('*/LOOP1-ARCH-REMEDIATION-004.md'))
assert len(tasks)==1
text=tasks[0].read_text(encoding='utf-8')
assert not re.search('\u6402[0-9]',text)
assert '\ufffd' not in text
for n in ['3','10','11','12-14']:
    assert '\u00a7'+n in text
current=(ROOT/'spec/progress/current.md').read_text(encoding='utf-8')
assert current.count('Current Task: LOOP1-ARCH-REMEDIATION-004')==1
assert 'Current Task State: '+tasks[0].parent.name in current
md=ROOT/'spec/architecture/frozen-architecture.md'
pdf=ROOT/'scalable-distributed-im-architecture.pdf'
assert hashlib.sha256(md.read_bytes()).hexdigest()=='83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e'
assert hashlib.sha256(pdf.read_bytes()).hexdigest()=='546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510'
print(json.dumps({'head':git('rev-parse','HEAD'),'task_queue':tasks[0].parent.name,'canonical_sha256':hashlib.sha256(md.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'protected_tree_objects':objects,'result':'PASS'},indent=2))
