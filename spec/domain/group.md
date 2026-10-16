# Group 领域规则

来源：canonical §4.3/§5/§6.7/§10/§11、Human-approved ADR-0013；本轮规划候选接受前不激活产品。这里定义业务语义，不定义wire/schema；机器公共权威仅contracts/。

| Rule ID | 规则 |
| --- | --- |
| GROUP-D-001 | 创建者从本人好友选择至少一名不同用户，自己自动加入一个GROUP。 |
| GROUP-D-002 | 任意有效成员可从其本人好友选人；好友资格只相对本次操作者校验。OWNER标签不授予额外加人权限。 |
| GROUP-D-003 | 当前Session、GROUP kind、有效成员及每目标好友资格由Core在事务中权威校验；整批合法才提交。目标规范化/去重，排除操作者；已有效成员无新增效果但仍校验本人好友资格。 |
| GROUP-D-004 | 创建身份(actor,create request)和加人身份(actor,conversation,add request)分隔操作类型，绑定规范目标集；同key同内容重放原结果，不同内容冲突。 |
| GROUP-D-005 | 群/新成员/持久操作结果/受影响用户Sync状态/Outbox原子提交；成功只在durable commit后。并发重叠最终成员唯一，仅实际变化产生逻辑事件。 |
| GROUP-D-006 | 所有当前有效成员含新成员的各端通过conversation.changed/membership.changed及授权快照取得会话与最小成员展示身份；非好友成员名称由群权限获取，不扩张用户搜索权限。 |
| GROUP-D-007 | 发送、seq、幂等、ACK、Outbox、分发/Sync沿用现有链；senderId映射真实群成员身份。新成员按现有成员鉴权可取群已提交消息，不增加join-seq过滤；Web保留memory/在线窗口边界。 |
| GROUP-D-008 | 未确认/超时不推定回滚或成功，原操作ID/目标可重试；真实失败可见，未知异常正常传播。 |
| GROUP-D-009 | 三端入口、新文案和无障碍使用既有i18n；不含管理/退群/移除/审批/邀请链接/二维码/陌生人入群/新群名功能。 |
