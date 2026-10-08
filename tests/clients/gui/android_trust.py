"""Exact Human-approved ephemeral trust overlay for named owned API34 emulator."""
from pathlib import Path
import hashlib,json,subprocess,sys
ADB='H:/Android/platform-tools/adb.exe'
PRIVATE=Path('H:/.codex/gui-handoffs/20261004-4f866046/gui-resume-research')
CA=PRIVATE.parent/'gui-runtime/tls-v2/ca.pem'
HASH='132339d5.0'; SOURCE='/data/local/tmp/im-gui-ca'; TARGET='/apex/com.android.conscrypt/cacerts'
def adb(*args):
 r=subprocess.run([ADB,'-s','emulator-5590',*args],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr.strip() or r.stdout.strip())
 return r.stdout.strip()
def shell(command):return adb('shell',command)
def snapshot(pid='1'):
 return {'files':shell(f'nsenter --mount=/proc/{pid}/ns/mnt -- sh -c "cd {TARGET} && sha256sum *"'),'mounts':shell(f'cat /proc/{pid}/mountinfo')}
if adb('emu','avd','name').splitlines()[0]!='IMClientSend34':raise RuntimeError('Wrong AVD')
if shell('getprop ro.build.version.sdk')!='34' or shell('getenforce')!='Enforcing':raise RuntimeError('Wrong API/SELinux')
if sys.argv[1]=='install':
 if hashlib.sha256((CA.parent/'ca.der').read_bytes()).hexdigest()!='e61a24364dc95315cbdf10bb6eade27b907ff94adb71bde1c827f93a48ad0de8':raise RuntimeError('Approved CA mismatch')
 if shell('id -u')!='0':raise RuntimeError('Approved adbd root required')
 baseline=PRIVATE/'android-trust-baseline.json'
 if baseline.exists():raise RuntimeError('Do not overwrite trust baseline')
 if shell(f'test ! -e {TARGET}/{HASH} && test ! -e {SOURCE} && echo ABSENT')!='ABSENT':raise RuntimeError('Owned collision')
 pids=['1',*shell('pidof zygote64 zygote').split()]
 state={pid:snapshot(pid) for pid in pids}
 baseline.write_text(json.dumps(state,indent=2)+'\n')
 shell(f'mkdir {SOURCE} && cp -a {TARGET}/. {SOURCE}/')
 adb('push',str(CA),SOURCE+'/'+HASH)
 shell(f'chmod 644 {SOURCE}/{HASH}')
 installed=[]
 try:
  for pid in pids:
   shell(f'nsenter --mount=/proc/{pid}/ns/mnt -- mount -o bind,ro {SOURCE} {TARGET}')
   installed.append(pid)
   (PRIVATE/'android-overlay-pids.json').write_text(json.dumps(installed))
   if not any(line.split()[4]==TARGET and 'ro' in line.split()[5].split(',') for line in shell(f'cat /proc/{pid}/mountinfo').splitlines()):raise RuntimeError('BLOCKED: approved read-only overlay unavailable; stop and roll back')
   if HASH not in shell(f'nsenter --mount=/proc/{pid}/ns/mnt -- ls {TARGET}'):raise RuntimeError('Added CA absent')
  shell('am force-stop im.platform.client')
  shell('am start -n im.platform.client/.MainActivity')
  app=shell('pidof im.platform.client')
  if HASH not in shell(f'nsenter --mount=/proc/{app}/ns/mnt -- ls {TARGET}'):raise RuntimeError('Fresh app namespace CA absent')
  if shell('getenforce')!='Enforcing':raise RuntimeError('SELinux changed')
  print(json.dumps({'result':'PASS','serial':'emulator-5590','namespaces':installed,'appPid':app,'overlay':'read-only bind','SELinux':'Enforcing','certificate':HASH}))
 except Exception:
  print('FAIL exact overlay; installed namespace pids='+str(installed));raise
elif sys.argv[1]=='rollback':
 shell('am force-stop im.platform.client')
 installed=json.loads((PRIVATE/'android-overlay-pids.json').read_text()) if (PRIVATE/'android-overlay-pids.json').exists() else []
 for pid in reversed(installed):shell(f'nsenter --mount=/proc/{pid}/ns/mnt -- umount {TARGET}')
 shell(f'test "{SOURCE}" = /data/local/tmp/im-gui-ca && rm -rf {SOURCE}')
 adb('reverse','--remove','tcp:18443')
 adb('reboot');adb('wait-for-device')
 print('Owned emulator reboot requested; verify fresh namespace baseline and unroot separately')
