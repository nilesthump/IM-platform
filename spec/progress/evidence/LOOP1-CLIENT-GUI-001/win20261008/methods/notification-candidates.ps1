$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;using System.Runtime.InteropServices;public static class ImNativeCenterPixels{[StructLayout(LayoutKind.Sequential)]public struct K{public ushort vk,scan;public uint flags,time;public UIntPtr extra;}[StructLayout(LayoutKind.Explicit,Size=32)]public struct U{[FieldOffset(0)]public K key;}[StructLayout(LayoutKind.Sequential)]public struct I{public uint type;public U data;}[DllImport("user32.dll")]static extern uint SendInput(uint n,I[] a,int s);[DllImport("user32.dll")]public static extern int GetSystemMetrics(int n);[DllImport("user32.dll")]public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr p);public static void Key(ushort k,bool up){var a=new I[1];a[0].type=1;a[0].data.key.vk=k;a[0].data.key.flags=up?2u:0u;if(SendInput(1,a,Marshal.SizeOf(typeof(I)))!=1)throw new Exception("Native center key failed");}public static void Toggle(){Key(0x5b,false);Key(0x4e,false);Key(0x4e,true);Key(0x5b,true);}}
"@
[void][ImNativeCenterPixels]::SetThreadDpiAwarenessContext([IntPtr](-4))
[void][ImNativeCenterPixels]::SetThreadDpiAwarenessContext([IntPtr](-4))
if([ImNativeCenterPixels]::GetSystemMetrics(0) -ne 2560 -or [ImNativeCenterPixels]::GetSystemMetrics(1) -ne 1600){throw 'Observed monitor dimensions changed'}
$rows=@()
foreach($step in 0..2){if($step -gt 0){[ImNativeCenterPixels]::Toggle();Start-Sleep -Milliseconds 1100};$b=[Drawing.Bitmap]::new(495,272);$g=[Drawing.Graphics]::FromImage($b);try{$g.CopyFromScreen(2040,90,0,0,$b.Size);$b.Save("H:/.codex/gui-handoffs/20261008-ca-desktop/native-notification-candidate-$step.png",[Drawing.Imaging.ImageFormat]::Png)}finally{$g.Dispose();$b.Dispose()};$rows+=@{step=$step;time=(Get-Date).ToString('o');region_x=2040;region_y=90;width=495;height=272;raw_native_pixels_no_edit=$true}}
@{parent_pid=(Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId;two_native_toggles_restore_start_state=$true;state_unproven_until_raw_inspection=$true;captures=$rows}|ConvertTo-Json -Depth 5|Set-Content H:/.codex/gui-handoffs/20261008-ca-desktop/native-notification-candidates.json -Encoding UTF8
'Native notification region candidates captured; original raw pixels'
