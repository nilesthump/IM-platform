---
task_id: LOOP1-GROUP-001
title: 建群、成员添加与三端群聊接入
status: active
owner: /root/completion_coordinator
stage: S2
gate: S2
client_supplement_phase: group_product
---

## Current recovery — 2026-11-05

Human scope is the complete GROUP product on Web, installed Windows Tauri and Android, stopping after GROUP acceptance and safe synchronization; no S2 Gate/next-task advancement. Assigned managed root H:/.codex/worktrees/g-8802/IM-platform; branch task/LOOP1-GROUP-001-resume. Accepted backend/main/LKG remains 3d30872d3d18c55fa8156a5ce1133281ffaa4e7e. Product source de88cf326c520801693480e193cbd50dee9b0853 is unchanged by this test-only Fix.

Exact f7ea fresh regular FAIL REG-F7EA-P2-001 found both current Web runtime runners still using removed inline Friends controls. Fresh Fix updates only those two UI operation/assertion chains: each CREATE opens New chat → Create group, selects the fixture in the dialog, and submits Confirm; success must detach the picker, select the returned conversation and expose its full ID in member management. ADD uses the member ellipsis → Add members → Confirm and verifies the same selected group. Both G06 modes reopen/reselect, retaining original request/target/response and independent DB checkpoints. f7ea operation/report/cleanup causes and privacy behavior remain intact.

Command: `node tests/clients/group/web-runners.cjs <root> <desktop-node-modules> <playwright> <Edge>`.
Result: original f7ea runners RED exit1 (both real current component checkbox lookups absent); final GREEN exit0. Entire runners execute actual React Shell/GroupPanel and WebClient group HTTP/retry/scan logic with controlled login/service boundaries; browser locators/assertions are real. Before-forward and after-commit simulations preserve same request/targets, two distinct created conversations; B adds C through management. No actual service, credentials, device or TLS/DB acceptance claimed. Initial test wrapper missing return failure is preserved.
Command: `python -Xutf8 -B tests/clients/group/verify.py`.
Result: exit0, including existing Python cleanup regression,26 JavaScript cleanup boundary cases, compiled Web/Desktop and group wire/application behavior.
Evidence: `spec/progress/evidence/LOOP1-GROUP-001/product/fix-web-runners-20261105/receipt.json`; external fix-web-runners-1105/research binds exact commands/exit/duration/raw output. All five startup baselines on exact f7ea committed snapshot pass; generated files in worktree remain untouched.

Final Fix SHA requires fresh regular followed by DIFFERENT fresh error review before any push/CI-triggering PR. f7ea FAIL and older reviews cannot accept the new SHA. Remaining real native G01-G09 binding, Architect, exact-head hosted CI, protected integration, actual-main and safe synchronization remain required. Windows fresh recovery independently bound six recaptures and duplicate/older actual UserSync plus SQLite MAX/cursor/message evidence as BOUNDED_PASS (windows-recover-1105/evidence-audit.json); Architect approval remains pending; old21 cached-image batch remains INVALID, preserved. Android final6b APK inputs remain unchanged; real final TLS close/new picker/friend states still pending. v5 root CA expired; replacement v6 and owned-emulator trust helper are prepared but no trust authorization/write is assumed. Concrete scope: external android-final-runtime-1105/trust-approval-request.json. Any new trust write requires specific Human authorization.

Unknown main work remains untouched (last qualified780 untracked+2tracked; historical782 count preserved without inferred cause). No product/native/backend/dependency/contract/schema change. Sole Fix writer owns web.cjs/web-ui.cjs/web-runners.cjs, this Task/current and new receipt until clean commit, then releases to coordinator. Recorder R-FIX-WEB-RUNNERS-1105 prospective_resume is partial: direct startup/reads/helper authoring/edits plus summarized delegation prompt outside capture, honestly finishes FAIL and validates structurally; no acceptance claim. Before files and all previous history are archived byte-for-byte under external fix-web-runners-1105/before-*.md and hash-bound in the new receipt; prior original evidence remains immutable.

