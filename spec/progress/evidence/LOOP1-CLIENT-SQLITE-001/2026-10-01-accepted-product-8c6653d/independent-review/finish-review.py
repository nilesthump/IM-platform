import json,subprocess,sys
from pathlib import Path
repo=Path('H:/.codex/worktrees/s2-sqlite-fixed-review/IM-platform')
e=Path('H:/.codex/evidence/s2-sqlite-fixed-independent-review-20261001')
base=[sys.executable,'-B',str(repo/'tools/research/recorder.py')]
common=['--repo',str(repo),'--research-root',str(e/'research'),'--run-id','R-SQLITE-FIXED-REVIEW-20261001']
for typ,data in [('instrumentation_warning',{'reason':'Initial mandatory startup reads before Recorder are incomplete pretrace. Two extra unrecorded read-tool attempts after start failed: constrained-language Console.OutputEncoding property (command continued) and quoted Python inline read SyntaxError exit1; corrected external Unicode read script succeeded. These were read tooling errors, not candidate failures; recorder command events all exit0. No raw trace edited.'}),('review_finished',{'result':'PASS','candidate':'8c6653d36051a805ccd576806ffda8a6159edbd3','reviewer':'/root/sqlite_fixed_independent_review','independent':True,'findings':[],'evidence':'fixed-event-probe.dart; native33/1/1; clean Acceptance; governance checks','limitations':'Local bounded review only; exact-head hosted acceptance delegated to Coordinator. Windows4 symlink privilege skips; no device/UI/fullS2 claim.'})]:
 subprocess.run(base+['record-event']+common+['--event-type',typ,'--data-json',json.dumps(data)],cwd=repo,check=True)
finish=subprocess.run(base+['finish-run']+common+['--result','PASS'],cwd=repo,text=True,capture_output=True)
validate=subprocess.run(base+['validate-run']+common,cwd=repo,text=True,capture_output=True)
(e/'recorder-outcome.json').write_text(json.dumps({'finish_exit':finish.returncode,'finish_stdout':finish.stdout,'finish_stderr':finish.stderr,'validation_exit':validate.returncode,'validation_stdout':validate.stdout,'validation_stderr':validate.stderr,'post_finish_boundary':'Report, command ledger and manifest archival occur after finish, no raw event append/edit.'},indent=2),encoding='utf-8')
print(finish.stdout,validate.stdout)
if finish.returncode or validate.returncode: raise SystemExit(1)
