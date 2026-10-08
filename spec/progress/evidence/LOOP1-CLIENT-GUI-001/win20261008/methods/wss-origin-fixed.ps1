$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Net.Http
$rows=@()
foreach($origin in @('','http://tauri.localhost')){
 $socket=[Net.WebSockets.ClientWebSocket]::new();$timeout=[Threading.CancellationTokenSource]::new();$timeout.CancelAfter(8000)
 try{if($origin){$socket.Options.SetRequestHeader('Origin',$origin)};$socket.ConnectAsync([Uri]'wss://localhost:8443/v1/ws',$timeout.Token).GetAwaiter().GetResult();$rows+=@{origin=if($origin){$origin}else{'absent'};opened=($socket.State -eq 'Open')}}
 catch{$e=$_.Exception;$errors=@();while($e){$errors+=$e.Message;$e=$e.InnerException};$rows+=@{origin=if($origin){$origin}else{'absent'};opened=$false;errors=$errors}}
 finally{$socket.Abort();$socket.Dispose();$timeout.Dispose()}
}
@{parent_pid=(Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId;default_os_tls=$true;no_auth_tokens_or_messages=$true;rows=$rows}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath H:/.codex/gui-handoffs/20261008-ca-desktop/wss-origin-fixed.json -Encoding utf8