Next exact action: fresh final-SHA two reviews, remaining runtime/Architect evidence, exact-head CI/integration and safe main sync. GROUP active, S2 OPEN. Latest checkpoint: spec/progress/checkpoints/2026-10-28-group-windows-feedback.md (bounded, not GROUP acceptance).

# Goal

创建者从本人好友选至少一人建群并自动加入；任意有效群成员从本人的好友列表添加新成员。三端显示真实群成员和非好友发言者身份，复用现 Send/ACK/seq/Outbox/Sync 和 i18n，完整完成 G01..G09。

Current Human UI requirements supersede historical inline Friends entry: New chat opens Add friend/Create group menu; Add friend navigates Friends; CREATE uses a separate searchable picker. Web/Desktop show friend list and removable selected targets, Confirm/Cancel; Android CREATE removes Selected section (ADD retains its layout). Confirm closes on real success and opens the returned group; Cancel sends nothing. Default-hidden management is opened by conversation ellipsis: Web/Desktop side panel, Android separate page. Missing avatars use user-ID initials. Preserve PlugWorldIM style, language/theme/draft/selection/original unconfirmed request. No group-name/removal/announcement/category functionality.

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

普通业务按服务职责窄列，allowed_paths不豁免canonical。首契约已独立接受/集成/安全同步，当前完整GROUP产品按下述Product Activation登记分阶段继续；确有新增输入先修Task范围，不在实施后追认。当前交付为 Human 已授权的完整 GROUP 三端；本轮 Fix 仅测试脚本与恢复记录，具体 runtime/trust 租约单独核验。无跨服务迁移。

