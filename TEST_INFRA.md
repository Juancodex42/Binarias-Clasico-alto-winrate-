# E2E Test Infra: Binary Options Quantitative Terminal UI/UX Redesign

## Test Philosophy
- Opaque-box, requirement-driven, and regression-preventative.
- Methodology: Static DOM & ID Invariant Verification + CSS Design System Audit + Backend API Contract Testing + Automated Browser / Flask Client Integration.

## Feature Inventory & Test Mapping
| # | Feature | Requirement Source | Tier 1 (Unit/DOM) | Tier 2 (Boundary/Edge) | Tier 3 (Cross-Feature) | Tier 4 (Full Flow) |
|---|---------|-------------------|:-----------------:|:----------------------:|:----------------------:|:------------------:|
| 1 | Institutional Dark Design System | GUIA_MAESTRA §4.1 | 5 | 5 | ✓ | ✓ |
| 2 | Calibrated Semantic Color Palette | GUIA_MAESTRA §4.3 | 5 | 5 | ✓ | ✓ |
| 3 | 8-Point Grid & Spacing Hierarchy | GUIA_MAESTRA §4.4 | 5 | 5 | ✓ | ✓ |
| 4 | Dual Typography & Tabular Numbers | GUIA_MAESTRA §5.1 | 5 | 5 | ✓ | ✓ |
| 5 | Micro-Interactions & Motion Tokens | GUIA_MAESTRA §7.1 | 5 | 5 | ✓ | ✓ |
| 6 | Unified Institutional Header | GUIA_MAESTRA §2.2 | 5 | 5 | ✓ | ✓ |
| 7 | High-Density Compact Control Bar | GUIA_MAESTRA §2.4 | 5 | 5 | ✓ | ✓ |
| 8 | 100% ID & Form Input Preservation | ORIGINAL_REQUEST R5 | 5 | 5 | ✓ | ✓ |
| 9 | Smart Mode Multi-Panel Workspace | GUIA_MAESTRA §2.5 | 5 | 5 | ✓ | ✓ |
| 10 | Advanced Mode Tab Panes & Forms | index.html | 5 | 5 | ✓ | ✓ |
| 11 | Data Tables & Markov Alignment | GUIA_MAESTRA §5.2 | 5 | 5 | ✓ | ✓ |
| 12 | Lightweight Charts Theme & Markers | GUIA_MAESTRA §6.1 | 5 | 5 | ✓ | ✓ |
| 13 | Chart.js Equity Curves & MC Cones | GUIA_MAESTRA §6.2 | 5 | 5 | ✓ | ✓ |
| 14 | Canvas 2D Correlation Heatmap | GUIA_MAESTRA §6.3 | 5 | 5 | ✓ | ✓ |
| 15 | Live Binance WebSocket & SSE Feeds | app.js, app.py | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **Backend Test Runner**: `pytest` (executes all tests in `tests/`)
- **Frontend DOM & Contract Validator**: Automated test script validating all 89 IDs, 37 inputs, CSS variables, Google Fonts links, Chart containers, and API responses.
- **Coverage Thresholds**:
  - 100% ID retention (0 missing IDs)
  - 100% backend test pass (264+ pytest tests)
  - Zero JS console errors / syntax errors

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | 1-Click Smart Optimization & Preset Selection | F6, F7, F8, F9, F12, F13, F14, F15 | High |
| 2 | Manual Multi-Asset Candlestick Inspection & Signal Markers | F6, F8, F10, F12 | Medium |
| 3 | Deep Quant Statistics & Markov Matrix Validation | F4, F10, F11, F13 | Medium |
| 4 | Rust Genetic Optimizer Run with Live SSE Progress | F5, F7, F8, F10, F15 | High |
| 5 | Barbell Streak Strategy Planning & Paroli Bet Ladder | F7, F8, F9, F11, F13 | High |
