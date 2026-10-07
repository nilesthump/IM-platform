from pathlib import Path
import subprocess,json
adb='H:/Android/platform-tools/adb.exe';serial='emulator-5590';private=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix')
def cmd(*a):return subprocess.check_output([adb,'-s',serial,*a],text=True,timeout=90)
print(cmd('install','-r','clients/mobile/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'))
cmd('reverse','tcp:8443','tcp:18443')
try:
 text=cmd('shell','am','instrument','-w','-e','caFile','4b1cffac.0','-e','port','8443','im.platform.client.test/im.platform.client.ui.GuiTrustRollbackInstrumentation');(private/'rollback-tls.txt').write_text(text,encoding='utf-8',newline='\n');print(text)
 assert 'INSTRUMENTATION_RESULT: result=PASS' in text and 'tlsRejection=SSLHandshakeException' in text
 data=json.loads((private/'rollback.json').read_text());data['defaultTLS']='PASS fresh default SDK SSLHandshakeException to same live fixture';(private/'rollback.json').write_text(json.dumps(data,indent=2)+'\n',newline='\n')
finally:cmd('reverse','--remove','tcp:8443')
assert cmd('shell','id','-u').strip()=='2000';assert cmd('shell','getenforce').strip()=='Enforcing';assert 'tcp:8443' not in cmd('reverse','--list')
print('PASS full Android temporary trust rollback')
cmd('emu','kill');print('Stopped only owned emulator-5590')
