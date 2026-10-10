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

规划仅源码/既有接受审计；没有新的真实客户端/故障/语言/视觉验收。本地验证与独立候选接受另行记录。
