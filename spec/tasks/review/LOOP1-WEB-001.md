---
task_id: LOOP1-WEB-001
title: Web complete memory-only Loop1 GUI
status: review
owner: /root/web_product_fix_b
stage: S2
gate: S2
---

# Goal

既有 Web Task 承载完整 Loop1 GUI：Login/session、Chat、Friends、AI Placeholder、Plugin capability/unavailable、Settings/Profile、双主题与本地字体/间距；React + TypeScript memory only，no SQLite/no offline history。遵守 CLIENT-UI-ARCH。

# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> `spec/architecture/frozen-architecture.md`，§2.3/§3/§6/§10 SRC-01 through SRC-07/§11/§19/§20。
- `spec/architecture/decisions/ADR-0005-client-technology-clarification.md`、`spec/architecture/decisions/ADR-0006-client-ui-architecture.md`、`spec/architecture/decisions/ADR-0007-client-mvp-task-planning.md`。
- `spec/governance/minimality.md`、`spec/governance/execution-boundaries.md`、`spec/governance/independent-review.md`、`spec/governance/technology-selection.md`。
- `spec/domain/messaging.md`、`spec/invariants/messaging.md`、`spec/domain/sync-plugin.md`、`spec/invariants/sync-plugin.md`、`contracts/websocket/`。
- `spec/architecture/decisions/client-ui/architecture.md`、`spec/architecture/decisions/client-ui/design-direction.md`、`spec/acceptance/client-gui.md`。

# Technology Authorization

已接受 canonical §6.1/§6.5 与 ADR-0005/0006 授权；本声明不选择新依赖，未明技术按 §2.3 停止受影响实现。Mobile Kotlin 等价契约行为，不强制 TS 复用；Desktop TypeScript application/Repository 与 existing Tauri SQLx boundary。
client_language: TypeScript
client_framework: React

# Dependencies

- LOOP1-CLIENT-GUI-001 (必须独立接受并 done).

- ADR-0007 本轮规划须独立 Review/精确 HEAD CI/集成 main 同步接受才可激活。依赖未满足保持 backlog；GUI/Web 在本轮 Human endpoint 之后，无本轮激活授权。

# Allowed Paths

- `clients/web/src/**`
- `clients/web/package.json`
- `clients/web/package-lock.json`
- `clients/web/tsconfig.json`
- `tests/clients/web/**`
- `spec/tasks/backlog/LOOP1-WEB-001.md`
- `spec/tasks/ready/LOOP1-WEB-001.md`
- `spec/tasks/active/LOOP1-WEB-001.md`
- `spec/tasks/review/LOOP1-WEB-001.md`
- `spec/tasks/done/LOOP1-WEB-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-WEB-001/**`
- `spec/progress/checkpoints/*loop1-web-001*.md`

- `spec/architecture/frozen-architecture.md`
- `spec/architecture/baseline.md`
- `spec/architecture/decisions/ADR-0011-web-appearance-storage.md`
- `ci/check_architecture.py`
- `tests/architecture/test_client_technology.py`
- `.github/workflows/ci.yml`
- `tests/ci/test_s0_boundary.py`

# Acceptance

spec/acceptance/client-gui.md 真实浏览器截图与 Architect 审查修复重拍批准；内存协议状态/发送重试、页面生命周期后不保证消息保留、无聊天持久化；refresh/logout/session-expired。独立 Review、exact-head hosted CI、protected integration/main sync。
适用 architecture/source/dependency guard 与实际职责/import/minimality Review 必需。Task allowed_paths 不授权新架构。

# Forbidden

不得聊天 DB/历史持久化/离线历史，AI/Plugin runtime/Marketplace/S4 renderer、新契约/API 或未授权 router/state/data 库；本地外观机制必须先有 §2.3 所需授权。

# Minimality

仅实现当前目标，用已有 Repository/规范协议/已冻结技术；不增加未来机制。激活前读实际源码，路径不足先显式收窄/补充 task scope，不借范围泛化。

# Verification

