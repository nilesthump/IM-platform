param([Parameter(Mandatory=$true)][ValidateSet('shared','desktop','mobile')][string]$Scope, [string]$Serial)
$arguments = @('-B', (Join-Path $PSScriptRoot 'verify_client_sqlite.py'), '--scope', $Scope)
if ($Serial) { $arguments += @('--serial', $Serial) }
python @arguments
exit $LASTEXITCODE
