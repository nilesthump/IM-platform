import subprocess,sys,os
py=r"C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
r=r"H:/IM-platform/.git/worktrees/IM-platform5/sync-final-candidate-review/actual-main"
os.environ["PATH"]=os.path.dirname(py)+os.pathsep+os.environ["PATH"]
raise SystemExit(subprocess.call([py,"-X","utf8","-B","tools/research/recorder.py","run-command","--research-root",r,"--run-id","R-ACTUALMAIN-AUDIT","--"]+sys.argv[1:]))
