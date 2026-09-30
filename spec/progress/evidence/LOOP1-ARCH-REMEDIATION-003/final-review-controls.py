"""Independent disposable controls; never alters reviewed checkout."""
import sys,importlib.util,tempfile,shutil,json,subprocess,time
from pathlib import Path
root=Path(sys.argv[1]);sys.dont_write_bytecode=True
sys.path.insert(0,str(root))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,root/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=load('independent_checker','ci/check_architecture.py');cl=load('independent_classifier','ci/classify.py');gate=load('independent_gate','ci/check_gate.py')
workflow=(root/'.github/workflows/ci.yml').read_text(encoding='utf-8')
for path in ['tools/verify_frozen_architecture.py','tools/verify-loop1-min-001.ps1','spec/acceptance/s1.md','spec/tasks/TASK_TEMPLATE.md','backend/go/removed.go']:
 matrix=cl.classify([path]);assert matrix['architecture'] and matrix['source_go'],path
for mutation in [workflow.replace('python3 ci/check_gate.py','python3 ci/check_gate.py || true'),workflow.replace('  classify:\n','  classify:\n    continue-on-error: true\n'),workflow.replace('  pull_request:','  pull_request:\n    paths-ignore: [spec/**]'),workflow.replace('    if: always()','    if: false')]:
 assert c.check_workflow(mutation)
needs={'classify':{'result':'success','outputs':{x:'true' for x in gate.JOBS}}};needs['classify']['outputs'].update({x:'false' for x in ('old_client','plugin','migration')});needs.update({x:{'result':'success'} for x in gate.JOBS});gate.check(needs)
for result in ('skipped','failure','cancelled'):
 needs['source_go']['result']=result
 try:gate.check(needs)
 except ValueError:pass
 else:raise AssertionError(result)
needs['source_go']['result']='success';del needs['architecture']
try:gate.check(needs)
except ValueError:pass
else:raise AssertionError('missing job')
with tempfile.TemporaryDirectory() as tmp:
 r=Path(tmp)
 def put(path,text):
  p=r/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
 for path in ['AGENTS.md','CLAUDE.md','spec/handoff/agent-context.md','spec/tasks/TASK_TEMPLATE.md','spec/governance/execution-boundaries.md','spec/governance/independent-review.md','.github/workflows/ci.yml']:put(path,(root/path).read_text(encoding='utf-8'))
 for scope,bad in [('backend/go/internal/renamed/**',True),('backend/go/core/session/**',False)]:
  put('spec/tasks/active/T.md','# Inputs\nspec/architecture/README.md SRC-01 allowed_paths\n# Allowed Paths\n- '+scope+'\n# Goal\nTest\n');assert bool(c.check_governance(r))==bad
 put('backend/java/core/X.java','package im.core; public class X {public static void start(){}}')
 put('backend/java/Main.java','public class Main {public static void main(String[] args){bootSomething();} static void bootSomething(){im.core.X.start();}}')
 put('backend/java/shared/Connector.java','package im.shared; import java.sql.Connection; import java.sql.DriverManager; public class Connector {static Connection open(String u)throws Exception{return DriverManager.getConnection(u);}}')
 put('backend/java/gateway/R.java','package im.gateway; import java.sql.Connection; public class R {void read(Connection db)throws Exception{db.prepareStatement("SELECT session_epoch FROM sessions").executeQuery();}}')
 assert not c.check_java(r)[0]
 for location,operation in [('gateway','db.prepareStatement(q).execute()'),('shared','db.prepareStatement(q).executeQuery()'),('gateway','db.commit()'),('shared','db.rollback()'),('gateway','db.setAutoCommit(false)')]:
  put('backend/java/'+location+'/Bad.java','package im.'+location+'; import java.sql.Connection; public class Bad {void arbitrary(Connection db,String q)throws Exception{String unrelated="SELECT session_epoch FROM sessions";'+operation+';}}');assert c.check_java(r)[0],operation;(r/('backend/java/'+location+'/Bad.java')).unlink()
 put('backend/go/go.mod','module review.test\n\ngo 1.23.0\n');put('backend/go/core/x.go','package core\nfunc Start(){}\n');put('backend/go/main.go','package main\nimport "review.test/core"\nfunc main(){bootSomething()}\nfunc bootSomething(){core.Start()}\n');assert not c.check_go(r)[0]
 put('backend/go/shared/disguised.go','//go:build never\n\npackage shared\nimport renamed "review.test/core"\nfunc Nothing(){renamed.Start()}\n');assert any('reverse dependency' in x for x in c.check_go(r)[0])
 put('backend/go/gateway/other.go','package gateway\nimport "review.test/core"\nfunc Nothing(){core.Start()}\n');assert any('directly depends' in x for x in c.check_go(r)[0])
 put('backend/go/arbitrary.go','package main\nfunc Nothing(){}\n');assert any('outside exact root whitelist' in x for x in c.check_go(r)[0])
errors,graph=c.check_go(root);assert len(set(errors))==72;assert graph
assert not c.check_java(root)[0];assert not c.check_governance(root)
protected=subprocess.check_output(['git','diff','--name-only','c0373ab', 'HEAD','--','backend','contracts','spec/architecture','scalable-distributed-im-architecture.pdf'],cwd=root,text=True);assert not protected,protected
assert subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)==''
print('PASS: independent six-class positive/negative controls; protected tree unchanged; expected real Go FAIL72; Java/governance PASS; clean exact candidate preserved')