- Minimum baseline: python -B ci/check_architecture.py --scope all --json 与 `tools/verify_frozen_architecture.py`。
- `tools/verify-loop1-ctrl-002.ps1` -Mode Development；候选 clean Acceptance；独立 exact-head applicable hosted jobs。
- 激活时将新增实现的精确行为验证命令、运行环境、启用条件和负例写入本节；尚未运行的测试不计 PASS。

# Evidence

spec/progress/evidence/LOOP1-WEB-001/；本次仅规划，未生成产品验收；prospective Research Recorder 激活时独立运行。

# Handoff

Backlog 规格实例化 canonical 已批准规划 ID；GUI 是唯一新增产品 ID。S1 PASS/S2 OPEN；未实现、未验收、未同步产品；known good59dcf34e4538d2f35ccafde8104e860f8cf5cd7a。当前规划文本 /root 所有；不覆盖主仓库未知工作。具体 code paths 在激活时按责任与实际源码确认。

# Next Action

Human 已批准最小前置方案并继续；直接落实 ADR-0011/canonical/policy/guard/CI 前置候选，fresh independent Review、exact-head hosted CI、protected integration/actual-main验证/安全同步后才生效；随后重评 ready/active 产品。最新 endpoint 是 Web完整接受同步后S2 Gate前停止，不执行S2 Stage Gate。


## Authorized next-task readiness (2026-10-08)

Latest exact Human request: 执行下一个task. Canonical ADR-0007 order selects LOOP1-WEB-001 after GUI; GUI dependency is independently accepted/done at synchronized actual main 6a6e97e6b7d5e19d8607c6800877187e70b4bd36. Original accepted final-sync report/binding/receipt and prior current snapshot are byte-preserved at readiness-20261008. Prior no-Web/SEND-only endpoint statements are historical. No missing consent to select Web remains.

Execution Status: BLOCKED_BY_ARCHITECTURE; status backlog and unique backlog queue retained. Required Web appearance storage decision is absent; current Web/compatibility CI rejects every product file and needed workflow/guard controls are outside allowed_paths. Present authority, current guard and seven-path scope request are concrete in `spec/progress/evidence/LOOP1-WEB-001/readiness-20261008/proposal.md`. Proposed localStorage stores only theme/font/density; it is not approved or implemented. Do not broaden scope or activate until inputs satisfy the required decision/freeze/independent acceptance chain.

Minimum baseline in assigned managed root H:/.codex/worktrees/w/IM-platform: bundled Python -Xutf8 -B ci/check_architecture.py --scope all --json exit0/3141ms; -Xutf8 -B tools/verify_frozen_architecture.py exit0/187ms. Exact argv/exits/hash receipts: `spec/progress/evidence/LOOP1-WEB-001/readiness-20261008/baseline-result.json`. Canonical a6b1670/PDF546915 verified. Local readiness evidence is not Task/S2 acceptance. Web runtime/browser/screenshots/behavior/hosted product tests have not run. S1 PASS/S2 OPEN; only former occupation-blocked helper regression remains deferred at S2 Gate.

Sole writer /root owns only Task/current/new Web readiness evidence, assigned Git root exactly verified and branch task/LOOP1-WEB-001-readiness. Last known good main6a6e97e6b7d5e19d8607c6800877187e70b4bd36; main31 unknown status entries/781 files untouched. Readiness metadata commit/independent Review/applicable exact-head CI/synchronization remain separately pending, not Web product completion. Prospective_resume Recorder R-WEB-COORDINATOR-20261008 registers actual visible prompt; startup/direct read/delegated-read instrumentation gaps and read-only missing-path/glob errors are disclosed. No product, contract, canonical, workflow, guard, dependency, helper or trust writes.

Local recovery Development exits0 for unique Web/backlog. Initial authored diff check exits2 on Windows CRLF; fixed authored outputs to LF, preserved original failed command and archived accepted GUI originals byte-exact in accepted-gui-originals.zip with original-bindings.json. Corrected diff/architecture all exits0; local-validation.json preserves real command outcomes. No verifier or acceptance assertion weakened. Readiness candidate requires fresh independent Review/hosted acceptance before its separate metadata synchronization; no Web product acceptance.

## Human-requested pause (2026-10-08)

