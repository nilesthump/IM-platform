import pathlib,json,subprocess,hashlib,re
root=pathlib.Path.cwd()
def git(*args, cwd=root):
 p=subprocess.run(['git',*args],cwd=cwd,capture_output=True,text=True,encoding='utf-8'); assert p.returncode==0,(args,p.stderr); return p.stdout
sha=git('rev-parse','HEAD').strip(); status=git('status','--porcelain=v1'); assert not status
print('SUBJECT',sha,'BRANCH',git('branch','--show-current').strip(),'CLEAN',not status)
print('DIFF_RANGE 279c1dc4681683e2af3b3534a00e5222dde36be6..'+sha)
changed=git('diff','--name-only','279c1dc..HEAD').splitlines();print('CHANGED',json.dumps(changed))
assert not any(p.startswith(('backend/','contracts/','ci/','.github/','tools/')) for p in changed)
for p,h in [('spec/architecture/frozen-architecture.md','83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e'),('scalable-distributed-im-architecture.pdf','546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510')]:
 actual=hashlib.sha256((root/p).read_bytes()).hexdigest();assert actual==h;print('HASH',p,actual)
o=json.loads((root/'contracts/http/auth-user-friend.openapi.json').read_text()); op=o['paths']['/v1/friends/{friendUserId}']['put']; print('BEARER',json.dumps(o['components']['securitySchemes']['bearerAuth']));print('PUT_INPUT',json.dumps({k:op.get(k) for k in ['security','parameters','requestBody']}));assert 'requestBody' not in op
n=json.loads((root/'contracts/fixtures/auth-user-friend/negative.json').read_text()); fx=next(x for x in n['fixtures'] if x['id']=='friend-add-authorization-denied') if 'fixtures' in n else next(x for x in n['scenarios'] if x['id']=='friend-add-authorization-denied');print('NEGATIVE403',json.dumps(fx))
files=git('ls-files','contracts','spec/architecture/decisions','spec/domain','spec/invariants','spec/acceptance').splitlines()
semantic=[]
for f in files:
 if f.endswith(('.md','.json','.sql')) and not any(x in f for x in ['validator','openapi-3.1-2026','fixtures/sync-plugin','plugin-api/v1.schema']):
  text=(root/f).read_text(encoding='utf-8');
  for i,line in enumerate(text.splitlines(),1):
   if re.search(r'insufficient.scope|authoriz|ownership|principal|permission|scope|user_id, session_id',line,re.I):semantic.append(f'{f}:{i}: {line.strip()}')
print('PRIMARY_CONTEXT_SEARCH',json.dumps(semantic,ensure_ascii=False))
base=root/'spec/progress/evidence/LOOP1-REMEDIATION-INTEGRATION-001'; manifest=json.loads((base/'closure-evidence-transport.json').read_text())
for item in manifest['files']:
 data=git('show','HEAD:'+str((base/item['file']).relative_to(root)).replace('\\','/')).encode('utf-8');actual=hashlib.sha256(data).hexdigest();assert actual==item['archived_lf_sha256'],item;print('TRANSPORT_HASH_PASS',item['file'],actual)
for name in ['hosted-36763289936-summary.json','hosted-36764254107-summary.json']:
 summary=json.loads((base/name).read_text());print('ARCHIVED_CI',name,json.dumps(summary))
old=pathlib.Path('H:/.codex/worktrees/loop1-s1/IM-platform')
for f in ['backend/go/social.go','backend/go/social_test.go','spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-09-30-implementation-handoff.md']:
 text=git('show','2a6eaa1:'+f,cwd=old) if f.startswith('backend/') else git('show','5b35735:'+f,cwd=old)
 print('OLD_TRACKED',f,'SHA256',hashlib.sha256(text.encode()).hexdigest())
 for i,line in enumerate(text.splitlines(),1):
  if re.search(r'403|scope|authoriz|func \(s \*authService\)|func Test|package main',line,re.I):print(f'OLDREF {f}:{i}: {line.strip()}')
print('FINAL_CLEAN',not git('status','--porcelain=v1'));print('CONTROL_PROOF_PASS; SOCIAL403_UNEXECUTED_UNRESOLVED')
