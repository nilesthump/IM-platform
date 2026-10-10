# ADR-0012：S2 客户端补充任务规划与语言偏好窄授权

状态：Human-approved candidate，APPROVED_PENDING_FREEZE；独立Review/精确hosted CI/受保护集成/actual-main验证/H:/IM-platform同步后才正式生效。
日期：2026-10-10
任务：LOOP1-CLIENT-SUPPLEMENT-PLAN-001
批准来源：`spec/progress/evidence/LOOP1-CLIENT-SUPPLEMENT-PLAN-001/human-request.txt`；直接Human原请求和继续事实见authorization.md。
semantic_change=true；沿用v1.1。

## 动机、基线与决定

Web已独立接受并同步，Human明确要求三项串行S2补充，不将已有低层能力或截图等同新端到端故障证明。基线最新行政main b4d271c/PR30，Web产品a1b154d/PR29；实际源码、accepted证据、逐项缺口见client-supplement.md基线表。原SOURCE/Repository/Auth/Send/Sync边界保留。

链为 LOOP1-WEB-001 → LOOP1-CLIENT-STATE-001 → LOOP1-CLIENT-UI-REF-001 → LOOP1-CLIENT-I18N-001 → S2 Gate。三个产品分别独立Task Spec/backlog；前项须独立接受、集成和主仓库同步后方可激活，STATE同时依赖本规划正式接受。S2既有门禁条件与三个新增完成项共同必需。本轮仅规划及其Review/CI/合入同步；三项不实施、不激活，S2 Gate OPEN且不评估。

## 强制目标与验收

### STATE

以最新三端实现和已有验收为基线，逐项记录现有能力、证据和待补齐内容，将以下要求写入任务目标与强制验收。

1. 消息可靠性的两个核心场景：
   A. 首次发送未在服务端提交，发送方超时显示 FAILED，用户点击重发后完成首次持久化并收敛为 SENT。
   B. 首次发送已在服务端提交，接收方已获得消息，发送方因成功确认丢失或延迟显示 FAILED；用户重发后获得原始提交结果，原消息收敛为 SENT。

2. 同一逻辑消息的每次重发复用原始 request_id、conversation_id、发送者身份和消息内容。服务端已有提交时返回原始 messageId、seq、createdAt；最终对应一条持久化消息、一条逻辑 Outbox 和各客户端的一条消息展示。

3. 覆盖 SENDING、FAILED、重发按钮和 SENT 的真实界面状态。FAILED 表达当前尝试未获得成功确认；迟到 ACK、实时消息和适用 Sync 均通过既有收敛入口更新原消息，SENT 保持终态。核对 Gateway/Core 超时与提交结果未知路径，使其处理符合实际提交结果和现行契约。

4. 同一会话的已确认消息以服务端 seq 为最终排序依据，覆盖：
   - R1 首次未提交，R2 先成功提交，R1 后重发成功：最终顺序为 R2、R1。
   - R1 首次已提交但确认超时，R2 随后提交，R1 再获得确认：最终顺序为 R1、R2。
   验证 UI 在 ACK、实时事件、Sync 交叉到达后保持正确身份、状态和顺序。

5. Desktop/Mobile 覆盖保留本地消息时的重启重发，以及受控测试中从全新账号本地数据库和初始同步游标恢复的流程。验证已提交历史按 seq 恢复，后续新消息使用新的 request_id 和服务端分配的序号，序号连续性与渲染顺序正确。Web 按当前页面内存生命周期和已接受的在线消息同步规则验收。

6. 补齐三端好友变更同步。明确既有好友查询和 User Sync 的触发、消费及界面刷新链路；任一端添加好友后，其余在线端最终更新好友列表、对应私聊和名称展示，并验证断线恢复与账号切换后的正确结果。

7. 使用真实服务端、数据库和客户端的受控故障注入验证上述链路。场景 B 同时取得服务端持久提交、接收方获得消息、发送方 FAILED、重发后原消息 SENT 的证据；分别核对存储记录、请求身份、序号、Outbox 和实际渲染。


### UI-REF

以任务一验收后的三端产品树为行为和视觉基线，规划并验收各端现有页面、组件和展示状态的职责拆分。

1. 根据实际源码拆分应用入口、Shell、导航、认证、会话列表、消息展示、输入区域、好友及设置等现有职责，明确入口挂载、组件输入输出、状态归属和导入方向。

2. 保持各端独立视觉实现及现有 Auth、Repository、Send、Sync 职责边界，共享现有协议、类型和适用展示语义。

3. 将组件展示文案、应用状态标识与业务判断建立清晰边界，为后续语言资源提取提供稳定接口。

4. 建立拆分前后的页面、入口、功能和测试覆盖对照表。完整回归现有客户端能力及任务一新增场景，验证状态保持、事件绑定、账号隔离、同步、重发、排序和外观设置的行为等价。

5. 完成各端构建、适用自动化测试、真实运行截图和 Architect 审查，以功能完整、行为等价和视觉基线保持作为验收结果。


### I18N

依赖任务二完成，提取三端现有用户可见文案，建立英语、简体中文和日语的独立语言资源。

1. 统一语言标识 en、zh-CN、ja-JP，以及跨端文案语义和占位参数。Web/Desktop 使用 TypeScript 侧纯数据语言资源，Android 使用现有 Kotlin/Compose 技术栈下的等价资源映射。

