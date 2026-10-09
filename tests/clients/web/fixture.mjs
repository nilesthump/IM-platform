// Isolated HTTPS/WSS protocol fixture. No production runtime dependency.
import https from 'node:https';import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';
export const id=n=>'10000000-0000-4000-8000-'+String(n).padStart(12,'0');
export async function fixture(build,cert,key){
 const alice={userId:id(1),username:'alice',displayName:'Alice Lin'},bob={userId:id(2),username:'bob',displayName:'Bob Chen'},carol={userId:id(7),username:'carol',displayName:'Carol Wu'};
 const session={userId:id(1),sessionId:id(4),clientType:'WEB',sessionEpoch:1,status:'ACTIVE'};
 const auth={session,tokens:{accessToken:'controlled-web-fixture-access',accessTokenExpiresInSeconds:3600,refreshTokenDelivery:'HTTP_ONLY_SECURE_COOKIE'},replacedExistingSession:false};
 const friends=[{user:bob,friendshipId:id(6),directConversationId:id(3)}],messages=[],sockets=new Set();let seq=100;
 const state={mode:'ok',delay:0,sends:[],requests:[],friends,messages,sockets};
 function frame(socket,type,r,p){const b=Buffer.from(JSON.stringify({protocolVersion:'1.0',type,requestId:r,payload:p}));const h=b.length<126?Buffer.from([0x81,b.length]):Buffer.from([0x81,126,b.length>>8,b.length&255]);socket.write(Buffer.concat([h,b]));}
 const server=https.createServer({cert:await fs.readFile(cert),key:await fs.readFile(key)},async(req,res)=>{
  const url=new URL(req.url,'https://localhost');let body='';for await(const b of req)body+=b;
  const p=body?JSON.parse(body):{};if(url.pathname.startsWith('/v1/')){state.requests.push({path:url.pathname,method:req.method,body:p,hasBearer:!!req.headers.authorization,query:url.search});if(state.delay)await new Promise(r=>setTimeout(r,state.delay));
   const json=(v,status=200)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(v));};
   const error=(code,status)=>json({requestId:id(90),error:{code,message:'Controlled fixture response'}},status);
   if(url.pathname==='/v1/auth/login'){if(state.mode==='loginError')return error('AUTH_CREDENTIALS_INVALID',401);res.setHeader('Set-Cookie','__Host-im_refresh=controlled-fixture-cookie; Secure; HttpOnly; Path=/; SameSite=Strict');return json(auth);}
   if(url.pathname==='/v1/auth/refresh/web'){if(!req.headers.cookie?.includes('__Host-im_refresh='))return error('AUTH_REQUIRED',401);return json(auth);}
   if(url.pathname==='/v1/auth/logout'){res.setHeader('Set-Cookie','__Host-im_refresh=; Secure; HttpOnly; Path=/; SameSite=Strict; Max-Age=0');return json({sessionId:id(4),status:'REVOKED'});}
   if(!req.headers.authorization)return error('AUTH_REQUIRED',401);
   if(url.pathname==='/v1/users/me'){if(state.mode==='profileError')return error('REQUEST_FAILED',500);return json({user:alice});}
   if(url.pathname==='/v1/friends'){if(state.mode==='friendsError')return error('REQUEST_FAILED',500);return json({friends:state.mode==='empty'?[]:friends});}
   if(url.pathname==='/v1/users/search'){if(state.mode==='searchError')return error('VALIDATION_FAILED',400);return json({users:url.searchParams.get('username')==='carol'?[carol]:[]});}
   if(url.pathname==='/v1/friends/'+id(7)){friends.push({user:carol,friendshipId:id(8),directConversationId:id(9)});return json({friendshipId:id(8),normalizedPair:{lowUserId:id(1),highUserId:id(7)},directConversationId:id(9),memberUserIds:[id(1),id(7)],created:true},201);}
   if(url.pathname==='/v1/sync/conversation'){if(state.mode==='dropAck')return error('REQUEST_FAILED',500);const selected=messages.filter(m=>m.conversationId===p.conversationId&&m.seq>p.afterSeq).sort((a,b)=>a.seq-b.seq);return json({syncVersion:'1.0',type:'sync.conversation.page',requestId:p.requestId,conversationId:p.conversationId,messages:selected.slice(0,100),hasMore:selected.length>100});}
   return error('VALIDATION_FAILED',400);
  }
  const rel=decodeURIComponent(url.pathname)==='/'?'index.html':decodeURIComponent(url.pathname).slice(1);const target=path.resolve(build,rel);if(!target.startsWith(path.resolve(build)+path.sep)) {res.writeHead(404);return res.end();}
  try{const b=await fs.readFile(target);res.writeHead(200,{'Content-Type':rel.endsWith('.html')?'text/html; charset=utf-8':rel.endsWith('.css')?'text/css':rel.endsWith('.js')||rel.endsWith('.mjs')?'application/javascript':'application/octet-stream','Cache-Control':'no-store'});res.end(b);}catch{res.writeHead(404);res.end();}
 });
 server.on('upgrade',(req,socket)=>{if(req.url!=='/v1/ws'){socket.destroy();return;}const accept=crypto.createHash('sha1').update(req.headers['sec-websocket-key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64');socket.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: '+accept+'\r\n\r\n');sockets.add(socket);socket.on('close',()=>sockets.delete(socket));let input=Buffer.alloc(0);
  socket.on('data',chunk=>{input=Buffer.concat([input,chunk]);for(;;){if(input.length<2)return;const opcode=input[0]&15;let len=input[1]&127,offset=2;if(len===126){if(input.length<4)return;len=input.readUInt16BE(2);offset=4;}if(len===127){socket.destroy();return;}if(!(input[1]&128)||input.length<offset+4+len)return;const mask=input.subarray(offset,offset+4),payload=Buffer.from(input.subarray(offset+4,offset+4+len));input=input.subarray(offset+4+len);for(let i=0;i<len;i++)payload[i]^=mask[i%4];if(opcode===8){socket.end();return;}if(opcode!==1)continue;const f=JSON.parse(payload.toString());
    if(f.type==='auth.bind')frame(socket,'auth.ack',f.requestId,{status:'bound',userId:session.userId,sessionId:session.sessionId,clientType:session.clientType,sessionEpoch:session.sessionEpoch});
    if(f.type==='pong')continue;
    if(f.type==='message.send'){state.sends.push(f);let m=messages.find(m=>m.requestId===f.requestId&&m.conversationId===f.payload.conversationId);if(!m){m={conversationId:f.payload.conversationId,requestId:f.requestId,messageId:crypto.randomUUID(),senderId:alice.userId,seq:++seq,createdAt:new Date().toISOString(),content:f.payload.content};messages.push(m);}if(state.mode==='dropAck')continue;setTimeout(()=>{if(!socket.destroyed)frame(socket,'message.ack',f.requestId,{status:'committed',conversationId:m.conversationId,messageId:m.messageId,seq:m.seq,createdAt:m.createdAt});},state.mode==='slowAck'?800:20);}
  }});
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 return {state,origin:'https://127.0.0.1:'+server.address().port,disconnect(){for(const s of sockets)s.destroy();},expire(){for(const s of sockets)frame(s,'session.revoked',id(88),{sessionId:id(4),reason:'REPLACED'});},async close(){for(const s of sockets)s.destroy();await new Promise(r=>server.close(r));}};
}
