param([ValidateSet('install','rollback')][string]$Action)
$ErrorActionPreference='Stop'
Import-Module C:/Windows/System32/WindowsPowerShell/v1.0/Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1
Import-Module C:/Windows/System32/WindowsPowerShell/v1.0/Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1
$dir='H:/.codex/gui-handoffs/20261004-4f866046/gui-runtime/tls-v2'
$baseline='H:/.codex/gui-handoffs/20261004-4f866046/gui-resume-research/windows-root-baseline.json'
$thumb='7A9B96E977CEED8DB1494467CB770121746E481A'
$current=@(Get-ChildItem Cert:/CurrentUser/Root | ForEach-Object Thumbprint | Sort-Object)
if($Action -eq 'install'){
 if(Test-Path $baseline){throw 'Existing baseline; do not overwrite'}
 if((Get-FileHash "$dir/ca.der" -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'e61a24364dc95315cbdf10bb6eade27b907ff94adb71bde1c827f93a48ad0de8'){throw 'Approved fingerprint mismatch'}
 $cert=Get-PfxCertificate -FilePath "$dir/ca.der"
 if($cert.Thumbprint -ne $thumb -or $cert.NotAfter.ToUniversalTime() -le [DateTime]::UtcNow){throw 'Approved CA expired or mismatched'}
 if($current -contains $thumb){throw 'Approved CA already present'}
 $current | ConvertTo-Json | Set-Content $baseline -Encoding utf8
 Import-Certificate -FilePath "$dir/ca.der" -CertStoreLocation Cert:/CurrentUser/Root | Out-Null
 if(!(@(Get-ChildItem Cert:/CurrentUser/Root | ForEach-Object Thumbprint) -contains $thumb)){throw 'CA installation not confirmed'}
 [pscustomobject]@{action=$Action;result='PASS';thumbprint=$thumb;expiresUTC=$cert.NotAfter.ToUniversalTime().ToString('o');scope='CurrentUser/Root only'} | ConvertTo-Json
}else{
 if(!(Test-Path $baseline)){throw 'Rollback baseline unavailable'}
 $original=@(Get-Content $baseline -Raw | ConvertFrom-Json)
 if($original -contains $thumb){throw 'Refuse deletion of baseline certificate'}
 if(@(Get-ChildItem Cert:/CurrentUser/Root | ForEach-Object Thumbprint) -contains $thumb){Remove-Item -LiteralPath "Cert:/CurrentUser/Root/$thumb"}
 $after=@(Get-ChildItem Cert:/CurrentUser/Root | ForEach-Object Thumbprint | Sort-Object)
 if(Compare-Object $original $after){throw 'Root set differs after rollback'}
 [pscustomobject]@{action=$Action;result='PASS';scope='Exact newly imported thumbprint removed; baseline Root set restored'} | ConvertTo-Json
}
