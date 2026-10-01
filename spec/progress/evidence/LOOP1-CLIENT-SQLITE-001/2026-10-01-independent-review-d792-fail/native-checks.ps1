$ErrorActionPreference='Stop'
foreach ($p in @('clients/shared/local-store','clients/desktop/storage','clients/mobile/storage')) {
 Push-Location $p
 try {
 dart pub get --enforce-lockfile
 if($LASTEXITCODE){exit $LASTEXITCODE}
 dart format --output=none --set-exit-if-changed lib test
 if($LASTEXITCODE){exit $LASTEXITCODE}
 dart analyze --fatal-infos
 if($LASTEXITCODE){exit $LASTEXITCODE}
 dart test
 if($LASTEXITCODE){exit $LASTEXITCODE}
 } finally {Pop-Location}
}
