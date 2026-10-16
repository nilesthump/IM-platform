# PASS_SPECIALIZED_ERROR_HANDLING_AUDIT_ONLY

独立专项 Agent `/root/group_error_bab8ef3`，全新上下文，未参与实现、Fix、常规 Review，未委派。精确候选 `bab8ef34612ba3a07455c7b674aaff353234db5a`，branch `task/LOOP1-GROUP-PLAN-001`，base `86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0`，审查完整 base..candidate。常规 Reviewer `/root/group_regular_r2_resume` 为不同上下文，其收据及实际消费的报告/发现均独立核 hash。

无专项阻塞发现。assigned/Git root 精确为 `H:/.codex/worktrees/grp/IM-platform`；起止 HEAD/branch/clean 已核验，无 reset/checkout/clean。未获得 source lease，未改 source/Git/main/PR/CI；仅写本外部目录。99 changed paths 的 bytes/SHA/Git blob 见 source-inventory.json；职责与覆盖见 review-inventory.json。六个产品树 contracts/backend/clients/plugins/deploy/.github 与 base 相同。唯一当前可执行变更为 ci/check_s2_planning.py；两份修改测试及实际调用者已读。

已按启动顺序恢复唯一 review Task，核 canonical33b7b2a0/PDF546915，读必需章节、ADR5–13、领域/不变量/验收、治理、Research及两阶段recovery。旧ERROR接受仅引用Coordinator已核原件摘要，不重复产品历史审查。

保留 catch 逐项结论：

- checker:94：authority文件IO、hash/谱系/批准/JSON/UTF8/对象结构错误，返回含原因的非空失败；CLI打印FAIL/exit1。缺policy的{}、缺字段/Task的空哨兵均进入明确拒绝。未知RuntimeError正常传播。
- checker:161：限定证据路径的缺失、不可读、空文件、symlink/reparse和解析环路拒绝，False仅为校验谓词；caller必加missing bounded错误。未知TypeError原样传播。
- checker:168：严格Completion解析的ValueError保留原因并明确FAIL；无默认接受或伪证据。

无新增catch/重试框架。frozen扩展失败列表；architecture governance/all传递checker错误并非零退出；Recovery检查LASTEXITCODE再exit1。既有language_product_enabled已知authority故障只拒绝能力，required governance另行判失败。测试保留拒绝断言与资源清理；OS skip明确可见。OPEN不评估实际Stage，隔离负例验证GROUP未完成则不能声称S2 PASS，I18N身份不随链尾改变。

规划各层一致要求actor好友权限、全批原子Core事务、durable后成功；未知commit/响应丢失诚实未确认，原ID/targets重试，不能推定回滚或假成功；未知异常/清理保留根因。未来契约切片明确runner/回归/现shared步骤及非零传播、旧checksum/锁/回滚。未来0002/PG/三端/截图/Architect均未执行，不计PASS。recovery缺失/损坏证据保持pending，不能复用旧PASS或覆盖未知main。

实际验证：frozen(base86)、planning、architecture-all、88架构测试(1既有OS skip)、35CI测试(4既有权限skip)、clean Acceptance全部exit0；Windows真实junction执行。外部探针证明未知authority/inventory/main RuntimeError与resolver TypeError原对象传播；非法policy明确FAIL；缺GROUP sync的CLI真实exit1、无PASS。命令/时长/原始输出见commands.json、verification.json、probes.json及Recorder。

Recorder `R-GROUP-PLAN-ERROR-bab8ef3-20261016`，parent COORD-20261015，prospective_resume/prework=true/trace_complete=false。启动直读、外部helper/报告封装不在命令捕获；截断authority已分段补读。首探针因外部inspect.py遮蔽stdlib而导入失败，原exit1保留，仅修外部导入路径后通过。related_run_id误填20261015，实际常规run后缀20261016；warning纠正事实，未改旧事件。finish/validate及匹配数见receipt。

结论仅同SHA专项PASS。source/external leases封存后RELEASED。hosted/protected integration/actual-main/safe sync及后续行政候选闭环仍待Coordinator；GROUP backlog/planned，S2 OPEN，未作产品或Stage接受。