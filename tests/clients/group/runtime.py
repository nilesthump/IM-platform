"""Owned Android real group entry runner; incomplete matrix is explicitly reported."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--serial',required=True);p.add_argument('--capture',action='store_true');p.add_argument('--out',required=True);a=p.parse_args()
 config=json.loads(Path(a.config).read_text(encoding='utf-8-sig'));out=Path(a.out).resolve();assert ROOT not in out.parents and not out.exists();out.mkdir(parents=True)
 assert a.serial==config['serial'] and re.fullmatch(r'emulator-\d+',a.serial)
 adb=[config['adb'],'-s',a.serial];record={'result':'PENDING','scope':'real Android create/member/send entry only, not full GROUP acceptance','serial':a.serial,'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_hashes':{},'commands':[]};private_written=False
 def run(args,timeout=120,data=None):
  begin=time.time();r=subprocess.run(list(map(str,args)),input=data,capture_output=True,timeout=timeout,cwd=ROOT);record['commands'].append({'argv':list(map(str,args)),'exit':r.returncode,'seconds':time.time()-begin})
  if r.returncode:raise RuntimeError('Owned command failed: '+str(args[0])+' exit '+str(r.returncode))
  return r.stdout
 try:
  assert run(adb+['shell','getprop','sys.boot_completed']).strip()==b'1'
  assert config['endpoint']=='https://localhost:8443'
  for path in (ROOT/'clients/mobile/app/src').rglob('*'):
   if path.is_file():record['source_hashes'][path.relative_to(ROOT).as_posix()]=sha(path)
  apks={k:Path(config[k]) for k in ('apk','test_apk')};record['apks']={k:sha(v) for k,v in apks.items()}
  for path in apks.values():assert b'Success' in run(adb+['install','-r',path])
  for package,key in [('im.platform.client','apk'),('im.platform.client.test','test_apk')]:
   installed=run(adb+['shell','pm','path',package]).decode().strip();assert installed.startswith('package:/data/app/') and '\n' not in installed
   assert hashlib.sha256(run(adb+['exec-out','cat',installed[8:]])).hexdigest()==record['apks'][key]
  fixture='files/group-runtime-fixture.json'
  exists=subprocess.run(adb+['shell','run-as','im.platform.client','test','-e',fixture],capture_output=True)
  assert exists.returncode==1,'Refusing to overwrite existing private fixture'
  credentials=json.loads(Path(config['credential_file']).read_text(encoding='utf-8-sig'))
  data=json.dumps({k:{n:credentials[k][n] for n in ('username','password','userId')} for k in ('A','B','C','D')}).encode()
  private_written=True;run(adb+["shell","run-as im.platform.client sh -c 'cat > files/group-runtime-fixture.json'"],data=data)
  raw=run(adb+['shell','am','instrument','-w','-e','runId',out.name,'-e','sourceSHA',record['source_sha'],'im.platform.client.test/im.platform.client.group.GroupRuntimeInstrumentation'],timeout=180)
  (out/'instrumentation.txt').write_bytes(raw)
  if a.capture:
   run(adb+['pull','/sdcard/Android/data/im.platform.client/files/group-runtime/'+out.name,str(out/'captures')])
  assert b'INSTRUMENTATION_RESULT: result=PASS' in raw and b'INSTRUMENTATION_CODE: -1' in raw,'Actual instrumentation failed; see raw evidence'
  record['screenshots']=[{'path':str(x.relative_to(out)),'sha256':sha(x)} for x in out.rglob('*.png')];record['result']='PASS_LOCAL_ENTRY';return 0
 except Exception as error:record['result']='FAIL';record['failure']=type(error).__name__+': '+str(error);return 1
 finally:
  if private_written:
   r=subprocess.run(adb+['shell','run-as','im.platform.client','rm','-f','files/group-runtime-fixture.json'],capture_output=True)
   record['private_cleanup_exit']=r.returncode
   if r.returncode:record['result']='FAIL';record['cleanup_failure']='Owned private fixture removal failed'
  (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8');print(record['result'])
  if record.get('cleanup_failure'):raise RuntimeError(record['cleanup_failure'])
if __name__=='__main__':sys.exit(main())
