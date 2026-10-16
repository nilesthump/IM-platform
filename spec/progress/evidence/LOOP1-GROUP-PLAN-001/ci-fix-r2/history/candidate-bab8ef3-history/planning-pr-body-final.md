将建群、任意有效群成员从本人好友添加成员、三端群聊入口和发言者展示，安排在 I18N 之后、S2 Gate 之前。新增 ADR-0013、冻结架构及基线哈希、领域规则/不变量/产品验收，以及 backlog 任务 LOOP1-GROUP-001。

S2 机器策略和检查器将群聊完成纳入前置条件，并保持语言激活精确绑定 LOOP1-CLIENT-I18N-001。未来首契约切片须同时覆盖 0002 迁移、现有迁移入口及回归适配、现有必需 CI 契约步骤的群聊验证接入；包括权限、幂等、原子提交、失败传播、多端补偿、三端真实入口/原始截图及 Architect 验收。

本轮产品源码、公共契约、数据库迁移和工作流源码均与基线相同。群聊保持 backlog/planned，S2 OPEN。

验证：冻结架构（相对本 PR 基线）、全职责架构检查、S2 planning、88 项架构测试（1 个既有系统适用性 skip）、35 项 CI 测试（4 个既有系统适用性 skip）、Development 和 clean committed Acceptance。原候选 R1 Review FAIL、初次控制字段格式失败及 Recorder 编码/轨迹限制均保留，修复后重新进行两项独立审查。

精确候选：`bab8ef34612ba3a07455c7b674aaff353234db5a`；基线：`86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0`。

最终 SHA 的全新常规 Review 与另一全新上下文错误专项均已通过：

- regular: /root/group_regular_r2_resume; receipt SHA-256 `ac638f5441a8dd5cdcbf9f7123dfda9d12fab111ee2939637a04014ff0c65c6d`.
- specialized: /root/group_error_bab8ef3; receipt SHA-256 `25577cb656bd63980de1959816d489ee963856c17245965f1a809e5e21356231`.

CI 结果以该精确候选和 actual-main 的实际 required jobs/steps 为准。本 PR 的 CI/集成不代表产品群聊完成或 S2 Gate PASS。
