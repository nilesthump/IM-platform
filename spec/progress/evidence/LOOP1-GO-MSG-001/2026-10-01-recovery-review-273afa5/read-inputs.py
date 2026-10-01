from pathlib import Path
r=Path('H:/.codex/worktrees/s1-recovery-review-20261001-b')
t=(r/'spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')
for start,end in [(3,4),(10,15)]:
 a=t.index('<a id="section-'+str(start)+'"'); b=t.index('<a id="section-'+str(end)+'"'); print(t[a:b])
for path in sorted((r/'spec/architecture/decisions').glob('*.md')): print(path.read_text(encoding='utf-8'))
for path in ['spec/domain/messaging.md','spec/invariants/messaging.md','spec/acceptance/s0-messaging.md','contracts/websocket/README.md','contracts/websocket/envelope.schema.json','contracts/sync/README.md','contracts/errors/catalog.json','contracts/database/README.md']:
 p=r/path
 if p.exists(): print(path,p.read_text(encoding='utf-8'))
