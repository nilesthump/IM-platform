# ADR-0011：Web 外观偏好的最小本地存储

状态：Human-approved candidate；APPROVED_PENDING_FREEZE，未独立接受/生效。
日期：2026-10-09
任务：LOOP1-WEB-001
批准来源：`spec/progress/evidence/LOOP1-WEB-001/freeze-20261009/human-approval.txt`；`human-approval.json` 记录直接 Human 答复与已提交方案 e35c425a90a851540e140078274126ac65606e3e。
精确答复：批准最小前置方案并继续。
semantic_change=true，版本 v1.1。

## 当前责任与决定

已冻结 UI 设计要求重启保持主题/字号/密度，而 Web 聊天仅内存；此前具体外观存储未冻结，守卫与 CI 空骨架阻止产品实现。Human 批准 readiness-20261008/proposal.md 的最小浏览器原生 localStorage 与七个前置文件权限，后在暂停后明确继续。不引入库或第二数据层；这些权限不授权其他架构选择。

唯一适配器 clients/web/src/ui/appearance.ts；唯一 key plugworldim.appearance.v1。版本由 key 标识，JSON exact keys 恰好 theme/fontSize/density：theme cold（Cold AI）或 warm（Warm Creative）；fontSize 14/16/18/20；density compact/comfortable/spacious；默认 cold/16/comfortable。读写均严格验证对象/字段/枚举和最大序列化长度128字符，禁止额外属性。只以固定 key 调用 window.localStorage.getItem/setItem；不导出底层存储或任意 key/任意数据接口。写入为验证后这三个字段的显式投影。 malformed/超长/不可用时回退默认内存外观，不清空其他 origin key；主题修改保持字号/密度。

外观不是账号数据：禁止 message/history/user/session/access/refresh credential/endpoint/conversation/cursor 或其他业务数据持久化。Web Repository/消息始终内存，不加载离线历史。保留禁止 SQLite、IndexedDB、其他浏览器存储、未批准 framework/runtime/dependency/bridge。原生 Desktop/Android 技术、协议、ACK、Sync、公共契约、安全边界与依赖方向不变。

## 前置控制与效力

canonical §6.5 和原客户端 policy 的 web_appearance 描述本决定；baseline 记录 exact digest、上一 accepted canonical a6b1670与批准链接，原 PDF546915不变。guard fail closed：授权链接/哈希/policy不匹配、其他存储路径、任意 key/别名/额外字段和业务持久化均拒绝。静态检查不替代真实行为或语义独立 Review。

已批准 workflow 通过与原 classifier 相同 base/head、--no-renames 含删除的 tests/clients/web/ diff，将变化仅 OR 入 web/architecture；所有输出每 key 一次，其他选择和 CI aggregate gate 原规则不变。Web 与兼容 Web入口执行同一实际 verifier。当前没有产品：仅真实非 symlink 空 .gitkeep、Task唯一backlog/appearance_prerequisite、可信base也无产品允许 PREREQUISITE_SKELETON_ONLY，这不是 Web build/behavior PASS。出现任何产品/部分脚手架则要求完整必需输入、锁定 install、实际 build、behavior/appearance测试及source guard；失败无骨架 fallback。删除已经存在的产品不能重获骨架例外。该阶段控制仅为先验收冻结再实现的当前顺序，产品存在即退出。

fresh independent Review -> applicable exact-head hosted CI -> protected integration -> actual-main verification -> H:/IM-platform safe synchronization 全部完成后才生效；此前 Web backlog 不激活。本候选本地检查/Recorder有效不等于 Task或S2 PASS，截图/Architect Approval/独立产品 Review/真实CI仍完整保留。最新 Human endpoint：Web完整接受并安全同步后停止于S2 Gate前，不对S2 Stage Gate操作；CI aggregate gate必需机制保留。

## 最小性、迁移与回滚

无新库、服务、schema或用户数据迁移。固定一个窄适配器/三个标量直接满足当前重启偏好需要。verifier 将 Web/现有 shared 构建输入复制到一次性系统临时目录安装/构建，以免第三方 node_modules 进入 active source/dependency guard；这只隔离验证输出，不创建仓库或产品复制根。

生效前失败只修复候选并保留已接受 main。生效后的权限/存储纠正须新 Human/Architect批准及独立验收；不得重写旧 ADR、FAIL、Recorder、PDF。v1 key没有用户业务数据，不授权旧key迁移/清除、远程同步或以后版本兼容机制。