Execution Status: PAUSED_BY_HUMAN. Human approved the exact minimal seven-path/localStorage prerequisite, then explicitly paused before implementation. Fresh e35c425 readiness metadata Review PASS is sealed; no prerequisite/product/hosted acceptance is claimed. Resume on 继续 from the saved state without re-auditing repository changes and without asking again for the same approval. Exact approval, released leases, evidence, uncommitted pause-write ownership and next action: `spec/progress/evidence/LOOP1-WEB-001/pause-20261008.md`. This newest pause/approval record supersedes the earlier missing-consent Next Action and not-approved wording; Task remains backlog until independently accepted prerequisite inputs are satisfied.

## Continued approved prerequisite (2026-10-09)

Execution Status: APPROVED_PENDING_FREEZE
web_verification_phase: appearance_prerequisite

Human精确答复“批准最小前置方案并继续”授权上述七额外路径与localStorage三标量；2026-10-09明确“继续”，恢复暂停点，无重复仓库改动审查。最新Human要求“你的任务截止到s2gate前，不对gate进行任何操作”：Web完整接受/同步后停止于S2 Stage Gate前；保留必要CI aggregate gate，不选择/执行Stage Gate或deferred helper regression。

本记录明确supersede此前not-approved/BLOCKED_BY_ARCHITECTURE/PAUSED_BY_HUMAN当前执行措辞；原readiness proposal和pause-20261008.md历史原件保持不变。Task仍唯一backlog，前置authority freeze须fresh Review/精确hosted/受保护集成/actual-main/安全main同步后生效才可ready/active。GUI done和ADR-0007输入已接受；不实现Web产品。

前置源/测试责任仅七paths与原tests/clients/web、Task/current/Web evidence；无ci/classify.py或check_gate.py改动。精确决策/批准/冻结说明见freeze-20261009。本轮sole writer与verification lease为/root/web_freeze_impl，assigned root严格匹配H:/.codex/worktrees/w/IM-platform，branch task/LOOP1-WEB-001-readiness；保留/root暂停写及immutable原件，main未知31entries/781files不读取/改写。last known good6a6e97e6b7d5e19d8607c6800877187e70b4bd36。

前置minimum baseline bundled Python -Xutf8 -B ci/check_architecture.py --scope all --json和tools/verify_frozen_architecture.py真实exit0。前置后续必需：architecture all/frozen；unittest discover tests/architecture、tests/ci、tests/clients/web；tests/clients/web/verify.py（只报告严格PREREQUISITE_SKELETON_ONLY）；Recovery Development/clean candidate Acceptance；diff/scope/hash checks。产品phase必需入口同verify.py执行locked npm ci/build + node tests/clients/web/behavior.mjs + appearance.mjs + clients source guard；缺输入/失败不可fallback。Webruntime/截图/Architect Approval尚未运行。候选commit/sync/hosted未完成，本地结果仅local evidence。

Research R-WEB-FREEZE-IMPL-20261009 prospective_resume独立implementation run；公开pre-Recorder只读startup gaps、首次注册关联future run失败与一次并发event锁冲突，原eventstream不改。无Task/S2 PASS宣称。

Local candidate verification: architecture all/frozen真实exit0；architecture56、CI34（4既有Windows真实symlink权限skip）、Web8负例controls exit0；Web入口exit0仅PREREQUISITE_SKELETON_ONLY，无产品build/behavior。Recovery Development initial exit1由current Verification格式三字段缺失导致，已修metadata，原FAIL保留；diff-check真实exit0。完整真实argv/exit/时长/output SHA在freeze-20261009/local-verification.json，后续clean committedAcceptance仍待运行，独立Review/hosted/main sync仍pending。

Recovery Development metadata修复定向重跑exit0/12875ms。本地最小checks已完成；clean候选branch/SHA/尚未sync与sealedRecorder由私有freeze-implementation/report.md记录供fresh Review，不是独立接受。前置尚未生效，Task仍backlog/S2 OPEN，latest endpoint S2 Gate前。

## Independent Review FAIL repaired candidate (2026-10-09)

