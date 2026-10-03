# ADR-0007：客户端 MVP 任务规划补充

状态：规划核心已独立接受于 candidate7466ce7/PR14/actualmain b60f116a14f9265031bff255db500f3414f2a357，并保护同步 H:/IM-platform；证据 mvp-planning/closure/acceptance.md。本状态发现仅行政收尾，仍待新独立 Review/精确 CI/集成；之后立即执行本轮 SEND。
日期：2026-10-03
批准来源：spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/mvp-planning/human-request.txt

## 动机与决定

ADR-0006 已冻结 UI 架构但 §19/§20 未完整落实产品 GUI 工作。Human 明确批准 minimum-task-count 补全：S2 仅新增 LOOP1-CLIENT-GUI-001，覆盖 Desktop/Mobile 完整 Loop1 GUI，依赖 SQLITE/UI-ARCH/SEND/SYNC；原 LOOP1-WEB-001 是 Web 完整 GUI，保持 React/TypeScript memory only、无 SQLite/离线历史。S2 顺序 SQLITE → UI-ARCH → SEND → SYNC → GUI → WEB → Gate。客户端自有 Settings/Profile、双主题与本地字体间距、真实发送/同步状态及平台能力均在 GUI 任务验收内。

S3 PARITY 兼顾无业务修改切换 profile；S4 PLUGIN-UI/FIX 承接真实宿主 UI、导航限制、截图证据；S5 COMPAT/RELEASE 承接三端兼容、SQLite/主题偏好/Plugin UI、实际制品与安装升级回滚；S6 仅 RC 增加最终三端 GUI smoke 和实质变化重拍批准，5000 WSS 由 load harness 承担。禁止新增 UI parity/plugin/release/soak/E2E ID。GUI/Web 引用既有 client-gui 截图 → Architect Review → 修复重拍 → Approval → fresh independent Review → exact-head CI → protected integration/main 链。

## 影响、兼容与迁移

semantic_change=true（任务规划与 Gate obligations）；v1.1 不变。规范 §15/§19/§20/附录 A 同步，baseline 当前 hash 更新，planning_previous_sha256 记录接受输入 a234bc06。不更改 §3/§6 存储/发送/Sync 职责、技术政策、契约/schema/ACK/security/compatibility；不选新依赖、不迁移产品数据；历史 PDF/ADR-0006/PR7/PR8/FAIL/Recorder 不变。单独最小 ADR 留下新批准来源，避免把已接受 ADR-0006 的旧 CI 当成本轮验收。

## 接受与本轮 endpoint

本次补充在 clean committed candidate 的完整性、architecture、dependency/negative controls、新 independent Review、精确候选 applicable hosted CI、protected merge/actual-main 与受保护主仓库同步完成后生效。之后立即进入 SEND 编排实现；本轮正常停止点 SEND 已独立接受、集成同步且 done；SYNC/GUI/WEB 不激活。UI 架构 Task 已接受内容不撤回，本次 pending 仅指新增规划。

## 最小性与回滚

复用 UI-ARCH 行政任务，产品只新增 GUI ID；其余队列实例化已有规划 ID，不生成未来 S3～S6 新任务层。生效前修复候选；生效后纠正通过新 Human 决定与独立验收，不重写历史。无产品/数据回滚。

## 接受发现

原文候选效力说明为历史流程。当前canonical16e9c7b4通过fresh candidate/actualmain Review与精确hosted5jobs/every stepPASS，v1.1/PDF不变；本段不修改规范职责/边界，S1PASS/S2OPEN。
