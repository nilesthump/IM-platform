import os, pathlib, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path.cwd() / 'ci'))
from classify import classify, diff_paths, FULL_COMPATIBILITY
from check_gate import JOBS, check
assert {k for k,v in classify(['contracts/http/x.json']).items() if v} == FULL_COMPATIBILITY
assert {k for k,v in classify(['ci/classify.py']).items() if v} == {'deploy'}
for job in JOBS:
    for status in ('failure','cancelled','skipped'):
        outputs={j:'false' for j in (*JOBS,'old_client','plugin','migration')}
        outputs[job]='true'
        needs={j:{'result':'skipped'} for j in JOBS}
        needs['classify']={'result':'success','outputs':outputs}
        needs[job]['result']=status
        try: check(needs)
        except ValueError: pass
        else: raise AssertionError((job,status))
outputs={j:'false' for j in (*JOBS,'old_client','plugin','migration')}
needs={j:{'result':'skipped'} for j in JOBS}
needs['classify']={'result':'success','outputs':outputs}
needs['go']['result']='success'
try: check(needs)
except ValueError: pass
else: raise AssertionError('unselected success')
old=os.getcwd()
with tempfile.TemporaryDirectory() as d:
    try:
        p=pathlib.Path(d)
        def git(*args): return subprocess.check_output(['git','-C',d,*args],stderr=subprocess.DEVNULL,text=True).strip()
        git('init','-q'); git('config','user.name','Review'); git('config','user.email','review@example.invalid')
        (p/'contracts').mkdir(); (p/'docs').mkdir()
        (p/'contracts'/'wire.json').write_text('unique fixture content\n')
        git('add','.'); git('commit','-qm','base'); base=git('rev-parse','HEAD')
        (p/'contracts'/'wire.json').rename(p/'docs'/'wire.json')
        git('add','-A'); git('commit','-qm','rename'); head=git('rev-parse','HEAD')
        os.chdir(d)
        paths=diff_paths(base,head)
        selected=[k for k,v in classify(paths).items() if v]
        print('rename paths=',paths,'selected=',selected)
        if 'compatibility' not in selected: raise AssertionError('renamed-away shared contract bypasses compatibility jobs')
    finally: os.chdir(old)
