# Project: Binary Options Quantitative Terminal UI/UX Pro Redesign

## Architecture
- **Tech Stack**: Flask / Python backend, Rust quantitative core bindings, Vanilla JS (ES6+) with SSE & WebSocket streaming, TradingView Lightweight Charts v4, Chart.js v4, HTML5 2D Canvas, Custom CSS Design System (Inter + JetBrains Mono).
- **Core Pattern**: Single-Page Application (SPA) with Dual-Mode Interface:
  1. *Smart Mode (Piloto Automático)*: 1-click execution with pre-calculated Barbell presets, multi-asset universe selection, real-time SSE genetic optimization logs, Top-5 strategy ranking, Paroli compound ladder, Markov matrix, cross-asset correlation heatmap, and equity / Monte Carlo cones.
  2. *Advanced Mode (Manual)*: Granular control over currency pairs, timeframes, custom strategy hyperparameters, genetic algorithm tuning, Monte Carlo stress testing (5,000 paths), and statistical diagnostics.
- **Data Flow**:
  - Backend API (`app.py`) serves REST endpoints and SSE streams.
  - Rust engine powers genetic optimization and high-frequency backtesting.
  - Frontend (`app.js`) handles DOM state, user interactions, WebSocket feeds, and data distribution to `charts.js`.
  - Styling (`style.css`) applies an institutional dark fintech visual design system.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Institutional Dark Design System | FinTech Slate & Obsidian surfaces (#080b11, #0e1420, #141d2e, #1c273d), 1px subtle borders | M1 | GUIA_MAESTRA §4.1 |
| 2 | Calibrated Semantic Color Palette | Anti-halation & anti-chromostereopsis semantic accents (#38bdf8, #10b981, #f43f5e, #a855f7, #f59e0b) | M1 | GUIA_MAESTRA §4.3 |
| 3 | 8-Point Grid & Spacing Hierarchy | Standardized spacing tokens (--space-1 to --space-8) and container padding | M1 | GUIA_MAESTRA §4.4 |
| 4 | Dual Typography & Tabular Numbers | Inter for UI text; JetBrains Mono with tabular-nums / tnum for all numeric data | M1 | GUIA_MAESTRA §5.1 |
| 5 | Micro-Interactions & Motion Tokens | 120ms-180ms ease transitions, hover elevations, focus rings, progress bar shimmer | M1 | GUIA_MAESTRA §7.1 |
| 6 | Unified Institutional Header | Brand identity, Smart/Advanced Mode Switcher, Rust engine badge, live pulse indicator | M2 | GUIA_MAESTRA §2.2 |
| 7 | High-Density Compact Control Bar | Single-line command bar for Smart Mode: Barbell presets, universe checkboxes, numeric inputs, auto-run button | M2 | GUIA_MAESTRA §2.4 |
| 8 | 100% ID & Form Input Preservation | Complete retention of all 89 DOM IDs and 37 form inputs across templates | M2 | Survey Explorer Report |
| 9 | Smart Mode Multi-Panel Workspace | Asymmetric layout: Top-5 strategy ranking, Paroli ladder, recommendation text, selected assets table | M3 | GUIA_MAESTRA §2.5 |
| 10 | Advanced Mode Tab Panes & Forms | Full styling of Mercado, Backtest, Resultados, Estadísticas, Optimizador panels & stats cards | M3 | index.html, style.css |
| 11 | Data Tables & Markov Alignment | Tabular numeric alignment (right-aligned numbers) on Markov matrices, trades, and streak tables | M3 | GUIA_MAESTRA §5.2 |
| 12 | Lightweight Charts Theme & Markers | Dark transparent canvas, subtle grid (0.03 opacity), crosshairs, candlestick styling, CALL/PUT badges | M4 | charts.js, GUIA_MAESTRA §6.1 |
| 13 | Chart.js Equity Curves & MC Cones | Auto-log scale equity curve with glowing gradient, Monte Carlo P5-P95 cones, dark tooltips | M4 | charts.js, GUIA_MAESTRA §6.2 |
| 14 | Canvas 2D Correlation Heatmap | High-DPI Retina canvas rendering of cross-asset return correlation matrix with color interpolation | M4 | charts.js, GUIA_MAESTRA §6.3 |
| 15 | Live Binance WebSocket & SSE Feeds | Robust live price updates, SSE streaming logs, modal dialogs (Pine Script & AI Prompt export) | M4 | app.js |
| 16 | E2E Testing Suite Pass (Tiers 1-4) | Comprehensive test suite validation (backend 264 tests + frontend DOM/ID/CSS verification) | M5 | Dual Track Plan |
| 17 | Adversarial Hardening (Tier 5) & Audit | Stress-testing edge cases, zero console errors, forensic integrity audit (CLEAN) | M5 | Project Protocol |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Design System & CSS Foundation | `static/css/style.css`: Tokens, variables, 8-pt grid, typography, cards, inputs, buttons, badges, shimmer | none | DONE |
| M2 | Institutional HTML5 Workspace & Templates | `templates/index.html`: Header, Mode Switcher, Telemetry badges, Smart Mode control bar, Multi-panel workspace, Advanced tabs, Tabular data tables, 100% ID retention | M1 | DONE |
| M3 | Charting Engine & Micro-Interactions | `static/js/charts.js` & `static/js/app.js`: Lightweight Charts, Chart.js, Canvas Heatmap, tooltips, markers | M1, M2 | DONE |
| M4 | E2E Verification, Hardening & Audit | Full test suite execution, zero console errors, browser render checks, Tier 5 hardening, Forensic Audit | M1..M3 | DONE |

## Interface Contracts
### `templates/index.html` ↔ `static/js/app.js`
- **Header & Modes**: `#mode-smart`, `#mode-advanced`, `.tabs-nav`
- **Smart Mode Form Controls**: `#smart-preset-select`, `#smart-streak-length`, `#smart-base-capital`, `#smart-profit-pct`, `#smart-risk-capital` (readonly), `#smart-attempts`, `#smart-payout`, `#smart-generations`, `#smart-population`, `input[name="smart-universe"]`, `.asset-wr-badge`, `#btn-smart-run`
- **Smart Mode Telemetry & Output**: `#smart-console-box`, `#smart-progress-bar-fill`, `#smart-console-logs`, `#smart-top-5-box`, `#smart-top-5-list`, `#smart-rec-content`, `#smart-ladder-content`, `#smart-selected-assets-table`, `#smart-selected-assets-body`, `#smart-markov-table`, `#smart-markov-explanation`, `#smart-asset-selector`, `#smart-tv-chart`, `#smart-tv-chart-empty`, `#smart-equity-chart-canvas`, `#smart-mc-chart-canvas`, `#smart-correlation-canvas`
- **Advanced Mode Controls & Panels**: `#pair-selector`, `#interval-selector`, `#source-selector`, `#live-badge`, `#live-badge-text`, `#tv-chart`, `#chart-loader`, `#backtest-form`, `#run-backtest-btn`, `#save-backtest-btn`, `#strategy-selector`, `#dynamic-params`, `#expiry-candles`, `#payout`, `#backtest-n-consecutive`, `#backtest-cycle-prob`, `#backtest-bet-fraction`, `#optimize-genetic-btn`, `#gen-generations`, `#gen-population`, `#gen-min-trades`, `#genetic-progress-fill`, `#genetic-progress-text`, `#genetic-progress-eta`, `#genetic-feedback`, `#backtest-progress-fill`, `#stat-winrate`, `#stat-trades`, `#stat-pnl`, `#stat-mw`, `#stat-ml`, `#equity-chart`, `#trades-table`, `#btn-clear-history`, `#history-list`, `#saved-list`, `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#cond-probs`, `#market-state-chart`, `#markov-table`, `#opt-winrate`, `#opt-payout`, `#opt-base-capital`, `#opt-profit-pct`, `#opt-risk-capital`, `#opt-target-capital`, `#opt-attempts`, `#btn-calc-streak`, `#streak-progress-fill`, `#streak-recommendation-content`, `#bet-ladder-container`, `#streak-alternatives-table`, `#mc-chart`
- **Global Window Hooks**: `window.togglePineScriptModal(id)`, `window.copyPineScript(id)`, `window.copyAIPrompt(id)`

### `static/js/app.js` ↔ `static/js/charts.js`
- `initLightweightChart(containerId, height)`
- `updateCandlestickChart(chartInstance, candleData, signalMarkers)`
- `renderEquityCurve(canvasId, equityData, tradeDates, options)`
- `renderMonteCarloCones(canvasId, mcPercentiles, initialCapital)`
- `renderCorrelationHeatmap(canvasId, correlationMatrix, tickerList)`
- `renderDiagnosticsCharts(statsData)`

### `static/js/app.js` ↔ Backend Flask / SSE APIs (`app.py`)
- `/api/data/pairs` (GET)
- `/api/data/candles` (GET)
- `/api/strategies` (GET)
- `/api/backtest-stream` (GET SSE)
- `/api/smart-optimize-v2-stream` (GET SSE)
- `/api/genetic/run-stream` (GET SSE)
- `/api/optimize-streak` (POST)
- `/api/montecarlo` (POST)

## Code Layout
- `templates/index.html`: Semantic HTML5 layout, container hierarchy, glass-card elements, form controls, charts placeholders.
- `static/css/style.css`: Design tokens, CSS reset, layout grid, typography, components, tables, animations.
- `static/js/app.js`: State manager, SSE listener, WebSocket, UI bindings, modal handlers.
- `static/js/charts.js`: Lightweight Charts v4 & Chart.js v4 wrappers, Canvas 2D renderers.
- `tests/`: Comprehensive Python test suite (Tiers 1-4).
- `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`: Reference UI/UX standard.
