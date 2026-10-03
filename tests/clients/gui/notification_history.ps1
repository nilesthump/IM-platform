# Read only the installed owned application's notification metadata.
# No global settings, other app histories, XML payloads or private notifications.
$ErrorActionPreference='Stop'
$notificationManager=[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]
$notifier=$notificationManager::CreateToastNotifier('im.platform.desktop')
$history=$notificationManager::History.GetHistory('im.platform.desktop')
[pscustomobject]@{AppUserModelId='im.platform.desktop';NativeSetting=$notifier.Setting.ToString();OwnedHistoryCount=$history.Count} | ConvertTo-Json
