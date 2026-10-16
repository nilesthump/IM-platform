---
task_id: LOOP1-GROUP-001
title: 建群、成员添加与三端群聊接入
status: backlog
owner: unassigned
stage: S2
gate: S2
client_supplement_phase: planned
---

# Goal

创建者从自己的好友列表选人，创建GROUP会话并自动加入；任意有效群成员均可从本人的好友列表选择新成员加入当前群，好友资格仅针对本次操作者校验。补齐Web/Desktop/Mobile群会话入口、成员与发言者身份展示；复用现有发送、成员鉴权、seq、幂等、ACK、Outbox、分发和Sync，新文案接入现有i18n。依赖I18N及本规划正式接受，位于I18N后/S2 Gate前。本轮仅入队，不激活。

# Inputs

- spec/architecture/README.md -> spec/architecture/baseline.md -> spec/architecture/frozen-architecture.md，先核hash；§2.3/§3/§4.3/§5/§6.1/§6.5/§6.6/§6.7/§10 SRC-01 through SRC-07/§11/§15/§19/§20/附录A/B。
- spec/architecture/decisions/ADR-0013-group-planning.md；已接受ADR-0005/0006/0007/0008/0009/0010/0011/0012及其原始接受；spec/governance/minimality.md、execution-boundaries.md、independent-review.md、technology-selection.md、error-handling.md；research/README.md。
- spec/domain/group.md、spec/invariants/group.md、spec/acceptance/group.md全G01..G09；既有domain/invariants auth-user-friend、messaging、sync-plugin；spec/acceptance/client-gui.md、client-supplement.md。
- contracts/http/auth-user-friend.openapi.json、contracts/http/sync.openapi.json、contracts/errors/http-errors.schema.json、contracts/websocket/envelope.schema.json、contracts/websocket/sync-v1.schema.json、contracts/database/及对应golden fixtures；产品激活前重新枚举真实权威及最新main。
- 已接受I18N/STATE三端源码、真实入口harness与截图证据，仅作为基线，不冒充群聊验收。

# Technology Authorization

沿用canonical§6.1与已接受ADR-0005/0006/0009/0011/0012；无新依赖/语言/框架/runtime。Web保持memory-only；Desktop TypeScript拥有Repository/模型/事务意图，SQLx原子native边界不改；Mobile Kotlin/Compose+Android SDK SQLite等价行为，无TS复用强制。ADR-0013仅明确现群功能和最小契约增量，不扩张native职责。
client_language: TypeScript
client_language: Kotlin
client_framework: React
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

# Dependencies

- LOOP1-CLIENT-I18N-001；独立接受、protected integration/actual-main验证及H:/IM-platform安全同步完成。
- LOOP1-GROUP-PLAN-001；本规划正式独立接受、protected integration/actual-main验证及H:/IM-platform安全同步完成。

# Allowed Paths

普通业务按服务职责窄列，allowed_paths不豁免canonical。下面只授予未来GROUP激活后使用；激活时核对路径，确有新增输入先修Task范围，不在实施后追认。无跨服务迁移。

