"""Approved exact ephemeral API34 trust tool lifecycle; no product TLS changes."""
from pathlib import Path
import datetime as dt,hashlib,json,posixpath,ssl,subprocess,sys,time
ADB='H:/Android/platform-tools/adb.exe';SERIAL='emulator-5590'
PRIVATE=Path('H:/.codex/gui-handoffs/20261004-4f866046/gui-mount-approved-research')
OLD=PRIVATE.parent/'gui-second-resume-research/android-mount-helper/mount-ro'
CA=PRIVATE.parent/'gui-runtime/tls-v2/ca.pem'
SOURCE='/data/local/tmp/im-gui-ca';TARGET='/apex/com.android.conscrypt/cacerts'
DEVICE='/data/local/tmp/im-gui-mount-ro';CAFILE='132339d5.0'
STATE=PRIVATE/'android-state.json'
def adb(*args,check=True):
 r=subprocess.run([ADB,'-s',SERIAL,*map(str,args)],capture_output=True,text=True,timeout=60)
 if check and r.returncode:raise RuntimeError('adb failed: '+r.stdout.strip()+' '+r.stderr.strip())
 return r
def sh(command):return adb('shell',command).stdout.strip()
def save(s):STATE.write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8',newline='\n')
def namespace(pid):return sh('readlink /proc/'+pid+'/ns/mnt')
def mounts(pid):
 lines=sh('cat /proc/'+pid+'/mountinfo').splitlines()
 result=[]
 for line in lines:
  f=line.split();sep=f.index('-')
  result.append({'id':f[0],'root':f[3],'target':f[4],'options':f[5].split(','),'device':f[sep+2],'line':line})
 return result
def target_mounts(pid):return [m for m in mounts(pid) if m['target']==TARGET]
def files(pid):
 return sh(f'nsenter --mount=/proc/{pid}/ns/mnt -- sh -c "cd {TARGET} && sha256sum *"')
def check_identity():
 assert adb('emu','avd','name').stdout.splitlines()[0]=='IMClientSend34'
 assert sh('getprop ro.build.version.sdk')=='34' and sh('getprop ro.product.cpu.abi')=='x86_64'
 assert sh('getenforce')=='Enforcing' and sh('getprop ro.debuggable')=='1'
 assert hashlib.sha256((CA.parent/'ca.der').read_bytes()).hexdigest()=='e61a24364dc95315cbdf10bb6eade27b907ff94adb71bde1c827f93a48ad0de8'
 assert hashlib.sha256(ssl.PEM_cert_to_DER_cert(CA.read_text())).hexdigest()=='e61a24364dc95315cbdf10bb6eade27b907ff94adb71bde1c827f93a48ad0de8'
 assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat('2026-10-04T19:20:46.586064+00:00')
 assert hashlib.sha256(OLD.read_bytes()).hexdigest()=='7f2e3b906d3ef36227d7d56c4c3c1856af7e32103c248d2e8655ef1bbc615577'
 assert hashlib.sha256(Path('tests/clients/gui/android_mount_ro.c').read_bytes()).hexdigest()=='ffe199bd1b9b3700cad0575d0df5f93622cc20311f6e42f2122852894848baba'
def verify_overlay(pid,base,state):
 now=target_mounts(pid);new=[m for m in now if m['id'] not in [x['id'] for x in base['mounts']]]
 if len(new)!=1 or now[-1]!=new[0]:raise RuntimeError('Exact new topmost mount not confirmed')
 m=new[0]
 if m['root']!=base['expectedRoot'] or m['device']!=base['expectedDevice'] or 'ro' not in m['options']:
  raise RuntimeError('New mount source/root/read-only mismatch')
 current=dict(line.split(maxsplit=1)[::-1] for line in files(pid).splitlines())
 original=dict(line.split(maxsplit=1)[::-1] for line in base['files'].splitlines())
 if set(current)!=set(original)|{CAFILE} or any(current[k]!=v for k,v in original.items()) or current[CAFILE]!=state['pemSHA256']:
  raise RuntimeError('Exact preserved CA set mismatch')
 return m
