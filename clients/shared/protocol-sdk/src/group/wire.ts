// Machine authority: contracts/http/group.openapi.json.
import {object,uuid,timestamp,WireFailure} from '../send/wire.js';
export interface GroupUser {userId:string;username:string;displayName:string}
export interface Member {user:GroupUser;role:'OWNER'|'MEMBER';joinedAt:string}
export interface MemberRow {conversationId:string;kind:'DIRECT'|'GROUP';createdBy:string;createdAt:string;member:Member}
export interface Continuation {afterConversationId:string;afterMemberUserId:string}
export interface GroupResult {requestId:string;conversationId:string;addedMemberUserIds:string[];createdAt:string}
export const start:Readonly<Continuation>=Object.freeze({afterConversationId:'',afterMemberUserId:''});
export function id(v:unknown):string {const s=uuid(v);if(s!==v)throw new WireFailure();return s;}
export function targets(values:readonly string[],actor:string):string[]{
  if(values.length<1||values.length>100)throw new WireFailure();
  const result=[...new Set(values.map(id))].sort();if(result.includes(id(actor)))throw new WireFailure();return result;
}
export function result(value:unknown,requestId:string,actor:string,selected:readonly string[],conversation?:string):GroupResult {
  const p=object(value,['requestId','conversationId','addedMemberUserIds','createdAt']);
  if(id(p.requestId)!==requestId||!Array.isArray(p.addedMemberUserIds))throw new WireFailure();
  const c=id(p.conversationId),added=p.addedMemberUserIds.map(id),expected=targets(selected,actor);
  if(added.length>101||added.some((v,i)=>i>0&&v<=added[i-1]))throw new WireFailure();
  if(conversation){if(c!==conversation||added.some(v=>!expected.includes(v)))throw new WireFailure();}
  else if(JSON.stringify(added)!==JSON.stringify([...expected,actor].sort()))throw new WireFailure();
  return {requestId,conversationId:c,addedMemberUserIds:added,createdAt:timestamp(p.createdAt)};
}
export function row(value:unknown):MemberRow {
  const p=object(value,['conversationId','kind','createdBy','createdAt','member']);
  const m=object(p.member,['user','role','joinedAt']),u=object(m.user,['userId','username','displayName']);
  if((p.kind!=='GROUP'&&p.kind!=='DIRECT')||(m.role!=='OWNER'&&m.role!=='MEMBER')||typeof u.username!=='string'||!/^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$/.test(u.username)||typeof u.displayName!=='string')throw new WireFailure();
  return {conversationId:id(p.conversationId),kind:p.kind,createdBy:id(p.createdBy),createdAt:timestamp(p.createdAt),member:{user:{userId:id(u.userId),username:u.username,displayName:u.displayName},role:m.role,joinedAt:timestamp(m.joinedAt)}};
}
export function page(value:unknown,requestId:string,after:Continuation=start,limit=100):{items:MemberRow[];hasMore:boolean;next:Continuation} {
  const p=object(value,['requestId','items','hasMore','next']),n=object(p.next,['afterConversationId','afterMemberUserId']);
  if(id(p.requestId)!==requestId||!Array.isArray(p.items)||p.items.length>limit||typeof p.hasMore!=='boolean')throw new WireFailure();
  const items=p.items.map(row);let previous=after.afterConversationId+after.afterMemberUserId;const metadata=new Map<string,string>();
  for(const item of items){const key=item.conversationId+item.member.user.userId;if(key<=previous)throw new WireFailure();previous=key;
    const value=JSON.stringify([item.kind,item.createdBy,item.createdAt]),prior=metadata.get(item.conversationId);if(prior!==undefined&&prior!==value)throw new WireFailure();metadata.set(item.conversationId,value);}
  if(p.hasMore){const last=items.at(-1);if(!last||n.afterConversationId!==last.conversationId||n.afterMemberUserId!==last.member.user.userId)throw new WireFailure();}
  else if(n.afterConversationId!==''||n.afterMemberUserId!=='')throw new WireFailure();
  return {items,hasMore:p.hasMore,next:{afterConversationId:n.afterConversationId as string,afterMemberUserId:n.afterMemberUserId as string}};
}