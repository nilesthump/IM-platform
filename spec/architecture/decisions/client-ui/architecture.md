# 客户端 UI 架构

状态：已冻结。Human 批准的设计内容已在候选33cc754与PR12实际 main4f18d222，经新鲜独立 Review、精确 HEAD 托管 CI 和主仓库同步接受。验收证据：`spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/accepted-freeze/acceptance.md`。本状态记录不启动 GUI 实现，S2 Gate 仍为 OPEN。

## 产品与信息架构

产品名为「构界 IM+ / PlugWorldIM」，采用 Adaptive Glass Workspace。视觉重点为未来 AI 通信 50%、生产力工具 30%、开发者扩展性 20%。这些比例表达设计优先级，不承诺功能或容量。

| 一级入口 | 职责 | 边界 |
| --- | --- | --- |
| Chat | 会话列表、会话视图、消息 | 好友管理归 Friends |
| Friends | 用户搜索、好友关系、添加好友 | 好友关系和唯一私聊由服务端权威判定 |
| AI | 未来入口、插图、施工提示 | 仅占位；不实现 AI 聊天、Agent、RAG、工具调用、API 或虚假数据 |
| Plugin | 已安装插件、插件状态、插件入口 | 个人能力面板；不是商店或 Marketplace，不实现 S2 安装系统或运行时 |

Application Shell 负责一级导航、账号上下文和入口选择。后续任务授权后，仅客户端自有代码可增加 Settings/Profile 等入口。插件不得增加一级导航，不得控制 Shell、主题品牌或基础 UI 语义。插件的下级入口仍位于宿主控制的 Plugin 页面内，且必须具有可用的已授权能力；能力不存在时，应如实展示不可用状态，不得伪造已安装清单或可执行操作。

## 数据归属与流向

UI 渲染视图状态并发出用户意图。页面状态、hooks 或 ViewModel 将意图转换为既有 Repository/协议操作，并提供加载、空、错误、认证过期、连接和同步状态。Repository 负责物化数据与事务收敛；协议适配器负责规范 HTTP/WSS 的序列化和传输行为。UI 不得直接打开 SQLite、推进游标、伪造 ACK、独立写入消息状态，或判定成员身份与权限。后端职责仍遵循 §3 和 SRC-01 至 SRC-07 的 Core/Gateway/Plugin Host 边界。

Desktop/Mobile 的发送方向为：用户意图 → 已批准的发送编排 → Repository 持久化 SENDING → 传输 → 服务端 durable commit 后的 ACK → Repository UPSERT → UI 观察状态。本任务只规定方向，不实现发送编排。重试复用 request_id；FAILED 只表示该次尝试尚未确认成功；匹配的实时事件或 Sync 可收敛为 SENT；SENT 不得回退。数据和游标更新必须原子提交；用户游标不包含消息；contiguous_seq 不得越过缺口。离线历史来自按账号隔离的本地视图，随后后台 Sync；切换账号必须停止旧账号观察，且不得显示前一账号数据。

Web 仅使用内存 Repository 状态，不建立聊天数据库，不持久化历史，不承诺离线历史或跨页面生命周期的数据保留。离线和错误视图必须表达真实连接状态。本地外观偏好不得包含消息、令牌或业务数据，也不构成聊天持久化授权。

## Web

采用 React + TypeScript，定位为简洁、高效的在线通信。Shell/路由负责入口选择；页面和自定义业务组件负责展示；自定义 hooks/数据层连接 Repository 与协议操作。状态管理采用 useState/useReducer/Context/custom hooks。页面局部状态留在本页面；Context 只承载当前确实需要共享的职责。不得为假设需求增加通用事件总线、store 或 controller 层级。

路由是职责描述，不是对某个第三方路由库的授权。不选择 Zustand/Redux/MobX、数据框架或整套业务 UI 框架。图标、无障碍和工具类基础库仍需遵循依赖治理；类别名称不能批准具体库。

## Desktop