if sys.argv[1]=='install':
 check_identity()
 if STATE.exists():raise RuntimeError('Do not overwrite state')
 if sh(f'test ! -e {SOURCE} && test ! -e {DEVICE} && test ! -e {TARGET}/{CAFILE} && echo ABSENT')!='ABSENT':raise RuntimeError('Owned path/CA collision')
 state={'originalUid':sh('id -u'),'originalSELinux':sh('getenforce'),'originalDebuggable':sh('getprop ro.debuggable'),'pemSHA256':hashlib.sha256(CA.read_bytes()).hexdigest(),'namespaces':{},'attempts':[],'helperPushed':False,'directoryCreated':False}
 save(state)
 adb('root');adb('wait-for-device')
 if sh('id -u')!='0':raise RuntimeError('Root unavailable')
 pids=['1',*sh('pidof zygote64 zygote').split()]
 if len(pids)<2:raise RuntimeError('Zygote missing')
 seen=set()
 for pid in pids:
  ns=namespace(pid)
  if ns in seen:continue
  seen.add(ns);allmounts=mounts(pid)
  ancestor=max([m for m in allmounts if SOURCE==m['target'] or SOURCE.startswith(m['target'].rstrip('/')+'/')],key=lambda m:len(m['target']))
  state['namespaces'][pid]={'namespace':ns,'files':files(pid),'mounts':target_mounts(pid),'expectedRoot':posixpath.normpath(posixpath.join(ancestor['root'],posixpath.relpath(SOURCE,ancestor['target']))),'expectedDevice':ancestor['device']}
  if any(m['target']==TARGET for m in allmounts):raise RuntimeError('Existing target mount requires inspection before operation')
 if len({b['files'] for b in state['namespaces'].values()})!=1:raise RuntimeError('Baseline CA views differ')
 save(state)
 sh(f'mkdir {SOURCE} && cp -a {TARGET}/. {SOURCE}/');state['directoryCreated']=True;save(state)
 adb('push',CA,SOURCE+'/'+CAFILE);sh(f'chmod 644 {SOURCE}/{CAFILE}')
 adb('push',OLD,DEVICE);state['helperPushed']=True;save(state);sh('chmod 700 '+DEVICE)
 if sh('sha256sum '+DEVICE).split()[0]!='7f2e3b906d3ef36227d7d56c4c3c1856af7e32103c248d2e8655ef1bbc615577':raise RuntimeError('Device binary hash mismatch')
 for pid,base in state['namespaces'].items():
  if namespace(pid)!=base['namespace']:raise RuntimeError('Namespace changed')
  state['attempts'].append({'pid':pid,'namespace':base['namespace'],'phase':'registered_before_invoke'});save(state)
  if target_mounts(pid)!=base['mounts']:
   m=verify_overlay(pid,base,state);state['attempts'][-1].update(phase='verified_inherited_owned_overlay',mount=m);save(state);continue
  r=adb('shell',f'nsenter --mount=/proc/{pid}/ns/mnt -- {DEVICE}',check=False)
  state['attempts'][-1].update(stdout=r.stdout,stderr=r.stderr,exit=r.returncode,phase='invoked');save(state)
  print('Helper namespace '+pid+' exit='+str(r.returncode)+' '+r.stdout.strip()+' '+r.stderr.strip(),flush=True)
  if r.returncode:raise RuntimeError('Approved helper rejected; stop and roll back')
  m=verify_overlay(pid,base,state);state['attempts'][-1].update(phase='verified_readonly',mount=m);save(state)
 sh('am force-stop im.platform.client');sh('am start -W -n im.platform.client/.MainActivity')
 app=sh('pidof im.platform.client');appview=files(app)
 if appview!=files(next(iter(state['namespaces']))):raise RuntimeError('Fresh app namespace CA inheritance mismatch')
 state['appPid']=app;state['appNamespace']=namespace(app);state['appMounts']=target_mounts(app);state['result']='PASS readonly overlay/inheritance; default SDK TLS still required';save(state)
 assert sh('getenforce')=='Enforcing'
 print(state['result'])
elif sys.argv[1]=='rollback':
 state=json.loads(STATE.read_text())
 sh('am force-stop im.platform.client')
 for pid,base in reversed(list(state['namespaces'].items())):
  if namespace(pid)!=base['namespace']:raise RuntimeError('Rollback namespace changed; stop')
  now=target_mounts(pid);new=[m for m in now if m['id'] not in [x['id'] for x in base['mounts']]]
  if new:
   if len(new)!=1 or now[-1]!=new[0] or new[0]['root']!=base['expectedRoot'] or new[0]['device']!=base['expectedDevice']:raise RuntimeError('Rollback mount identity mismatch')
   sh(f'nsenter --mount=/proc/{pid}/ns/mnt -- umount {TARGET}')
  if target_mounts(pid)!=base['mounts']:raise RuntimeError('Namespace mounts not restored')
  if files(pid)!=base['files']:raise RuntimeError('Namespace CA baseline differs')
 if state['helperPushed']:sh('rm '+DEVICE)
 if state['directoryCreated']:sh(f'test "{SOURCE}" = /data/local/tmp/im-gui-ca && rm -rf {SOURCE}')
 adb('reverse','--remove','tcp:18443',check=False);adb('reboot');adb('wait-for-device')
 state['rollback']='reboot requested; fresh baseline/SDK rejection/unroot pending';save(state)
 print(state['rollback'])
