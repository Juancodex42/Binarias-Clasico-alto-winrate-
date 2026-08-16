# Specification Mining Report: Milestone 3 — Charting Engine Harmonization & Micro-Interactions

**Subagent**: `spec_miner_m3`  
**Date**: 2026-08-16  
**Scope**: TradingView Lightweight Charts v4, Chart.js v4, Canvas 2D Correlation Heatmap, UI Micro-Interactions, SSE Telemetry & Motion Design  
**Authoritative Sources**:
- `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md` (Sections 3, 4, 5, 6, 7, 8, 9)
- `ORIGINAL_REQUEST.md` (R1, R2, R3, R4, R5)
- `PROJECT.md` (Milestone 3 Architecture & Interface Contracts)
- `TEST_INFRA.md` (Test Scenarios & Validation Invariants)
- `templates/index.html` (Canvases, Chart Containers, Overlays, DOM IDs)
- `static/css/style.css` (Tokens, Variables, Keyframes, Transitions, Tooltips)
- `static/js/charts.js` & `static/js/app.js` (Chart Renderers, Event Handlers, SSE Streaming)

---

## 1. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Lightweight Charts v4 | Dark Canvas & Grid System | Configures Lightweight Charts background to `#080b11` / transparent, ultra-subtle grid lines `rgba(255,255,255,0.03)` | `containerId: string` (`#tv-chart`, `#smart-tv-chart`) | `IChartApi` instance | Throws or logs if container missing | `GUIA_MAESTRA` §4.1, `charts.js:11-56` |
| 2 | Lightweight Charts v4 | Calibrated Candlestick Styling | Renders Japanese candlesticks with Cyber Emerald (`#10b981`) for bullish/CALL and Rose Crimson (`#f43f5e`) for bearish/PUT, without borders | `candleData: Array<{time, open, high, low, close}>` | `ISeriesApi<"Candlestick">` | Clamps / skips malformed OHLC bars | `GUIA_MAESTRA` §4.3, `charts.js:58-72` |
| 3 | Lightweight Charts v4 | Dynamic Trade Signal Markers | Renders directional CALL/PUT arrow badges and WIN/LOSS circle badges with formatted prices and PnL | `signals: Array<{time, direction, result, entry_price, exit_price, pnl}>` | `series.setMarkers()` array | Skips duplicate/invalid timestamps; returns `[]` on empty | `app.js:415-470`, `charts.js:74-91` |
| 4 | Lightweight Charts v4 | Interactive Trade Price Lines | On trade row click in table, overlays solid entry price line and dotted exit price line with badges | `trade: {entry_price, exit_price, direction, result, pnl}` | `series.createPriceLine()` lines | Clears previous lines before creating new | `app.js:1110-1136` |
| 5 | Lightweight Charts v4 | Empty State & Resize Handlers | Shows `#smart-tv-chart-empty` overlay when no klines exist; uses `ResizeObserver` for zero-height collapse prevention | `ResizeObserver` callback; candle data length check | Dynamic container dimensions & display toggle | Falls back to default dimensions if rect is 0 | `templates/index.html:350`, `app.js:506-522` |
| 6 | Chart.js v4 | Global Institutional Dark Defaults | Sets Chart.js global defaults: font family `Inter`, text color `#94a3b8`, dark tooltips with elevated background `#141d2e` and 1px border | Global `Chart.defaults` configuration | Unified default tooltip/axis rendering | N/A | `charts.js:1-9`, `GUIA_MAESTRA` §4.1 |
| 7 | Chart.js v4 | Equity Curve with Electric Sky Fill | Renders capital growth curve with Electric Sky (`#38bdf8`) border and linear gradient fill (`rgba(56,189,248,0.18)` -> `0.00`) | `canvasId`, `equityPoints: Array<{equity, time}>`, `labels` | Chart.js Line chart instance | Falls back to `#1, #2...` if timestamps missing | `charts.js:119-234`, `GUIA_MAESTRA` §4.3 |
| 8 | Chart.js v4 | Auto-Logarithmic Scale Switching | Automatically switches Y-axis from linear to logarithmic if max/min span > 100x and min >= 1.0; cleans log(0) | Array of numerical values | `scales.y.type: 'logarithmic'` or `'linear'` | Clamps values <= 0 to 1.0 to prevent `-Infinity` | `charts.js:159-162` |
| 9 | Chart.js v4 | Non-Decade Tick Filtering Formatter | Filters out intermediate sub-ticks (e.g. 5, 50, 500) on log scale to prevent vertical tick collision; adds `$`, `k`, `M` | `value: number`, `useLog: boolean` | Formatted tick string (e.g. `'$1.2k'`, `'$1M'`) or `null` | Returns formatted string or `null` to hide tick | `charts.js:94-117` |
| 10 | Chart.js v4 | Monte Carlo Probability Cones | Renders 5 percentile paths: P95 (Cyber Emerald `#10b981`), P75 (Emerald 45%), P50 Median (Electric Sky `#38bdf8` 3px), P25 (Crimson 45%), P5 (Rose Crimson `#f43f5e`) | `canvasId`, `labels`, `percentiles: {p95, p75, p50, p25, p5}` | Chart.js multi-line percentile cone chart | Clamps values <= 0.01 to 0.01; switches to log if span > 50x | `charts.js:290-375` |
| 11 | Chart.js v4 | Diagnostic Analytics Bar Charts | Renders Autocorrelation (`#a855f7`), Streaks Frequency (`#38bdf8`), Hourly Win Rate (`#38bdf8`), Market Regimes (`#a855f7`), and $G(N)$ Growth Rate | `canvasId`, `labels`, `values`, `title`, `color` | Chart.js Bar chart instance | Destroys previous instance if re-rendered | `charts.js:236-289`, `app.js:1139-1194` |
| 12 | Canvas 2D | High-DPI Retina Scaling | Detects `window.devicePixelRatio`, scales canvas width/height buffer by DPR, and applies context scale for ultra-sharp Retina rendering | `canvasId`, `window.devicePixelRatio` | Scaled Canvas 2D context | Fallback to `400x280` if parent clientWidth is 0 | `charts.js:378-396` |
| 13 | Canvas 2D | Correlation Heatmap (-1.0 to +1.0) | Renders cross-asset correlation matrix using non-linear gamma intensity $|r|^{1.2}$, mapping $r < 0$ (diversified) vs $r > 0$ (concentrated) | `matrix: number[][]`, `labels: string[]` | Custom Canvas 2D grid with in-cell text | Renders centered "Sin datos de correlación" if empty | `charts.js:377-469` |
| 14 | Canvas 2D | JetBrains Mono In-Cell Typography | Renders correlation values with `JetBrains Mono` / `tabular-nums`, dynamically sized, contrast-adjusted (`#ffffff` for $|r| > 0.40$) | Cell dimensions, correlation float | Centered tabular numbers in each cell | Skips text if cell width < 18px or height < 14px | `charts.js:441-450`, `GUIA_MAESTRA` §5.1 |
| 15 | Micro-Interactions | Standard Motion Tokens & Easing | Applies `--duration-micro: 120ms`, `--duration-state: 180ms`, `--duration-reveal: 240ms` with `--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1)` | CSS transition properties | Smooth 60fps UI feedback without perceived lag | N/A | `style.css:72-76`, `GUIA_MAESTRA` §7.1 |
| 16 | Micro-Interactions | Interactive Button Loading States | On action trigger, disables button, reduces opacity (0.7), sets cursor `not-allowed`, updates dynamic text (`⏳ Optimizando (X%)...`), shows spinner | Button click event | Disabled loading button with spinner | Cleanup callback guarantees restoration on completion/error | `app.js:1977-1988`, `style.css:1425-1447` |
| 17 | Micro-Interactions | SSE Streaming Telemetry & Auto-Scroll | Real-time console receiver formats log lines with timestamps `[HH:MM:SS]`, applies semantic colors, and auto-scrolls to bottom | SSE stream message items (`type: 'log'`, `'progress'`) | Formatted DOM elements in `#smart-console-logs` | Logs red error line on stream error; cleans up state | `app.js:2005-2079`, `style.css:781-813` |
| 18 | Micro-Interactions | Live Pulse & Shimmer Progress Bar | Continuous 2s breathing pulse (`@keyframes livePulse`) on live data feed badge; continuous 2s gradient shimmer (`@keyframes progressShimmer`) | CSS animation triggers | Visual heartbeat & active computation feedback | N/A | `style.css:767-779, 1506-1522` |
| 19 | Micro-Interactions | Strategy Ranking Pills & Paroli Ladder | Interactive pills with hover lift (`translateY(-1px)`), active purple glow (`rgba(168,85,247,0.2)`), and Paroli step slide (`translateX(3px)`) | Mouse hover / click on `.top-strat-pill`, `.ladder-step` | Visual elevation & border highlight | N/A | `style.css:830-858, 995-1065` |

