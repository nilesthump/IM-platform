Set-Location clients/shared/local-store
dart format lib test
if($LASTEXITCODE){exit $LASTEXITCODE}
dart test test/user_event_test.dart
exit $LASTEXITCODE
