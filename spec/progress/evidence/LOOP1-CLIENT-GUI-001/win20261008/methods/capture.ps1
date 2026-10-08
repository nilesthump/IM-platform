param([ValidatePattern("^[a-z0-9-]+$")][string]$Name)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;using System.Runtime.InteropServices;
public static class ImCaptureApi { [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr context);
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int Left,Top,Right,Bottom;}
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr window,out RECT rect);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr window,IntPtr dc,uint flags);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr window,out uint pid);
}
"@
$taskPid=21720
$taskProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$taskPid"
if ($taskProcess.ExecutablePath -ne 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe') { throw 'Unexpected client process' }
$taskWindow=[IntPtr]527312
[uint32]$taskWindowPid=0
[void][ImCaptureApi]::GetWindowThreadProcessId($taskWindow,[ref]$taskWindowPid)
if ($taskWindowPid -ne $taskPid) { throw 'Window ownership changed' }
[void][ImCaptureApi]::SetThreadDpiAwarenessContext([IntPtr](-4))
$taskRect=[ImCaptureApi+RECT]::new()
if (-not [ImCaptureApi]::GetWindowRect($taskWindow,[ref]$taskRect)) { throw 'Window rectangle unavailable' }
$taskBitmap=[Drawing.Bitmap]::new($taskRect.Right-$taskRect.Left,$taskRect.Bottom-$taskRect.Top)
$taskGraphics=[Drawing.Graphics]::FromImage($taskBitmap)
$taskDc=$taskGraphics.GetHdc()
try { $taskCaptured=[ImCaptureApi]::PrintWindow($taskWindow,$taskDc,2) } finally { $taskGraphics.ReleaseHdc($taskDc);$taskGraphics.Dispose() }
try { if (-not $taskCaptured) { throw 'PrintWindow failed' }; $taskBitmap.Save(('H:/.codex/gui-handoffs/20261008-ca-desktop/'+$Name+'.png'),[Drawing.Imaging.ImageFormat]::Png) } finally { $taskBitmap.Dispose() }
Write-Output 'Native PrintWindow target-only capture saved; current source cc13 package'





