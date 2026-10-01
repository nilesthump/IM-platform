from pathlib import Path
import subprocess,json,hashlib,sys
r=Path('H:/.codex/evidence/plugin-application-guard-fix-20261001')
forms={"container-command":"plugins.apply 'java'","manager-command":"pluginManager.apply 'java'","container-variable":"def selected = 'java'\nplugins.apply selected","closure":"apply { plugin 'java' }","method-reference":"def selected = pluginManager.&apply\nselected('java')"}
results={}
for name,source in forms.items():
 p=r/('runtime-'+name);p.mkdir(exist_ok=True)
 (p/'settings.gradle').write_text("rootProject.name='proof'\n")
 (p/'build.gradle').write_text(source+"\ntasks.register('proof') { doLast { println('UNAPPROVED_JAVA_PLUGIN_APPLIED=' + plugins.hasPlugin('java')) } }\n")
 argv=['pwsh','-NoProfile','-Command',"$env:JAVA_HOME='H:/jdk-25.0.2'; $env:GRADLE_USER_HOME='"+str(r/'gradle-cache')+"'; & 'C:/Users/21441/.gradle/wrapper/dists/gradle-9.1.0-all/bmafxlsgu9ht0l6ebxq31nf0s/gradle-9.1.0/bin/gradle.bat' --no-daemon --offline -p '"+str(p)+"' proof; exit $LASTEXITCODE"]
 x=subprocess.run(argv,capture_output=True)
 (r/(name+'.stdout.raw')).write_bytes(x.stdout);(r/(name+'.stderr.raw')).write_bytes(x.stderr)
 results[name]=dict(source=source,argv=argv,exit=x.returncode,applied=b'UNAPPROVED_JAVA_PLUGIN_APPLIED=true' in x.stdout,stdout_sha256=hashlib.sha256(x.stdout).hexdigest(),stderr_sha256=hashlib.sha256(x.stderr).hexdigest())
 print(name,results[name]['exit'],results[name]['applied'])
(r/'runtime-proofs.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(x['exit']==0 and x['applied'] for x in results.values())
