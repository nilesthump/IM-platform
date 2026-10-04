# 剩余 GUI 验证的最小执行决定
本文件是待决方案，不是执行授权。GUI active/S2 OPEN；未安装证书、未推送、未同步。

## Windows：原方案已批准，仅缺稳定的实际确认界面
原始 CA SHA256 e61a24364dc95315cbdf10bb6eade27b907ff94adb71bde1c827f93a48ad0de8；Windows thumbprint7A9B96E977CEED8DB1494467CB770121746E481A；subject IM GUI owned fixture 20261004。到期2026-10-05 03:20:46 Asia/Shanghai（2026-10-04T19:20:46.586064Z）。到期后停止，替换 CA 必须另行批准。
仅允许原公开 ca.der 到 CurrentUser/Root，禁止 LocalMachine。用户手动稳定操作或可正常操作的支持工具窗口均可完成同一已批准方案，无需重复扩大信任审批。公开文件 H:/.codex/gui-handoffs/20261004-4f866046/gui-runtime/tls-v2/ca.der。正常证书导入向导选择当前用户、受信任的根证书颁发机构，核对上述身份后确认；仅原 CA。不能以命令“成功”判断安装成功，独立 fresh .NET/certutil/实际客户端默认 TLS 必须验证。
本次 certutil成功但三种视图均证明未安装；normal向导窗口瞬间变更后消失，未发任何系统 UI 输入，原因未知，不归因为用户取消。目前 Root 完全等于新基线，相关导入进程已退出。得到稳定确认后启动精确受控 fixture、完成真实客户端认证矩阵；结束仅删除新增原 thumbprint，集合与基线比较、默认 TLS 拒绝、清理 fixture。无需放宽 TLS 或其他系统保护。

## Android：请求批准具体测试工具方法替代
原方案明确只读 bind被拒绝必须停止；该条件已满足。以下新 root执行测试工具方法需明确批准后才能实施，不因“继续”自动获得授权。
目的：绕过 Toybox mount对 bind/remount标志的可能解释差异，直接发起同一个只读 bind操作，不改变任何产品 TLS、系统分区、SELinux、boot、系统属性或 APK。诊断仅是上游 Toybox0.8.9源码推断，未证明该 Android patched二进制的实际 syscall；源码https://github.com/landley/toybox/blob/0.8.9/toys/lsb/mount.c 。不得声称已修复当前 image。
具体工具：小型临时 C测试程序，源码/审查/hash记录保存在本任务 evidence及私有 android-mount-helper目录；仅使用已安装 H:/Android/ndk/28.2.13676358/toolchains/llvm/prebuilt/windows-x86_64/bin/x86_64-linux-android34-clang.cmd，API34/x86_64，禁止安装依赖。它不是产品语言/运行时/依赖或 native business迁移，不进入 APK；产品 Kotlin/TypeScript/Rust责任保持原样。
设备路径固定 /data/local/tmp/im-gui-mount-ro，数据目录固定 /data/local/tmp/im-gui-ca，目标固定 /apex/com.android.conscrypt/cacerts；仅既有 IMClientSend34/emulator5590/API34。
程序无网络、日志不含密钥；拒绝 root以外调用和额外参数，拒绝路径不一致/非目录。核心两个调用：
1. mount(SOURCE,TARGET,NULL,MS_BIND,NULL)；
2. mount(NULL,TARGET,NULL,MS_REMOUNT|MS_BIND|MS_RDONLY,NULL)。
任一失败立即停止并返回 errno；第二步失败立即卸载本次刚创建的 overlay。外层先注册本次 namespace/mount记录，再调用，避免进程中止后遗失回滚信息。拒绝已有 overlay或原 CA/temp碰撞；init及每个 zygote namespace使用原 nsenter。核对新增 mount ID、source/root与 topmost目标 mount（不得匹配底层旧 ro mount），statvfs ST_RDONLY、原完整证书集合+仅原 CA及其 hash、fresh app namespace实际继承；只读确认通过前不得登录。
建议命令形状（尚未执行）：NDK clang -O2 -Wall -Wextra -Werror mount-ro.c -o mount-ro；adb -s emulator-5590 push mount-ro /data/local/tmp/im-gui-mount-ro；固定命名 nsenter --mount=/proc/<本次核对PID>/ns/mnt -- /data/local/tmp/im-gui-mount-ro。完整固定路径源码已准备于 tests/clients/gui/android_mount_ro.c；已有 NDK clang.exe --target=x86_64-linux-android34 -O2 -Wall -Wextra -Werror 本地交叉编译通过。源码 SHA256 ffe199bd1b9b3700cad0575d0df5f93622cc20311f6e42f2122852894848baba；私有7752字节程序 SHA256 7f2e3b906d3ef36227d7d56c4c3c1856af7e32103c248d2e8655ef1bbc615577，路径 H:/.codex/gui-handoffs/20261004-4f866046/gui-second-resume-research/android-mount-helper/mount-ro。尚未 adb push、运行/root/mount，设备方法未批准。审批应覆盖该精确源码/二进制及上述固定路径；独立只读安全检查可在批准前完成。
仍保持 SELinux Enforcing；若执行/挂载/只读/实际 SDK TLS被拒绝，停止该证明并按日志回滚，不 relabel、关闭 SELinux、改policy/boot/system/APEX、添加 APK TLS例外或替换 CA。
回滚检查点：只停止本任务 app，按本次精确namespace/mountID卸载、仅删除固定新测试程序及原临时目录、移除本任务reverse；仅本AVD reboot无修改snapshot/无wipe；fresh app原证书文件/hash完全恢复、默认TLS拒绝、Enforcing/ro.debuggable不变、adb unroot。异常回滚立即阻塞，不继续采集。原 CA到期条件同上。
决定问题：是否批准这一小型临时 root测试工具，仅用于执行原来计划的内存只读 bind，并坚持上述停止/回滚边界？不批准则 Android认证GUI仍等待另行批准的兼容测试环境；不得改个人AVD或共享系统镜像。
