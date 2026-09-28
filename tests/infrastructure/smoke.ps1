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
    $migration = & docker compose -f $compose -p $project --profile $Profile exec -T postgres psql -U im -d im -Atc 'SELECT version FROM schema_migrations'
    if ($LASTEXITCODE -ne 0 -or ($migration -join '').Trim() -ne '0001_initial') { throw "canonical migration missing: $migration" }
    $health = Read-TlsResponse '/__infra/health' @()
    if ($health.Status -notmatch '^HTTP/1\.[01] 200 ' -or $health.Body.Trim() -ne "profile=$Profile role=gateway") {
        throw "HTTPS gateway response invalid: $($health.Status) $($health.Body)"
    }
    $key = 'dGhlIHNhbXBsZSBub25jZQ=='
    $ws = Read-TlsResponse '/__infra/ws' @('Upgrade: websocket', 'Connection: Upgrade', 'Sec-WebSocket-Version: 13', "Sec-WebSocket-Key: $key")
    if ($ws.Status -notmatch '^HTTP/1\.[01] 101 ' -or $ws.Headers['sec-websocket-accept'] -ne 's3pPLMBiTxaQ9kYGzzhZRbK+xOo=') {
        throw "WSS gateway upgrade invalid: $($ws.Status)"
    }
    Write-Output "PASS: $Profile profile, PostgreSQL migration, Core NATS, HTTPS and WSS over $($health.Protocol)"
} finally {
    & docker compose -f $compose -p $project --profile $Profile down --volumes --remove-orphans | Out-Host
    Remove-Item Env:IM_HTTPS_PORT -ErrorAction SilentlyContinue
    Remove-Item Env:COMPOSE_PROGRESS -ErrorAction SilentlyContinue
}