2. 覆盖页面文本、按钮、输入提示、校验与错误提示、连接及同步状态、无障碍标签，以及已有系统通知和托盘文案。将状态逻辑使用的稳定标识与翻译后的显示文本分离。

3. Settings 增加固定入口“Language / 语言 / 言語”，使用固定顺序的滚动选择列表：
   English → 简体中文 → 日本語。
   选项名称保持各自语言，切换后即时更新当前界面，本地保存并恢复语言选择。

4. 将语言选择的本地持久化范围、存储位置、字段和校验规则纳入三端偏好适配器的明确架构授权，保证现有外观配置继续有效，主题、字号、间距和语言独立保持。

5. 建立语言键完整性、占位参数一致性和英文回退验证；覆盖切换后的页面状态、消息状态、布局可读性及本地偏好恢复，完成三种语言的适用截图和 Architect 验收。


## 明确语言偏好架构

语言偏好为设备/宿主应用范围，跨账号保持、无云同步，独立于credential、账号SQLite、消息和Sync cursor。默认 en；只允许大小写精确的 en、zh-CN、ja-JP，不trim、不接受系统locale猜测或任意别名。缺失/非法/超长/存储不可用回退内存en，写失败诚实显示且不覆盖其他偏好或清除其他key。固定三端位置：Web仅新增 src/ui/language.ts 以原生 localStorage固定key plugworldim.language.v1读取/写入raw UTF-8 enum（最长5bytes），不改plugworldim.appearance.v1三字段；Desktop TypeScript native.ts持有language意图，desktop_capabilities.rs仅窄language_load/save字符串枚举校验及app_data/language.txt读写raw UTF-8（最多5bytes、无BOM/换行），appearance.json三项tuple原字节继续可读；Android Preferences.kt在既有MODE_PRIVATE appearance SharedPreferences只增String key language（最多5UTF-8bytes），保留theme/fontSize/density键和值。theme仅cold/warm；Web fontSize14/16/18/20、density compact/comfortable/spacious；Desktop/Android既有fontSize14..22、density0.8/1.0/1.2及默认cold/16/1继续有效。四标量语义各自独立，但Web/Desktop外观record仍三项，不合并为四字段记录。当前三字段appearance守卫不得提前放宽；只有I18N依赖独立接受+集成同步且任务active/review/done、client_supplement_phase: i18n_product才可实现语言adapter及对应窄源码guard。STATE/UI-REF和本规划不获得语言持久化产品许可。

语言资源是TS/Kotlin纯数据映射，跨端键/占位参数语义一致；已有native通知/tray显示文本由TypeScript应用选择后交现有native presentation，native不拥有翻译/业务决定。英文回退、固定入口/滚动列表、即时更新及本地恢复完整验收；不批准第三方i18n/state/network/runtime/ORM库。

## 效力、兼容、迁移及回滚

canonical§6/15/19/20/附录A落实决定，baseline当前hash与supplement谱系绑定旧accepted2ba864fc。ADR-0007原只增GUI/WEB→Gate的历史范围保留；新链在ADR12正式生效后追加取代直接边，既有GUI/Web/S1接受保持。旧ADR、PDF、checkpoint、FAIL、Recorder不可变。无contract/schema/ACK/security/后端职责变更；STATE只按现契约修真实路径，矛盾按架构流程阻止受影响实现，不发明rejection/成功语义。本规划无产品/数据迁移，未来语言存储以独立标量位置兼容旧appearance字节，无清库、云同步或全局格式迁移。

machine policy绑定依赖和未来窄授权，guard真正解析queue/status/依赖及done证据字段，S2 prerequisite function以隔离正负fixture测试；本次不对actual S2评估。CI classifier现ci改动full matrix保留，任务治理路径必需architecture/source_go/source_java；缺失/失败/异常skip不能接受。独立Reviewer必须读真实完成证据，字段PASS不是独立接受。生效前候选失败修复复审；生效后纠正需新批准/独立接受，不重写历史。

## 最小性与完成

单行政Task、三明确产品Task、直接标准库校验，无通用编排/抽象层/新库/未来产品。完成须clean committed candidate、fresh independent Reviewer与必要Architect、exact-head hosted required jobs、protected merge、actual-main audit和主仓库未知work保存安全同步；记录branch/SHA/证据/checkpoint后本控制任务才done。产品仍backlog，S2 OPEN；Recorder不是接受。


## 正式生效发现（2026-10-10）

上方Human-approved candidate / APPROVED_PENDING_FREEZE为候选时点历史；当前状态Human-approved，APPROVED。规划规范在candidate 8b52a56403a5a761a12d94e4fabf4f2cf82f63d0 / protectedPR31 actualmain 9f99cfda1cecfc85c0acf3ae8db979f622c97a02独立Review/精确hosted/actual-main/主仓库安全同步接受，spec/progress/evidence/LOOP1-CLIENT-SUPPLEMENT-PLAN-001/acceptance/acceptance.md提供完整原件。正文决定与canonical当前hash不变。三产品仍backlog、语言仅I18N正式phase可实施；S2 OPEN。本行政状态记录另待独立接受，不提前声称其未来SHA通过。
