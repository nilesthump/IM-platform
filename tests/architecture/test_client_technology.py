import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('client_checker', ROOT/'ci/check_architecture.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class ClientTechnologyControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('spec/architecture/baseline.md', 'spec/architecture/frozen-architecture.md', 'spec/architecture/decisions/ADR-0005-client-technology-clarification.md', 'spec/architecture/decisions/ADR-0011-web-appearance-storage.md', 'spec/progress/evidence/LOOP1-WEB-001/freeze-20261009/human-approval.txt'):
            destination = self.root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, destination)

    def put(self, name, content):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def appearance_source(self):
        return ('const APPEARANCE_KEY = "plugworldim.appearance.v1";\n'
                'const raw = window.localStorage.getItem(APPEARANCE_KEY);\n'
                'window.localStorage.setItem(APPEARANCE_KEY, JSON.stringify({theme: valid.theme, fontSize: valid.fontSize, density: valid.density}));')

    def test_only_authorized_appearance_record_receives_bounded_storage_exception(self):
        self.put('clients/web/src/ui/appearance.ts', self.appearance_source())
        self.assertEqual([], checker.check_clients(self.root))
        for relative in ('clients/web/src/state.ts', 'clients/web/src/ui/nested/appearance.ts'):
            with self.subTest(relative=relative):
                p = self.put(relative, self.appearance_source())
                self.assertTrue(checker.check_clients(self.root))
                p.unlink()

    def test_appearance_storage_rejects_other_keys_arbitrary_data_and_business_payloads(self):
        positive = self.appearance_source()
        mutations = (
            positive.replace('plugworldim.appearance.v1', 'messages'),
            positive.replace('getItem(APPEARANCE_KEY)', 'getItem("history")'),
            positive.replace('JSON.stringify({theme: valid.theme, fontSize: valid.fontSize, density: valid.density})', 'JSON.stringify(valid)'),
            positive.replace('density: valid.density}', 'density: valid.density, messages: data}'),
            positive.replace('valid.theme', 'valid.accessToken'),
            positive + '\nconst s = window.localStorage; s.setItem("secret", value);',
            positive + '\nwindow.localStorage.clear();',
            positive + '\nwindow["localStorage"].setItem(APPEARANCE_KEY, raw);',
            positive + '\nconst db = indexedDB.open("history");',
            positive + '\nsessionStorage.setItem("appearance", raw);',
        )
        for source in mutations:
            with self.subTest(source=source):
                self.put('clients/web/src/ui/appearance.ts', source)
                self.assertTrue(checker.check_clients(self.root))

    def test_appearance_exception_fails_closed_without_matching_authority(self):
        import hashlib, json, re
        self.put('clients/web/src/ui/appearance.ts', self.appearance_source())
        approval = self.root/'spec/progress/evidence/LOOP1-WEB-001/freeze-20261009/human-approval.txt'
        original = approval.read_bytes()
        approval.write_text('not approved', encoding='utf-8')
        self.assertTrue(checker.check_clients(self.root))
        approval.write_bytes(original)
        adr = self.root/'spec/architecture/decisions/ADR-0011-web-appearance-storage.md'
        adr.unlink()
        self.assertTrue(checker.check_clients(self.root))
        shutil.copyfile(ROOT/'spec/architecture/decisions/ADR-0011-web-appearance-storage.md', adr)
        canonical = self.root/'spec/architecture/frozen-architecture.md'
        text = canonical.read_text(encoding='utf-8').replace('"plugworldim.appearance.v1"', '"history"')
        canonical.write_bytes(text.encode('utf-8'))
        baseline = self.root/'spec/architecture/baseline.md'
        baseline.write_text(re.sub(r'(?m)^- sha256: `[^`]+`$', '- sha256: `'+hashlib.sha256(canonical.read_bytes()).hexdigest()+'`', baseline.read_text(encoding='utf-8')), encoding='utf-8')
        self.assertTrue(checker.check_clients(self.root))  # Even rehashing cannot extend policy.

    def test_current_active_clients(self):
        self.assertEqual([], checker.check_clients(ROOT))

    def test_approved_ts_native_config_assets(self):
        for name, content in {
            'clients/shared/protocol-sdk/types.ts': 'export type Envelope = {request_id: string};',
            'clients/shared/ui/view.tsx': 'import React from "react"; export const View = () => <div/>;',
            'clients/web/package.json': '{"dependencies":{"react":"18","react-dom":"18"},"devDependencies":{"typescript":"5","@types/react":"18"}}',
            'clients/web/tsconfig.json': '{}',
            'clients/web/tool.config.mjs': 'export default {};',
            'clients/desktop/src-tauri/main.rs': 'fn main() {}',
            'clients/desktop/src-tauri/build.rs': 'fn main() {}',
            'clients/desktop/src-tauri/Cargo.toml': '[dependencies]\ntauri="2"\nsqlx={version="0.8",features=["sqlite"]}\n[build-dependencies]\ntauri-build="2"',
            'clients/desktop/src-tauri/capabilities/default.json': '{}',
            'clients/desktop/package.json': '{"dependencies":{"react":"18","@tauri-apps/api":"2"}}',
            'clients/mobile/app/src/main/java/im/Model.kt': 'package im; enum class State { SENDING, SENT, FAILED }',
            'clients/mobile/data/migration.sql': 'CREATE TABLE messages(id TEXT);',
            'clients/web/style.css': 'body {color:black}',
            'clients/web/logo.svg': '<svg/>',
        }.items(): self.put(name, content)
        self.assertEqual([], checker.check_clients(self.root))

    def test_forbidden_source_and_config_controls(self):
        cases = {
            'clients/shared/store.dart': 'void main() {}',
            'clients/mobile/pubspec.yaml': 'name: app',
            'clients/shared/pubspec.lock': 'packages: {}',
            'clients/desktop/.metadata': 'project_type: app',
            'clients/mobile/lib/App.swift': 'import UIKit',
            'clients/shared/repository.rs': 'fn repository() {}',
            'clients/web/src/main.js': 'export const message = {};',
            '.github/workflows/client.yml': 'steps:\n- uses: dart-lang/setup-dart@v1',
            'clients/mobile/build.yml': 'run: flutter build apk',
            'clients/mobile/native.json': '{"runtime":"expo"}',
            'clients/web/config.json': '{"runtime":"Deno"}',
            'clients/web/data.ts': 'const db = indexedDB.open("history");',
            'clients/web/storage.sql': '-- SQLite history',
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                path = self.put(name, content)
                self.assertTrue(checker.check_clients(self.root))
                path.unlink()

    def test_unapproved_generic_dependencies_and_imports(self):
        cases = {
            'clients/shared/package.json': '{"dependencies":{"new-client-framework":"1"}}',
            'clients/web/package.json': '{"devDependencies":{"new-runtime":"1"}}',
            'clients/mobile/package.json': '{"dependencies":{"react":"18"}}',
            'clients/mobile/platform.ts': 'import {x} from "new-client-framework";',
            'clients/shared/runtime.ts': 'const x = require("new-runtime");',
            'clients/shared/platform.ts': 'const x = import("new-framework");',
            'clients/desktop/src-tauri/Cargo.toml': '[dependencies]\nstorage={package="rusqlite",version="1"}',
            'clients/desktop/src-tauri/Cargo.toml.sqlx_other_db': '[dependencies]\nsqlx={version="0.8",features=["postgres"]}',
            'clients/desktop/sql_calls.ts': 'import Database from "@tauri-apps/plugin-sql"; db.execute("BEGIN"); db.execute("INSERT"); db.execute("COMMIT");',
            'clients/desktop/src-tauri/Cargo.toml.target': '[target.windows.dependencies]\nnew-native="1"',
            '.github/workflows/client.yml': 'run: npm install new-client-framework',
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                if name.endswith('.target'): name = name.removesuffix('.target')
                if name.endswith('.sqlx_other_db'): name = name.removesuffix('.sqlx_other_db')
                path = self.put(name, content)
                self.assertTrue(checker.check_clients(self.root))
                path.unlink()

    def test_task_paths_and_passing_tests_cannot_approve_framework(self):
        task = '# Allowed Paths\n- `clients/mobile/**`\n# Technology Authorization\nclient_framework: NewFramework\nclient_runtime: NewRuntime\n# Verification\nTests PASS\n'
        errors = checker.client_task_violations(task, 'spec/tasks/active/TASK.md', self.root)
        self.assertTrue(any('NewFramework' in error for error in errors))
        self.assertTrue(any('NewRuntime' in error for error in errors))
        self.assertTrue(checker.client_task_violations(task.replace('NewFramework', 'React'), 'TASK.md', self.root))
        valid = 'client_language: TypeScript\nclient_framework: React\nclient_runtime: Tauri\nclient_dependency: typescript\n'
        self.assertEqual([], checker.client_task_violations(valid, 'TASK.md', self.root))
        native = '# Allowed Paths\n- `clients/desktop/src-tauri/**`\nclient_dependency: sqlx\nclient_language: Rust\n'
        self.assertEqual([], checker.client_task_violations(native, 'TASK.md', self.root))
        self.assertTrue(checker.client_task_violations(native.replace('clients/desktop/src-tauri/', 'clients/shared/'), 'TASK.md', self.root))

    def test_authority_missing_or_mutated_is_failure(self):
        self.put('spec/architecture/frozen-architecture.md', 'client_framework: NewFramework')
        self.assertTrue(checker.check_clients(self.root))
        self.assertTrue(checker.client_task_violations('client_framework: NewFramework', 'TASK.md', self.root))

    def test_history_is_not_active_client_implementation(self):
        self.put('research/runs/immutable/example.dart', 'void main() {}')
        self.put('spec/progress/evidence/HISTORICAL/pubspec.yaml', 'dependencies: flutter')
        self.assertEqual([], checker.check_clients(self.root))

    def test_symlink_cannot_bypass_boundary(self):
        source = self.put('archive/bad.dart', 'void main() {}')
        link = self.root/'clients/shared/store.ts'
        link.parent.mkdir(parents=True)
        try: link.symlink_to(source)
        except OSError:
            # Windows without symlink privilege still exercises the rejection branch.
            from unittest.mock import patch
            self.put('clients/shared/store.ts', 'export const x = 1;')
            original = Path.is_symlink
            with patch.object(Path, 'is_symlink', lambda path: path == link or original(path)):
                self.assertTrue(checker.check_clients(self.root))
        else:
            self.assertTrue(checker.check_clients(self.root))


    def test_android_compose_gradle_source_and_tooling(self):
        fixtures = {
            'clients/mobile/build.gradle.kts': 'plugins {\n id("com.android.application") version "8.9.0" apply false\n id("org.jetbrains.kotlin.android") version "2.1" apply false\n id("org.jetbrains.kotlin.plugin.compose") version "2.1" apply false\n}',
            'clients/mobile/app/build.gradle.kts': 'plugins {\n id("com.android.application")\n kotlin("android")\n id("org.jetbrains.kotlin.plugin.compose")\n}\ndependencies {\n implementation(platform("androidx.compose:compose-bom:2025.01"))\n implementation("androidx.compose.ui:ui:1.7")\n implementation("androidx.activity:activity-compose:1.10")\n implementation(libs.compose.material3)\n}',
            'clients/mobile/gradle/libs.versions.toml': '[versions]\ncompose="1.7"\n[libraries]\ncompose-material3={module="androidx.compose.material3:material3",version.ref="compose"}\n[plugins]\nandroid-application={id="com.android.application",version="8.9"}',
            'clients/mobile/data/build.gradle': 'plugins {\n id "com.android.library"\n id "org.jetbrains.kotlin.android"\n}\ndependencies {\n implementation "org.jetbrains.kotlin:kotlin-stdlib:2.1"\n}',
            'clients/mobile/settings.gradle.kts': 'rootProject.name="IM"\ninclude(":app", ":data")',
            'clients/mobile/gradle/wrapper/gradle-wrapper.properties': 'distributionUrl=https\\://services.gradle.org/distributions/gradle-8.13-bin.zip',
            'clients/mobile/gradle/wrapper/gradle-wrapper.jar': 'standard wrapper fixture',
            'clients/mobile/gradlew': '#!/bin/sh\nexec java org.gradle.wrapper.GradleWrapperMain "$@"',
            'clients/mobile/app/src/main/AndroidManifest.xml': '<manifest package="im"><application/></manifest>',
            'clients/mobile/app/src/main/java/im/Main.kt': 'package im\nimport android.database.sqlite.SQLiteDatabase\nimport androidx.activity.ComponentActivity\nimport androidx.compose.runtime.Composable\nimport kotlin.collections.List\nimport im.data.State\n@Composable fun Main() {}',
            'clients/mobile/data/src/main/java/im/data/State.kt': 'package im.data\nenum class State { SENDING, SENT, FAILED }',
            '.github/workflows/android.yml': 'jobs:\n  mobile:\n    steps:\n      - uses: android-actions/setup-android@v3\n      - uses: gradle/actions/setup-gradle@v4\n      - uses: reactivecircus/android-emulator-runner@v2\n        with:\n          script: cd clients/mobile && ./gradlew connectedCheck',
        }
        for name, content in fixtures.items(): self.put(name, content)
        self.assertEqual([], checker.check_clients(self.root))
        self.put('clients/mobile/app/build.gradle.kts', 'plugins {\n alias(libs.plugins.android.application)\n}\ndependencies {\n implementation(libs.compose.material3)\n}')
        self.assertEqual([], checker.check_clients(self.root))
        declarations = '# Allowed Paths\n- `clients/mobile/**`\nclient_language: Kotlin\nclient_framework: Jetpack Compose\nclient_runtime: Android\nclient_dependency: androidx.compose.ui:ui\nclient_dependency: com.android.application\nclient_dependency: Gradle\n'
        self.assertEqual([], checker.client_task_violations(declarations, 'TASK.md', self.root))
        mixed = declarations.replace('- `clients/mobile/**`', '- `clients/mobile/**`\n- `clients/shared/**`\n- `clients/desktop/**`')
        self.assertEqual([], checker.client_task_violations(mixed, 'TASK.md', self.root))
        for old, new in [('Kotlin','TypeScript'), ('Jetpack Compose','React'), ('Android','Tauri'), ('androidx.compose.ui:ui','androidx.room:room-runtime')]:
            with self.subTest(new=new):
                self.assertTrue(checker.client_task_violations(declarations.replace(old, new), 'TASK.md', self.root))
        self.assertTrue(checker.client_task_violations(declarations.replace('clients/mobile/', 'clients/shared/'), 'TASK.md', self.root))

    def test_android_plugin_declarations_fail_closed(self):
        cases = {
            'variable-apply': 'def selected = "java"\napply plugin: selected',
            'variable-apply-approved-value': 'def selected = "com.android.application"\napply plugin: selected',
            'unresolved-get-alias': 'plugins { alias(libs.plugins.unapproved.get()) }',
            'dynamic-alias': 'plugins { alias(libs.plugins[selected]) }',
            'dynamic-get-alias': 'plugins { alias(selected.get()) }',
            'wrong-catalog-alias': 'plugins { alias(libs.unapproved) }',
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                self.put('clients/mobile/build.gradle.kts' if 'alias' in name else 'clients/mobile/build.gradle', content)
                errors = checker.check_clients(self.root)
                self.assertTrue(errors, name)
                self.assertTrue(any('plugin' in error for error in errors), errors)
                for suffix in ('.gradle', '.gradle.kts'):
                    (self.root/('clients/mobile/build' + suffix)).unlink(missing_ok=True)

    def test_android_literal_and_direct_catalog_plugins_remain_approved(self):
        self.put('clients/mobile/gradle/libs.versions.toml', '[plugins]\nandroid-application={id="com.android.application",version="8.9"}')
        cases = (
            'apply plugin: "com.android.application"',
            "apply plugin: 'org.jetbrains.kotlin.android'",
            'plugins { id("com.android.application") }',
            'plugins { id "com.android.application" }',
            'plugins { alias(libs.plugins.android.application) }',
        )
        for content in cases:
            with self.subTest(content=content):
                self.put('clients/mobile/build.gradle', content)
                self.assertEqual([], checker.check_clients(self.root))

    def test_android_plugin_selectors_require_complete_literal_arguments(self):
        cases = (
            'id("com.android.application".replace("com.android.application", "java"))',
            'id("com.android.application" + ".unapproved")',
            'id("com.android.${selected}")',
            'id(selected)',
            'id "com.android.application" + ".unapproved"',
            'kotlin("android".replace("android", "multiplatform"))',
            'kotlin("android" + ".unapproved")',
            'kotlin("${selected}")',
            'kotlin(selected)',
        )
        for suffix in ('.gradle', '.gradle.kts'):
            for declaration in cases:
                with self.subTest(suffix=suffix, declaration=declaration):
                    self.put('clients/mobile/build' + suffix, 'plugins { ' + declaration + ' }')
                    errors = checker.check_clients(self.root)
                    self.assertTrue(any('plugin' in error for error in errors), errors)
            (self.root/('clients/mobile/build' + suffix)).unlink()

    def test_android_plugin_block_shortcuts_and_generic_apply_fail_closed(self):
        # These ordinary Kotlin DSL forms apply builtin Java plugins at runtime.
        for source in ('plugins { java }', 'plugins { application }',
                       'plugins { `java-library` }', 'plugins { java', 'apply<JavaPlugin>()',
                       'plugins.apply<JavaPlugin>()'):
            with self.subTest(source=source):
                self.put('clients/mobile/build.gradle.kts', source)
                errors = checker.check_clients(self.root)
                self.assertTrue(any('plugin' in error for error in errors), errors)

    def test_android_unsupported_plugin_applications_fail_closed(self):
        # Gradle9.1/Java25 confirms these application forms apply builtin Java.
        forms = (
            "plugins.apply 'java'", "pluginManager.apply 'java'",
            "def selected = 'java'\nplugins.apply selected",
            "def selected = pluginManager\nselected.apply 'java'",
            "apply { plugin 'java' }",
            "def selected = pluginManager.&apply\nselected('java')",
            'plugins.apply("java")', 'apply<JavaPlugin>()',
            "plugins.apply 'com.android.application'",
            "apply plugin: 'com.android.application'\nplugins.apply 'java'",
        )
        for source in forms:
            with self.subTest(source=source):
                self.put('clients/mobile/build.gradle', source)
                errors = checker.check_clients(self.root)
                self.assertTrue(any('plugin' in error for error in errors), errors)

    def test_android_quoted_member_dispatch_fails_closed(self):
        # Review proved literal quoted dispatch applies builtin Java in Gradle.
        # Quoted/dynamic members are outside the supported direct declaration DSL.
        forms = (
            "plugins.'apply'('java')",
            'pluginManager."apply"("java")',
            "def selected = pluginManager.&'apply'\nselected('java')",
            "def selected = 'apply'\nplugins.\"${selected}\"('java')",
            "pluginManager?.'apply'('java')",
            "def selected = pluginManager\nselected.'apply'('java')",
            "plugins.'apply'('com.android.application')",
            "dependencies.'add'(configuration, selected)",
            'def selected = "apply"\nplugins./${selected}/("java")',
            'def selected = "apply"\npluginManager.$/${selected}/$("java")',
        )
        for source in forms:
            with self.subTest(source=source):
                self.put('clients/mobile/build.gradle', source)
                errors = checker.check_clients(self.root)
                self.assertTrue(any('plugin' in error for error in errors), errors)

    def test_android_quoted_dispatch_text_remains_data(self):
        forms = (
            'def note = "plugins.\'apply\'(\'java\')"',
            "def note = 'pluginManager.\"apply\"(\"java\")'",
            "// plugins.'apply'('java')\napply plugin: 'com.android.application'",
            "/* pluginManager.\"apply\"(\"java\") */\nplugins { id 'com.android.library' }",
            'def note = ' + '"' * 3 + "plugins.'apply'('java')\npluginManager.&'apply'" + '"' * 3,
            "def note = " + "'" * 3 + 'pluginManager."apply"("java")\nplugins."${selected}"' + "'" * 3,
            "def note = \"text.\"\n'data'",
            "def note = /plugins.'apply'('java')/",
            "def note = $/plugins.'apply'('java')/$",
        )
        for source in forms:
            with self.subTest(source=source):
                self.put('clients/mobile/build.gradle', source)
                self.assertEqual([], checker.check_clients(self.root))

    def test_android_supported_apply_and_quoted_contexts_remain_approved(self):
        forms = (
            "apply plugin: 'com.android.application'",
            "apply plugin: 'org.jetbrains.kotlin.android'; apply plugin: 'org.jetbrains.kotlin.plugin.compose'",
            "// plugins.apply 'java'\napply plugin: 'com.android.application'",
            "/* apply { plugin 'java' } */\napply plugin: 'com.android.library'",
            'def note = "pluginManager.apply"',
            "def note = 'apply'",
            'def note = ' + '"' * 3 + 'plugins.apply\napply' + '"' * 3,
            'def note = ' + "'" * 3 + 'pluginManager.&apply\napply' + "'" * 3,
            "plugins { id 'com.android.application' version '8.9' apply false }\napply plugin: 'org.jetbrains.kotlin.android'",
        )
        for source in forms:
            with self.subTest(source=source):
                self.put('clients/mobile/build.gradle', source)
                self.assertEqual([], checker.check_clients(self.root))

    def test_android_complete_literal_plugin_notations_remain_approved(self):
        self.put('clients/mobile/gradle/libs.versions.toml',
                 '[plugins]\nandroid-application={id="com.android.application",version="8.9"}')
        for source in (
            'plugins { id("com.android.application") version "8.9" apply false }',
            "plugins { id 'com.android.library' version '8.9' apply false }",
            'plugins { kotlin("android") version "2.1" apply false }',
            "plugins { kotlin('plugin.compose') }",
            'plugins { id("com.android.application").version("8.9").apply(false) }',
            'plugins { alias(libs.plugins.android.application) apply false }',
            'plugins {\n id ( "com.android.application" )\n kotlin ( "android" )\n}',
            'plugins { id("com.android.application"); kotlin("android") }',
            'plugins { kotlin("android") }\nkotlin { jvmToolchain(17) }',
        ):
            with self.subTest(source=source):
                self.put('clients/mobile/build.gradle.kts', source)
                self.assertEqual([], checker.check_clients(self.root))

    def test_android_negative_real_gradle_catalog_import_build_workflow_controls(self):
        cases = {
            'clients/mobile/model.ts': 'export type Model = {};',
            'clients/mobile/build.config.js': 'module.exports={};',
            'clients/mobile/tsconfig.json': '{}',
            'clients/mobile/build.gradle.kts': 'plugins {\n id("org.jetbrains.kotlin.multiplatform")\n}',
            'clients/mobile/build.gradle': 'apply plugin: "org.jetbrains.compose"',
            'clients/mobile/app/build.gradle.kts': 'dependencies {\n implementation("androidx.room:room-runtime:2.6")\n}',
            'clients/mobile/app/network.gradle': 'dependencies {\n implementation "com.squareup.okhttp3:okhttp:4"\n}',
            'clients/mobile/app/kotlin.gradle.kts': 'dependencies {\n implementation("io.ktor:ktor-client-core:3")\n}',
            'clients/mobile/app/dynamic.gradle': 'dependencies {\n implementation selectedNativeRuntime\n}',
            'clients/mobile/app/alias.gradle.kts': 'dependencies {\n implementation(libs.new.runtime)\n}',
            'clients/mobile/app/plugin.gradle.kts': 'plugins {\n id(selectedFramework)\n}',
            'clients/mobile/app/local.gradle.kts': 'dependencies {\n implementation(files("native-runtime.jar"))\n}',
            'clients/mobile/gradle/libs.versions.toml': '[plugins]\nnew-framework={id="org.jetbrains.compose",version="1"}',
            'clients/mobile/gradle/dependency/libs.versions.toml': '[libraries]\nroom={module="androidx.room:room-runtime",version="2"}',
            'clients/mobile/app/Model.kt': 'package im\nimport androidx.room.Room\nclass Model',
            'clients/mobile/app/Network.kt': 'package im\nimport okhttp3.OkHttpClient\nclass Network',
            'clients/mobile/app/Bridge.kt': 'package im\nfun bridge(v: android.webkit.WebView) { v.addJavascriptInterface(Object(), "bridge") }',
            'clients/mobile/app/Runtime.kt': 'package im\nfun load() { System.loadLibrary("customRuntime") }',
            'clients/shared/model.kt': 'package im\nclass Model',
            'clients/mobile/app/native.rs': 'fn main() {}',
            'clients/mobile/build.sh': 'cd clients/mobile\nnpm install typescript',
            'clients/mobile/gradle/wrapper/gradle-wrapper.properties': 'distributionUrl=https://example.invalid/selected-runtime.zip',
            '.github/workflows/android.yml': 'jobs:\n  mobile:\n    steps:\n      - uses: actions/setup-node@v4\n      - run: cd clients/mobile && npm install typescript',
            '.github/workflows/tool.yml': 'jobs:\n  mobile:\n    steps:\n      - uses: unapproved/setup-android@v1',
            '.github/workflows/build.yml': 'jobs:\n  mobile:\n    steps:\n      - run: cd clients/mobile && ./gradlew -I select-runtime.gradle build',
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                path = self.put(name, content)
                errors = checker.check_clients(self.root)
                self.assertTrue(errors, name)
                self.assertTrue(any('CLIENT' in error for error in errors), errors)
                path.unlink()

if __name__ == '__main__': unittest.main()