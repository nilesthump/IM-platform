from pathlib import Path
import re,subprocess
ROOT=Path(__file__).resolve().parents[5]
BASE='59dcf34e4538d2f35ccafde8104e860f8cf5cd7a'
def check(doc, specs):
    errors=[]
    def need(ok,msg):
        if not ok: errors.append(msg)
    ids=set(re.findall(r'LOOP1-[A-Z0-9-]+',doc))
    old=subprocess.check_output(['git','show',BASE+':spec/architecture/frozen-architecture.md'],cwd=ROOT,text=True,encoding='utf-8')
    oldids=set(re.findall(r'LOOP1-[A-Z0-9-]+',old))
    oldids.add('LOOP1-CLIENT-UI-ARCH-001') # accepted existing queue ID
    need(ids-oldids=={'LOOP1-CLIENT-GUI-001'},'sole new product planning ID violated')
    for tid in ('LOOP1-CLIENT-GUI-001','LOOP1-WEB-001'):
        need(len(re.findall(r'^\| '+tid+r' \|',doc,re.M))==2,tid+' absent/duplicate in section19 and20')
    expected={'LOOP1-CLIENT-SEND-001':{'LOOP1-CLIENT-SQLITE-001','LOOP1-CLIENT-UI-ARCH-001'},
      'LOOP1-SYNC-001':{'LOOP1-CLIENT-SEND-001'},
      'LOOP1-CLIENT-GUI-001':{'LOOP1-CLIENT-SQLITE-001','LOOP1-CLIENT-UI-ARCH-001','LOOP1-CLIENT-SEND-001','LOOP1-SYNC-001'},
      'LOOP1-WEB-001':{'LOOP1-CLIENT-GUI-001'}}
    table=doc.split('## 20. 后续任务队列与依赖')[1].split('### 20.1')[0]
    for tid,deps in expected.items():
        text=specs[tid]
        section=text.split('# Dependencies')[1].split('# Allowed Paths')[0]
        declared=set(re.findall(r'LOOP1-[A-Z0-9-]+',section))
        need(declared==deps,tid+' queue dependency mismatch')
        row=re.search(r'^\| '+tid+r' \| ([^|]+)\|',table,re.M)
        need(row is not None and set(re.findall(r'LOOP1-[A-Z0-9-]+',row.group(1)))==deps,tid+' canonical dependency mismatch')
        need('status: backlog' in text,tid+' activated prematurely')
    need('v1.1' in doc,'version missing')
    need('Web memory only/no SQLite/no offline history' in doc,'S2 Web gate boundary missing')
    for tid in specs:
        paths=list((ROOT/'spec/tasks').glob('*/'+tid+'.md'))
        need(len(paths)==1 and paths[0].parent.name=='backlog',tid+' queue uniqueness')
    return errors
def main():
    doc=(ROOT/'spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')
    specs={p.stem:p.read_text(encoding='utf-8') for p in (ROOT/'spec/tasks/backlog').glob('*.md')}
    errors=check(doc,specs)
    if errors: raise SystemExit('FAIL: '+str(errors))
    assert check(doc+'\n| LOOP1-CLIENT-SOAK-UI-001 | redundant |',specs),'extra UI ID accepted'
    broken=dict(specs);broken['LOOP1-CLIENT-GUI-001']=broken['LOOP1-CLIENT-GUI-001'].replace('- LOOP1-SYNC-001 (必须独立接受并 done).','')
    assert check(doc,broken),'missing GUI dependency accepted'
    assert check(doc.replace('| LOOP1-WEB-001 | LOOP1-CLIENT-GUI-001 |','| LOOP1-WEB-001 | LOOP1-CLIENT-SEND-001 |'),specs),'wrong canonical Web dependency accepted'
    print('PASS: sole new GUI ID, canonical/queue dependency equality and uniqueness; 3 negative controls rejected')
if __name__=='__main__':main()
