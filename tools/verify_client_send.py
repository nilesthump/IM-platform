#!/usr/bin/env python3
"""Fail-closed SEND verification on actual SQLx and Android TLS/SQLite runtimes."""
from pathlib import Path
import argparse, base64, importlib.util, os, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
def run(argv,cwd=ROOT,env=None):
    print('+',' '.join(map(str,argv)),flush=True);subprocess.run(list(map(str,argv)),cwd=cwd,env=env,check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--scope',choices=['shared','desktop','mobile'],required=True);p.add_argument('--serial');a=p.parse_args()
    if a.scope in ('shared','desktop'):
        npm='npm.cmd' if os.name=='nt' else 'npm'
        run([npm,'--prefix','clients/shared/protocol-sdk','ci','--ignore-scripts','--no-audit','--no-fund']);run([npm,'--prefix','clients/shared/protocol-sdk','run','build']);run(['node','tests/clients/send/shared.mjs'])
        if a.scope=='shared':return
        run([npm,'--prefix','clients/desktop','ci','--ignore-scripts','--no-audit','--no-fund']);run([npm,'--prefix','clients/desktop','run','build'])
        native=ROOT/'clients/desktop/src-tauri';run(['cargo','build','--locked','--bin','storage_probe'],native)
        target=Path(os.environ.get('CARGO_TARGET_DIR',native/'target'));target=target if target.is_absolute() else native/target
        probe=target/'debug'/('storage_probe.exe' if os.name=='nt' else 'storage_probe')
    else:
        if not a.serial or not a.serial.startswith('emulator-'):raise RuntimeError('Actual emulator serial required')
        wrapper=os.environ.get('IM_CLIENT_GRADLE',ROOT/'clients/mobile'/('gradlew.bat' if os.name=='nt' else 'gradlew'))
        if os.name!='nt':run(['chmod','+x',wrapper])
        run([wrapper,'--no-daemon','-PimSendInstrumentation=im.platform.client.send.SendInstrumentation','assembleDebug','assembleDebugAndroidTest'],ROOT/'clients/mobile')
        adb=os.environ.get('IM_CLIENT_ADB','adb');serial=a.serial
        def shell(*args):return subprocess.check_output([adb,'-s',serial,'shell',*args],text=True,timeout=30).strip()
        if shell('getprop','ro.build.version.sdk')!='34' or shell('getprop','sys.boot_completed')!='1' or shell('getprop','sys.user.0.ce_available')!='true':raise RuntimeError('Unlocked, fully booted minimum API34 emulator required')
        for apk in ('debug/app-debug.apk','androidTest/debug/app-debug-androidTest.apk'):run([adb,'-s',serial,'install','-r',ROOT/'clients/mobile/app/build/outputs/apk'/apk])
    with tempfile.TemporaryDirectory(prefix='im-send-tls-') as tmp:
        tmp=Path(tmp);cert=tmp/'cert.pem';key=tmp/'key.pem'
        openssl=os.environ.get('IM_CLIENT_OPENSSL','D:/Git/usr/bin/openssl.exe' if os.name=='nt' and Path('D:/Git/usr/bin/openssl.exe').exists() else 'openssl')
        # Private ephemeral fixture credentials; never product trust overrides.
        subprocess.run([openssl,'req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost,IP:127.0.0.1'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        spec=importlib.util.spec_from_file_location('send_tls_fixture',ROOT/'tests/clients/send/tls_fixture.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        fixture=module.Fixture(cert,key)
        try:
            endpoint='wss://localhost:'+str(fixture.port)
            if a.scope=='desktop':
                env=os.environ.copy();env['NODE_EXTRA_CA_CERTS']=str(cert);run(['node','tests/clients/send/desktop.mjs',probe,endpoint],env=env)
            else:
                run([adb,'-s',serial,'reverse','tcp:'+str(fixture.port),'tcp:'+str(fixture.port)])
                try:
                    pem=cert.read_text();der=base64.b64encode(base64.b64decode(''.join(pem.splitlines()[1:-1]))).decode()
                    argv=[adb,'-s',serial,'shell','am','instrument','-w','-e','endpoint',endpoint,'-e','certificate',der,'im.platform.client.test/im.platform.client.send.SendInstrumentation']
                    # The certificate is public; omit its long argv from logs.
                    print('+ actual API34 SendInstrumentation with private TLS fixture',flush=True)
                    result=subprocess.run(argv,capture_output=True,text=True,timeout=180);print(result.stdout);print(result.stderr,file=sys.stderr)
                    if result.returncode or 'INSTRUMENTATION_RESULT: result=PASS' not in result.stdout or 'INSTRUMENTATION_RESULT: sdkInt=34' not in result.stdout or 'INSTRUMENTATION_CODE: -1' not in result.stdout:raise RuntimeError('Actual Android SEND instrumentation failed')
                finally:run([adb,'-s',serial,'reverse','--remove','tcp:'+str(fixture.port)])
            if fixture.errors:raise RuntimeError('TLS fixture protocol assertions failed: '+str(fixture.errors))
            if fixture.sends<5:raise RuntimeError('Actual WSS sends were not exercised')
            print('PASS: controlled TLS fixture actual client behavior; this is distinct from Go durable-ACK E2E',flush=True)
        finally:fixture.close()
if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,subprocess.SubprocessError) as error:print('FAIL:',error,file=sys.stderr);sys.exit(1)
