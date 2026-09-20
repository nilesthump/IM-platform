[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$openApiPath = Join-Path $repoRoot 'contracts/http/auth-user-friend.openapi.json'
$errorPath = Join-Path $repoRoot 'contracts/errors/http-errors.schema.json'
$fixtureRoot = Join-Path $repoRoot 'contracts/fixtures/auth-user-friend'
$fixtureSchemaPath = Join-Path $fixtureRoot 'fixture.schema.json'
$positivePath = Join-Path $fixtureRoot 'positive.json'
$negativePath = Join-Path $fixtureRoot 'negative.json'
$failures = @()

foreach ($path in @($openApiPath, $errorPath, $fixtureSchemaPath, $positivePath, $negativePath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $failures += "missing required contract file: $path"
    }
}
if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

try { $openApiRaw = Get-Content -LiteralPath $openApiPath -Raw; $openApi = $openApiRaw | ConvertFrom-Json -Depth 100 }
catch { $failures += "OpenAPI JSON parse failed: $($_.Exception.Message)" }
try { $errorRaw = Get-Content -LiteralPath $errorPath -Raw; $errors = $errorRaw | ConvertFrom-Json -Depth 100 }
catch { $failures += "error schema JSON parse failed: $($_.Exception.Message)" }
try { $positiveRaw = Get-Content -LiteralPath $positivePath -Raw; $positive = $positiveRaw | ConvertFrom-Json -Depth 100 }
catch { $failures += "positive fixtures JSON parse failed: $($_.Exception.Message)" }
try { $negativeRaw = Get-Content -LiteralPath $negativePath -Raw; $negative = $negativeRaw | ConvertFrom-Json -Depth 100 }
catch { $failures += "negative fixtures JSON parse failed: $($_.Exception.Message)" }

if ($failures.Count -eq 0) {
    foreach ($fixturePath in @($positivePath, $negativePath)) {
        try {
            $valid = Get-Content -LiteralPath $fixturePath -Raw | Test-Json -SchemaFile $fixtureSchemaPath -ErrorAction Stop
            if (-not $valid) { $failures += "fixture schema validation returned false: $fixturePath" }
        } catch { $failures += "fixture schema validation failed: $fixturePath $($_.Exception.Message)" }
    }
}

if ($openApi.openapi -ne '3.1.0') { $failures += 'OpenAPI version must be 3.1.0' }
if ($openApi.info.version -ne '1.0.0') { $failures += 'contract version must be 1.0.0' }
$expectedPaths = @('/v1/auth/register','/v1/auth/login','/v1/auth/refresh','/v1/auth/logout','/v1/users/me','/v1/users/search','/v1/friends','/v1/friends/{friendUserId}')
$actualPaths = @($openApi.paths.PSObject.Properties.Name)
foreach ($path in $expectedPaths) { if ($path -notin $actualPaths) { $failures += "missing canonical path: $path" } }
foreach ($path in $actualPaths) {
    if ($path -match '(?i)(websocket|wss|sync|plugin|message|group|database)') { $failures += "forbidden out-of-scope path: $path" }
}

$operationIds = @()
foreach ($pathProperty in $openApi.paths.PSObject.Properties) {
    foreach ($methodProperty in $pathProperty.Value.PSObject.Properties) {
        if ($methodProperty.Name -notin @('get','post','put','delete','patch')) { continue }
        $operation = $methodProperty.Value
        if (-not $operation.operationId) { $failures += "missing operationId: $($methodProperty.Name.ToUpper()) $($pathProperty.Name)" }
        else { $operationIds += $operation.operationId }
        foreach ($parameter in @($operation.parameters)) {
            if ($parameter.in -eq 'query' -and $parameter.name -match '(?i)(token|password|secret|credential)') {
                $failures += "authentication material declared in query: $($pathProperty.Name) $($parameter.name)"
            }
        }
    }
}
$duplicates = @($operationIds | Group-Object | Where-Object Count -gt 1 | Select-Object -ExpandProperty Name)
if ($duplicates.Count -gt 0) { $failures += "duplicate operationId: $($duplicates -join ', ')" }

$clientTypes = @($openApi.components.schemas.ClientType.enum)
if (($clientTypes -join ',') -ne 'WEB,DESKTOP,MOBILE') { $failures += "client type slots must be exactly WEB,DESKTOP,MOBILE; actual=$($clientTypes -join ',')" }
foreach ($schemaName in @('LoginRequest','RefreshRequest','Session','AuthResult','NormalizedUserPair','FriendshipResult')) {
    if ($schemaName -notin @($openApi.components.schemas.PSObject.Properties.Name)) { $failures += "missing semantic schema: $schemaName" }
}
foreach ($field in @('username','password','clientType','deviceId','clientVersion','protocolVersion')) {
    if ($field -notin @($openApi.components.schemas.LoginRequest.required)) { $failures += "LoginRequest missing required field: $field" }
}
if ($openApi.components.schemas.Session.properties.sessionEpoch.type -ne 'integer') { $failures += 'Session.sessionEpoch must be an integer' }
if (@($openApi.components.schemas.RefreshRequest.allOf).Count -ne 1) { $failures += 'RefreshRequest must machine-enforce WEB cookie versus native body delivery' }
if (@($openApi.components.schemas.AuthResult.oneOf).Count -ne 2) { $failures += 'AuthResult must machine-enforce WEB versus native token delivery' }
if ($openApi.components.schemas.FriendshipResult.properties.memberUserIds.minItems -ne 2 -or $openApi.components.schemas.FriendshipResult.properties.memberUserIds.maxItems -ne 2) { $failures += 'FriendshipResult must require exactly two members' }
$bearerDescription = [string]$openApi.components.securitySchemes.bearerAuth.description
foreach ($claim in @('user_id','session_id','client_type','session_epoch','iat','exp')) {
    if ($bearerDescription -notmatch [regex]::Escape($claim)) { $failures += "access token contract missing claim: $claim" }
}
$refreshDescription = [string]$openApi.components.securitySchemes.refreshCookie.description
if ($refreshDescription -notmatch 'only its hash' -or $refreshDescription -notmatch 'independently') { $failures += 'refresh token hash-only and independent-revocation semantics are missing' }
$friendDescription = [string]$openApi.paths.'/v1/friends/{friendUserId}'.put.description
foreach ($term in @('Idempotently','normalized','single DIRECT','exactly two','atomically','no pending')) {
    if ($friendDescription -notmatch [regex]::Escape($term)) { $failures += "friend transaction description missing: $term" }
}
$loginDescription = [string]$openApi.paths.'/v1/auth/login'.post.description
foreach ($term in @('atomically revokes','increments','Other clientType slots remain valid')) {
    if ($loginDescription -notmatch [regex]::Escape($term)) { $failures += "login replacement description missing: $term" }
}

$refMatches = [regex]::Matches($openApiRaw, '"\$ref"\s*:\s*"([^"]+)"')
foreach ($match in $refMatches) {
    $ref = $match.Groups[1].Value
    if ($ref.StartsWith('#/')) {
        $segments = @($ref.Substring(2) -split '/')
        $node = $openApi
        foreach ($segment in $segments) {
            $decoded = $segment.Replace('~1','/').Replace('~0','~')
            $properties = @($node.PSObject.Properties | Where-Object { $_.Name -eq $decoded })
            if ($properties.Count -ne 1) { $failures += "unresolved internal reference: $ref"; break }
            $node = $properties[0].Value
        }
    } elseif ($ref -notmatch '^\.\./errors/http-errors\.schema\.json#/\$defs/ErrorResponse$') {
        $failures += "unexpected external reference: $ref"
    }
}

$expectedErrorCodes = @('VALIDATION_FAILED','AUTH_REQUIRED','AUTH_INVALID_CREDENTIALS','AUTH_TOKEN_INVALID','AUTH_TOKEN_EXPIRED','AUTH_SESSION_REVOKED','AUTH_SESSION_EPOCH_STALE','AUTH_CLIENT_TYPE_MISMATCH','AUTH_REFRESH_REVOKED','AUTHORIZATION_DENIED','PROTOCOL_VERSION_UNSUPPORTED','USERNAME_ALREADY_EXISTS','USER_NOT_FOUND','FRIEND_SELF_NOT_ALLOWED','FRIENDSHIP_STATE_CONFLICT')
$actualErrorCodes = @($errors.'$defs'.ErrorCode.enum)
if (($actualErrorCodes -join ',') -ne ($expectedErrorCodes -join ',')) { $failures += 'shared error code registry differs from the canonical ordered set' }
if ($errorRaw -match '(?i)"(accessToken|refreshToken|password|cookie)"\s*:') { $failures += 'error response schema exposes authentication material fields' }

$requiredPositive = @('registration-and-authorized-user-search','same-slot-login-replaces-only-that-slot','refresh-rotates-current-session-credential','logout-revokes-session-refresh-and-connection','friend-add-normalizes-and-reuses-direct')
$requiredNegative = @('invalid-credentials','token-in-query-rejected','invalid-client-type','refresh-client-type-mismatch','unsupported-protocol-version','missing-authentication','authorization-binding-mismatch','friend-self-rejected','duplicate-friendship-divergence-rejected','non-normalized-pair-divergence-rejected','stale-session-epoch-rejected','revoked-refresh-token-rejected')
if ($positive.polarity -ne 'positive') { $failures += 'positive fixture polarity is incorrect' }
if ($negative.polarity -ne 'negative') { $failures += 'negative fixture polarity is incorrect' }
foreach ($fixture in @($positive, $negative)) {
    if ((@($fixture.profiles) -join ',') -ne 'go,java') { $failures += "$($fixture.polarity) fixtures must target both go and java profiles" }
}
$positiveIds = @($positive.scenarios.id)
$negativeIds = @($negative.scenarios.id)
foreach ($id in $requiredPositive) { if ($id -notin $positiveIds) { $failures += "missing positive fixture: $id" } }
foreach ($id in $requiredNegative) { if ($id -notin $negativeIds) { $failures += "missing negative fixture: $id" } }
$allIds = @($positiveIds + $negativeIds)
$duplicateFixtureIds = @($allIds | Group-Object | Where-Object Count -gt 1 | Select-Object -ExpandProperty Name)
if ($duplicateFixtureIds.Count -gt 0) { $failures += "duplicate fixture IDs: $($duplicateFixtureIds -join ', ')" }
foreach ($scenario in @($negative.scenarios)) {
    foreach ($step in @($scenario.steps)) {
        if ($step.expected.errorCode -and $step.expected.errorCode -notin $actualErrorCodes) { $failures += "fixture uses unknown error code: $($scenario.id) $($step.expected.errorCode)" }
    }
}
if ($negativeRaw -notmatch 'token-in-query-rejected' -or $negativeRaw -notmatch 'password or token appears') { $failures += 'security negative coverage is incomplete' }
if ($positiveRaw -notmatch 'one normalized friendship exists' -or $positiveRaw -notmatch 'exactly two distinct memberships exist') { $failures += 'friend atomic-normalization assertions are incomplete' }
if ($positiveRaw -notmatch 'local SQLite or client history is deleted') { $failures += 'logout local-history non-semantics are not explicit' }

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "PASS: Auth/User/Friend OpenAPI, shared errors, refs, and golden fixtures verified paths=$($actualPaths.Count) operations=$($operationIds.Count) error_codes=$($actualErrorCodes.Count) positive=$($positiveIds.Count) negative=$($negativeIds.Count) profiles=go,java."
exit 0
