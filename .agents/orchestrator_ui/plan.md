# Master Plan: Binary Options Terminal UI/UX Pro Redesign

## 1. Objectives
Transform the existing Binary Options Quantitative Terminal & Simulator into a high-density, institutional-grade quantitative trading interface adhering to `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`.
Maintain strict zero-regression compatibility: 100% preservation of all existing IDs, input names, event handlers, WebSocket/Flask API routes, and Rust backend interop.

## 2. Phase 0: Survey & Architecture Extraction
- Explorer 1 (Spec Miner): Extract exact design specs, palette (#080b11, #0e1420, #141d2e, accents), typography rules, grid system, and visual requirements from `GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`.
- Explorer 2 (DOM & Frontend Structure): Map all HTML files, templates, existing DOM IDs, form elements, JS scripts, and event listeners in the project.
- Explorer 3 (Charts & Backend Integration): Map Lightweight Charts integration, Chart.js instances, CSS/styling stylesheets, Flask routes, and simulation data pipelines.

## 3. Phase 1: Global Project Plan & Decomposition (PROJECT.md & TEST_INFRA.md)
- Consolidate explorer findings.
- Establish Feature Inventory, Milestone Decomposition (3-7 milestones), and Interface Contracts.
- Launch Dual Track: Implementation Track and E2E Testing Track.

## 4. Phase 2: Implementation Milestones Execution
- Milestone 1: Design System Foundation & Global CSS/Tokens (Variables, Reset, Typography, Grid, Dark Surfaces, Micro-interactions).
- Milestone 2: Institutional Header, Mode Switcher (Smart/Advanced), & High-Density Control Bar.
- Milestone 3: Core Workspace Layouts (Panels, Tabs, Tabular Numbers, Markov/Metrics/Balance Data Tables).
- Milestone 4: Charting Engine Harmonization (Lightweight Charts candlesticks & overlay signals, Chart.js Equity/Monte Carlo/Heatmap dark themes).
- Milestone 5: Responsive Polish, Micro-interactions, Diagnostics Panel & Zero-Regression Validation.

## 5. Phase 3: E2E Testing & Final Verification
- Pass 100% E2E test suite (Tiers 1-4).
- Tier 5: Adversarial Coverage Hardening.
- Forensic Integrity Audit (CLEAN).
- Final handoff to Sentinel.
