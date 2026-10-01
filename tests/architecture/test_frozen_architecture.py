import importlib.util
from pathlib import Path
import tempfile
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('frozen', ROOT/'tools/verify_frozen_architecture.py')
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
DOC = (ROOT/'spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')

class ArchitectureIntegrityTests(unittest.TestCase):
    def test_current_document(self):
        self.assertEqual([], frozen.structural_errors(DOC))

    def test_semantic_negative_controls(self):
        mutations = {
            'unapproved technology permission': ('Agent 没有未授权技术选型权', 'Agent 可以自由选型'),
            'missing Desktop native boundary': ('clients/desktop/src-tauri/**', 'clients/shared/native/**'),
            'Mobile premature framework': ('Mobile = Android + Kotlin + Jetpack Compose', 'Mobile = Flutter'),
            'Web SQLite permission': ('无 SQLite', '允许 SQLite'),
            'missing Mobile TS removal': ('移除 Mobile TypeScript 技术栈', '保留 Mobile TypeScript 技术栈'),
            'historical reverse arrow': ('NATS --> Gateway','NATS --> PG'),
            'missing native chapter': ('## 8. 插件平台架构','## Removed'),
            'missing index entry': ('- [0. 执行摘要](#section-0)','- removed'),
            'missing diagram': ('```mermaid','```text'),
            'wrong session cardinality': ('有效槽位 1 : 0..3','all historic sessions 1 : 0..3'),
            'multiple logical outbox': ('1 : 1 logical message.created','1 : 1+'),
            'early ACK': ('PG-->>Core: COMMIT 成功','PG-->>Core: BEGIN'),
            'gateway bypass': ('Core-->>Gateway: ACK','Core-->>Sender: ACK'),
            'fanout bypass': ('Bus->>Gateway:','Bus->>Receiver:'),
            'business membership in gateway': ('Core->>Core: 校验成员权限与业务规则','Gateway->>Gateway: 校验成员权限与业务规则'),
            'conflated plugin lifecycle': ('subgraph Artifact','subgraph Lifecycle'),
            'review failure closure': ('Failure --> Test','Failure --> Complete'),
            'CI failure closure': ('CI -->|"FAIL"| Failure','CI -->|"FAIL"| Complete'),
            'missing governance trigger': ('Diff --> Rules','Shared --> Rules'),
            'disconnected gate': ('Structure --> Gate','Structure --> Handoff'),
            'old task path': ('backend/go/core/message/**','backend/go/internal/message/**'),
            'lost shared restriction': ('不得反向依赖任何服务包','可反向依赖服务包'),
            'active empty shortcut': ('精确 Current Task ID','若无 active 则选'),
            'lost final stage gate': ('W11-12<br/>Gate PASS','W11-12'),
            'token optional collection': ('token 严禁进入日志或 trace','token 默认不采集'),
        }
        for name,(old,new) in mutations.items():
            with self.subTest(name=name):
                self.assertIn(old,DOC)
                self.assertTrue(frozen.structural_errors(DOC.replace(old,new)), name)

    def test_layout_flexibility_preserves_semantics(self):
        self.assertEqual([], frozen.structural_errors(DOC+'\n```mermaid\nflowchart LR\n  Extra --> Illustration\n```\n'))

    def test_hash_and_provenance_mutations(self):
        # Minimal temporary authority copy; never mutate product or historical tree.
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('spec/architecture','AGENTS.md','spec/handoff/agent-context.md','scalable-distributed-im-architecture.pdf','spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/approval-and-recovery.md','spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md','spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-mobile-kotlin-compose-decision.txt'):
                src=ROOT/name; dst=root/name; dst.parent.mkdir(parents=True,exist_ok=True)
                if src.is_dir(): shutil.copytree(src,dst)
                else: shutil.copyfile(src,dst)
            self.assertEqual([],frozen.verify(root))
            mobile = root/'spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-mobile-kotlin-compose-decision.txt'
            mobile_raw = mobile.read_bytes(); mobile.write_bytes(mobile_raw + b'altered approval')
            self.assertTrue(any('Mobile Human approval' in e for e in frozen.verify(root)))
            mobile.write_bytes(mobile_raw)
            manifest=root/'spec/architecture/baseline.md'; original=manifest.read_bytes()
            manifest.write_text(original.decode('utf-8').replace('semantic_change: `true`','semantic_change: `false`'),encoding='utf-8')
            self.assertTrue(any('semantic_change' in e for e in frozen.verify(root)))
            manifest.write_bytes(original)
            doc=root/'spec/architecture/frozen-architecture.md'; doc.write_bytes(doc.read_bytes()+b'\nunauthorized')
            self.assertTrue(any('SHA-256 mismatch' in e for e in frozen.verify(root)))
            shutil.copyfile(ROOT/'spec/architecture/frozen-architecture.md',doc)
            pdf=root/'scalable-distributed-im-architecture.pdf'; pdf.write_bytes(pdf.read_bytes()+b'x')
            self.assertTrue(any('SHA-256 mismatch' in e for e in frozen.verify(root)))

if __name__=='__main__': unittest.main()
