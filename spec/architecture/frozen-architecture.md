# 面向十万级在线连接的可扩展分布式即时通信平台

**架构基线 v1.1 · Frozen Architecture · Loop 1 执行版**

**正式架构方案 · Loop 1 可执行基线 · AI Agent 工作手册**

## 决策状态

本文件把当前对话中已冻结的架构决策固化为唯一执行基线。新 Agent 可据此启动，但不得绕过 contracts/ 中的机器可验证公共契约，也不得把未来目标写成当前能力。

| 文档属性 | 值 |
| --- | --- |
| 版本 | v1.1 |
| 基线日期 | 2026-09-30（原始基线 2026-09-19） |
| 执行周期 | Loop 1: 三个月 / 12 周预算窗口 |
| 推进机制 | 里程碑门禁驱动；Gate 提前通过即可立即进入下一阶段 |
| 当前容量验收 | 单机 8C / 16GB / 3TB；5000 authenticated WSS users |
| 未来容量目标 | Loop 2: 双机十万认证连接、N+1、定向路由与高级分布式状态 |

适用对象：架构负责人、实现 Agent、测试 Agent、Reviewer、CI/CD 维护者。
规范性关键词：MUST / MUST NOT 表示不可违反；SHOULD 表示默认遵循；MAY 表示允许但非必需。

## 目录

现行章节及附录索引；原 PDF 页码仅用于历史来源定位，不限制现行规范的修订。v1.1 冲突消解依据 ADR-0003；历史格式迁移仍由 ADR-0002 记录。

