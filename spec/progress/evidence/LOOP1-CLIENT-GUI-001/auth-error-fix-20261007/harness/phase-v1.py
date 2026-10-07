from pathlib import Path
import subprocess,json,re,sys,time,threading,hashlib,shlex,uuid
P=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix');A='H:/Android/platform-tools/adb.exe';S='emulator-5590';D='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
pub=json.loads((P/'public.json').read_text());users={u['displayName'].split()[-1]:u for u in pub['accounts']};project=pub['project'];pg=project+'-postgres-1';uid=str(uuid.UUID(users['Avery']['userId']))
def cmd(*a,timeout=300):return subprocess.check_output([A,'-s',S,*a],text=True,timeout=timeout)
def dc(*a):return subprocess.check_output([D,*a],text=True,timeout=60)
labels=json.loads(dc('inspect',pg))[0]['Config']['Labels'];assert labels['com.docker.compose.project']==project and labels['com.docker.compose.service']=='postgres'
out=P/('attempt-'+str(time.time_ns()));out.mkdir();events=[];fail=[]
def sessionFacts():return dc('exec',pg,'psql','-U','im','-d','im','-v','ON_ERROR_STOP=1','-Atc',"SELECT client_type,(expires_at<=now())::text FROM sessions WHERE user_id='"+uid+"' AND client_type='MOBILE'").strip()
def controller():
 try:
  for _ in range(720):
   paths=cmd('shell','if [ -d /sdcard/Android/data/im.platform.client/files/gui-auth ]; then find /sdcard/Android/data/im.platform.client/files/gui-auth -name expiry-ready; fi',timeout=10).splitlines()
   if paths:break
   time.sleep(.25)
  else:raise RuntimeError('Readiness marker absent expiry')
  marker=paths[-1];before=sessionFacts();assert before=='MOBILE|false';(P/'fixture-command').write_text('expire Avery\n')
  for _ in range(150):
   if (P/'fixture-expiry-applied').exists():break
   time.sleep(.2)
  else:raise RuntimeError('Canonical fixture stdin expiry acknowledgement absent')
  after=sessionFacts();assert after=='MOBILE|true';events.append({'marker':marker,'ownedProject':project,'exactGoHelper':'tests/clients/gui/go_runtime.py stdin expire Avery','before':before,'after':after,'secretsRecorded':False});cmd('shell','touch '+marker.replace('expiry-ready','expiry-continue'),timeout=10)
 except Exception as e:fail.append(repr(e))
cmd('shell','am','force-stop','im.platform.client');cmd('shell','pm','clear','im.platform.client');cmd('logcat','-c')
src=['clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt','clients/mobile/app/src/main/kotlin/im/platform/client/ui/Workspace.kt','clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt','clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/GuiAuthenticatedInstrumentation.kt']
sourceHashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in src}
for p in src:(out/Path(p).name).write_bytes(Path(p).read_bytes())
beforeHEAD=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
t=threading.Thread(target=controller,daemon=True);t.start();start=time.monotonic()
argv=['am','instrument','-w','-e','phase','auth-errors','-e','avery',users['Avery']['username'],'im.platform.client.test/im.platform.client.ui.GuiAuthenticatedInstrumentation']
text=cmd('shell',shlex.join(argv),timeout=600);(out/'instrumentation.txt').write_text(text,encoding='utf-8');(out/'androidruntime.txt').write_text(cmd('logcat','-d','-s','AndroidRuntime:E'),encoding='utf-8');m=re.search(r'captureRun=(\d+)',text)
if m:cmd('pull','/sdcard/Android/data/im.platform.client/files/gui-auth/'+m[1],str(out/'screens'))
(out/'controls.json').write_text(json.dumps({'events':events,'failures':fail},indent=2))
(out/'run.json').write_text(json.dumps({'phase':'auth-errors','elapsedSeconds':time.monotonic()-start,'captureRun':m[1] if m else None,'sourceHEAD':beforeHEAD,'sourceDirtyAtCapture':False,'buildBeforeProductCommit':False,'sourceHashes':sourceHashes,'apkHashes':json.loads((P/'apk-hashes.json').read_text()),'publicFixture':pub,'runtime':'actual API34 x86_64 IMClientSend34 emulator5590','steps':['cold14/Compact wrong anonymous login','real login set cold22/Comfort via Settings logout and wrong login','real login switch Warm22/Comfort logout and wrong login','real login save secure slot, controlled canonical Go stdin expiry, actual Refresh session button, UI expired plus former secure slot and current pointer absent']},indent=2));print(text);print('Evidence attempt '+str(out));assert 'INSTRUMENTATION_RESULT: result=PASS' in text and 'INSTRUMENTATION_CODE: -1' in text;assert not fail and len(events)==1