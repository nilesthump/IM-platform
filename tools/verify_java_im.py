"""Execute the same group contract exchanges on real Java and Go services."""
import argparse
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
from verify_java_auth import ROOT, profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=Path, required=True)
    args = parser.parse_args()
    build = args.build_dir.resolve()
    if build.is_relative_to(ROOT):
        raise ValueError("External Maven build directory required")
    env = dict(os.environ)
    for key in ("PGHOST", "PGPORT", "PGUSER", "PGDATABASE", "PGPASSWORD", "NATS_URL"):
        if not env.get(key):
            raise ValueError(f"{key} required to run live fixtures")
    env["JAVA_AUTH_SIGNING_KEY"] = secrets.token_hex(32)
    java = shutil.which("java")
    if not java:
        raise RuntimeError("Java required")
    cp = os.pathsep.join((str(build / "test-classes"), str(build / "classes"),
                          (build / "classpath.txt").read_text(encoding="utf8").strip()))
    with tempfile.TemporaryDirectory(prefix="java-im-", dir=build) as directory:
        for index, name in enumerate(("java", "go", "java")):
            folder = Path(directory) / f"{index}-{name}"
            folder.mkdir()
            with profile(name, build, folder, env, java, cp) as (url, config):
                if index < 2:
                    subprocess.run([java, "-cp", cp, "im.platform.tests.im.GroupFixtures",
                                    url, str(ROOT), str(config)], check=True, timeout=150)
                for mode, state in ([("read", index - 1)] if index else []) + ([("write", index)] if index < 2 else []):
                    subprocess.run([java, "-cp", cp, "im.platform.tests.im.ProfileContinuity",
                                    url, mode, str(config), str(Path(directory) / f"switch-{state}")],
                                   check=True, timeout=20)


if __name__ == "__main__":
    main()

