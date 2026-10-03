# 中文修订与旧 Review 修复说明

旧候选 22e82db 的独立 Review 为 FAIL：完整 BASE..HEAD diff 检查暴露 CRCRLF/尾随空白，且新 Human 要求中文文档。其语义/最小性审查未报告其他阻塞。failed-review1.zip 保留原报告、JSON 和 run 文件；解压哈希列于 raw-archive-manifest.json。既有提交未重写。

原始日志移至字节保持的 .log.gz；Human 请求/补充及 JSON 的原始字节保存在同名 .gz，可读副本使用 LF 并明确区分哈希；JSON 日志引用更新为 .gz。清单记录原始/压缩/规范化哈希。human-supplement.txt.gz 保存旧候选的原始字节；可读 LF 副本另追加本轮新 Human 原句。

初始只读环境默认 python 是 Python 2，baseline/Recorder 命令语法失败；改用已知 bundled Python 3 后 Go temp sandbox 拒绝。后续显式 Python 3 和授权执行重试。注册 prompt 第一次错误地以空 stdin 注册空哈希；该错误记录保留，另注册 CORRECTED prompt，真实 run 关联正确原句。Recorder 开始前读取不完整，capture_mode=prospective_resume。

本修订不改规范正文/hash、历史 PDF、公共契约、产品代码或根 Agent Recorder。任务保持 review，须重新独立 Review、精确 HEAD 托管 CI、集成与实际主仓库同步，不声明 Task/Stage PASS。

本轮本地检查：frozen integrity PASS；source all PASS/zero violations；53 architecture tests PASS；git diff --check BASE（含工作区）PASS；recovery Development PASS/24 tasks。精确命令、退出码、时长、原始输出哈希见 checks.json 与 check-*.log.gz。这些本地结果不构成验收。
