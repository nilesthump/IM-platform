"""Current architecture integrity; historical representation is provenance, not policy.

This bounded checker verifies the native document and specified diagram relationships.
Product source/import/CI-trigger enforcement is the separate remediation stage 3.
"""
import argparse
import hashlib
from pathlib import Path
import re
import subprocess

PDF_SHA = '546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510'
HISTORICAL_MD_SHA = 'ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91'


def section(doc, key):
    match = re.search(r'(?ms)^<a id="' + re.escape(key) + r'"></a>\n(.*?)(?=^<a id="|\Z)', doc)
    return match.group(1) if match else ''


def chapter(doc, number):
    match = re.search(r'(?ms)^## ' + str(number) + r'\. .*?(?=^## |\Z)', doc)
    return match.group() if match else ''


def graph(doc, number):
    return '\n'.join(re.findall(r'(?ms)^```mermaid\n(.*?)^```\s*$', chapter(doc, number)))


def structural_errors(doc):
    errors = []
    def need(ok, message):
        if not ok:
            errors.append(message)
    need(not re.search(r'^## 原 PDF 第 \d+ 页', doc, re.M), 'page-fenced PDF representation is not native Markdown')
    for n in range(22):
        need(bool(chapter(doc, n)), f'missing chapter {n}')
    for letter in 'AB':
        need(bool(re.search(r'^## 附录 ' + letter + r'\. ', doc, re.M)), f'missing appendix {letter}')
    links = re.findall(r'^\s*- \[[^\]]+\]\(#([a-z0-9-]+)\)', doc, re.M)
    anchors = re.findall(r'^<a id="([a-z0-9-]+)"></a>$', doc, re.M)
    need(len(links) == len(set(links)) and len(anchors) == len(set(anchors)), 'duplicate TOC/anchor')
    need(set(links) == set(anchors) and bool(links), 'TOC must map every actual anchor exactly once')
    for key in [f'section-{i}' for i in range(22)] + ['appendix-a', 'appendix-b']:
        need(key in anchors, f'missing required anchor {key}')
    # Bind each required diagram to its chapter; no frozen total figure/table counts.
    for n in (0, 3, 4, 5, 6, 9, 12, 14, 15):
        need(bool(graph(doc, n)), f'missing semantic diagram in chapter {n}')
        need(f'图 {n}-1' in chapter(doc, n), f'missing figure caption in chapter {n}')
    for n in (0, 3):
        g = graph(doc, n)
        for edge in ('Gateway --> Core', 'Core --> PG', 'Core --> NATS', 'NATS --> Gateway'):
            need(edge in g, f'deployment chapter {n} missing {edge}')
        need(not re.search(r'NATS\s*-->\s*PG', g), f'deployment chapter {n} reverses source of truth')
    g = graph(doc, 4)
    need('有效槽位 1 : 0..3' in g, 'Session cardinality must describe active slots')
    need('Message -->|"1 : 1 logical message.created"| Outbox' in g, 'one logical message-created Outbox required')
    g = graph(doc, 5)
    chain = ['Core->>Core: 校验成员权限与业务规则', 'Core->>PG: BEGIN / seq / message / outbox', 'PG-->>Core: COMMIT 成功', 'Core-->>Gateway: ACK = durable commit', 'Gateway-->>Sender: 转发 ACK']
    positions = [g.find(x) for x in chain]
    need(all(x >= 0 for x in positions) and positions == sorted(positions), 'message authorization/commit/ACK sequence invalid')
    for edge in ('Core->>PG: Outbox dispatcher', 'Core->>Bus: dispatcher', 'Bus->>Gateway:', 'Gateway->>Receiver:'):
        need(edge in g, f'message relay missing {edge}')
    need('Core-->>Sender' not in g and 'Bus->>Receiver' not in g, 'message diagram bypasses Gateway')
    g = graph(doc, 9)
    need('subgraph Artifact' in g and 'subgraph Instance' in g and 'Verified -.->' in g, 'artifact and instance lifecycle must remain separate')
    g = graph(doc, 12)
    for edge in ('Review -->|"FAIL"| Failure', 'Failure --> Test', 'Review -->|"PASS"| CI', 'CI -->|"FAIL"| Failure', 'CI -->|"PASS"| Complete'):
        need(edge in g, f'independent review loop missing {edge}')
    need('新独立 Review Agent' in g and '新 Fix Agent' in g and 'Failure --> Complete' not in g, 'failure cannot bypass fresh independent review')
    g = graph(doc, 14)
    for node in ('GoPath', 'JavaPath', 'Shared', 'Rules'):
        need(f'Diff --> {node}' in g, f'CI classification branch {node} missing')
    need('Rules --> Structure' in g and 'Structure --> Gate' in g, 'governance checks disconnected from Gate')
    g = graph(doc, 15)
    for n in range(7):
        need(bool(re.search(r'S' + str(n) + r'\["[^"\n]*<br/>Gate PASS"\]', g)), f'S{n} missing Gate PASS prerequisite')
        if n < 6:
            need(bool(re.search(r'S' + str(n) + r'(?:\["[^"\n]*"\])?\s*-->\s*S' + str(n + 1) + r'\[', g)), f'S{n} progression edge missing')
    c = chapter(doc, 10)
    for n in range(1, 8):
        need(f'**SRC-{n:02}**' in c, f'missing source rule SRC-{n:02}')
    need('MUST NOT' in c and '不得反向依赖任何服务包' in c and '不是架构豁免' in c, 'source restrictions missing')
    c = chapter(doc, 12)
    need('backend/go/internal/' not in c and 'backend/go/core/message/**' in c, 'task example contradicts service ownership')
    need('LOOP1-CI-001' in c and '现已失效' in c, 'bootstrap expiration omitted')
    need('精确 Current Task ID' in chapter(doc, 13) and '若无 active 则选' not in chapter(doc, 13), 'current-task recovery bypass')
    need('token 严禁进入日志或 trace' in chapter(doc, 18), 'token observability prohibition missing')
    for token in ('Agent 没有未授权技术选型权', '未禁止 ≠ 已批准', 'BLOCKED_BY_ARCHITECTURE', 'machine guard'):
        need(token in chapter(doc, 2), 'universal technology selection rule missing: ' + token)
    for token in ('Web = React + TypeScript', 'Desktop = Tauri + React + TypeScript', 'Mobile = Android + Kotlin + Jetpack Compose', '移除 Mobile TypeScript 技术栈', '同一 canonical contracts/fixtures', '不要求直接复用 TypeScript SDK', 'Android Studio emulator', 'Web/Desktop/shared', 'clients/desktop/src-tauri/**', 'Desktop SQLite native boundary 使用 Tauri + SQLx(SQLite)', '不得通过多个独立 tauri-plugin-sql execute() 调用模拟跨调用事务', 'Repository API', 'protocol/model/plugin SDK 仍为 TypeScript', '无 SQLite', '无离线历史加载', 'S2 Gate OPEN', '<!-- client-technology-policy -->'):
        need(token in chapter(doc, 6), 'approved client boundary missing: ' + token)
    need('不等于可自行选型' in chapter(doc, 11), 'backend variation bypasses selection governance')
    return errors


