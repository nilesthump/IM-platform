import subprocess,json,time
from pathlib import Path
r=Path('H:/.codex/evidence/s1-closure-review');t=str(time.time_ns());head='cb2cf431a59e0318a1163073a1c76432135c86d9'
def api(path,name):
 b=subprocess.check_output(['gh','api',path]);(r/(name+'-'+t+'.json')).write_bytes(b);return json.loads(b)
out=[]
for rid,kind in [(36833725670,'push'),(36833732278,'pull_request')]:
 run=api('repos/nilesthump/IM-platform/actions/runs/'+str(rid),kind+'-run');jobs=api('repos/nilesthump/IM-platform/actions/runs/'+str(rid)+'/jobs?per_page=100',kind+'-jobs');assert run['head_sha']==head and run['event']==kind
 req={'classify','architecture','source_go','source_java','gate'} if kind=='push' else {'classify','architecture','source_go','source_java','gate','go','java','web','desktop','mobile','shared','compatibility','deploy'}
 d={j['name']:(j['status'],j['conclusion']) for j in jobs['jobs']};assert set(d)<={'classify','architecture','source_go','source_java','gate','go','java','web','desktop','mobile','shared','compatibility','deploy'}
 ok=all(d.get(n)==('completed','success') for n in req) and all(d[n]==('completed','skipped') for n in set(d)-req)
 out.append({'run':rid,'event':kind,'head':run['head_sha'],'jobs':d,'result':'PASS' if ok else 'PENDING','raw_suffix':t});print(out[-1])
pr=api('repos/nilesthump/IM-platform/pulls/5','pr5');assert pr['head']['sha']==head and pr['base']['sha']=='b442acd26777c481620a6bd917863cebfaf79b35';v=api('repos/nilesthump/IM-platform/git/commits/'+pr['merge_commit_sha'],'virtual-merge');ct=api('repos/nilesthump/IM-platform/git/commits/'+head,'candidate');assert [p['sha'] for p in v['parents']]==[pr['base']['sha'],head] and v['tree']['sha']==ct['tree']['sha'];pr4=api('repos/nilesthump/IM-platform/pulls/4','pr4');assert pr4['state']=='open' and not pr4['merged'];print('PR binding',pr['merge_commit_sha'],v['tree']['sha'],'PR4OPEN')
summary={'runs':out,'binding':{'head':head,'base':pr['base']['sha'],'merge':pr['merge_commit_sha'],'tree':v['tree']['sha']},'result':'PASS' if all(x['result']=='PASS' for x in out) else 'PENDING'};(r/('hosted-summary-'+t+'.json')).write_text(json.dumps(summary,indent=2))

