#!/usr/bin/env python3
"""Actual current storage verification. Missing toolchains/runtime fail, never skip."""
from pathlib import Path
import argparse, subprocess, os, sys, hashlib
ROOT=Path(__file__).resolve().parents[1]
def run(args,cwd=ROOT):
    print("+", " ".join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),cwd=cwd,check=True)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--scope",choices=["shared","desktop","mobile"],required=True)
    parser.add_argument("--serial")
    args=parser.parse_args()
    if args.scope in ("shared","desktop"):
        npm="npm.cmd" if os.name=="nt" else "npm"
        run([npm,"--prefix","clients/shared/protocol-sdk","ci","--ignore-scripts","--no-audit","--no-fund"])
        run([npm,"--prefix","clients/shared/protocol-sdk","run","build"])
        if args.scope=="shared":
            print("PASS: shared TypeScript compile (behavior exercised by Desktop SQLx and Android jobs)")
            return
        run([npm,"--prefix","clients/desktop","ci","--ignore-scripts","--no-audit","--no-fund"])
        run([npm,"--prefix","clients/desktop","run","build"])
        native=ROOT/"clients/desktop/src-tauri"
        run(["cargo","test","--locked"],native)
        run(["cargo","build","--locked","--bin","storage_probe"],native)
        target=Path(os.environ.get("CARGO_TARGET_DIR",native/"target"))
        if not target.is_absolute(): target=native/target
        probe=target/"debug"/("storage_probe.exe" if os.name=="nt" else "storage_probe")
        run(["node","tests/clients/sqlite/desktop.mjs",probe])
        return
    canonical=ROOT/"contracts/fixtures/sync-plugin/golden.json"
    asset=ROOT/"clients/mobile/app/src/androidTest/assets/golden.json"
    if canonical.read_bytes()!=asset.read_bytes(): raise RuntimeError("Android fixture differs from canonical input")
    if (ROOT/"tests/clients/sqlite/v1.sql").read_bytes()!=(ROOT/"clients/mobile/app/src/androidTest/assets/v1.sql").read_bytes(): raise RuntimeError("Android migration fixture differs from retained old layout")
    mobile=ROOT/"clients/mobile"
    wrapper=Path(os.environ.get("IM_CLIENT_GRADLE",mobile/("gradlew.bat" if os.name=="nt" else "gradlew")))
    if os.name!="nt": run(["chmod","+x",wrapper])
    run([wrapper,"--no-daemon","assembleDebug","assembleDebugAndroidTest"],mobile)
    adb=os.environ.get("IM_CLIENT_ADB","adb")
    if not args.serial: raise RuntimeError("Explicit real emulator serial required")
    serial=args.serial
    if not serial.startswith("emulator-"): raise RuntimeError("Acceptance requires Android emulator")
    devices=subprocess.check_output([adb,"devices"],text=True)
    if serial+"\tdevice" not in devices: raise RuntimeError("Emulator unavailable or unauthorized")
    def shell(*argv):
        return subprocess.check_output([adb,"-s",serial,"shell",*argv],text=True,timeout=30).strip()
    sdk=shell("getprop","ro.build.version.sdk")
    boot=shell("getprop","sys.boot_completed"); unlocked=shell("getprop","sys.user.0.ce_available")
    print("Actual minimum emulator SDK:",sdk,"boot:",boot,"credential-encrypted storage:",unlocked,flush=True)
    if sdk!="34": raise RuntimeError("Declared minimum API34 must be exercised, not a newer substitute")
    if boot!="1" or unlocked!="true": raise RuntimeError("Emulator boot/user-unlocked prerequisites not satisfied")
    run([adb,"-s",serial,"install","-r",mobile/"app/build/outputs/apk/debug/app-debug.apk"])
    run([adb,"-s",serial,"install","-r",mobile/"app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk"])
    command=[adb,"-s",serial,"shell","am","instrument","-w","im.platform.client.test/im.platform.client.storage.StorageInstrumentation"]
    for attempt in ("install","data-clear"):
        if attempt=="data-clear":
            clear=shell("pm","clear","im.platform.client")
            print("Task application data-clear:",clear,flush=True)
            if clear!="Success": raise RuntimeError("Task application data-clear failed")
        print("+"," ".join(command),"phase="+attempt,flush=True)
        result=subprocess.run(command,capture_output=True,text=True,timeout=180)
        print(result.stdout); print(result.stderr,file=sys.stderr)
        if result.returncode or "INSTRUMENTATION_RESULT: result=PASS" not in result.stdout or "INSTRUMENTATION_CODE: -1" not in result.stdout:
            raise RuntimeError("Real Android SQLite instrumentation failed in "+attempt)
        if "INSTRUMENTATION_RESULT: sdkInt=34" not in result.stdout:
            raise RuntimeError("Instrumentation did not establish actual minimum SDK")
    print("PASS: real Android SDK SQLite fixture/migration/restart/isolation/rollback instrumentation")
if __name__=="__main__":
    try: main()
    except (subprocess.SubprocessError,OSError,RuntimeError) as error:
        print("FAIL:",error,file=sys.stderr); sys.exit(1)
