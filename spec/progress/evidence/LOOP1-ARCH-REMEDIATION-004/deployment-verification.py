import os,secrets,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
with tempfile.TemporaryDirectory(prefix='im-arch4-infra-config-') as d:
    d=Path(d);(d/'config.json').write_bytes((ROOT/'backend/go/config.example.json').read_bytes())
    (d/'pg_password').write_text('local-development-only',encoding='utf-8');(d/'jwt_key').write_text(secrets.token_urlsafe(48),encoding='utf-8')
    env=os.environ.copy();env['IM_GO_CONFIG_DIR']=str(d);env['DOCKER_CONTEXT']='default'
    for profile in ['go','java']:
        subprocess.run(['pwsh','-NoProfile','-File',str(ROOT/'tests/infrastructure/smoke.ps1'),'-Profile',profile],cwd=ROOT,env=env,check=True,timeout=600)
print('PASS: applicable existing Go and Java actual Compose/TLS infrastructure smokes')
