$env:JAVA_HOME='H:/jdk-25.0.2'
$env:GRADLE_USER_HOME='H:/.codex/evidence/gradle-guard-independent-review-20261001/gradle-runtime-cache-9'
& 'H:/jdk-25.0.2/bin/java.exe' -version
& 'C:/Users/21441/.gradle/wrapper/dists/gradle-9.1.0-all/bmafxlsgu9ht0l6ebxq31nf0s/gradle-9.1.0/bin/gradle.bat' --no-daemon --offline -p H:/.codex/evidence/gradle-guard-independent-review-20261001/gradle-runtime-probe tasks --all
exit $LASTEXITCODE