---

## 2. Edge Cases & Boundary Conditions

| # | Feature | Input | Observed / Required Behavior |
|---|---------|-------|------------------------------|
| 1 | Chart.js Log Scale | Equity curve contains $0.00$ or negative balance | Clamps values to $\max(v, 1.0)$ in log mode (or $\max(v, 0.01)$ in Monte Carlo) to prevent $\log(0) = -\infty$ crashing Chart.js engine. |
| 2 | Chart.js Log Scale | Narrow value span ($max/min < 100$) | Remains in `linear` mode to avoid distorting small variations or misleading exponential curves. |
| 3 | Lightweight Charts | Empty candle dataset or no trade signals | `cleanCandles = []`, `buildChartMarkers([])` returns `[]`. `#smart-tv-chart-empty` overlay is displayed (`display: flex`). No JavaScript runtime error thrown. |
| 4 | Lightweight Charts | Container resized during tab switch (`display: none` -> `block`) | `ResizeObserver` detects container width/height changes and invokes `chart.applyOptions({ width: r.width, height: r.height })` to prevent 0px collapsed canvas. |
| 5 | Canvas 2D Heatmap | Matrix is null, undefined, or empty `[]` | Canvas is cleared; renders centered muted message *"Sin datos de correlación"* in `#64748b` without throwing canvas context errors. |
| 6 | Canvas 2D Heatmap | High-DPI screen with devicePixelRatio = 2 (Retina) | Canvas internal buffer is scaled by $2\times$ (`canvas.width = w * 2`, `canvas.height = h * 2`), and `ctx.scale(2, 2)` is applied. Visual text and grid lines remain razor-sharp without blur. |
| 7 | Canvas 2D Heatmap | Matrix contains `NaN`, `null`, or undefined cells | Renders neutral dark slate background `rgba(22, 27, 34, 0.9)` and skips drawing text for invalid cells. |
| 8 | SSE Streaming Console | Optimization generates 100+ rapid log lines in < 1 second | DOM appends lines with `consoleLogs.appendChild(line)` and immediately sets `consoleLogs.scrollTop = consoleLogs.scrollHeight`, maintaining smooth 60fps auto-scroll without freezing the main thread. |
| 9 | SSE Stream Connection Failure | Server connection drops or returns HTTP 500 | `eventSource.onerror` catches error, invokes `eventSource.close()`, executes `cleanup()` (re-enabling button and restoring original label), and outputs red error in console. |
| 10 | Trade Markers | Multiple signals at identical timestamp or different directions | `buildChartMarkers` sorts by time and deduplicates using unique key `${s.time}_${s.direction}_${s.result}`, preventing overlapping duplicate badges. |
| 11 | Tooltip Hovering | Hovering over data point at rightmost or topmost edge of canvas | Chart.js tooltips use `caretPadding: 6`, `position: 'nearest'`, and boundaries clipping to keep tooltips within canvas viewport without overflowing parent containers. |

