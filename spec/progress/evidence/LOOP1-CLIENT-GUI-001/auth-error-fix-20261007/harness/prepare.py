from pathlib import Path
import subprocess,json,ssl,hashlib,datetime,socket
P=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix');O=Path('H:/.codex/gui-handoffs/20261007-android-evidence-fix')
for name in ['boot.py','await-boot.py','setup.py','lifecycle.py','rollback-check.py','rollback-tls.py']:
 (P/name).write_text((O/name).read_text(encoding='utf-8').replace('20261007-android-evidence-fix','20261007-auth-error-fix'),encoding='utf-8',newline='\n')
ca=Path('H:/.codex/gui-handoffs/20261004-4f866046/gui-runtime/tls-ui-20261007/ca.pem');der=ssl.PEM_cert_to_DER_cert(ca.read_text())
assert hashlib.sha256(der).hexdigest()=='567914623580f1cf36dcc943794481c0472eac8294d3601818d3de7650a54946';assert hashlib.sha1(der).hexdigest().upper()=='5C2B8129A44043C0912E4CE413B4799570E92733';assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-08T05:05:13+00:00')
assert 'emulator-5590' not in subprocess.check_output(['H:/Android/platform-tools/adb.exe','devices'],text=True)
with socket.socket() as so:so.bind(('127.0.0.1',18443))
(P/'tls-identity.json').write_text(json.dumps({'derSHA256':hashlib.sha256(der).hexdigest(),'sha1Thumbprint':hashlib.sha1(der).hexdigest().upper(),'validUntil':'2026-10-08T05:05:13Z','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'emulator5590Absent':True,'port18443Free':True},indent=2))
print('PASS exact approved CA valid, owned serial absent, endpoint port free; original harness copied to new private scope')