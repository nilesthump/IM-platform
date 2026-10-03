# 公开 Sync 传输前置实现交接

状态：REVIEW_READY_LOCAL_ONLY；非 Task PASS、非 SYNC/S2 PASS。前置 accepted/main sync PENDING，Go 产品实施尚未获同意。

分支 task/LOOP1-SYNC-001；已分配且精确验证 Git root H:/.codex/worktrees/sync-resume/IM-platform。基线 accepted main a0304fcc7be18b87f5986d014849d6b48b96a071；前置输入 blocker bc1bebb31fac6f0256db998746187005c9028606。候选提交 SHA 由 clean commit handoff 提供，避免把自引用SHA写入同一commit。review范围 acceptedbase..candidate（含已授权原恢复与sealed research输入）。主仓库仍 acceptedbase/同步PENDING，不声明完成。

## 实际交付

仅HTTPS POST两操作、现有四shape/Auth/errors外部refs、用户opaque/accountcursor、每请求Session/member权限、bounded100分页、严格关联、空页/hasMore/no-progress/大整数语义。现有Sync shapes、WSS/ACK/DB/producer payload保持原样。ADR0008中文与canonical§11.5/manifest谱系；当前任务唯一review，SYNC唯一backlog。共享契约现有pwsh CI step新增两条实际验证。新依赖/服务/product行数=0。

canonical SHA256457c405b79ca068af2b398b9fbe49859810c455359b01dbfdb2d4c6d72a9d966；上一accepted16e9c7b4，PDF546915原字节不变。

## 校验与实际失败

完整记录在 research/runs/R-SYNC-TRANSPORT-20261003/events.jsonl 与各command redacted stdout/stderr，verification-history.md列实际argv/exit/elapsed/hash。final local：frozen integrity PASS；architecture all PASS无violations；53architecture testsPASS；新4组Sync binding testsPASS（11documentmutations+page/schema/correlation/auth-status/largeinteger/gap/isolation负例）；official OAI structural lint/ref checksPASS；HTTP9operations/6positive/21negative/15mutationsPASS；WSS18vectors/44mutationsPASS；SyncPlugin79vectors/16mutationsPASS。

最初大整数testFAIL因既有offline oracle默认sys.maxsize，与schema无max冲突；只在新请求guard对limit/afterSeq先精确验证、给旧oracle提供受控copy，以保留公开shape。原oracle/shape不改。工具/quoting/encoding和首个CI定位/lineending失误在Recorder instrumentation_warning如实保留并已修复。read-only启动gap为prospective_resume；前继额外UI/ADR输入在canonical初始设计后完整核对，无冲突，顺序例外公开。没有假Go/native/TLS acceptance。

## 权属与独立性

本实施者 /root/sync_transport_design sole writer；不得接受自己candidate。bc1bebb前继 implementation/implementation-research 已commit输入原字节不改。Coordinator明确授权把 root原untracked research sealed20eventBLOCKED/validatePASS纳入候选，原stream不修改、不重新归属。自己的Recorder只在本前置目录。既有done/PDF/旧FAIL/其他用户/agent main work无触碰。

## 下一步与同意边界

Coordinator派fresh independent Review of clean candidate；FAIL由新Fix再新Review。随后exactcandidatefull13job hosted CI/protected merge；实际main review/精确CI与主仓库同步核验并记录SHA。前置仅之后done；S2OPEN、SYNCbacklog保留runtime blocker。然后向Human展示go-implementation-proposal.md并取得同意；之前严禁任何Go/client/UI产品写入。该方案明确Core sync/Authmux、Gatewaygenericproxy无产品改、accountopaque响应投影、真正PostgreSQL稳定prefix并发与TLS验收、必要精确路径。SYNC最终接受同步后停止，GUI/Web不推进。

## Post-seal staging check

Own authored non-Recorder docs normalized to Git LF; final staged diff check excluding only two immutable raw Recorder research directories PASS. Unrestricted staged diff check reports CRLF/raw unified-patch context whitespace and a blank output EOF within immutable archived Recorder artifacts; this is exposed, not repaired by editing evidence. No product/authority whitespace failure remains. Own Recorder sealed45events/localPASS/validatePASS before commit; final command history reflects all recorded checks. Main synchronization still PENDING.