采用 Tauri + React + TypeScript，使用独立 UI，面向舒适、高频的生产力场景。更丰富的布局、交互和原生能力展示由后续限定任务实施。本决策替代原 §6.1「最大程度复用 Web UI」要求。共享协议、模型、Repository 行为、适合跨平台的 hooks、Design Token 和 UI 语义；不得共享 Button、MessageBubble、ChatWindow 等完整 React 视觉组件。不得重复协议/领域逻辑，也不得将 Desktop 原生 hooks 引入 Web。

TypeScript 负责 Repository、模型和事务意图；SQLx Rust 原生适配器仍限于连接、查询和单次原子事务。系统通知、托盘和安全存储须遵循已授权的原生边界及后续任务；本设计不增加库或功能实现。

## Mobile

采用 Android Kotlin + Jetpack Compose。UI 向 ViewModel 发出意图；ViewModel 调用 Repository 并通过 StateFlow 暴露状态；Compose 按生命周期收集该状态。StateFlow 是可观察状态，不是传输或存储层。Repository 委托给 SDK SQLite 和已授权协议适配器。Jetpack Navigation Compose 负责宿主导航。ViewModel/StateFlow/Navigation 是明确的 Human 决策，记录于规范 §6.5 / ADR-0006，而非由 Task Spec 自行选型。

必须在真实 Android Studio 模拟器中验证。Kotlin 模型、Repository、协议和插件适配器依据相同规范契约与 fixtures 实现等价行为；不要求复用 TypeScript SDK、hooks 或组件。不得引入 Room/ORM、任意网络库、JS bridge/runtime/codegen 或共享原生重写。

## 共享 UI 边界

共享设计规范、Token 含义和 UI 行为语义。Web/Desktop 共享 TypeScript protocol-sdk/plugin-sdk/models 和适用 hooks；Mobile 根据同一契约与 fixtures 实现等价 Kotlin 行为。不建立三端视觉组件库。本文件中的 UI contract 指展示义务，不建立新的机器可验证 wire/API/schema 权威；该权威仍唯一归属 contracts/。

## Plugin 与 AI 边界

S2 仅预留宿主控制的 Plugin/AI 入口。不实现 renderer、UI 代码下载或执行、远程组件注入、插件安装、动态加载或运行时。声明式投票描述仅用于说明未来设计，不定义新 schema/API，也不是 S2 实现。S4 保留 §8.2 经审查的 Custom Render Bundle 和声明式 UI，以及包/签名/哈希/schema/兼容性/权限/资源/CSP/入口校验、sandbox iframe/隔离 WebView 和白名单 Bridge。不得放宽令牌、SQLite、宿主敏感资源保护或规范插件 fixtures。AI 在单独明确 API、契约、架构决策并完成验收前始终为占位。

## 后续 GUI 的 API 覆盖

覆盖认证登录、Web/原生 refresh、logout、会话过期处理；当前用户信息；用户搜索和添加好友；会话列表/打开；消息发送/接收/状态；Sync 状态。操作必须从 contracts/http/auth-user-friend.openapi.json 和规范 WSS envelope/sync schema 解析。不得自行发明会话/消息/Sync HTTP 路由；已接受的协议契约决定传输方式与字段结构。本任务不授权修改 OpenAPI 或后端。其他既有操作或未来能力需另行限定任务。Plugin/AI 占位不得暗示缺失的后端能力已经存在。

## 交付边界

本任务不交付页面、组件、UI 交互实现、像素级设计或运行时。后续 GUI 任务必须引用独立验收后的规范架构/ADR 和 spec/acceptance/client-gui.md。架构冻结、GUI Task PASS 与 S2 Gate PASS 是三个不同结果。

## Web 后 S2 补充（ADR-0012候选）

原GUI/Web接受保持。正式生效后追加WEB→STATE→UI-REF→I18N→S2 Gate；完整要求见canonical§6.6及spec/acceptance/client-supplement.md。三产品任务backlog、逐项独立接受/集成/主仓库同步后激活下项；本次不实施，S2 OPEN。独立视觉/Repository/Auth/Send/Sync职责与原截图/Architect/Review/hosted/main链共同保留。STATE真实A/B/排序/恢复/跨端好友，UIREF完整对照回归和视觉基线，I18N三纯数据语言/固定入口/独立偏好窄授权均必需。
