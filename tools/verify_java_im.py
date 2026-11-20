"""Execute the same group contract exchanges on real Java and Go services."""
import argparse
import json
import runpy
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
                if index == 0:
                    ack = folder / "replayed-message-ack.json"
                    contract = runpy.run_path(str(ROOT / "contracts/websocket/verify.py"))
                    timestamp_cases = {}
                    for value in ("2026-01-01T00:00:00Z", "2024-02-29T23:59:59.1234567891-23:59",
                                  "+02026-01-01T00:00:00Z", "0000-01-01T00:00:00Z",
                                  "2025-02-29T00:00:00Z", "2026-01-01T24:00:00Z",
                                  "2026-12-31t23:59:59.999+05:30", "2026-12-31t24:00:00.000+05:30",
                                  "2026-01-01T24:00:00-07:00", "2026-01-01T00:00:60Z", "2026-01-01T00:00:00z"):
                        try:
                            contract["validate"](value, contract["SCHEMA"]["$defs"]["Timestamp"])
                            timestamp_cases[value] = True
                        except contract["Invalid"]:
                            timestamp_cases[value] = False
                    timestamps = folder / "timestamp-cases.json"
                    timestamps.write_text(json.dumps(timestamp_cases), encoding="utf8")
                    subprocess.run([java, "-cp", cp, "im.platform.tests.im.MessageOutcomeProbe",
                                    str(config), url, str(ack), str(timestamps)], check=True, timeout=35)
                    contract["validate"](json.loads(ack.read_text(encoding="utf8")), contract["SCHEMA"])
                if index < 2:
                    subprocess.run([java, "-cp", cp, "im.platform.tests.im.GroupFixtures",
                                    url, str(ROOT), str(config)], check=True, timeout=150)
                for mode, state in ([("read", index - 1)] if index else []) + ([("write", index)] if index < 2 else []):
                    subprocess.run([java, "-cp", cp, "im.platform.tests.im.ProfileContinuity",
                                    url, mode, str(config), str(Path(directory) / f"switch-{state}")],
                                   check=True, timeout=20)


if __name__ == "__main__":
    main()

