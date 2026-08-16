# BRIEFING — 2026-08-16T19:19:30Z

## Mission
Extract and catalog an exhaustive UI/UX specification report for the Binary Options Quantitative Terminal Redesign from authoritative design docs and codebases.

## 🔒 My Identity
- Archetype: Specification Miner / UI Spec Miner
- Roles: UI Specification Analysis & Extraction, Quantitative Terminal Design Systems
- Working directory: c:\Users\juanc\Desktop\prueba\.agents\survey_spec_miner
- Original parent: 4c01017d-c627-4ce2-bd33-30c9b6192414
- Milestone: UI/UX Specification Mining & Cataloging

## 🔒 Key Constraints
- Visual Design System tokens: exact HEX colors for surfaces (#080b11, #0e1420, #141d2e), borders, semantic & accent colors (#38bdf8, #10b981, #f43f5e, #a855f7, #f59e0b), anti-chromostereopsis / anti-halation rules.
- 8-point grid metrics, compact layout, institutional header, multi-panel workspace.
- Typography: Inter/Geist UI + JetBrains Mono tabular-nums for numeric/quant metrics.
- Charting themes: Lightweight Charts and Chart.js specs.
- Micro-interactions, transitions (150-200ms ease), focus rings.
- 100% Preservation: Keep all DOM element IDs, form inputs, button event handlers, API endpoints, zero JS console errors.
- Read-only specification miner: do NOT implement source code changes.

## Current Parent
- Conversation ID: 4c01017d-c627-4ce2-bd33-30c9b6192414
- Updated: not yet

## Task Summary
- **What to build**: Exhaustive specification report (`survey_spec_report.md`) detailing the institutional UI design system, architecture, charts, interactions, and strict preservation contracts.
- **Success criteria**: Comprehensive catalog with all HEX tokens, CSS variables, typography rules, charting config objects, DOM ID preservation matrix, standard features & edge cases tables, and handoff report.
- **Interface contracts**: `ORIGINAL_REQUEST.md`, `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`.

## Key Decisions Made
- Will systematically analyze both primary spec files, as well as existing HTML/JS/CSS files in the workspace to catalog exact DOM IDs and existing implementations to guarantee 100% compatibility.

## Artifact Index
- `.agents/survey_spec_miner/DISPATCH.md` — Dispatch prompt
- `.agents/survey_spec_miner/progress.md` — Progress tracker and heartbeat
- `.agents/survey_spec_miner/survey_spec_report.md` — Exhaustive specification mining report
- `.agents/survey_spec_miner/handoff.md` — Handoff report
