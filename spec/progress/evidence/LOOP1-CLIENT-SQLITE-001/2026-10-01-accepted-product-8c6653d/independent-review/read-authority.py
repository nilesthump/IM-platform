from pathlib import Path
s=Path('spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')
for start,end in [('section-3','section-4'),('section-10','section-12'),('section-19','section-20')]:
 print(s[s.index(f'<a id="{start}">'):s.index(f'<a id="{end}">')])
print(s[s.index('<a id="appendix-a">'):])