def verify(root, base_commit=''):
    errors = []
    manifest = (root / 'spec/architecture/baseline.md').read_text(encoding='utf-8')
    fields = dict(re.findall(r'^- ([a-z_0-9]+): `([^`]+)`\s*$', manifest, re.M))
    expected = {'version':'v1.1', 'canonical_format':'markdown', 'repository_path':'spec/architecture/frozen-architecture.md', 'previous_canonical_format':'pdf', 'previous_repository_path':'scalable-distributed-im-architecture.pdf', 'previous_sha256':PDF_SHA, 'historical_migration_type':'representation_only', 'historical_semantic_change':'false', 'historical_migration_task_id':'LOOP1-ARCHDOC-001', 'historical_markdown_sha256':HISTORICAL_MD_SHA, 'previous_revision_sha256':'83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e', 'previous_revision_type':'conflict_resolution', 'previous_revision_task_id':'LOOP1-ARCH-REMEDIATION-001', 'previous_revision_adr':'spec/architecture/decisions/ADR-0003-architecture-conflict-resolution.md', 'previous_revision_approval_source':'spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/approval-and-recovery.md', 'revision_type':'human_approved_client_clarification', 'semantic_change':'true', 'revision_task_id':'LOOP1-CLIENT-ARCH-CLARIFICATION-001', 'revision_adr':'spec/architecture/decisions/ADR-0005-client-technology-clarification.md', 'approval_source':'spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md'}
    for key, value in expected.items():
        if fields.get(key) != value:
            errors.append(f'manifest {key} mismatch')
    mobile_source = 'spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-mobile-kotlin-compose-decision.txt'
    if fields.get('mobile_approval_source') != mobile_source or not (root / mobile_source).is_file() or hashlib.sha256((root / mobile_source).read_bytes()).hexdigest() != '1901f6dcd93069a19b6a88f5249858c8017ad36c71d61a109cbbad2ec5e9c061':
        errors.append('Mobile Human approval raw-byte linkage/hash mismatch')
    if fields.get('superseded_preacceptance_candidate_sha256') != 'ac0421074c41589d1d409cc91729953984839aea3c05e805608fcf7677da4f68':
        errors.append('superseded preacceptance candidate lineage mismatch')
    for path_key, hash_key in [('repository_path','sha256'),('previous_repository_path','previous_sha256')]:
        relative = expected[path_key]
        actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        if fields.get(hash_key) != actual:
            errors.append(f'{relative} SHA-256 mismatch actual={actual}')
    doc = (root / expected['repository_path']).read_text(encoding='utf-8')
    errors.extend(structural_errors(doc))
    if '| 版本 | v1.1 |' not in doc:
        errors.append('body version differs from revision')
    for key in ('revision_adr', 'approval_source'):
        if not (root / expected[key]).is_file():
            errors.append(f'missing linked {key}')
    adr = (root / expected['revision_adr']).read_text(encoding='utf-8')
    if 'Human-approved' not in adr or 'semantic_change=true' not in adr or expected['approval_source'] not in adr:
        errors.append('revision ADR approval/semantic/source linkage missing')
    archfiles = {p.name for p in (root/'spec/architecture').glob('*.md')}
    if archfiles != {'README.md','baseline.md','frozen-architecture.md'}:
        errors.append('additional competing canonical Markdown artifact')
    for path in ('AGENTS.md','spec/handoff/agent-context.md'):
        if 'canonical Frozen Architecture Markdown' not in (root/path).read_text(encoding='utf-8'):
            errors.append(f'{path} does not route to canonical Markdown')
    index = (root/'spec/architecture/README.md').read_text(encoding='utf-8')
    if 'historical PDF' not in index or 'ADR-0005' not in index:
        errors.append('resolver lacks historical/current discovery metadata')
    if base_commit:
        for args in (['diff','--name-only',base_commit,'HEAD','--','contracts','backend','clients','plugins'], ['diff','--name-only','--','contracts','backend','clients','plugins'], ['diff','--cached','--name-only','--','contracts','backend','clients','plugins']):
            result = subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True)
            if result.returncode or result.stdout.strip():
                errors.append('product scope changed or base cannot be inspected: ' + result.stdout + result.stderr)
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--base-commit',default='')
    args = parser.parse_args()
    errors = verify(args.root,args.base_commit)
    for error in errors:
        print('FAIL: '+error)
    if errors:
        return 1
    print('PASS: v1.1 current SHA/PDF provenance/ADR and section-bound semantic structure; historical migration semantic_change=false; current revision semantic_change=true')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
