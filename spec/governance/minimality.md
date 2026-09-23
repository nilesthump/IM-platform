# Minimality Contract

Every additional abstraction must pay rent. This is a development and review rule subordinate to Frozen Architecture, approved ADRs, public contracts, invariants, acceptance criteria, and the current Task Spec. It creates no product requirement or authority to rewrite a contract.

Implement the smallest direct mechanism that satisfies current approved requirements, invariants, acceptance criteria, and observed implementation constraints. A new interface, layer, framework, dependency, option, database object, worker, service, compatibility layer, or extension point needs a present responsibility. Possible future reuse, future stages, elegance, and generic “best practice” are insufficient on their own.

When a less direct mechanism is needed, identify the current requirement or observed failure it serves, why the simpler path falls short, and the smallest added mechanism. Record measurements where performance or reliability motivates the change, and a removal or replacement condition if the mechanism is provisional. Do not use lines of code as a decision rule.

Necessary boundaries and abstractions remain valid: for example, a real transaction boundary, shared Go/Java observable contract checks, an existing plugin capability boundary, or required Outbox reliability. Prefer one direct path when only one behavior exists. Do not add a strategy/factory hierarchy for a hypothetical second implementation, compatibility for nonexistent versions, or Loop 2 infrastructure in Loop 1 without current evidence and the required architecture approval.

The Frozen Architecture already applies this judgment: Loop 2 goals do not expand Loop 1 implementation scope (chapter 1.3); Redis, Kafka, sharding, and automatic failover require fault or load evidence and an approved ADR (chapter 1.3); the simple conversation sequence row is allowed to be hot until load testing proves contention unacceptable (chapter 5); tasks do not grant architectural discretion, and agents stop at architecture conflicts (chapters 2 and 21). This document does not reinterpret those decisions or permanently ban a technology.

## Independent review

Alongside correctness, security, contracts, and acceptance, review added complexity against current responsibility. Inspect abstractions without current consumers; production code for future stages; new dependencies; strategy, factory, or framework layers for one current path; speculative compatibility or infrastructure; and production mechanisms whose removal would leave every approved acceptance criterion satisfied.

Ask: **If this code or abstraction were removed or simplified, would every currently approved acceptance criterion still pass?** If yes, request deletion or simplification, or a concrete current requirement and evidence justifying it. A finding must cite that requirement or evidence gap and the affected code. Personal style preference and a raw size or LOC threshold are not findings. Reviewers cannot change product requirements, public contracts, or Frozen Architecture; a conflict follows the approved architecture process.

Complexity delta (files, production/test lines, dependencies, public symbols, configuration, database objects, services) may help focus review. It is a signal, never an automatic score or FAIL.
