"""Compile real Web/Desktop group UI and exercise behavior. Native acceptance is separate."""
from pathlib import Path
import json, os, shutil, subprocess, sys, tempfile
root=Path(__file__).resolve().parents[3]
npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm');node=shutil.which('node')
if not npm or not node:raise RuntimeError('Node/npm required')
subprocess.run([sys.executable,'-B',str(root/'tests/clients/group/test_harness_failures.py')],check=True,cwd=root)
subprocess.run([node,str(root/'tests/clients/group/harness-failures.cjs')],check=True,cwd=root)
with tempfile.TemporaryDirectory(prefix='group-client-') as directory:
 stage=Path(directory)
 for name in ('package.json','package-lock.json'):shutil.copyfile(root/'clients/desktop'/name,stage/name)
 subprocess.run([npm,'--prefix',str(stage),'ci','--ignore-scripts','--no-audit','--no-fund'],check=True,cwd=root)
 out=stage/'output';out.mkdir();(out/'package.json').write_text('{"type":"commonjs"}',encoding='utf8')
 modules=stage/'node_modules'
 config={'compilerOptions':{'strict':True,'target':'ES2022','module':'commonjs','moduleResolution':'node','lib':['ESNext','DOM','DOM.Iterable'],'esModuleInterop':True,'jsx':'react','rootDir':str(root/'clients'),'outDir':str(out),'typeRoots':[str(modules/'@types')],'paths':{'react':[str(modules/'@types/react')],'react-dom/*':[str(modules/'@types/react-dom/*')],'@tauri-apps/api/*':[str(modules/'@tauri-apps/api/*')]}},'files':[str(root/'clients/web/src/ui/components/Shell.tsx'),str(root/'clients/desktop/src/ui/components/Shell.tsx')]}
 (stage/'tsconfig.json').write_text(json.dumps(config),encoding='utf8')
 subprocess.run([node,str(modules/'typescript/bin/tsc'),'-p',str(stage/'tsconfig.json')],check=True,cwd=root)
 subprocess.run([node,str(root/'tests/clients/group/behavior.cjs'),str(out)],check=True,cwd=root)
 subprocess.run([node,str(root/'tests/clients/group/desktop.cjs'),str(out)],check=True,cwd=root)
