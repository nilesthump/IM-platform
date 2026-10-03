from pathlib import Path
import subprocess,os,json,time,sys
root=Path.cwd()
env=os.environ.copy()
env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env['PATH']
env['PYTHONUTF8']='1';env['PYTHONDONTWRITEBYTECODE']='1'
prefix='spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/mvp-planning/'
commands=[
[sys.executable,'-X','utf8','-B','tools/verify_frozen_architecture.py','--base-commit','59dcf34e4538d2f35ccafde8104e860f8cf5cd7a'],
[sys.executable,'-X','utf8','-B','ci/check_architecture.py','--scope','all','--json'],
[sys.executable,'-X','utf8','-B','-m','unittest','discover','-s','tests/architecture'],
[sys.executable,'-X','utf8','-B',prefix+'verify_planning.py'],
['git','diff','--check'],
['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development']]
results=[]
for i,cmd in enumerate(commands):
 t=time.monotonic();p=subprocess.run(cmd,cwd=root,env=env,capture_output=True,encoding='utf-8',errors='replace')
 (root/prefix/f'check-{i}.txt').write_text(p.stdout+p.stderr,encoding='utf-8')
 result={'argv':cmd,'exit_code':p.returncode,'elapsed_seconds':round(time.monotonic()-t,3),'result':'PASS' if p.returncode==0 else 'FAIL','output':prefix+f'check-{i}.txt'}
 results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
(root/prefix/'checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raise SystemExit(int(any(x['exit_code'] for x in results)))
