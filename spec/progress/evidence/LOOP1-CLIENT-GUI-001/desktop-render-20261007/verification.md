# Desktop self-check 2026-10-07

Human requested 自己检查. Assigned managed root verified; branch task/LOOP1-CLIENT-GUI-001-ui-update, sole writer /root. Main unchanged, six unknown-origin recovery screenshot moves preserved.

## Actual finding and minimal repair

Installed candidate e548461 imports useRef, but shipped React ES module adapter omitted that named export. Real compiled frontend render failed before first paint: The requested module react does not provide an export named useRef. TypeScript/build and isolated helper tests had passed and did not cover runtime module loading. Preserved blank-page capture and original failures in Recorder. Added useRef to existing clients/desktop/src/ui/react.config.mjs export only; no runtime/dependency/business/contract/security change.

## Executed checks

Browser-render regression tests/clients/gui/desktop_render.mjs uses already available bundled Playwright and existing installed Edge. Real unmodified dist HTML/React/UI/CSS modules served loopback; only presentation Workspace replaced by explicitly synthetic fixture, native invoke returns false. Screenshots are browser-render fixtures, not actual Windows authenticated screenshots or independent acceptance. Never use them to satisfy the outstanding real Windows proof.

Command: npm --prefix clients/desktop run build (via recorded PowerShell wrapper); node tests/clients/gui/desktop_render.mjs; node tests/clients/gui/auth.mjs; node tests/clients/gui/composer.mjs.
Result: PASS real compiled render, zero page errors; 12 grouped render checks; canonical auth/list/lifecycle tests; seven composer helper checks. Render checks cover actual hover backgrounds/title, real pointer up/down with bottom anchor/clamps/release, keyboard, actual message and Settings wheel scrolling while bars hidden, Session Online vs real connection Offline, local-history Offline without Session, cold/warm14/20/22 viewport. Retained rerunnable render regression catches missing hook export.
Environment: IM_GUI_PLAYWRIGHT_MODULE points to bundled playwright/index.mjs; IM_GUI_RENDER_OUTPUT to private evidence directory; IM_GUI_BROWSER_EXECUTABLE to installed Edge/Application/msedge.exe. No repository test dependency added. Host browser download failed/was stopped, switched to existing Edge; original logs retained.

Command: python -Xutf8 -B tests/clients/gui/native.py package; official NSIS /S update; exact bundle-byte comparison.
Result: PASS; installed im-client-storage.exe exactly matches rebuilt executable except official single UNK->NSS bundle marker. SHA256 in package.json. Previous owned installed process27632 closed for update; app not silently launched in tool trust context.

Command: IM_GUI_ASSIGNED_ROOT=<assigned root> python -Xutf8 -B tests/clients/gui/check_sources.py --development.
Result: baseline and final PASS (all source/dependency, frozen authority, 53 architecture controls, development recovery). Local guards, not CI/Gate acceptance.

## Limits and next action

Native supported UI tools still fail host setup/trusted Node; outside-sandbox standalone capture/input lacks approval elicitation channel. Thus real Windows maximize/minimize operations/authenticated current Chat/Friends and complete screenshot matrix remain unverified. Browser test covers requested rendered control hover, not actual OS window commands. Human desktop Root trust and service39112/session58647 retained for inspection; remove exact temporary CA in same actual desktop context and stop only owned runtime after inspection. Current task active/S2 OPEN; Architect approval, fresh independent Review, exact-head hosted CI and protected main synchronization still pending.

Recorder R-GUI-RENDER-CHECK-20261007: one direct npm child launch failed WinError2 before subprocess creation; recorder emitted command_started without command_finished. This instrumentation gap is explicitly exposed and preserved; subsequent build used PowerShell wrapper and actual tests recorded. No recorder evidence rewritten. Tool probes/prep are disclosed resumed work. Research structural validation cannot imply complete trace or product acceptance.

Recorder sealed46events; validate-run/private validate-repository structural PASS, manifest eebcb5ca0e9e04d02f1c4fd2b21ae56dedf2a9283c5502613d3a4a39cadfe655. Structural PASS does not erase declared child-start observation gap. Candidate/source/artifact binding and current metadata archived after seal; no product source changed.
