param([ValidateSet('sent','sending','failed','retried','reconnected')][string]$Phase='sent')
$ErrorActionPreference='Stop'
$taskDatabase=Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'im.platform.desktop/im-4dada728-e56b-48a0-a84c-d8ae88507adc.sqlite'
& 'C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -Xutf8 -B H:/.codex/gui-handoffs/20261008-ca-desktop/read-sqlite.py $taskDatabase $Phase
if($LASTEXITCODE -ne 0){throw 'Controlled native SQLite snapshot failed'}
@{phase=$Phase;parent_pid=(Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId;actual_profile_path_resolved=$true}|ConvertTo-Json|Set-Content ("H:/.codex/gui-handoffs/20261008-ca-desktop/sqlite-$Phase-context.json") -Encoding utf8
