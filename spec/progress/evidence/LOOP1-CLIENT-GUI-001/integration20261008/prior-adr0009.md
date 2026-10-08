# ADR-0009：最小原生 GUI 能力与外观存储

状态：Human-approved freeze candidate；APPROVED_PENDING_FREEZE。新独立 Review、适用 exact-head hosted CI、protected integration/actual-main 验证及安全同步至 H:/IM-platform 后才生效。
日期：2026-10-04
任务：LOOP1-CLIENT-NATIVE-ARCH-001
批准来源：spec/progress/evidence/LOOP1-CLIENT-GUI-001/readiness/human-decisions.md 与 authority-gap.md；本任务 approval.md 保存精确批准与范围。
semantic_change=true；保留 v1.1。

## 当前需要与决策

已接受 GUI 要求原生 refresh persistence、HTTPS auth/Sync、真实通知/tray/global shortcut 与持久化外观。现 Desktop 是存储宿主；SyncHttp 已支持 injected fetch。Human 单独批准八个装配文件范围后明确批准该最小前置方案并继续。范围许可不是技术权威；本 ADR 冻结具体选型。

Desktop 首次真实验收目标是 Windows。必要 Rust 限于 clients/desktop/src-tauri；批准 reqwest 原生 HTTPS、keyring/Windows Credential Manager refresh credential、官方 tauri-plugin-notification 与 tauri-plugin-global-shortcut；tray 使用已有 Tauri feature。相较手写 Win32 FFI，这些窄适配器直接满足当前职责。产品实施时将具体支持的版本/features 锁定于 Cargo.lock 并独立 Review；本次不安装依赖、不预言测试结果，不授权额外前端 plugin package、其他 OS 或替代库。

HTTPS 使用系统证书/主机名验证，仅 HTTPS、禁重定向，保持应用序列化 request bytes/headers 与响应 status/headers/body bytes，不解释协议。禁止证书绕过、token query/logging 或 backend/CORS 替代入口。TypeScript UI/auth application 通过既有 SyncHttp injected-fetch 与规范 auth 调用组合传输；原生层不拥有 login/refresh/logout 编排、request schema、Repository、ACK/retry/Sync 或业务授权；既有 WSS/protocol 职责不变。

Desktop keyring 按 app/account/session 隔离 refresh credential；TypeScript 持有 auth lifecycle、账号隔离及 replacement/logout/expiry cleanup intent。存储失败不得明文降级；access credential 为临时。官方 notification/global-shortcut 仅提供 OS presentation/input，应用决定动作。Windows 通知验收必须使用已安装、有自身身份的客户端包，开发 PowerShell toast 不可代替；tray/shortcut 同样需要真实客户端行为。

Desktop app-owned app_data JSON、Android SDK SharedPreferences 只持久化 Cold AI/Warm Creative theme 与 font-size/density 标量。外观存储不得包含 credential/message/sync cursor/account Repository data，与账号 SQLite 分离。

Android 使用 Android Keystore AES/GCM 非导出密钥保护 refresh credential，SDK SharedPreferences 仅存 ciphertext 及必要 IV/metadata；Kotlin 持有 auth lifecycle/cleanup/account isolation，无明文降级。SDK HttpsURLConnection 使用系统证书/主机名验证、HTTPS-only、禁重定向及 exact serialized bytes；不增加 network/ORM/JS runtime/bridge/codegen dependency。Kotlin 等价 Repository/protocol/model 行为仍依据同一 canonical contracts/fixtures 和真实 Android Studio emulator 验收。

## 最小性、权威与兼容

只增加当前 GUI 必需的适配器/外观选型，不增加 generic framework、未来 OS 机制或 plugin runtime。TypeScript/Kotlin 保留 application/business/Repository/protocol 职责；Desktop SQLx 原子事务意图不变。无 database schema、ACK、public API、compatibility、backend/CORS、AI、plugin sandbox/security boundary 或 source dependency direction 改动。

canonical §6.1/§6.5/native_packages 枚举窄权威；ADR-0005 仍为基础 stack/policy marker，ADR-0009 为追加谱系。先前 canonical ef90846ba380df14086795a3c58aef43f6503447fe0cb83ee2d0772d725d8e03、PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510、v1.1、旧 ADR/历史证据不变。

## 生效与回滚

GUI 依赖本任务，在独立接受、集成、actual-main 验证及安全同步前仍为 backlog。S1 PASS/S2 OPEN；local/Recorder PASS 不是 Task/Stage 接受。FAIL 在授权范围修复后由新独立 Agent Review。本次无数据/产品迁移；生效后修正需新批准 ADR 与独立接受，保留历史。

## Human 指定统一候选批次（2026-10-04；取代单独前置接受时序）

最新精确 Human 指令：完成GUI任务后统一审查推送。来源：spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/unified-batch.md，原始 prompt 与 SHA 记录于 linked Recorder P-UNIFIED-20261004。

此指令只对本次已明确批准的 native/appearance freeze + LOOP1-CLIENT-GUI-001 授权统一本地候选准备：GUI 可以使用本 ADR 已批准并写入本地 frozen candidate 的具体选择继续实现，不等待单独 native Task 接受/推送。此前“GUI 保持 backlog 直到前置独立接受”时序被本精确指令取代；不是取消独立 Review/CI，也不是认定候选权威已正式生效。canonical §6.1 候选待接受及 §2.3 全局流程不改，本窄 ACP/ADR 指令不扩展到其他任务。

native Task 仍为 review/pending，GUI 按实际输入经过 backlog -> ready -> active；已接受 SQLITE/UI-ARCH/SEND/SYNC 依赖不变，native 同批候选依赖例外明确追溯到上述 Human 指令。既有八个装配路径、选型、契约/存储/安全/ACK/职责边界不变，不新增技术。完成完整 GUI 与截图/Architect 审阅后，对精确完整候选进行 fresh independent Review，统一推送、适用 exact-head hosted CI、protected integration/actual-main 验证与安全主仓库同步；两任务 done、正式生效及 S2 Gate 判断均延后到各自适用接受条件满足。此前独立 native Review 已取消，不能记为 PASS；无 hosted 接受或推送事实。
