param([int]$X,[int]$Y,[string]$Text="",[int]$Key=0,[switch]$Replace)
Add-Type -TypeDefinition @"
using System;using System.Runtime.InteropServices;
public static class ImLoginApi{
 [StructLayout(LayoutKind.Sequential)]public struct RECT{public int l,t,r,b;}
 [StructLayout(LayoutKind.Sequential)]public struct POINT{public int x,y;}
 [StructLayout(LayoutKind.Sequential)]public struct MI{public int x,y;public uint data,flags,time;public UIntPtr extra;}
 [StructLayout(LayoutKind.Sequential)]public struct KI{public ushort vk,scan;public uint flags,time;public UIntPtr extra;}
 [StructLayout(LayoutKind.Explicit,Size=32)]public struct U{[FieldOffset(0)]public MI mouse;[FieldOffset(0)]public KI key;}
 [StructLayout(LayoutKind.Sequential)]public struct INPUT{public uint type;public U data;}
 [DllImport("user32.dll")]public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr p);
 [DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out RECT r);
 [DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")]public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")]public static extern IntPtr WindowFromPoint(POINT p);
 [DllImport("user32.dll")]public static extern IntPtr GetAncestor(IntPtr h,uint f);
 [DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll",SetLastError=true)]public static extern uint SendInput(uint n,INPUT[] i,int s);
 public static uint Key(ushort vk,bool up){var a=new INPUT[1];a[0].type=1;a[0].data.key.vk=vk;a[0].data.key.flags=up?2u:0u;return SendInput(1,a,Marshal.SizeOf(typeof(INPUT)));}
 public static uint Click(){var a=new INPUT[2];a[0].data.mouse.flags=2;a[1].data.mouse.flags=4;return SendInput(2,a,Marshal.SizeOf(typeof(INPUT)));}
 public static uint Text(string text){var a=new INPUT[text.Length*2];for(int i=0;i<text.Length;i++){a[i*2].type=1;a[i*2].data.key.scan=text[i];a[i*2].data.key.flags=4;a[i*2+1]=a[i*2];a[i*2+1].data.key.flags=6;}return SendInput((uint)a.Length,a,Marshal.SizeOf(typeof(INPUT)));}
}
"@
$taskProcess=Get-CimInstance Win32_Process -Filter 'ProcessId=21720'
if ($taskProcess.ExecutablePath -ne 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe' -or $taskProcess.CreationDate.ToString('yyyy-MM-dd HH:mm') -ne '2026-10-08 11:28') {throw 'Client identity changed'}
$taskWindow=[IntPtr]527312
[void][ImLoginApi]::SetThreadDpiAwarenessContext([IntPtr](-4));[void][ImLoginApi]::SetForegroundWindow($taskWindow)
function Click-Fixture([int]$x,[int]$y){
 if ([ImLoginApi]::GetForegroundWindow() -ne $taskWindow){throw 'Lost client focus'}
 $taskRect=[ImLoginApi+RECT]::new();[void][ImLoginApi]::GetWindowRect($taskWindow,[ref]$taskRect)
 if (($taskRect.r-$taskRect.l) -ne 1942 -or ($taskRect.b-$taskRect.t) -ne 1273){throw 'Observed dimensions changed'}
 $taskPoint=[ImLoginApi+POINT]::new();$taskPoint.x=$taskRect.l+$x;$taskPoint.y=$taskRect.t+$y
 if ([ImLoginApi]::GetAncestor([ImLoginApi]::WindowFromPoint($taskPoint),2) -ne $taskWindow){throw 'Target is covered'}
 [void][ImLoginApi]::SetCursorPos($taskPoint.x,$taskPoint.y)
 if ([ImLoginApi]::Click() -ne 2){throw 'Click failed'}
}

foreach($taskEvent in @(@(0x11,$false),@(0x10,$false),@(0x20,$false),@(0x20,$true),@(0x10,$true),@(0x11,$true))){if([ImLoginApi]::Key([uint16]$taskEvent[0],[bool]$taskEvent[1]) -ne 1){throw 'Native registered shortcut input failed'}}
Start-Sleep -Milliseconds 300
Click-Fixture $X $Y
if($Replace){foreach($event in @(@(0x11,$false),@(0x41,$false),@(0x41,$true),@(0x11,$true))){if([ImLoginApi]::Key([uint16]$event[0],[bool]$event[1]) -ne 1){throw 'Replace chord failed'}}}
if($Text){if([ImLoginApi]::Text($Text) -ne $Text.Length*2){throw 'Text input failed'}}
if($Key){if([ImLoginApi]::Key([uint16]$Key,$false) -ne 1 -or [ImLoginApi]::Key([uint16]$Key,$true) -ne 1){throw 'Key input failed'}}
'Guarded current fixture UI input applied'

