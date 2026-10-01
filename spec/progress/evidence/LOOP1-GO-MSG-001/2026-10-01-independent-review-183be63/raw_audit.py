from pathlib import Path
import subprocess,hashlib,json
r=Path.cwd(); e=r.parent/'evidence'; entries=[]
for group in ['research/prompts/P-MSG-FIX-20261001','research/runs/R-MSG-FIX-20261001','research/prompts/P-MSG-IMPLEMENTATION-20261001','research/runs/R-MSG-IMPLEMENTATION-20261001']:
 paths=subprocess.check_output(['git','ls-files',group],text=True).splitlines()
 for path in paths:
  raw=(r/path).read_bytes(); committed=subprocess.check_output(['git','show','HEAD:'+path]); assert raw==committed,path
  entries.append(dict(path=path,sha256=hashlib.sha256(raw).hexdigest(),byte_identical=True))
diff=subprocess.check_output(['git','diff','--exit-code','84b7a63..HEAD','--','spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-independent-review-f1764fd'])
assert not diff
(e/'raw-byte-audit.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
print('PASS raw tracked file working/HEAD byte identity',len(entries),'immutable prior FAIL range unchanged')
