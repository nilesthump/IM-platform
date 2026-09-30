from pathlib import Path
import argparse,hashlib,json,subprocess,importlib.util
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args();root=Path(a.root)
def git(*args):return subprocess.check_output(['git','-C',str(root),*args])
head=git('rev-parse','HEAD').decode().strip();assert head=='a09f4fbb1dc497c46c8dc0b8901b0417c534fb2d'
assert not git('status','--porcelain=v1')
protected=git('diff','--name-only','8cd90a7',head,'--','backend','contracts','clients','plugins','scalable-distributed-im-architecture.pdf','spec/architecture/decisions/ADR-0001-*.md','spec/architecture/decisions/ADR-0002-*.md').decode();assert not protected,protected
sp=importlib.util.spec_from_file_location('frozen',root/'tools/verify_frozen_architecture.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)
doc=(root/'spec/architecture/frozen-architecture.md').read_text(encoding='utf-8');assert not f.structural_errors(doc)
# Chapter-specific independent negatives; do not mutate committed product or authority.
for chapter,old,new in [(3,'NATS --> Gateway','NATS --> PG'),(5,'PG-->>Core: COMMIT 成功','PG-->>Core: ACK before COMMIT'),(12,'Review -->|"PASS"| CI','Review -->|"PASS"| Complete'),(14,'Structure --> Gate','Structure --> Detached'),(10,'不得反向依赖任何服务包','允许反向依赖服务包')]:
    text=f.chapter(doc,chapter);assert old in text;mutated=doc.replace(text,text.replace(old,new));assert f.structural_errors(mutated),(chapter,'mutation escaped')
rows=[]
for run in ['R-20260929T183826Z-8cd6416f-9684-4596-bc81-bc6f8ee8ce56','R-20260930T120604Z-82f5344c-b7a0-4876-a454-f4b2bf344fa8']:
    directory=root/'research/runs'/run
    result=subprocess.run([__import__('sys').executable,str(root/'tools/research/recorder.py'),'validate-run','--repo',str(root),'--research-root',str(root/'research'),'--run-id',run],capture_output=True,text=True);assert result.returncode==0,result.stderr
    for e in map(json.loads,(directory/'events.jsonl').read_text(encoding='utf-8').splitlines()):
        if e['event_type']!='command_finished':continue
        data=e['data']
        for stream in ['stdout','stderr']:
            p=directory/data[stream+'_blob'];raw=p.read_bytes();actual=hashlib.sha256(raw).hexdigest();persisted=git('cat-file','blob',f'{head}:{p.relative_to(root).as_posix()}');assert persisted==raw
            match=actual==data[stream+'_sha256']
            if not match:assert p.name=='C-3e0d003f-8661-4322-811e-7a14054a219e.stderr.txt' and actual=='62b9875b8941f1e4ef1c891d9982191906e7658f8e2817178feb24286bc5bdfe' and raw.count(b'\xef\xbf\xbd')==60
            rows.append({'run':run,'path':p.name,'persisted_sha256':actual,'raw_match':match})
assert len(rows)==50 and sum(not r['raw_match'] for r in rows)==1
print(json.dumps({'result':'PASS','head':head,'status':'clean detached checkout','protected_diff':'empty','independent_semantic_negatives':5,'transported_blobs':len(rows),'raw_matches':49,'disclosed_raw_encoding_mismatch':1,'canonical_sha256':hashlib.sha256((root/'spec/architecture/frozen-architecture.md').read_bytes()).hexdigest()},indent=2))