原944b9bf独立Review FAIL：clean committed产品删除与first branch push before=zero绕过前置；immutable原件见fix-20261009-a/independent-fail-originals.zip及original-bindings.json。fresh Fix /root/web_freeze_fix_a只修verify.py+14真实Git/阶段controls，增加可信HEAD相关full-history，无关branches不扫、历史Markdown-only非产品、当前仍exact skeleton；shallow/graft failclosed，Git替换对象不影响真实历史。Web/compat workflow fetch-depth0已有，其他authority/guard/CI/Gate不变。

Local architecture all/frozen exit0、architecture56/CI34/Web14 tests exit0，4既有Windows真实symlink权限skip公开；actual Web入口仅PREREQUISITE_SKELETON_ONLY，无产品行为接受。Recovery Development/clean committed Acceptance、最终branch/SHA/diff/Recorder由私有freeze-fix-20261009-a/report.md封存，精确argv/exit/ms/hash见fix-20261009-a/local-verification.json。last good6a6e97e；main sync PENDING，no main write。所有新uncommitted fix scope归fresh Fix唯一lease；clean后释放待NEW independent Review，Fix不得自行接受。Task仍backlog/APPROVED_PENDING_FREEZE，S2 OPEN，不选Stage Gate。

Recovery Development本fix真实exit0/7953.0ms，仅local非接受验证；source/control修复待clean commit后由新独立Reviewer审查，最终clean Recovery Acceptance结果与SHA在私有report封存。

Immutable FAIL原件以ZIP保持entry原字节与original-bindings.json哈希：原negative-zero.log含CRCRLF，直接复制导致cached diff-check exit1；序列控制错误随后产生1d832e5，未amend，失败Recorder保留。新纠正commit仅封装task-owned复制证据与metadata，原review原件不动，源代码修复不变。

## Product activated after accepted prerequisite (2026-10-09)

Execution Status: IMPLEMENTING
web_verification_phase: product

This current record supersedes all historical pending/paused/no-Web endpoint wording above. GUI dependency done, accepted ADR-0007, accepted prerequisite e15f43f9 / protected PR28 actual main d4bb8200e7f5410d101a27ad58f8abb5eaa80f8f / independently audited exact-head hosted candidate and actual-main / safe main synchronization satisfy inputs. Immutable receipts and independent reports are byte-bound in product-20261009/accepted-freeze-originals.zip. Transition backlog -> ready -> active is dependency-satisfied in this activation; unique queue remains active. Seven extra prerequisite paths are not product write scope. No S2 Stage Gate work; full accepted/synced Web then stop.

Concrete product responsibilities: application auth/HTTP/WSS orchestration and memory Repository in clients/web/src/application; independent Web visual Shell/pages and fixed appearance adapter in src/ui; reuse only approved shared protocol/model leaves, no native Repository. React18.3.1/react-dom18.3.1/TypeScript5.9.3 and corresponding type bindings are canonical §6.1 policy packages, same accepted Desktop family; no new runtime/router/state/data/network library.

Real browser entry: built index.html served from controlled same-origin HTTPS fixture at loopback, WSS /ws; installed Microsoft Edge via bundled Playwright validation tooling. Runtime/version/fixture/build provenance recorded by screenshot manifest, no production dependency. 1280x900 and narrow viewport; Cold AI/Warm Creative, font14/20, compact/spacious. Screens: Login idle/loading/error/refresh/logout/expired; Chat empty/SENDING/SENT/FAILED/retry/disconnect/reconnect; Friends loading/empty/error/search/add success; Profile loading/error/success; AI construction and Plugin unavailable; Settings themes and independent preference extremes. Only controlled fixture identities; original unchanged screenshots under product-20261009/screens. Candidate commit SHA, source/build hash, exact steps and PNG SHA bind the set. Screenshot approval is outstanding.

Exact verification: python -Xutf8 -B tests/clients/web/verify.py requires locked npm ci, actual TypeScript build and node tests/clients/web/behavior.mjs plus appearance.mjs; architecture all/frozen; unittest tests/clients/web; tools/verify-loop1-ctrl-002.ps1 Development then clean candidate Acceptance; real browser harness tests/clients/web/browser.mjs with installed Edge and controlled HTTPS fixture. Negative coverage includes malformed wire/auth/session identity, late account callbacks, request retry identity/SENT terminal, sequence gaps/realtime duplicates, failed pagination, no business persistence and preference validation/unavailable storage. No product fallback or skip.

