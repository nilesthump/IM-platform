from pathlib import Path
import subprocess,json,hashlib,re
p=Path('H:/.codex/gui-handoffs/20261008-gui-actual-main-audit');gh='C:/Program Files/GitHub CLI/gh.exe';h=p/'hosted'
for name,jid in [('classify-main',113182960288),('mobile-main-PRIVATE',113183129015)]:
 f=h/(name+'.log');assert not f.exists()
 x=subprocess.run([gh,'api','--allow-escape-sequences',f'repos/nilesthump/IM-platform/actions/jobs/{jid}/logs'],capture_output=True);f.write_bytes(x.stdout);(h/(name+'.stderr.txt')).write_bytes(x.stderr);assert x.returncode==0,(name,x.stderr)
 if name.startswith('mobile'):
  lines=x.stdout.decode(errors='replace').splitlines();safe=[s for s in lines if 'INSTRUMENTATION_RESULT:' in s and any('INSTRUMENTATION_RESULT: '+k+'=' in s for k in ['assertions','sdkInt','result','captureRun','engine']) or 'INSTRUMENTATION_CODE:' in s or 'Emulator version ' in s or 'API level:' in s]
  text='\n'.join(safe)+'\n';assert 'assertions=46' in text and 'sdkInt=34' in text and 'INSTRUMENTATION_CODE: -1' in text and 'result=FAIL' not in text
  (h/'mobile-main-safe-excerpt.txt').write_text(text);print(text)
 else:
  text=x.stdout.decode(errors='replace');assert 'BASE_SHA: 7088ecd5c905dceadae8ed2f504d54d6585ca3dc' in text and 'HEAD_SHA: b14bf1070ba26ac368488e2c6ea15a7936e2de89' in text
  flags={m[1]:m[2]=='true' for m in re.finditer(r'"(go|java|web|desktop|mobile|shared|old_client|plugin|migration|compatibility|deploy|architecture|source_go|source_java)": (true|false)',text)};assert len(flags)==14 and all(flags.values());(h/'classify-main-derived.json').write_text(json.dumps({'result':'PASS','flags':flags,'originalSHA256':hashlib.sha256(x.stdout).hexdigest()},indent=2));print(json.dumps(flags))
 print(json.dumps({'name':name,'exit':x.returncode,'bytes':len(x.stdout),'sha256':hashlib.sha256(x.stdout).hexdigest(),'wholeMobileLogPrivateOnly':name.startswith('mobile')}))
