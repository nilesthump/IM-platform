# ADR-0008：公开 Sync HTTPS 拉取绑定

状态：Human-approved freeze candidate；仅经 fresh independent Review、精确候选 hosted CI、protected integration/actual-main 核验及 H:/IM-platform 同步后生效。
日期：2026-10-03
批准来源：spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/human-authorization.txt
任务：LOOP1-SYNC-TRANSPORT-001
semantic_change=true；版本 v1.1 不变。

## 动机与最小决定

SYNC 的四种现有 JSON 形状已有 contracts/websocket/sync-v1.schema.json，但无公开传输绑定。Human 授权先提出并冻结公开 Sync 方案；Go 产品代码另待本前置接受后展示具体方案并取得同意。

新增两个 HTTPS POST 拉取操作 /v1/sync/user 与 /v1/sync/conversation。机器权威为 contracts/http/sync.openapi.json，外部引用现有 UserRequest/UserPage/ConversationRequest/ConversationPage、Bearer 与 HTTP ErrorResponse。WSS 保留实时/ACK，不新增 envelope/type；Core 保有 Sync、成员/用户授权和 PostgreSQL 查询；Gateway 沿用公开 HTTP 代理，不写业务。无新语言、framework/runtime/dependency、服务、DB 对象或通用协议层。

每次请求验证数据库权威 Session；身份只来自 Bearer。用户 cursor 初值 0，随后是当前用户绑定、可跨其 Session 重放的 opaque token，客户端只作相等比较。无效/外账号 token 返回既有400 VALIDATION_FAILED；当前 Loop 1 不引入 cursor 过期、保留窗口或重置协议。user events 仍为四种低频 metadata，排除 Message/Session；边界可把内存/持久化内部 cursor_id 投影为外部 event.cursor 与 nextCursor，无需修改 producer payload/schema。

任何现有正整数 limit 均接受，先精确取 min(limit,100)，再作有界转换；查询最多 effectiveLimit+1 合格项，返回不超过 effectiveLimit。空页终止且 user nextCursor 保持请求 cursor；非空 user 页 nextCursor 为末事件 cursor 并前进。hasMore 仅表示当前读取有额外已提交合格项，不能产生无限无进展页。用户流必须是稳定已提交前缀，不能跳过并发较低序号晚提交；conversation 顺序从 afterSeq+1 连续前进，超 head 空页终止。不改变客户端数据/cursor 同事务或 contiguous_seq/gap 语义。

成功和已解码有效 UUID 的错误响应 echo 请求 body requestId；不可关联的格式错误用 server UUID。错误码/状态仅沿用既有目录，未知服务器或基础设施失败为 non-2xx transport failure，不冒充成功页、不引入错误码。Query 参数一律拒绝，凭据/正文不进入日志/错误；响应 no-store。具体优先级/字段/状态以公开契约为准。不存在/非成员会话统一403避免泄露；权限由 Core 每请求判定。

## 影响、兼容与回滚

新增传输操作，不改现有四形状、Auth API、WSS/ACK、数据库/迁移、存储、客户端技术政策或安全边界。旧 schema/oracle 离线向量保持原样且仍有效；opaque token 的具体编码是后续 Core 边界实现细节，不能反向定义契约。冻结正文增加 §11.5（绑定），baseline 保存旧 canonical hash16e9c7b4 与批准来源。历史 PDF/ADR/失败/Recorder 不改。

候选未接受前不得作为 Go/client 产品实现授权；接受后依然必须先向 Human 展示 Go 实现方案并取得同意。规则接受不代表实际 Sync 服务存在，不解除 SYNC backlog 的 runtime 输入阻塞。新任务只有这一个当前已证明必要的前置，不实例化未来产品/UI 层。撤销未接受候选即可回滚；生效后的调整走新决定与独立接受，不重写历史。
