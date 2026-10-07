from pathlib import Path
import subprocess,json
adb='H:/Android/platform-tools/adb.exe';serial='emulator-5590';private=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix')
def cmd(*a):return subprocess.check_output([adb,'-s',serial,*a],text=True).strip()
def sh(s):return cmd('shell',s)
state=json.loads((private/'android-state.json').read_text());cmd('root');cmd('wait-for-device');assert sh('id -u')=='0'
baseline=next(iter(state['namespaces'].values()))['files'];checks=[]
for pid in ['1',*sh('pidof zygote64 zygote').split()]:
 files=sh('nsenter --mount=/proc/'+pid+'/ns/mnt -- sh -c "cd /apex/com.android.conscrypt/cacerts && sha256sum *"');assert files==baseline
 mounts=sh('cat /proc/'+pid+'/mountinfo');assert not any('/apex/com.android.conscrypt/cacerts' in line.split()[4:5] for line in mounts.splitlines())
 checks.append({'pid':pid,'CAcount':len(files.splitlines()),'baselineEqual':True,'ownedMountAbsent':True})
assert sh('test ! -e /data/local/tmp/im-gui-ca && test ! -e /data/local/tmp/im-gui-mount-ro && test ! -e /apex/com.android.conscrypt/cacerts/4b1cffac.0 && echo ABSENT')=='ABSENT'

if 'tcp:8443' in cmd('reverse','--list'):cmd('reverse','--remove','tcp:8443')
assert 'tcp:8443' not in cmd('reverse','--list');assert sh('getenforce')=='Enforcing';cmd('unroot');cmd('wait-for-device');assert sh('id -u')=='2000'
data={'freshNamespaces':checks,'ownPathsAbsent':True,'SELinux':'Enforcing','unroot':'PASS uid2000','reverse8443Absent':True,'defaultTLS':'fresh SDK rejection pending'};(private/'rollback.json').write_text(json.dumps(data,indent=2)+'\n',newline='\n');print(json.dumps(data,indent=2))

