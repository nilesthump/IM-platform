#!/usr/bin/env python3
"""Deterministic shared Go/Java Sync and Plugin API v1 vectors."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
U="10000000-0000-4000-8000-000000000001"; C="30000000-0000-4000-8000-000000000001"; R="40000000-0000-4000-8000-000000000001"; P="60000000-0000-4000-8000-000000000001"
M=lambda n:f"50000000-0000-4000-8000-{n:012d}"
def msg(n): return {"conversationId":C,"seq":n,"messageId":M(n),"senderId":U,"requestId":f"40000000-0000-4000-8000-{n:012d}","createdAt":"2026-09-28T00:00:01Z","content":{"kind":"TEXT","text":f"message-{n}"}}
def user(kind="friend.changed"): return {"syncVersion":"1.0","type":"sync.user.page","requestId":R,"events":[{"eventId":M(9),"cursor":"1","kind":kind,"subjectId":U,"revision":1}],"nextCursor":"1","hasMore":False}
def call(t,n):
    x={"apiVersion":"1.0","type":t,"pluginId":P,"version":"1.0.0"}
    if t=="event.subscribe": x["event"]=n
    if t=="query": x.update(query=n,conversationId=C,pageSize=20,pageToken="")
    if t=="action": x.update(action=n,conversationId=C,requestId=R)
    if t=="ui.host": x["slot"]=n
    return x
def artifact(**changes):
    x={"apiVersion":"1.0","type":"artifact","pluginId":P,"version":"1.0.0","packageHash":"a"*64,"backendHash":"b"*64,"rendererHash":"c"*64,"signature":"fixture-signature","manifestValid":True,"compatible":True,"permissionsApproved":True,"resourceSizeOk":True,"cspValid":True,"entryPointValid":True,"sandbox":"iframe"}
    x.update(changes); return x
cases=[]
def sync_snap(op,last,cursor="0",contiguous=0,messages=None,user_state=None):
    return {"op":op,"cursor":cursor,"contiguous":contiguous,"messages":messages or {},"userState":user_state or {},"last":last}
def add(i,p,r,s,e=None,error=False):
    x={"id":i,"polarity":p,"rules":r,"steps":s}
    if e is not None:x["expect"]=e
    if error:x["expectError"]=True
    cases.append(x)

manifest={"apiVersion":"1.0","type":"manifest","pluginId":P,"version":"1.0.0","capabilities":["events","queries","actions","ui"],"permissions":["event.message.created","query.messages","action.send_message","ui.panel"],"backendEntry":"backend/plugin.wasm","rendererEntry":"ui/render.bundle.js"}
add("manifest-valid","positive",["SP-A-005"],[{"op":"plugin.manifest","manifest":manifest}],{"last":"VALID"})
add("manifest-unknown-capability","negative",["SP-A-005"],[{"op":"plugin.manifest","manifest":dict(manifest,capabilities=["core_db"])}],error=True)
add("manifest-duplicate-permission","negative",["SP-A-005"],[{"op":"plugin.manifest","manifest":dict(manifest,permissions=["query.messages","query.messages"])}],error=True)

add("gap-out-of-order-duplicate","positive",["SP-A-001","SP-A-012"],[{"op":"sync.message","message":msg(n)} for n in (2,2,1)],{"contiguous":2,"messages":{"1":M(1),"2":M(2)},"timeline":[sync_snap("sync.message","APPLIED",messages={"2":M(2)}),sync_snap("sync.message","APPLIED",messages={"2":M(2)}),sync_snap("sync.message","APPLIED",contiguous=2,messages={"1":M(1),"2":M(2)})]})
add("gap-stops","negative",["SP-A-001"],[{"op":"sync.message","message":msg(2)}],{"contiguous":0,"messages":{"2":M(2)}})
add("failed-to-sent-terminal","positive",["SP-A-002"],[{"op":"local.failed","conversationId":C,"requestId":R},{"op":"sync.message","message":msg(1)},{"op":"local.failed","conversationId":C,"requestId":R}],{"local":{C+"/"+R:"SENT"},"last":"SENT"})
add("message-rollback-and-retry","positive",["SP-A-003"],[{"op":"sync.message","message":msg(1),"fault":"before_commit"},{"op":"sync.message","message":msg(1)}],{"contiguous":1,"messages":{"1":M(1)},"timeline":[sync_snap("sync.message","ROLLED_BACK"),sync_snap("sync.message","APPLIED",contiguous=1,messages={"1":M(1)})]})
add("user-rollback-and-retry","positive",["SP-A-003","SP-A-004"],[{"op":"sync.user","page":user(),"fault":"before_commit"},{"op":"sync.user","page":user()}],{"cursor":"1","messages":{},"userState":{"friend.changed/"+U:1},"timeline":[sync_snap("sync.user","ROLLED_BACK"),sync_snap("sync.user","APPLIED",cursor="1",user_state={"friend.changed/"+U:1})]})
for kind in ("friend.changed","conversation.changed","membership.changed","plugin.changed"):
    add("user-"+kind,"positive",["SP-A-004"],[{"op":"sync.user","page":user(kind)}],{"cursor":"1","contiguous":0})
add("message-event-in-user-cursor","negative",["SP-A-004"],[{"op":"sync.user","page":user("message.created")}],error=True)
add("sequence-collision","negative",["SP-A-001"],[{"op":"sync.message","message":msg(1)},{"op":"sync.message","message":dict(msg(1),messageId=M(3))}],error=True)
add("request-identity-collision","negative",["SP-A-001","SP-A-002"],[{"op":"sync.message","message":msg(1)},{"op":"sync.message","message":dict(msg(2),requestId=R)}],error=True)
other="30000000-0000-4000-8000-000000000002"
add("per-conversation-independent-sequence","positive",["SP-A-001","SP-A-012"],[{"op":"sync.message","message":msg(1)},{"op":"sync.message","message":dict(msg(1),conversationId=other,messageId=M(8))}],{"conversations":{C:{"contiguous":1,"messages":{"1":M(1)}},other:{"contiguous":1,"messages":{"1":M(8)}}}})

for t,n,cap,perm in (("event.subscribe","message.created","events","event.message.created"),("query","messages","queries","query.messages"),("action","send_message","actions","action.send_message"),("ui.host","panel","ui","ui.panel")):
    s={"op":"plugin.call","call":call(t,n),"capabilities":[cap],"permissions":[perm],"authorizedAtExecution":True}
    tag=t.replace(".","-")
    add("allow-"+tag,"positive",["SP-A-005","SP-A-012"],[s],{"last":"ALLOWED"})
    add("deny-"+tag+"-capability","negative",["SP-A-005"],[dict(s,capabilities=[])],{"last":"DENIED","sideEffects":0})
    add("deny-"+tag+"-permission","negative",["SP-A-005","SP-A-012"],[dict(s,permissions=[])],{"last":"DENIED","sideEffects":0})
add("deny-direct-core-db","negative",["SP-A-005"],[{"op":"plugin.call","call":call("query","messages"),"capabilities":["queries"],"permissions":["query.messages"],"directAccess":True}],{"last":"DENIED"})
q={"op":"plugin.call","call":call("query","messages"),"capabilities":["queries"],"permissions":["query.messages"]}
add("query-read-only-paginated","positive",["SP-A-006"],[q],{"last":"ALLOWED","sideEffects":0})
add("query-over-limit","negative",["SP-A-006"],[dict(q,call=dict(q["call"],pageSize=101))],{"last":"DENIED"})
add("query-mutation","negative",["SP-A-006"],[dict(q,mutates=True)],{"last":"DENIED","sideEffects":0})
a={"op":"plugin.call","call":call("action","send_message"),"capabilities":["actions"],"permissions":["action.send_message"],"authorizedAtExecution":True}
audit_allowed={"requestId":R,"authorizedAtExecution":True,"outcome":"ALLOWED","sideEffectApplied":True}
audit_retry={"requestId":R,"authorizedAtExecution":True,"outcome":"ALLOWED","sideEffectApplied":False}
audit_denied={"requestId":R,"authorizedAtExecution":False,"outcome":"DENIED","sideEffectApplied":False}
add("action-retry-audited","positive",["SP-A-006","SP-A-013"],[a,a],{"last":"ALLOWED","sideEffects":1,"auditAttempts":2,"auditLog":[audit_allowed,audit_retry]})
add("action-revoked-at-execution","negative",["SP-A-006","SP-A-013"],[a,dict(a,authorizedAtExecution=False)],{"last":"DENIED","sideEffects":1,"auditAttempts":2,"auditLog":[audit_allowed,audit_denied]})

b={"op":"plugin.artifact","artifact":artifact(),"hashValid":True,"signatureValid":True}
add("artifact-verified","positive",["SP-A-007","SP-A-008"],[b],{"last":"VERIFIED"})
for field in ("packageHash","backendHash","rendererHash"):
    add("immutable-"+field,"negative",["SP-A-007"],[b,dict(b,artifact=artifact(**{field:"d"*64}))],{"last":"REJECTED"})
add("artifact-version-split","negative",["SP-A-007"],[dict(b,rendererVersion="2.0.0")],{"last":"REJECTED"})
for label,delta in (("hash",{"hashValid":False}),("signature",{"signatureValid":False}),("manifest",{"artifact":artifact(manifestValid=False)}),("compatibility",{"artifact":artifact(compatible=False)}),("permission",{"artifact":artifact(permissionsApproved=False)}),("size",{"artifact":artifact(resourceSizeOk=False)}),("csp",{"artifact":artifact(cspValid=False)}),("entry",{"artifact":artifact(entryPointValid=False)})):
    add("renderer-reject-"+label,"negative",["SP-A-008"],[dict(b,**delta)],{"last":"REJECTED"})
add("renderer-unsafe-sandbox","negative",["SP-A-008"],[dict(b,artifact=artifact(sandbox="host_native"))],error=True)
add("renderer-bridge-sandbox","positive",["SP-A-008"],[{"op":"plugin.renderer_runtime","sandbox":"iframe","throughBridge":True,"resource":"ui.host"}],{"last":"ALLOWED"})
for resource in ("database","core_internal","server_file","os_resource","arbitrary_network"):
    add("renderer-runtime-deny-"+resource,"negative",["SP-A-008"],[{"op":"plugin.renderer_runtime","sandbox":"iframe","throughBridge":True,"resource":resource}],{"last":"DENIED"})
add("renderer-runtime-deny-unmediated","negative",["SP-A-008"],[{"op":"plugin.renderer_runtime","sandbox":"isolated_webview","throughBridge":False,"resource":"ui.host"}],{"last":"DENIED"})

for resource in ("database","server_file","arbitrary_network","other_plugin_memory"):
    add("wasm-deny-"+resource,"negative",["SP-A-009"],[{"op":"plugin.wasm","resource":resource}],{"last":"DENIED","failureCount":1})
for resource in ("cpu_time","memory","concurrency","storage","network"):
    add("wasm-limit-"+resource,"negative",["SP-A-009"],[{"op":"plugin.wasm","resource":resource,"overLimit":True}],{"last":"DENIED","failureCount":1})
add("wasm-auto-disable","negative",["SP-A-009"],[{"op":"plugin.wasm","timeout":True}]*3,{"last":"AUTO_DISABLED","autoDisabled":True,"failureCount":3})

up={"op":"plugin.upgrade","backendVersion":"2.0.0","rendererVersion":"2.0.0"}
stages=("snapshot","migration","backend_health","renderer_health","atomic_switch")
def upgrade_trace(fail=None):
    trace=[{"stage":s,"oldVersionServed":True} for s in stages[:stages.index(fail)+1] if fail] if fail else [{"stage":s,"oldVersionServed":True} for s in stages]
    if fail: trace.append({"stage":"restore_snapshot","oldVersionServed":True})
    return trace
add("upgrade-atomic-switch","positive",["SP-A-010"],[up],{"last":"SWITCHED","activeVersion":"2.0.0","oldVersionServed":False,"dataPreserved":True,"upgradeTrace":upgrade_trace()})
for stage in ("snapshot","migration","backend_health","renderer_health","atomic_switch"):
    add("upgrade-fail-"+stage,"negative",["SP-A-010"],[dict(up,failAt=stage)],{"last":"ROLLED_BACK","activeVersion":"1.0.0","oldVersionServed":True,"snapshotRestored":True,"dataPreserved":True,"upgradeTrace":upgrade_trace(stage)})
add("upgrade-version-split","negative",["SP-A-007","SP-A-010"],[dict(up,rendererVersion="3.0.0")],{"last":"REJECTED","activeVersion":"1.0.0"})

add("disable-preserves-data","positive",["SP-A-011"],[{"op":"plugin.lifecycle","action":"DISABLE"}],{"last":"DISABLED","dataPreserved":True})
add("uninstall-retained","positive",["SP-A-011"],[{"op":"plugin.lifecycle","action":"UNINSTALL"}],{"last":"RETAINED","dataPreserved":True})
for missing in ("explicit","elevated","audited","retention_confirmed"):
    req={k:True for k in ("explicit","elevated","audited","retention_confirmed")};req[missing]=False
    add("purge-deny-"+missing,"negative",["SP-A-011"],[dict(op="plugin.lifecycle",action="PURGE",**req)],{"last":"DENIED","dataPreserved":True})
add("purge-explicit-authorized","positive",["SP-A-011"],[{"op":"plugin.lifecycle","action":"PURGE","explicit":True,"elevated":True,"audited":True,"retention_confirmed":True}],{"last":"PURGED","dataPreserved":False})

if __name__=="__main__":
    with (HERE/"golden.json").open("w",encoding="utf-8",newline="\n") as target:
        target.write(json.dumps({"fixtureVersion":"1.0","profiles":["go","java"],"cases":cases},indent=2)+"\n")
    print(f"wrote {len(cases)} cases")
