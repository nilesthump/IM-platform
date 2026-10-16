# ADR-0013：建群、成员添加与三端群聊接入规划

状态：Human-approved candidate，APPROVED_PENDING_FREEZE；fresh 常规独立 Review → different fresh 错误处理专项 → exact-head hosted CI → protected integration → actual-main 验证与 H:/IM-platform 安全同步后生效。
日期：2026-10-15
任务：LOOP1-GROUP-PLAN-001
批准来源：spec/progress/evidence/LOOP1-GROUP-PLAN-001/human-request.txt；authorization.md 记录授权边界。
semantic_change=true；沿用 v1.1。前 canonical SHA256 efbe04c7eb308904d1759b8e145a32363620ed8c14daef58f09c644bdc897bdc；PDF/旧 ADR/接受及 FAIL 历史不改。

## 现需求与最小决定

原§4.3只明确从发起者好友建群，现公共HTTP没有建群/加人/非好友群成员名称查询，三端会话入口以好友DIRECT为基线。Human明确将群聊补齐为S2前置。新增且唯一产品Task LOOP1-GROUP-001，标题“建群、成员添加与三端群聊接入”；依赖 LOOP1-CLIENT-I18N-001 与本规划正式接受、受保护集成/actual-main/主目录同步，安排 I18N→GROUP→S2 Gate。原补充三任务、语言激活 I18N 的身份/phase及旧门禁继续有效。本轮不实现或激活产品，GROUP backlog/S2 OPEN。

创建者从自己的好友列表选一个或多个不同用户，原子创建一个GROUP并自动成为有效成员；他不能代替另一用户声明操作者身份。任意有效群成员均可选一个或多个其本人好友加入同群；不要求OWNER、不要求新成员与创建者或其他成员为好友。服务端以数据库权威Session、GROUP kind、操作者有效成员和每个目标的操作者好友关系鉴权；UI限制不能替代。创建者自身由服务端加入，目标列表去重后不含操作者。已有有效成员作为无新增变化处理，但仍校验该请求目标的本人好友资格；任一目标无效则整个请求拒绝，无部分成功。无退群/移除/审批/管理权限/群名编辑/陌生人邀请。

## 幂等、事务与真实失败

创建幂等身份为操作者+create request_id；加人为操作者+conversation+add request_id，操作类型分隔。重试绑定规范化目标集合；同身份同集合返回原始提交结果，同身份异内容明确冲突，不创建第二群/成员/逻辑事件。目标顺序无业务语义，重复目标先规范化；不同request的重叠或并发加人最终每群每用户一个有效成员，已在群目标不重复写变更事件。原子事务在Core内校验、写Conversation/新增成员、必要持久幂等结果、所有受影响用户低频Sync事件和对应Outbox后COMMIT才成功。并发同key必须归并；失败回滚全部新效果。现schema已具GROUP、create唯一键、成员主键、Sync/Outbox，优先复用；加人原结果重放确需最小持久操作收据，未来contract migration先定义并独立接受，不引入通用工作流/消息投递表/新服务。

每次调用先验证当前身份/授权，重放也不得越权。响应丢失/超时或commit结果未知只能诚实呈现未获确认，客户端保留原request和目标重试，不能换ID自动创建或宣称已回滚/未提交。明确失败显示可行动错误；未知异常/内部错误/不变量破坏传播并使操作失败。已有结果重放不重复mutation，必要资源清理/回滚不掩盖根因。

## 契约先行及现有链路

未来GROUP的首个独立契约切片在contracts/http/group.openapi.json定义建群、加人、本人会话快照查询；明确字段、身份、结果、状态/错误码及幂等冲突。既有错误目录能表示者复用，新增条目只在contracts/errors/http-errors.schema.json及fixtures中共同冻结；具体wire/schema不是本ADR或实现的第二权威。数据库仅必要additive migration，不改0001历史。相同contract输入约束后续Java parity，不提前实现S3。

低频conversation.changed/membership.changed只承载已有User Sync事件形状，受影响范围覆盖全部有效群成员（含新成员）及其各端；每个实际成员变化与事件/outbox同事务。事件消费者用授权会话快照取得GROUP、成员与最小用户展示身份，包括并非自己好友的C，按revision幂等刷新；名称是数据，不翻译。在线沿现有通知/周期User Sync触发更新，断线/NATS漏失由持久cursor补偿；消息保持现有conversation seq与Sync。新成员有效后能按现有成员鉴权查询该群已提交消息，MVP不引入join-seq历史过滤。Web仍只当前在线页面窗口，不新增离线历史；Desktop/Mobile依现有账号SQLite/数据游标原子UPSERT。

发送复用 message.send/成员鉴权/seq/原request幂等/durable ACK/单Message单Outbox/分发与Sync，发言者按senderId关联群成员userId及真实displayName显示，防重名/无好友关系混淆。Gateway只代理/连接/local fan-out，不拥有好友/成员决策；Core承载事务，shared仅契约传输类型支持。无需新WSS命令或消息ACK语义。

## 三端与验收

沿用React/TypeScript Web memory-only、Tauri/React/TypeScript Desktop+已有SQLx原子native边界、Android Kotlin/Compose/SDK SQLite。复用已接受i18n en/zh-CN/ja-JP、新入口/选择/加载空错成功/未确认与重试/成员和sender标签及无障碍键统一占位参数；语言偏好adapter/激活任务保持I18N。无新库/runtime/bridge/数据库框架。

强制spec/acceptance/group.md：A-B好友，A建群+B；B-C好友且A-C非好友，B加C；三者获得群会话、互发并辨认身份。拒绝非成员、非好友/混合非法批次，重复/并发、事务注入回滚、提交前与提交后响应丢失同ID重试、跨端和离线补偿。真实Go/PG/NATS/TLS、浏览器/安装Tauri/Android Studio emulator入口，三端真实截图及Architect批准；截图不替代事务/权限证据。每最终SHA全新两审、精确CI/受保护合入/actual-main/主目录同步均必须，Task PASS不等于S2 PASS。

## 兼容、回滚与最小性

本轮无产品/数据库迁移。未来只增量契约/必要schema，保留旧DIRECT/HTTP/WSS/ACK/Sync与旧客户端支持窗口；契约切片先提交独立接受并记录精确SHA，产品才实现。不能满足兼容/架构时BLOCKED_BY_ARCHITECTURE提出最小问题。产品回滚依现有expand/migrate/switch/contract和已验证制品，不删除旧数据/清空用户库。群大小仍按既有阶梯负载证据决定，不新增拍脑袋人数上限；传输资源界限须在契约中明确但不变成未经依据的产品容量宣称。

机器策略/checker直接验证唯一队列、串行依赖、planning接受/主目录同步、GROUP完成metadata/证据和S2阻断；这些只是结构必要条件，独立Review仍检查原件/实际逻辑/真实required jobs。仅标准库和现有流程，无通用调度或未来功能。
