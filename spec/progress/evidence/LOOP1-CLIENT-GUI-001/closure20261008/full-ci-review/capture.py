from pathlib import Path
import subprocess,json,sys,time,hashlib
p=Path('H:/.codex/gui-handoffs/20261008-mobile-diag-hosted');gh='C:/Program Files/GitHub CLI/gh.exe'
def capture(name,args):
 t=time.monotonic(); x=subprocess.run([gh,*args],capture_output=True); (p/(name+'.stdout.txt')).write_bytes(x.stdout);(p/(name+'.stderr.txt')).write_bytes(x.stderr)
 print(json.dumps({'name':name,'exit':x.returncode,'elapsed':round(time.monotonic()-t,3),'bytes':len(x.stdout),'sha256':hashlib.sha256(x.stdout).hexdigest()}));assert x.returncode==0
 return x.stdout
mode=sys.argv[1]
if mode=='initial':
 capture('pr24-initial',['api','repos/nilesthump/IM-platform/pulls/24'])
 capture('classify-pr',['run','view','37737318185','--repo','nilesthump/IM-platform','--job','113179712058','--log'])
 capture('push-initial',['run','view','37737314493','--repo','nilesthump/IM-platform','--json','databaseId,event,status,conclusion,headSha,headBranch,jobs,url,createdAt,updatedAt'])
elif mode=='snapshot':
 for n,id in [('pr',37737318185),('push',37737314493)]:
  b=capture(n+'-'+str(int(time.time())),['run','view',str(id),'--repo','nilesthump/IM-platform','--json','databaseId,event,status,conclusion,headSha,headBranch,jobs,url,createdAt,updatedAt']);d=json.loads(b)
  print(json.dumps({'run':id,'head':d['headSha'],'status':d['status'],'conclusion':d['conclusion'],'jobs':[{k:j[k] for k in ['name','status','conclusion','databaseId']} for j in d['jobs']]}))
if mode=='pushlogs':
 capture('classify-push',['run','view','37737314493','--repo','nilesthump/IM-platform','--job','113179700582','--log'])
 b=capture('mobile-push-PRIVATE',['run','view','37737314493','--repo','nilesthump/IM-platform','--job','113179827622','--log'])
 lines=b.decode(errors='replace').splitlines(); safe=[s for s in lines if 'INSTRUMENTATION_RESULT:' in s and any('INSTRUMENTATION_RESULT: '+k+'=' in s for k in ['assertions','sdkInt','result','captureRun','engine']) or 'INSTRUMENTATION_CODE:' in s or 'Emulator version ' in s or 'API level:' in s]
 (p/'mobile-push-safe-excerpt.txt').write_text('\n'.join(safe)+'\n');print('\n'.join(safe)[-2500:])
if mode=='finallogs':
 capture('classify-pr-final',['run','view','37737318185','--repo','nilesthump/IM-platform','--job','113179712058','--log'])
 b=capture('mobile-pr-PRIVATE',['run','view','37737318185','--repo','nilesthump/IM-platform','--job','113179817908','--log'])
 lines=b.decode(errors='replace').splitlines();safe=[s for s in lines if 'INSTRUMENTATION_RESULT:' in s and any('INSTRUMENTATION_RESULT: '+k+'=' in s for k in ['assertions','sdkInt','result','captureRun','engine']) or 'INSTRUMENTATION_CODE:' in s or 'Emulator version ' in s or 'API level:' in s]
 (p/'mobile-pr-safe-excerpt.txt').write_text('\n'.join(safe)+'\n')
 capture('pr24-final',['pr','view','24','--repo','nilesthump/IM-platform','--json','number,headRefOid,baseRefOid,baseRefName,headRefName,isDraft,state,mergeStateStatus,url'])
 print('full Mobile safe evidence extracted; no whole Mobile log exported')
