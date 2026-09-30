from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zipfile,io
BASE='17f45d0b917159a3380b02a0d0c59ec7c4276597'
RUN='R-20260929T183826Z-8cd6416f-9684-4596-bc81-bc6f8ee8ce56'
root=Path.cwd()
def git(*args):
    return subprocess.run(['git','-c','core.excludesFile=.git/info/exclude',*args],check=True,capture_output=True).stdout
def sha(b): return hashlib.sha256(b).hexdigest()
rows=[]
for e in map(json.loads,(root/'research/runs'/RUN/'events.jsonl').read_text(encoding='utf-8').splitlines()):
    if e['event_type']!='command_finished': continue
    d=e['data']
    assert not d['secret_redaction_applied'], 'Redacted blob requires distinct raw vs persisted validation'
    for stream in ('stdout','stderr'):
        path=f"research/runs/{RUN}/{d[stream+'_blob']}"
        raw=(root/path).read_bytes()
        expected=d[stream+'_sha256']
        # Recorder hashes subprocess raw bytes but persists decode UTF-8(errors=replace).
        raw_match=sha(raw)==expected
        if not raw_match:
            assert path.endswith('C-3e0d003f-8661-4322-811e-7a14054a219e.stderr.txt')
            assert sha(raw)=='62b9875b8941f1e4ef1c891d9982191906e7658f8e2817178feb24286bc5bdfe'
            assert raw.count(b'\xef\xbf\xbd')==60
        old=git('cat-file','blob',f'{BASE}:{path}')
        changed=old!=raw
        if changed: assert old==raw.replace(b'\r\n',b'\n'),(path,'difference beyond normalization')
        row={'path':path,'event_raw_sha256':expected,'event_raw_matches_persisted':raw_match,'working_sha256':sha(raw),'old_commit_sha256':sha(old),'normalization_only':changed}
        if '--candidate' in sys.argv:
            idx=git('cat-file','blob',f':{path}')
            committed=git('cat-file','blob',f'HEAD:{path}')
            assert idx==raw==committed,(path,'index/commit byte mismatch')
            row.update(index_sha256=sha(idx),committed_sha256=sha(committed))
        rows.append(row)
assert sum(r['normalization_only'] for r in rows)==22
result={'base':BASE,'head':git('rev-parse','HEAD').decode().strip(),'blob_count':len(rows),'normalized_blob_count':22,'result':'PASS','rows':rows}
print(json.dumps(result,indent=2))
if '--candidate' in sys.argv:
    # Clean temporary clone of exact committed HEAD, no untracked input or product write.
    with tempfile.TemporaryDirectory(prefix='im-recorder-committed-') as directory:
        exported=Path(directory)
        assert exported.resolve().parent == Path(tempfile.gettempdir()).resolve()
        subprocess.run(['git','clone','--no-hardlinks','--no-checkout',str(root),str(exported)],check=True,capture_output=True)
        subprocess.run(['git','-C',str(exported),'-c','core.autocrlf=false','checkout','--detach',result['head']],check=True,capture_output=True)
        clean=subprocess.run(['git','-C',str(exported),'status','--porcelain'],check=True,capture_output=True).stdout
        assert clean==b'',clean
        print('PASS: clean detached temporary checkout of',result['head'])
        for row in rows: assert sha((exported/row['path']).read_bytes())==row['working_sha256']
        print('PASS: clean committed checkout bytes match all original persisted blob hashes (37 raw matches, 1 disclosed UTF-8 replacement mismatch)')
        command=[sys.executable,str(exported/'tools/research/recorder.py'),'validate-run','--repo',str(exported),'--research-root',str(exported/'research'),'--run-id',RUN]
        completed=subprocess.run(command,capture_output=True,text=True)
        print('clean committed extraction command:',json.dumps(command),'exit:',completed.returncode)
        print(completed.stdout,completed.stderr)
        assert completed.returncode==0
