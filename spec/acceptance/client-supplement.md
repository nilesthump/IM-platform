# S2 客户端补充验收

从属于canonical§6.6/§15/§19/§20/附录A及Human-approved ADR12候选；正式生效依赖本规划独立接受/集成/主仓库同步。公共机器契约唯一contracts/。新任务均backlog/S2 OPEN。

## 实际基线与证据（起点 b4d271c）

| 能力 | 当前实际实现与证据 | 新任务必须补齐/验证 |
| --- | --- | --- |
| 重发/状态 | Desktop send.ts、Mobile SendViewModel.kt从Repository原row读身份/content；shared/Kotlin Repository.markFailed不倒退SENT、committedAck/realtime/Sync UPSERT。WEB repository.ts内存sameID/terminal、client.ts保留迟到ACK身份 | 既有单元/受控TLS向量不是三端真实A/B联合证据；逐端同一logical消息/单Outbox/真实FAILED再SENT |
| 服务端提交 | core/message.go已有message+seq+outbox事务、重复查询原messageId/seq/createdAt、content冲突拒绝；gateway10s HTTP timeout、core Commit(ctx)未知结果路径待逐项审计 | 首次未提交与已提交确认丢失必须受控区分；未知commit不伪成功，也不能把已提交事实伪造为无persist rejected |
| 排序 | shared Repository.messages与Mobile Repository.messages ORDER BY server_seq IS NULL,server_seq,local_id；Web snapshot排序bigint seq | 两种R1/R2真实渲染身份/seq/状态在ACK/realtime/Sync交叉后正确 |
| 持久恢复 | Desktop accountDatabase/SQLx与Android account SQLite、restore显示saved history；Sync从cursor0连续分页 | 同账号保留本地FAILED重启retry、全新该账号DB/初始cursor恢复完整历史+新request/seq，只处理受控fixture DB不删真实用户 |
| Web生命周期 | memory Repository、无initial history；baseline live window/held terminal crossing/ACK-only gap已regression接受 | A/B/顺序遵守同页面、已有在线window Sync；不能为测试新增历史DB/全量backfill |
| 好友 | Web login/refresh/add调用loadFriends，无User Sync；realtime按已知friends过滤。Desktop Workspace/Mobile WorkspaceViewModel bind/add调用Auth.friends；Sync userPage存metadata，idle仅updateList，未重新刷新friend/user名称；UserSync在bound/reconnect/open/delivery触发 | 补齐无消息亦能最终触发UserSync→consumer→好友/私聊/name UI链；三端添加、其他在线端、断线恢复/切账号 |
| 页面/组件 | Web/desktop src/ui/main.tsx入口含Shell/page/local state；Mobile MainActivity.kt挂载Workspace.kt，内含Auth/Chat/Friends/Settings组合；各端独立视觉 | 激活UIREF时以STATE接受树再次枚举实际entry/组件输入输出/state/import，行为视觉完整对照 |
| 显示/状态 | Web View.connection用中文“在线”且transmit判断它；native应用error/preview英语内嵌、Mobile ApiFailure.kind的“Session expired”也参与判定 | UIREF先稳定ID与display分离；I18N禁止translated strings进入业务条件 |
| 偏好 | Web appearance.ts v1 exact3keys；Desktop native.ts+desktop_capabilities appearance.json3tuple；Android Preferences appearance SharedPrefs3keys | 语言独立位置/标量保持theme/font/density，非法/不可用及三语言readability恢复 |

接受原件：`spec/progress/evidence/LOOP1-SYNC-001/acceptance/acceptance.md`（PR22 main2351a293；真实DesktopSQLx/GoTLS/PG，MobileAPI34契约fixture62 controls；不声称Mobile-to-Go）；`spec/progress/evidence/LOOP1-CLIENT-GUI-001/closure20261008/`（PR24 mainb14bf107、Windows43原图/真实native、AndroidAPI34、独立Review/CI）；`spec/progress/evidence/LOOP1-WEB-001/product-closure-20261009/acceptance-originals.zip`及original-bindings.json（PR29 maina1b154d，ArchitectE52 originals、语义/delta/hosted接受）。PR30只行政恢复，最新main b4d271c。缺口表表示当前源码观察，不撤销原范围接受，不声称未执行的新产品验收PASS。

## LOOP1-CLIENT-STATE-001 强制验收

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


故障注入仅受控fixture、真实Go profile/PostgreSQL/NATS/TLS入口及真实浏览器/已安装Windows Tauri/Android Studio emulator；test proxy/held-response拦截仅受控发送方confirmation，不改生产契约。A证明首次0消息/0Outbox；B证明提交唯一记录+接收方实际得到+发送方真实FAILED（确认路径受控丢失/延迟）+点击retry原消息SENT；持久化snapshot与request/conversation/sender/content、originalACK三元组、Outbox logical count及实际render bind同候选/fixture/scenario。自动Sync若先确认不能计作FAILED/retry证据；受控安排timing并同时记录Sync/实时路径恢复。重复publication不等于多个logicalOutbox。保存原始失败，不用mock截图证明持久化。

## LOOP1-CLIENT-UI-REF-001 强制验收

以任务一验收后的三端产品树为行为和视觉基线，规划并验收各端现有页面、组件和展示状态的职责拆分。

1. 根据实际源码拆分应用入口、Shell、导航、认证、会话列表、消息展示、输入区域、好友及设置等现有职责，明确入口挂载、组件输入输出、状态归属和导入方向。

2. 保持各端独立视觉实现及现有 Auth、Repository、Send、Sync 职责边界，共享现有协议、类型和适用展示语义。

