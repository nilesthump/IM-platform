[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('go', 'java')][string]$Profile)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$compose = Join-Path $root 'deploy/compose.yaml'
$project = "im-infra-smoke-$Profile-$PID"
$port = if ($Profile -eq 'go') { 18443 } else { 18444 }
$expected = @('postgres', 'nats', "gateway-$Profile", "core-$Profile", "plugin-host-$Profile", "tls-$Profile")
$opposite = if ($Profile -eq 'go') { 'java' } else { 'go' }
$env:IM_HTTPS_PORT = [string]$port
$env:COMPOSE_PROGRESS = 'quiet'

function Compose([string[]]$Arguments) {
    & docker compose -f $compose -p $project --profile $Profile @Arguments
    if ($LASTEXITCODE -ne 0) { throw "docker compose $($Arguments -join ' ') failed: $LASTEXITCODE" }
}

function Read-TlsResponse([string]$Path, [string[]]$Headers) {
    $tcp = [System.Net.Sockets.TcpClient]::new('127.0.0.1', $port)
    try {
        $tls = [System.Net.Security.SslStream]::new($tcp.GetStream(), $false, { $true })
        try {
            $tls.AuthenticateAsClient('localhost')
            if ($tls.SslProtocol -eq [System.Security.Authentication.SslProtocols]::None -or -not $tls.RemoteCertificate) {
                throw 'TLS handshake or server certificate missing'
            }
            $request = "GET $Path HTTP/1.1`r`nHost: localhost`r`n" + (($Headers | ForEach-Object { "$_`r`n" }) -join '') + "Connection: close`r`n`r`n"
            $bytes = [System.Text.Encoding]::ASCII.GetBytes($request)
            $tls.Write($bytes, 0, $bytes.Length)
            $tls.Flush()
            $reader = [System.IO.StreamReader]::new($tls, [System.Text.Encoding]::UTF8, $false, 1024, $true)
            $status = $reader.ReadLine()
            $responseHeaders = @{}
            while (($line = $reader.ReadLine()) -ne '') {
                if ($null -eq $line) { throw 'TLS response ended before headers' }
                $parts = $line.Split(':', 2)
                if ($parts.Count -eq 2) { $responseHeaders[$parts[0].ToLowerInvariant()] = $parts[1].Trim() }
            }
            $body = if ($Path -eq '/__infra/health') { $reader.ReadToEnd() } else { '' }
            return @{ Status = $status; Headers = $responseHeaders; Body = $body; Protocol = $tls.SslProtocol }
        } finally { $tls.Dispose() }
    } finally { $tcp.Dispose() }
}

function Test-JavaAuthTransport([string]$base, [int]$port) {
    $username = "tls$([Guid]::NewGuid().ToString('N'))"
    $password = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    # This disposable Compose endpoint uses Caddy's local CA. Certificate
    # bypass is confined to this smoke client; TLS handshake is asserted above.
    $registration = Invoke-RestMethod -Uri "$base/v1/auth/register" -Method Post -SkipCertificateCheck -ContentType 'application/json' -Body (@{ username=$username; password=$password; displayName='TLS fixture' } | ConvertTo-Json)
    $login = Invoke-RestMethod -Uri "$base/v1/auth/login" -Method Post -SkipCertificateCheck -ContentType 'application/json' -Body (@{ username=$username; password=$password; clientType='DESKTOP'; deviceId='tls-smoke'; clientVersion='1.0.0'; protocolVersion='1' } | ConvertTo-Json)
    if ($login.session.userId -ne $registration.user.userId -or $login.session.status -ne 'ACTIVE') { throw 'TLS Auth session mismatch' }
    $socket = [System.Net.WebSockets.ClientWebSocket]::new()
    $socket.Options.SetRequestHeader("Origin",$base)
    $httpHandler = [System.Net.Http.HttpClientHandler]::new()
    $httpHandler.ServerCertificateCustomValidationCallback = [System.Net.Http.HttpClientHandler]::DangerousAcceptAnyServerCertificateValidator
    $invoker = [System.Net.Http.HttpMessageInvoker]::new($httpHandler)
    $timeout = [System.Threading.CancellationTokenSource]::new([TimeSpan]::FromSeconds(10))
    try {
        $socket.ConnectAsync([Uri]"wss://localhost:$port/v1/ws",$invoker,$timeout.Token).GetAwaiter().GetResult()
        $requestId = [Guid]::NewGuid().ToString()
        $frame = @{protocolVersion='1.0';type='auth.bind';requestId=$requestId;payload=@{accessToken=$login.tokens.accessToken}} | ConvertTo-Json -Depth 5 -Compress
        $bytes = [Text.Encoding]::UTF8.GetBytes($frame)
        $socket.SendAsync([ArraySegment[byte]]::new($bytes),[System.Net.WebSockets.WebSocketMessageType]::Text,$true,$timeout.Token).GetAwaiter().GetResult()
        $buffer = [byte[]]::new(65536)
        $result = $socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),$timeout.Token).GetAwaiter().GetResult()
        if (-not $result.EndOfMessage -or $result.MessageType -ne [System.Net.WebSockets.WebSocketMessageType]::Text) { throw 'TLS auth.ack frame invalid' }
        $ack = [Text.Encoding]::UTF8.GetString($buffer,0,$result.Count) | ConvertFrom-Json
        if ($ack.type -ne 'auth.ack' -or $ack.requestId -ne $requestId -or $ack.payload.status -ne 'bound' -or $ack.payload.sessionId -ne $login.session.sessionId) { throw 'TLS WSS bind failed' }
        Invoke-WebRequest -Uri "$base/v1/auth/logout" -Method Post -SkipCertificateCheck -Headers @{Authorization="Bearer $($login.tokens.accessToken)"} | Out-Null
        $result = $socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),$timeout.Token).GetAwaiter().GetResult()
        $event = [Text.Encoding]::UTF8.GetString($buffer,0,$result.Count) | ConvertFrom-Json
        if ($event.type -ne 'session.revoked' -or $event.payload.reason -ne 'LOGOUT') { throw 'TLS logout event absent' }
    } finally { $socket.Dispose(); $invoker.Dispose(); $timeout.Dispose() }
}

