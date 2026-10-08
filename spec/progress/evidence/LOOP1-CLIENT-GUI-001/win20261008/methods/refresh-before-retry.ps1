$ErrorActionPreference='Stop'
$root='H:/.codex/gui-handoffs/20261008-ca-desktop'
& "$root/action-shortcut.ps1" -X 120 -Y 1050
& "$root/action-shortcut.ps1" -X 1380 -Y 580
Start-Sleep -Milliseconds 800
& "$root/action-shortcut.ps1" -X 120 -Y 270
& "$root/action-shortcut.ps1" -X 550 -Y 500
& "$root/message-scroll.ps1" -X 1500 -Y 850
& "$root/capture.ps1" -Name chat-retry-after-fresh-session
'Controlled session explicitly refreshed; current retry presentation captured'