- `contracts/http/group.openapi.json`（建群/加人/本人会话快照；唯一新增HTTP权威）
- `contracts/http/verify-group.py`（标准库/现有validator适配，不新依赖）
- `contracts/errors/http-errors.schema.json`（仅已批准群操作必要错误）
- `contracts/database/migrations/0002_group_operations.up.sql`
- `contracts/database/migrations/0002_group_operations.down.sql`
- `contracts/database/README.md`（仅新增migration语义/兼容与回滚）
- `contracts/database/migrate.py`（仅现有独立runner支持0001→0002的有序应用、ledger/status与已冻结回退；保留0001字节、历史checksum、锁及真实失败行为）
- `tests/database/test_migrations.py`（仅上述迁移入口的空库/0001升级/重入/回退/旧fixture兼容正反回归）
- `.github/workflows/ci.yml`（仅在现有shared必需contract步骤接入群verifier与正负suite；保留旧检查、真实非零传播及既有作业选择，不增workflow/job/framework）
- `contracts/fixtures/group/**`（canonical正负/并发/幂等/兼容输入与expected）
- `backend/go/core/group.go`（群权限、事务、快照）
- `backend/go/core/group_test.go`
- `backend/go/core/http.go`（仅现HTTP路由注册）
- `backend/go/core/social.go`（仅现user状态事件/Outbox复用所需最小内部提取，不重写好友）
- `backend/go/core/sync.go`（仅已授权群metadata恢复衔接，分页/cursor语义不变）
- `backend/go/core/outbox.go`（仅现低频群状态通知衔接）
- `backend/go/gateway/http.go`（仅现HTTPS代理路由）
- `backend/go/gateway/group_test.go`
- `backend/go/tests/group*.go`（跨服务黑盒，不放运行期业务）
- `clients/shared/protocol-sdk/src/group/**`（契约传输adapter）
- `clients/shared/protocol-sdk/src/storage/models.ts`（现群metadata类型）
- `clients/shared/protocol-sdk/src/storage/repository.ts`（仅现metadata读写/群身份投影；不改消息写入与草稿）
- `clients/web/src/application/group.ts`
- `clients/web/src/application/http.ts`（已授权群HTTP transport）
- `clients/web/src/application/client.ts`（群操作与现同步编排）
- `clients/web/src/application/repository.ts`（memory群快照/身份，无存储）
- `clients/web/src/ui/components/Shell.tsx`
- `clients/web/src/ui/components/FriendsPanel.tsx`
- `clients/web/src/ui/components/ConversationList.tsx`
- `clients/web/src/ui/components/Messages.tsx`
- `clients/web/src/ui/components/Header.tsx`
- `clients/web/src/ui/components/GroupPanel.tsx`
- `clients/web/src/ui/i18n/en.ts`（群聊键/参数）
- `clients/web/src/ui/i18n/zh-CN.ts`（群聊键/参数）
- `clients/web/src/ui/i18n/ja-JP.ts`（群聊键/参数）
- `clients/web/src/ui/i18n/resources.ts`（群聊键/参数）
- `clients/web/src/ui/style.css`（仅新入口必要现有tokens布局）
- `clients/desktop/src/application/ui/group.ts`
- `clients/desktop/src/application/ui/auth.ts`（现HTTP transport，不改认证）
- `clients/desktop/src/application/ui/workspace.ts`（现群/同步编排）
- `clients/desktop/src/ui/components/Shell.tsx`
- `clients/desktop/src/ui/components/FriendsPanel.tsx`
- `clients/desktop/src/ui/components/ConversationList.tsx`
- `clients/desktop/src/ui/components/Messages.tsx`
- `clients/desktop/src/ui/components/Header.tsx`
- `clients/desktop/src/ui/components/GroupPanel.tsx`
- `clients/desktop/src/ui/i18n/en.ts`
- `clients/desktop/src/ui/i18n/zh-CN.ts`
- `clients/desktop/src/ui/i18n/ja-JP.ts`
- `clients/desktop/src/ui/i18n/resources.ts`
- `clients/desktop/src/ui/style.css`（仅新入口）
- `clients/mobile/app/src/main/kotlin/im/platform/client/group/**`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt`（仅现HTTP transport，无认证语义修改）
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Shell.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Chat.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Friends.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/ConversationList.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Messages.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Group.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n/**`（仅现纯数据群资源与键）
- `clients/mobile/app/src/main/kotlin/im/platform/client/storage/Repository.kt`（仅现metadata读写/群身份投影；不改消息写入/草稿/SQLite事务adapter）
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/group/**`
- `tests/clients/group/**`
- `tests/contract/group/**`
- `tests/integration/group/**`
- `tests/clients/i18n/verify.mjs`（群资源键/参数负例）
- `tests/clients/i18n/compiled.mjs`（群资源键/参数负例）
- `ci/check_s2_planning.py`（仅GROUP phase/完成事实，不能自删Gate要求）
- `tests/architecture/test_s2_planning.py`（对应完成/阻断负例）
- `spec/tasks/backlog/LOOP1-GROUP-001.md`
- `spec/tasks/ready/LOOP1-GROUP-001.md`
- `spec/tasks/active/LOOP1-GROUP-001.md`
- `spec/tasks/review/LOOP1-GROUP-001.md`
- `spec/tasks/done/LOOP1-GROUP-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GROUP-001/**`
- `spec/progress/checkpoints/*group*.md`

以上现有路径及新群文件已明确列举；checker/Reviewer核实，无权增加无关页面、根装配、shared业务、native能力。当前没有schema本地变化依据，不授权native SQLite/schema/Composer改动；如契约冻结后证明必要，先按架构/Task流程处理。

# Public Contract Slice

先建立并独立冻结contracts/http/group.openapi.json：POST /v1/groups（requestId、memberUserIds）、POST /v1/groups/{conversationId}/members（requestId、memberUserIds）、GET /v1/conversations（只返回本人有效会话和群成员最小展示身份）。字段/成功结果/错误码/分页资源界限/关联ID/幂等冲突/权限/兼容负例以contracts/唯一机器定义；本Task仅规定必须交付的入口和语义，不成为第二wire权威。复用既有PublicUser/ID/错误形状；读取不泄露非成员会话，返回GROUP种类、成员userId/真实displayName及可区分身份，含非好友成员；状态事件只提供subjectId/revision invalidation不能代替快照。

建群：(actor,create request)；加人：(actor,conversation,add request)，操作类型分隔；目标集合规范化、去重、至少一人且不含操作者。当前授权校验后，同key同集合返回原始已提交结果，同key不同集合冲突。创建利用现(created_by,group_create_request_id)唯一键；必要最小持久幂等结果支持加人重放，additive0002先定义唯一约束/原结果绑定/回滚fixture，绝不重写0001。旧DIRECT/HTTP/WSS/ACK/Sync/旧客户端保持兼容。若资源或具体shape需扩张批准范围，BLOCKED_BY_ARCHITECTURE提出最小问题。

首个契约切片同时交付0002、现有独立migration runner及tests/database/test_migrations.py必要适配，并把群verifier与tests/contract/group正负suite接入现有shared必需contract步骤。真实hosted证据须证明这两个新入口确实执行并传播非零失败，不能只证明路径分类选中了job。现有Go部署/CI仍通过contracts/database/migrate.py up应用canonical schema，既有compatibility步骤仍执行tests/database；不得由Core启动或群verifier偷偷执行DDL，不改写0001绕过runner。保留0001 up/down原字节及历史checksum、既有checksum不符拒绝、事务advisory lock、ledger原子性和失败传播；0001→0002及空库到0002、重复up、受控回退和旧fixture兼容须实际验证，详见Verification。

契约/runner/回归/现有CI接入作为同一个首契约切片，须clean commit、fresh常规Review→different fresh错误专项→exact-head适用hosted CI→protected integration/actual-main→主目录安全同步独立冻结接受并登记实际contract SHA，才实现Go/客户端；本planning接受不是新公共契约已冻结。中间契约切片不使整个GROUP done。

# Server Transaction and Sync

Core在一个PG事务中按当前Session校验actor；create校验每目标本人好友并加入创建者；add校验GROUP/当前有效成员和每目标本人好友。目标已有有效成员为无新增效果但仍验证其好友资格；任一目标非法全批失败。锁/唯一约束使同key并发与不同request重叠归并，写群/新增成员/持久原结果/所有受影响用户conversation.changed、membership.changed及对应Outbox同事务，COMMIT后才成功。仅实际变化产生逻辑变更；原key重放不产生第二群/成员/事件。注入每写点失败证明全部回滚。

低频事件面向全部当前有效成员含新成员及其所有端；现User Sync触发/轮询/reconnect消费invalidations，以授权会话快照刷新群/成员/非好友身份并按revision幂等。丢NATS由持久cursor恢复，不以消息到达作为唯一发现入口。成员加入后沿当前成员鉴权查询已提交群消息，不引入join-seq限制。消息仍现message.send、seq、原身份幂等、ACK、单Message/单Outbox、Gateway local fan-out和conversation Sync；不新增群WSS envelope。Gateway仅代理，不决定好友/成员事务。

# Three Client Slice

Web/Desktop沿既有TypeScript分层和各端独立React视觉；Android Kotlin/Compose等价adapter。不复制发送/Sync领域机制。各端好友入口选本人好友建群，群内任意成员入口选本人好友加人；可见加载/空列表/验证拒绝/成功/失败/提交未确认、可用原ID重试，失败不能伪装空群或成功；选择/草稿/现发送状态在切语言时保持。群会话列表/成员展示/消息senderId关联群身份，不能只查好友造成C匿名或错认；重名仍可区分。新文案/错误呈现/accessibility放现en/zh-CN/ja-JP纯数据资源，参数和英文回退测试，语言偏好与activation_task固定I18N不改。Web只当前在线页面memory，Desktop/Mobile现按账号SQLite/游标事务收敛。

# Error Handling Review

按治理逐文件inventory当前产品范围/源hash/职责；每finding记录位置/触发/掩盖/最小修复/测试，每保留catch说明具体故障→现依据→真实恢复。事务rollback/资源清理保留根因，未知异常/编程错误/不变量破坏正常传播。超时/response loss/commit unknown诚实未确认，保留原request/targets，不能推定未提交、自动换ID或显示假成功。最终SHA fresh regular后different fresh专项，任一修复两项重做；专项FAIL禁止push/CI-triggering PR。真实错误和根因不得用通用兜底/重试平台掩盖。

# Acceptance

完整spec/acceptance/group.md G01..G09：A-B好友、A建群+B；B-C好友、A-C非好友，B加C；三者各端发现群互发辨认sender。非成员/失效Session/非好友/混合批次/伪造actor/DIRECT拒绝；重复/同key异内容/并发/重叠/已有成员；事务失败回滚、提交前与提交后响应丢失原ID重试；多端同步/离线补偿/账号隔离；现ACK/seq/单逻辑Outbox/成员授权/无gap保持。

三端真实入口测试/原始截图manifest及独立Architect Review→修复重拍→Approval；语言三套键参数/可读性完整。真实Go/PG/NATS/TLS和浏览器/同候选安装Tauri/Android Studio emulator，截图不能代替权限/事务/幂等。各切片与最终产品fresh两审、exact-head actual required hosted jobs、protected integration、actual-main CI/完整树/安全主目录同步有精确SHA证据才done；S2保留OPEN直到全部独立Stage条件另行判定。

# Forbidden

不实现退群/移除/群主管理/邀请审批/链接/二维码/陌生人拉群/群名编辑/已读/新消息类型/每成员持久投递；不加服务/runtime/库/bridge/ORM/通用工作流或错误框架，不提前S3/S4。不改ACK/security/现兼容语义，不绕过契约独立冻结，不扩大搜索/非成员身份访问。未知main工作不复制覆盖；本轮仅backlog，不激活或实现。

# Minimality

直接现Core事务与既有Send/Sync/Outbox，现Group/member/create唯一约束优先；加人原结果在response-loss后需最小持久操作receipt，为当前幂等要求而设，禁止泛化任务系统。一次批次全成全败省去部分成功协议。仅群相关入口、数据与i18n键，无新平台或重构。

# Verification

- Minimum activation baseline：`python -Xutf8 -B tools/verify_frozen_architecture.py`、`python -Xutf8 -B ci/check_s2_planning.py`、`python -Xutf8 -B ci/check_architecture.py --scope all --json`，`python -Xutf8 -B -m unittest discover -s tests/architecture`、`python -Xutf8 -B -m unittest discover -s tests/ci`；已有accepted stage-three checker，不豁免。
- 现契约回归：`pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1`、`python -Xutf8 -B tools/verify_sync_transport.py`、`python -Xutf8 -B -m unittest discover -s tests/contract -p test_sync_transport.py`、`python -Xutf8 -B contracts/websocket/verify.py`、`python -Xutf8 -B contracts/plugin-api/verify.py`，不删除或压低旧检查。
- 首契约切片（未来交付后执行）：`python -Xutf8 -B contracts/http/verify-group.py`和`python -Xutf8 -B -m unittest discover -s tests/contract/group -p "test_*.py" -v`真实覆盖群schema/正负fixtures，二者须在现有shared必需contract步骤执行并传播非零退出；核对精确hosted SHA/job/step原始日志，不能只核对classifier选择。
- 同一首契约切片的迁移验证：在明确受控、可丢弃PostgreSQL中，配置真实psql/libpq PGHOST/PGPORT/PGUSER/PGDATABASE和安全凭据（不放argv或日志），设置`DB_TEST_ENABLE=1`，实际执行`python -Xutf8 -B contracts/database/migrate.py status`、`python -Xutf8 -B contracts/database/migrate.py up`、再次status及up，并运行`python -Xutf8 -B -m unittest discover -s tests/database -p test_migrations.py -v`。回归分别覆盖空库→0002、保留旧数据/ledger的0001→0002、重复应用无新增、checksum不符拒绝、锁/并发与失败整批回滚；按该切片冻结的回退规则仅在受控库调用现有`python -Xutf8 -B contracts/database/migrate.py down --allow-data-loss`，核对0002的实际schema/ledger回退及重入、旧fixtures/兼容窗口。不得把只测0001当0002覆盖，不新增业务DDL入口。记录0001 up/down原字节SHA-256与历史ledger checksum保持、实际迁移level、命令/启用环境/退出/耗时；现有Go up和compatibility数据库suite的真实hosted执行同样必需。缺PG/psql、未启用或skip均未执行，不计PASS；当前规划轮不运行这些未来迁移/产品检查。
- 未来新增（当前不存在/不可计PASS）：`python -Xutf8 -B contracts/http/verify-group.py`，`python -Xutf8 -B tests/clients/group/verify.py`、`python -Xutf8 -B tests/clients/group/runtime.py --serial <实际独占serial> --capture`。激活后先实现/登记参数、fault hooks/fixture/服务/清理及每G项映射；若命令有变化先Task更新，不能把planned harness当已执行。
- cwd backend/go：`go test ./...`；真实受控PG/NATS使用DB_TEST_ENABLE=1及受控DATABASE_URL/NATS_URL执行group integration/concurrency/fault测试，缺环境skip不是PASS；`python -Xutf8 -B tools/verify_sync_runtime.py`沿现TLS入口。
- `python -Xutf8 -B tests/clients/web/verify.py`、`node tests/clients/web/browser.mjs`；shared/Desktop现`tools/verify_client_send.py --scope shared`和`--scope desktop`、`tools/verify_client_sync.py --scope shared`和`--scope desktop`适用回归。
- Desktop `python -Xutf8 -B tests/clients/gui/native.py package`，Windows现MSVC/Rust/Tauri/locked npm、安装同候选制品并以真实身份运行和截图；host renderer不替代。
- Android `python -Xutf8 -B tests/clients/gui/native.py gradle assembleDebug assembleDebugAndroidTest`，实际独占Android Studio emulator执行group instrumentation及现Send/Sync回归；记录真实serial/API/受控TLS，无私人物理设备/全局trust修改。`tools/verify_client_send.py --scope mobile --serial <实际serial>`、`tools/verify_client_sync.py --scope mobile --serial <实际serial>`仅真实执行才PASS。
- `python -Xutf8 -B tests/clients/i18n/verify.py`及新增群资源负例；screenshot/Architect候选绑定；`pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`，clean committed `-Mode Acceptance`。
- 全部实际命令经Recorder，绑定exit/elapsed/raw outputs；两审/hosted/job selection/actualmain/sync独立证据，不把local/Recorder/截图当最终Gate。

# Evidence

spec/progress/evidence/LOOP1-GROUP-001/；未来contract freeze、G01..G09原始DB/请求/故障/三端入口/截图/Architect/双审/hosted/protectedmain/sync按候选SHA保存。当前仅规划入队，全部产品验收未执行。

# Completion Metadata

acceptance_result: PENDING
accepted_candidate_sha: unavailable
integrated_main_sha: unavailable
main_sync_result: PENDING
independent_review_evidence: unavailable
hosted_acceptance_evidence: unavailable
main_sync_evidence: unavailable

# Handoff

由LOOP1-GROUP-PLAN-001创建，status backlog/client_supplement_phase planned；I18N后/S2前，本规划接受/同步前阻止激活。无群聊产品实现/接受或截图PASS。last known good 86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0；新规划接受main以后按本规划seal恢复。无产品未提交work。

# Next Action

本轮保持backlog、S2 OPEN并STOP。未来Human授权恢复时核验I18N及本规划实际独立接受/集成/主目录同步，全部满足再唯一队列backlog→ready→active、phase group_product；先契约切片独立冻结接受再实现，不能因active空选择。
