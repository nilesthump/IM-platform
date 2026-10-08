from pathlib import Path
import hashlib,json,subprocess,sys,time,shutil
r=Path('H:/.codex/worktrees/g/IM-platform');p=Path('H:/.codex/gui-handoffs/20261008-win-finalize/development');base=p/'isolated-owned';paths=['clients/desktop/dist','clients/desktop/node_modules','clients/desktop/src-tauri/gen/schemas','clients/mobile/.gradle','clients/mobile/app/build','clients/shared/protocol-sdk/dist','clients/shared/protocol-sdk/node_modules'];moved=[];data={}
def inv(s):return {str(f.relative_to(s)):hashlib.sha256(f.read_bytes()).hexdigest() for f in s.rglob('*') if f.is_file()}
try:
 for rel in paths:
  s=(r/rel).resolve();d=(base/rel).resolve();assert s.is_relative_to(r.resolve()) and d.is_relative_to(base.resolve())
  if not s.exists():continue
  subprocess.run(['git','-c','core.excludesFile=NUL','check-ignore','-q',rel+'/'],cwd=r,check=True);assert not d.exists();data[rel]=inv(s);d.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(s),str(d));moved.append((rel,s,d))
 results=[]
 for i,args in enumerate([[]]):
  a=['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development'];t=time.monotonic();x=subprocess.run(a,cwd=r,capture_output=True);(p/f'clean-{i}.stdout.txt').write_bytes(x.stdout);(p/f'clean-{i}.stderr.txt').write_bytes(x.stderr);results.append({'argv':a,'exit':x.returncode,'elapsedSeconds':time.monotonic()-t,'stdoutSHA256':hashlib.sha256(x.stdout).hexdigest(),'stderrSHA256':hashlib.sha256(x.stderr).hexdigest()})
finally:
 for rel,s,d in reversed(moved):
  assert not s.exists();s.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(d),str(s));assert data[rel]==inv(s)
out={'checks':results,'beforeAfterByteHashesEqual':True,'restoredFiles':{k:len(v) for k,v in data.items()},'beforeHashInventorySHA256':hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest(),'cleanAfter':not subprocess.check_output(['git','status','--porcelain'],cwd=r,text=True).strip()};(p/'clean-acceptance-result.json').write_text(json.dumps(out,indent=2));(p/'owned-hash-inventory.json').write_text(json.dumps(data,sort_keys=True));print(json.dumps(out,indent=2));assert all(x['exit']==0 for x in results)