Sole writer/verification /root/web_product_impl; assigned managed root verified exact, branch task/LOOP1-WEB-001-product; last good synchronized main d4bb820. Product uncommitted files belong only to this writer; main unknown work untouched. Fresh Architect/implementation independent Review, exact-head hosted CI, protected integration/actual-main and safe sync remain required. Recorder R-WEB-PRODUCT-IMPL-20261009 prospective_resume captures product; incomplete pre-Recorder direct startup declared. Next: implement approved full Web, local behavior and genuine browser matrix, clean committed candidate for root to delegate Architect and independent implementation Review.

## Latest product checkpoint: required Edge plugin runtime blocked

Execution Status: BLOCKED_EXTERNAL_ACCESS

User now explicitly requires validation using the Edge plugin. Root's actual CUA getState attempts yielded trusted Node/kernel exit1 and helper_unknown_error setup refresh had errors, including after successful reset; no Edge surface was available. This genuine platform-runtime blocker prevents required plugin QA and final real screenshot approval. Existing Playwright Edge failure-run screenshots do not fulfill it. Product source candidate c785ef39bb1e66c90587a3288ce819584e05fcfc is frozen and real artifact/long-lived controlled fixture is bound in product-20261009/edge-plugin-server-binding.json; root holds browser verification lease. This state supersedes the earlier IMPLEMENTING execution label, not the active queue.

Full source/scope/local checks and final candidate SHA are sealed by private product-implementation/report.md and public local-verification-final.json after final clean commit. Product remains unaccepted; no done/Architect Approval/independent Review/hosted/new PR/main synchronization. Last good main d4bb820; all product changes are this implementation's owned scope; main unknown work untouched. Immutable failed run bytes at failed-browser-runs-originals.zip; exact failure provenance/next action browser-blocker.md. Recorder run has explicitly pending long-lived fixture command and incomplete prior startup; no fake trace completion.

Next: restore Edge-plugin runtime then root uses original https://127.0.0.1:52497 fixture to complete genuine Edge-plugin matrix, Architect/fresh Review/exact CI/integration/main sync. Final endpoint remains Web fully accepted/synchronized before S2 Gate; no Stage Gate/helper regression.

Fixture lifecycle correction: root explicitly authorized cleanup; exact-owned PID32808 stopped with corrected stop exit0 and original long-run exit1, Recorder command_finished preserved. Service is STOPPED, old URL is historical. Restart recipe and source/build binding: product-20261009/edge-plugin-server-stopped.json. No detached replacement, no user browser process or OS trust changed. Root original CUA failures and exact Human prompt are byte-preserved in root-edge-plugin-originals.zip/hash bindings; no auto-approval rejection and no tab/HTTPS interstitial ever observed.

## Latest Human cancellation of Edge validation

Execution Status: IN_PROGRESS

Human exact reply“失败那就不验证edge”撤销新增Edge/插件验证要求，supersede临时BLOCKED_EXTERNAL_ACCESS；保留原真实浏览器截图/Architect/独立Review/CI/integration/main sync链，改用validation-only Chromium，不继续Edge。原阻塞/失败原件immutable保留。旧fixture已按显式授权真实结束，无新detached服务；重新运行不同浏览器时绑定新的精确source/build/URL。所有产品与Task仍未独立接受，S1 PASS/S2 OPEN，完成Web后Gate前停止。Next: complete latest-source localchecks and genuine Chromium matrix, clean source-mapped screenshots candidate for root Architect and fresh implementationReview.

## Product candidate for independent Architect and implementation Review

Execution Status: REVIEW_PENDING

Full approved memory-only Web Shell/Login/session/Chat/Friends/AI-placeholder/Plugin-unavailable/Settings/Profile implemented; only fixed three-field appearance persistence. Original public HTTP friend/search/profile/auth and canonical shared WSS/Sync wire adapters, pure memory Repository, retry identity/SENT terminal/window gaps and account isolation. No initial history backfill: first authority seq establishes this page realtime window; earlier late frames expand it and expose gaps; after checkpoint denotes only gap-free prefix in this window, never global contiguous_seq or old history materialization. No timestamp filtering.