$primaryFailed = $false
try {
    Compose @('config', '--quiet')
    Compose @('up', '-d', '--build')
    $running = @(& docker compose -f $compose -p $project --profile $Profile ps --services --status running)
    if ($LASTEXITCODE -ne 0) { throw 'docker compose ps failed' }
    foreach ($service in $expected) {
        if ($service -notin $running) { throw "missing running service: $service" }
    }
    foreach ($service in @("gateway-$opposite", "core-$opposite", "plugin-host-$opposite", "tls-$opposite")) {
        if ($service -in $running) { throw "opposite profile started: $service" }
    }
    Compose @('exec', '-T', 'postgres', 'pg_isready', '-U', 'im', '-d', 'im')
    Compose @('exec', '-T', 'nats', 'wget', '-q', '-O', '/dev/null', 'http://127.0.0.1:8222/healthz')
    # JSON aggregation preserves row boundaries even for unknown versions
    # containing commas or newlines; native psql failure remains an error.
    $migrationJson = @(& docker compose -f $compose -p $project --profile $Profile exec -T postgres psql -U im -d im -Atc 'SELECT json_agg(version ORDER BY version) FROM schema_migrations')
    if ($LASTEXITCODE -ne 0 -or $migrationJson.Count -ne 1) { throw "canonical migration query failed: $migrationJson" }
    $migration = ConvertFrom-Json -InputObject $migrationJson[0] -NoEnumerate
    if (-not ($migration -is [array]) -or $migration.Count -ne 2 -or $migration[0] -cne '0001_initial' -or $migration[1] -cne '0002_group_operations') { throw "canonical migration missing: $migrationJson" }
    $health = Read-TlsResponse '/__infra/health' @()
    if ($Profile -eq 'java') {
        # Caddy can start before the JVM has bound its listener. Only 502 is
        # retried, bounded; all other status and transport failures remain errors.
        $deadline = [DateTime]::UtcNow.AddSeconds(45)
        while ($health.Status -match '^HTTP/1\.[01] 502 ' -and [DateTime]::UtcNow -lt $deadline) {
            Start-Sleep -Milliseconds 250
            $health = Read-TlsResponse '/__infra/health' @()
        }
    }
    if ($health.Status -notmatch '^HTTP/1\.[01] 200 ' -or $health.Body.Trim() -ne "profile=$Profile role=gateway") {
        throw "HTTPS gateway response invalid: $($health.Status) $($health.Body)"
    }
    $key = 'dGhlIHNhbXBsZSBub25jZQ=='
    $wsPath = if ($Profile -eq 'java') { '/v1/ws' } else { '/__infra/ws' }
    $ws = Read-TlsResponse $wsPath @('Upgrade: websocket', 'Connection: Upgrade', 'Sec-WebSocket-Version: 13', "Sec-WebSocket-Key: $key")
    if ($ws.Status -notmatch '^HTTP/1\.[01] 101 ' -or $ws.Headers['sec-websocket-accept'] -ne 's3pPLMBiTxaQ9kYGzzhZRbK+xOo=') {
        throw "WSS gateway upgrade invalid: $($ws.Status)"
    }
    if ($Profile -eq 'java') {
        $base = "https://localhost:$port"
        foreach ($origin in @($base, 'http://tauri.localhost', 'https://foreign.invalid')) {
            $probe = Read-TlsResponse '/v1/ws' @('Upgrade: websocket', 'Connection: Upgrade', 'Sec-WebSocket-Version: 13', "Sec-WebSocket-Key: $key", "Origin: $origin", 'X-Forwarded-Host: foreign.invalid', 'X-Forwarded-Proto: https', 'Forwarded: host=foreign.invalid;proto=https')
            $status = if ($origin -eq 'https://foreign.invalid') {403} else {101}
            if ($probe.Status -notmatch "^HTTP/1\.[01] $status ") { throw "Browser Origin policy mismatch: $($probe.Status)" }
        }

        Test-JavaAuthTransport $base $port
    }
} catch {
    $primaryFailed = $true
    throw
} finally {
    try {
        Compose @('down', '--volumes', '--remove-orphans') | Out-Host
    } catch {
        if (-not $primaryFailed) { throw }
        # Cleanup cannot replace a pending primary failure; report its own
        # original error while the primary exception continues to propagate.
        Write-Error -ErrorRecord $_ -ErrorAction Continue
    } finally {
        Remove-Item Env:IM_HTTPS_PORT -ErrorAction SilentlyContinue
        Remove-Item Env:COMPOSE_PROGRESS -ErrorAction SilentlyContinue
    }
}
Write-Output "PASS: $Profile profile, PostgreSQL migration, Core NATS, HTTPS and WSS over $($health.Protocol)"
