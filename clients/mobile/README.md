# Android storage slice

Approved Android Kotlin + Jetpack Compose, built-in Android SDK SQLite; no Room, network library, JS bridge or third-party testing framework. Canonical §6.1 and ADR-0005 authorize equivalent Kotlin models/Repository behavior using the same contracts/fixtures.

Build toolchain: Gradle8.9, AGP8.7.0, Kotlin/Compose compiler2.1.10, JDK17, compile/targetSDK35, minSDK26. Necessary Compose foundation/activity binding provides only a minimal validation host. Version compatibility: https://developer.android.com/build/releases/agp-8-7-0-release-notes and https://kotlinlang.org/docs/gradle-configure-project.html . Debug instrumentation uses the built-in android.app.Instrumentation runner.

From repository root: python -B tools/verify_client_sqlite.py --scope mobile --serial emulator-5554
IM_CLIENT_GRADLE may explicitly select an actual verified Gradle executable when the wrapper download is unavailable; evidence must name the fallback, and clean hosted CI still runs the official pinned wrapper. Set JAVA_HOME/ANDROID_HOME for your actual tools and select the exact real emulator serial. Missing build/runtime or failed instrumentation fails; host/mock and skipped execution never pass. APK installation targets only that explicit emulator. The verifier does not start/stop user AVDs. Local Coordinator tooling creates a separate hidden task AVD outside the checkout; existing user AVD remains untouched.

Canonical golden.json is copied byte-identically into test assets and validated against contracts. v1.sql is the independent retained old-schema fixture copied from tests/clients/sqlite/v1.sql. Instrumentation checks canonical normalized results plus migration rollback/history preservation, reopen, account isolation, identity/content conflicts, realtime-first ACK/Sync merging, terminal SENT and actual data/contiguous rollback. Synthetic local.failed fixture steps omit message content; the fixture harness seeds the matching local message before the FAILED observation, using the same case's server message. This does not change product input or wire schema.

This task establishes storage foundation, not full send/retry/Sync UI or S2 Gate PASS. Token storage and network orchestration are untouched.
