from pathlib import Path
import subprocess,json,time,hashlib,os
r=Path('H:/.codex/worktrees/g/IM-platform');p=Path('H:/.codex/gui-handoffs/20261007-auth-final-review/metadata-extension');source=r/'tests/clients/gui/check_sources.py'
s=source.read_text(encoding='utf8').replace("'--development'","'--acceptance'").replace("'Development'","'Acceptance'").replace('ROOT=Path(__file__).resolve().parents[3]',"ROOT=Path('H:/.codex/worktrees/g/IM-platform')")
(p/'check-sources-acceptance.py').write_text(s,encoding='utf8')
env=os.environ.copy();env['IM_GUI_ASSIGNED_ROOT']=str(r);env['PYTHONIOENCODING']='utf-8'
args=['C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-Xutf8','-B',str(p/'check-sources-acceptance.py'),'--acceptance'];start=time.monotonic();x=subprocess.run(args,cwd=r,env=env,capture_output=True);(p/'acceptance.stdout.txt').write_bytes(x.stdout);(p/'acceptance.stderr.txt').write_bytes(x.stderr)
result={'argv':args,'exit':x.returncode,'elapsedSeconds':time.monotonic()-start,'originalScriptSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'privateCopySHA256':hashlib.sha256(s.encode()).hexdigest(),'onlyChanges':'ROOT assigned absolute; development switches to Acceptance; ownership/gitignored/path checks/finally restore unchanged','stdoutSHA256':hashlib.sha256(x.stdout).hexdigest(),'stderrSHA256':hashlib.sha256(x.stderr).hexdigest(),'stdoutTail':x.stdout.decode('utf8')[-1100:],'stderrTail':x.stderr.decode('utf8')[-600:]};(p/'acceptance-result.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));raise SystemExit(x.returncode)

