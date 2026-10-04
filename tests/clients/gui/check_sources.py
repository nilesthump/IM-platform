"""Check unchanged guards with only owned Git-ignored build outputs isolated."""
from pathlib import Path
import os,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
expected=Path(os.environ.get('IM_GUI_ASSIGNED_ROOT','H:/.codex/worktrees/s/IM-platform')).resolve()
if ROOT.resolve()!=expected:raise RuntimeError('Assigned worktree root mismatch')
resolved=subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip()
if Path(resolved).resolve()!=expected:raise RuntimeError('Resolved Git root mismatch')
owned=Path('H:/.codex/toolchains/client-gui/guard-artifacts').resolve()
target=owned/str(time.time_ns())
paths=['clients/desktop/dist','clients/desktop/node_modules','clients/desktop/src-tauri/gen/schemas','clients/mobile/.gradle','clients/mobile/app/build','clients/shared/protocol-sdk/dist','clients/shared/protocol-sdk/node_modules']
moved=[]
try:
    for relative in paths:
        source=(ROOT/relative).resolve();dest=(target/relative).resolve()
        if not source.is_relative_to(expected) or not dest.is_relative_to(owned):raise RuntimeError('Unsafe move target')
        if not source.exists():continue
        subprocess.run(['git','-c','core.excludesFile=NUL','check-ignore','-q',relative+'/'],cwd=ROOT,check=True)
        if dest.exists():raise RuntimeError('Artifact destination already exists')
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(source),str(dest));moved.append((source,dest));print('Isolated own ignored output '+relative,flush=True)
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
    for args in [('ci/check_architecture.py','--scope','all','--json'),('tools/verify_frozen_architecture.py',),('-m','unittest','discover','-s','tests/architecture','-p','test_*.py')]:
        subprocess.run([sys.executable,'-X','utf8','-B',*args],cwd=ROOT,env=env,check=True)
    if '--development' in sys.argv:
        subprocess.run(['C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development'],cwd=ROOT,env=env,check=True)
finally:
    for source,dest in reversed(moved):
        if source.exists():raise RuntimeError('Unexpected regenerated artifact; restore needs explicit reconciliation')
        source.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(dest),str(source));print('Restored '+str(source.relative_to(ROOT)),flush=True)
