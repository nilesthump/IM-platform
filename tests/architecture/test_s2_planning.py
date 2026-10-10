import importlib.util
import hashlib
import json
import os
import subprocess
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('s2_controls', ROOT/'ci/check_s2_planning.py')
checker = importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)


class SupplementControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT/'spec/tasks', self.root/'spec/tasks')
        for p in ['spec/architecture/baseline.md', 'spec/architecture/frozen-architecture.md', checker.ADR, checker.APPROVAL]:
            out = self.root/p; out.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/p, out)
        self.put('spec/progress/current.md', 'Current Gate: S2\nGate Status: OPEN\n')

    def put(self, p, text):
        out = self.root/p; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text, encoding='utf8'); return out

    def path(self, task):
        paths = list((self.root/'spec/tasks').glob('*/'+task+'.md')); self.assertEqual(1, len(paths)); return paths[0]

    def move(self, task, queue):
        p = self.path(task); text = re.sub(r'(?m)^status: \w+$', 'status: '+queue, p.read_text(encoding='utf8'))
        if task in checker.NEW:
            phase = 'planned' if queue == 'backlog' else checker.PHASES[task]
            text = re.sub(r'(?m)^client_supplement_phase: \w+$', 'client_supplement_phase: '+phase, text)
        p.unlink(); return self.put('spec/tasks/'+queue+'/'+task+'.md', text)

    def accepted(self, task):
        p = self.move(task, 'done'); text = p.read_text(encoding='utf8')
        # Deliberately simulated independent facts, used only in isolated negative fixtures.
        values = {'acceptance_result':'PASS','accepted_candidate_sha':'1'*40,'integrated_main_sha':'2'*40,'main_sync_result':'PASS'}
        for key in ('independent_review_evidence','hosted_acceptance_evidence','main_sync_evidence'):
            value = f'spec/progress/evidence/{task}/fixture-{key}.md'; self.put(value, 'simulated test-only evidence\n'); values[key] = value
        for k,v in values.items(): text = re.sub(r'(?m)^'+k+r': .+$', k+': '+v, text)
        p.write_text(text, encoding='utf8')

    def accepted_prefix(self):
        self.accepted(checker.PLAN)
        for task in checker.NEW: self.accepted(task)

    def policy(self, change):
        p = self.root/'spec/architecture/frozen-architecture.md'; text=p.read_text(encoding='utf8')
        m=re.search(r'<!-- client-supplement-policy -->\s*```json\s*(.*?)\s*```',text,re.S)
        value=json.loads(m.group(1)); change(value)
        text=text[:m.start(1)]+json.dumps(value,ensure_ascii=False,indent=2)+text[m.end(1):];p.write_text(text,encoding='utf8')
        p=self.root/'spec/architecture/baseline.md';p.write_text(re.sub(r'(?m)^- sha256: `[^`]+`$', '- sha256: `'+hashlib.sha256((self.root/'spec/architecture/frozen-architecture.md').read_bytes()).hexdigest()+'`', p.read_text(encoding='utf8')),encoding='utf8')

    def test_actual_backlog_planning_is_valid_and_does_not_evaluate_open_stage_gate(self):
        self.assertEqual([], checker.check(ROOT))
        with patch.object(checker, 's2_gate_errors', side_effect=AssertionError('OPEN stage evaluation forbidden')):
            self.assertEqual([], checker.check(self.root))

    def test_each_task_missing_and_duplicate_fails(self):
        for task in checker.NEW:
            p=self.path(task);raw=p.read_bytes();p.unlink();self.assertTrue(checker.check(self.root));p.write_bytes(raw)
            q=self.put('spec/tasks/active/'+p.name,p.read_text(encoding='utf8').replace('status: backlog','status: active'))
            self.assertTrue(checker.check(self.root));q.unlink()

    def test_declared_status_and_id_must_match_queue_file(self):
        p=self.path(checker.NEW[0]);old=p.read_text(encoding='utf8')
        for text in (old.replace('status: backlog','status: done'),old.replace('task_id: '+checker.NEW[0],'task_id: LOOP1-WRONG-001')):
            p.write_text(text,encoding='utf8');self.assertTrue(checker.check(self.root))

    def test_dependency_order_and_planning_dependency_are_enforced(self):
        for task in checker.NEW:
            p=self.path(task);old=p.read_text(encoding='utf8');text=old.replace('- '+checker.CHAIN[checker.NEW.index(task)]+'；','- LOOP1-WEB-001；' if task!=checker.NEW[0] else '- LOOP1-CLIENT-UI-REF-001；')
            p.write_text(text,encoding='utf8');self.assertTrue(checker.check(self.root));p.write_text(old,encoding='utf8')
        p=self.path(checker.NEW[0]);p.write_text(p.read_text(encoding='utf8').replace('- '+checker.PLAN+'；','- LOOP1-WEB-001；'),encoding='utf8');self.assertTrue(checker.check(self.root))

    def test_ready_and_active_require_predecessor_and_plan_accepted_synced(self):
        p=self.move(checker.NEW[0],'ready');self.assertTrue(checker.check(self.root))
        self.accepted(checker.PLAN);self.assertEqual([],checker.check(self.root))
        self.move(checker.NEW[0],'active');self.assertEqual([],checker.check(self.root))
        self.move(checker.NEW[1],'active');self.assertTrue(checker.check(self.root))

    def test_backlog_cannot_claim_implementation_phase(self):
        p=self.path(checker.NEW[-1]);p.write_text(p.read_text(encoding='utf8').replace('client_supplement_phase: planned','client_supplement_phase: i18n_product'),encoding='utf8');self.assertTrue(checker.check(self.root))

    def test_done_without_independent_acceptance_and_sync_fails(self):
        self.accepted(checker.PLAN);self.move(checker.NEW[0],'done');self.assertTrue(checker.check(self.root))

    def test_all_simulated_accepted_tasks_satisfy_only_structural_prerequisites(self):
        self.accepted_prefix();self.assertEqual([],checker.check(self.root));self.assertEqual([],checker.s2_gate_errors(self.root))

    def test_each_new_completion_result_sha_and_evidence_missing_fails(self):
        self.accepted_prefix()
        for task in checker.NEW:
            p=self.path(task);old=p.read_text(encoding='utf8')
            for key in ('acceptance_result','main_sync_result','accepted_candidate_sha','integrated_main_sha','independent_review_evidence','hosted_acceptance_evidence','main_sync_evidence'):
                with self.subTest(task=task,key=key):
                    p.write_text(re.sub(r'(?m)^'+key+r': .+$',key+': unavailable',old),encoding='utf8');self.assertTrue(checker.s2_gate_errors(self.root))
            p.write_text(old,encoding='utf8')

    def test_completion_evidence_cannot_escape_task_scope(self):
        self.accepted_prefix();p=self.path(checker.NEW[0]);text=p.read_text(encoding='utf8');p.write_text(re.sub(r'(?m)^main_sync_evidence: .+$','main_sync_evidence: ../private.txt',text),encoding='utf8');self.assertTrue(checker.check(self.root))

    def test_completion_metadata_rejects_duplicate_sections_fields_empty_and_malformed(self):
        self.accepted_prefix()
        self.assertEqual([], checker.check(self.root))
        p = self.path(checker.NEW[0]); original = p.read_text(encoding='utf8')
        mutations = [original + '\n# Completion Metadata\nacceptance_result: PASS\n',
                     original.replace('acceptance_result: PASS', 'acceptance_result: FAIL\nacceptance_result: PASS'),
                     original.replace('main_sync_result: PASS', 'main_sync_result PASS')]
        for key in checker.COMPLETION_KEYS:
            line = re.search(r'^' + key + r': .+$', original, re.M).group()
            mutations.extend([original.replace(line, line + '\n' + line),
                              original.replace(line, key + ':   \n'),
                              original.replace(line, key + ':\nPASS'),
                              original.replace(line, '')])
        for text in mutations:
            with self.subTest(metadata=text):
                p.write_text(text, encoding='utf8')
                errors = checker.check(self.root)
                self.assertTrue(any('invalid completion metadata' in e for e in errors), errors)
        p.write_text(original, encoding='utf8')
        self.assertEqual([], checker.check(self.root))

    def set_redirect_evidence(self, task, relative):
        p = self.path(task); text = p.read_text(encoding='utf8')
        p.write_text(re.sub(r'^main_sync_evidence: .+$', 'main_sync_evidence: ' + relative, text, flags=re.M), encoding='utf8')

    @unittest.skipIf(os.name == 'nt', 'Linux/POSIX symlink case; Windows executes real junction case')
    def test_real_symlink_evidence_leaf_ancestor_and_task_directory_rejected(self):
        self.accepted_prefix(); self.assertEqual([], checker.check(self.root))
        task = checker.NEW[0]; base = self.root/'spec/progress/evidence'/task
        external = self.root/'external'; external.mkdir(); (external/'proof.md').write_text('outside proof', encoding='utf8')
        for target, directory in ((external/'proof.md', False), (external, True), (base, True)):
            link = base/'redirect'
            link.symlink_to(target, target_is_directory=directory)
            self.addCleanup(lambda p=link: p.unlink(missing_ok=True))
            relative = f'spec/progress/evidence/{task}/redirect' + ('/proof.md' if target == external else '/fixture-main_sync_evidence.md' if directory else '')
            self.set_redirect_evidence(task, relative)
            self.assertTrue(checker.check(self.root))
            link.unlink()
        original = base.with_name(task + '-original'); base.rename(original); base.symlink_to(original, target_is_directory=True)
        try:
            self.set_redirect_evidence(task, f'spec/progress/evidence/{task}/fixture-main_sync_evidence.md')
            self.assertTrue(checker.check(self.root))
        finally:
            base.unlink(); original.rename(base)

    @unittest.skipUnless(os.name == 'nt', 'Windows junction case; POSIX executes real symlink case')
    def test_real_windows_junction_evidence_ancestor_and_task_directory_rejected(self):
        self.accepted_prefix(); self.assertEqual([], checker.check(self.root))
        task = checker.NEW[0]; base = self.root/'spec/progress/evidence'/task
        external = self.root/'external'; external.mkdir(); (external/'proof.md').write_text('outside proof', encoding='utf8')
        for target in (external, base):
            link = base/'redirect'
            result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(link), str(target)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            try:
                leaf = link/('proof.md' if target == external else 'fixture-main_sync_evidence.md')
                self.assertTrue(link.is_junction()); self.assertFalse(leaf.is_symlink())
                self.set_redirect_evidence(task, leaf.relative_to(self.root).as_posix())
                self.assertTrue(checker.check(self.root))
            finally:
                link.rmdir()  # Remove only this test-created junction, never its target.
        original = base.with_name(task + '-original'); base.rename(original)
        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(base), str(original)], capture_output=True, text=True)
        try:
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(base.is_junction())
            self.set_redirect_evidence(task, f'spec/progress/evidence/{task}/fixture-main_sync_evidence.md')
            self.assertTrue(checker.check(self.root))
        finally:
            if base.is_junction(): base.rmdir()
            original.rename(base)

    def test_completion_evidence_resolution_errors_and_empty_file_fail_closed(self):
        self.accepted_prefix(); self.assertEqual([], checker.check(self.root))
        with patch.object(Path, 'resolve', side_effect=OSError('unavailable resolution')):
            self.assertTrue(checker.check(self.root))
        task = checker.NEW[0]
        proof = self.root/f'spec/progress/evidence/{task}/fixture-main_sync_evidence.md'
        proof.write_text('   ', encoding='utf8'); self.assertTrue(checker.check(self.root))
        proof.unlink(); self.assertTrue(checker.check(self.root))

    def test_every_prior_gate_prerequisite_remains_required(self):
        self.accepted_prefix()
        for task in checker.PREREQUISITES:
            with self.subTest(task=task):
                p=self.path(task);raw=p.read_bytes();p.unlink();self.assertTrue(checker.s2_gate_errors(self.root));p.write_bytes(raw)

    def test_claimed_stage_pass_fails_with_backlog_and_passes_only_fixture_completed_set(self):
        self.put('spec/progress/current.md','Current Gate: S2\nGate Status: PASS\n');self.assertTrue(checker.check(self.root))
        self.accepted_prefix();self.assertEqual([],checker.check(self.root))

    def test_rehashed_policy_cannot_remove_or_reorder_chain_or_gate_requirement(self):
        originals={p:(self.root/p).read_bytes() for p in ['spec/architecture/frozen-architecture.md','spec/architecture/baseline.md']}
        for mut in (lambda p:p['chain'].reverse(),lambda p:p['gate_prerequisites'].pop(),lambda p:p['chain'].pop()):
            self.policy(mut);self.assertTrue(checker.check(self.root))
            for p,raw in originals.items():(self.root/p).write_bytes(raw)

    def test_frozen_prompt_hash_and_linkage_fail_closed(self):
        self.put(checker.APPROVAL,'not Human approval\n');self.assertTrue(checker.check(self.root))

    def test_language_policy_fixed_ids_order_storage_and_phase(self):
        originals={p:(self.root/p).read_bytes() for p in ['spec/architecture/frozen-architecture.md','spec/architecture/baseline.md']}
        mutations=(lambda p:p['language']['locales'].reverse(),lambda p:p['language'].update(default='zh-CN'),lambda p:p['language']['web'].update(key='other'),lambda p:p['language']['desktop'].update(storage='appearance.json'),lambda p:p['language']['mobile'].update(key='credentials'),lambda p:p['language'].update(activation_phase='state_product'))
        for mut in mutations:
            self.policy(mut);self.assertTrue(checker.check(self.root))
            for p,raw in originals.items():(self.root/p).write_bytes(raw)

    def test_language_storage_is_forbidden_before_real_i18n_dependency_phase(self):
        for path,code in [('clients/web/src/ui/language.ts','window.localStorage.getItem("plugworldim.language.v1")'),('clients/desktop/src-tauri/src/desktop_capabilities.rs','fn language_load() {}'),('clients/mobile/app/src/main/kotlin/im/platform/client/ui/Preferences.kt','getString("language","en")')]:
            with self.subTest(path=path):
                p=self.put(path,code);self.assertTrue(checker.check(self.root));p.unlink()

    def test_future_i18n_phase_only_after_accepted_prefix_preserves_existing_appearance_guard(self):
        self.accepted(checker.PLAN);self.accepted(checker.NEW[0]);self.accepted(checker.NEW[1]);self.move(checker.NEW[2],'active')
        self.put('clients/web/src/ui/language.ts','window.localStorage.getItem("plugworldim.language.v1")')
        self.assertEqual([],checker.check(self.root))  # Phase permission only; actual source guard remains separate.
        architecture=importlib.util.spec_from_file_location('source_guard',ROOT/'ci/check_architecture.py');module=importlib.util.module_from_spec(architecture);architecture.loader.exec_module(module)
        policy,_=module.client_policy(ROOT)
        source='const APPEARANCE_KEY="plugworldim.appearance.v1";window.localStorage.getItem(APPEARANCE_KEY);window.localStorage.setItem(APPEARANCE_KEY,JSON.stringify({theme:v.theme,fontSize:v.fontSize,density:v.density,language:v.language}));'
        self.assertTrue(module.check_web_storage('clients/web/src/ui/appearance.ts',source,policy))

if __name__ == '__main__': unittest.main()
