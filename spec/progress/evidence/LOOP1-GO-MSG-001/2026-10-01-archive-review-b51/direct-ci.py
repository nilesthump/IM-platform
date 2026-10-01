from pathlib import Path
import subprocess,json,time,concurrent.futures
from review import OUT
runid=36828991394
ledger=[]
def api(path,name):
 t=time.monotonic();p=subprocess.run(['gh','api',path],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (OUT/(name+'.json')).write_bytes(p.stdout);(OUT/(name+'.stderr.txt')).write_bytes(p.stderr)
 row=dict(argv=['gh','api',path],exit=p.returncode,elapsed=time.monotonic()-t);ledger.append(row)
 if p.returncode:raise RuntimeError(name)
 return json.loads(p.stdout)
r=api(f'repos/nilesthump/IM-platform/actions/runs/{runid}','hosted-final-run');jobs=api(f'repos/nilesthump/IM-platform/actions/runs/{runid}/jobs?per_page=100','hosted-final-jobs')
assert r['head_sha']=='b51e62a529ad0f06f31828f49a77734ea2ca010c' and r['event']=='push' and r['status']=='completed' and r['conclusion']=='success'
required={'classify','architecture','source_go','source_java','gate'};expected={'classify','architecture','source_go','source_java','go','java','web','desktop','mobile','deploy','compatibility','shared','gate'}
assert len(jobs['jobs'])==13 and {j['name'] for j in jobs['jobs']}==expected
def direct(j):
 d=api(f'repos/nilesthump/IM-platform/actions/jobs/{j["id"]}',f'direct-job-{j["id"]}')
 assert d['run_id']==runid and d['status']=='completed' and d['name']==j['name']
 assert d['conclusion']==('success' if d['name'] in required else 'skipped')
 return dict(id=d['id'],name=d['name'],status=d['status'],conclusion=d['conclusion'],steps=d['steps'])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(direct,jobs['jobs']))
summary=dict(result='PASS',head=r['head_sha'],run_id=runid,event=r['event'],actual_job_conclusions='5 required SUCCESS / 8 correctly inactive SKIPPED',diff_base='273afa5eb492e1550119885484a68c85f27e0171',diff_head=r['head_sha'],classification='architecture/source_go/source_java true; all other matrix jobs false, independently recomputed from exact diff',jobs=results,commands=ledger,PR_binding='N/A no new candidate PR; historical PR4 binding does not extend')
(OUT/'hosted-direct-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print('PASS exactb51 push36828991394 5requiredSUCCESS / 8correctSKIPS all13directAPIs')
