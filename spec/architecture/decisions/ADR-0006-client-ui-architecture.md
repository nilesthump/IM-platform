# ADR-0006：客户端 UI 架构与截图验收

状态：Human 已批准设计方向；候选仍待新的独立 Review 和精确 HEAD 托管 CI，尚未在 main 生效。
日期：2026-10-03
批准来源：spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/human-request.txt
补充决定：spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/human-supplement.txt

## 动机与明确决策

Human 要求在 GUI 实现前冻结三端 UI 架构、Adaptive Glass Workspace 设计方向，以及由截图驱动的 Architect 验收。请求明确选择 Desktop 独立 UI、React 内置状态机制和 Mobile ViewModel/StateFlow/Jetpack Navigation Compose。后续 Human 答复将 UI 代码执行禁令限定于 S2，保留 S4 经审查的沙箱 Render Bundle。工作树补充说明授权：没有分配时，在 Codex 设置的工作树目录中自主分配受管理工作树。新增 Human 要求「架构文档用中文编写」，本 ADR 与三份新交付文档据此使用中文。

规范 §6.5 记录全部规范性决定；从属架构/设计文档解释这些要求，不建立另一份规范权威。§6.1 原完整组件复用规则改为各端独立视觉实现，共享协议、模型、适用 hooks、Token 和 UI 语义。不共享 Button/MessageBubble/ChatWindow。Mobile Kotlin 等价行为保持不变；批准的 Navigation/Lifecycle/StateFlow 依赖仅在规范机器策略中限定列出，供未来已批准任务使用。Web 路由以及通用图标/无障碍/工具库类别未选择任何新增具体包。不选择状态管理框架、AI API 或 Plugin 运行时。

## 规范效力与兼容性

semantic_change=true。保留 v1.1。规范正文及哈希已由此前候选更新；已接受输入 aa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c 在 baseline.md 中保留为 UI 修订谱系，客户端基础技术来源仍为 ADR-0005。基础修订元数据、ADR-0001 至 ADR-0005、原 PDF546915、PR7/PR8 历史及既有 FAIL/豁免/证据保持不可变。§8.2 安全校验、sandbox、Bridge 和插件契约保持完整；S2 不实现 renderer、下载、安装或运行时。不改变 wire contract、ACK、兼容性、存储 schema、安全权限或后端。不涉及产品/数据迁移。本次中文修订不改变规范正文或其候选哈希。

## 初始交付与生效点

交付文档为 decisions/client-ui/architecture.md、decisions/client-ui/design-direction.md 和 spec/acceptance/client-gui.md。GUI 任务必须要求绑定候选 SHA 的真实运行截图清单、Architect 审查/修复/重拍/批准、独立语义实现 Review，以及适用的精确 HEAD 托管 CI。截图批准不替代这些检查，也不能建立 S2 PASS。

冻结仅在新的独立干净候选 Review、适用的精确 HEAD 托管 CI、被接受的集成与实际 main 验证之后生效。此前已接受 main 仍是最后已知良好提交，产品实现不得将候选当作已接受权威。Reviewer 须检查规范变更、从属文档、精确写入范围、机器策略依赖新增及历史谱系保留。如实记录生效 SHA/CI/main 和受保护同步结果之后，任务才可 done；保留 S1 PASS/S2 OPEN。不激活 SEND/SYNC/WEB 任务。

## 最小性与回滚

范围为三份文档、限定的规范/ADR/索引/清单修订和 Human 要求的 AGENTS 补充；不实现组件、Token 引擎、库安装、插件运行时或 AI。新增工程标识仅服务明确的 Mobile 状态/导航设计，不授权 Room、网络或测试框架。生效前，在已接受 main 不变的情况下修复候选；生效后修正必须使用 Human 批准的纠正 ADR 和新的独立验收，不得重写历史、PDF 或 Recorder。
