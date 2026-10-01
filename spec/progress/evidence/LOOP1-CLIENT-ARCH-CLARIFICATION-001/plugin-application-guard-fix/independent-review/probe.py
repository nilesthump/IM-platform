import json, pathlib, shutil, importlib.util
ROOT=pathlib.Path('H:/icp'); OUT=pathlib.Path('H:/.codex/evidence/plugin-guard-final-independent-review-20261001')
spec=importlib.util.spec_from_file_location('check', ROOT/'ci/check_architecture.py'); check=importlib.util.module_from_spec(spec); spec.loader.exec_module(check)
probe=OUT/'probes'; probe.mkdir(exist_ok=True)
for f in ('spec/architecture/baseline.md','spec/architecture/frozen-architecture.md','spec/architecture/decisions/ADR-0005-client-technology-clarification.md'):
 p=probe/f; p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/f,p)
cases={
 'old-variable-apply':'def selected = "java"\napply plugin: selected',
 'old-get-alias':'plugins { alias(libs.plugins.unapproved.get()) }',
 'old-literal-transform':'plugins { id("com.android.application".replace("com.android.application", "java")) }',
 'java-shortcut':'plugins { java }',
 'typed-apply':'apply<JavaPlugin>()',
 'groovy-plugin-container-command':"plugins.apply 'java'",
 'groovy-plugin-manager-command':"pluginManager.apply 'java'",
 'groovy-plugin-container-parentheses':'plugins.apply("java")',
 'approved-id':'plugins { id("com.android.application") version "8.9" apply false }',
 'approved-kotlin':'plugins { kotlin("android") }\nkotlin { jvmToolchain(17) }',
 'approved-groovy':"plugins { id 'com.android.library' version '8.9' apply false }",
 'approved-apply':"apply plugin: 'org.jetbrains.kotlin.android'"
}
p=probe/'clients/mobile/build.gradle'; p.parent.mkdir(parents=True,exist_ok=True)
results={}
for name,source in cases.items():
 p.write_text(source,encoding='utf8'); results[name]={'source':source,'errors':check.check_clients(probe)}
for name in ('groovy-plugin-container-command','groovy-plugin-manager-command'):
 runtime=OUT/name; runtime.mkdir(exist_ok=True)
 (runtime/'settings.gradle').write_text("rootProject.name='independent-plugin-probe'",encoding='utf8')
 (runtime/'build.gradle').write_text(cases[name]+"\ntasks.register('proof') { doLast { println('UNAPPROVED_JAVA_PLUGIN_APPLIED=' + plugins.hasPlugin('java')) } }\n",encoding='utf8')
(OUT/'independent-probes.json').write_text(json.dumps(results,indent=2),encoding='utf8'); print(json.dumps(results,indent=2))
