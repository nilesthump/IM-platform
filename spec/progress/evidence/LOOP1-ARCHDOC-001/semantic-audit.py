from pathlib import Path
import re
import subprocess
import sys
import hashlib

root=Path(__file__).resolve().parents[4]
pdf=root/"scalable-distributed-im-architecture.pdf"
md=root/"spec/architecture/frozen-architecture.md"
old=subprocess.check_output(["git","show","5f117a41bf2f906fcb0f490e0f87352ad19aadb7:spec/architecture/frozen-architecture.md"],cwd=root).decode("utf-8")
fence=chr(96)*3
pattern=r"## 原 PDF 第 (\d+) 页\n\n"+re.escape(fence)+r"text\n(.*?)\n"+re.escape(fence)
blocks=re.findall(pattern,old,re.S)
assert len(blocks)==28,len(blocks)
text=subprocess.check_output(["pdftotext","-layout","-enc","UTF-8",str(pdf),"-"]).decode("utf-8").replace("\r\n","\n")
pages=text.split("\f")
if pages[-1]=="":pages.pop()
assert len(pages)==28,len(pages)
for i,((number,body),page) in enumerate(zip(blocks,pages),1):
    assert int(number)==i
    assert body.rstrip("\n")==page.rstrip("\n"),f"PDF text mismatch page {i}"
print("PDF extraction 28/28 exact against preserved reviewed candidate")
new=md.read_text(encoding="utf-8")
links=re.findall(r"\]\(#(section-[0-9-]+|appendix-[ab])\)",new)
anchors=re.findall(r'<a id="(section-[0-9-]+|appendix-[ab])"></a>',new)
assert len(links)==len(anchors)==86
assert set(links)==set(anchors)
assert len(re.findall(r"^"+re.escape(fence)+r"mermaid$",new,re.M))==9
assert len(re.findall(r"^## 原 PDF 第 ",new,re.M))==0
assert len(re.findall(r"^\| [^|]+ \|",new,re.M))>=100
assert new.count("NATS --> PG")==2
for fig in ("0-1","3-1","4-1","5-1","6-1","9-1","12-1","14-1","15-1"):
    assert new.count("图 "+fig)>=1,fig
for term in ("MUST NOT","MUST","SHOULD","MAY","5000 authenticated WSS users","8C / 16GB / 3TB",
             "UNIQUE(conversation_id, request_id)","ACK-before-commit = 0","SENDING/SENT/FAILED",
             "10/50/200/500","LOOP1-CONTRACT-001","LOOP1-CLIENT-SQLITE-001",
             "LOOP1-RC-001","Appendix"):
    if term=="Appendix":continue
    assert term in new,term
print("Native Markdown: 86 jump targets, 25 tables, nine figures, key strength/numeric/task tokens present")
print("PDF sha256",hashlib.sha256(pdf.read_bytes()).hexdigest())
print("Markdown sha256",hashlib.sha256(md.read_bytes()).hexdigest())
