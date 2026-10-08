$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Net.Http
$client=[System.Net.Http.HttpClient]::new();$client.Timeout=[TimeSpan]::FromSeconds(8)
try{$response=$client.GetAsync('https://localhost:8443/__infra/health').GetAwaiter().GetResult();@{time=[DateTimeOffset]::Now.ToString('o');default_windows_tls_success=$true;status=[int]$response.StatusCode;no_custom_ca_or_validation_callback=$true;pid=$PID;parent_pid=(Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId}|ConvertTo-Json|Set-Content -LiteralPath H:/.codex/gui-handoffs/20261008-ca-desktop/default-tls-after-rollback-detailed.json -Encoding utf8}
catch{$taskErrors=@();$taskException=$_.Exception;while($taskException){$taskErrors+=$taskException.Message;$taskException=$taskException.InnerException};@{time=[DateTimeOffset]::Now.ToString('o');pid=$PID;parent_pid=(Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId;default_windows_tls_success=$false;no_custom_ca_or_validation_callback=$true;error_chain=$taskErrors;error=$_.Exception.Message}|ConvertTo-Json|Set-Content -LiteralPath H:/.codex/gui-handoffs/20261008-ca-desktop/default-tls-after-rollback-detailed.json -Encoding utf8}finally{$client.Dispose()}


