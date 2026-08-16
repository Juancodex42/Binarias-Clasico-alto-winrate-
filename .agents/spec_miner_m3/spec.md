# SPECIFICATION — MILESTONE 3: CHARTING ENGINE HARMONIZATION & MICRO-INTERACTIONS

## 1. Overview & Scope
Milestone 3 defines the visual harmonization, rendering precision, and dynamic micro-interactions across all charting engines in the Binary Options Quantitative Terminal:
- **TradingView Lightweight Charts v4**: Candlestick price action, live WebSocket/polling updates, and CALL/PUT entry/exit markers.
- **Chart.js v4**: Barbell equity curves with dynamic log-scaling, Monte Carlo stochastic cones (P5–P95), and statistical diagnostics (Autocorrelation, Streaks, Hourly Win Rate, Market State, G(N) Growth Rate).
- **HTML5 Canvas 2D**: Retina high-DPI cross-asset correlation matrix heatmap ($N \times N$).
- **Micro-Interactions & Physics**: 120ms–180ms ease transitions, shimmer progress bars, pulse indicators, and responsive resize handling.

---

## 2. Authoritative Specification Sources
1. `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md` (§2, §3, §4, §5, §6, §7, §9)
2. `ORIGINAL_REQUEST.md` (Requirements R1, R2, R3, R4, R5)
3. `PROJECT.md` (Architecture, Feature Inventory #12, #13, #14, #15, Milestone 3 scope)
4. `static/css/style.css` (Design tokens, animations, variables, layout classes)
5. `static/js/charts.js` (Current chart implementations & wrappers)
6. `static/js/app.js` (UI event listeners, SSE feeds, WebSocket stream, marker builders)
7. `templates/index.html` (DOM hierarchy, canvas elements, modal boxes, overlays)

---

## 3. Detailed Specification Requirements

### 3.1 Exact Visual Tokens, Palettes & Dimensions

#### A. Global FinTech Slate & Obsidian Palette
| Token Name | CSS Variable | Hex / RGBA Value | Role & Usage |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | `--bg-canvas` | `#080b11` | Window background, zero-contrast foundation |
| **Surface Card Base** | `--bg-card` | `#0e1420` | Card bodies, chart backgrounds, sub-panels |
| **Surface Elevated** | `--bg-elevated` | `#141d2e` | Headers, toolbars, chart tooltips, dialogs |
| **Surface Hover / Input** | `--bg-hover` | `#1c273d` | Form controls, select dropdowns, hover rows |
| **Border Subtle** | `--border-subtle` | `rgba(255, 255, 255, 0.07)` | 1px perimeters, chart axes, card borders |
| **Border Focus / Glow** | `--border-focus` | `rgba(56, 189, 248, 0.35)` | Active chart card focus, input highlights |
| **Grid Lines (Subtle)** | `--grid-lines` | `rgba(255, 255, 255, 0.03)` | Lightweight Charts & Chart.js axis grids |
| **Text Primary** | `--text-primary` | `#f0f6fc` | Active labels, tooltip headers, key metrics |
| **Text Secondary** | `--text-secondary` | `#94a3b8` | Chart axes tick labels, subtitles, units |
| **Text Muted** | `--text-muted` | `#64748b` | Coordinate crosshairs, timestamps |

#### B. Calibrated Semantic Accents (Anti-Halation & Anti-Chromostereopsis)
| Semantic Role | Token Variable | Hex Value | RGBA Value | Usage in Charts |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Action / Focus** | `--accent-primary` | `#38bdf8` | `rgba(56, 189, 248, 1.0)` | Equity Curve line, Median P50 line, Active UI |
| **CALL / Win / P95** | `--accent-green` | `#10b981` | `rgba(16, 185, 129, 1.0)` | Bullish candles, CALL arrows, P95/P75 cones, WIN dots |
| **PUT / Loss / P5** | `--accent-red` | `#f43f5e` | `rgba(244, 63, 94, 1.0)` | Bearish candles, PUT arrows, P5/P25 cones, LOSS dots |
| **Optimization / Gen** | `--accent-purple` | `#a855f7` | `rgba(168, 85, 247, 1.0)` | Autocorrelation bar chart, Shimmer gradient start |
| **Balas / Amber** | `--accent-amber` | `#f59e0b` | `rgba(245, 158, 11, 1.0)` | Warning states, Paroli ladder highlights |
| **Cool Slate Grid** | `--accent-slate` | `#64748b` | `rgba(100, 116, 139, 0.12)` | Chart scale dividers, inactive axes |

#### C. Lightweight Charts Configuration (`createCandlestickChart`)
```javascript
{
    layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: '#94a3b8',
        fontSize: 12,
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    },
    grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.03)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.03)' }
    },
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
        vertLine: { color: 'rgba(56, 189, 248, 0.4)', style: 3, labelBackgroundColor: '#141d2e' },
        horzLine: { color: 'rgba(56, 189, 248, 0.4)', style: 3, labelBackgroundColor: '#141d2e' }
    },
    timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: 'rgba(255, 255, 255, 0.07)',
        rightOffset: 10,
        barSpacing: 10,
        minBarSpacing: 0.5,
        autoScale: true,
        shiftVisibleRangeOnNewBar: true
    },
    rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.07)',
        autoScale: true,
        scaleMargins: { top: 0.1, bottom: 0.1 }
    }
}
```
- **Candlestick Series**:
  - `upColor`: `#10b981` (Cyber Emerald)
  - `downColor`: `#f43f5e` (Rose Crimson)
  - `borderVisible`: `false`
  - `wickUpColor`: `#10b981`
  - `wickDownColor`: `#f43f5e`
  - `priceFormat`: `{ type: 'price', precision: 5, minMove: 0.00001 }`

#### D. Chart.js v4 Global Configuration & Tooltips
- **Global Defaults**:
  - `Chart.defaults.color = '#94a3b8'`
  - `Chart.defaults.font.family = "'Inter', system-ui, sans-serif"`
  - `Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(20, 29, 46, 0.95)'` (`--bg-elevated`)
  - `Chart.defaults.plugins.tooltip.titleColor = '#f0f6fc'`
  - `Chart.defaults.plugins.tooltip.bodyColor = '#94a3b8'`
  - `Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.08)'`
  - `Chart.defaults.plugins.tooltip.borderWidth = 1`
  - `Chart.defaults.plugins.tooltip.padding = 10`
  - `Chart.defaults.plugins.tooltip.cornerRadius = 6`
  - `Chart.defaults.plugins.tooltip.titleFont = { size: 11, weight: '600', family: "'JetBrains Mono', monospace" }`
  - `Chart.defaults.plugins.tooltip.bodyFont = { size: 11, family: "'JetBrains Mono', monospace" }`

#### E. Chart.js Equity Curve (`createEquityCurve`)
- **Dataset Configuration**:
  - `borderColor`: `#38bdf8` (Electric Sky)
  - `backgroundColor`: Linear gradient on Canvas Context from `rgba(56, 189, 248, 0.25)` at $y=0$ to `rgba(56, 189, 248, 0.00)` at $y=height$
  - `borderWidth`: `2`
  - `fill`: `true`
  - `tension`: `0.15`
  - `pointRadius`: `0`
  - `pointHoverRadius`: `4`
  - `pointHoverBackgroundColor`: `#38bdf8`
  - `pointHoverBorderColor`: `#ffffff`
  - `pointHoverBorderWidth`: `2`
- **Dynamic Logarithmic Scaling**:
  - Automatically activates `type: 'logarithmic'` if $\frac{\text{maxVal}}{\max(\text{minVal}, 0.01)} > 100$ and $\text{minVal} \ge 1.0$.
  - Y-axis min: `Math.max(1, Math.pow(10, Math.floor(Math.log10(Math.max(minVal, 1)))))`.
- **Y-Axis Tick Formatter (`formatYAxisTick`)**:
  - Tabular prefix `$`, compact units: $\ge 1\text{M} \rightarrow \$1.2\text{M}$, $\ge 1\text{k} \rightarrow \$50.5\text{k}$, $< 1\text{k} \rightarrow \$100.00$.
  - Negative prefix `-$` (e.g. `-$25.00`).
  - In log mode, filters intermediate non-decade sub-ticks ($\log_{10}(v) \notin \mathbb{Z}$) to prevent label collisions.

#### F. Chart.js Monte Carlo Stochastic Cones (`createMonteCarloChart`)
- **5 Percentile Bands**:
  1. **P95 (Top 5% Best Case)**: `borderColor: 'rgba(16, 185, 129, 0.85)'`, `borderDash: [5, 5]`, `borderWidth: 1.5`, `fill: false`
  2. **P75 (Upper Quartile)**: `borderColor: 'rgba(16, 185, 129, 0.45)'`, `borderWidth: 1`, `fill: false`
  3. **P50 (Median)**: `borderColor: '#38bdf8'`, `borderWidth: 2.5`, `fill: false`
  4. **P25 (Lower Quartile)**: `borderColor: 'rgba(244, 63, 94, 0.45)'`, `borderWidth: 1`, `fill: false`
  5. **P5 (Risk Tail 5%)**: `borderColor: 'rgba(244, 63, 94, 0.85)'`, `borderDash: [5, 5]`, `borderWidth: 1.5`, `fill: false`
- **Logarithmic protection**: Clean array values $\le 0.01 \rightarrow 0.01$ to avoid $\log(0) = -\infty$.

#### G. Canvas 2D Correlation Matrix Heatmap (`createCorrelationHeatmap`)
- **Container**: Canvas element `#smart-correlation-canvas` (height 290px, width 100%).
- **High-DPI Retina Scaling**:
  ```javascript
  const dpr = window.devicePixelRatio || 1;
  canvas.width = (width || 400) * dpr;
  canvas.height = (height || 280) * dpr;
  ctx.scale(dpr, dpr);
  ```
- **Layout & Margins**:
  - `leftMargin`: `70px` (y-axis asset tickers)
  - `topMargin`: `15px`
  - `rightMargin`: `15px`
  - `bottomMargin`: `35px` (x-axis asset tickers)
  - `cellGap`: `1.5px`
- **Color Interpolation (Anti-Halation Smooth Gradient)**:
  - Base neutral (no correlation / zero): `#0e1420` (RGB: 14, 20, 32)
  - Positive correlation ($r > 0$): Interpolate to Rose Crimson `#f43f5e` (RGB: 244, 63, 94) for high cross-asset risk / collinearity, or Cyber Emerald `#10b981` (RGB: 16, 185, 129) for diversification. Formula: $I = |r|^{1.2}$, $R = \text{round}(14 + I \cdot (244 - 14))$, $G = \text{round}(20 + I \cdot (63 - 20))$, $B = \text{round}(32 + I \cdot (94 - 32))$.
  - Negative correlation ($r < 0$): Interpolate to Electric Sky `#38bdf8` (RGB: 56, 189, 248).
- **Cell Text & Typography**:
  - Value: `r.toFixed(2)`
  - Font: `bold ${fontSize}px "JetBrains Mono", Inter, sans-serif`
  - Color: `#f0f6fc` if $|r| > 0.40$, else `#94a3b8`
  - Tickers: Strip `USDT` and `=X` suffixes (e.g. `BTCUSDT` $\rightarrow$ `BTC`, `EURUSD=X` $\rightarrow$ `EURUSD`), font `bold ${labelFontSize}px Inter, sans-serif`, color `#94a3b8`.

---

### 3.2 Signal Markers Specification (CALL, PUT, EXIT)

#### A. Signal Marker Attributes
| Signal Type | Marker Shape | Position | Color (Hex) | Text Formatting | Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CALL Entry** | `'arrowUp'` | `'belowBar'` | `#10b981` | `CALL @ <entry_price>` | Algorithmic buy signal |
| **PUT Entry** | `'arrowDown'` | `'aboveBar'` | `#f43f5e` | `PUT @ <entry_price>` | Algorithmic sell signal |
| **EXIT (CALL WIN)** | `'circle'` | `'aboveBar'` | `#10b981` | `WIN @ <exit_price> (+<pnl>$)` | Expiry close > entry close |
| **EXIT (CALL LOSS)**| `'circle'` | `'belowBar'` | `#f43f5e` | `LOSS @ <exit_price> (<pnl>$)` | Expiry close $\le$ entry close |
| **EXIT (PUT WIN)** | `'circle'` | `'belowBar'` | `#10b981` | `WIN @ <exit_price> (+<pnl>$)` | Expiry close < entry close |
| **EXIT (PUT LOSS)** | `'circle'` | `'aboveBar'` | `#f43f5e` | `LOSS @ <exit_price> (<pnl>$)` | Expiry close $\ge$ entry close |

#### B. Marker Deduplication & Sorting
- Markers must be sorted strictly ascending by timestamp: `signals.sort((a, b) => a.time - b.time)`.
- Unique key per marker: `${s.time}_${s.direction}_${s.result || ''}` tracked via `Set()` to eliminate duplicate overlay markers on rapid updates.
- Number formatting: prices formatted with `formatPrice(price)` (5 decimal places for forex/sub-dollar crypto, 2 decimal places for major assets).

---

### 3.3 Micro-Interactions, Motion Tokens & Physics

#### A. Motion Tokens
- **Standard Acceleration Curve**: `cubic-bezier(0.16, 1, 0.3, 1)` (`--ease-out-expo`)
- **Micro-interactions (Hover, Focus, Clicks)**: `100ms - 150ms` (`--duration-micro: 120ms`)
- **State Transitions (Tabs, Panels, Mode Switcher)**: `180ms - 220ms` (`--duration-state: 180ms`)
- **Reveal / Overlay Transitions (Modals, Tooltips)**: `200ms - 240ms` (`--duration-reveal: 240ms`)

#### B. Shimmer Effect on Progress Bars
- Containers: `.smart-progress-bar-fill`, `.progress-bar-fill`, `#streak-progress-fill`
- Gradient: `linear-gradient(90deg, #a855f7 0%, #38bdf8 50%, #10b981 100%)`
- Size: `background-size: 200% 100%`
- Animation: `animation: progressShimmer 2s linear infinite`
- Keyframes:
  ```css
  @keyframes progressShimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
  }
  ```

#### C. Live Streaming Pulse Indicator
- Selector: `.pulse-dot`
- Color: `#10b981` (Cyber Emerald)
- Animation: `animation: livePulse 2s infinite ease-in-out`
- Keyframes:
  ```css
  @keyframes livePulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.35; transform: scale(0.85); }
  }
  ```

#### D. Interactive Top Strategy Ranking Pills
- Selector: `.top-strat-pill`
- Base state: `background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.07);`
- Hover state: `transform: translateY(-1px); border-color: rgba(56, 189, 248, 0.35); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);`
- Active state: `background: rgba(168, 85, 247, 0.20); border-color: #a855f7; box-shadow: 0 0 12px rgba(168, 85, 247, 0.25);`

#### E. Chart Responsive Auto-Refit
- Observer: `ResizeObserver` attached to `#tv-chart`, `#smart-tv-chart`, and container wrappers.
- Handler: `chartInstance.applyOptions({ width: rect.width, height: rect.height });` followed by `chartInstance.timeScale().fitContent()`.
- Debounced tab-switch refit: `setTimeout(..., 50)` on `switchTab(tabId)`.

---

### 3.4 Error State Handling, Empty Overlays & Fallbacks

#### A. Empty Chart Overlays
- **Smart TV Chart Empty State** (`#smart-tv-chart-empty`):
  - Position: Absolute cover `inset: 0`, `z-index: 10`, `background: var(--bg-card)`.
  - Icon & Message: `📈 Ejecuta la optimización inteligente para visualizar velas y señales CALL/PUT`.
  - Display toggle: `display: flex` before execution; `display: none` once candle data loads.

#### B. Correlation Matrix Fallback
- Condition: `!matrix || matrix.length === 0 || !labels || labels.length === 0`
- Canvas output: Clear canvas, render centered text `Sin datos de correlación` at $(w/2, h/2)$ with font `13px Inter` and color `#94a3b8`.

#### C. Equity Curve & Monte Carlo Fallbacks
- Missing or empty points: Render clean baseline `$0.00` or `$1000.00` without throwing JavaScript exceptions.
- Zero/Negative clamping: `Math.max(v, 0.01)` to prevent $\log(0)$ breakdown in logarithmic scales.

#### D. Live WebSocket Disconnection & Polling Fallback
- On WebSocket failure/close (`liveWs.onerror`, `liveWs.onclose`):
  - Check `#source-selector.value === 'live'`.
  - Trigger `startFallbackPolling(pair, interval)` executing REST GET to `https://api.binance.com/api/v3/klines` every 3000ms.
  - Update telemetry badge text: `En Vivo (Polling)` with active `.pulse-dot`.

#### E. Loading Spinner
- Element: `.loading-spinner` / `#chart-loader`
- CSS: Centered circular loader `border: 3px solid rgba(255, 255, 255, 0.08); border-top-color: #38bdf8; border-radius: 50%; animation: spin 0.8s linear infinite;`

---

### 3.5 Invariant UI Event Hooks & API Contract

#### A. Global Window Export Hooks
- `window.togglePineScriptModal(id)`: Toggles visibility of `#pinescript-box-${id}`.
- `window.copyPineScript(id)`: Copies contents of `#pinescript-code-${id}` to clipboard.
- `window.copyAIPrompt(id)`: Copies structured prompt from `#ai-prompt-${id}` to clipboard.

#### B. Chart Interface Functions (`charts.js`)
- `createCandlestickChart(containerId)` $\rightarrow$ returns `{ chart, candleSeries }`
- `addSignalMarkers(series, signals)` / `buildChartMarkers(signals)` $\rightarrow$ returns structured marker array
- `createEquityCurve(canvasId, equityPoints, rawLabels)`
- `createMonteCarloChart(canvasId, labels, percentiles)`
- `createCorrelationHeatmap(canvasId, matrix, labels)`
- `createBarChart(canvasId, labels, values, title, color)`
- `createGrowthRateChart(canvasId, ns, g_values, optimal_n)`
- `formatYAxisTick(value, useLog)` $\rightarrow$ returns formatted string

#### C. Backend API Contracts
- `GET /api/data/pairs` $\rightarrow$ `{ pairs: [...], intervals: [...] }`
- `GET /api/data/candles?pair={p}&interval={i}&limit={l}` $\rightarrow$ `{ candles: [{time, open, high, low, close, volume}, ...] }`
- `GET /api/strategies` $\rightarrow$ `{ strategies: [...] }`
- `GET /api/backtest-stream?...` $\rightarrow$ SSE stream of progress and final `{ summary, stats, signals, equity_curve }`
- `GET /api/smart-optimize-v2-stream?...` $\rightarrow$ SSE stream emitting genetic iterations, top strategies, correlation matrix, Markov matrix, Monte Carlo paths.
- `POST /api/optimize-streak` $\rightarrow$ `{ best_n, bet_ladder, final_capital, prob_duplication_pct, ... }`
- `POST /api/montecarlo` $\rightarrow$ `{ percentiles: { p95, p75, p50, p25, p5 }, labels: [...] }`

---

## 4. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Charting Tokens | Lightweight Charts Dark Obsidian Theme | Transparent canvas background with subtle grid lines (<0.04 opacity) and slate borders | Container ID, DOM size | Configured IChartApi instance | Falls back to default container dims if parent rect is 0 | GUIA_MAESTRA §4.1, charts.js |
| 2 | Charting Tokens | Cyber Emerald & Rose Crimson Candlesticks | Non-halating green (`#10b981`) and red (`#f43f5e`) candles with precision 5 pricing | Clean candle array `[{time, open, high, low, close, volume}]` | Rendered candlestick series | Ignores NaN prices and duplicate timestamps | GUIA_MAESTRA §4.3, charts.js |
| 3 | Signal Markers | CALL & PUT Signal Badges | Visual entry markers on candles with price formatted to tabular precision | Signals array `[{time, direction: 'CALL'/'PUT', entry_price}]` | Arrow markers (Up/Green, Down/Red) | Skips invalid timestamps or missing directions | GUIA_MAESTRA §6.1, app.js |
| 4 | Signal Markers | Dynamic WIN / LOSS Resolution Dots | Circle markers positioned on favorable/unfavorable side based on trade outcome | Signals array with `{direction: 'EXIT', result: 'WIN'/'LOSS', pnl}` | Green/Red circles with PnL and exit price text | Deduplicates overlapping keys via Set | app.js:415, charts.js:75 |
| 5 | Chart.js Curve | Auto-Logarithmic Equity Curve | Capital growth curve with glowing Electric Sky (`#38bdf8`) area gradient and auto-log scaling | Equity point array or `{equity, time}` objects | Line chart on HTML5 Canvas | Clamps values to $\ge 1.0$ if log scale active to prevent $-\infty$ | GUIA_MAESTRA §6.2, charts.js:119 |
| 6 | Chart.js Cones | 5-Band Monte Carlo Stochastic Cones | P5, P25, Median (P50), P75, P95 probabilistic trajectories for capital stress-testing | Percentile object `{p95, p75, p50, p25, p5}` | Multi-dataset line chart with dashed bounds | Clamps $\le 0.01$ to $0.01$ to avoid $\log(0)$ crash | GUIA_MAESTRA §6.2, charts.js:290 |
| 7 | Canvas 2D | High-DPI Cross-Asset Correlation Heatmap | Retina 2D Canvas rendering $N \times N$ correlation matrix with continuous slate-to-crimson/emerald gradient | Matrix 2D array, Ticker labels list | High-DPI Canvas heatmap with tabular numeric text | Renders "Sin datos de correlación" if matrix is empty | GUIA_MAESTRA §6.3, charts.js:377 |
| 8 | Chart.js Diagnostics | Multi-Metric Diagnostic Bar Charts | Autocorrelation, Streak Frequency, Hourly Win Rate, Market State, and G(N) Growth Rate | Numeric labels, value arrays, title, accent color | Bar chart instance on Canvas | Replaces and destroys previous chart instance safely | charts.js:236, app.js:1139 |
| 9 | Micro-Interactions | Motion Tokens & Physics Easing | Sub-200ms transitions with `cubic-bezier(0.16, 1, 0.3, 1)` on hover, focus, and panel expansion | CSS transitions | Smooth visual state changes | Degrades gracefully without JS intervention | GUIA_MAESTRA §7.1, style.css |
| 10 | Micro-Interactions | Shimmer Progress Bar Animation | Multi-color animated gradient shimmer during genetic optimization and backtests | Progress percentage (0-100%) | Continuous 2s linear horizontal shimmer | Stops and hides container upon completion/error | GUIA_MAESTRA §7.1, style.css:768 |
| 11 | Micro-Interactions | Real-Time WebSocket Pulse Indicator | Breathing pulse dot confirming live Binance market tick ingestion | Live stream active state boolean | Pulsing green dot with status pill text | Reverts to polling badge or hidden upon stream close | GUIA_MAESTRA §7.1, app.js:269, style.css:1506 |
| 12 | Micro-Interactions | Strategy Ranking Pill Micro-Elevations | Top-5 strategy pills with $1\text{px}$ elevation on hover and purple active halo | Click / hover user interaction | Visual feedback & dynamic strategy view load | Disables interaction if no strategies found | GUIA_MAESTRA §2.5, app.js:2426 |
| 13 | Fallback / Error | Smart Mode Empty Chart Overlay | Initial placeholder overlay with instructions for the TradingView canvas | Execution trigger state | Hidden overlay upon first candle batch load | Restored if clear history or reset occurs | index.html:350, style.css:1449 |
| 14 | Fallback / Error | WebSocket to REST Polling Fallback | Automatic fallback to Binance public REST klines endpoint if WebSocket disconnects | WebSocket error/close event | Continuous 3000ms polling feed | Cleans up interval timer when switching source | app.js:361, app.js:380 |
| 15 | API Hooks | Pine Script v5 & AI Prompt Export Dialogs | Modals with auto-generated Pine Script indicators and LLM prompt specifications | Strategy object & best genome parameters | Formatted Pine Script v5 / AI text | Displays default generic strategy schema if genome is empty | app.js:19, app.js:146, app.js:2177 |

---

## 5. Edge Cases & Boundary Behaviors

| # | Feature | Input / Condition | Observed / Required Behavior |
|---|---------|-------------------|-----------------------------|
| 1 | Equity Curve | All trades lose (Equity drops to $0.00) | In logarithmic mode, values clamped to $\ge 1.0$; in linear mode, Y-axis shows negative ticks with `-$` prefix without crashing. |
| 2 | Monte Carlo Cones | Percentile array contains 0 or negative values | `clean(arr)` replaces values $\le 0.01$ with $0.01$; chart renders cleanly without $-\infty$ axis stretching. |
| 3 | Correlation Heatmap | Empty correlation matrix (`matrix = []`) | Canvas clears and displays centered `#94a3b8` text `"Sin datos de correlación"`. |
| 4 | Correlation Heatmap | Collapsed container dimensions (`clientWidth = 0`) | Falls back to default $400 \times 280\text{px}$ scaled by `window.devicePixelRatio`. |
| 5 | Candlestick Chart | Zero or 1 candle returned from API | Lightweight Charts handles 0/1 candle without error; does not crash `timeScale().fitContent()`. |
| 6 | Candlestick Chart | Duplicate timestamps in candle series | `prepareCandles()` filters out candles with $t_i == t_{i-1}$ ensuring strict monotonic time order. |
| 7 | Signal Markers | Simultaneous CALL and EXIT on same bar | Deduplicated via unique key `${time}_${direction}_${result}`; both render cleanly above/below bar without collisions. |
| 8 | Live WebSocket Stream | Network disconnects while in Live mode | `liveWs.onerror` triggers `startFallbackPolling()` polling `/api/v3/klines` every 3s and badge updates to `En Vivo (Polling)`. |
| 9 | Tab Switching | User switches from Backtest to Dashboard while chart is hidden | `switchTab()` runs `ResizeObserver` and debounced 50ms refit calling `chart.applyOptions({width, height})` and `timeScale().fitContent()`. |
| 10 | Pine Script / AI Prompt Modal | Strategy has no custom hyperparameters | Generates robust default Pine Script v5 with fallback parameter schemas (RSI 14, BB 20, 2.0σ). |
