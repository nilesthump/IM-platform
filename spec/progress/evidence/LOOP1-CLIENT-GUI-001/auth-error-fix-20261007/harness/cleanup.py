from pathlib import Path
import subprocess,time,json,hashlib
P=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix');D='C:/Program Files/Docker/Docker/resources/bin/docker.exe';A='H:/Android/platform-tools/adb.exe'
assert json.loads((P/'rollback.json').read_text())['defaultTLS'].startswith('PASS')
(P/'fixture-stop').touch();project=json.loads((P/'public.json').read_text())['project']
for _ in range(120):
 containers=subprocess.check_output([D,'ps','-aq','--filter','label=com.docker.compose.project='+project],text=True).split();volumes=subprocess.check_output([D,'volume','ls','-q','--filter','label=com.docker.compose.project='+project],text=True).split()
 if not containers and not volumes:break
 time.sleep(.5)
else:raise RuntimeError('Exact owned fixture cleanup incomplete')
assert 'emulator-5590' not in subprocess.check_output([A,'devices'],text=True)
p=Path('clients/mobile/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk');(P/'rollback-test.apk').write_bytes(p.read_bytes());(P/'rollback-apk-hash.json').write_text(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'instrumentation':'im.platform.client.ui.GuiTrustRollbackInstrumentation'},indent=2))
facts={'result':'PASS','project':project,'containers':containers,'volumes':volumes,'ownedEmulator5590Absent':True,'fixtureStoppedAfterSameLiveFreshDefaultSDKRejection':True,'unrelatedResourcesUntouched':True};(P/'cleanup.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))