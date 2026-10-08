from pathlib import Path
import subprocess, json, hashlib,re
r=Path('H:/.codex/worktrees/g/IM-platform'); out=Path('H:/.codex/gui-handoffs/20261008-gui-actual-main-audit')
sha='b14bf1070ba26ac368488e2c6ea15a7936e2de89'; old='6f21e00f8731020e6344545e1383854a5354b6e9'
def git(*args): return subprocess.check_output(['git',*args],cwd=r).decode()
assert git('rev-parse','HEAD').strip()==sha and not git('status','--porcelain').strip()
path='clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/GuiInstrumentation.kt'
before=git('show',old+':'+path); after=(r/path).read_text()
anchor='    private fun verify(value:Boolean){check(value){"GUI assertion $assertions failed"};assertions++}\n'
helper='    // Compose transitions can leave the accessibility cache on the previous form.\n    private fun actualRoot():AccessibilityNodeInfo?{uiAutomation.clearCache();return uiAutomation.rootInActiveWindow}\n'
assert before.count(anchor)==1
expected=before.replace('uiAutomation.rootInActiveWindow','actualRoot()').replace(anchor,anchor+helper)
assert expected==after,'Unexpected change outside exact observation transformation'
changed=git('diff','--name-only',old,sha).splitlines()
assert all(p==path or p in ['spec/progress/current.md','spec/tasks/review/LOOP1-CLIENT-GUI-001.md'] or p.startswith('spec/progress/evidence/LOOP1-CLIENT-GUI-001/mobile-ci-fix20261008/') for p in changed)
e=r/'spec/progress/evidence/LOOP1-CLIENT-GUI-001/mobile-ci-fix20261008'
checked=0
for manifest,root in [('final-bindings.json',e),('original-bindings.json',e),('after-fix/binding.json',e/'after-fix')]:
 j=json.loads((e/manifest).read_text()); entries=j if isinstance(j,list) else j['files']
 for x in entries:
  f=(root/x['path']).resolve(); assert f.is_relative_to(e.resolve());assert hashlib.sha256(f.read_bytes()).hexdigest()==x['sha256'];checked+=1
b=json.loads((e/'after-fix/binding.json').read_text());assert hashlib.sha256((r/path).read_bytes()).hexdigest()==b['testSourceSHA256']
fail=(e/'reproduced-cache-failure/instrumentation.txt').read_text();assert 'INSTRUMENTATION_RESULT: result=FAIL' in fail and 'INSTRUMENTATION_CODE: 0' in fail
line=next(x for x in fail.splitlines() if 'lookupDiagnostic=' in x);d=json.loads(line.split('lookupDiagnostic=',1)[1]);assert d['phase']=='warm-register-16';assert d['cached']['rootPackage']==d['fresh']['rootPackage']=='im.platform.client'
assert not d['cached']['labels']['Confirm password']['present'];assert d['fresh']['labels']['Confirm password']['present'] and d['fresh']['labels']['Confirm password']['visible']
assert set(d['cached']['labels'])==set(d['fresh']['labels'])=={'Open your workspace','Create your account','Username','Password','Confirm password','New here? Create an account','Already have an account? Sign in'}
for f in sorted((e/'after-fix').glob('no-capture-*.stdout.txt')):
 s=f.read_text(); assert 'assertions=46' in s and 'result=PASS' in s and 'sdkInt=34' in s and 'INSTRUMENTATION_CODE: -1' in s
assert len(list((e/'after-fix').glob('no-capture-*.stdout.txt')))==3
pre=json.loads((e/'reproduced-cache-failure/binding.json').read_text()); assert b['appAPK_SHA256']==pre['apkSHA256']=='6bbcd0bcec1216d9f8239c03c5b8e7e62c7ee3197b0c7aa903c1695200c03d30'
assert json.loads((e/'cleanup.json').read_text())['cleanupPASS'] is True
host=json.loads((e/'hosted-fail/full-pr-completed-fail.json').read_text()); assert host['conclusion']=='failure' and host['headSha']==old
assert not git('diff',old,sha,'--','clients/mobile/app/src/main','clients/desktop','clients/shared','.github/workflows/ci.yml','contracts','spec/architecture').strip()
result={'result':'PASS','reviewedSHA':sha,'baseSHA':old,'changedFiles':len(changed),'verifiedBindingEntries':checked,'operativeRootReadReplacements':before.count('uiAutomation.rootInActiveWindow'),'exactTransformationOnly':True,'allOriginalAssertionsDelaysAndPASSFAILLogicRetained':True,'productWorkflowAuthorityUnchanged':True,'observedPreFixFailureRetained':True,'sameProductAPK':b['appAPK_SHA256'],'sameLocalAPI34ThreeNoCapturePASS46':True,'hostedFailureNotConvertedToPASS':True,'newHostedAcceptanceRequired':True}
(out/'source-evidence-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

