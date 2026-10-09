import type {LocalMessage,ServerMessage,Committed,RealtimeMessage,State} from '../../../shared/protocol-sdk/src/storage/models.js';
export interface Message extends LocalMessage {state:State;messageId?:string;seq?:bigint;createdAt?:string}
export class MemoryRepository {
  private rows:Message[]=[];
  private cursors=new Map<string,bigint>();
  // This page's realtime window only. It never asserts old history is materialized.
  private starts=new Map<string,bigint>();
  snapshot(c:string):Message[]{return this.rows.filter(m=>m.conversationId===c).map(m=>({...m,content:{...m.content}})).sort((a,b)=>a.seq!==undefined&&b.seq!==undefined?(a.seq<b.seq?-1:a.seq>b.seq?1:0):a.seq!==undefined?-1:b.seq!==undefined?1:0);}
  reset(){this.rows=[];this.cursors.clear();this.starts.clear();}
  after(c:string){return this.cursors.get(c)??0n;}
  hasBaseline(c:string){return this.cursors.has(c);}
  begin(m:LocalMessage){
    const prior=this.rows.find(v=>v.conversationId===m.conversationId&&v.requestId===m.requestId);
    if(prior){if(prior.senderId!==m.senderId||prior.content.text!==m.content.text)throw new Error('Retry identity changed');if(prior.state!=="SENT")prior.state="SENDING";}
    else this.rows.push({...m,content:{...m.content},state:"SENDING"});
  }
  fail(c:string,r:string){const row=this.rows.find(v=>v.conversationId===c&&v.requestId===r);if(row&&row.state!=="SENT")row.state="FAILED";}
  ack(r:string,p:Committed){const row=this.rows.find(v=>v.conversationId===p.conversationId&&v.requestId===r);if(!row)return;this.commit({...row,messageId:p.messageId,seq:p.seq,createdAt:p.createdAt});}
  realtime(r:string,m:RealtimeMessage){this.commit({...m,requestId:r});}
  page(c:string,after:bigint,messages:ServerMessage[]){
    // Validate entire page against the current view before publishing anything.
    let next=after+1n;const draft=new MemoryRepository();draft.rows=this.rows.map(m=>({...m,content:{...m.content}}));draft.cursors=new Map(this.cursors);draft.starts=new Map(this.starts);
    for(const m of messages){if(m.conversationId!==c||BigInt(m.seq)!==next++)throw new Error('Sync gap');draft.commit(m);}
    this.rows=draft.rows;this.cursors=draft.cursors;this.starts=draft.starts;
  }
  private commit(m:ServerMessage){
    const seq=BigInt(m.seq);
    const existing=this.rows.find(v=>v.conversationId===m.conversationId&&v.requestId===m.requestId);
    const collision=this.rows.find(v=>(v.messageId===m.messageId||v.conversationId===m.conversationId&&v.seq===seq)&&v!==existing);
    if(collision||existing&&(existing.senderId!==m.senderId||existing.content.text!==m.content.text||existing.state==="SENT"&&(existing.messageId!==m.messageId||existing.seq!==seq)))throw new Error('Conflicting committed identity');
    const row:Message={...m,content:{...m.content},seq,state:"SENT"};
    if(existing)Object.assign(existing,row);else this.rows.push(row);
    const oldStart=this.starts.get(m.conversationId);const start=oldStart===undefined||seq<oldStart?seq:oldStart;this.starts.set(m.conversationId,start);
    // An earlier late frame expands the live window, exposing any intervening gap.
    // Recompute that window's prefix; never discard the late frame or call this global contiguous_seq.
    let at=start-1n;
    while(this.rows.some(v=>v.conversationId===m.conversationId&&v.seq===at+1n))at++;
    this.cursors.set(m.conversationId,at);
  }
}
