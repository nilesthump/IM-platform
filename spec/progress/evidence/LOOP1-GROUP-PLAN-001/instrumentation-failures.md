# 原始失败与记录限制

默认sandbox首次branch操作exit1：fatal: cannot lock ref 'refs/heads/task/LOOP1-GROUP-PLAN-001': Unable to create 'H:/IM-platform/.git/refs/heads/task/LOOP1-GROUP-PLAN-001.lock': Permission denied；Set-Content同次对assigned activeTask Access denied，无source写入。已获用户工作树常规分配授权，elevated同scope写入成功。

只读诊断：rg literal Windows '*.ts' path error123；两recovery JSON误带不存在external/目录；随后均按真实path读取，未写旧原件。

Recorder并发启动一次architecture unittest命令返回exit1：ERROR: event stream is locked; interrupted writer may require inspection。命令未实际启动，后续实际重跑88tests/one既有Windows skip通过，原事实保留。

R-GROUP-PLAN-IMPL-20261015 architectureall子进程输出捕获后，外层Python未设置UTF8，sys.stdout打印遇Unicode K，实际Recorder返回exit1：ERROR: 'gbk' codec can't encode character '\u212a' in position 123486: illegal multibyte sequence。此command_started没有command_finished，原子进程结果和完整stdout不存在于该Recorder原件，保持unavailable；不得从后续PASS倒填。旧run按真实记录失败finish resultFAIL；validate-run实际exit0只表结构，不校验成对command完整性，不可声称该trace完整。

所有旧events原字节/FAIL不改，durable recorder-snapshot是明确时点副本。新R-GROUP-PLAN-IMPL-RESUME-20261015 related旧run、parentCoordinator、prospective_resume/pre_recorder_work=true；所有外层Python -Xutf8，实际重跑architectureall/frozen/planningexit0。最终新runfinish/validate、clean Acceptance和sourcelease见外部implementation/final-receipt.json，不能用structuralPASS替代Task接受。早期直接read/准备/截断和pwsh中文失真等gap保持implementation-handoff披露。
