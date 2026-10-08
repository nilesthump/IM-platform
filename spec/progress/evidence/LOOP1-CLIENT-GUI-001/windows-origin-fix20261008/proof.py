from pathlib import Path
import subprocess,time,json,hashlib
p=Path('H:/.codex/gui-handoffs/20261008-origin-proposal-fix')
a=['H:/go/bin/go.exe','run',str(p/'origin-proof.go')];t=time.monotonic();x=subprocess.run(a,cwd='H:/.codex/worktrees/g/IM-platform/backend/go',capture_output=True);(p/'proof.stdout.txt').write_bytes(x.stdout);(p/'proof.stderr.txt').write_bytes(x.stderr);(p/'proof-result.json').write_text(json.dumps({'argv':a,'cwd':'H:/.codex/worktrees/g/IM-platform/backend/go','exit':x.returncode,'elapsedSeconds':time.monotonic()-t,'stdoutSHA256':hashlib.sha256(x.stdout).hexdigest(),'stderrSHA256':hashlib.sha256(x.stderr).hexdigest()},indent=2));print(x.stdout.decode());print(x.stderr.decode());raise SystemExit(x.returncode)
