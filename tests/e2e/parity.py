"""Build the locked Web application once and exercise the same bytes on both profiles."""
import hashlib
from pathlib import Path
import runpy
import tempfile

from go_tls_messaging import ROOT, run_profile


def artifact_hash(artifact):
    digest = hashlib.sha256()
    for path in sorted(artifact.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(artifact).as_posix().encode() + b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def main():
    web = runpy.run_path(str(ROOT / 'tests/clients/web/verify.py'))
    with tempfile.TemporaryDirectory(prefix='im-parity-') as temp:
        artifact = web['build_web'](ROOT, Path(temp))
        expected = artifact_hash(artifact)
        for profile in ('go', 'java'):
            run_profile(profile, artifact)
            if artifact_hash(artifact) != expected:
                raise AssertionError('Web artifact changed during profile switch')
            print(f'PASS {profile} Web artifact SHA-256 {expected}', flush=True)


if __name__ == '__main__':
    main()
