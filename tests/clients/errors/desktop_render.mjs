// Actual compiled Messages component; SSR checks renderer invariants only.
import assert from "node:assert/strict";
import {createRequire} from "node:module";
import {resolve} from "node:path";
const require=createRequire(resolve("clients/desktop/package.json"));
const React=require("react"),{renderToStaticMarkup}=require("react-dom/server");
const {Messages}=await import("../../../clients/desktop/dist/desktop/src/ui/components/Messages.js");
const row=["controlled-request","controlled-sender","controlled required body","SENDING",null,null,null];
const render=message=>renderToStaticMarkup(React.createElement(Messages,{s:{selected:"controlled-conversation",session:{userId:"controlled-sender"},offlineAccount:null,groups:[],messages:[message]},retry:async()=>{},run:()=>{}}));
for(const state of ["SENDING","SENT","FAILED"]){const value=[...row];value[3]=state;assert.match(render(value),/controlled required body/);}
const server=[...row];server[0]=null;server[4]="controlled-server-identity";server[3]="SENT";assert.match(render(server),/controlled required body/);
for(const [change,reason] of [[v=>{v[3]="UNKNOWN";},/Unknown message state/],[v=>{v[2]=null;},/Message content missing/],[v=>{v[0]=null;v[4]=null;},/Message identity missing/]]){const invalid=[...row];change(invalid);assert.throws(()=>render(invalid),reason);}
console.log("PASS compiled actual Desktop renderer valid SENDING/SENT/FAILED and nullable ACK fields; unknown state/body/identity fail");
