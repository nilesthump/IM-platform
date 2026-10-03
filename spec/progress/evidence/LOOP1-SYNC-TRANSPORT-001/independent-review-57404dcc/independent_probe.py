import runpy,copy,subprocess,pathlib,json
v=runpy.run_path("tools/verify_sync_transport.py"); R="40000000-0000-4000-8000-000000000001"; C="30000000-0000-4000-8000-000000000001"
q=dict(syncVersion="1.0",type="sync.conversation.request",requestId=R,conversationId=C,afterSeq=10**100,limit=10**100)
page=dict(syncVersion="1.0",type="sync.conversation.page",requestId=R,conversationId=C,messages=[],hasMore=False)
v["check_page"]("conversation",q,page); assert q["afterSeq"]==10**100 and q["limit"]==10**100
cases=[dict(q,extra=1),dict(q,requestId="bad"),dict(q,conversationId="bad"),dict(q,syncVersion="2.0"),dict(q,type="sync.user.request")]
cases += [dict(q,afterSeq=x) for x in (True,-1,1.2,"1",None)]
cases += [dict(q,limit=x) for x in (True,0,-1,1.2,"1",None)]
for bad in cases:
 try: v["check_page"]("conversation",bad,page)
 except v["Invalid"]: continue
 raise AssertionError("invalid request accepted: "+repr(bad))
base="a0304fcc7be18b87f5986d014849d6b48b96a071"; paths=subprocess.check_output(["git","diff","--name-only",base+"..HEAD"],text=True).splitlines()
assert not any(x.startswith(("backend/","clients/","contracts/database/")) for x in paths)
old=subprocess.check_output(["git","diff","--name-only","bc1bebb..HEAD","--","spec/progress/evidence/LOOP1-SYNC-001/implementation-research","spec/progress/evidence/LOOP1-SYNC-001/implementation"],text=True); assert not old.strip()
print("PASS independent probe: 16 invalid request cases, huge exact request preserved, no product/schema changes, immutable committed predecessor preserved")
