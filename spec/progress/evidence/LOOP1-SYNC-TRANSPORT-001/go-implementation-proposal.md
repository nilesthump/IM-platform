# Go Sync 入口实现方案（待 Human 同意，非实现授权）

状态：PROPOSAL_AWAITING_HUMAN_CONSENT_AFTER_PREREQUISITE_ACCEPTANCE。ADR-0008/公开契约须先独立 Review、精确候选/actual-main CI、受保护集成并同步主仓库；此后向 Human 展示本方案，取得同意再创建产品范围。当前没有 Go 产品修改。

## 最小范围与职责

1. Core 的现有 Auth public mux（backend/go/core/auth.go 的 handler 装配）注册 POST /v1/sync/user 与 /v1/sync/conversation；后续任务只允许此处必要路由装配、backend/go/core/sync.go 和必要测试。现有 backend/go/gateway/http.go 已通用代理 /v1/，默认无需 Gateway 产品修改；真实 TLS → Gateway → Core 仍要黑盒验证。根 main/shared 不增加业务。
2. Core Sync 按现有四形状严格解码必填/未知字段，版本/类型、UUID 与整数符合 canonical。使用 Go 标准库 json.Number/math/big 等必要精确整数字段解析：limit 无最大值，先 cap100 再转换；afterSeq 超存储 head 返回空 terminal，禁止 int64 overflow 或 double 丢失。请求不得有 query。不修改通用 Auth decode/errors 以迁就 Sync。
3. Core 复用既有 Bearer/token/database-authoritative Session 校验，每请求检查 ID/epoch/client_type/revocation/expiry；用户从凭据导出，不接受 userId。Session/Auth 写职责、WSS/ACK/cache 不变。Sync 独立的窄错误响应器 echo 已有效解码 requestId，否则 server UUID；catalog/status与优先级依新契约，未知5xx无伪成功页。
4. User Sync 读取当前 user 的已提交 user_sync_events，过滤且验证四种现有低频类型，不加入 Message/session.revoked。起点0；Core 在 response边界将 cursor_id 投影为账户绑定 opaque event.cursor/nextCursor。最小具体候选是标准库 HMAC + base64url 的 user/id token（复用现有受控签名 key，domain-separated cursor payload；无新库/DB表/producer rewrite；无 expiry），只认可对应用户有效已提交事件。token编码不是公共契约，客户端不解析；其他用户/伪造/未知位置拒绝400。此实现细节在授权产品 Task 内再独立审查。
5. User BIGSERIAL 分配不能被误当作 commit顺序。现有 social.go 在低频事件写前锁接收用户行；read端取得相同用户行序列化锁并检查所有现有四类型 producer路径，确保页为已提交稳定前缀，不跳过较小id迟提交；无DB schema改动或新worker。session.revoked不在用户Sync四种事件里。必须用真实PostgreSQL并发事务证明，不凭静态分析承诺。
6. Conversation Sync 在Core验证有效Session和当前membership；不存在/非成员统一403；读取 afterSeq后的最多 effectiveLimit+1 已提交Message，返回有效limit项，按seq从afterSeq+1连续。使用单次一致读取得分页/hasMore；必要现有授权锁按现有顺序，禁止新权限绕过。read-only无Message/Outbox/ACK写入。当前私有 /__core/history 保留已有消费者及测试，不擅自删除/改变私人边界；复用局部查询能力仅当不扩大抽象。
7. 返回四种canonical page，不添加丰富User payload/revision机制。no-store、body/error/log无credentials。真正limit+1/item存在性计算hasMore，空页不循环推进user cursor；客户端数据/游标事务逻辑仍由后续SYNC负责。

## 拟允许产品路径（尚未生效）

- backend/go/core/sync.go（现有服务职责，必要 Sync 请求/page、cursor projection、read查询）
- backend/go/core/auth.go（现有 handler 中两个公共路由的最小装配，既有Auth写逻辑不改）
- backend/go/core/sync_test.go 与必要新 backend/go/core/sync_http_test.go
- backend/go/tests/sync_tls_test.go（若现有 profile 黑盒 harness 适合则复用其最小路径）
- tools/verify_sync_runtime.py（仅必要真实入口运行检查）
- .github/workflows/ci.yml（仅新运行验收检查接入）
- 当前新 Go 产品 Task/进度/证据及 checkpoint 所需精确路径

以上须先由独立产品 Task 写成明确 allowed_paths，实际文件/责任检查后激活；非 blanket backend/**。不增加contracts/schema/producer/client/GUI路径；出现新架构冲突先停该部分。

## 必须通过的运行证据与退出

真实 PostgreSQL + Go Core/Gateway + TLS入口（当前既有部署/harness），不是 offline oracle/profile结果文件。测试有效多页/空页/retry/限额/大整数/关联；缺失、无效、过期、撤销、旧epoch和client mismatch；跨用户cursor/伪造/无权限会话；被阻塞写者和并发commit不得丢低频事件；无gap消息页、readonly/无新Outbox；service/source/import/minimality和旧Auth/social/message/ACK回归。每项绑定实际candidate/environment/output，不制造结果。

fresh independent Review → exact-head hosted applicable jobs → protected integration/actual-main Review和CI → H:/IM-platform同步与SHA记录。Go前置实际服务接受后才评估 LOOP1-SYNC-001 的依赖/输入并恢复Desktop/Mobile双层同步；完成SYNC同样需要独立Review/CI/真实客户端运行和主仓库同步。最终在SYNC完成后停止，GUI/Web不继续；Go任务PASS并不等于SYNC/S2 PASS。

## Human 分页修正与真实验收要求

100 仅限制单页，不限制总同步条数或页数。客户端每页数据与游标/连续序号事务提交成功后，若 hasMore=true，用户流使用 nextCursor、会话流使用已提交无 gap 前缀的 afterSeq 继续拉取，直到 hasMore=false；不得以固定总条数或总页数提前截断。终止页表示该次读取可见的已提交最新状态，不保证终止后的新写入已经同步；后续实时流/再次同步承担新变化。

真实 PostgreSQL + Go/Gateway/TLS 验收必须为 user 与 conversation 各准备超过100项的已提交数据，逐页拉到 terminal，断言每页不超过 min(limit,100)、完整总数、身份去重与最后 cursor/seq；证明未在第一页或固定总页数处截断，并验证 terminal 后新提交由再次同步获取。离线向量只判定契约预期，不证明数据库查询、事务或运行入口正确；后续 Desktop/Mobile SYNC 再证明本地事务成功后分页推进。
