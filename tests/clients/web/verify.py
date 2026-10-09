#!/usr/bin/env python3
"""Web CI entry: strict pre-product prerequisite or actual locked product checks.

No skip/fallback flag: any product input requires the complete product path.
Temporary source copies isolate npm/build outputs from active repository guards.
"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
REQUIRED = ('package.json', 'package-lock.json', 'tsconfig.json', 'src/ui/main.tsx',
            'src/ui/index.html', 'src/ui/build.config.mjs', 'src/ui/appearance.ts')
BEHAVIOR = ('tests/clients/web/behavior.mjs', 'tests/clients/web/appearance.mjs')
MARKERS = (b'', b'\n', b'\r\n')


def git(root, *args, input=None):
    result = subprocess.run(['git', '-C', str(root), *args], input=input, capture_output=True, check=True)
    return result.stdout


def compared_base(root):
    """CI base comes from GitHub's event, never a caller-supplied --base waiver."""
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
        kind = os.environ['GITHUB_EVENT_NAME']
        if kind == 'pull_request':
            base, head = event['pull_request']['base']['sha'], event['pull_request']['head']['sha']
        elif kind == 'push':
            base, head = event['before'], event['after']
        else:
            raise ValueError('Unsupported Web verification event')
        if not re.fullmatch(r'[0-9a-f]{40}', base) or not re.fullmatch(r'[0-9a-f]{40}', head):
            raise ValueError('Invalid event base/head')
        if git(root, 'rev-parse', 'HEAD').decode().strip() != head:
            raise ValueError('Web verifier checkout does not equal exact event head')
        if base == '0' * 40:
            return git(root, 'hash-object', '-t', 'tree', '--stdin', input=b'').decode().strip()
        git(root, 'cat-file', '-e', base + '^{commit}')
        return base
    # Local dirty deletions must be compared with committed HEAD, not HEAD^.
    return git(root, 'rev-parse', 'HEAD').decode().strip()


def base_had_product(root, base):
    files = git(root, 'ls-tree', '-r', '--name-only', '-z', base, '--', 'clients/web/').split(b'\0')
    files = [name for name in files if name]
    if files != [b'clients/web/.gitkeep']:
        return bool(files)
    return git(root, 'show', base + ':clients/web/.gitkeep') not in MARKERS


def prerequisite(root):
    paths = list((root/'spec/tasks').glob('*/LOOP1-WEB-001.md'))
    if len(paths) != 1 or paths[0].parent.name != 'backlog' or paths[0].is_symlink():
        return False
    task = paths[0].read_text(encoding='utf-8')
    current = (root/'spec/progress/current.md').read_text(encoding='utf-8')
    return (bool(re.search(r'(?m)^status: backlog\s*$', task))
            and 'web_verification_phase: appearance_prerequisite' in task
            and bool(re.search(r'(?m)^Current Task: LOOP1-WEB-001\s*$', current))
            and bool(re.search(r'(?m)^Current Task State: backlog\s*$', current))
            and bool(re.search(r'(?m)^Execution Status: APPROVED_PENDING_FREEZE\s*$', current)))


def run(command, *, cwd, env=None):
    print('RUN ' + ' '.join(str(arg) for arg in command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def verify(root=ROOT, *, runner=run):
    web = root/'clients/web'
    if (root/'clients').is_symlink() or web.is_symlink() or not web.is_dir():
        raise ValueError('Web root is missing or symlinked')
    entries = list(web.rglob('*'))
    if any(path.is_symlink() for path in entries):
        raise ValueError('Web input symlink forbidden')
    skeleton = (entries == [web/'.gitkeep'] and entries[0].is_file()
                and entries[0].read_bytes() in MARKERS)
    if skeleton:
        if not prerequisite(root) or base_had_product(root, compared_base(root)):
            raise ValueError('Empty Web skeleton cannot bypass product verification')
        runner([sys.executable, '-B', 'ci/check_s0_boundary.py', 'web'], cwd=root)
        runner([sys.executable, '-B', 'ci/check_architecture.py', '--scope', 'clients', '--json'], cwd=root)
        print('PREREQUISITE_SKELETON_ONLY: exact empty Web; no Web build/behavior/product acceptance performed.')
        return 'PREREQUISITE_SKELETON_ONLY'
    missing = [str(web/name) for name in REQUIRED if not (web/name).is_file() or not (web/name).stat().st_size]
    missing += [str(root/name) for name in BEHAVIOR if not (root/name).is_file() or not (root/name).stat().st_size or (root/name).is_symlink()]
    if missing:
        raise ValueError('Incomplete Web product; no skeleton fallback: ' + ', '.join(missing))
    runner([sys.executable, '-B', 'ci/check_architecture.py', '--scope', 'clients', '--json'], cwd=root)
    npm, node = shutil.which('npm.cmd' if os.name == 'nt' else 'npm'), shutil.which('node')
    if not npm or not node:
        raise ValueError('Actual npm/Node tooling unavailable; never skipped')
    with tempfile.TemporaryDirectory(prefix='web-verification-') as temp:
        stage = Path(temp)
        shutil.copytree(web, stage/'clients/web', ignore=shutil.ignore_patterns('node_modules', 'dist', 'build'))
        shutil.copytree(root/'clients/shared', stage/'clients/shared', ignore=shutil.ignore_patterns('node_modules', 'dist', 'build'))
        artifact = stage/'web-build'
        env = os.environ.copy()
        env['WEB_BUILD_DIR'] = str(artifact)
        runner([npm, '--prefix', str(stage/'clients/web'), 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=root, env=env)
        runner([npm, '--prefix', str(stage/'clients/web'), 'run', 'build'], cwd=root, env=env)
        if not (artifact/'index.html').is_file() or not list(artifact.rglob('*.js')):
            raise ValueError('Actual Web build artifacts missing; no skeleton fallback')
        for test in BEHAVIOR:
            runner([node, str(root/test)], cwd=root, env=env)
    print('PASS: actual locked Web build, behavior, appearance and source verification; GUI screenshots remain independent.')
    return 'PRODUCT_VERIFIED'


def main():
    try:
        verify()
    except (ValueError, OSError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
