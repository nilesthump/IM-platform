"""Bounded S2 planning controls. Structural evidence never substitutes for Review/CI."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'LOOP1-CLIENT-SUPPLEMENT-PLAN-001'
NEW = ('LOOP1-CLIENT-STATE-001', 'LOOP1-CLIENT-UI-REF-001', 'LOOP1-CLIENT-I18N-001')
CHAIN = ('LOOP1-WEB-001', *NEW)
PREREQUISITES = ('LOOP1-CLIENT-SQLITE-001', 'LOOP1-CLIENT-UI-ARCH-001', 'LOOP1-CLIENT-SEND-001', 'LOOP1-SYNC-001', 'LOOP1-CLIENT-GUI-001', *CHAIN)
QUEUES = ('backlog', 'ready', 'active', 'review', 'done')
ADR = 'spec/architecture/decisions/ADR-0012-client-supplement-planning.md'
APPROVAL = f'spec/progress/evidence/{PLAN}/human-request.txt'
PHASES = dict(zip(NEW, ('state_product', 'ui_ref_product', 'i18n_product')))


def fields(text):
    return dict(re.findall(r'^([a-z_]+):\s*([^\n]+?)\s*$', text, re.M))


def section(text, heading):
    m = re.search(r'^# ' + re.escape(heading) + r'\s*\n(.*?)(?=^# |\Z)', text, re.M | re.S)
    return m.group(1) if m else ''


def authority_errors(root):
    try:
        manifest = dict(re.findall(r'^- ([a-z_0-9]+): `([^`]+)`\s*$', (root/'spec/architecture/baseline.md').read_text(encoding='utf8'), re.M))
        raw = (root/'spec/architecture/frozen-architecture.md').read_bytes()
        if manifest.get('sha256') != hashlib.sha256(raw).hexdigest():
            raise ValueError('canonical hash mismatch')
        required = {'supplement_revision_adr': ADR, 'supplement_revision_task_id': PLAN,
                    'supplement_revision_type': 'human_approved_s2_client_supplement_planning',
                    'supplement_semantic_change': 'true', 'supplement_approval_source': APPROVAL,
                    'supplement_previous_sha256': '2ba864fc2805900117f62c3c88795c52364ecc7450da17975e26d35ebf2cc432'}
        if any(manifest.get(k) != v for k, v in required.items()):
            raise ValueError('supplement manifest lineage/approval linkage')
        approved = (root/APPROVAL).read_bytes()
        if manifest.get('supplement_approval_sha256') != hashlib.sha256(approved).hexdigest():
            raise ValueError('supplement Human raw prompt hash')
        adr = (root/ADR).read_text(encoding='utf8')
        if 'Human-approved' not in adr or 'semantic_change=true' not in adr or APPROVAL not in adr:
            raise ValueError('Human-approved ADR linkage')
        doc = raw.decode('utf8')
        m = re.search(r'<!-- client-supplement-policy -->\s*```json\s*(.*?)\s*```', doc, re.S)
        p = json.loads(m.group(1)) if m else {}
        if (p.get('decision') != 'ADR-0012-client-supplement-planning' or p.get('planning_task') != PLAN
                or p.get('stage') != 'S2' or p.get('chain') != list(CHAIN)
                or p.get('gate_prerequisites') != list(PREREQUISITES)):
            raise ValueError('exact chain/Stage Gate prerequisites')
        language = p.get('language', {})
        if (language.get('activation_task') != NEW[-1] or language.get('activation_phase') != 'i18n_product'
                or language.get('locales') != ['en', 'zh-CN', 'ja-JP'] or language.get('default') != 'en'
                or language.get('names') != ['English', '简体中文', '日本語']
                or language.get('entry') != 'Language / 语言 / 言語'):
            raise ValueError('language identity/order/activation')
        expected = {
            'web': {'adapter':'clients/web/src/ui/language.ts','key':'plugworldim.language.v1','storage':'localStorage','field':'language','format':'raw UTF-8 enum','max_bytes':5},
            'desktop': {'adapter':'clients/desktop/src/application/ui/native.ts','native_adapter':'clients/desktop/src-tauri/src/desktop_capabilities.rs','storage':'app_data/language.txt','field':'language','format':'raw UTF-8 enum','max_bytes':5},
            'mobile': {'adapter':'clients/mobile/app/src/main/kotlin/im/platform/client/ui/Preferences.kt','storage':'SharedPreferences appearance MODE_PRIVATE','key':'language','field':'language','format':'String enum','max_bytes':5}}
        if any(language.get(k) != v for k, v in expected.items()):
            raise ValueError('fixed language adapter/storage/field/validation scope')
        for chapter in (6, 15, 19, 20):
            body = re.search(r'^## ' + str(chapter) + r'\. .*?(?=^## |\Z)', doc, re.M | re.S)
            if not body or any(t not in body.group() for t in NEW):
                raise ValueError(f'chapter {chapter} supplement missing')
        appendix = re.search(r'^\| S2 \| (.*)$', doc, re.M)
        if not appendix or any(t.removeprefix('LOOP1-') not in appendix.group() for t in NEW):
            raise ValueError('appendix S2 completion prerequisite missing')
        return []
    except (OSError, ValueError, AttributeError) as exc:
        return ['S2 planning authority unavailable: ' + str(exc)]


def inventory(root):
    tasks = {}; errors = []
    for queue in QUEUES:
        for path in sorted((root/'spec/tasks'/queue).glob('*.md')):
            if path.is_symlink():
                errors.append(f'S2 task symlink: {path.name}'); continue
            text = path.read_text(encoding='utf8'); f = fields(text.split('---', 2)[1] if text.startswith('---') else '')
            task = f.get('task_id', '')
            if task != path.stem or f.get('status') != queue:
                errors.append(f'S2 task id/queue/status mismatch: {path.name}')
            tasks.setdefault(path.stem, []).append((queue, text, f))
    for task, entries in tasks.items():
        if len(entries) != 1:
            errors.append(f'S2 task must be unique: {task}')
    return tasks, errors


COMPLETION_KEYS = ('acceptance_result', 'accepted_candidate_sha', 'integrated_main_sha',
                   'main_sync_result', 'independent_review_evidence',
                   'hosted_acceptance_evidence', 'main_sync_evidence')


def completion_fields(text):
    headings = list(re.finditer(r'^# Completion Metadata[ \t]*$', text, re.M))
    if len(headings) != 1:
        raise ValueError('Completion Metadata must be a single section')
    body = text[headings[0].end():]
    body = re.split(r'^# ', body, maxsplit=1, flags=re.M)[0]
    values = {}
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'([a-z_]+):[ \t]*([^\r\n]+)', line)
        if not match:
            raise ValueError('malformed Completion Metadata line')
        key, value = match.group(1), match.group(2).strip(' \t')
        if key not in COMPLETION_KEYS or key in values or not value:
            raise ValueError('duplicate, unknown or empty Completion Metadata field')
        values[key] = value
    if set(values) != set(COMPLETION_KEYS):
        raise ValueError('missing Completion Metadata field')
    return values


def bounded_evidence(root, task, value):
    relative = Path(value)
    if (not value.startswith(f'spec/progress/evidence/{task}/')
            or relative.is_absolute() or '..' in relative.parts):
        return False
    path = root/relative
    try:
        # Inspect every component, including the task directory and repository root.
        # Windows junctions/reparse points are not reported by is_symlink().
        for component in (path, *path.parents):
            info = component.lstat()
            if (stat.S_ISLNK(info.st_mode)
                    or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                return False
        directory = (root/'spec/progress/evidence'/task).resolve(strict=True)
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(directory):
            return False
        return resolved.is_file() and bool(resolved.read_bytes().strip())
    except (OSError, RuntimeError, ValueError):
        return False


def completion_errors(root, task, text):
    try:
        f = completion_fields(text)
    except ValueError as exc:
        return [f'S2 {task}: invalid completion metadata: {exc}']
    errors = []
    if f.get('acceptance_result') != 'PASS' or f.get('main_sync_result') != 'PASS':
        errors.append(f'S2 {task}: independent acceptance/main sync incomplete')
    for key in ('accepted_candidate_sha', 'integrated_main_sha'):
        if not re.fullmatch(r'[0-9a-f]{40}', f.get(key, '')):
            errors.append(f'S2 {task}: missing actual {key}')
    for key in ('independent_review_evidence', 'hosted_acceptance_evidence', 'main_sync_evidence'):
        if not bounded_evidence(root, task, f.get(key, '')):
            errors.append(f'S2 {task}: missing bounded {key}')
    # These are necessary structural links only. Review must inspect the contents,
    # actual exact-head jobs, independence, merge and preservation-aware sync.
    return errors


def accepted_errors(root, tasks, task):
    entries = tasks.get(task, [])
    if len(entries) != 1 or entries[0][0] != 'done':
        return [f'S2 prerequisite not uniquely done: {task}']
    return completion_errors(root, task, entries[0][1]) if task in (*NEW, PLAN) else []


def s2_gate_errors(root, tasks=None):
    """Stage prerequisite check; called on fixtures or an explicit claimed S2 PASS.

    The normal planning command never evaluates the actual OPEN Stage Gate.
    Existing behavioral/Architect/helper/Gate obligations remain independently mandatory.
    """
    if tasks is None:
        tasks, errors = inventory(root)
    else:
        errors = []
    for task in PREREQUISITES:
        errors += accepted_errors(root, tasks, task)
    return errors


def check(root):
    errors = authority_errors(root)
    tasks, found = inventory(root); errors += found
    if errors: return errors
    for i, task in enumerate(NEW):
        entries = tasks.get(task, [])
        if len(entries) != 1:
            errors.append(f'S2 missing unique planned task: {task}'); continue
        queue, text, f = entries[0]
        deps = re.findall(r'^\s*-\s+(LOOP1-[A-Z0-9-]+)(?=\s|[；;])', section(text, 'Dependencies'), re.M)
        expected = [CHAIN[i]] + ([PLAN] if i == 0 else [])
        if deps != expected:
            errors.append(f'S2 {task}: exact serial dependency mismatch')
        if f.get('stage') != 'S2' or f.get('gate') != 'S2':
            errors.append(f'S2 {task}: stage/gate mismatch')
        phase = f.get('client_supplement_phase')
        if queue == 'backlog' and phase != 'planned':
            errors.append(f'S2 {task}: backlog cannot enable product phase')
        if queue in ('active', 'review', 'done') and phase != PHASES[task]:
            errors.append(f'S2 {task}: product phase mismatch')
        if queue in ('ready', 'active', 'review', 'done'):
            for dep in expected:
                errors += accepted_errors(root, tasks, dep)
        if queue == 'done': errors += completion_errors(root, task, text)
    plan = tasks.get(PLAN, [])
    if len(plan) != 1: errors.append('S2 missing unique planning control Task')
    elif plan[0][0] == 'done': errors += completion_errors(root, PLAN, plan[0][1])
    i18n = tasks.get(NEW[-1], [])
    enabled = (len(i18n) == 1 and i18n[0][0] in ('active', 'review', 'done')
               and i18n[0][2].get('client_supplement_phase') == 'i18n_product'
               and not accepted_errors(root, tasks, NEW[-2]))
    if not enabled:
        # Detect premature language persistence in actual source ownership only.
        for relative, tokens in {
            'clients/web/src/ui/language.ts': ('localStorage',),
            'clients/desktop/src/application/ui/native.ts': ('language_load', 'language_save'),
            'clients/desktop/src-tauri/src/desktop_capabilities.rs': ('language.txt', 'language_load', 'language_save'),
            'clients/mobile/app/src/main/kotlin/im/platform/client/ui/Preferences.kt': ('"language"',),
        }.items():
            p = root/relative
            if p.exists() and any(token in p.read_text(encoding='utf8') for token in tokens):
                errors.append(f'S2 premature language persistence: {relative}')
    current = (root/'spec/progress/current.md').read_text(encoding='utf8')
    gate = re.search(r'^Current Gate:\s*(\S+)', current, re.M)
    status = re.search(r'^Gate Status:\s*(\S+)', current, re.M)
    if gate and status and gate.group(1) == 'S2' and status.group(1) == 'PASS':
        errors += s2_gate_errors(root, tasks)
    return sorted(set(errors))


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, default=ROOT)
    args = p.parse_args(); errors = check(args.root)
    for error in errors: print('FAIL: ' + error)
    print('FAIL: planning controls' if errors else 'PASS: planning queue/authority/dependencies; OPEN Stage Gate not evaluated')
    return bool(errors)

if __name__ == '__main__': raise SystemExit(main())
