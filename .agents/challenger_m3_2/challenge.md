# Milestone 3 Adversarial Challenge Report: DOM, Charts & Micro-Interactions

## Challenge Summary

**Overall risk assessment**: LOW (Verdict: **CONFIRM**)

An adversarial audit and empirical stress harness (`tests/test_m3_challenger2_adversarial.py`, `tests/test_m3_charts_integrity.py`, `tests/test_m2_html_workspace_integrity.py`) were executed against `templates/index.html`, `static/js/app.js`, and `static/js/charts.js`. All 105 DOM IDs from `PROJECT.md` are present in `templates/index.html` with zero duplicate IDs and are correctly bound in `static/js/app.js`. All 37 form inputs and 16 action/tab buttons are wired to functional event handlers. Smart Mode and Advanced Mode tab switching functions cleanly via non-destructive CSS class toggling with automated canvas and chart resizing. The live WebSocket streaming engine incorporates automated fallback to REST polling upon connection drop or network exceptions.

---

## Challenges

### [Low] Challenge 1: Error Notification Consistency (Legacy `alert()` vs `showToast()`)
- **Assumption challenged**: That all blocking `alert()` notifications had been replaced with institutional non-blocking toasts across the frontend.
- **Attack scenario**: Triggering network dropouts, empty backtest history selections, or invalid manual inputs triggers `alert(...)` dialogs instead of toast popups.
- **Blast radius**: Cosmetic & UX flow interruption. 12 occurrences of `alert(...)` remain in error-handling catch blocks in `static/js/app.js` (e.g. lines 1033, 1108, 1297, 1332, 1476, 1575, 1598, 1957, 2017, 2106, 2161, 2663). While `showToast` was added for clipboard actions (Pine Script & AI Prompt export), error handlers still invoke browser `alert()`.
- **Mitigation**: Migrate the remaining 12 `alert()` calls in `app.js` to `showToast(msg, 'error')` during Milestone 4/5 hardening.

### [Low] Challenge 2: Correlation Heatmap Redraw on Window Resizing
- **Assumption challenged**: That the 2D HTML5 canvas for the cross-asset correlation matrix redraws crisply at native high-DPI resolution when resizing containers or toggling tabs.
- **Attack scenario**: User resizes viewport or toggles between Smart Mode and Advanced Mode tabs when a correlation matrix was previously rendered.
- **Blast radius**: Potential canvas pixel stretching or blank canvas if not resized and re-rendered.
- **Mitigation**: Confirmed that `app.js` attaches a `ResizeObserver` to `smart-correlation-canvas.parentElement` (lines 578-586) and caches `_lastMatrix` / `_lastLabels` on the canvas element, automatically re-invoking `createCorrelationHeatmap` on tab switch (`switchTab`, line 749). Empirical tests confirm pass.

---

## Stress Test Results

| Test ID | Scenario | Expected Behavior | Actual Behavior | Pass/Fail |
|---|---|---|---|---|
| ST-01 | DOM ID Exhaustion (105 IDs) | All 105 DOM IDs in `PROJECT.md` present in `templates/index.html` | 105/105 IDs present, 0 missing | **PASS** |
| ST-02 | DOM ID Uniqueness | Zero duplicate IDs in `templates/index.html` | 0 duplicate IDs detected across all elements | **PASS** |
| ST-03 | Interactive DOM JS Bindings | All interactive DOM elements referenced in `static/js/app.js` | 100% matched in `app.js` event listeners/selectors | **PASS** |
| ST-04 | Form Controls Inventory | $\ge 37$ form controls (9 checkboxes, 8 smart, 8 backtest, 7 optimizer, 5 selects) | All 37+ form controls present with constraints (min, max, step, readonly) | **PASS** |
| ST-05 | Button Inventory & Handlers | $\ge 16$ buttons with attached click/submit listeners | All 16 buttons bound to listeners in `app.js` | **PASS** |
| ST-06 | Smart/Advanced Mode Switching | Switching between `#mode-smart` and `#mode-advanced` toggles classes without node detachment | Uses `classList.add('active')` / `classList.remove('active')`, zero `removeChild` or destructive `innerHTML` | **PASS** |
| ST-07 | Tab Switching Resize Hook | `switchTab(tabId)` resizes Lightweight Charts & Canvas | Dispatches `applyOptions({width, height})` and `createCorrelationHeatmap` on 50ms delay | **PASS** |
| ST-08 | WebSocket Stream Lifecycle | Connects to `wss://stream.binance.com:9443/ws/{pair}@kline_{interval}` and updates live candle | `onopen`, `onmessage`, `onerror`, `onclose` wired | **PASS** |
| ST-09 | WebSocket Fallback to Polling | On WS error or unexpected close when live mode is active, triggers `startFallbackPolling` | `liveWs.onerror` and `liveWs.onclose` invoke `startFallbackPolling` | **PASS** |
| ST-10 | WebSocket Synchronous Init Guard | If WebSocket constructor throws (e.g. offline/CSP block), catches and starts fallback polling | `try/catch` around `new WebSocket()` calls `startFallbackPolling` | **PASS** |
| ST-11 | Stream Teardown Cleanup | `stopLiveStream()` cleanly disconnects WS without triggering unintended fallback loop | Unbinds `liveWs.onclose = null`, closes socket, clears polling interval | **PASS** |
| ST-12 | Line 1098 Reference Bug | Trade table row click passes defined `mainChart` instead of undefined `tvChart` | Invokes `highlightTradeOnChart(trade, mainChart, candleSeries)` | **PASS** |
| ST-13 | Color Palette De-Halation | Eradication of legacy `#00f5a0`, `#ff4d4d`, `#58a6ff`, `#30363d`, `#8b949e`, `#c9d1d9` | 0 legacy tokens found in `app.js` or `charts.js` | **PASS** |
| ST-14 | Global Window Export Contracts | Window exposes all required modal and charting helper functions | All 17 global exports (`window.togglePineScriptModal`, `window.copyPineScript`, `window.initLightweightChart`, etc.) present | **PASS** |

---

## Unchallenged Areas

- **Backend Flask API Endpoints (`/api/*`)**: Validated via unit test suite integration; live backend network streaming was mocked/verified at unit boundary.
- **Physical Multi-Monitor High-DPI Rendering**: Canvas physical DPI math verified via AST/parser and `devicePixelRatio` scaling formulas.
