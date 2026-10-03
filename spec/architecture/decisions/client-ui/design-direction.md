# Client Design Direction

Status: Human-approved initial direction; candidate pending independent acceptance. Subordinate to canonical v1.1 §6.5 / ADR-0006; no pixel design or component code.

## Adaptive Glass Workspace

构界 IM+ / PlugWorldIM combines concise communication, comfortable productivity and modular extensibility. Design emphasis: 50% Future AI Communication / 30% Productivity Tool / 20% Developer Extensibility. AI-native describes the visual direction; S2 AI is only a construction placeholder. Avoid information piling, complex dashboards, excessive Cyber/HUD style and visuals added merely to demonstrate technology.

Minimal Glassmorphism uses translucent surfaces, subtle borders, blur and layered depth to make hierarchy legible. Glass expresses hierarchy rather than decoration. No heavy glow, neon, particles or complex 3D. The base must remain readable over changing backgrounds; foreground contrast and focus/selection/error affordances cannot depend solely on transparency or hue. If blur/transparency is unsuitable for platform performance or readability, use a restrained opaque surface preserving the same hierarchy; no new rendering library is implied.

## Themes

| Theme | Position | Color direction |
| --- | --- | --- |
| Cold AI | AI / Technology / Intelligence | Cool blue, purple gradient, dark glass |
| Warm Creative | Social / Creative / Human | Warm gradient, soft glass, approachable tone |

Both themes MUST keep the same Logo, brand elements, layout, interaction meanings and component semantics. Theme switching changes Color tokens only, including background/surface/foreground/border/accent/gradient/selection/status colors; it cannot change type, spacing, blur, navigation or behavior. No additional light/dark theme matrix is implied. Transparent-surface hierarchy must remain consistent between the themes.

## Design Token principles

Use semantic names with one responsibility, shared meanings across platforms and native representation per platform. Color tokens express surfaces/text/borders/accent/status; Typography tokens express font family/size/line-height; Spacing tokens express density/spacing. Fixed typography/spacing/color values, pixel layout, fonts, scales and generation/build tooling are outside this initial direction. Later GUI tasks choose concrete values within the accepted direction, with screenshot evidence and Architect approval; introducing sensitive dependencies still follows §2.3.

Two theme presets vary only colors. User appearance preferences may independently adjust Typography and Spacing locally within validated supported ranges. This distinction must hold after restart and theme switching: theme changes do not reset user type/density, and user settings do not alter component meaning. No cloud synchronization, plugin styling control, arbitrary CSS/script injection or downloaded font system is authorized. Web appearance preferences must stay separate from its memory-only chat state; the storage mechanism needs a later bounded choice. Desktop/Mobile preferences must not modify Repository message/schema/transaction semantics.

## Configuration and interaction guardrails

The host client controls theme, typography and spacing. Plugins cannot modify primary navigation, brand core or base UI semantics. Larger type/spacing must preserve readable content, usable input, reachable navigation and meaningful empty/loading/error/sync states on each platform. Keyboard focus and accessible labels must be available where applicable; color is not the only message-delivery indicator. These are future GUI review obligations, not authorization for a named accessibility/component library.

## Per-platform expression

Web favors compact online communication. Desktop favors comfortable repeated use with richer workspace layout and native capability surfaces. Mobile favors touch-readable Compose presentation and emulator-verified behavior. Share semantic design direction and token meanings, not full visual components or forced pixel-identical layouts. Logo creation and pixel-perfect screens are not this task's deliverables.