---

## 3. Detailed Specification Breakdown

### 3.1 Lightweight Charts v4 Harmonization
- **Canvas Background**: Solid `#080b11` (Canvas Obsidian) or `transparent` so the underlying `.chart-card.glass-card` background (`#0e1420`) shines through.
- **Grid Lines**:
  - `grid.vertLines.color: 'rgba(255, 255, 255, 0.03)'`
  - `grid.horzLines.color: 'rgba(255, 255, 255, 0.03)'`
- **Crosshair**:
  - `mode: LightweightCharts.CrosshairMode.Normal`
  - Crosshair line color: `rgba(56, 189, 248, 0.40)`
- **Candlestick Colors**:
  - Bullish / CALL: `upColor: '#10b981'`, `wickUpColor: '#10b981'` (*Cyber Emerald*)
  - Bearish / PUT: `downColor: '#f43f5e'`, `wickDownColor: '#f43f5e'` (*Rose Crimson*)
  - `borderVisible: false`
- **Scales & Typography**:
  - `timeScale.borderColor: 'rgba(255, 255, 255, 0.07)'`
  - `rightPriceScale.borderColor: 'rgba(255, 255, 255, 0.07)'`
  - `layout.textColor: '#94a3b8'`, `fontSize: 12`, `fontFamily: "'Inter', sans-serif"`
- **Trade Markers (`buildChartMarkers`)**:
  - CALL: `{ time, position: 'belowBar', color: '#10b981', shape: 'arrowUp', text: 'CALL @ <price>' }`
  - PUT: `{ time, position: 'aboveBar', color: '#f43f5e', shape: 'arrowDown', text: 'PUT @ <price>' }`
  - WIN (Exit): `{ time, position: (tradeDir === 'CALL' ? 'aboveBar' : 'belowBar'), color: '#10b981', shape: 'circle', text: 'WIN @ <price> (+<pnl>$)' }`
  - LOSS (Exit): `{ time, position: (tradeDir === 'CALL' ? 'belowBar' : 'aboveBar'), color: '#f43f5e', shape: 'circle', text: 'LOSS @ <price> (<pnl>$)' }`
