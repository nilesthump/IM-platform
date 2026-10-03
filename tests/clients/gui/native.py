"""Explicit local toolchain selection for owned GUI builds and regressions."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
env=os.environ.copy()
env.update(JAVA_HOME="H:/.jdks/jdk17",ANDROID_HOME="H:/Android",ANDROID_SDK_ROOT="H:/Android",GRADLE_USER_HOME="H:/gradle",IM_CLIENT_GRADLE="H:/gradle/wrapper/dists/gradle-8.9-bin/78qddjpeqn5v6yec3xb8kv9ca/gradle-8.9/bin/gradle.bat",IM_CLIENT_ADB="H:/Android/platform-tools/adb.exe",CARGO_HOME="H:/.codex/toolchains/client-sqlite/cargo",RUSTUP_HOME="H:/.codex/toolchains/client-sqlite/rustup",RUSTUP_TOOLCHAIN="stable",CARGO_TARGET_DIR="H:/.codex/toolchains/client-gui/target",CARGO_BUILD_JOBS="2",PYTHONIOENCODING="utf-8")
mode=sys.argv[1]
if mode=="gui-mobile":env.update(ANDROID_USER_HOME="H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user",ANDROID_AVD_HOME="H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/avd-home")
if mode in ("rust","package","desktop","send-desktop","sqlite-desktop"):
    vc="C:/Program Files/Microsoft Visual Studio/18/Community/VC/Auxiliary/Build/vcvars64.bat"
    output=subprocess.check_output('cmd.exe /d /s /c ""'+vc.replace("/","\\")+'" >nul && set"',env=env,text=True)
    for line in output.splitlines():
        key,sep,value=line.partition("=")
        if sep and key and not key.startswith("="):env[key]=value
env["PATH"]=";".join([env["JAVA_HOME"]+"/bin",env["CARGO_HOME"]+"/bin","H:/Android/platform-tools",env.get("PATH","")])
if mode=="rust":argv=[env["CARGO_HOME"]+"/bin/cargo.exe",*sys.argv[2:]];cwd=ROOT/"clients/desktop/src-tauri"
elif mode=="package":
    # GUI target-only flags: host scripts/proc macros and storage_probe unchanged.
    env['CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_RUSTFLAGS']='-C link-arg=/SUBSYSTEM:WINDOWS -C link-arg=/ENTRY:mainCRTStartup'
    argv=["npm.cmd","run","tauri","--","build","--target","x86_64-pc-windows-msvc",*sys.argv[2:]];cwd=ROOT/"clients/desktop"
elif mode=="gradle":argv=[env["IM_CLIENT_GRADLE"],"--no-daemon",*sys.argv[2:]];cwd=ROOT/"clients/mobile"
elif mode=="gui-mobile":argv=[sys.executable,"-B","tests/clients/gui/android.py",*sys.argv[2:]];cwd=ROOT
elif mode in ("desktop","mobile","shared"):argv=[sys.executable,"-B","tools/verify_client_sync.py","--scope",mode,*sys.argv[2:]];cwd=ROOT
elif mode.startswith("send-") or mode.startswith("sqlite-"):
    family,scope=mode.split("-",1);argv=[sys.executable,"-B","tools/verify_client_"+family+".py","--scope",scope,*sys.argv[2:]];cwd=ROOT
else:raise RuntimeError("Unrecognized build mode")
print("Owned GUI/native mode="+mode,flush=True)
raise SystemExit(subprocess.call(argv,cwd=cwd,env=env))
