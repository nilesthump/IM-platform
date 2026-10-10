# 精确候选与实际主线托管接受

独立 Reviewer /root/s2_plan_review_b（未实施/修复）已接受：candidate 8b52a56403a5a761a12d94e4fabf4f2cf82f63d0，push38032373658及PR38032400125，各14 selected/124 steps；全部必需job SUCCESS，无failed steps。PR默认检出50ed4c44c0248a286ffee15245da421cd4b4e383，父提交b4/8b52且whole tree相同；显式refs为candidate，不把合成SHA误称candidate。

普通受保护PR31合入 actual main 9f99cfda1cecfc85c0acf3ae8db979f622c97a02，自身push38033632164独立接受，14 selected/no failure，所有checkout精确actualmain。Linux真实symlink负例在三run执行OK；平台条件false的步骤/Windows-only测试skip与workflow相符，不将skip当PASS。

原始API/全部selected job logs/实际classifier与独立报告、seal、commands无损封存在originals.zip，哈希见original-bindings.json。候选Review fresh_context=true；后续hosted/actualmain同独立角色fresh_context=false，事实区分。CI aggregate gate不是S2 Stage Gate。

运行：[候选push](https://github.com/nilesthump/IM-platform/actions/runs/38032373658)、[PR](https://github.com/nilesthump/IM-platform/actions/runs/38032400125)、[actual-main](https://github.com/nilesthump/IM-platform/actions/runs/38033632164)。
