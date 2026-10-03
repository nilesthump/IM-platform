"""Hold only the owned fixture conversation row for a real SENDING screenshot.
No fake ACK, product source change, persisted mutation or host trust change.
"""
from pathlib import Path
import argparse,json,queue,subprocess,threading,time,uuid
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=Path("H:/IM-platform/.git/worktrees/IM-platform3/gui-runtime").resolve()
p=argparse.ArgumentParser();p.add_argument("--public",required=True);p.add_argument("--seconds",type=float,default=8);a=p.parse_args()
public=Path(a.public).resolve()
if not public.is_relative_to(PRIVATE) or public.name!="public.json" or not .5<=a.seconds<=10:raise RuntimeError("Exact owned fixture and bounded duration required")
data=json.loads(public.read_text(encoding="utf-8"));project=data["project"];conversation=str(uuid.UUID(data["conversationId"]))
if not project.startswith("im-gui-product-20261004-") or not project.removeprefix("im-gui-product-20261004-").isdigit():raise RuntimeError("Owned GUI project required")
docker="C:/Program Files/Docker/Docker/resources/bin/docker.exe"
container=project+"-postgres-1"
obj=json.loads(subprocess.check_output([docker,"inspect",container]))[0]
if obj["Config"]["Labels"].get("com.docker.compose.project")!=project or obj["Config"]["Labels"].get("com.docker.compose.service")!="postgres":raise RuntimeError("Owned postgres label mismatch")
argv=[docker,"exec","-i",container,"psql","-U","im","-d","im","-Atq","-v","ON_ERROR_STOP=1"]
process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
started=time.monotonic()
try:
    process.stdin.write("BEGIN;\nSELECT conversation_id FROM conversations WHERE conversation_id='"+conversation+"' FOR UPDATE;\n");process.stdin.flush()
    lines=queue.Queue()
    threading.Thread(target=lambda:lines.put(process.stdout.readline().strip()),daemon=True).start()
    if lines.get(timeout=5)!=conversation:raise RuntimeError("Owned row lock not confirmed")
    print("READY actual owned PostgreSQL row lock; seconds="+str(a.seconds),flush=True)
    time.sleep(a.seconds)
    process.stdin.write("ROLLBACK;\n");process.stdin.flush()
    process.stdin.close();process.stdin=None
    process.communicate(timeout=5)
    if process.returncode:raise RuntimeError("Owned row lock cleanup failed")
    print("PASS actual owned row lock released without persisted mutation; elapsed="+str(round(time.monotonic()-started,3)),flush=True)
finally:
    if process.poll() is None:
        if process.stdin:process.stdin.close();process.stdin=None
        try:process.communicate(timeout=5)
        except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
