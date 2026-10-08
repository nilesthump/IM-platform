$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @"
using System;using System.Runtime.InteropServices;using System.Text;
public static class ImOwnedCredRead {
 [StructLayout(LayoutKind.Sequential)] public struct CRED {public uint Flags,Type;public IntPtr TargetName,Comment;public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;public uint Size;public IntPtr Blob;public uint Persist,Count;public IntPtr Attributes,Alias,User;}
 [DllImport("advapi32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool CredReadW(string target,uint type,uint flags,out IntPtr p);
 [DllImport("advapi32.dll")]static extern void CredFree(IntPtr p);
 public static string Metadata(){IntPtr p;if(!CredReadW("https://localhost:8443/current.im.platform.desktop",1,0,out p)){if(Marshal.GetLastWin32Error()==1168)return null;throw new Exception("Owned metadata read failed");}try{var c=(CRED)Marshal.PtrToStructure(p,typeof(CRED));if(c.Size>512)throw new Exception("Owned metadata bound exceeded");var b=new byte[c.Size];Marshal.Copy(c.Blob,b,0,b.Length);return Encoding.Unicode.GetString(b);}finally{CredFree(p);}}
 public static bool Present(string slot){IntPtr p;if(!CredReadW(slot+".im.platform.desktop",1,0,out p)){if(Marshal.GetLastWin32Error()==1168)return false;throw new Exception("Owned slot presence read failed");}try{var c=(CRED)Marshal.PtrToStructure(p,typeof(CRED));return c.Size>0;}finally{CredFree(p);}}
}
"@
$taskSlot=[ImOwnedCredRead]::Metadata()
if($taskSlot -and $taskSlot -notmatch '^https://localhost:8443/825d00d7-a621-4307-b3ae-a501f65f8c14/[0-9a-f-]{36}$'){throw 'Expected fixture account metadata mismatch'}
$taskResult=@{time=(Get-Date).ToString('o');parent_pid=(Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId;only_owned_pointer_and_slot_presence=$true;refresh_token_value_read=$false;pointer_present=($null -ne $taskSlot);owned_slot=$taskSlot;owned_slot_present=($taskSlot -and [ImOwnedCredRead]::Present($taskSlot))}
$taskFormer=(Get-Content -LiteralPath 'H:/.codex/gui-handoffs/20261008-ca-desktop/credential-riley-before-logout.json' -Raw | ConvertFrom-Json).owned_slot
if($taskFormer -notmatch '^https://localhost:8443/825d00d7-a621-4307-b3ae-a501f65f8c14/[0-9a-f-]{36}$'){throw 'Former fixture metadata mismatch'}
$taskResult.former_owned_slot_present=[ImOwnedCredRead]::Present($taskFormer)
$taskResult|ConvertTo-Json|Set-Content -LiteralPath H:/.codex/gui-handoffs/20261008-ca-desktop/credential-riley-after-logout.json -Encoding UTF8
'Controlled native credential presence recorded; no token value read'



