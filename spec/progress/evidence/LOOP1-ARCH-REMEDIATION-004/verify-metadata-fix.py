from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[4]
def git(*args): return subprocess.check_output(['git','-C',str(ROOT),*args],encoding='utf-8').strip()
def valid(s):
 return all(x in s for x in ['applicable \u00a73/\u00a710/\u00a711/\u00a712-14','canonical \u00a73/\u00a710 SRC-01 through SRC-07/\u00a711']) and '\u6402' not in s and '\ufffd' not in s
s=(ROOT/'spec/tasks/review/LOOP1-ARCH-REMEDIATION-004.md').read_text(encoding='utf-8')
assert valid(s)
assert not valid(s.replace('\u00a7','\u6402'))
assert not valid(s.replace('\u00a710','\ufffd10'))
assert 'Wait for predecessor' not in s
assert 'fresh post-fix independent Review' in s
c=(ROOT/'spec/progress/current.md').read_text(encoding='utf-8')
assert c.count('Current Task: LOOP1-ARCH-REMEDIATION-004')==1
assert 'Current Task State: review' in c and 'new independent Review' in c
for scope in ['backend','contracts','deploy','ci','tools','tests','spec/architecture']:
 assert not git('diff','87c0ee2','--',scope), scope
assert git('rev-parse','HEAD:backend/go')==git('rev-parse','87c0ee2:backend/go')
print('PASS: UTF-8 exact current authority references; two negative controls rejected; recovery unique004 review; protected implementation/authority trees unchanged from87c0ee2')
