from pathlib import Path
import subprocess,os,sys
P=Path('H:/.codex/gui-handoffs/20261007-auth-error-fix');R=Path.cwd();env=os.environ.copy();env.update(JAVA_HOME='H:/.jdks/jdk17',GRADLE_USER_HOME='H:/gradle',ANDROID_HOME='H:/Android',ANDROID_SDK_ROOT='H:/Android')
if sys.argv[1]=='desktop':
 for argv in [['H:/node.js/node.exe','H:/node.js/node_modules/npm/bin/npm-cli.js','ci','--ignore-scripts'],['H:/node.js/node.exe','H:/node.js/node_modules/npm/bin/npm-cli.js','run','build']]:subprocess.run(argv,cwd=R/'clients/desktop',env=env,check=True)
 subprocess.run(['H:/node.js/node.exe','tests/clients/gui/auth.mjs'],cwd=R,env=env,check=True)
else:
 subprocess.run(['H:/gradle/wrapper/dists/gradle-8.9-bin/78qddjpeqn5v6yec3xb8kv9ca/gradle-8.9/bin/gradle.bat','--no-daemon',':app:assembleDebug',':app:assembleDebugAndroidTest','-PimSendInstrumentation='+('im.platform.client.ui.GuiTrustRollbackInstrumentation' if sys.argv[1]=='android-rollback' else 'im.platform.client.ui.GuiAuthenticatedInstrumentation')],cwd=R/'clients/mobile',env=env,check=True)
print('PASS '+sys.argv[1]+' focused build/tests')