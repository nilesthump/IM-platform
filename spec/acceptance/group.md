# 建群、成员添加与三端群聊产品验收

从属于canonical §4.3/§5/§6.7/§15/§19/§20/附录A、ADR-0013及既有client-gui规则。本轮仅规划：LOOP1-GROUP-001 backlog，产品验收未执行。公共wire、数据库和golden authority只在contracts/；未来先独立冻结契约再实现。

## 必需场景和证据

| ID | 场景 | 判定及原始证据 |
| --- | --- | --- |
| G01 | A-B为好友，A选B建群；B-C为好友，A-C非好友，B从本人好友加C | 真实好友/成员DB快照与请求；单GROUP包含A/B/C。证明B非OWNER仍可加C，A-C非好友没有被悄悄建立；三用户都获得同一群会话并互发，senderId与名称/账号可辨认。 |
| G02 | 非成员/失效Session加人、非好友、混合合法非法目标、DIRECT当GROUP、伪造actor | 经真实TLS入口拒绝，错误状态/码与canonical一致；零新增成员/群/成功receipt/Sync/Outbox，查询与消息同样无越权。 |
| G03 | 相同创建/加人ID重放、同key异目标、目标重复/顺序变化、已有成员 | 同规范集合重放原始结果；异内容明确冲突；成员/逻辑事件唯一，已有成员不重复产生变更，但仍校验操作者好友资格；操作者自身目标按冻结契约拒绝。 |
| G04 | 并发相同key建群/加人、不同request/操作者重叠加人 | 并发屏障+真实PG验证一个GROUP/成员/结果；不同操作全部合法则成功并收敛，成员唯一、仅真实变化有事件，无不合法中间快照。 |
| G05 | 事务各写点受控失败、提交失败与未知commit | GROUP/成员/receipt/Sync/Outbox同事务；确定回滚零新效果。未知结果诚实未确认，重试查询原结果；故障/清理异常不吞根因、不假成功。 |
| G06 | 首次未提交与已提交后响应丢失分别重试 | 保留原request/目标；前者首次真正提交，后者返回原conversation/operation结果，无第二群/重复成员/事件。UI真实未确认/重试到成功，DB与响应捕获绑定同fixture，不以mock证明持久化。 |
| G07 | 成员各自多端在线，元数据事件重复/乱序，NATS漏通知/断线 | 全部受影响用户含新成员，User Sync持久cursor→授权快照→会话/成员展示更新；不同会话隔离，无需发送消息才发现群。重连/持续分页最终一致。 |
| G08 | 群消息正常/重试/ACK丢失/乱序/离线补偿 | 复用现发送成员鉴权/seq/ACK/Outbox/Sync；单logical message+Outbox，同ID收敛，SENT不退、seq无gap；三人群内非好友仍识别sender。Desktop/Mobile账号SQLite重启/全新受控DB补偿；Web只当前页面在线窗口，不新增离线历史或存储。 |
| G09 | 三端真实入口/i18n/视觉 | 逐端从好友页建群、群页从本人好友加人、会话列表进入群、成员/发言者展示、加载/空/拒绝/失败/未确认重试；en/zh-CN/ja-JP键/参数/回退及即时切换状态保持；实际截图与Architect批准。 |

## 运行与独立接受

契约首切片必须包括contracts/机器schema/正负fixture/0002迁移、现有独立runner与迁移回归的必要适配，以及现有shared必需contract步骤中的群verifier/正负suite调用。按GROUP Task Verification在可丢弃PG且DB_TEST_ENABLE=1下真实验证空库/0001→0002/重复应用/回退/旧fixture兼容，保留0001原字节、历史checksum、锁及真实失败行为；核对精确hosted原始job/step证明新群验证确实执行且非零传播，不能只凭路径选择或旧验证绿。无新workflow/job/framework，也不得由业务或verifier绕过runner执行DDL。上述契约切片在clean commit上完成fresh常规Review、different fresh错误专项、适用exact-head CI、受保护集成/actual-main/主目录安全同步，记录精确contract SHA，才实现产品；不能以本规划接受等同新增wire已冻结。后续产品候选也重复完整闭环。

真实Go profile/PostgreSQL/NATS/TLS入口和受控非私人fixture；Web真实浏览器、Desktop同候选构建并安装的Windows Tauri、Mobile真实独占Android Studio emulator。契约fixture/host/mock是补充，不代替入口证据。记录环境/真实serial、命令argv/退出码/耗时/DB断言、请求/操作/用户/会话关联、原始响应/故障时序及资源清理；skip/缺环境为未执行，不计PASS。

每端真实截图至少：好友选择建群、成功群列表/群消息、B加C、sender身份、拒绝/失败/未确认重试；截图manifest绑定Task、final产品SHA/build/runtime/fixture/状态/尺寸/theme/font/density/locale/原始截图文件及SHA-256和复现步骤。两主题及受影响布局的字号密度极值保持可读。Architect独立绑定同候选/原始截图Review→修复重拍→Approval；源码或视觉影响证据即重拍重审。截图不能证明事务/权限/ACK。

全部G01..G09、契约兼容、服务/客户端职责导入、minimality、真实构建/入口/截图/Architect、最终SHA两项独立审查、实际required hosted jobs、protected integration、actual-main验证和H:/IM-platform安全同步均满足才GROUP done。独立证据与Task Completion Metadata可核对；本地或Recorder不是接受，GROUP单项PASS不是Stage PASS。

## S2 Gate

链：WEB→STATE→UI-REF→I18N→LOOP1-GROUP-001→S2 Gate。GROUP同时依赖LOOP1-GROUP-PLAN-001正式接受并安全同步。保留SQLITE/UI-ARCH/SEND/SYNC/GUI/WEB、原三补充任务及旧行为/Architect/deferred-helper适用门禁；缺GROUP完成或接受/main sync任一项，S2必须阻止。语言激活仍是LOOP1-CLIENT-I18N-001/i18n_product，与GROUP任务/phase无关。本轮不执行实际S2评估；Gate负例只在隔离fixture。
