from pathlib import Path
import json,hashlib,subprocess
p=Path('H:/.codex/gui-handoffs/20261008-gui-actual-main-audit');r=Path('H:/.codex/worktrees/g/IM-platform');src=Path('H:/.codex/gui-handoffs/20261008-ca-native/research/runs/R-GUI-MOBILE-REPAIR-COORD-20261008');dest=p/'merge-originals';dest.mkdir(exist_ok=True)
h=lambda b:hashlib.sha256(b).hexdigest()
raw=src.joinpath('events.jsonl').read_bytes().splitlines(keepends=True);selected=[b for b in raw if json.loads(b)['seq'] in {22,23,25,26,27,28,29,30}];assert len(selected)==8
(dest/'selected-original-events.jsonl').write_bytes(b''.join(selected));events=[json.loads(b) for b in selected];starts={e['data']['command_id']:e['data'] for e in events if e['event_type']=='command_started'};commands=[]
for e in events:
 if e['event_type']!='command_finished':continue
 d=e['data'];assert d['exit_code']==0;cmd=starts[d['command_id']];commands.append({**cmd,**d})
 for k in ('stdout','stderr'):
  s=src/d[k+'_blob'];b=s.read_bytes();assert h(b)==d[k+'_sha256'];(dest/s.name).write_bytes(b)
protection=json.loads((dest/'C-f1b58710-04a4-43a5-a59c-156bf60225a2.stdout.txt').read_bytes());assert protection['enforce_admins']['enabled'] and protection['required_status_checks']['strict'] and protection['required_status_checks']['contexts']==['gate']
merge=next(c for c in commands if 'merge' in c['argv']);assert merge['argv']==['C:/Program Files/GitHub CLI/gh.exe','pr','merge','24','--repo','nilesthump/IM-platform','--merge','--match-head-commit','d37626427b96fc7040280a0fe5a5cda8a700cb16'];assert '--admin' not in merge['argv']
pr=json.loads((dest/'C-91d62b24-1637-48ea-b087-1ddde477178a.stdout.txt').read_bytes());assert pr['state']=='MERGED' and pr['headRefOid']=='d37626427b96fc7040280a0fe5a5cda8a700cb16' and pr['mergeCommit']['oid']=='b14bf1070ba26ac368488e2c6ea15a7936e2de89'
result={'result':'PASS','commands':commands,'strictAndEnforceAdmins':True,'normalMatchedHeadMergeNoAdminFlag':True,'actualMergedSHA':pr['mergeCommit']['oid'],'selectedEventsAreByteExactExtractNotWholeEventStream':True,'sourceRun':'R-GUI-MOBILE-REPAIR-COORD-20261008'};(p/'protected-merge-binding.json').write_text(json.dumps(result,indent=2));print('protected-merge source events and all8 original output blobs verified')
refs=['spec/progress/evidence/LOOP1-CLIENT-GUI-001/final-review20261008/report.md','spec/progress/evidence/LOOP1-CLIENT-GUI-001/win20261008/manifest.json','spec/progress/evidence/LOOP1-CLIENT-GUI-001/win20261008/result.md','spec/architecture/decisions/ADR-0010-windows-tauri-wss-origin.md','spec/architecture/decisions/ADR-0009-client-native-capabilities.md','spec/progress/evidence/LOOP1-CLIENT-GUI-001/mobile-ci-fix20261008/final-bindings.json','spec/progress/evidence/LOOP1-CLIENT-GUI-001/android-review-resume-20261007/final-review/coverage.json','.github/workflows/ci.yml','spec/architecture/frozen-architecture.md','scalable-distributed-im-architecture.pdf']
refdata=[{'path':x,'sha256':h((r/x).read_bytes()),'bytes':(r/x).stat().st_size} for x in refs]
for f in [Path('H:/.codex/gui-handoffs/20261008-mobile-diag-review/report.md'),Path('H:/.codex/gui-handoffs/20261008-mobile-diag-hosted/report.md'),Path('H:/.codex/gui-handoffs/20261008-mobile-diag-hosted/binding-result.json')]:refdata.append({'path':str(f),'sha256':h(f.read_bytes()),'bytes':f.stat().st_size})
(p/'source-reference-bindings.json').write_text(json.dumps(refdata,indent=2))
