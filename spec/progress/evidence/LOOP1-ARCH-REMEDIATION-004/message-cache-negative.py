import os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
with tempfile.TemporaryDirectory(prefix='im-arch4-cache-negative-') as d:
    d=Path(d)
    source=ROOT/'backend/go'
    for p in list(source.rglob('*.go'))+[source/'go.mod',source/'go.sum']:
        q=d/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    p=d/'gateway/gateway.go';s=p.read_text();needle='if h.auth.now().Unix() >= c.bound.ExpiresAt {'
    assert needle in s
    s=s.replace(needle,'_, _ = h.auth.authenticate(r.Context(), c.token)\n'+needle,1);p.write_text(s)
    result=subprocess.run(['go','test','-run','^TestPostgresAuthSessionAndWSS$','-count=1','./tests'],cwd=d,capture_output=True,text=True,encoding='utf-8',timeout=60)
    print(result.stdout);print(result.stderr)
    assert result.returncode!=0 and 'bound operation blocked by PostgreSQL' in result.stdout
    print('PASS: isolated reintroduced message PostgreSQL lookup rejected by actual exclusive-lock behavior control; product bytes unchanged')
