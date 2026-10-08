from pathlib import Path
import sqlite3,json,sys,datetime
p=Path(sys.argv[1]);phase=sys.argv[2]
if p.name!='im-4dada728-e56b-48a0-a84c-d8ae88507adc.sqlite' or phase not in ('sent','sending','failed','retried','reconnected'):raise RuntimeError('Controlled database identity/phase mismatch')
con=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True,timeout=5);con.row_factory=sqlite3.Row
try:
 rows=[dict(r) for r in con.execute('SELECT request_id,sender_id,content,state,server_message_id,server_seq,server_time FROM messages WHERE conversation_id=? AND sender_id=? AND content IN (?,?) ORDER BY local_id',('3511b34b-4d5d-46e9-a32e-e936eca78fce','4dada728-e56b-48a0-a84c-d8ae88507adc','Windows native SEND 20261008-1220-owned-79ec62c','Windows native RETRY 20261008-1222-owned-79ec62c'))]
 prefix=con.execute('SELECT contiguous_seq FROM conversations WHERE conversation_id=?',('3511b34b-4d5d-46e9-a32e-e936eca78fce',)).fetchone()
 cursor=con.execute('SELECT cursor FROM user_cursor WHERE singleton=1').fetchone()
 result={'time':datetime.datetime.now().astimezone().isoformat(),'phase':phase,'physical_read_only':True,'only_controlled_account_conversation_messages':True,'rows':rows,'contiguous_seq':prefix[0] if prefix else None,'user_cursor':cursor[0] if cursor else None,'database_basename':p.name}
 Path('H:/.codex/gui-handoffs/20261008-ca-desktop/sqlite-'+phase+'.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print('Read-only controlled native SQLite snapshot saved')
finally:con.close()
