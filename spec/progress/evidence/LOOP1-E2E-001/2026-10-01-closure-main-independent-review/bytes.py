from pathlib import Path
import json,hashlib,subprocess
r=Path.cwd();sha=lambda x:hashlib.sha256(x).hexdigest();e=r/'spec/progress/evidence/LOOP1-E2E-001';a=json.loads((e/'2026-10-01-closure-archive-byte-audit.json').read_text())
for f in a['files']:
 p=r/f['destination']; b=p.read_bytes(); assert len(b)==f['size'] and sha(b)==f['sha256']; assert b==Path(f['source']).read_bytes(); assert b==subprocess.check_output(['git','show','HEAD:'+Path(f['destination']).as_posix()])
arc=e/'2026-10-01-independent-review-6346';assert sha((arc/'final-transport-manifest.json').read_bytes())=='5e18bcb28c5d6685f61748f8b1cb223fa0b0dd8d9028891ce3e3ce980aa20fba'
m=json.loads((arc/'final-manifest.json').read_text());
for f in m['files']:
 b=(arc/f['path']).read_bytes();assert len(b)==f['size'] and sha(b)==f['sha256']
orig=Path('H:/IM-platform');inv=json.loads((orig/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync/original-inventory.json').read_text());rel={'spec/progress/evidence/LOOP1-CI-001/review2-negative-probe.py':'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync/preserved-original/review2-negative-probe.py'}
for f in inv['untracked']:
 b=(orig/rel.get(f['path'],f['path'])).read_bytes();assert len(b)==f['size'] and sha(b)==f['sha256']
for i in ['LOOP1-GO-AUTH-001','LOOP1-GO-SOCIAL-001','LOOP1-GO-MSG-001','LOOP1-E2E-001']:
 p=list((r/'spec/tasks').glob('*/'+i+'.md'));assert len(p)==1 and p[0].parent.name=='done' and 'status: done' in p[0].read_text()
print('PASS',len(a['files']),'source/worktree/committed archive bytes;',len(m['files']),'reviewer manifest entries;605 original files;four unique done')
json.dump({'result':'PASS','archive_files':len(a['files']),'review_manifest_files':len(m['files']),'original_files':len(inv['untracked']),'task_queue':'four unique done'},open('H:/.codex/evidence/s1-closure-review/bytes.json','w'),indent=2)

