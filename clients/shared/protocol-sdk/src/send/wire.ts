// Canonical schema: contracts/websocket/envelope.schema.json. No wire library.
export type ObjectValue = { [key: string]: unknown };
const invalid = (): never => { throw new Error("Invalid WSS frame"); };
export function object(v: unknown, keys: string[]): ObjectValue {
  if (!v || typeof v !== "object" || Array.isArray(v)) return invalid();
  const o = v as ObjectValue;
  if (Object.keys(o).length !== keys.length || keys.some(k => !Object.hasOwn(o,k))) return invalid();
  return o;
}
export function uuid(v: unknown): string {
  if (typeof v !== "string" || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v)) return invalid();
  return v.toLowerCase();
}
export function positive(v: unknown): bigint {
  if (typeof v !== "bigint" || v < 1n) return invalid();
  return v;
}
export function timestamp(v: unknown): string {
  if (typeof v !== "string" || !/^\d{4}-\d\d-\d\d[Tt]\d\d:\d\d:\d\d(?:\.\d+)?(?:[Zz]|[+-]\d\d:\d\d)$/.test(v) || !Number.isFinite(Date.parse(v))) return invalid();
  const date = v.slice(0,10), day = Number(date.slice(8)), month = Number(date.slice(5,7)), year = Number(date.slice(0,4));
  if (month<1 || month>12 || day<1 || day>new Date(Date.UTC(year,month,0)).getUTCDate()) return invalid();
  return v;
}
export function content(v: unknown): {kind: "TEXT"; text: string} {
  const o=object(v,["kind","text"]);
  if(o.kind!=="TEXT" || typeof o.text!=="string" || [...o.text].length<1 || [...o.text].length>4096) return invalid();
  return {kind:"TEXT",text:o.text};
}
// Parse integers before JavaScript Number can round them. Reject duplicate keys,
// exponent/fraction values where the canonical fields require positive integers.
export function parse(raw: string, maxLength=131072): unknown {
  if(raw.length>maxLength) return invalid();
  let at=0, depth=0;
  const whitespace=()=>{ while(/[\x20\t\r\n]/.test(raw[at]??"x")) at++; };
  function string(): string {
    const start=at++;
    while(at<raw.length) {
      if(raw[at]==='"') { at++; try { return JSON.parse(raw.slice(start,at)); } catch { return invalid(); } }
      if(raw[at]==="\\") at++;
      at++;
    }
    return invalid();
  }
  function value(): unknown {
    whitespace(); if(++depth>32) return invalid();
    let out: unknown;
    if(raw[at]==='"') out=string();
    else if(raw[at]==="{") {
      at++; const o: ObjectValue=Object.create(null); whitespace();
      if(raw[at]!=="}") for(;;) {
        whitespace(); if(raw[at]!=='"') return invalid(); const k=string();
        if(Object.hasOwn(o,k)) return invalid(); whitespace(); if(raw[at++]!==":") return invalid(); o[k]=value(); whitespace();
        if(raw[at]!==",") break; at++;
      }
      if(raw[at++]!=="}") return invalid(); out=o;
    } else if(raw[at]==="[") {
      at++; const items: unknown[]=[]; whitespace();
      if(raw[at]!=="]") for(;;) { items.push(value()); whitespace(); if(raw[at]!==",") break; at++; }
      if(raw[at++]!=="]") return invalid(); out=items;
    } else if(raw.startsWith("true",at)) { at+=4; out=true;
    } else if(raw.startsWith("false",at)) { at+=5; out=false;
    } else {
      const number=raw.slice(at).match(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/);
      if(number) { at+=number[0].length; const parts=number[0].toLowerCase().split("e"), exponent=Number(parts[1]??"0");
        const [whole,fraction=""]=parts[0].split("."); const scale=fraction.length-exponent;
        if(!Number.isSafeInteger(exponent) || Math.abs(exponent)>131072) return invalid();
        const digits=BigInt(whole+fraction);
        out=scale<=0?digits*10n**BigInt(-scale):digits%10n**BigInt(scale)===0n?digits/10n**BigInt(scale):Number(number[0]); }
      else return invalid();
    }
    depth--; return out;
  }
  const out=value(); whitespace(); if(at!==raw.length) return invalid(); return out;
}
export interface Frame { type: string; requestId: string; payload: ObjectValue }
const authErrors=["VALIDATION_FAILED","AUTH_TOKEN_INVALID","AUTH_TOKEN_EXPIRED","AUTH_SESSION_REVOKED","AUTH_SESSION_EPOCH_STALE","AUTH_CLIENT_TYPE_MISMATCH","PROTOCOL_VERSION_UNSUPPORTED"];
const messageErrors=["VALIDATION_FAILED","AUTH_REQUIRED","AUTH_SESSION_REVOKED","AUTHORIZATION_DENIED","MESSAGE_REQUEST_CONFLICT","MESSAGE_COMMIT_FAILED"];
export function decode(raw: string): Frame {
  const e=object(parse(raw),["protocolVersion","type","requestId","payload"]);
  if(e.protocolVersion!=="1.0" || typeof e.type!=="string") return invalid();
  const requestId=uuid(e.requestId); let p: ObjectValue;
  function rejected(codes: string[]): ObjectValue {
    const p=object(e.payload,["status","error"]), error=object(p.error,["code","message"]);
    if(p.status!=="rejected" || typeof error.code!=="string" || !codes.includes(error.code) || typeof error.message!=="string" || !error.message) return invalid();
    return p;
  }
  switch(e.type) {
    case "auth.ack":
      if((e.payload as ObjectValue)?.status==="rejected") p=rejected(authErrors);
      else { p=object(e.payload,["status","userId","sessionId","clientType","sessionEpoch"]); if(p.status!=="bound" || typeof p.clientType!=="string" || !["WEB","DESKTOP","MOBILE"].includes(p.clientType)) return invalid(); p.userId=uuid(p.userId); p.sessionId=uuid(p.sessionId); p.sessionEpoch=positive(p.sessionEpoch); }
      break;
    case "message.ack":
      if((e.payload as ObjectValue)?.status==="rejected") p=rejected(messageErrors);
      else { p=object(e.payload,["status","conversationId","messageId","seq","createdAt"]); if(p.status!=="committed") return invalid(); p.conversationId=uuid(p.conversationId); p.messageId=uuid(p.messageId); p.seq=positive(p.seq); p.createdAt=timestamp(p.createdAt); }
      break;
    case "message.created":
      p=object(e.payload,["conversationId","messageId","senderId","seq","createdAt","content"]); p.conversationId=uuid(p.conversationId); p.messageId=uuid(p.messageId); p.senderId=uuid(p.senderId); p.seq=positive(p.seq); p.createdAt=timestamp(p.createdAt); p.content=content(p.content); break;
    case "session.revoked":
      p=object(e.payload,["sessionId","reason"]); p.sessionId=uuid(p.sessionId); if(typeof p.reason!=="string" || !["LOGOUT","REPLACED","REVOKED"].includes(p.reason)) return invalid(); break;
    case "ping": case "pong": p=object(e.payload,[]); break;
    default: return invalid();
  }
  return {type:e.type,requestId,payload:p};
}
export function envelope(type: "auth.bind" | "message.send" | "ping" | "pong", requestId: string, payload: unknown): string {
  return JSON.stringify({protocolVersion:"1.0",type,requestId:uuid(requestId),payload});
}
