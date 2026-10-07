from pathlib import Path
import subprocess,os,time,json,sys
P=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix');assert not (P/'fixture-stop').exists();assert not (P/'fixture-command').exists()
env=os.environ.copy();env.update(IM_GUI_PRIVATE_RUNTIME='H:/.codex/gui-handoffs/20261004-4f866046/gui-runtime',IM_GUI_TLS_DIR='H:/.codex/gui-handoffs/20261004-4f866046/gui-runtime/tls-ui-20261007',IM_GUI_HTTPS_PORT='18443')
with (P/'fixture.stdout.txt').open('wb') as out,(P/'fixture.stderr.txt').open('wb') as err:
 p=subprocess.Popen([sys.executable,'-Xutf8','-B','tests/clients/gui/go_runtime.py'],env=env,stdin=subprocess.PIPE,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
 public=Path(env['IM_GUI_PRIVATE_RUNTIME'])/('go-'+str(p.pid))/'public.json'
 (P/'fixture-process.json').write_text(json.dumps({'pid':p.pid,'public':str(public),'project':'im-gui-product-20261004-'+str(p.pid)},indent=2))
 try:
  for _ in range(600):
   if p.poll() is not None:raise RuntimeError('Fixture exited before READY')
   if public.exists():break
   time.sleep(.5)
  else:raise RuntimeError('Fixture READY absent')
  (P/'public.json').write_bytes(public.read_bytes());print('READY exact owned project '+str(p.pid),flush=True)
  sent=False
  while not (P/'fixture-stop').exists():
   if p.poll() is not None:raise RuntimeError('Owned fixture exited unexpectedly')
   if (P/'fixture-command').exists() and not sent:
    assert (P/'fixture-command').read_text().strip()=='expire Avery';p.stdin.write(b'expire Avery\n');p.stdin.flush();sent=True
   if sent and 'Applied owned fixture session expiry' in (P/'fixture.stdout.txt').read_text(encoding='utf-8'):(P/'fixture-expiry-applied').touch()
   time.sleep(.2)
 finally:
  if p.poll() is None:p.stdin.write(b'stop\n');p.stdin.flush();p.stdin.close();p.wait(timeout=90)
 print('Owned fixture exit='+str(p.returncode));assert p.returncode==0