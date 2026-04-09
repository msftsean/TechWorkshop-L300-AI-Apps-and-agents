# Decision: Workshop SWA — Single-File Architecture

**Author:** Tony Stark
**Date:** 2026-04-09
**Status:** Implemented

## Context
Sean needs a dashboard to track manual workshop tasks across Exercises 4, 5, and 6. These are portal/CLI tasks that can't be automated.

## Decision
Built as a single `index.html` file at `src/swa/` — no build step, no framework, no external JS dependencies. All CSS and JS is inline.

## Rationale
- **Zero build complexity** — deploys directly to Azure Static Web Apps without any CI pipeline changes
- **No dependency drift** — nothing to update, no `node_modules`, no bundler config
- **Portable** — works offline, can be opened directly from filesystem
- **localStorage for state** — checkbox progress persists across sessions without a backend

## Tradeoffs
- 42KB single file is larger than it would be split, but still trivial for a dashboard
- Inline JS means no tree-shaking, but the JS is ~80 lines total
- No component reuse, but the 7 tabs follow a consistent pattern via copy

## Impact
- New directory: `src/swa/`
- No changes to existing code or workflows
- Can be deployed independently as an Azure SWA or served from any static host
