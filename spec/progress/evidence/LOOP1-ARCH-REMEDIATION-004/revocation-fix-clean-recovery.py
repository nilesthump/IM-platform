import os,sys,tempfile,subprocess
from pathlib import Path
root=Path.cwd().resolve()
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,encoding='utf-8').strip()
with tempfile.TemporaryDirectory(prefix='im-revocation-fix-clean-') as d:
    checkout=(Path(d)/'checkout').resolve()
    assert checkout.is_relative_to(Path(d).resolve())
    subprocess.run(['git','worktree','add','--detach',str(checkout),sha],cwd=root,env=env,check=True)
    try:
        status=subprocess.check_output(['git','status','--porcelain'],cwd=checkout,env=env,text=True,encoding='utf-8')
        assert not status,status
        print('Exact clean detached candidate '+sha,flush=True)
        subprocess.run(['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance'],cwd=checkout,env=env,check=True)
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,env=env,text=True,encoding='utf-8')
    finally:
        subprocess.run(['git','worktree','remove',str(checkout)],cwd=root,env=env,check=True)
print('PASS local clean recovery structure; not independent Review or hosted acceptance')
