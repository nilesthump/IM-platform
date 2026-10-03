"""Fail-closed actual API34 GUI instrumentation, preserving existing test families."""
from pathlib import Path
import argparse,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--serial',required=True);a=p.parse_args()
if not a.serial.startswith('emulator-'):raise RuntimeError('Explicit actual emulator required')
env=os.environ.copy()
def run(argv,cwd=ROOT,command_env=None):subprocess.run(list(map(str,argv)),cwd=cwd,env=command_env or env,check=True)
gradle=env.get('IM_CLIENT_GRADLE',ROOT/'clients/mobile'/('gradlew.bat' if os.name=='nt' else 'gradlew'))
adb=env.get('IM_CLIENT_ADB','adb')
build_env=env.copy();build_env.pop('ANDROID_USER_HOME',None);build_env.pop('ANDROID_AVD_HOME',None)
run([gradle,'--no-daemon','-PimSendInstrumentation=im.platform.client.ui.GuiInstrumentation','assembleDebug','assembleDebugAndroidTest'],ROOT/'clients/mobile',build_env)
sdk=subprocess.check_output([adb,'-s',a.serial,'shell','getprop','ro.build.version.sdk'],env=env,text=True).strip()
if sdk!='34':raise RuntimeError('Actual API34 emulator required')
for name in ('debug/app-debug.apk','androidTest/debug/app-debug-androidTest.apk'):run([adb,'-s',a.serial,'install','-r',ROOT/'clients/mobile/app/build/outputs/apk'/name])
r=subprocess.run([adb,'-s',a.serial,'shell','am','instrument','-w','im.platform.client.test/im.platform.client.ui.GuiInstrumentation'],env=env,capture_output=True,text=True,timeout=180)
print(r.stdout);print(r.stderr,file=sys.stderr)
if r.returncode or 'INSTRUMENTATION_RESULT: result=PASS' not in r.stdout or 'INSTRUMENTATION_RESULT: sdkInt=34' not in r.stdout or 'INSTRUMENTATION_CODE: -1' not in r.stdout:raise RuntimeError('Actual GUI instrumentation failed')
print('PASS actual API34 Compose navigation, appearance extrema, encrypted SDK credentials and cleanup')