- [0. 执行摘要](#section-0) · 原 PDF 第 5 页
- [1. 项目目标、成功定义与边界](#section-1) · 原 PDF 第 6 页
  - [1.1 目标](#section-1-1) · 原 PDF 第 6 页
  - [1.2 Loop 1 成功定义](#section-1-2) · 原 PDF 第 6 页
  - [1.3 非目标与延后项](#section-1-3) · 原 PDF 第 6 页
- [2. 冻结架构原则与变更治理](#section-2) · 原 PDF 第 7 页
  - [2.1 Frozen Architecture 变更协议](#section-2-1) · 原 PDF 第 7 页
  - [2.2 权威顺序](#section-2-2) · 原 PDF 第 7 页
- [3. 系统总体架构与部署单元](#section-3) · 原 PDF 第 8 页
  - [3.1 三个物理部署单元](#section-3-1) · 原 PDF 第 8 页
  - [3.2 运行 profile](#section-3-2) · 原 PDF 第 8 页
  - [3.3 Loop 1 单机部署](#section-3-3) · 原 PDF 第 8 页
- [4. 领域模型与业务不变量](#section-4) · 原 PDF 第 9 页
  - [4.1 账号与 Session](#section-4-1) · 原 PDF 第 9 页
  - [4.2 好友与唯一私聊](#section-4-2) · 原 PDF 第 9 页
  - [4.3 群聊最小实现](#section-4-3) · 原 PDF 第 9 页
  - [4.4 消息身份与序号](#section-4-4) · 原 PDF 第 9 页
- [5. 消息写入、Outbox 与实时 fan-out](#section-5) · 原 PDF 第 10 页
  - [5.1 发送事务](#section-5-1) · 原 PDF 第 10 页
  - [5.2 NATS 与 Gateway fan-out](#section-5-2) · 原 PDF 第 10 页
  - [5.3 群聊 fan-out](#section-5-3) · 原 PDF 第 10 页
- [6. 客户端状态、本地存储与离线同步](#section-6) · 原 PDF 第 11 页
  - [6.1 三端差异](#section-6-1) · 原 PDF 第 11 页
  - [6.2 Optimistic write 与状态机](#section-6-2) · 原 PDF 第 11 页
  - [6.3 SQLite 事务不变量](#section-6-3) · 原 PDF 第 11 页
  - [6.4 双层 Cursor](#section-6-4) · 原 PDF 第 11 页
- [7. HTTPS/WSS/TLS 与认证协议](#section-7) · 原 PDF 第 12 页
  - [7.1 登录与 Token](#section-7-1) · 原 PDF 第 12 页
  - [7.2 WSS 状态机](#section-7-2) · 原 PDF 第 12 页
  - [7.3 Session 缓存一致性](#section-7-3) · 原 PDF 第 12 页
  - [7.4 传输与日志安全](#section-7-4) · 原 PDF 第 12 页
- [8. 插件平台架构](#section-8) · 原 PDF 第 13 页
  - [8.1 包结构与公共 API](#section-8-1) · 原 PDF 第 13 页
  - [8.2 Custom Render Bundle](#section-8-2) · 原 PDF 第 13 页
  - [8.3 WASM 后端 Sandbox](#section-8-3) · 原 PDF 第 13 页
- [9. 插件版本、热插拔与回滚](#section-9) · 原 PDF 第 14 页
  - [9.1 安装](#section-9-1) · 原 PDF 第 14 页
  - [9.2 升级与双版本共存](#section-9-2) · 原 PDF 第 14 页
  - [9.3 Disable / Uninstall / Purge](#section-9-3) · 原 PDF 第 14 页
  - [9.4 官方兼容 fixtures](#section-9-4) · 原 PDF 第 14 页
- [10. Monorepo 与规范控制面](#section-10) · 原 PDF 第 15 页
  - [10.1 spec/ 各目录的职责](#section-10-1) · 原 PDF 第 15 页
- [11. 公共契约与双后端实现](#section-11) · 原 PDF 第 16 页
  - [11.1 唯一权威](#section-11-1) · 原 PDF 第 16 页
  - [11.2 等价而非同构](#section-11-2) · 原 PDF 第 16 页
  - [11.3 Golden Contract Tests](#section-11-3) · 原 PDF 第 16 页
  - [11.4 数据库迁移](#section-11-4) · 原 PDF 第 16 页
  - [11.5 公开 Sync HTTPS 绑定](#section-11-5)
- [12. AI Development Loop](#section-12) · 原 PDF 第 17 页
  - [12.1 Task Spec 模板](#section-12-1) · 原 PDF 第 17 页
  - [12.2 状态队列](#section-12-2) · 原 PDF 第 17 页
  - [12.3 Git 工作模式](#section-12-3) · 原 PDF 第 17 页
- [13. Agent 启动与交接协议](#section-13) · 原 PDF 第 18 页
  - [13.1 强制读取顺序](#section-13-1) · 原 PDF 第 18 页
  - [13.2 Handoff 必填项](#section-13-2) · 原 PDF 第 18 页
  - [13.3 Checkpoint 规则](#section-13-3) · 原 PDF 第 18 页
- [14. CI/CD 独立校验架构](#section-14) · 原 PDF 第 19 页
  - [14.1 路径感知规则](#section-14-1) · 原 PDF 第 19 页
  - [14.2 流水线层次](#section-14-2) · 原 PDF 第 19 页
  - [14.3 兼容矩阵](#section-14-3) · 原 PDF 第 19 页
  - [14.4 CI 与 Agent 的信任边界](#section-14-4) · 原 PDF 第 19 页
- [15. Loop 1: 12 周预算、里程碑门禁驱动](#section-15) · 原 PDF 第 20 页
- [16. Loop 1 性能与可靠性验收](#section-16) · 原 PDF 第 21 页
  - [16.1 固定环境与连接定义](#section-16-1) · 原 PDF 第 21 页
  - [16.2 必测场景](#section-16-2) · 原 PDF 第 21 页
  - [16.3 观测指标](#section-16-3) · 原 PDF 第 21 页
  - [16.4 Gate 判定](#section-16-4) · 原 PDF 第 21 页
- [17. Release、迁移与回滚规则](#section-17) · 原 PDF 第 22 页
  - [17.1 Release Manifest](#section-17-1) · 原 PDF 第 22 页
  - [17.2 发布规则](#section-17-2) · 原 PDF 第 22 页
  - [17.3 数据库迁移](#section-17-3) · 原 PDF 第 22 页
  - [17.4 回滚](#section-17-4) · 原 PDF 第 22 页
  - [17.5 发布失败判定](#section-17-5) · 原 PDF 第 22 页
- [18. 可观测性、安全与运维基线](#section-18) · 原 PDF 第 23 页
  - [18.1 关联标识](#section-18-1) · 原 PDF 第 23 页
  - [18.2 健康与就绪](#section-18-2) · 原 PDF 第 23 页
  - [18.3 安全清单](#section-18-3) · 原 PDF 第 23 页
  - [18.4 告警优先级](#section-18-4) · 原 PDF 第 23 页
- [19. 第一批 Agent 可执行任务](#section-19) · 原 PDF 第 24 页
- [20. 后续任务队列与依赖](#section-20) · 原 PDF 第 25 页
  - [20.1 依赖纪律](#section-20-1) · 原 PDF 第 25 页
- [21. Agent 首日执行清单](#section-21) · 原 PDF 第 26 页
  - [21.1 第 0-2 小时](#section-21-1) · 原 PDF 第 26 页
  - [21.2 第一个实现回合](#section-21-2) · 原 PDF 第 26 页
  - [21.3 Agent 的停止条件](#section-21-3) · 原 PDF 第 26 页
- [附录 A. Gate Checklist](#appendix-a) · 原 PDF 第 27 页
- [附录 B. 冻结不变量速查](#appendix-b) · 原 PDF 第 28 页

<a id="section-0"></a>
## 0. 执行摘要

本项目构建一个前后端分离、多端、多实现、插件一等公民的分布式即时通信平台。题目中的“十万级”描述平台的扩展方向，不等于 Loop 1 已验收十万连接。Loop 1 先用单机 8C/16GB/3TB 完成 5000 个真实认证 WSS 用户的正确性与容量基线；通过后，双机十万连接正式验收延后至 Loop 2。

```mermaid
flowchart LR
  Web["Web<br/>临时内存态"]
  Desktop["Desktop<br/>SQLite"]
  Mobile["Mobile<br/>SQLite"]
  UI["Plugin UI Host<br/>声明式 UI + Render Bundle"]
  Gateway["TLS Proxy / Gateway<br/>HTTPS + WSS"]
  Core["Core 模块化单体<br/>Auth / IM / Sync"]
  Plugin["Plugin Host<br/>WASM Sandbox"]
  PG["PostgreSQL<br/>事实来源 + Outbox"]
  NATS["NATS<br/>实时事件总线"]
  Web --> Gateway
  Desktop --> Gateway
  Mobile --> Gateway
  UI --> Gateway
  Gateway --> Core
  Core --> Plugin
  Core --> PG
  Core --> NATS
  NATS --> Gateway
```

> 图 0-1 总体逻辑架构：PostgreSQL 是事实来源，NATS 是实时通知总线；Gateway 只承担接入与 fan-out。

> 实时路径为 Core 的 Outbox dispatcher → NATS → Gateway；PostgreSQL 写入由 Core 事务负责。历史 PDF 的 NATS → PostgreSQL 箭头只保留在历史来源中，不代表现行运行依赖。

#### 四条总纲

1. contracts/ 是机器可验证公共契约的唯一来源；总体权威顺序见 §2.2，Go 与 Java/Spring 是独立实现；
2. 消息可靠性来自 PostgreSQL + Outbox + Sync，不来自 NATS；
3. Agent 可改代码但无权自行宣布正确，CI 是独立事实裁判；
4. 未经架构决策流程，任何 Agent 不得修改 frozen architecture。

| 维度 | Loop 1 必须完成 | 明确不进入 Loop 1 |
| --- | --- | --- |
| 业务 | 账号、搜索、最小好友、唯一私聊、最小群聊、纯文本、插件消息 | 音视频、文件、朋友圈、超级群、陌生人拉群 |
| 客户端 | Web 临时态；Desktop/Mobile SQLite、离线历史、optimistic write | Web 本地历史数据库；离线创建需要服务端确认的业务操作 |
| 后端 | Go 与 Java/Spring 两套独立 profile，行为等价 | Go/Java 混合集群生产流量 |
| 容量 | 单机 5000 authenticated WSS users | 双机 100000 正式验收、N+1 满负载 |
| 基础设施 | PostgreSQL、Core NATS、TLS Proxy、Docker Compose | 为“看起来分布式”而预先加入 Redis/Kafka/分库分表 |

<a id="section-1"></a>
## 1. 项目目标、成功定义与边界

<a id="section-1-1"></a>
### 1.1 目标

- 以 HTTPS/WSS/TLS 提供真实认证、多端同步的即时通信纵向闭环。

- 用同一套公共契约证明 Go 与 Java/Spring 两套独立后端可替换，客户端无需改动。

- 把插件平台作为一等公民：WASM 后端 sandbox + 全客户端 UI Extension + 经审查的 Custom Render Bundle。

- 建立 AI 全流程自动化开发的控制面，使新 Agent 只通过 spec + contracts + progress + tasks 即可恢复工作。

- 以门禁和自动化证据驱动进度；12 周是预算，不是等待日历。

<a id="section-1-2"></a>
### 1.2 Loop 1 成功定义

| 验收域 | 不可省略的证据 |
| --- | --- |
| 业务 E2E | 注册/登录 -> 搜索 -> 添加好友 -> 自动出现唯一私聊 -> 文本消息 -> 从好友列表创建群聊 -> 群消息 -> 安装/使用插件 |
| 消息正确性 | ACK 仅在 durable commit 后；同一 request_id 重试不产生重复逻辑消息；离线恢复无永久 gap |
| 客户端 | Desktop/Mobile SQLite 事务 UPSERT；SENDING/SENT/FAILED；Web 不保存历史 |
| 实现等价 | Go profile 与 Java profile 分别通过同一 Golden Contract Tests；客户端不改代码 |
| 工程体系 | path-aware CI、兼容矩阵、迁移测试、插件 fixture、Release Manifest、rollback rehearsal |
| 容量 | 单机 8C/16GB/3TB，5000 个已完成 TLS/WSS/auth.bind/session validation 的在线用户 |

<a id="section-1-3"></a>
### 1.3 非目标与延后项

#### Loop 2 范围

双机正式部署与十万 authenticated WSS connections；N+1 failover；Gateway targeted routing；更高级的分布式Session/Presence；超级群；进一步水平扩展。Loop 1 文档与代码可以预留扩展点，但不得以此扩大当前实现范围。

Loop 1 不把 Redis、Kafka、分库分表、自动数据库切主视为必选项。只有基于压测、故障证据和新 ADR 才能引入。两节点环境不具备安全自动 quorum failover 条件；生产级自动切主须等待第三方 witness 或更多节点。

<a id="section-2"></a>
## 2. 冻结架构原则与变更治理

| ID | 冻结决策 | 强制约束 |
| --- | --- | --- |
| F-01 | 公共契约唯一权威 | HTTPS、WSS、错误码、领域语义、Sync、Plugin API 先定义，两个后端不得各自发明 |
| F-02 | 双后端独立实现 | 100% Go profile 或 100% Java/Spring profile；Loop 1 不混跑 |
| F-03 | PostgreSQL 是事实来源 | 消息、会话、Session、插件状态持久化；NATS 丢事件不能造成永久数据缺失 |
| F-04 | Transactional Outbox | message 与 outbox 同一事务；ACK 表示 durable commit |
| F-05 | Gateway 轻业务 | 接入、鉴权绑定、连接注册、限流、协议路由、local fan-out；业务规则在 Core |
| F-06 | 双层同步游标 | 用户低频状态用 user_sync_cursor；消息用 conversation seq + contiguous_seq |
| F-07 | 客户端差异 | Web memory only；Desktop/Mobile SQLite materialized view |
| F-08 | 插件最小权限 | 所有能力经 capability/permission；Render Bundle 审查 + sandbox；不可直接触达宿主敏感资源 |
| F-09 | 门禁驱动 | Gate PASS 立即前进；Gate FAIL 必须留在阶段修复 |
| F-10 | CI 独立裁判 | Agent 的自检不是验收；合并与发布只依据独立流水线证据 |

<a id="section-2-1"></a>
### 2.1 Frozen Architecture 变更协议

- 禁止：未经明确批准直接修改 frozen spec / contracts / DB invariants / plugin security boundary
- 允许：创建 Architecture Change Proposal (ACP) 或 ADR 草案
- 流程：提出动机 -> 影响分析 -> 兼容/迁移/回滚方案 -> 架构负责人批准 -> 修订现行正文及基线 -> 按影响更新契约（仅在授权改变契约时）与执行约束 -> 独立 Review 与适用 CI -> 实施迁移并验证。不得以尚待迁移实现违反新规则为由永久豁免；规则交付和产品最终合规分别验收。

Agent 遇到与 frozen architecture 冲突的任务时必须停止该冲突部分，在任务记录中标记 BLOCKED_BY_ARCHITECTURE，并提出最小决策问题。不得用“实现方便”作为静默改变协议、唯一约束、ACK 语义或安全边界的理由。

<a id="section-2-2"></a>
### 2.2 权威顺序

1. 本 Frozen Architecture（由 spec/architecture/README.md 与 baseline.md 解析）及 spec/architecture/decisions/ 的已批准 ADR / frozen decision。ADR 记录动机、批准来源和迁移；批准的现行规则必须落实到正文。同等权威存在无法消解的实质冲突时停止冲突部分并提出最小决策问题。

2. contracts/ (机器可验证的公共契约)

3. spec/domain/ + spec/invariants/

4. spec/acceptance/ (Gate 与验收证据)

5. spec/tasks/ (任务局部范围)

6. implementation (不得反向定义契约)

### 2.3 Agent 技术选型权限（所有任务适用）

Agent 没有未授权技术选型权。编程语言、UI/application/client/cross-platform framework、runtime、database/local database、ORM、network framework、IPC/RPC、state management framework、plugin runtime、serialization framework、message queue、cache、storage engine、native bridge、authentication framework、major infrastructure dependency，以及形成长期架构耦合的核心第三方库，都必须具有现行 Frozen Architecture、approved ADR、contracts 或明确 Human 架构决定的充分授权。

答案不明确时唯一合法顺序是：停止受影响实现 → 标记 BLOCKED_BY_ARCHITECTURE → 最小决策问题与影响范围 → Architect / Human 明确决定 → 写入 Frozen Architecture / approved ADR → 必要 machine guard → 新独立 Review + applicable 精确候选 hosted CI → 决定正式生效 → 产品实现。可继续不依赖该决定的已批准工作。禁止先实现、测试通过后再修改架构追认。

“熟悉、已安装、方便、流行、代码少、以前失败实现用过、Task Spec 未禁止、allowed_paths 允许、CI PASS”都不能授权；未禁止 ≠ 已批准。chat、handoff、task notes、current.md、implementation README、source comments 不能代替权威层。Task Spec 只能收窄范围、指定已授权细节/测试/路径，不能自行创造技术栈、框架、runtime、数据库、跨平台策略、服务边界或协议。Reviewer 必须逐项回答新的敏感选型来自哪个已接受权威条款/ADR；无法追溯则 Review FAIL。机器检查只补充语义 Review；执行规约见 spec/governance/technology-selection.md。

<a id="section-3"></a>
## 3. 系统总体架构与部署单元

```mermaid
flowchart LR
  Web["Web<br/>临时内存态"]
  Desktop["Desktop<br/>SQLite"]
  Mobile["Mobile<br/>SQLite"]
  UI["Plugin UI Host<br/>声明式 UI + Render Bundle"]
  Gateway["TLS Proxy / Gateway<br/>HTTPS + WSS"]
  Core["Core 模块化单体<br/>Auth / IM / Sync"]
  Plugin["Plugin Host<br/>WASM Sandbox"]
  PG["PostgreSQL<br/>事实来源 + Outbox"]
  NATS["NATS<br/>实时事件总线"]
  Web --> Gateway
  Desktop --> Gateway
  Mobile --> Gateway
  UI --> Gateway
  Gateway --> Core
  Core --> Plugin
  Core --> PG
  Core --> NATS
  NATS --> Gateway
```

> 图 3-1 逻辑组件图。

> 实时路径为 Core 的 Outbox dispatcher → NATS → Gateway；PostgreSQL 写入由 Core 事务负责。历史 PDF 的 NATS → PostgreSQL 箭头只保留在历史来源中，不代表现行运行依赖。

<a id="section-3-1"></a>
### 3.1 三个物理部署单元

| 部署单元 | 职责 | 明确不负责 |
| --- | --- | --- |
| gateway | TLS 之后的 WSS 生命周期、auth.bind、session/cache 校验、connection registry、协议路由、local fan-out、heartbeat/限流 | 好友/群成员规则、消息持久化、插件业务逻辑 |
| core | Auth、Session、User、Friendship、Conversation、Message、Sync、Outbox；模块化单体 | 不可信插件执行；大量 socket 连接状态 |
| plugin-host | WASM runtime、事件分派、经授权的 Query/Action Host bridge、资源限制、熔断、编译缓存 | 不可信 WASM 直接访问数据库/文件/任意网络；绕过 Core 业务授权；成为 IM 主链单点 |

<a id="section-3-2"></a>
### 3.2 运行 profile

```text
docker compose --profile go up
# gateway-go + core-go + plugin-host-go adapter + shared PostgreSQL/NATS/TLS
docker compose --profile java up
# gateway-java + core-java + plugin-host adapter + same canonical schema/contracts
```

profile 的目标是行为可替换；服务内部源码结构可以不同，但 §3 职责、§10 服务源码归属和依赖方向共同约束两个后端。Go 与 Java 可使用各自惯用的框架和组织方式，但必须共享：公共契约、数据库迁移语义、错误码、测试向量、插件 API、Release Manifest 格式。

Go/Java 可采用不同内部组织方式，但所有新增框架、ORM、runtime、核心依赖必须先遵守 §2.3；结构自由不是技术选型授权。

<a id="section-3-3"></a>
### 3.3 Loop 1 单机部署

| 层 | Loop 1 单机部署规则 |
| --- | --- |
| 入口 | TLS reverse proxy 暴露 HTTPS/WSS；部署 smoke、E2E、容量与发布验收流量经过真实入口。单元和隔离集成测试可直接访问被测组件，但不得替代入口验收 |
| 服务 | 仅启动一个后端 profile；gateway/core/plugin-host 为可独立启动的部署角色。可复用一个构建制品按角色启动；不强制三个 module 或三个 binary，禁止把源码职责混为一个业务包 |
| 数据 | PostgreSQL 单实例；所有 migration 有 forward/rollback 规则 |
| 事件 | Core NATS，默认非事实来源；Outbox dispatcher 可重放 |
| 存储 | 3TB 是机器容量约束，不代表测试必须填满；记录实际占用与增长 |

<a id="section-4"></a>
## 4. 领域模型与业务不变量

```mermaid
flowchart LR
  User["User<br/>user_id<br/>username / display_name"]
  Session["Session<br/>client_type / epoch<br/>ACTIVE / REVOKED"]
  Friendship["Friendship<br/>low_user / high_user<br/>UNIQUE pair"]
  Conversation["Conversation<br/>DIRECT / GROUP<br/>seq allocator"]
  Member["ConversationMember<br/>role / joined_at"]
  Message["Message<br/>request_id / seq<br/>TEXT / PLUGIN"]
  Instance["PluginInstance<br/>active / desired status"]
  Artifact["PluginArtifact<br/>version / hashes<br/>immutable"]
  Outbox["OutboxEvent<br/>aggregate / payload<br/>published_at"]
  KV["PluginKV<br/>schema_version<br/>conversation scope"]
  User -->|"有效槽位 1 : 0..3"| Session
  User --> Friendship
  Friendship -->|"pair → direct"| Conversation
  User -->|"member"| Member
  Member -->|"1 : N"| Message
  Message -->|"N : 1"| Conversation
  Message -->|"1 : 1 logical message.created"| Outbox
  Instance -->|"N : 1"| Artifact
  Instance -->|"1 : N"| KV
```

> 图 4-1 UML 领域关系概览。字段仅显示关键不变量；完整 schema 由 contracts/database 管理。

<a id="section-4-1"></a>
### 4.1 账号与 Session

每个用户拥有 WEB、DESKTOP、MOBILE 三个登录槽位。每种 client_type 同时最多一个有效 Session，但三种端可同时登录。同端新登录必须在事务中撤销旧 Session 并递增 session_epoch。PostgreSQL 是登录状态权威；Gateway 内存是在线连接与路由缓存。

- 每个 (user_id, client_type) 最多一个有效槽位；当前 contracts/database 定义为每槽一行，替换时原子轮换 session_id 与 epoch。本图不定义历史 Session 总量或另行创建历史表。
- Access Token: user_id, session_id, client_type, session_epoch, iat, exp
- Refresh Token: 只存 hash，可独立撤销
- WSS: 先建立 TLS/WebSocket，再发送 auth.bind；禁止 token 放 URL query

<a id="section-4-2"></a>
### 4.2 好友与唯一私聊

Loop 1 不做好友申请审批。添加好友表示即时建立双向关系，并在同一事务中创建或取得唯一 DIRECT Conversation。好友关系使用规范化无向 pair：low=min(A,B)、high=max(A,B)。

- friendships: UNIQUE(user_low_id, user_high_id)
- DIRECT conversation: UNIQUE(direct_user_low_id, direct_user_high_id)
- 事务: friendship + direct conversation + two members + sync events + outbox -> COMMIT

<a id="section-4-3"></a>
### 4.3 群聊最小实现

发起者只能从自己的好友列表选择成员。创建请求必须带 request_id 以避免网络重试重复建群。事务写入 GROUP Conversation、成员、用户状态同步事件与 outbox。Loop 1 不含邀请链接、二维码、陌生人拉群、复杂管理员审批。

<a id="section-4-4"></a>
### 4.4 消息身份与序号

| 身份 | 约束 | 用途 |
| --- | --- | --- |
| 客户端逻辑身份 | UNIQUE(conversation_id, request_id) | SQLite 本地发送、ACK、重试、Sync 收敛 |
| 服务端幂等身份 | UNIQUE(sender_id, conversation_id, request_id) | 跨重试/节点避免重复逻辑消息 |
| 服务端正式身份 | UNIQUE(server_message_id) | 全局记录身份 |
| 顺序 | UNIQUE(conversation_id, seq) | 会话内单调递增、缺口检测与历史分页 |

<a id="section-5"></a>
## 5. 消息写入、Outbox 与实时 fan-out

```mermaid
sequenceDiagram
  participant Sender as 发送端
  participant Gateway
  participant Core
  participant PG as PostgreSQL
  participant Bus as Outbox/NATS
  participant Receiver as 接收端
  Sender->>Gateway: message.send(request_id)
  Gateway->>Core: 转发绑定身份与发送请求
  Core->>Core: 校验成员权限与业务规则
  Core->>PG: BEGIN / seq / message / outbox
  PG-->>Core: COMMIT 成功
  Core-->>Gateway: ACK = durable commit
  Gateway-->>Sender: 转发 ACK
  Core->>PG: Outbox dispatcher 读取已提交事件
  Core->>Bus: dispatcher 可重试发布
  Bus->>Gateway: message.created
  Gateway->>Receiver: local fan-out
```

> 图 5-1 私聊消息时序图。ACK 的唯一成功语义是 message 与 outbox 已持久化提交。

<a id="section-5-1"></a>
### 5.1 发送事务

1. BEGIN
2. 校验 sender 是 conversation member
3. 幂等查询/冲突处理 (sender_id, conversation_id, request_id)
4. 锁定/更新 conversation sequence row
5. INSERT message(seq, ...)
6. INSERT outbox_event(message.created, ...)
7. COMMIT
8. 返回 ACK(message_id, seq, server_created_at)

第一轮 sequence row 允许成为热门会话热点，因为它最直观且易验证。只有压测证明竞争不可接受时，才通过 ADR 评估 range allocation 等演进方案。

<a id="section-5-2"></a>
### 5.2 NATS 与 Gateway fan-out

- Outbox dispatcher 发布 message.created 到 NATS，并以可重试方式标记 published。

- Gateway 订阅需要的实时事件，并只向本机活跃连接 fan-out。

- 收件人的所有在线端、发送者的其他在线端接收 message.created；发送端原连接由 ACK 收敛。

- NATS 事件可重复，消费者必须幂等；NATS 事件可短暂错过，Sync 必须最终补齐。

- Loop 1 不把 NATS JetStream 作为消息事实来源，也不为每个群成员写一条持久投递记录。消息写一次，在线端由

Gateway 读扩散。

<a id="section-5-3"></a>
### 5.3 群聊 fan-out

GROUP 消息仍只写一条 message 和一条 outbox 事件。Gateway 根据会话在线成员执行 local fan-out。普通群最大成员数不在设计阶段拍脑袋固定，应由 10/50/200/500 成员等阶梯测试结果决定。

#### 消息正确性红线

lost committed messages = 0；duplicate logical messages = 0；wrong conversation delivery = 0；permanent seq gap = 0；ACK-before-commit = 0。

<a id="section-6"></a>
## 6. 客户端状态、本地存储与离线同步

<a id="section-6-1"></a>
### 6.1 三端差异

| 客户端 | 本地持久化 | 离线历史 | 启动行为 |
| --- | --- | --- | --- |
| Web | 无聊天 DB；Memory only | 不补聊天历史；登录后获取当前好友/会话状态 | HTTPS 登录 -> WSS auth.bind -> 仅展示本会话实时数据 |
| Desktop | 按账号独立 SQLite + OS secure token storage | 支持 | 先读 SQLite 立即渲染，再后台同步 |
| Mobile | 按账号独立 SQLite + OS secure token storage | 支持 | 先读 SQLite 立即渲染，再后台同步 |


#### 已批准客户端技术栈与边界（Human-approved v1.1 clarification）

- Web = React + TypeScript；仅临时在线 Memory only；无 SQLite、无聊天历史持久化、无离线历史加载；通过 HTTPS + WSS 通信，页面生命周期结束后不保证消息状态保留。
- Desktop = Tauri + React + TypeScript；UI 独立实现；共享协议、模型、适用 hooks、Design Token 和 UI 语义，不共享完整 React 视觉组件（ADR-0006）；按账号 SQLite、离线历史、optimistic send、SENDING/SENT/FAILED、ACK 回写、retry 复用 request_id、Sync 收敛。
- Desktop 必要 Rust/native 代码仅限 `clients/desktop/src-tauri/**`，仅作为 SQLite native access、OS secure storage、必要文件系统等系统能力的 native adapter；客户端业务层、Repository API、protocol/model/plugin SDK 仍为 TypeScript，不得迁入 Rust。Desktop SQLite native boundary 使用 Tauri + SQLx(SQLite)；TypeScript 持有共享 Repository、模型和事务意图，Rust 仅提供数据库连接、查询和原子 transaction adapter。不得通过多个独立 tauri-plugin-sql execute() 调用模拟跨调用事务。SQLx 以外的 SQLite crate/plugin/library 未批准。
- Mobile = Android + Kotlin + Jetpack Compose；Human 明确移除 Mobile TypeScript 技术栈，具体 framework 不再 TBD。Android Studio emulator 为真实 Android 验证环境；按账号 SQLite、离线历史、optimistic send、ACK/retry/Sync 与其他客户端相同。
- Mobile 在 `clients/mobile/**` 使用 Kotlin 等价模型、Repository 语义、协议/插件适配与 data/domain 行为，服从同一 canonical contracts/fixtures；不要求直接复用 TypeScript SDK。优先 Android SDK 自带 SQLite 事务能力，不授权 Room、第三方 SQLite/ORM/network library 或其他架构敏感依赖。不得为共享代码自行加入 JS runtime、TS/JS bridge、codegen 或把 shared 层改写成跨端 native。完整 Mobile acceptance 未满足时 S2 Gate OPEN；Desktop host/mock 不能冒充 Android emulator acceptance。
- `clients/shared/{protocol-sdk,plugin-sdk,ui}/` 及 Web/Desktop shared models、Repository、data/domain logic 保持 TypeScript 生态。Mobile 以同一公共契约与 fixtures 验证等价行为；不创建新公共契约。保留现有目录权威，无无意义搬迁。S2 不实现 S4 WASM host、marketplace 或完整 lifecycle。
- Dart/Flutter 不属于当前批准 active client 技术栈；历史 PR7/Review/FAIL/Recorder/evidence 保留，但 PR7 不提供授权或新 TypeScript acceptance。

机器检查读取下列已批准技术标识；标准包名仅对应上述显式栈及必要 type/build bindings，不授权额外框架、runtime、数据库驱动或原生依赖。每个架构敏感新依赖仍须独立 Review 追溯授权。Android SDK、Gradle、Kotlin/Compose compiler/plugin、标准 Compose UI 与 Android activity binding 是所选栈的必要工程标识，仅限 Mobile；不授权其他 Kotlin frameworks、ORM、网络或 plugin runtimes。

<!-- client-technology-policy -->
```json
{
  "decision": "ADR-0005-client-technology-clarification",
  "languages": [
    "TypeScript",
    "JavaScript",
    "Rust",
    "Kotlin"
  ],
  "frameworks": [
    "React",
    "Tauri",
    "Jetpack Compose"
  ],
  "runtimes": [
    "Tauri",
    "Android"
  ],
  "packages": [
    "typescript",
    "react",
    "react-dom",
    "@types/react",
    "@types/react-dom",
    "@tauri-apps/api",
    "@tauri-apps/cli"
  ],
  "native_packages": [
    "tauri",
    "tauri-build",
    "sqlx"
  ],
  "mobile_framework": "Jetpack Compose",
  "native_boundary": "clients/desktop/src-tauri/",
  "mobile_languages": [
    "Kotlin"
  ],
  "mobile_runtimes": [
    "Android"
  ],
  "mobile_frameworks": [
    "Jetpack Compose"
  ],
  "mobile_plugins": [
    "com.android.application",
    "com.android.library",
    "org.jetbrains.kotlin.android",
    "org.jetbrains.kotlin.plugin.compose"
  ],
  "mobile_dependencies": [
    "com.android.tools.build:gradle",
    "org.jetbrains.kotlin:kotlin-gradle-plugin",
    "org.jetbrains.kotlin:compose-compiler-gradle-plugin",
    "org.jetbrains.kotlin:kotlin-stdlib",
    "org.jetbrains.kotlin:kotlin-stdlib-jdk8",
    "org.jetbrains.kotlin:kotlin-test",
    "androidx.activity:activity-compose",
    "androidx.compose:compose-bom",
    "androidx.compose.runtime:runtime",
    "androidx.compose.ui:ui",
    "androidx.compose.ui:ui-tooling",
    "androidx.compose.ui:ui-tooling-preview",
    "androidx.compose.foundation:foundation",
    "androidx.compose.animation:animation",
    "androidx.compose.material3:material3",
    "androidx.lifecycle:lifecycle-viewmodel-compose",
    "androidx.lifecycle:lifecycle-runtime-compose",
    "androidx.navigation:navigation-compose",
    "org.jetbrains.kotlinx:kotlinx-coroutines-core",
    "org.jetbrains.kotlinx:kotlinx-coroutines-android"
  ],
  "mobile_tooling": [
    "Android SDK",
    "Android Studio",
    "Gradle",
    "android-actions/setup-android",
    "gradle/actions/setup-gradle",
    "reactivecircus/android-emulator-runner"
  ],
  "mobile_import_prefixes": [
    "android.",
    "kotlin.",
    "java.",
    "javax.",
    "org.json.",
    "org.xml.",
    "org.w3c.",
    "androidx.compose.",
    "androidx.activity.",
    "androidx.lifecycle.",
    "androidx.navigation.",
    "kotlinx.coroutines."
  ]
}
```

JavaScript 仅为 TypeScript 生态的必要配置/构建互操作；Web/Desktop/shared 客户端业务/API/protocol/model/plugin SDK 必须 TypeScript；Mobile 的等价实现为 Kotlin。Rust 仅上述 native adapter。此标识表不授权 Node/Bun/Deno 等产品 runtime，SQLite native driver 仅批准 Desktop SQLx(SQLite)。Mobile 已批准 Android Kotlin + Jetpack Compose，Android Studio emulator 验证；Android 工程标识不是其他框架或第三方核心依赖的选型授权。

<a id="section-6-2"></a>
### 6.2 Optimistic write 与状态机

以下 SQLite 持久状态机适用于 Desktop/Mobile；Web 使用内存态收敛，不引入聊天历史数据库。

1. 用户点击发送
2. -> 生成不可变 request_id
3. -> SQLite 事务 UPSERT，state=SENDING
4. -> UI 立即渲染
5. -> WSS message.send
6. -> ACK: SENT + server_message_id + seq + server_time
7. -> timeout/offline: FAILED
8. -> Retry: 复用相同 request_id，FAILED -> SENDING

FAILED 仅表示当前尝试没有收到成功确认，不证明服务端未提交。SENT 是终态，不能倒退到 FAILED。Sync 若看到本地FAILED 但服务端已有相同 (conversation_id, request_id)，必须 UPSERT 为 SENT，而不是新增一行。

<a id="section-6-3"></a>
### 6.3 SQLite 事务不变量

- UNIQUE(conversation_id, request_id)
- UNIQUE(server_message_id) WHERE server_message_id IS NOT NULL
- UNIQUE(conversation_id, server_seq) WHERE server_seq IS NOT NULL
- 所有本地发送 / ACK / WSS realtime / Sync 均走事务 UPSERT
- 业务数据变更与 cursor / contiguous_seq 推进必须在同一事务

```mermaid
flowchart LR
  Start["启动<br/>读取 SQLite 并渲染"] --> Connect["连接<br/>HTTPS + WSS"]
  Connect --> UserSync["用户状态同步<br/>user_sync_cursor"]
  UserSync --> GapSync["消息缺口同步<br/>conversation seq"]
  UserSync --> Tx["同一 SQLite 事务<br/>UPSERT 数据 + 推进 cursor / contiguous_seq"]
  GapSync --> Tx
```

> WSS 实时流与 Sync 补偿流允许交叉，靠唯一约束和事务收敛，不暂停实时推送。
>
> 图 6-1 双层同步与本地收敛。

<a id="section-6-4"></a>
### 6.4 双层 Cursor

user_sync_cursor 只承载 friend、conversation、membership、plugin 等低频用户状态。消息不进入用户级事件流，以避免群消息按成员写放大。每个会话维护 contiguous_seq，只有本地从旧值开始连续无缺口时才能前移。

### 6.5 客户端 UI 架构与 GUI 验收（Human-approved ADR-0006 候选）

以下 Human 决定待新独立 Review、精确候选 hosted CI、集成与实际 main 核验后生效；此前不得据候选启动产品实现。补充设计说明位于 `spec/architecture/decisions/client-ui/architecture.md` 和 `design-direction.md`；GUI 验收规约为 `spec/acceptance/client-gui.md`；这些从属于本正文和 ADR-0006，不是第二 canonical 或公共 wire/schema 权威。

- 产品构界 IM+ / PlugWorldIM；Adaptive Glass Workspace；视觉重点 50% Future AI Communication / 30% Productivity Tool / 20% Developer Extensibility。简洁、玻璃层次、AI-native、模块化、可配置；该比例不是功能能力承诺。Minimal Glassmorphism 使用 translucent surface、subtle border、blur、layered depth 表达层次；禁止信息堆砌、复杂 Dashboard、过度 Cyber/HUD、重度发光/霓虹/粒子/复杂 3D 和为炫技添加视觉元素。
- 两主题 Cold AI（冷蓝、紫色渐变、深色玻璃）和 Warm Creative（暖色渐变、柔和玻璃、亲和）。共享 Logo、品牌、Layout、Component semantic；主题切换只改变 Color token。用户独立本地设置 Typography/Spacing；插件不得修改主导航、品牌核心或基础 UI 语义。主题切换不得重置字体/间距；设计值/像素布局和具体偏好存储机制由后续受控 GUI Task 给出，不授权 Web 聊天持久化。可读性/焦点/状态不能仅靠颜色或透明效果表达。
- Application Shell 拥有 Chat / Friends / AI / Plugin 一级导航；未来仅客户端受控任务可增加 Settings/Profile；插件不得新增一级导航或直接控制 Shell。Chat 负责 Conversation List/View/Message；好友搜索、关系、添加属 Friends。AI 仅入口/插图/施工中，不含 AI chat、Agent、RAG、Tool Calling、API 或假 AI 数据。Plugin 为 Installed Plugins/Status/Entry 个人能力面板；缺失能力诚实显示未开放，不制造假数据；不是商店或 Marketplace。
- Web React/TypeScript 工程分层为 Shell/routing、定制业务组件、hooks/data/state 和 Repository/protocol adapter；默认 useState/useReducer/Context/custom hooks。不选择第三方 router/data/state 库；Zustand/Redux/MobX 或敏感库需单独 ADR 批准。基础 icon/accessibility/utility 类别并非具体包的 blanket approval；不得绑定完整业务 UI framework。
- Desktop Tauri/React/TypeScript 独立 UI，定位舒适、高频、生产力，允许后续受控任务提供更丰富布局/交互/本地能力展示。共享 protocol-sdk/plugin-sdk/models、Repository 行为、适用平台中立 hooks、Design Token/UI semantic；不共享完整 Button/MessageBubble/ChatWindow。Mobile 分享规范和 canonical contracts/fixtures，通过 Kotlin 等价实现，不要求复用 TS hook/SDK/组件。现行 SQLx/TypeScript 原子适配边界不变。
- Mobile Compose UI 向 ViewModel 发出意图；ViewModel 调用 Repository 并通过 StateFlow 暴露状态；Compose 生命周期感知地观察 StateFlow。Repository 委托 SDK SQLite 与授权 WSS/protocol adapter。Jetpack Navigation Compose 管理宿主导航；仅明确 state/navigation 所需依赖按本节 machine policy；Android Studio emulator 验收，不授权额外 Room/ORM/network/runtime/bridge/codegen。
- UI 只显示观察状态并发出意图；Repository 拥有本地 materialized data/事务收敛，protocol 层遵循 contracts/；UI 不直连 SQLite、不自行推进 cursor/contiguous_seq、不伪造 ACK/SENT、不决定服务端权限。Desktop/Mobile 本地先显示再背景 Sync；SENDING/SENT/FAILED、retry 复用 request_id、SENT 不回退、失败与服务端事件收敛、数据与 cursor 原子性沿用 §6.2-6.4。Web memory only、无离线历史；账号切换不显示旧账号数据。
- S2 不下载/执行插件 UI 代码、不动态加载/注入任意远程组件、不实现 Renderer/runtime/安装系统。未来声明式 poll 描述是方向，不是新契约。Human 明确上述代码执行禁令仅限 S2；S4 保留 §8.2 审查加沙箱 Custom Render Bundle/白名单 Bridge、签名/hash/schema/API/权限/CSP/资源/入口校验及历史版本绑定；本节不删除或放宽它们。插件不能控制宿主导航。
- 后续 GUI 覆盖现有 contracts/ 的 Auth login/refresh/logout/session-expired、User info、Friend search/add、Conversation list/open、Message send/receive/state、Sync state；传输/字段来自现行 OpenAPI/WSS，不发明 HTTP route 或 AI/Plugin API。无 AI 功能、Plugin runtime、Marketplace 实现。
- GUI Task acceptance 必须含真实运行截图 -> Architect Review -> 修复/重新截图 -> Architect Approval，并保留独立实现 Review、精确候选 CI 与集成/main 核验。Web 截图覆盖 Login/Chat/Friends/AI Placeholder/Plugin Page；Desktop 覆盖主窗口/Chat/Friends/Offline History/真实 Notification-Tray/Theme；Mobile 为真实 Android emulator Login/Chat/Friends/Offline History/Sync 状态/Theme。两主题/受支持字体间距变化与相关加载/空/错误/会话失效/离线状态需实际证据；局部任务明确剩余范围，不得宣称全客户端 PASS。
- 截图绑定 Task、候选 SHA/build/runtime、屏幕状态/尺寸、theme/配置、可重复步骤、文件/hash；使用受控无秘密数据。Architect 决策绑定同一候选和截图集，失败留未完成；影响已批准视觉的改动必须重新截图批准。截图不能证明 ACK/事务/幂等，不替代行为/权限/契约/源码依赖测试；Task PASS 不等于 S2 Gate PASS。

<a id="section-7"></a>
## 7. HTTPS/WSS/TLS 与认证协议

<a id="section-7-1"></a>
### 7.1 登录与 Token

- 登录端点、字段名、版本与传输形状由 contracts/http/ 定义（当前为 POST /v1/auth/login）。本章 snake_case 领域名称不是另一套 wire schema。

- Access Token 短期、Refresh Token 长期；具体时长是配置，不写死进协议。

- Web 优先使用 HttpOnly Secure Cookie 持有 Refresh Token；原生端使用 OS secure storage。

- 显式 logout 撤销 Session、Refresh Token 与 WSS；退出登录不等于立即删除本地 SQLite。

<a id="section-7-2"></a>
### 7.2 WSS 状态机

1. TCP/TLS -> WebSocket Upgrade -> UNAUTHENTICATED
2. UNAUTHENTICATED 只允许 auth.bind 与 ping/pong
3. auth.bind 校验签名、exp、session_id、client_type、session_epoch
4. 成功 -> AUTHENTICATED，socket 永久绑定 user/session/client_type
5. 同端新登录 -> session.revoked -> 推送旧连接 -> close

<a id="section-7-3"></a>
### 7.3 Session 缓存一致性

Core 在 Session 创建/撤销事务中写 outbox；Gateway 经 NATS 更新内存映射 (user_id, client_type) ->session_id/epoch/connection_id。每条消息不查询 PostgreSQL。实时撤销事件是体验优化；每次新绑定/重连必须验证数据库权威 Session ID 与 epoch，拒绝旧凭据；不得把实时撤销事件作为唯一有效性来源。Gateway 只拥有验证/连接能力；注册、登录、刷新、退出、Session 写事务及其 Outbox 属于 Core，不能通过共享完整 Auth 服务绕过边界。

<a id="section-7-4"></a>
### 7.4 传输与日志安全

| 规则 | 要求 |
| --- | --- |
| 传输 | 生产入口仅 HTTPS/WSS/TLS；禁用明文回退 |
| Token | 禁止放 URL query；禁止写应用日志/trace；错误响应不得回显 |
| 密码 | 只存强哈希；凭证与普通用户资料分离 |
| 插件 | 永不向 Custom Renderer 暴露认证 token 或 SQLite 直连 |
| 日志 | request_id/message_id 可观测；消息正文默认不进入结构化日志 |

<a id="section-8"></a>
## 8. 插件平台架构

<a id="section-8-1"></a>
### 8.1 包结构与公共 API

```text
plugin.pkg
├── manifest.json
├── backend/plugin.wasm
└── ui/
├── render.bundle.js
├── render.css
└── assets/
```

Plugin API v1 = Events + Queries + Actions + UI Host API

| 面 | 能力 | 约束 |
| --- | --- | --- |
| Events | message.created、member.joined、plugin lifecycle 等 | 仅订阅 manifest 声明且已授权的事件 |
| Queries | 读取被授权的会话、成员、消息、插件私有状态 | 只读、分页、限额；不可直接访问 Core 内部服务/DB |
| Actions | 发送消息、更新插件状态、触发允许的 UI 行为 | 每个 Action 重新鉴权、幂等与审计 |
| UI Host | Page/Modal/Panel/Menu/Form/Toolbar/Message Renderer 等 | 完整 UI 扩展能力不等于宿主 OS 权限 |

<a id="section-8-2"></a>
### 8.2 Custom Render Bundle

所有客户端都支持声明式 UI 与 Custom Render Bundle 两档。自定义包在加载前必须完成 package hash、签名、manifest schema、Plugin API 兼容、权限、大小/资源、CSP 与入口检查；运行时在 sandbox iframe 或 isolated WebView 中执行，并且只能通过白名单 Plugin Bridge 调用 Host API。

#### 不可变制品

UNIQUE(plugin_id, version)。同一版本的 package/backend/renderer hash 变化必须拒绝。消息数据与渲染代码分离，历史插件消息携带 plugin_id、plugin_version、renderer 与 fallback TEXT；客户端必须保留仍被历史消息引用的旧 renderer。

<a id="section-8-3"></a>
### 8.3 WASM 后端 Sandbox

- 默认不可访问数据库、服务器文件、任意 socket、其他插件内存。

- 资源边界包括 CPU/执行时长、内存、并发、存储配额与网络策略。

- 持久状态在 PostgreSQL plugin_kv；WASM 执行尽量无状态，可缓存编译 module。

- 连续 timeout/panic/limit violation 达阈值后 AUTO_DISABLED，并通知 Conversation Owner；IM 主链继续工作。

<a id="section-9"></a>
## 9. 插件版本、热插拔与回滚

```mermaid
flowchart LR
  subgraph Artifact["不可变制品"]
    Uploaded["UPLOADED"] --> Validating["VALIDATING"] --> Verified["VERIFIED"]
  end
  Verified -.->|"安装前提，不是同一状态机"| Installing
  subgraph Instance["Conversation 实例"]
    Installing["INSTALLING"] --> Enabled["ENABLED"]
  Enabled --> Disabled["DISABLED"] --> Uninstalled["UNINSTALLED"] --> Retained["RETAINED"] --> Purged["PURGED"]
  Disabled -->|"re-enable"| Enabled
  end
  Exception["异常旁路<br/>VALIDATION / INSTALL / RUNTIME / ROLLBACK_FAILED"]
  Upgrade["升级<br/>旧版保持 ENABLED → 快照/迁移/健康检查 → 原子切换；失败回滚"]
  %% 异常及升级仍遵循正文和 canonical lifecycle contracts。
```

> 图 9-1 插件制品与实例生命周期。Artifact 状态和 Conversation 下 Instance 状态必须分离。

<a id="section-9-1"></a>
### 9.1 安装

1. 检查安装权限 -> Artifact VERIFIED -> API compatibility -> 权限确认
2. BEGIN: plugin_instance=INSTALLING + grants + sync_event + outbox -> COMMIT
3. 异步: preload WASM + client bundle fetch + health check
4. 成功: ENABLED；失败: INSTALL_FAILED，不影响 IM 主服务

<a id="section-9-2"></a>
### 9.2 升级与双版本共存

Plugin Instance 维护 active_version、desired_version、previous_version。升级期间旧版保持服务：安装新版 -> plugin_kv 快照 -> storage migration -> backend/renderer 健康检查 -> 原子切换。任何一步失败都恢复快照并继续旧版。Backend WASM 与 Renderer Bundle 属于同一制品版本，不允许拆开升级。

<a id="section-9-3"></a>
### 9.3 Disable / Uninstall / Purge

| 操作 | 运行行为 | 数据 |
| --- | --- | --- |
| DISABLE | 停止接收新事件与产生 Action，隐藏入口，可重新 enable | 保留 |
| UNINSTALL | Conversation 不再持有活动实例 | 默认 RETAINED |
| PURGE | 显式不可逆清理操作；需要高权限和审计 | 删除前必须确认保留策略；不得删除仍被历史消息引用且必须保留的 renderer |

<a id="section-9-4"></a>
### 9.4 官方兼容 fixtures

Loop 1 必须提供 Echo Plugin 和 Poll Plugin。Echo 验证 event -> WASM -> action -> message；Poll 验证 PLUGIN message、Custom Renderer、plugin storage、客户端 UI 交互与 fallback TEXT。这两个插件进入持续兼容矩阵。

<a id="section-10"></a>
## 10. Monorepo 与规范控制面

```text
/
├── spec/
│ ├── architecture/
│ │ ├── README.md + baseline.md # resolver 与完整性元数据
│ │ ├── frozen-architecture.md # 唯一现行正文
│ │ └── decisions/ # ADR + frozen decisions
│ ├── domain/ # auth/user/friend/conversation/message/sync/plugin
│ ├── invariants/ # 跨语言不可变量
│ ├── acceptance/ # loop-1.md + stage gates
│ ├── progress/
│ │ ├── current.md
│ │ └── checkpoints/
│ ├── handoff/agent-context.md
│ └── tasks/{backlog,ready,active,review,done}/
├── contracts/
│ ├── http/
│ ├── websocket/
│ ├── errors/
│ ├── database/
│ ├── plugin-api/
│ └── fixtures/ # golden vectors / old clients / plugins
├── backend/
│ ├── go/{gateway,core,plugin-host,tests,shared}/
│ └── java/{gateway,core,plugin-host,tests,shared}/
├── clients/
│ ├── shared/{protocol-sdk,plugin-sdk,ui}/
│ ├── web/
│ ├── desktop/
│ └── mobile/
├── plugins/fixtures/{echo,poll}/
├── tests/{contract,integration,e2e,compatibility,load}/
├── deploy/{compose,proxy,observability}/
├── ci/
└── tools/
```

### 服务源码与依赖规则（Go / Java 共同适用）

- **SRC-01**：`backend/<language>/gateway/**` 只实现 §3.1 Gateway；`core/**` 拥有 Auth/Session 写事务、User/Friend/Conversation/Message/Sync/Outbox；`plugin-host/**` 拥有受控插件执行与代理。业务源码 MUST 位于对应服务范围，不能放在语言根目录或未批准的 `internal/**` 业务目录。
- **SRC-02**：语言根目录只白名单允许入口装配（Go `main.go`、Java `Main.java`）、模块/依赖/构建文件（Go `go.mod`/`go.sum`，Java `pom.xml` 或 Gradle 配置）、Dockerfile、README.md、config.example.json 及根入口测试（Go `main_test.go`、Java `MainTest.java`）。入口只能读取配置、选择角色、连接依赖、启动/关闭对应服务；不得实现路由业务、Auth 服务或 Session 写逻辑。根测试仅验证装配，服务测试与职责同迁或置于 `tests/**`；不能以测试文件名藏业务实现。新增根源码例外必须先明确批准、列入检查器白名单并限定用途。
- **SRC-03**：`shared/**` 可承载配置读取、日志、连接建立、通用编解码、密码学/令牌原语和由 canonical contracts 约束的传输数据类型。共享包 MUST NOT 承载完整 Auth 服务、注册/登录/刷新/退出流程、Session 写事务、业务仓储、权限/成员决策、Outbox 业务编排，亦不得反向依赖任何服务包。Gateway 的只读权威 Session 校验归 Gateway；Core 保有写事务。共享不是绕过职责的后门。
- **SRC-04**：服务可依赖共享支持与本服务内部包；任何服务 MUST NOT 直接 import/依赖另一服务内部实现。服务间通过现有授权的 HTTP/WSS/事件/受控 Host bridge 边界协作；不因源码整改新增 RPC、公共契约、module 或基础设施。根装配可依赖各服务的最小启动接口，测试可跨服务作黑盒组合验证，均不得成为运行期业务反向依赖。
- **SRC-05**：Go 与 Java 可使用不同的服务内部包/模块/线程组织；共同职责、物理角色和上述源码边界不可被“行为等价”豁免。不强制三 module、三 binary 或多层架构。Reviewer 检查实际职责和 import 图，不只看文件名或目录存在。
- **SRC-06**：S0 历史占位白名单为 Go `backend/go/main.go` 与 Java `backend/java/InfraPlaceholder.java` 的非业务启动/健康/transport echo 骨架；清单不允许其承载业务。按后端分别退出：该后端第一次业务实现开始即移除业务路径的占位豁免；另一后端仍按明确占位清单验证，不能永久跳过结构规则。新规则暴露的旧实现偏离必须在迁移任务消除，不能 grandfather。单次跨服务迁移需 Task Spec 明确列出迁移文件/职责、范围和退出条件。
- **SRC-07**：Task `allowed_paths` 仅限定可修改范围，不是架构豁免。普通业务任务按服务职责收窄；结构/依赖检查和行为测试共同验收。规范冲突必须在实现前升级，禁止事后修改架构追认错误布局。

<a id="section-10-1"></a>
### 10.1 spec/ 各目录的职责

| 路径 | 回答的问题 | 禁止内容 |
| --- | --- | --- |
| architecture/decisions | 为什么这样设计，哪些已经冻结？ | 临时实现笔记 |
| domain | 业务对象与行为是什么？ | 某语言的类结构 |
| invariants | 无论实现如何都必须成立什么？ | 性能猜测 |
| acceptance | 怎样判定阶段/Loop 通过？ | 不可验证的“基本完成” |
| progress/current.md | 现在整体在哪里？最后已验证状态是什么？ | 任务细节堆积 |
| checkpoints | 稳定里程碑的可恢复快照是什么？ | 每次小编辑日志 |
| handoff/agent-context.md | 新 Agent 先知道什么？ | 重复全部文档 |
| tasks | 下一件可执行工作是什么？允许修改哪里？ | 架构自由发挥 |

<a id="section-11"></a>
## 11. 公共契约与双后端实现

<a id="section-11-1"></a>
### 11.1 唯一权威

Canonical Contracts 位于 contracts/，同时驱动 Go、Java/Spring 和客户端 SDK。契约包含 OpenAPI/HTTP、WSS envelope 与消息类型、错误码、协议版本与 capabilities、数据库 schema/migrations、Plugin API、Golden Test Vectors。实现代码不得成为反向权威。

<a id="section-11-2"></a>
### 11.2 等价而非同构

| 必须相同 | 允许不同 |
| --- | --- |
| HTTP/WSS 可观察行为、错误码、事务语义、幂等、顺序、Sync、插件权限、数据库结果；§3/§10 服务职责、源码归属和依赖方向 | 服务内部框架、包结构、依赖注入、ORM/SQL 工具、线程/协程模型、内部接口 |
| Release Manifest、健康检查、metrics 标签、日志关联字段 | 内部模块名称与代码风格 |

内部结构可不同不等于可自行选型；§2.3 适用于所有新增 architecture-sensitive framework、ORM、runtime 与核心依赖。§11.2 的可不同栏目仅表示在各自已批准技术决定内不要求同构。

<a id="section-11-3"></a>
### 11.3 Golden Contract Tests

```text
同一 fixture 输入 -> Go profile -> 规范化结果 A
同一 fixture 输入 -> Java profile -> 规范化结果 B
断言 A == Canonical Expected && B == Canonical Expected
必须覆盖：auth/session、friend/direct uniqueness、group idempotency、message ACK/outbox、retry、sync gap、plugin permissions、errors/version negotiation
```

<a id="section-11-4"></a>
### 11.4 数据库迁移

两套后端共享数据库语义，但单次部署只运行一个 profile。migration 由独立迁移组件执行，不允许应用实例竞争执行。所有兼容窗口内的服务与客户端 fixture 必须通过 migration 测试。破坏性 schema 变更采用 expand -> migrate/backfill-> switch -> contract，多版本共存期间禁止先删旧字段。

<a id="section-11-5"></a>
### 11.5 公开 Sync HTTPS 绑定（Human-approved ADR-0008 候选）

公开拉取通过 HTTPS POST /v1/sync/user 与 /v1/sync/conversation；唯一机器权威 contracts/http/sync.openapi.json，复用现有四种 Sync v1 形状和既有 Bearer/HTTP 错误目录。WSS realtime/ACK 保持原义，不添加 Sync envelope。Gateway 仅代理，Core 负责每请求数据库权威 Session、用户隔离、会话成员授权、稳定已提交分页；无新服务/依赖/数据库对象。

用户初值 cursor 为 0，后续 opaque cursor 绑定认证用户、可跨其 Session 重放；客户端不解析/排序。仅 friend/conversation/membership/plugin metadata；消息仍使用会话 seq。内部 cursor_id 可在响应投影为 external event.cursor/nextCursor，既有 producer payload/schema 不改。任意正整数 limit 仍合法，effectiveLimit=min(limit,100)，先精确取 cap 再有界转换。空页 terminal（user 保持输入 cursor）；非空 user nextCursor=末事件 cursor 且前进；hasMore 要求非空进展且存在额外已提交合格项，不能跳过并发晚提交。会话消息从 afterSeq+1 有序连续；客户端仅跨无 gap 前缀推进 contiguous_seq，数据/cursor 同事务不变。

100 仅限制单页，不限制总同步条数或页数。客户端每页数据与游标/连续序号事务提交成功后，若 hasMore=true，用户流使用 nextCursor、会话流使用已提交无 gap 前缀的 afterSeq 继续拉取，直到 hasMore=false；不得以固定总条数或总页数提前截断。终止页表示该次读取可见的已提交最新状态，不保证终止后的新写入已经同步；后续实时流/再次同步承担新变化。

成功/可解码有效 requestId 的 canonical error 与 body UUID 关联；不可关联格式错误用 server UUID。具体认证、字段、错误码/状态、资源界限和关联行为以 contracts/ 为准，不从实现推导。无效/外账号 cursor 400 VALIDATION_FAILED，不存在/非成员会话403 AUTHORIZATION_DENIED。未列入错误目录的服务器/传输失败不得冒充成功页或推进 cursor。查询参数禁止，入口 HTTPS、日志/错误无凭据，响应 no-store。

批准来源与兼容/迁移见 ADR-0008。此绑定仅经 fresh independent Review、精确候选 hosted CI、protected integration/actual-main 与主仓库同步后生效；接受后仍须展示具体 Go 入口实现方案并取得 Human 同意才可写 Go 产品代码。SYNC 仍须真实服务与客户端独立接受；本前置不等于 Task SYNC/S2 Gate PASS。

<a id="section-12"></a>
## 12. AI Development Loop

```mermaid
flowchart LR
  Context["读取上下文"] --> Repo["恢复真实任务状态"] --> Plan["PLAN"] --> Implement["新 Implementation Agent"] --> Test["本地验证 + 候选提交"] --> Review["新独立 Review Agent"]
  Review -->|"FAIL"| Failure["新 Fix Agent；授权范围内修复"]
  Failure --> Test
  Review -->|"PASS"| CI["适用真实 CI；核对 head SHA 与必跑作业"]
  CI -->|"FAIL"| Failure
  CI -->|"PASS"| Complete["接受任务；更新队列/证据/current/checkpoint"]
  Complete --> Handoff["HANDOFF / 下一依赖满足任务"]
```

> 实现/修复与接受候选的 Review 必须是真实不同的新上下文；同一上下文改角色名不是独立审查。单写者；普通失败进入修复与新的独立 Review 循环。验收依据是权威规范、契约、候选 diff、结构/依赖/最小性检查及真实测试结果。
>
> 图 12-1 Agent 工作流。开发自动化和 CI/CD 是两个独立系统。

<a id="section-12-1"></a>
### 12.1 Task Spec 模板

```text
task_id: LOOP1-MSG-003
goal: implement WSS text message sending
inputs:
 - spec/architecture/README.md # resolve §3/§10/§11 + Minimality Contract
 - spec/domain/messaging.md
 - spec/invariants/messaging.md
 - contracts/websocket/
allowed_paths:
 - backend/go/core/message/**
 - backend/go/core/outbox/**
 - backend/go/tests/**
acceptance:
 - applicable source ownership and dependency checks pass
 - contract tests pass
 - retry is idempotent
 - ACK only after durable commit
forbidden:
 - change public contract
 - change DB contract without migration
 - modify Java implementation
```

<a id="section-12-2"></a>
### 12.2 状态队列

backlog -> ready -> active -> review -> done

- 进入 ready: inputs 完整、依赖完成、验收可执行
- 进入 active: 分配唯一 owner/agent、建立 task branch
- 进入 review: 实现完成 + 本地最小验证 + handoff 完整
- 进入 done: 对精确候选的适用真实 CI PASS + 新独立 review 接受 + progress 更新；Task PASS 不等于整个 Stage Gate PASS。ADR-0001 临时 bootstrap 机制仅在 LOOP1-CI-001 operational 且 done 前有效，现已失效，不得恢复为绕过方式。

<a id="section-12-3"></a>
### 12.3 Git 工作模式

采用 main + task/，不引入复杂 GitFlow。每个任务独立分支、最小提交、CI、Review 后合并。Agent 不得长期堆积跨任务改动，也不得为了让 CI 变绿而修改无关测试或公共契约。

<a id="section-13"></a>
## 13. Agent 启动与交接协议

<a id="section-13-1"></a>
### 13.1 强制读取顺序

| 顺序 | 必须读取 | 退出条件 |
| --- | --- | --- |
| 1 | spec/handoff/agent-context.md | 理解项目边界、frozen decisions 与工作方式 |
| 2 | spec/progress/current.md | 知道当前 Stage、Gate、最后已验证commit、blockers |
| 3 | 按 current.md 的精确 Current Task ID 查找 backlog/ready/active/review/done，必须唯一且 status 匹配 | review 继续独立审查/修复；active 继续实现；ready 验依赖后激活；backlog 保持阻塞；仅当前 done 且无未完当前任务才按依赖选下一任务，禁止 active 为空就跳任务 |
| 4 | resolver/hash、现行冻结正文适用 §3/§10/§11、批准 ADR、Minimality 及任务引用的 domain/invariants/acceptance/contracts | 能复述职责、源码/依赖边界、不可变量、输入输出与验收 |
| 5 | git status、当前 diff、最近提交 | 识别用户/前 Agent 未完成改动，不覆盖 |
| 6 | 最小基线验证 | 确认仓库状态可继续；失败则记录而非盲改 |
| 7 | PLAN -> IMPLEMENT -> TEST -> REVIEW | 仅在授权路径与任务范围内工作 |

<a id="section-13-2"></a>
### 13.2 Handoff 必填项

- Current task / stage / gate
- Completed work
- Files and migrations changed
- Tests: command + result + evidence location
- Known failures / risks / assumptions
- Next exact action
- Last known good commit
- Uncommitted changes and ownership
- Architecture conflicts or ACP/ADR required

<a id="section-13-3"></a>
### 13.3 Checkpoint 规则

稳定 Gate、重要纵向链路、schema/contract 版本切换或可恢复发布点必须生成 checkpoint。checkpoint 记录 commit、contract version、migration level、image digests、fixture versions、通过的 Gate 与已知限制。current.md 始终指向最新 checkpoint，而不是复制其全部内容。

#### 崩溃恢复目标

新的 Agent 不扫描整个仓库重新猜架构。它通过 agent-context -> current -> 精确 Current Task 的真实队列状态 -> referenced specs/contracts -> git status/diff/commits 在一个可控上下文中恢复工作。

<a id="section-14"></a>
## 14. CI/CD 独立校验架构

```mermaid
flowchart LR
  Diff["Diff 分类"]
  Diff --> GoPath["backend/go/**"]
  Diff --> JavaPath["backend/java/**"]
  Diff --> Shared["contracts/** / DB / shared SDK"]
  Diff --> Rules["architecture / Agent / task template / acceptance / checker"]
  Rules --> Structure["规范 + 源码归属 + 依赖 + 触发负例"]
  GoCI --> Structure
  JavaCI --> Structure
  Structure --> Gate
  GoPath --> GoCI["Go CI<br/>unit + integration<br/>contract"]
  JavaPath --> JavaCI["Java CI<br/>unit + integration<br/>contract"]
  Shared --> Matrix["全平台兼容矩阵<br/>Go + Java + clients<br/>plugin + migration"]
  Matrix --> Artifacts["可重复制品<br/>镜像 / 客户端"]
  Matrix --> Smoke["Staging Smoke"]
  Artifacts --> Smoke
  Smoke --> Gate["Release Gate<br/>manifest + rollback"]
```

> Agent 负责提出变更；CI 独立验证事实。Agent 无权自行宣布 Gate 通过。
>
> 图 14-1 Path-aware CI DAG。分类分支相互独立；公共契约/schema/shared SDK 变更按表触发兼容矩阵，规范与检查器变更必须触发适用架构检查。部署/发布节点表示相应阶段要求，不把未来发布能力冒充当前 skeleton。

<a id="section-14-1"></a>
### 14.1 路径感知规则

| 变更路径 | 必跑作业 |
| --- | --- |
| backend/go/** | Go lint/unit/integration/contract；不默认跑 Java |
| backend/java/** | Java lint/unit/integration/contract；不默认跑 Go |
| clients/web/** | Web unit/build/protocol/plugin UI tests |
| clients/desktop/** 或 clients/mobile/** | architecture/client technology guard + 对应客户端 + SQLite migration + protocol tests |
| contracts/**、数据库迁移、shared protocol/plugin SDK | Go + Java + Web + Desktop + Mobile + old client fixtures + plugin fixtures + migration compatibility |
| deploy/**、ci/**、.github/workflows/** | 按当前阶段执行 compose/manifest/security/smoke/rollback validation，并验证分类与 Gate |
| spec/architecture/**、Agent 入口、handoff、活动任务/模板/batch、acceptance、架构检查器与测试 | baseline/resolver/ADR 一致性、活动引用、源码归属、Go/Java 适用阶段依赖检查、触发与正负控制；Markdown-only 不能全部跳过 |

<a id="section-14-2"></a>
### 14.2 流水线层次

static/lint -> unit -> contract -> integration -> compatibility -> build
-> immutable artifacts -> SBOM/signature -> staging deploy -> smoke/E2E
-> release gate -> canary/controlled rollout -> observe -> complete or rollback

<a id="section-14-3"></a>
### 14.3 兼容矩阵

完整兼容阶段的最低矩阵包含 Client Protocol v1、v2、HEAD；在相应协议与客户端版本尚未定义的早期阶段，只能明确报告现有契约向量/占位检查，不能虚构 v2 或声称已通过完整矩阵；后续阶段不得永久豁免。Go/Java profile；Echo/Poll 插件 fixture；SQLite old schema fixtures。服务端只维护一个当前实现版本与有限兼容窗口。latest/recommended/min_supported 必须在 Release Manifest 中显式声明，客户端版本号与 protocol_version 不绑定。

<a id="section-14-4"></a>
### 14.4 CI 与 Agent 的信任边界

Agent 可运行本地测试并提交证据，但 Gate 只能由隔离 Runner 从干净 checkout 重建后判定。核对精确 head SHA、要求运行的作业及实际结果；必跑作业缺失、异常 skip、失败或取消均不满足 Gate。测试环境未启用导致的 skip 不是集成 PASS；旧提交的绿色不覆盖新增要求。历史 ADR-0001 的适用及失效条件见 §12.2。任何需要跳过测试、重录 golden fixture、降低阈值或更改验收项的动作都视为架构/验收变更，必须单独审批。

<a id="section-15"></a>
## 15. Loop 1: 12 周预算、里程碑门禁驱动

```mermaid
flowchart LR
  S0["S0<br/>控制面<br/>W1<br/>Gate PASS"] --> S1["S1<br/>Go 纵切<br/>W2-3<br/>Gate PASS"]
  S1 --> S2["S2<br/>客户端同步<br/>W4-5<br/>Gate PASS"]
  S2 --> S3["S3<br/>Java 等价<br/>W6-7<br/>Gate PASS"]
  S3 --> S4["S4<br/>插件平台<br/>W8-9<br/>Gate PASS"]
  S4 --> S5["S5<br/>工程硬化<br/>W10<br/>Gate PASS"]
  S5 --> S6["S6<br/>5k RC<br/>W11-12<br/>Gate PASS"]
```

> 提前通过即立即进入下一阶段；任何必需项失败则留在当前阶段修复。周数仅是预算窗口。
>
> 图 15-1 依赖图而非固定甘特图。周数表示预算窗口；Gate 决定实际前进时间。原图在 S0 至 S6 七个阶段下方均标有 Gate PASS；此处分别置于对应阶段节点的末行，阶段间箭头仍只表示原图的前进方向。

#### Execution Policy

This loop is milestone-gated, not calendar-gated. A stage MAY begin immediately once all acceptance criteria of the previous stage pass. Agents MUST NOT wait for a scheduled date after Gate PASS, and MUST NOT advance while any required criterion is failed or unresolved.

| 阶段 | 预算窗口 | 范围 | Gate 证据 |
| --- | --- | --- | --- |
| S0 控制面 | W1 | Monorepo、spec/contracts/tasks/progress、CI skeleton、Compose、PostgreSQL/NATS/TLS；冻结 HTTP/WSS/Error/Session/Message/Sync/Plugin API v1 | 新 Agent 仅靠控制面可定位项目、状态、下一任务；契约 lint 与 skeleton CI PASS |
| S1 Go 纵向链路 | W2-3 | 注册/登录、WSS、搜索、好友、唯一私聊、文本发送、ACK、持久化、Outbox、NATS | A 搜索/添加 B 后发 hello，B 实时收到；contract/integration PASS |
| S2 客户端与Sync | W4-5 | Desktop/Mobile SQLite、optimistic/retry/Sync 和完整 Loop1 GUI；Web memory-only 完整 GUI | ACK 丢失/离线 gap/重复乱序 PASS；GUI/Web 完整截图 Architect Approval、独立 Review、精确 HEAD CI 与 main 验证 |
| S3 Java 等价 | W6-7 | Auth/Session/User/Friend/Conversation/Message/Sync/Outbox/NATS | 两 profile 同一 Golden Tests PASS；客户端零改动切换 |
| S4 插件平台 | W8-9 | Registry、Manifest、Permission、WASM、UI Host、Render Bundle、生命周期、Echo/Poll | 两个 fixture 在三端与双后端兼容；sandbox/权限负例 PASS |
| S5 工程硬化 | W10 | path-aware CI、compatibility matrix、migration/plugin tests、Release Manifest、rollback/security | Compatibility CI 可复现；无硬编码跳过；回滚演练 PASS |
| S6 性能与 RC | W11-12 | 500/1000/2500/5000 阶梯压测、profile、修复、soak、RC、architecture snapshot | 单机 5k authenticated WSS Gate PASS；正确性零红线违例；RC 可回滚 |

<a id="section-16"></a>
## 16. Loop 1 性能与可靠性验收

<a id="section-16-1"></a>
### 16.1 固定环境与连接定义

| 项 | Loop 1 定义 |
| --- | --- |
| 被测机 | 单机 8C / 16GB / 3TB；记录 OS、内核、容器限制、文件描述符、网络参数 |
| 连接数 | 5000 authenticated WSS users，不是空 TCP socket |
| 认证链 | TLS -> WebSocket Upgrade -> auth.bind -> Session validation -> Gateway registry -> heartbeat |
| 入口 | Load Generator 必须经过 TLS reverse proxy / 真实入口 |
| 后端 | Go profile 与 Java profile 分开测试、分开出报告 |
| 阶梯 | 500 -> 1000 -> 2500 -> 5000；每级稳定后才上一级 |

<a id="section-16-2"></a>
### 16.2 必测场景

| 场景 | 操作 | 正确性断言 |
| --- | --- | --- |
| 连接 soak | 维持 5000 认证连接与 heartbeat | 异常断连可解释；FD/内存/CPU 无无界增长 |
| 私聊 | 配置活跃率、频率、ACK/投递采样 | 无 ACK-before-commit、无重复逻辑消息、无错投 |
| 群聊 | 10/50/200/500 成员梯度，在线比例可配置 | 单消息单持久记录，fan-out 数量正确 |
| 重试 | 重复 request_id、ACK 丢失、网络中断 | 最终一条逻辑消息，客户端 SENT |
| 离线 Sync | seq 100 离线，服务器到 500；制造乱序和重复 | 101..500 完整、无永久 gap、contiguous_seq=500 |
| 重连风暴 | 批量断开后指数退避 + jitter 重连 | 入口可恢复，无同步雪崩 |

<a id="section-16-3"></a>
### 16.3 观测指标

至少记录 connections、handshake/auth success、CPU、RSS、GC、FD、network、PostgreSQL transaction/lock/latency/throughput、Outbox lag、NATS throughput、ACK p50/p95/p99、delivery p50/p95/p99、Sync latency/gaps、plugin runtime failures。数值 SLO 除 5000 连接与正确性红线外，以实测基线和 acceptance 文件为准，不在此凭空冻结。

<a id="section-16-4"></a>
### 16.4 Gate 判定

#### S6 PASS

5000 个认证 WSS 用户达到规定 soak 时长；所有正确性红线为 0；资源无无界增长；两 profile 均有可复现实验报告；任何降级、限制或瓶颈被记录；Release Candidate、manifest、migration 与 rollback rehearsal 全部通过。

<a id="section-17"></a>
## 17. Release、迁移与回滚规则

<a id="section-17-1"></a>
### 17.1 Release Manifest

```text
release_id / git_commit / build_time
backend_profile: go | java
container_digests / client_artifact_hashes
contract_version / protocol_versions / plugin_api_version
db_migration_level / sqlite_schema_versions
min_supported_client / recommended_client
feature_flags / rollout plan / rollback target
verification evidence links
```

<a id="section-17-2"></a>
### 17.2 发布规则

- 制品不可变：同一版本号不得覆盖镜像、客户端包或插件包。

- 从同一已验证 commit 构建一次，按环境提升制品；禁止生产环境重新构建。

- 先 migration compatibility，再服务端，再客户端；支持窗口内旧客户端必须继续工作。

- staging smoke/E2E、兼容矩阵、security、rollback rehearsal 未通过不得发布。

- Go 与 Java profile 的发布相互独立，但都声明同一 contract version。

<a id="section-17-3"></a>
### 17.3 数据库迁移

| 阶段 | 允许动作 | 禁止动作 |
| --- | --- | --- |
| Expand | 新增 nullable/有默认值字段、新表、新索引（评估锁） | 删除/重命名旧字段 |
| Migrate | 可重入 backfill、双写/双读兼容、验证计数与约束 | 一次性不可恢复数据改写 |
| Switch | 服务开始使用新结构，旧结构仍保留一个兼容窗口 | 混合版本尚在运行时 contract |
| Contract | 证据证明无旧版本依赖后删除旧结构 | 无备份/无回滚点直接清理 |

<a id="section-17-4"></a>
### 17.4 回滚

应用回滚必须指向 manifest 中已验证的前一不可变制品。数据库若已进入不可逆阶段，不得盲目回滚二进制；应优先forward-fix 或使用预先验证的 down migration。插件升级依靠 previous_version + plugin_kv 快照回滚。客户端 SQLite migration 必须保留升级 fixture，无法安全 down-migrate 时采用向前修复。

<a id="section-17-5"></a>
### 17.5 发布失败判定

出现认证失败率异常、ACK/投递错误、Outbox lag 持续增长、schema 兼容失败、插件 sandbox 越权、资源无界增长或正确性红线任一非零时，立即停止 rollout，并按 manifest 执行回滚/forward-fix。事故后生成 checkpoint 与 ADR/修复任务。

<a id="section-18"></a>
## 18. 可观测性、安全与运维基线

<a id="section-18-1"></a>
### 18.1 关联标识

所有链路使用 request_id、server_message_id、conversation_id、session_id（脱敏）、outbox_event_id、plugin_instance_id 关联。Trace 跨 Gateway/Core/DB/Outbox/NATS/Plugin Host 传播，消息正文默认不采集；token 严禁进入日志或 trace，与 §7.4 一致。

<a id="section-18-2"></a>
### 18.2 健康与就绪

| 探针 | 含义 |
| --- | --- |
| liveness | 进程事件循环仍工作；不得因下游短暂失败反复重启 |
| readiness | 能接受新流量：依赖连接、migration level、contract version 均满足 |
| degraded | 插件平台/NATS 局部失败但 IM durable path 可用；明确暴露，不伪装 healthy |

<a id="section-18-3"></a>
### 18.3 安全清单

- TLS 配置、依赖/SBOM、镜像/插件签名、secret 扫描、最小容器权限纳入 CI。

- WSS 鉴权前只允许 auth.bind/ping/pong；每条业务命令校验绑定 Session 与权限。

- 好友、群成员、消息、插件 Action 都有服务端授权；不可相信客户端 UI 隐藏。

- Custom Renderer 使用 CSP、隔离 origin/WebView、Bridge 白名单、配额；不可访问 Host DOM、token、任意网络、本地文件与进程。

- WASM 使用燃料/超时/内存限制与熔断；插件故障不得拖垮 Core。

<a id="section-18-4"></a>
### 18.4 告警优先级

P0: 数据丢失/错投/越权/ACK-before-commit；P1: 大面积认证/连接/Sync 失败、Outbox 堵塞；P2: 资源异常、插件自动禁用、单端兼容退化；P3: 非阻塞性能与开发体验问题。每个告警必须关联 runbook、owner 与最近已知良好 checkpoint。

<a id="section-19"></a>
## 19. 第一批 Agent 可执行任务

任务必须逐个进入 ready。S0 Gate 未通过前，S1 任务不得 active；依此类推。下面清单是阶段规划，不是现行队列快照；按 Task Spec 的真实依赖选择，不以表格/文件名顺序代替依赖。不授权并行修改同一契约。

| Task ID | 目标 | 阶段 | 交付物 | 验收 |
| --- | --- | --- | --- | --- |
| LOOP1-CTRL-001 | 建立 Monorepo 与规范目录 | S0 | repo skeleton; spec/ contracts/tasks/ progress/；README 仅指向权威入口 | 目录 lint PASS；无重复权威文档 |
| LOOP1-CTRL-002 | 编写 agent-context/current/task 模板 | S0 | handoff、progress、task schema | 新 Agent dry-run 能按顺序恢复 |
| LOOP1-CONTRACT-001 | 冻结 HTTP Auth/User/Friend 契约 | S0 | OpenAPI + errors + golden fixtures | schema lint；正/负例齐全 |
| LOOP1-CONTRACT-002 | 冻结 WSS Envelope/Auth/Message 契约 | S0 | auth.bind/ack、message.send/ack/created、session.revoked | contract generator/tests PASS |
| LOOP1-CONTRACT-003 | 冻结 Sync 与 Plugin API v1 | S0 | user cursor、conversation seq、Events/Queries/Actions/UI Host | fixtures 覆盖重复/乱序/权限拒绝 |
| LOOP1-DB-001 | 建立 canonical schema 与migration runner | S0 | users/sessions/friendships/conversations/members/messages/outbox/plugins | 唯一约束与迁移测试 PASS |
| LOOP1-INFRA-001 | Compose + PostgreSQL +NATS + TLS Proxy | S0 | go/java profile skeleton、真实 TLS入口 | clean checkout 一键启动 +smoke |
| LOOP1-CI-001 | Path-aware CI skeleton | S0 | diff classifier、Go/Java/client/shared jobs | 路径矩阵单元测试 PASS |
| LOOP1-GO-AUTH-001 | Go Auth/Session 纵切 | S1 | login/refresh/logout、slot、epoch、auth.bind | 同端替换旧 Session；多端并存 |
| LOOP1-GO-SOCIAL-001 | Go 搜索/好友/唯一私聊事务 | S1 | normalized pair、direct uniqueness、sync/outbox | 并发互加最终 1 friendship+ 1 direct |
| LOOP1-GO-MSG-001 | Go 文本消息 + seq +outbox | S1 | durable ACK、idempotency、dispatcher、NATS | ACK 丢失重试不重复；接收端实时收到 |
| LOOP1-E2E-001 | 首条纵向 E2E | S1 | A 登录搜索添加 B 并发送 hello | 从 TLS 入口运行；证据归档 |
| LOOP1-CLIENT-SQLITE-001 | SQLite schema 与 repository | S2 | UNIQUE(conversation_id, request_id)、UPSERT、migration fixture | 四条入口均幂等收敛 |
| LOOP1-CLIENT-UI-ARCH-001 | 客户端 UI 架构冻结 | S2 | 三端职责、Adaptive Glass Workspace、截图驱动 Architect Review | 独立 Review/CI 与 main 核验后冻结；不代替 GUI 实现 |
| LOOP1-CLIENT-SEND-001 | Optimistic send 状态机 | S2 | SENDING/SENT/FAILED/retry | SENT 不倒退；retry 复用request_id |
| LOOP1-SYNC-001 | 双层离线同步 | S2 | user cursor + per-conversation contiguous_seq | 乱序/重复/交叉实时流无gap |
| LOOP1-CLIENT-GUI-001 | Desktop/Mobile 完整 Loop1 GUI | S2 | Login/session、Chat、Friends、AI Placeholder、Plugin capability/unavailable、Settings/Profile、双主题/本地字体间距、Offline History、SENDING/SENT/FAILED/retry、Sync/reconnect、Desktop notification/tray/shortcut、Android emulator | CLIENT-UI-ARCH 与 spec/acceptance/client-gui.md；真实截图/Architect Review/修复重拍/Approval，再独立 Review、精确 HEAD CI、protected main 核验 |
| LOOP1-WEB-001 | Web 完整 Loop1 GUI | S2 | React + TypeScript；memory only；Chat/Friends/AI Placeholder/Plugin/Settings/Profile、双主题和本地字体/间距 | 无 SQLite/离线历史；遵守 CLIENT-UI-ARCH、client-gui 截图验收和独立 Review/精确 HEAD CI/main 核验 |

### S2 最小任务依赖与执行顺序（Human-approved ADR-0007）

LOOP1-CLIENT-SQLITE-001（已接受） → LOOP1-CLIENT-UI-ARCH-001（UI 冻结已接受，当前规划补充另行验收） → LOOP1-CLIENT-SEND-001 → LOOP1-SYNC-001 → LOOP1-CLIENT-GUI-001 → LOOP1-WEB-001 → S2 Gate。

该补充只新增一个产品 UI ID LOOP1-CLIENT-GUI-001。Desktop/Mobile GUI 独立边界包含上述完整界面及既有发送/同步编排的可观察状态，不重新实现 SQLite、发送或 Sync 领域逻辑。GUI 明确依赖 SQLITE、UI-ARCH、SEND、SYNC 四个已接受任务；Web 完整 GUI 使用原 LOOP1-WEB-001 且在 GUI 后执行。各任务在真实队列中唯一存在，依赖未接受不得激活；本轮 Human endpoint 为 SEND done，后续任务保持 backlog。

GUI/Web 均须引用 spec/acceptance/client-gui.md 和 CLIENT-UI-ARCH，完成真实运行截图 → Architect Review → 修复 → 重新截图 → Architect Approval → fresh independent Review → exact-head applicable hosted CI → protected integration/actual-main verification。S2 不实现 AI API/chat/Agent/RAG、Plugin runtime、Marketplace、S4 renderer 或新公共 API；Web 始终 React/TypeScript memory only、no SQLite、no offline history。偏好仅存外观设置，不授权聊天持久化；未冻结具体存储机制按 §2.3 先决策后实现。

<a id="section-20"></a>
## 20. 后续任务队列与依赖

| Task ID | 依赖 | 目标 | Gate |
| --- | --- | --- | --- |
| LOOP1-CLIENT-UI-ARCH-001 | LOOP1-CLIENT-SQLITE-001 | UI architecture 冻结与当前 MVP 规划补充验收 | S2 |
| LOOP1-CLIENT-SEND-001 | LOOP1-CLIENT-SQLITE-001 + LOOP1-CLIENT-UI-ARCH-001 | Desktop/Mobile 发送编排；Repository 先持久化再 WSS，ACK/realtime/Sync 收敛、FAILED/retry 同 ID | S2 |
| LOOP1-SYNC-001 | LOOP1-CLIENT-SEND-001 | 双层 Sync 编排及断线重连；保留领域职责 | S2 |
| LOOP1-CLIENT-GUI-001 | LOOP1-CLIENT-SQLITE-001 + LOOP1-CLIENT-UI-ARCH-001 + LOOP1-CLIENT-SEND-001 + LOOP1-SYNC-001 | Desktop/Mobile 完整 GUI；CLIENT-UI-ARCH、client-gui 截图/Architect/独立 Review/CI/main 验收 | S2 |
| LOOP1-WEB-001 | LOOP1-CLIENT-GUI-001 | Web 完整 Loop1 GUI；React/TypeScript memory only，无 SQLite/离线历史，同一截图验收 | S2 |
| LOOP1-JAVA-AUTH-001 | S2 PASS + Auth contracts | Java/Spring Auth/Session 等价实现 | S3 |
| LOOP1-JAVA-IM-001 | Java Auth + IM contracts | Friend/Conversation/Message/Sync/Outbox/NATS | S3 |
| LOOP1-PARITY-001 | Go + Java core + S2 PASS | Golden parity；同一客户端制品/代码无需业务修改切换 Go/Java profile，GUI 不改写协议，两 profile 当前关键纵向流程通过 | S3 |
| LOOP1-PLUGIN-REG-001 | Plugin API v1 | Registry、immutable artifact、validation | S4 |
| LOOP1-PLUGIN-WASM-001 | Registry | WASM host、permissions、limits、circuit breaker | S4 |
| LOOP1-PLUGIN-UI-001 | Registry + client hosts | Declarative UI/Render Bundle review/sandbox；遵守 CLIENT-UI-ARCH，禁止控制一级导航；真实宿主 UI 证据，显著视觉变化按 client-gui Architect 截图验收 | S4 |
| LOOP1-PLUGIN-LIFE-001 | WASM/UI | install/enable/disable/uninstall/upgrade/rollback | S4 |
| LOOP1-PLUGIN-FIX-001 | Plugin runtime | Echo/Poll 在 Web/Desktop/Mobile 真实宿主 UI 与两 profile 验证；真实运行证据及适用 Architect 截图批准 | S4 |
| LOOP1-COMPAT-001 | S4 PASS | Web/Desktop/Android 与 old-client 兼容矩阵、SQLite migration、UI/theme/local preference 与 Plugin UI compatibility | S5 |
| LOOP1-RELEASE-001 | compat CI | Desktop/Android 实际制品、Web 制品、manifest/hash/signing、install/upgrade/rollback smoke 和 staging rehearsal | S5 |
| LOOP1-LOAD-001 | S5 PASS | Go load generator + scenarios + evidence format | S6 |
| LOOP1-LOAD-GO-001 | load harness | Go 500->5000 benchmark/soak | S6 |
| LOOP1-LOAD-JAVA-001 | load harness | Java 500->5000 benchmark/soak | S6 |
| LOOP1-RC-001 | all gates | 三端最终可运行制品、关键 GUI smoke；相对最近 Architect-approved 截图集有实质视觉变化则重拍并批准；最终 5k/RC/rollback/architecture snapshot，容量负载由 harness 承担，不把 GUI 自动化放入 5000 WSS 热路径 | Loop 1 |

<a id="section-20-1"></a>
### 20.1 依赖纪律

- 先契约与不变量，后实现；先 Go reference vertical slice，后客户端，再 Java parity。

- 插件平台不得抢跑到 IM 主链稳定之前；兼容 CI 不得延后到发布前临时补。

- 性能优化必须有 profile/metric 证据和回归测试；禁止先加基础设施再找问题。

- 提前完成形成 schedule buffer，并立即推进下一 Gate，不做无验收价值的额外功能。

<a id="section-21"></a>
## 21. Agent 首日执行清单

<a id="section-21-1"></a>
### 21.1 第 0-2 小时

| 动作 | 输出 |
| --- | --- |
| 按第 13 章读取顺序恢复上下文 | 一段不超过 10 行的理解摘要，引用当前 Stage/Gate/Task |
| 检查 git status/diff 与目录现状 | 明确未提交改动归属，不覆盖 |
| 运行最小 verification | 记录命令、结果、耗时；失败则写 blocker |
| 确认 Task Spec 的 allowed_paths/forbidden | 任何冲突先升级，不扩大范围 |

<a id="section-21-2"></a>
### 21.2 第一个实现回合

- PLAN: 从 acceptance 倒推最小实现与测试
- IMPLEMENT: 只改 allowed_paths；先写/更新测试向量
- TEST: unit -> contract -> integration 的最小相关集合
- REVIEW: 新独立 Reviewer 重新读取权威输入，检查行为、职责归属、依赖方向、最小性、diff 与不变量；实现者自检不能替代
- HANDOFF: 更新 task + current.md；Gate 点生成 checkpoint

<a id="section-21-3"></a>
### 21.3 Agent 的停止条件

- 需要改变 frozen architecture、公共契约或安全边界，但没有批准的 ADR。

- 发现当前任务会覆盖他人未提交改动，且无法安全隔离。

- 验收标准不可执行或相互矛盾；必须先修 Task Spec。

- 迁移/回滚存在不可逆数据风险且无明确授权。

#### 开始工作的最短路径

如果仓库尚为空：领取 LOOP1-CTRL-001。完成后立即创建 LOOP1-CTRL-002、三项 Contract 任务、DB/Infra/CI skeleton，并以 S0 Gate 为第一目标。不得直接开始聊天 UI 或插件功能。

<a id="appendix-a"></a>
## 附录 A. Gate Checklist

| Gate | 全部为 PASS 才可前进 |
| --- | --- |
| S0 | spec/contracts/tasks/progress 完整；CI/Compose/TLS/PostgreSQL/NATS skeleton；Agent dry-run 可恢复；无重复权威 |
| S1 | Go Auth -> Friend -> Direct -> Message 全链；durable ACK/outbox/NATS；contract/integration/E2E PASS |
| S2 | SQLITE/UI-ARCH/SEND/SYNC/CLIENT-GUI/WEB 全部接受；Desktop/Mobile 完整 Loop1 GUI，Web memory only/no SQLite/no offline history；client-gui 真实截图/Architect Approval、fresh independent Review、精确 HEAD CI/main 验证；ACK 丢失/离线 gap/乱序重复 PASS |
| S3 | Java 核心等价；Go/Java Golden Tests；客户端零修改 profile switch |
| S4 | Registry/WASM/UI/Render Bundle/lifecycle；Echo/Poll；权限与 sandbox 负例 |
| S5 | Path-aware CI、全平台 compatibility、migration、manifest、security、rollback rehearsal |
| S6 | 两 profile 各自 500->5000；authenticated WSS；soak；正确性红线 0；RC 可回滚 |

#### 通用 Gate 条件

- 功能/交付物完成且与 Task Spec 一致。

- 自动化测试在干净环境通过，兼容性未破坏；适用源码/依赖/规范检查通过，新独立 Review 与精确候选 hosted CI 有效。

- 无未处理 blocker、未批准架构偏离或隐藏 skip。

- spec/progress/current.md 已更新，证据可定位。

- 形成可恢复 checkpoint，记录 last known good commit。

<a id="appendix-b"></a>
## 附录 B. 冻结不变量速查

| 域 | 不变量 |
| --- | --- |
| Session | 同 user/client_type 最多一个有效 Session；不同 client_type 可同时登录；epoch 使旧端失效 |
| Friend | 规范化 pair 唯一；好友与唯一 DIRECT Conversation 同事务 |
| Group | 成员只能来自发起者好友列表；create request 幂等 |
| Message | ACK=durable commit；conversation 内 seq 单调；服务端幂等 key 含 sender/conversation/request |
| Outbox | 与业务数据同事务；NATS 可重复/短暂遗漏；Sync 保证最终完整 |
| SQLite | UNIQUE(conversation_id, request_id)；所有入口事务 UPSERT；SENT 不回退 |
| Sync | user cursor 只管低频状态；消息按 conversation seq；contiguous_seq 不跨 gap |
| Web | 无聊天 DB、无离线历史；页面生命周期之外不保证消息状态 |
| Plugin | 版本制品不可变；权限最小化；WASM/renderer sandbox；后端与 renderer 同版本原子绑定 |
| Architecture | §2.2 权威顺序；contracts/ 是机器可验证公共契约唯一来源；§3/§10 服务职责/源码归属/依赖共同约束 Go/Java；allowed_paths 不豁免架构 |
| CI | 后端路径感知；shared contract/schema/SDK 变更触发兼容矩阵；规范/Agent/模板/检查器变更触发适用架构验证；必跑作业缺失/失败/异常 skip 不能 PASS |
| Release | 不可变制品 + manifest；expand/migrate/switch/contract；发布前验证回滚 |

#### 文档结束

本方案是 Loop 1 的正式执行基线。任何新增目标必须先进入 backlog；任何架构变更必须走 ACP/ADR；任何阶段前进必须以 Gate 证据为准。

Human-approved client clarification under ADR-0005: version remains v1.1; canonical bytes/hash changed; immutable historical PDF and older ADR/evidence unchanged. PR7 withdrawn implementation deviation is not architecture authority. No public contract/ACK/Sync/security/compatibility change.
