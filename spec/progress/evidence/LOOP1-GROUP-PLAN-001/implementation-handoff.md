# 本轮群聊规划实现交接

唯一实现writer /root/group_plan_impl；assigned/Git-resolved root H:/.codex/worktrees/grp/IM-platform，base/latest acceptedmain86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0，branch task/LOOP1-GROUP-PLAN-001。旧ERROR恢复由Coordinator核验，recovery-verification.md及两个小JSON为本轮固定引用，旧封存/原件不改。

## 本轮交付与最小性

一个控制Task和一个GROUP backlog，ADR13/canonical4.3/6.7/15/19/20/附录+当前hash/新lineage、group domain/invariants/acceptance、旧验收/I18N append-only后继发现、S2 checker与负例。公共契约/服务/三端未实现，contracts/backend/clients/plugins/deploy树全等base。未来GROUP先独立冻结contract切片，再现Core原子事务/现Send/Sync/UI/i18n；无新技术/依赖/服务/管理/邀请机制。

现contracts HTTP只有Auth/User/Friend/DIRECT与Sync，无GROUP route；FriendshipResult.memberUserIds不是CreateGroup。DB已有GROUP/group_create_request_id及UNIQUE(created_by,group_create_request_id)、成员PK/Sync/Outbox；现Sync UserEvent只kind/subjectId/revision invalidation，因此未来授权快照查询需要最小增量才能发现群/非好友sender身份。新增成员消息历史沿当前member授权，不引入joinseq。持久操作原结果只为add幂等/响应丢失，不预建通用receipt平台。

S2策略追加GROUP及其独立planning接受/同步，保留旧三补充phase和全部原Gate；语言激活改为显式I18N_TASK/I18N_PREDECESSOR常量，绝不用NEW[-1]。标准库检查保留原authorityErrors已知OSError/ValueError/AttributeError→显式FAIL与bounded_evidence既有I/O/路径失败→False，都是当前结构拒绝边界；无新增catch/默认成功。inventory未知读取错误直接失败。completion字段/非空bounded evidence只是必要链接，独立Reviewer仍读原件，不把结构metadata当事实接受。

## 验证与证据

起点frozen/planning各exit0。当前本地结果、精确argv/exit/elapsed/redacted stdout/stderr hashes见local-verification.json与local-outputs/；最终cleanSHA/Acceptance/Recorder/source lease及本次local snapshot之外后续commands见外部implementation/final-receipt.json。local/Recorder PASS不是Task或Stage接受。当前两项最终SHA独立审查/CI/protectedmain/actualmain/sync均PENDING。

## 失败与真实限制

首次普通sandbox branch lock和Task写入Permission denied，未source写入；已授权elevated重试成功。一次rg把Windows路径glob当literal报123；只读目标重新枚举。两项恢复小JSON首次误带external/目录报不存在，随后按实际根路径读取/精确复制。早期startup大段输出截断和嵌套pwsh中文编码失真，必要canonical§2.3/§3/§4.3/§5/§6.1/§10/§11随后用utf8读取；直接读取/外部脚本准备有Recorder gap，prospective_resume/pre_recorder_trace_complete=false，不宣称完整trace。一次并发Recorder事件锁拒绝architecture测试启动，未执行该命令；改为后续实际重新run，原错误保留。既有architecture Windows symlink skip1与CI OSskip4不是新增产品PASS。

协调预提交反馈指出README旧CRLF无关规范化；已从Git86原blob恢复append-only前缀，再只追加本轮发现，旧client-gui/supplement及I18N历史前缀同样逐字节保留。canonical语义修订与baseline当前hash是Human批准范围，旧PDF/ADR/FAIL/evidence/Recorder原字节不改。

## 下一步与租约

提交clean初始review候选后sourcelease RELEASED，仅Coordinator可分配新writer。NEW常规→DIFFERENT NEW错误专项同finalSHA，任何修复重复；之后实际required hosted/保护合入/actualmain/安全同步。内容接受后独立closing writer写真实done/Completion与metadata pending，再同样两审/CI/main/第二次sync；recovery.md固定外部seal消费终态，避免递归source封存。本轮交付后GROUP backlog/S2 OPEN/STOP。Main782unknown/two tracked edits/branch/index未由本writer写。

补充：architectureall外层Recorder输出GBK编码FAIL，旧run真实finishFAIL，structuralvalidateexit0但oneunmatchedcommand仍未闭合；新related resume R-GROUP-PLAN-IMPL-RESUME-20261015外层-Xutf8实跑architectureall/frozen/planningPASS。instrumentation-failures.md与snapshots保留失败/缺失，不倒填旧结果。
