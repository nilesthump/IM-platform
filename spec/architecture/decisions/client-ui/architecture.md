# Client UI Architecture

Status: Human-approved direction; candidate pending fresh independent Review / exact-head hosted CI / integrated-main verification. Canonical v1.1 §6.5 and ADR-0006 govern this subordinate design document. No product implementation is authorized by this candidate alone.

## Product and information architecture

构界 IM+ / PlugWorldIM uses Adaptive Glass Workspace. The visual emphasis is 50% Future AI Communication, 30% Productivity Tool, 20% Developer Extensibility; these are design priorities, never feature or capacity claims.

| Primary destination | Responsibility | Boundary |
| --- | --- | --- |
| Chat | Conversation List, Conversation View, messages | Friend management belongs to Friends |
| Friends | User search, friend relationships, add friend | Server authority decides friendship/direct uniqueness |
| AI | Future entry, illustration, construction notice | Placeholder only; no AI chat, Agent, RAG, tool calling, API or fake data |
| Plugin | Installed Plugins, Plugin Status, Plugin Entry | Personal capability panel; no store, Marketplace or S2 installation/runtime |

Application Shell owns primary navigation, account context and destination selection. Only client-owned code may later add Settings/Profile after task authorization. Plugins cannot add primary destinations or control the Shell, theme brand or base UI semantics. Nested plugin entry remains inside the host-owned Plugin destination and requires available authorized capability; absent capability displays an honest unavailable state, never a fake installed inventory or working action.

## Data ownership and flow

UI renders view state and emits user intent. Screen state/hooks/ViewModel translate intent to existing Repository/protocol operations and expose loading/empty/error/auth-expired/connection/sync state. Repository owns materialized data and transactional convergence; protocol adapters own canonical HTTP/WSS serialization and transport behavior. UI must not open SQLite, advance cursors, fabricate ACK, write message state independently or decide membership/permissions. Backend ownership remains Core/Gateway/Plugin Host under §3 and SRC-01..07.

Desktop/Mobile send intent -> approved send orchestration -> persist SENDING through Repository -> transmit -> durable server ACK -> Repository UPSERT -> observed UI state. This task specifies direction and does not implement orchestration. Retry reuses request_id; FAILED means unconfirmed attempt; matching realtime/Sync may converge to SENT; SENT never regresses. Data/cursor updates are atomic, user cursor excludes messages, contiguous_seq never crosses a gap. Offline history is the account-scoped local view, followed by background Sync; switching account must stop old observations and display no previous-account data.

Web uses in-memory Repository state only; no chat database, persisted history, offline history or page-lifecycle durability promise. Offline/error views must describe actual connection state. Local appearance preferences contain no messages, tokens or business data and do not create chat persistence authority.

## Web

React + TypeScript for concise, efficient online communication. Shell/routing handles destination selection; screen/custom business components handle presentation; custom hooks/data layer connect Repository/protocol operations; state is useState/useReducer/Context/custom hooks. Local screen state stays local; Context carries only genuinely shared current responsibility. No speculative generic event bus/store/controller hierarchy.

Router is a responsibility, not authorization for a named third-party router. No Zustand/Redux/MobX, data framework or full business UI framework. Icons/accessibility/utilities may be considered only through dependency governance; the category alone does not approve a concrete library.

## Desktop

Tauri + React + TypeScript, independent UI for comfortable, frequent productivity use; richer layout/interactions and native capability presentation follow later bounded tasks. This supersedes the former §6.1 instruction to maximize Web UI reuse. Share protocol/model/Repository behavior, suitable platform-neutral hooks, design tokens and UI semantics; do not share complete React visual components such as Button, MessageBubble or ChatWindow. Avoid duplicating protocol/domain logic or importing Desktop native hooks into Web.

TypeScript owns Repository/models/transaction intent; SQLx Rust native adapter remains limited to connections/queries/one atomic transaction. OS notifications/tray/secure storage use authorized native boundaries and later tasks; this design does not add a library or feature implementation.

## Mobile

Android Kotlin + Jetpack Compose. UI emits intent to ViewModel; ViewModel invokes Repository and exposes StateFlow; Compose observes that state with lifecycle-aware collection. StateFlow is observable state, not a transport or storage layer. Repository delegates to SDK SQLite and authorized protocol adapters. Jetpack Navigation Compose owns host navigation; ViewModel/StateFlow/Navigation choices are explicit Human decisions recorded in canonical §6.5 / ADR-0006, not a Task Spec selection.

Real Android Studio emulator validation is required. Kotlin models/Repository/protocol/plugin adapters implement equivalent behavior under the same canonical contracts/fixtures; TypeScript SDK/hook/component reuse is not required. No Room/ORM, arbitrary network library, JS bridge/runtime/codegen or shared native rewrite.

## Shared UI boundary

Share design specification, token meanings and UI behavioral semantics. Web/Desktop share TypeScript protocol-sdk/plugin-sdk/models and eligible hooks; Mobile implements equivalent Kotlin behavior using identical contracts/fixtures. No three-platform visual component library. UI contracts here mean presentation obligations, never a new machine-verifiable wire/API/schema authority; those remain exclusively contracts/.

## Plugin and AI boundaries

S2 reserves host-owned Plugin/AI entries only. No renderer, UI-code download/execution, remote component injection, plugin installation, dynamic loading or runtime. Declarative poll descriptions illustrate future design, not a new schema/API or S2 implementation. S4 retains §8.2 reviewed Custom Render Bundle plus declarative UI, package/signature/hash/schema/compatibility/permission/resource/CSP/entry validation, sandbox iframe/isolated WebView and whitelist Bridge. No relaxation of token/SQLite/host-resource protections or canonical plugin fixtures. AI remains placeholder until separate explicit API/contracts/architecture decisions and acceptance.

## Future GUI API coverage

Auth login, web/native refresh, logout and expired-session handling; current user information; user search and add friend; conversation list/open; message send/receive/state; Sync state. Resolve operations from contracts/http/auth-user-friend.openapi.json and canonical WSS envelope/sync schemas. Conversation/message/sync are not invented HTTP routes: current accepted protocol contracts decide transport and field shape. No changes to OpenAPI/backend are authorized. Other existing operations or future functionality require their own bounded task. Plugin/AI placeholders cannot imply missing backend capability exists.

## Delivery boundary

No pages, components, UI interaction implementation, pixel design or runtime is delivered here. Future GUI tasks must cite the independently accepted canonical/ADR and spec/acceptance/client-gui.md; architecture freeze, GUI Task PASS and S2 Gate PASS are separate outcomes.
