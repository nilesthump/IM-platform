"""Unaltered owned Android app screenshot with truthful build/source metadata."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
out=Path(sys.argv[1]).resolve();owned=(ROOT/'spec/progress/evidence/LOOP1-CLIENT-GUI-001').resolve()
if not out.is_relative_to(owned) or out.exists():raise RuntimeError('New exact task evidence screenshot path required')
env=os.environ.copy();env.update(ANDROID_USER_HOME='H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user',ANDROID_AVD_HOME='H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/avd-home')
adb='H:/Android/platform-tools/adb.exe';serial='emulator-5590'
def adb_output(*args):return subprocess.check_output([adb,'-s',serial,*args],env=env)
if adb_output('shell','getprop','ro.build.version.sdk').strip()!=b'34':raise RuntimeError('API34 required')
adb_output('shell','am','start','-W','-n','im.platform.client/.MainActivity');time.sleep(2)
focus=adb_output('shell','dumpsys','window').decode(errors='replace')
if not any('mCurrentFocus=' in line and 'im.platform.client/im.platform.client.MainActivity' in line for line in focus.splitlines()):raise RuntimeError('Owned app must be foreground')
png=adb_output('exec-out','screencap','-p')
if png[:8]!=b'\x89PNG\r\n\x1a\n':raise RuntimeError('Actual PNG capture required')
out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(png)
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
dirty=bool(subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain'],cwd=ROOT,text=True).strip())
apk=ROOT/'clients/mobile/app/build/outputs/apk/debug/app-debug.apk'
meta={'task':'LOOP1-CLIENT-GUI-001','sha':sha,'workingTreeDirty':dirty,'status':'preliminary runtime QA; no final Architect approval','platform':'Android API34','serial':serial,'size':list(struct.unpack('>II',png[16:24])),'captureSHA256':hashlib.sha256(png).hexdigest(),'apkSHA256':hashlib.sha256(apk.read_bytes()).hexdigest(),'capture':'adb exec-out screencap -p; no image transformation','foreground':'im.platform.client.MainActivity','fixture':'unauthenticated local UI; no trusted fixture installed'}
out.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
