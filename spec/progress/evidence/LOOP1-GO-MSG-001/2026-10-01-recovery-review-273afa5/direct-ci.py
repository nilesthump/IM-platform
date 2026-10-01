from pathlib import Path
import subprocess,json,time,concurrent.futures
out=Path('H:/.codex/evidence/s1-recovery-review-20261001-b');runid=36826506799
def api(path,name):
 t=time.monotonic(); p=subprocess.run(['gh','api',path],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (out/(name+'.json')).write_bytes(p.stdout); (out/(name+'.stderr.txt')).write_bytes(p.stderr)
 if p.returncode:raise RuntimeError(name)
 return json.loads(p.stdout),{'command':['gh','api',path],'exit':p.returncode,'elapsed':time.monotonic()-t}
r,rr=api(f'repos/nilesthump/IM-platform/actions/runs/{runid}','hosted-final-run');jobs,jr=api(f'repos/nilesthump/IM-platform/actions/runs/{runid}/jobs?per_page=100','hosted-final-jobs')
assert r['head_sha']=='273afa5eb492e1550119885484a68c85f27e0171' and r['status']=='completed' and r['conclusion']=='success'
def direct(j):
 d,dr=api(f'repos/nilesthump/IM-platform/actions/jobs/{j["id"]}',f'direct-job-{j["id"]}')
 assert d['run_id']==runid and d['status']=='completed' and d['conclusion']=='success' and d['name']==j['name']
 return {'id':d['id'],'name':d['name'],'status':d['status'],'conclusion':d['conclusion'],'steps':d['steps'],'command':dr}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: results=list(ex.map(direct,jobs['jobs']))
assert len(results)==13 and {d['name'] for d in results}=={'classify','architecture','source_go','source_java','go','java','web','desktop','mobile','deploy','compatibility','shared','gate'}
summary={'head':r['head_sha'],'run_id':runid,'event':'push','all13directjobs':'PASS','selection':'new branch empty-tree full tracked diff selects all13 jobs','commands':[rr,jr],'jobs':results,'PR_merge_binding':'N/A no new recovery PR; historical33b binding only33b','result':'PASS'}
(out/'hosted-direct-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print('PASS exact273 push run36826506799 all13 actual directjob completed/success')