- `contracts/http/group.openapi.json`（建群/加人/本人会话快照；唯一新增HTTP权威）
- `contracts/http/verify-group.py`（标准库/现有validator适配，不新依赖）
- `contracts/http/verify-auth-user-friend.ps1`（现全局 ordered registry 仍精确为原15码原序+GROUP_REQUEST_CONFLICT；本Fix R5仅修 EH-R3-P2-001 的 Get-OpenApiStructureErrors 直接边界：只有 pinned checker 明确 schema-invalid exit1 可计结构拒绝；缺Node/launch失败、内部exit2/37及其他非零/未知异常、ConvertTo-Json内部异常正常传播，使整个verifier非零且不报PASS。保留旧15码业务覆盖、全局16码、6正例/21负例/15 mutations及全部原模型/结构断言；不得修改Auth OpenAPI、JS checkers或旧fixtures）
- `contracts/errors/http-errors.schema.json`（仅已批准群操作必要错误）
- `contracts/database/migrations/0002_group_operations.up.sql`
- `contracts/database/migrations/0002_group_operations.down.sql`
- `contracts/database/README.md`（仅新增migration语义/兼容与回滚）
- `contracts/database/migrate.py`（仅现有独立runner支持0001→0002的有序应用、ledger/status与已冻结回退；Fix R6仅修R6-P2-001的applied读取边界，以无歧义结构保留每条真实version/checksum记录，再执行原duplicate/known ordered prefix/canonical checksum验证；拒绝单物理TAB+LF别名行，status/up/down明确非零且无效果。保留0001字节、历史checksum、现事务advisory lock/JSONB guard、重入与真实失败行为；不增加未来migration机制）
- `tests/database/test_migrations.py`（仅上述迁移入口的空库/0001升级/重入/回退/旧fixture兼容正反回归；Fix R6仅追加真实可丢弃PG中单物理version或checksum含TAB/LF而别名为两canonical记录的回归，实际status/up/down非零、ledger/业务schema无效果；原11测试方法及既有行为断言保持，不以skip/隔离text输入代替真实DB）
- `tests/infrastructure/smoke.ps1`（现Go/Java profile的直接验证边界：EH-R3-P2-003要求ledger SELECT保留ORDER BY version，以保留/转义元素边界的结果精确验证两条且仅两条canonical记录0001_initial、0002_group_operations，大小写/顺序精确；拒绝单条含逗号或换行的unknown version、缺失/额外/重复/乱序/大小写错/native非零，不用另一个有歧义join、过滤unknown或动态接受未来migration。EH-R3-P2-002要求仅检查现owned project cleanup的实际结果，cleanup-only失败使操作非零，body与cleanup同时失败保留两因，环境清理仍执行，全部必需清理完成后才输出PASS。保留role/TLS/WSS/Compose、现资源归属和全部其他检查；不加通用错误/清理/重试框架）
- `tests/e2e/go_tls_messaging.py`（同一首契约切片的现Go S1 strict TLS E2E迁移ledger输入适配：Fix R6仅修R6-P2-002的现SELECT/断言，显式ORDER BY version并以保留真实记录边界的结构精确比较两条且仅两条0001_initial、0002_group_operations，拒绝单条含LF的unknown version及缺失/额外/重复/乱序/大小写错/native非零；TLS/hostname反例、Auth/成员/ACK/seq/Outbox/Sync/cleanup及原失败传播保持，不扩大完整E2E产品范围）
- `.github/workflows/ci.yml`（保留已接受首契约在现shared必需contract步骤的群verifier与正负suite；当前产品仅在同一现有shared必需pwsh步骤追加真实`python3 -B tests/clients/group/verify.py`及立即`if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`，满足现Verification独立CI输入。保留全部旧检查/原生非零传播/现作业及选择/版本/依赖，不增workflow/job/framework）
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
- `clients/web/src/ui/react.config.mjs` (existing React wrapper export only: expose useRef required by the approved group dialog; no dependency/runtime change)
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
- `clients/desktop/src-tauri/src/desktop_capabilities.rs` (Human 2026-10-25 tray request: existing Tauri tray left single click shows/restores/focuses main window; right single click keeps existing menu. Only existing tray builder/event binding; no dependency, transport, credential, storage, shortcut or other native change.)
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
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Workspace.kt`（仅既有Activity-owned同一WorkspaceViewModel的群create/add/retry/select callbacks向现Shell显式透传；无新入口/新VM/业务/native或根源码职责）
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
- `tests/contract/group/**`（Fix R5新增的 `tests/contract/group/test_verification_failures.py` 原6测试方法保持；Fix R6仅在该文件追加R6-P2-002现E2E实际SQL/断言边界的有意义回归：精确两真实记录正例、单LF记录别名及必要缺失/额外/重复/乱序/大小写错/native非零反例，隔离边界证据不冒称真实Docker/TLS接受。原test_group.py全部22测试方法、35valid/30invalid对象与helpers保持）
- `tests/integration/group/**`
- `tests/clients/i18n/verify.mjs`（群资源键/参数负例）
- `tests/clients/i18n/scheduling.mjs`（2026-10-23 coordinator批准：仅现source-derived Workspace fixture补GroupFailure依赖绑定；保持全部现断言与unknown异常原样传播负例，不放宽接受）
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

# Product Activation and Verification Registration

The first public contract slice was independently frozen, integrated and synchronized at candidate82a37fad256ef9ffb69bf5940d296b251cf7266d / protected PR44 actualmain79d39dcbd045597ccc5abd459edd388eed269254. Original acceptance seal: C:/Users/21441/.codex/visualizations/2026/10/18/01a14d96-146d-7f42-9fd8-0fd0c7e399e0/contract-acceptance-seal.json, SHA256 ab4485bf4f50accfc0ac5f975d0acee0237820565c0d326174c11d35e78c3d93. Backend PR70 subsequently accepted/synchronized main3d30872. These are bounded accepted prerequisites; full three-client GROUP remains unfinished.

product_owner: /root/completion_coordinator
product_registration: FULL_GROUP_PRODUCT_RESUMED_BY_HUMAN
product_G01_G09: PARTIAL_RUNTIME_EVIDENCE_PENDING_FINAL_BINDING
product_regular_review: F7EA_FAIL_REG_F7EA_P2_001_NEW_FIX_REVIEW_PENDING
product_error_handling_review: NEW_FINAL_SHA_PENDING_AFTER_REGULAR_PASS
product_hosted_acceptance: PENDING_FINAL_CANDIDATE_BOTH_FRESH_REVIEWS
product_main_sync: PENDING_PRODUCT

The Human full-GROUP resumption supersedes old backend-only/phase-only stops. Exactly one assigned-worktree writer owns each serial fix; separate qualified runtime leases do not grant source writes. No new public contract/native schema/ACK/security/compatibility/dependency authority is granted. Original activation and past grants are preserved in the archived Task, not treated as current owners or new trust authorization.

## Registered verification interfaces and ownership

- `python -Xutf8 -B tests/clients/group/verify.py`：实际编译/运行本次群transport/模型/Repository/分页与UI状态/i18n键参数回退正反例；不启动服务或声称native运行。现shared必需pwsh步骤增加`python3 -B tests/clients/group/verify.py`并立即`if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`，证明原生非零传播；保留原group verifier+29suite及所有旧Send/Sync/GUI/Auth/contract检查、现jobs/classifier/版本/依赖，不藏进仅i18n键检查、不增workflow/job/framework。
- `python -Xutf8 -B tests/integration/group/runtime.py --config <owned-public-config> --scenario <G01|G02|G03|G04|G05|G06|G07|G08|all> --out <owned-out>`：真实Go/PG/NATS/TLS黑盒及故障编排。`python -Xutf8 -B tests/clients/group/runtime.py --config <owned-public-config> --serial <owned-actual-Android-serial> --capture --out <owned-out>`：真实浏览器/同候选构建安装Windows Tauri/独占Android Studio emulator入口与原图manifest；未实现前均planned/不可计PASS。public config仅fixture ID、公开endpoint/路径、own schema/project/端口/serial、构建安装hash/资源owner；无password/token/privatekey。凭据只现安全环境/PGPASSFILE路径与应用内现通道，不由Agent读/复制凭据。
- 本地PG由获runtime lease的owner新建随机own schema，用现PGOPTIONS exact search_path不含public回退、同child libpq路径与既有canonical migrate.py status/up/status应用0002；Go连接先真实核DB/user/server/port/current_schema/search_path/ledger。root既有availability原件路径`C:/Users/21441/.codex/visualizations/2026/10/18/01a14d96-146d-7f42-9fd8-0fd0c7e399e0/pg-owned-recovery-20261020-availability.json`、SHA7bd37d4189e60de46439b53a9af949385d17d183b628163a9b592a9912e71e6c仅输入来源，不冒称当前亲核/可清public。运行前按当前独占租约和真实资源身份资格核验，不从历史登记假定未知资源可写。backend/go cwd执行`go test -count=1 -run '^TestGroup' ./core`再全`go test -count=1 ./...`及`go test -race -count=1 ./...`；本地全suite亦新own schema隔离。hosted现Go job已提供新可丢弃PG16/im_ci+NATS、DB_TEST_ENABLE=1与runner，不加新的CI env/flag前置或skip；新TestGroup必须在其现配置真实执行。
- 新group fixture仅自有随机用户/会话/request、唯一条件trigger/function/loopback listeners/processes；不复用遗漏receipt清理的旧messageFixture。PG每写点conversation/member（含批中途）/receipt/user_sync INSERT及UPDATE/Outbox真实trigger拒绝；deferred constraint trigger在实际COMMIT等待/抛错，独立连接核成功前不可见/确定失败全零。test-only装置仅包装既有锁定pgx BuildFrontend在TLS/SASL既有协商之后的IO，使用既有pgproto3与标准库，转发真实COMMIT→观察真正PG CommandComplete COMMIT成功→先独立直连核完整durable，再仅截客户端COMMIT响应/EOF→Core保留真实IO cause正常失败→原ID正常重试原结果，无mock Commit/生产hook/新代理机制/新依赖。auth帧与connConfig不记录/打印，unknown装置错误测试失败。群user按稳定升序FOR NO KEY UPDATE互斥并阻UserSync SHARE，保持现FK KEY SHARE兼容；Session/member/conversation随后按既有职责锁定并重检。真实logout持Session及send持conversation时的条件trigger屏障回归核无user FK锁环，不为群改旧Auth/Message。
- G06单独owned HTTPS relay仅群POST原序列化bytes：首次不转发证明零commit；另一情形转发后独立PG证明完整提交才截客户端响应；三端真实未确认/原ID与memberUserIds点击重试。不能拿旧message ACK relay冒充群HTTP覆盖。清理保留body及cleanup两因；drop仅own triggers/functions/fixture FK依赖（含receipts），关闭own监听/连接/进程并排空goroutines，schema inventory前后保持非own项。不操作unknown资源/数据。

| G | 本产品必须建立的真实证据（当前全部未执行） |
| --- | --- |
| G01 | A-B好友、A建群+B；B-C好友/A-C非好友而B以MEMBER加C；三人同群发现互发及非好友sender真实身份，PG单GROUP/成员/receipt/events/Outbox与实际三端入口绑定 |
| G02 | TLS入口非member/失效Session/非friend/mixed/DIRECT/伪actor/读取和消息越权拒绝，canonical状态码与request关联、全部表零新效果 |
| G03 | create/add同key原targets重放原status/body/createdAt，异targets冲突、重复/顺序规范、already-member仍friend授权、操作/actor/conversation分隔、missingreceipt真实服务器失败 |
| G04 | 真实PG屏障/实际锁等待，同key与不同key/actor重叠、交叉群及login/logout/refresh/send/UserSync竞争，唯一性/稳定提交prefix/单调revision/只actualchange事件 |
| G05 | 上述每写点及真正deferredCOMMIT确定rollback全零；真正服务端COMMIT成功后响应截断产生unknown，保因未确认/原ID重试且无第二效果 |
| G06 | 群HTTP首次未提交及已提交响应丢失，两条真实DB/response时序与三端未确认→点击原ID重试→原结果 |
| G07 | 所有active含new用户各端，无发送亦发现；metadata重复乱序/漏通知/断连、>100持续分页、合法短页/低key插入/inflight dirty再从头扫描；账号/会话隔离 |
| G08 | 群内现Send/ACK loss/retry/seq/单logicalOutbox/SENT终态/无gap；Desktop/Mobile保留库重启和全新own账号DB补偿，Web仅当前页memory在线窗口；非好友/同名sender可区分 |
| G09 | 真实browser/同候选安装Windows Tauri/独占Android emulator建/加/成员/sender及loading/empty/rejected/failure/unconfirmed/retry；en/zh-CN/ja-JP切语不丢draft/selection/原request；双主题及受影响font-density极值原PNG manifest→fresh Architect Review/修复重拍/Approval |

三端应用层保存不可变pending群操作（account/endpoint/type/conversation/requestId/memberUserIds）；同账号refresh/rebind保留内存operation/metadata并绑定新generation，logout/expire/account switch清除，旧closed Repository不继续使用。严格验证群HTTP具体201/200/status和canonicalbody，不把GROUP_REQUEST_CONFLICT丢成generic失败。Web全部friend-only open/send/ACK/realtime/sync gates须接授权snapshot；元数据前首条realtime竞态不得用seq1历史baseline掩盖。TS/Kotlin Repository只账号生命周期内存群snapshot/identity，SQLite v2/原user_state revision+cursor事务保持，不塞成员JSON、不改native/schema。senderId关联授权PublicUser displayName+@username，离线缺真实名称诚实显示可区分ID。Native既有10秒Sync idle衔接独立from-origin持续分页，不能被friend cursor相等早退跳过。

真实构建复用现native.py package/gradle与现Send/Sync/i18n回归；group Android instrumentation用既有-PimSendInstrumentation runner选择器。native.py gui-mobile含旧admin/send-runtime ANDROID_USER_HOME/AVD_HOME，禁止盲用/接管；group runtime只新own childenv+实际serial/源构建安装hash，不创建H:/clone/copy/独立产品实现目录、不改旧harness或WT外产品源。当前NATS/HTTPS/native/ADB/trust runtime租约均NONE；ADB历史3221226505和旧Windows CA过期CLOSED不是可用输入/续期授权。先具体核真实入口默认TLS及资源对象；无须Root写则不加Human流程，任何需要的新信任写仍须具体授权，禁止证书绕过。

最终必须同时满足全部G01..G09、旧Auth/Sync/WSS/Plugin及三端Send/Sync/Web/i18n回归、责任/依赖/Minimality/ErrorHandling、真实截图Architect、最终SHA fresh常规→different fresh专项（任何fix两项重做）→实际required exact-head hosted→protected integration→actual-main/tree→保存未知main安全同步，才可GROUP done。firstslice接受、local/Recorder/截图都不替代产品接受或S2 Gate；当前GROUP active/group_product、S2 OPEN。产品运行原件保存spec/progress/evidence/LOOP1-GROUP-001/product/；此前PHASE1仅外部registration receipt的限制已随root明确PHASE2 grant结束。


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

不实现退群/移除/群主管理/邀请审批/链接/二维码/陌生人拉群/群名编辑/已读/新消息类型/每成员持久投递；不加服务/runtime/库/bridge/ORM/通用工作流或错误框架，不提前S3/S4。不改ACK/security/现兼容语义，不绕过契约独立冻结，不扩大搜索/非成员身份访问。未知main工作不复制覆盖；首契约已在82候选/PR44实际main79独立接受并安全同步，当前按Product Activation登记继续完整Go/三端群产品；本轮为已授权完整GROUP；不把首契约或本地切片当全Task完成。

# Minimality

直接现Core事务与既有Send/Sync/Outbox，现Group/member/create唯一约束优先；加人原结果在response-loss后需最小持久操作receipt，为当前幂等要求而设，禁止泛化任务系统。一次批次全成全败省去部分成功协议。仅群相关入口、数据与i18n键，无新平台或重构。

# Verification

- Minimum activation baseline：`python -Xutf8 -B tools/verify_frozen_architecture.py`、`python -Xutf8 -B ci/check_s2_planning.py`、`python -Xutf8 -B ci/check_architecture.py --scope all --json`，`python -Xutf8 -B -m unittest discover -s tests/architecture`、`python -Xutf8 -B -m unittest discover -s tests/ci`；已有accepted stage-three checker，不豁免。
- Fix R5三项错误回归：`python -Xutf8 -B -m unittest discover -s tests/contract/group -p "test_verification_failures.py" -v`；实际调用当前PS入口/边界，隔离transport shim只控制外部依赖/原生exit，不作为真实Docker/TLS接受。known structural exit1仍为正常拒绝；初始真实Node正例0后，mutation阶段exit2/37/异常终止/launch与内部异常均令完整verifier非零且无PASS。Go/Java smoke成功、仅primary失败、仅cleanup失败、双失败覆盖真实native退出/两因/环境清理/成功输出时序；精确两canonical记录通过，单逗号/嵌入换行version及缺/extra/duplicate/order/case/nonzero拒绝。新增suite必须在现shared Ubuntu runner已有pwsh/Node下实际执行，不用Windows-only skip、未启用环境或新workflow/job冒充覆盖。
- 现契约回归：`pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1`、`python -Xutf8 -B tools/verify_sync_transport.py`、`python -Xutf8 -B -m unittest discover -s tests/contract -p test_sync_transport.py`、`python -Xutf8 -B contracts/websocket/verify.py`、`python -Xutf8 -B contracts/plugin-api/verify.py`，不删除或压低旧检查。
- 首契约切片（已按activation seal独立接受，保留适用回归）：`python -Xutf8 -B contracts/http/verify-group.py`和`python -Xutf8 -B -m unittest discover -s tests/contract/group -p "test_*.py" -v`真实覆盖群schema/正负fixtures，二者须在现有shared必需contract步骤执行并传播非零退出；核对精确hosted SHA/job/step原始日志，不能只核对classifier选择。
- 同一首契约切片的迁移验证：在明确受控、可丢弃PostgreSQL中，配置真实psql/libpq PGHOST/PGPORT/PGUSER/PGDATABASE和安全凭据（不放argv或日志），设置`DB_TEST_ENABLE=1`，实际执行`python -Xutf8 -B contracts/database/migrate.py status`、`python -Xutf8 -B contracts/database/migrate.py up`、再次status及up，并运行`python -Xutf8 -B -m unittest discover -s tests/database -p test_migrations.py -v`。回归分别覆盖空库→0002、保留旧数据/ledger的0001→0002、重复应用无新增、checksum不符拒绝、锁/并发与失败整批回滚；按该切片冻结的回退规则仅在受控库调用现有`python -Xutf8 -B contracts/database/migrate.py down --allow-data-loss`，核对0002的实际schema/ledger回退及重入、旧fixtures/兼容窗口。不得把只测0001当0002覆盖，不新增业务DDL入口。记录0001 up/down原字节SHA-256与历史ledger checksum保持、实际迁移level、命令/启用环境/退出/耗时；现有Go up和compatibility数据库suite的真实hosted执行同样必需。缺PG/psql、未启用或skip均未执行，不计PASS；当前规划轮不运行这些未来迁移/产品检查。
- 三端群回归（实际执行和独立证据绑定才计入接受）：`python -Xutf8 -B tests/clients/group/verify.py`、`python -Xutf8 -B tests/clients/group/runtime.py --serial <实际独占serial> --capture`及Product Activation已登记完整参数/装置。首契约verify-group.py已存在且已独立接受，适用旧契约回归仍必需；三端harness必须匹配当前参数、fault装置/fixture/服务/清理及每G项映射，不能把planned harness当已执行。
- cwd backend/go：`go test -count=1 ./...`及适用现有CC的`go test -race -count=1 ./...`；真实受控PG/NATS使用DB_TEST_ENABLE=1、现pgx实际读取的PGHOST/PGPORT/PGDATABASE/PGUSER/仅path PGPASSFILE、child PGOPTIONS exact own search_path及own NATS_URL执行group integration/concurrency/fault测试。本地执行owner先核服务器身份/随机own schema及隔离，不默认未知DATABASE_URL/public可清空；hosted现有新建im_ci/PG16/NATS配置真实执行，不加新flag或skip gate。缺环境skip不是PASS；`python -Xutf8 -B tools/verify_sync_runtime.py`沿现TLS入口，真实入口接受依实际证据，不能以本地替代。
- `python -Xutf8 -B tests/clients/web/verify.py`、`node tests/clients/web/browser.mjs`；shared/Desktop现`tools/verify_client_send.py --scope shared`和`--scope desktop`、`tools/verify_client_sync.py --scope shared`和`--scope desktop`适用回归。
- Desktop `python -Xutf8 -B tests/clients/gui/native.py package`，Windows现MSVC/Rust/Tauri/locked npm、安装同候选制品并以真实身份运行和截图；host renderer不替代。
- Android `python -Xutf8 -B tests/clients/gui/native.py gradle assembleDebug assembleDebugAndroidTest`，实际独占Android Studio emulator执行group instrumentation及现Send/Sync回归；记录真实serial/API/受控TLS，无私人物理设备/全局trust修改。`tools/verify_client_send.py --scope mobile --serial <实际serial>`、`tools/verify_client_sync.py --scope mobile --serial <实际serial>`仅真实执行才PASS。
- `python -Xutf8 -B tests/clients/i18n/verify.py`及新增群资源负例；screenshot/Architect候选绑定；`pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`，clean committed `-Mode Acceptance`。
- 全部实际命令经Recorder，绑定exit/elapsed/raw outputs；两审/hosted/job selection/actualmain/sync独立证据，不把local/Recorder/截图当最终Gate。

# Evidence

spec/progress/evidence/LOOP1-GROUP-001/；已接受contract/backend历史保持。G01..G09原始DB/请求/故障/三端入口/截图/Architect/双审/hosted/protectedmain/sync按候选SHA保存和绑定。客户端本地/部分runtime证据已执行，完整接受和同步仍PENDING。

# Completion Metadata

acceptance_result: PENDING
accepted_candidate_sha: unavailable
integrated_main_sha: unavailable
main_sync_result: PENDING
independent_review_evidence: unavailable
hosted_acceptance_evidence: unavailable
main_sync_evidence: unavailable