3. 将组件展示文案、应用状态标识与业务判断建立清晰边界，为后续语言资源提取提供稳定接口。

4. 建立拆分前后的页面、入口、功能和测试覆盖对照表。完整回归现有客户端能力及任务一新增场景，验证状态保持、事件绑定、账号隔离、同步、重发、排序和外观设置的行为等价。

5. 完成各端构建、适用自动化测试、真实运行截图和 Architect 审查，以功能完整、行为等价和视觉基线保持作为验收结果。


对照表按端列actual entry/挂载、Shell/navigation、Auth/register/login/refresh/logout/expiry、conversation list/view/message/composer、Friends/search/add、AI占位/Plugin unavailable、Settings/Profile、appearance、OfflineHistory/Sync及Desktop通知/tray/shortcut；对应旧新文件、输入输出、状态归属、事件/订阅清理、import方向、测试/真实截图和批准。不为了拆分新增generic store/总线/framework。状态与文本边界必须包含Web“在线”业务判断及native error分类，协议/Repository state保持稳定ID。复用STATE已接受故障harness并完整回归，不重写其已接受原件。

## LOOP1-CLIENT-I18N-001 强制验收

依赖任务二完成，提取三端现有用户可见文案，建立英语、简体中文和日语的独立语言资源。

1. 统一语言标识 en、zh-CN、ja-JP，以及跨端文案语义和占位参数。Web/Desktop 使用 TypeScript 侧纯数据语言资源，Android 使用现有 Kotlin/Compose 技术栈下的等价资源映射。

2. 覆盖页面文本、按钮、输入提示、校验与错误提示、连接及同步状态、无障碍标签，以及已有系统通知和托盘文案。将状态逻辑使用的稳定标识与翻译后的显示文本分离。

3. Settings 增加固定入口“Language / 语言 / 言語”，使用固定顺序的滚动选择列表：
   English → 简体中文 → 日本語。
   选项名称保持各自语言，切换后即时更新当前界面，本地保存并恢复语言选择。

4. 将语言选择的本地持久化范围、存储位置、字段和校验规则纳入三端偏好适配器的明确架构授权，保证现有外观配置继续有效，主题、字号、间距和语言独立保持。

5. 建立语言键完整性、占位参数一致性和英文回退验证；覆盖切换后的页面状态、消息状态、布局可读性及本地偏好恢复，完成三种语言的适用截图和 Architect 验收。


语言偏好为设备/宿主应用范围，跨账号保持、无云同步，独立于credential、账号SQLite、消息和Sync cursor。默认 en；只允许大小写精确的 en、zh-CN、ja-JP，不trim、不接受系统locale猜测或任意别名。缺失/非法/超长/存储不可用回退内存en，写失败诚实显示且不覆盖其他偏好或清除其他key。固定三端位置：Web仅新增 src/ui/language.ts 以原生 localStorage固定key plugworldim.language.v1读取/写入raw UTF-8 enum（最长5bytes），不改plugworldim.appearance.v1三字段；Desktop TypeScript native.ts持有language意图，desktop_capabilities.rs仅窄language_load/save字符串枚举校验及app_data/language.txt读写raw UTF-8（最多5bytes、无BOM/换行），appearance.json三项tuple原字节继续可读；Android Preferences.kt在既有MODE_PRIVATE appearance SharedPreferences只增String key language（最多5UTF-8bytes），保留theme/fontSize/density键和值。theme仅cold/warm；Web fontSize14/16/18/20、density compact/comfortable/spacious；Desktop/Android既有fontSize14..22、density0.8/1.0/1.2及默认cold/16/1继续有效。四标量语义各自独立，但Web/Desktop外观record仍三项，不合并为四字段记录。当前三字段appearance守卫不得提前放宽；只有I18N依赖独立接受+集成同步且任务active/review/done、client_supplement_phase: i18n_product才可实现语言adapter及对应窄源码guard。STATE/UI-REF和本规划不获得语言持久化产品许可。

TS/Kotlin资源键set与每键占位参数set必须一致；未知locale/非法本地值回退en；缺locale键回退en并有negative测试，英文基础键缺失FAIL。输出文案不能修改wire/error code、用户消息/名称内容或request ID。每语言涵盖全部实际入口/加载空错/连接Sync/message状态/accessibility/已有系统通知tray；固定Language入口及三本名顺序滚动列表在三个语言下可达。即时切换不丢draft/selected/history/send状态或订阅，不重置其他偏好；重启本地恢复及invalid/unavailable用真实适配器验证。截图真实三端和三语言，必要窄viewport/字号密度极值保持可读、图文/参数不溢出，Architect独立绑定候选批准。

## 独立闭环与S2前置

沿用client-gui完整截图→Architect Review→修复重拍→Approval、fresh independent semantic Review、exact-head applicable hosted CI、protected integration/actual-main和safe H:/IM-platform同步。每新任务done必须在Task Completion Metadata写实际candidate/main SHA、PASS与独立review/hosted/main sync证据路径；Reviewer读证据内容与实际jobs/checkout/受保护合入/保存未知work，字段本身不提供接受。

顺序WEB→STATE→UI-REF→I18N→S2 Gate，前项独立接受/集成同步后才能激活后项；STATE另依赖本规划正式生效。Gate仍需旧SQLITE/UI-ARCH/SEND/SYNC/GUI/WEB和所有旧要求、三个新完成项及deferred helper适用验收。规划或单Task PASS不能S2 PASS。本次仅独立接受规划、三个backlog交付，不评估实际Stage Gate。