Source c785ef39bb1e66c90587a3288ce819584e05fcfc and exact actual build bytes bound by product-20261009/build-provenance.json. Final follow-up changes only QA capture wait/evidence/recovery metadata; reviewer must verify actual source tree equality, not infer from SHA labels. Genuine non-Edge Chromium151.0.7922.34/locked Playwright captured38 original PNGs with manifest/protocol-proof under product-20261009/screens/chromium-b; delayed color-transition captures superseded, original bytes preserved. User canceled Edge/plugin QA; its failures stay historical, current blocker removed. ControlledHTTPS/WSS fixtures only, no real credentials/system trust change. Screenshot self-check/test success is not Architect Approval.

Verification: strict tests/clients/web/verify.py actual locked npm ci/build/behavior/appearance/source checks; architecture all/frozen;14 Web phase controls; Recovery Development and clean committed Acceptance; diff/scope/provenance. Exact observed argv/exits/ms/outputhashes in local-verification-latest.json and sealed private report. Initial Evidence-format FAILs archived and corrected without checker edits. No selfReview/Architect approval/hosted/product main sync/done. Last accepted synchronized main d4bb820; task-owned branch task/LOOP1-WEB-001-product, final SHA and lease release private report. All screenshots/hash originals and known failures immutable.

Next exact action: root delegates fresh independent Architect Review/Approval of latest38 screenshots and full candidate; repair/newshots onFAIL then fresh implementation Review/exact-head hosted CI/protected integration/actual-main/safe sync. Full accepted/synced Web thenSTOP before S2 Gate, no Gate/helper actions. Sole writer/verification lease releases only after clean candidate/local acceptance and Recorder sealing.

## Final source strict-scalar revision and latest screenshot set

Latest product source 2aa37ad5b3b19cf1f50c03aa6e1029beb867431b fixes ADR-required strict theme/density string validation (reject custom toString objects), with targeted negative tests; no broader storage/interface/visual behavior. New exact-source actual build and38 genuine Chromium screenshots re-captured at product-20261009/screens/chromium-c/manifest.json. This supersedes earlier source/set claims without changing their immutable originals. Latest tree/hash binding product-source-binding.json, actual full build provenance build-provenance.json. Updated full applicable local checks and clean committed Recovery Acceptance are sealed in private final report; current Task remains review pending genuine Architect/fresh independent implementationReview/hosted/integration/actual-main/safe sync. User canceled Edge QA, S2 endpoint unchanged.

## Fresh Architect FAIL repair (2026-10-09)

Execution Status: REPAIRING_AFTER_ARCHITECT_FAIL

Latest Human directs Cold to accepted Desktop theme. Fresh Fix aligns actual light-blue/white-glass/deep-blue color hierarchy, keeps independent font/density and Web UI. Bounded Friends input/action CSS reserves readable idle/busy labels. Genuine Chromium matrix now adds both themes560x90020px/spacious Chat sending/sent/input and all host nav, Friends search/busy/error. Original Architect FAIL and all previous screenshot bytes immutable at product-fix-20261009-a; no Desktop/authority/contract/dependency changes. Local checks/new bound screenshots/clean candidate pending; new fresh Architect Approval and independent implementationReview/hosted/integration/main sync required. Sole lease /root/web_product_fix_a; accepted main d4bb820 remains lastgood. Edge canceled, Web endpoint before S2 Gate unchanged.

Evidence path correction: first repair reused prior prerequisite fix directory and overwrote original-bindings.json; this commit restores exact previous9d7 bytes and moves new Architect copies to distinct product-fix-20261009-a. Erroneous c357 commit retained, no amend; original source artifacts unchanged.

