# Handoff Report - Frontend Structure Explorer
**Phase 1: Exhaustive Survey & DOM Preservation Inventory**

---

## 1. Observation

- **Project Root**: `c:\Users\juanc\Desktop\prueba`
- **Analyzed Templates & Assets**:
  - `templates/index.html` (846 lines, 66,358 bytes): Jinja2 SPA template containing 6 main view panes (`smart-dashboard`, `dashboard`, `backtest`, `resultados`, `estadisticas`, `optimizador`), 3 sub-tab panes (`sec-strategy`, `sec-barbell`, `sec-genetic`), 37 static form controls, 16 buttons, and 6 table structures.
  - `static/css/style.css` (1043 lines, 22,717 bytes): Custom dark theme stylesheet with `:root` variables, `.glass-card` styling, flex/grid layouts, responsive breakpoints (`@media (max-width: 1100px)`), and status badges.
  - `static/js/app.js` (2583 lines, 128,222 bytes): Core application logic managing global `state`, SSE streaming listeners for `/api/backtest-stream`, `/api/genetic/run-stream`, `/api/smart-optimize-v2-stream`, Binance WebSocket feeds, DOM event bindings (32 event listeners), LocalStorage persistence (`binsim_history`, `binsim_saved`), and dynamic DOM generators (PineScript modals, dynamic strategy parameters, top-5 pills).
  - `static/js/charts.js` (470 lines, 16,620 bytes): Visual rendering engine for TradingView Lightweight Charts v4 (candlestick chart with CALL/PUT/WIN/LOSS markers), Chart.js (Equity curve, Monte Carlo cones, Bar charts), and Canvas 2D correlation heatmap.
- **Backend API Endpoints**:
  - `app.py` exposes 17 routes including REST endpoints (`/api/data/pairs`, `/api/data/candles`, `/api/strategies`, `/api/optimize-streak`) and SSE endpoints (`/api/backtest-stream`, `/api/genetic/run-stream`, `/api/smart-optimize-v2-stream`).

## 2. Logic Chain

1. **SPA Architecture**: `templates/index.html` relies on single-page tab pane toggling via `.tab-pane.active` and `#mode-smart` / `#mode-advanced` class toggles.
2. **Coupling between JS and DOM**: JavaScript (`app.js`) queries exactly 89 distinct element IDs using `document.getElementById`, binds listeners to `.tab-btn`, `.subtab-btn`, `.mode-btn`, `.top-strat-pill`, `.backtest-item`, `.btn-save-item`, `.btn-delete-item`, and dynamic inputs `param-${p.name}` inside `#dynamic-params`.
3. **Zero-Regression Requirement**: If any existing ID, form input name (`smart-universe`), data attribute (`data-tab`, `data-subtab`, `data-param`, `data-strat-idx`, `data-trade-idx`, `data-id`, `data-type`), or canvas ID is altered or deleted during redesign, the corresponding JavaScript handler, SSE stream receiver, or Chart.js/Lightweight Charts instance will throw runtime exceptions or fail to render.
4. **Preservation Inventory**: A complete catalog of 89 IDs, 37 static input controls, 16 buttons, and all dynamic generation hooks was compiled and validated against JS queries.

## 3. Caveats

- In `app.js`, there are legacy fallback references to `gn-chart`, `kelly-chart`, `opt-recommendation`, `n-table`, and `mc-stats` from earlier iterations of the manual optimizer. These do not cause errors because the code checks `if (document.getElementById(...))` before manipulating them, but all active elements must remain preserved.
- The Binance WebSocket feed requires an active internet connection to `stream.binance.com:9443`; if disconnected, `app.js` gracefully falls back to polling `api.binance.com` or local historical data.

## 4. Conclusion

The frontend codebase has been exhaustively analyzed and mapped. The comprehensive report has been written to:
`c:\Users\juanc\Desktop\prueba\.agents\survey_frontend_explorer\survey_frontend_report.md`

All DOM element IDs, form inputs, buttons, event bindings, JS global state, chart integrations, and API endpoints are fully documented. The critical preservation inventory provides an unambiguous blueprint for the subsequent UI/UX redesign phases to execute institutional-grade styling without any functional regressions.

## 5. Verification Method

- **Automated DOM Extraction Verification**: Run `python .agents/survey_frontend_explorer/analyze_dom.py` to confirm all 89 IDs, 37 form inputs, and 16 buttons are parsed without errors.
- **Flask Route & API Verification**: Run `python scratch/test_flask_routes.py` to verify backend endpoints `/api/strategies`, `/api/backtest`, and `/api/smart-optimize` return HTTP 200 and expected data structures.
- **Unit Test Integrity**: Run `pytest test_high_winrate_mechanisms.py` to confirm zero regression on quant engines.
