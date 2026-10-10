# GUI 验收规范

状态：已冻结。Human 批准的设计内容已在候选33cc754与PR12实际 main4f18d222，经新鲜独立 Review、精确 HEAD 托管 CI 和主仓库同步接受。验收证据：`spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/accepted-freeze/acceptance.md`。本状态记录不启动 GUI 实现，S2 Gate 仍为 OPEN。

## 必需验收链

GUI 实现 → 真实运行截图 → Architect Review → 限定范围修复 → 新截图 → Architect Approval → 新的独立候选 Review 与适用的精确 HEAD 托管 CI → 受保护的集成/主仓库验证 → GUI Task PASS。各项审查可共享证据，但不能取消彼此独立的义务。Architect 批准展示效果；独立 Review 审查实现、权威和最小性；CI 判定适用的可执行检查。任何单项都不能建立 S2 Gate PASS。仓库规定的完整验收与集成完成前，不得进入 done。

截图是 Task 验收要求，不是可选设计反馈。每个 GUI Task 必须在实现前声明入口/运行环境矩阵和证据路径。必须捕获真实客户端运行画面，不接受 mockup 或编辑过的图片。记录 Task ID、候选 SHA、源代码/构建来源、平台/运行环境版本、不含秘密的账号/测试 fixture 标识、页面/状态、视口/窗口/设备尺寸、主题和字体/间距设置、精确复现步骤，以及图片文件名/哈希。图片不得包含真实凭据、令牌展示或私人用户数据；使用受控 fixtures。

## 最低覆盖矩阵

| 客户端 | 必需运行证据 |
| --- | --- |
| Web | 真实浏览器中的登录、Chat、Friends、AI 占位、Plugin 页面 |
| Desktop | 真实 Tauri 客户端中的主窗口、Chat、Friends、离线历史、通知/托盘、主题 |
| Mobile | 真实 Android Studio 模拟器中的登录、Chat、Friends、离线历史、Sync 状态、主题 |

Cold AI 和 Warm Creative 都必须展示一致的布局/语义；布局受影响时，覆盖支持的字体/间距极值。跨端共有入口须展示各端实际宿主布局。Desktop 通知/托盘证据须包含真实原生表面和复现步骤，仅画在应用内不能替代。Mobile 证据须标明模拟器/设备/API；宿主测试或 mock 页面不能替代。

每个范围内页面须覆盖有意义且相关的加载、空、错误和成功状态。认证须覆盖 refresh/logout/session-expired，且不暴露凭据。Chat 须展示真实 SENDING/SENT/FAILED、重试身份和收敛行为，并由可执行协议/存储证据支持；截图本身不能证明 durable ACK、去重或原子性。离线/Sync 须覆盖受控断开/重连；Web 不得宣称持久化或离线历史。主题/偏好须在允许的本地生命周期内保留，不得暗示业务数据持久化。

若某个限定 GUI Task 未实现全部矩阵界面，必须在激活前于 Task Spec 明确该切片和剩余任务。缺失证据不得计作整个客户端验收。Plugin/AI 能力不可用时，截图须如实展示预留入口、占位或不可用状态。不得伪造可工作的控件或 AI/插件数据。

## Architect 决策与修复循环

Architect Review 记录精确候选 SHA、截图清单/哈希、PASS/FAIL 决策、具体逐页面问题、所检查的信息层级/导航/可读性/主题/配置规则，以及审查者身份。FAIL 时保持任务未完成，在 allowed_paths 内修复并重新截图。既有截图与问题记录保持不可变；批准必须标明最新被接受的截图集和构建。后续视觉、状态或代码变更影响已批准证据时，必须重新捕获并再次批准。未受影响的旧图可以附哈希和理由引用，但不得重新标为新截图。

新的独立 Reviewer 检查实际 Repository/协议/状态/原生职责、源码导入、最小性、公共契约和安全边界。所有新增敏感依赖必须可追溯至已接受的规范架构/ADR；截图质量不能使框架或契约变更合法化。适用 CI 必须对应精确被审查候选 SHA 和正确的必需任务；缺失、失败、取消或异常跳过的任务不能建立 PASS。

## 证据与闭环

在 spec/progress/evidence/<GUI_TASK_ID>/ 下保存截图清单、原始图片、Architect 决策、修复迭代、独立 Review 与托管验收。Task handoff 记录命令、退出码/时长、已知失败和最后已知良好 SHA；current.md 只链接简洁恢复状态与最新稳定 checkpoint。视觉证据须绑定到集成后的产品树，声明完成前须记录任务分支/提交/同步结果/主仓库 SHA。不接受 Photoshop 或生成图片作为运行证明，不以截图替代 CI，不因单个 GUI Task 推进 Stage。

## MVP 任务归属（ADR-0007 规划候选）

新增且唯一产品 UI ID 为 LOOP1-CLIENT-GUI-001（Desktop/Mobile）；Web 完整 Loop1 GUI 使用既有 LOOP1-WEB-001。两者均覆盖 Login/session、Chat、Friends、AI Placeholder、Plugin capability/unavailable、Settings/Profile、Cold AI/Warm Creative、本地字体/间距与真实发送/重连状态。Desktop/Mobile 还覆盖 Offline History、Sync，Desktop 真实通知/托盘/快捷键，Mobile Android Studio emulator；Web 无 SQLite/离线历史，不持久化聊天。

S3 PARITY、S4 PLUGIN-UI/FIX、S5 COMPAT/RELEASE、S6 RC 在各自既有 acceptance 承接适用 GUI 要求，规则见 canonical §20；不新增 GUI E2E/parity/plugin/release/soak Task。实质视觉变化须针对最近 Architect-approved set 重新截图批准；容量测试由 load harness 承担，GUI 自动化不进入 5000 WSS 热路径。本段随 ADR-0007 独立接受后生效；既有截图与架构验收要求不降低。

## Web 后 S2 补充（ADR-0012候选）

原GUI/Web接受保持。正式生效后追加WEB→STATE→UI-REF→I18N→S2 Gate；完整要求见canonical§6.6及spec/acceptance/client-supplement.md。三产品任务backlog、逐项独立接受/集成/主仓库同步后激活下项；本次不实施，S2 OPEN。独立视觉/Repository/Auth/Send/Sync职责与原截图/Architect/Review/hosted/main链共同保留。STATE真实A/B/排序/恢复/跨端好友，UIREF完整对照回归和视觉基线，I18N三纯数据语言/固定入口/独立偏好窄授权均必需。