Repair local matrix: genuine Chromium48 new originals exit0; both themes narrow20/spacious Chat SENDING/SENT/input, six navigation targets click-reachable, Friends idle/busy/error. Fixture/browser really closed by harness finally. Source bd0838a tree/build/file bindings preserved; original prereq fix directory exact9d7 restored. Full fresh source checks and clean Acceptance receipts sealed in product-fix-a; no approval by this Fix. Next new Architect/new implementationReview; lastgood main d4bb820, sync pending, S2 Gate untouched.

Latest Human requests unified top-left Logo. Web now copies accepted Desktop logo.png byte-exact under allowed Web src and builds local asset, replaces command-symbol mark with IM+ / PLUGWORLDIM graphic and wordmark;44px image/6px gap/34px wordmark/9px caption follow Desktop. No native hooks/components/dependencies; new source full screenshot matrix required, original48 pre-logo images retained. First full-check Development exited1 because receipt was written only after verifier; receipt now durable, original failure/logs retained and fresh checks follow.

Repair local matrix: genuine Chromium48 new originals exit0; both themes narrow20/spacious Chat SENDING/SENT/input, six navigation targets click-reachable, Friends idle/busy/error. Fixture/browser really closed by harness finally. Source bd0838a tree/build/file bindings preserved; original prereq fix directory exact9d7 restored. Full fresh source checks and clean Acceptance receipts sealed in product-fix-a; no approval by this Fix. Next new Architect/new implementationReview; lastgood main d4bb820, sync pending, S2 Gate untouched.

## Final fresh repair candidate

Execution Status: REVIEW_PENDING

Final source bc21106 includes Desktop-aligned Cold, readable Friends idle/busy action and exact Desktop Logo. Latest48 genuine Chromium original set screens/chromium-b replaces all earlier pre-Logo sets for approval; build-provenance-latest verifies exact source/stage/current file bytes, original Desktop Logo bytes and final candidate product-tree equality. Actual full source verifier/architecture all/frozen/14Web controls/diff exit0; receipt-order Recovery Development failure retained then targeted recheck with existing durable receipts. Prior prerequisite directory exactly9d7 byte-restored at bd0838, no netdiff or other original evidence change. No fixtures alive, Edge canceled. Fix local readiness only, Architect and implementationReview/hosted/main sync pending. Sole lease /root/web_product_fix_a released only at final seal; main d4bb820 unchanged; S2 Gate untouched.

## Latest independent Architect B FAIL evidence repair (2026-10-09)

Execution Status: REVIEW_PENDING; queue remains review. This supersedes earlier repair-ready Next Action wording. Architect B observed Cold Desktop alignment and unified Logo met, but withheld Approval: Warm narrow new send was still SENDING because older Cold SENT satisfied generic wait. Immutable report/seal and original hashes archived in product-fix-20261009-b. Fresh Fix only changes tests/clients/web/browser.mjs: exact unique new message article, fixture request/conversation/expected seq binding, same-article SENDING and not SENT, Warm older-SENT negative control, same-article SENT plus expected seq before capture. Product clients/web/shared trees unchanged from bc2110662e1de4a24fd3d76271f0cdbe992754a6; Desktop logo byteequal remains. No business/authority/contract/guard/workflow/runtime/dependency edits.

Actual Chromium151 full48 new original screenshots completed exit0, same controlled fixture and existing approved test-only tooling; all own browser/fixture processes genuinely closed. Bindings/proof/build provenance at product-fix-20261009-b; actual command/exit/timing/hash receipts in local-verification.json. Fresh independent Architect and implementation Review still required; no Fix approval, done/hosted/push/PR/integration/main sync. Lastgood accepted main d4bb8200e7f5410d101a27ad58f8abb5eaa80f8f. Sole lease /root/web_product_fix_b until private report/seal release. Edge canceled; full Web accepted/synced then stop BEFORE S2 Stage Gate, no Gate/helper work.

Fresh B local strict locked Web/build/behavior/appearance/source, all architecture/frozen, Web14 controls, Recovery Development and both diff checks exit0 in local-verification.json. Private verification path typo build/clients/.../logo.png failed once; actual build/logo.png correction only private helper; Recorder original exit1 retained, new public screenshots compared byteexact on rerun. No product change. Final clean candidate Recovery Acceptance and SHA/lease release sealed privately product-fix-b/report.md; no independent Task PASS.