- **Price Lines (`createPriceLine`)**:
  - Entry Line: `color: (dir === 'CALL' ? '#10b981' : '#f43f5e')`, `lineWidth: 1`, `lineStyle: Solid`
  - Exit Line: `color: (result === 'WIN' ? '#10b981' : '#f43f5e')`, `lineWidth: 2`, `lineStyle: Dotted`

### 3.2 Chart.js v4 Harmonization
- **Global Theme Defaults**:
  - `Chart.defaults.color = '#94a3b8'`
  - `Chart.defaults.font.family = "'Inter', sans-serif"`
  - `Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(20, 29, 46, 0.95)'` (`#141d2e` Elevated Surface)
  - `Chart.defaults.plugins.tooltip.titleColor = '#f0f6fc'`
  - `Chart.defaults.plugins.tooltip.bodyColor = '#f0f6fc'`
  - `Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.07)'`
  - `Chart.defaults.plugins.tooltip.borderWidth = 1`
  - `Chart.defaults.plugins.tooltip.cornerRadius = 6`
- **Equity Curve (`#equity-chart`, `#smart-equity-chart-canvas`)**:
  - Line color: `#38bdf8` (*Electric Sky*)
  - Fill: Linear Gradient `rgba(56, 189, 248, 0.18)` (top) to `rgba(56, 189, 248, 0.00)` (bottom)
  - Auto-Log Scale: `(maxVal / Math.max(minVal, 0.01)) > 100 && minVal >= 1.0`
  - Tick Formatter: `formatYAxisTick(value, useLog)` filtering sub-decade values and prefixing `$`, `k`, `M`.
- **Monte Carlo Probability Cones (`#mc-chart`, `#smart-mc-chart-canvas`)**:
  - P95: `borderColor: '#10b981'`, `borderDash: [5, 5]`, `borderWidth: 1.5`
  - P75: `borderColor: 'rgba(16, 185, 129, 0.45)'`, `borderWidth: 1.5`
  - P50 (Median): `borderColor: '#38bdf8'`, `borderWidth: 3`
  - P25: `borderColor: 'rgba(244, 63, 94, 0.45)'`, `borderWidth: 1.5`
  - P5: `borderColor: '#f43f5e'`, `borderDash: [5, 5]`, `borderWidth: 1.5`
  - Auto-Log Scale: `(maxVal / minVal) > 50 && minVal > 0.01`

### 3.3 Canvas 2D Correlation Heatmap
- **Retina Scaling**: `const dpr = window.devicePixelRatio || 1; canvas.width = width * dpr; canvas.height = height * dpr; ctx.scale(dpr, dpr);`
- **Grid Layout**: `leftMargin = 70px`, `topMargin = 15px`, `rightMargin = 15px`, `bottomMargin = 35px`.
- **Cell Gaps**: `ctx.fillRect(x, y, cellW - 1.5, cellH - 1.5)` for clean 1.5px separation.
- **Color Mapping**:
  - $r < 0$ (Diversified): Interpolate `#0e1420` -> `#38bdf8` / `#10b981`
  - $r > 0$ (Concentrated Risk): Interpolate `#0e1420` -> `#f43f5e`
  - $r = 0$: `#0e1420`
- **Typography**: In-cell values with `font: bold {size}px 'JetBrains Mono', monospace`, `font-variant-numeric: tabular-nums`, `#f0f6fc` when $|r| > 0.40$. Axis tickers in `#94a3b8`.

### 3.4 Micro-Interactions & Transitions
- **Motion Tokens**: `--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1)`, `--duration-micro: 120ms`, `--duration-state: 180ms`, `--duration-reveal: 240ms`.
- **Button Loading State**: `btn.disabled = true`, `btn.style.opacity = '0.7'`, `cursor: not-allowed`, text: `⏳ Optimizando (X%)...`, `.loading-spinner.active` spinning at 0.8s.
- **SSE Telemetry Console**: `#smart-console-box`, `#smart-console-logs` with auto-scroll `scrollTop = scrollHeight`, semantic classes `.info` (`#38bdf8`), `.success` (`#10b981`), `.error` (`#f43f5e`), `.warning` (`#f59e0b`).
- **Animations**:
  - Live pulse: `@keyframes livePulse 2s infinite ease-in-out` (scale 1 <-> 0.85, opacity 1 <-> 0.35).
  - Shimmer progress: `@keyframes progressShimmer 2s linear infinite` across purple-blue-green gradient.
- **Interactive Elevations**: `.top-strat-pill:hover` (`translateY(-1px)`), `.ladder-step:hover` (`translateX(3px)`), `.stat-card:hover` (`translateY(-1px)`).
