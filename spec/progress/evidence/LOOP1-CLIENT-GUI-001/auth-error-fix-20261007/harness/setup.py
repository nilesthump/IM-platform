from pathlib import Path
import subprocess,json,hashlib,time
private=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix');adb='H:/Android/platform-tools/adb.exe';serial='emulator-5590'
def run(*a):return subprocess.check_output([adb,'-s',serial,*a],text=True,timeout=180)
assert run('shell','getprop','sys.boot_completed').strip()=='1'
for sub,name in [('debug','app-debug.apk'),('androidTest/debug','app-debug-androidTest.apk')]:
 p=Path('clients/mobile/app/build/outputs/apk')/sub/name;(private/name).write_bytes(p.read_bytes());print(run('install','-r',str(p)).strip())
print(run('shell','pm','clear','im.platform.client').strip());print(run('reverse','tcp:8443','tcp:18443').strip())
(private/'apk-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in private.glob('*.apk')},indent=2))
print('PASS owned emulator API34 fresh installed APKs/app fixture state')
