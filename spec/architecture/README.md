# Architecture Index

This file is a resolver, not an independent architecture specification.

1. Read the [baseline manifest](./baseline.md).
2. Resolve and SHA-256-check the single canonical Markdown artifact named by that manifest.
3. Verify the retained historical PDF against the manifest's separate `previous_sha256` provenance value.
4. Apply approved decisions in [`decisions/`](./decisions/) through the documented architecture process.

The manifest and this index contain discovery and migration metadata only. They do not summarize, replace, or silently reinterpret the canonical Markdown. The PDF is an immutable pre-migration snapshot, not an active second canonical source. The Markdown remains frozen under the same ACP/ADR approval rule.
