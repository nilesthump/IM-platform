import importlib.util, tempfile, pathlib, subprocess, os, json
root=pathlib.Path('H:/.codex/worktrees/w/IM-platform')
spec=importlib.util.spec_from_file_location('verifier',root/'tests/clients/web/verify.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
with tempfile.TemporaryDirectory(prefix='web-review-negative-') as tmp:
    r=pathlib.Path(tmp)
    def put(name,value):
        p=r/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(value,encoding='utf-8'); return p
    def git(*args): return subprocess.check_output(['git','-C',str(r),*args],stderr=subprocess.STDOUT).decode().strip()
    def commit():
        git('add','.'); git('-c','user.name=Review control','-c','user.email=review@example.invalid','commit','-qm','review control'); return git('rev-parse','HEAD')
    put('clients/web/.gitkeep',''); put('spec/tasks/backlog/LOOP1-WEB-001.md','status: backlog\nweb_verification_phase: appearance_prerequisite\n'); put('spec/progress/current.md','Current Task: LOOP1-WEB-001\nCurrent Task State: backlog\nExecution Status: APPROVED_PENDING_FREEZE\n')
    git('init','-q'); commit()
    p=put('clients/web/product.ts','export const actual = true;'); product=commit(); p.unlink(); deletion=commit()
    os.environ['GITHUB_ACTIONS']='false'
    calls=[]; result=v.verify(r,runner=lambda command,**kwargs:calls.append(command))
    print(json.dumps({'case':'clean committed product deletion','product_sha':product,'deletion_sha':deletion,'clean':git('status','--porcelain')=='','local_base':v.compared_base(r),'result':result,'calls':calls}))
    assert result=='PREREQUISITE_SKELETON_ONLY','Reproduction unexpectedly blocked'
    event=pathlib.Path(tmp).parent/(pathlib.Path(tmp).name+'-event.json')
    try:
        event.write_text(json.dumps({'before':'0'*40,'after':deletion}),encoding='utf-8')
        os.environ.update(GITHUB_ACTIONS='true',GITHUB_EVENT_NAME='push',GITHUB_EVENT_PATH=str(event))
        calls=[]; result=v.verify(r,runner=lambda command,**kwargs:calls.append(command))
        print(json.dumps({'case':'first push zero before with committed product deletion ancestry','head':deletion,'event_before':'0'*40,'result':result,'calls':calls}))
        assert result=='PREREQUISITE_SKELETON_ONLY'
        event.write_text(json.dumps({'before':product,'after':deletion}),encoding='utf-8')
        try: v.verify(r,runner=lambda command,**kwargs:None)
        except ValueError as e: print('CONTROL regular push product base correctly rejects:',str(e))
        else: raise AssertionError('Regular push control failed to reject')
    finally: event.unlink(missing_ok=True)
