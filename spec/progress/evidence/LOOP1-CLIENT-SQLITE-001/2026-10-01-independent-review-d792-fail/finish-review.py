import json,pathlib,subprocess,sys
repo='H:/.codex/worktrees/s2-sqlite-independent-review/IM-platform'
root='H:/.codex/evidence/s2-sqlite-independent-review-20261001/research'
base=[sys.executable,repo+'/tools/research/recorder.py']
common=['--repo',repo,'--research-root',root,'--run-id','R-SQLITE-REVIEW-20261001']
data={'finding':'P2 user-event identity conflict is accepted, contrary to canonical oracle','review_result':'FAIL','candidate':'d7920b1f504cf77a913e105a3df3a738c211ad28','recorder_limitations':'Startup incomplete prospective_resume. Wrapper parsing exit1 before execution. Direct dart launcher WinError2 created command_started without completion; preserved, not edited. All substantive checks and corrected probes recorded.'}
subprocess.run(base+['record-event']+common+['--event-type','review_result','--data-json',json.dumps(data)],check=False)
subprocess.run(base+['finish-run']+common+['--result','FAIL'],check=False)
subprocess.run(base+['validate-run']+common,check=False)
