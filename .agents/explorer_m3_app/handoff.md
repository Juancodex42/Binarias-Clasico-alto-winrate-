# Handoff Report — explorer_m3_app

- **Agent Name**: explorer_m3_app
- **Archetype**: explorer
- **Mission**: In-depth investigation of `static/js/app.js`, `templates/index.html`, and `app.py` covering Smart Mode UI, Advanced Mode UI, Micro-interactions, and WebSocket live price feeds.
- **Date**: 2026-08-16

---

## 1. Observation

Direct observations and evidence collected across the codebase:

### Smart Mode UI Flow
- **Preset Selection**: `templates/index.html:115-119` defines `#smart-preset-select` with options `preset_33_6`, `preset_25_8`, `preset_200_1`. `static/js/app.js:1940-1967` synchronizes `#smart-attempts` and `#smart-streak-length`.
- **Universe Selection & Validation**: `templates/index.html:87-98` defines checkboxes `input[name="smart-universe"]`. `static/js/app.js:2017-2025` validates `universe.length >= 3`. `static/js/app.js:2094-2113` updates `.asset-wr-badge` with star badges (`⭐⭐⭐`, `⭐⭐`, `⭐`) and OOS Win Rate percentages upon SSE completion.
- **Risk Capital Live Sync**: `templates/index.html:144-150` defines `#smart-base-capital`, `#smart-profit-pct`, `#smart-risk-capital` (`readonly`). `static/js/app.js:527-536` attaches `input` listeners to auto-calculate `risk = base * pct / 100`.
- **SSE Stream Execution**: `app.py:1413-2083` handles `GET /api/smart-optimize-v2-stream`. `static/js/app.js:2051` opens `EventSource` with JSON stringified parameters.
- **Progress & Console Logs**: `templates/index.html:182-196` defines `#smart-console-box`, `#smart-progress-bar-fill`, `#smart-console-logs`. `static/js/app.js:2005-2013`, `2068-2074` updates fill width and appends timestamped log lines with auto-scroll (`scrollTop = scrollHeight`).
- **Top Strategies Ranking**: `templates/index.html:201-217` defines `#smart-top-5-box` and `#smart-top-5-list`. `static/js/app.js:2116-2467` renders interactive ranking pills (🥇, 🥈, 🥉, #N). Clicking any pill triggers `renderStrategyView(strat)`, dynamically updating the entire Smart dashboard (ladder, recs, equity curve, Monte Carlo, TradingView chart, Markov matrix).
- **Paroli Ladder**: `templates/index.html:228-244` defines `#smart-ladder-content`. `static/js/app.js:2234-2279` builds the step-by-step Paroli compound ladder with `bet_size`, `payout_return`, accumulated next bet, and final completed step.
- **Markov Transition Matrix**: `templates/index.html:356-382` defines `#smart-markov-table` and `#smart-markov-explanation`. `static/js/app.js:2362-2408` populates transition probabilities `P(W|W)`, `P(L|W)`, `P(W|L)`, `P(L|L)`.
- **Selected Assets Table**: `templates/index.html:266-292` defines `#smart-selected-assets-table` and `#smart-selected-assets-body`. `static/js/app.js:2474-2524` populates non-correlated assets (<0.65 threshold) with historical sample period (~2021-2026, 1250 daily candles) and Win Rate OOS breakdown, followed by dimmed discarded correlated assets.

### Advanced Mode UI Flow
- **Pair & Timeframe Selector**: `templates/index.html:390-428` defines `#pair-selector`, `#interval-selector`, `#source-selector`. `static/js/app.js:686-750` loads pairs from `/api/data/pairs` and enforces timeframe restrictions (`updatePairTimeframeRestrictions` locks non-USDT traditional assets to `1d` and historical source).
- **Dynamic Strategy Parameters**: `templates/index.html:475-477` defines `#dynamic-params`. `static/js/app.js:875-893` renders parameter inputs dynamically from `strategy.get_params_schema()`.
- **Backtest SSE Stream**: `app.py:2086-2260` handles `GET /api/backtest-stream`. `static/js/app.js:897-1043` sends requests via `EventSource`, updates `#backtest-progress-fill` / ETA, and calls `displayBacktestResults(data)` and `displayStatistics(stats)`.
- **Genetic Optimizer SSE**: `app.py:2263-2347` handles `GET /api/genetic/run-stream`. `static/js/app.js:1824-1938` streams Rust generations, injects optimal parameters into `#dynamic-params`, shows `#genetic-feedback`, and auto-submits `#backtest-form`.
- **Streak Optimizer & Monte Carlo**: `app.py:645-680` (`POST /api/optimize-streak`) and `app.py:505-544` (`POST /api/montecarlo`). `static/js/app.js:1198-1427` calculates campaign plans and renders `#streak-recommendation-content`, `#bet-ladder-container`, `#streak-alternatives-table`, and `#mc-chart`.
- **Trade Log Table**: `templates/index.html:596-613` defines `#trades-table`. `static/js/app.js:1077-1136` populates the last 100 trades. Line 1098 calls `highlightTradeOnChart(trade, tvChart, candleSeries)` (noting `tvChart` should be `mainChart`).
- **History & Saved Persistence**: `templates/index.html:617-641` defines `#history-list` and `#saved-list`. `static/js/app.js:1441-1820` persists simulations in `localStorage`, allowing favorite pinning, deletion, history wiping, and comprehensive state reloading via `loadBacktestState`.

### Micro-Interactions & Modals
- **Pine Script & AI Prompt Export**: `static/js/app.js:5-234` implements `generatePineScriptV5(strat)` and `generateAIPrompt(strat)` with global window hooks `window.togglePineScriptModal`, `window.copyPineScript`, and `window.copyAIPrompt`.
- **Tab Navigation**: `static/js/app.js:476-500`, `661-682`, `851-873` manages switching between `#mode-smart` and `#mode-advanced`, `.tabs-nav` sub-tabs (`dashboard`, `backtest`, `resultados`, `estadisticas`, `optimizador`), and `.subtabs-nav` (`sec-strategy`, `sec-barbell`, `sec-genetic`).

### WebSocket Live Price Feed
- **Binance WebSocket Feed**: `static/js/app.js:251-379` connects to `wss://stream.binance.com:9443/ws/${streamPair}@kline_${interval}` when source is `live`.
- **Status Badge**: `templates/index.html:48-50` defines `#live-badge` and `#live-badge-text`. `static/js/app.js:269-279` displays `En Vivo: $${price}`.
- **REST Polling Fallback**: `static/js/app.js:380-413` automatically switches to 3s polling fallback on WebSocket error/disconnection.

---

## 2. Logic Chain

1. **Architecture Verification**: The UI cleanly isolates Smart Mode (1-click portfolio optimization) from Advanced Mode (granular backtesting and diagnostics), while sharing core state management, chart instances, and localStorage persistence.
2. **Contract Consistency**: All 89 DOM IDs and 37 form inputs identified in `PROJECT.md` are actively mapped in `static/js/app.js` and rendered in `templates/index.html`.
3. **SSE & Streaming Robustness**: Both `/api/smart-optimize-v2-stream` and `/api/backtest-stream` follow consistent event payloads (`type: log | progress | error | result`), allowing real-time progress bars, ETA calculation, and telemetry console logging.
4. **Minor Bugs Identified**:
   - `static/js/app.js:1098`: `highlightTradeOnChart(trade, tvChart, candleSeries)` references undefined variable `tvChart` instead of `mainChart`.
   - Native `alert()` calls in copy actions and form validation interrupt the dark institutional experience and should be replaced by lightweight toast notifications.

---

## 3. Caveats

- **Network Dependency for Binance Live Feed**: Live WebSocket and REST kline endpoints require internet access to `api.binance.com` / `stream.binance.com`. In offline environments, the terminal automatically falls back to local CSV historical data without crashing.
- **Rust Optimizer Binary**: Búsqueda genética relies on `genetic_optimizer.exe` in `engine/genetic_optimizer/target/release/`. If uncompiled, backend returns explicit error messages cleanly handled by the SSE error event listener.
- **No other caveats.**

---

## 4. Conclusion

The application's interaction flows, DOM architecture, SSE streaming pipelines, and WebSocket handlers are functionally solid and aligned with the requirements in `ORIGINAL_REQUEST.md` and `PROJECT.md`. Milestone 3 implementation can proceed with high confidence by applying the minor fix to `tvChart` and optionally introducing a non-blocking toast notification system.

---

## 5. Verification Method

To independently verify all findings:
1. **Source Inspection**:
   - Inspect `static/js/app.js` lines 1077-1136 (`trades-table` click handler and `highlightTradeOnChart`).
   - Inspect `static/js/app.js` lines 1969-2582 (`runSmartOptimization` SSE and top-5 strategy rendering).
   - Inspect `static/js/app.js` lines 251-413 (WebSocket lifecycle and fallback polling).
   - Inspect `templates/index.html` lines 27-61 (header, badges, mode switcher), lines 65-385 (Smart Mode), and lines 388-860 (Advanced Mode).
2. **Automated Backend Test Suite**:
   ```bash
   pytest tests/
   ```
3. **Invalidation Condition**: If any DOM ID in `templates/index.html` is altered or removed without updating `static/js/app.js`, event listeners will fail silently.
