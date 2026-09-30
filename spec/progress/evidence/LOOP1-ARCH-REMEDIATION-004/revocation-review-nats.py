import os,sys,tempfile,subprocess,importlib.util
from pathlib import Path
r=Path(sys.argv[1]);os.chdir(r);os.environ['DOCKER_CONTEXT']='default'
s=importlib.util.spec_from_file_location('roles',r/'tests/go/live_role_smoke.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.PORT=19450
observer="""import socket,json
s=socket.create_connection(('nats',4222),timeout=30);s.settimeout(30);f=s.makefile('rb');assert f.readline().startswith(b'INFO ')
s.sendall(b'CONNECT {}\\r\\nSUB session.revoked 1\\r\\nPING\\r\\n')
while f.readline().strip()!=b'PONG':pass
print('READY',flush=True)
reasons=[]
while len(reasons)<2:
 line=f.readline().strip()
 if line==b'PING':s.sendall(b'PONG\\r\\n');continue
 if not line.startswith(b'MSG '):continue
 size=int(line.split()[-1]);data=f.read(size);assert f.read(2)==b'\\r\\n'
 v=json.loads(data);assert v['reason'] in ('REPLACED','LOGOUT');reasons.append(v['reason'])
 print('NATS observed '+v['reason'],flush=True)
assert reasons==['REPLACED','LOGOUT'],reasons
s.close()
"""
with tempfile.TemporaryDirectory(prefix='independent-nats-observer-') as d:
 p=Path(d)/'observe.py';p.write_text(observer,encoding='utf-8');proc=None;name='im-independent-nats-'+str(os.getpid())
 original=m.call
 def call(*a,**kw):
  global proc
  if proc is None:
   proc=subprocess.Popen(['docker','run','--rm','--name',name,'--network','im-arch4-live-'+str(os.getpid())+'_default','-v',d+':/review','python:3.12-alpine','python','-u','/review/observe.py'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
   assert proc.stdout.readline().strip()=='READY','NATS observer not ready'
  return original(*a,**kw)
 m.call=call
 try:
  m.main()
  out,err=proc.communicate(timeout=40);print(out);print(err);assert proc.returncode==0
  assert 'NATS observed REPLACED' in out and 'NATS observed LOGOUT' in out
  print('PASS independent raw NATS subscription observed real CoreOutbox notifications alongside actual three-role TLS/WSS smoke')
 finally:
  if proc and proc.poll() is None:
   subprocess.run(['docker','rm','-f',name],check=True);proc.wait(timeout=30)
