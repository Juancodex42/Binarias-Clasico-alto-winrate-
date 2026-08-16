# In-Depth Code-Level Analysis: Charting Engine & Visualizations (Milestone 3)
**Author**: `explorer_charts_m3` (Teamwork Preview Explorer)  
**Date**: 2026-08-16  
**Target Files**: `static/js/charts.js`, `static/js/app.js`, `templates/index.html`, `static/css/style.css`  
**Reference Standard**: `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`

---

## 1. Executive Summary

The Quantitative Binary Options Terminal relies on a hybrid multi-layer charting architecture composed of:
1. **TradingView Lightweight Charts v4**: For high-performance interactive Japanese candlestick rendering, live price tracking, and discrete CALL / PUT / EXIT signal markers.
2. **Chart.js v4**: For statistical distribution and risk analysis, including cumulative equity curves (with dynamic linear/logarithmic switching), 5,000-path Monte Carlo probability cones (P5–P95), and multi-dimensional diagnostic histograms.
3. **HTML5 2D Canvas**: For high-DPI Retina cross-asset return correlation matrices.

This analysis maps all existing chart entities, evaluates their implementation mechanics, identifies visual and functional divergences against the institutional design specification (`GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`), and presents a concrete, zero-regression implementation plan for the Milestone 3 Worker.

---

## 2. Comprehensive Inventory & Map of Chart Entities

### 2.1 Functions in `static/js/charts.js`

| Function Signature | Target DOM Element(s) | Primary Technology | Purpose & Mechanism |
|---|---|---|---|
| `createCandlestickChart(containerId)` | `#tv-chart`, `#smart-tv-chart` | Lightweight Charts v4 | Instantiates candlestick chart with dark transparent background, crosshairs, time/price scales, and scroll/zoom interactions. Returns `{ chart, candleSeries }`. |
| `addSignalMarkers(series, signals)` | Lightweight Candlestick Series | Lightweight Charts v4 | Attaches execution markers to candle bars. Calls `buildChartMarkers()` if available, otherwise maps simple arrows. |
| `formatYAxisTick(value, useLog)` | Chart.js Y-Axis callbacks | Vanilla JS | Formats currency values ($0, $1k, $1.5M, -$50). In log scale, suppresses intermediate sub-ticks to prevent label collisions. |
| `createEquityCurve(canvasId, equityPoints, rawLabels)` | `#equity-chart`, `#smart-equity-chart-canvas` | Chart.js v4 (Line) | Renders cumulative account equity. Automatically toggles between linear and logarithmic scale if $\frac{\text{max}}{\text{min}} > 100$. Parses timestamps into `YYYY-MM-DD HH:mm`. |
| `createBarChart(canvasId, labels, values, title, color)` | `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#market-state-chart`, `#kelly-chart` | Chart.js v4 (Bar) | Renders discrete diagnostic histograms with custom bar colors and 4px border radius. |
| `createGrowthRateChart(canvasId, ns, g_values, optimal_n)` | `#gn-chart` | Chart.js v4 (Bar) | Renders Paroli growth rate $G(N)$ across streak lengths, highlighting $N_{\text{optimal}}$ in green vs blue. |
| `createMonteCarloChart(canvasId, labels, percentiles)` | `#mc-chart`, `#smart-mc-chart-canvas` | Chart.js v4 (Multi-Line) | Renders 5 percentile trajectory curves (P95, P75, P50 Median, P25, P5) with auto-log scale detection. |
| `createCorrelationHeatmap(canvasId, matrix, labels)` | `#smart-correlation-canvas` | HTML5 2D Canvas API | Renders a High-DPI cross-asset correlation matrix grid with non-linear color interpolation and numeric overlays. |

### 2.2 Global Chart.js Defaults in `charts.js`

```javascript
Chart.defaults.color = '#8b949e';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(22, 27, 34, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#c9d1d9';
Chart.defaults.plugins.tooltip.bodyColor = '#c9d1d9';
Chart.defaults.plugins.tooltip.borderColor = '#30363d';
Chart.defaults.plugins.tooltip.borderWidth = 1;
```

### 2.3 Chart Containers in `templates/index.html`

```
templates/index.html
├── Smart Mode Workspace (#smart-dashboard)
│   ├── #smart-equity-chart-canvas (canvas, inside .chart-wrapper) -> Equity Curve
│   ├── #smart-mc-chart-canvas (canvas, inside .chart-wrapper) -> Monte Carlo Cones
│   ├── #smart-tv-chart (div, .chart-container) -> Lightweight Candlesticks
│   │   └── #smart-tv-chart-empty (overlay placeholder)
│   └── #smart-correlation-canvas (canvas) -> 2D Correlation Heatmap
└── Advanced Mode Workspace (#dashboard & sub-panes)
    ├── #tv-chart (div, .chart-container, inside #mercado tab) -> Lightweight Candlesticks
    │   └── #chart-loader (.loading-spinner)
    ├── #equity-chart (canvas, inside #resultados tab) -> Backtest Equity Curve
    ├── #autocorr-chart (canvas, inside #estadisticas tab) -> Autocorrelation Lags
    ├── #streaks-chart (canvas, inside #estadisticas tab) -> Streak Frequencies
    ├── #hourly-chart (canvas, inside #estadisticas tab) -> Hourly Win Rate
    ├── #cond-probs (div, .cond-probs-grid, inside #estadisticas tab) -> 2x2 DOM Matrix
    ├── #market-state-chart (canvas, inside #estadisticas tab) -> Volatility / Regime WR
    ├── #gn-chart (canvas, inside #optimizador tab) -> Paroli G(N) Growth
    ├── #kelly-chart (canvas, inside #optimizador tab) -> Kelly Fraction
    └── #mc-chart (canvas, inside #optimizador tab) -> 5,000-Path Monte Carlo Cones
```

---

## 3. Lightweight Charts Architecture & Analysis

### 3.1 Dual-Mode Instantiation (`#tv-chart` vs `#smart-tv-chart`)

Lightweight Charts instances are initialized during `initApp()` in `static/js/app.js`:
- **Advanced Mode**:
  ```javascript
  const chartObj = createCandlestickChart('tv-chart');
  mainChart = chartObj.chart;
  candleSeries = chartObj.candleSeries;
  ```
- **Smart Mode**:
  ```javascript
  const smartChartObj = createCandlestickChart('smart-tv-chart');
  smartChart = smartChartObj.chart;
  smartCandleSeries = smartChartObj.candleSeries;
  ```

### 3.2 Current Configuration Options

- **Layout**: Solid transparent background, font family `'Inter', system-ui, -apple-system, sans-serif`, text color `#8b949e`.
- **Grid**: Horizontal and vertical grid lines set to `rgba(48, 54, 61, 0.3)`.
- **Crosshair**: `LightweightCharts.CrosshairMode.Normal`.
- **TimeScale**: `timeVisible: true`, `secondsVisible: false`, `borderColor: '#30363d'`, `rightOffset: 10`, `barSpacing: 10`, `minBarSpacing: 0.5`, `shiftVisibleRangeOnNewBar: true`.
- **RightPriceScale**: `borderColor: '#30363d'`, `autoScale: true`, `scaleMargins: { top: 0.1, bottom: 0.1 }`.
- **Series Configuration**:
  - `upColor: '#00f5a0'`, `downColor: '#ff4d4d'`
  - `wickUpColor: '#00f5a0'`, `wickDownColor: '#ff4d4d'`
  - `borderVisible: false`
  - `priceFormat: { type: 'price', precision: 5, minMove: 0.00001 }`

### 3.3 Dynamic Markers & Trade Lines

1. **Signal Markers (`buildChartMarkers`)**:
   - `CALL`: Shape `arrowUp`, color `#00f5a0` (neon mint), position `belowBar`.
   - `PUT`: Shape `arrowDown`, color `#ff4d4d` (neon red), position `aboveBar`.
   - `EXIT`: Shape `circle`, color `#00f5a0` for WIN, `#ff4d4d` for LOSS. Dynamic positioning (favorable vs unfavorable side).
2. **Price Lines (`highlightTradeOnChart`)**:
   - Entry line: `createPriceLine({ lineWidth: 2, lineStyle: Dashed, color: CALL ? '#00f5a0' : '#ff4d4d' })`.
   - Exit line: `createPriceLine({ lineWidth: 2, lineStyle: Dotted, color: WIN ? '#00f5a0' : '#ff4d4d' })`.

### 3.4 Responsive Resize & Tab Synchronization

- **ResizeObserver**: Attached to both `#tv-chart` and `#smart-tv-chart` containers in `app.js` (lines 506-521).
- **Tab Switching (`switchTab`)**: Invokes a 50ms delayed resize trigger:
  ```javascript
  targetChart.applyOptions({ width: el.clientWidth, height: el.clientHeight });
  targetChart.timeScale().fitContent();
  ```
- **Empty Overlay**: `#smart-tv-chart-empty` is hidden dynamically via `style.display = 'none'` when candles for the selected smart asset are loaded.

---

## 4. Chart.js Instances & Diagnostic Renderers

### 4.1 Equity Curve (`createEquityCurve`)

- **Rendering Mode**: `type: 'line'`, single dataset with `fill: true`, `tension: 0.1`, `pointRadius: 0`, `pointHoverRadius: 4`.
- **Current Colors**: Border `#58a6ff`, Background `rgba(88, 166, 255, 0.12)`.
- **Logarithmic vs Linear Scale**:
  - Automatically calculates $\frac{\max(V)}{\max(\min(V), 0.01)}$. If ratio $> 100$ and $\min(V) \ge 1.0$, sets `type: 'logarithmic'`.
  - In log mode, filters out non-decade ticks in `formatYAxisTick()` ($1, $10, $100, $1k, $10k, $100k, $1M) to prevent tick label collisions.
- **X-Axis Timestamps**: Auto-formats Unix epoch seconds or milliseconds into `YYYY-MM-DD HH:mm`. Falls back to `#1, #2...` if timestamps are absent.

### 4.2 Monte Carlo Cones (`createMonteCarloChart`)

- **Rendering Mode**: `type: 'line'`, 5 datasets representing probabilistic quantiles:
  - **P95** (Upper Optimistic): `borderDash: [5, 5]`, current color `rgba(63, 185, 80, 0.8)`.
  - **P75** (Upper Moderate): Solid line, current color `rgba(63, 185, 80, 0.4)`.
  - **P50** (Median Expected): Solid line with `borderWidth: 3`, current color `#58a6ff`.
  - **P25** (Lower Moderate): Solid line, current color `rgba(248, 81, 73, 0.4)`.
  - **P5** (Worst-Case VaR): `borderDash: [5, 5]`, current color `rgba(248, 81, 73, 0.8)`.
- **Logarithmic Scale**: Auto-enables log scale if $\frac{\max}{\min} > 50$ and $\min > 0.01$. Clamps lower values to $0.01$ to avoid $\log(0) = -\infty$.

### 4.3 Diagnostic Histograms (`createBarChart` & `createGrowthRateChart`)

- Used for:
  - `#autocorr-chart`: Purple `#a371f7` bars showing dependency lag correlations.
  - `#streaks-chart`: Blue `#58a6ff` bars showing empirical streak lengths.
  - `#hourly-chart`: Blue `#58a6ff` bars showing intraday hourly win rates.
  - `#market-state-chart`: Purple `#d2a8ff` bars showing regime win rates (High/Low Volatility, Trend, Range).
  - `#gn-chart`: Green `#3fb950` for $N_{\text{optimal}}$, blue `#58a6ff` for other $N$.
  - `#kelly-chart`: Green `#3fb950` bars for Kelly fraction.

### 4.4 Critical Bug Identified: Instance Key Collisions

In `charts.js`:
- `createEquityCurve` and `createBarChart` correctly use `window[canvasId + 'Inst']`.
- However, `createMonteCarloChart` hardcodes:
  ```javascript
  if (window.mcChartInst) window.mcChartInst.destroy();
  window.mcChartInst = new Chart(ctx, { ... });
  ```
- Similarly, `createGrowthRateChart` hardcodes:
  ```javascript
  if (window.gnChartInst) window.gnChartInst.destroy();
  window.gnChartInst = new Chart(ctx, { ... });
  ```

**Consequence**: When switching between Smart Mode (`#smart-mc-chart-canvas`) and Advanced Mode (`#mc-chart`), `window.mcChartInst` only stores one instance. Calling destroy on `window.mcChartInst` destroys the chart instance belonging to the wrong canvas or leaks the previous canvas instance, leading to Chart.js "Canvas is already in use" errors during mode switches.

---

## 5. Canvas 2D Correlation Heatmap Architecture

### 5.1 Technical Implementation (`createCorrelationHeatmap`)

- **Target Element**: `#smart-correlation-canvas`.
- **High-DPI Scaling**:
  ```javascript
  const dpr = window.devicePixelRatio || 1;
  canvas.width = (width || 400) * dpr;
  canvas.height = (height || 280) * dpr;
  ctx.scale(dpr, dpr);
  ```
- **Grid Layout & Margins**:
  - `leftMargin = 70`, `topMargin = 15`, `rightMargin = 15`, `bottomMargin = 35`.
  - `cellW = (width - 85) / N`, `cellH = (height - 50) / N`.
  - Cell spacing of $1.5\text{px}$ (`fillRect(..., cellW - 1.5, cellH - 1.5)`).

### 5.2 Color Mapping & Numeric Rendering

- **Power Intensity**: `intensity = Math.pow(Math.abs(val), 1.2)`
- **Current Color Ramp**:
  - Positive ($r \ge 0$): Linear blend towards red `rgb(248, 81, 73)`.
  - Negative ($r < 0$): Linear blend towards blue `rgb(88, 166, 255)`.
- **Numeric Text Overlay**:
  - If `cellW > 18 && cellH > 14`, renders `val.toFixed(2)` centered in the cell.
  - Text color: `#ffffff` if $|r| > 0.4$, else `#c9d1d9`.
  - Font: `bold ${fontSize}px Inter, sans-serif`.
- **Axis Tickers**:
  - Strips `USDT` and `=X` suffixes (e.g. `BTCUSDT` -> `BTC`, `EURUSD=X` -> `EURUSD`).
  - Y-axis rendered on left margin, X-axis rendered along bottom.

---

## 6. Gap Analysis vs Institutional Design Specification

| Feature / Element | Current Code (`charts.js`) | Institutional Spec (`GUIA_MAESTRA`) | Technical Gap & Visual Defect |
|---|---|---|---|
| **Candlestick Colors** | `#00f5a0` (neon mint) & `#ff4d4d` (neon red) | Cyber Emerald `#10b981` & Rose Crimson `#f43f5e` | Extreme saturation causes retinal halation and chromostereopsis against dark surfaces. |
| **Lightweight Chart Grid** | `rgba(48, 54, 61, 0.3)` | `rgba(255, 255, 255, 0.03)` to `0.05` | High data-to-ink ratio violation; grid lines are too prominent. |
| **Lightweight Chart Borders** | `#30363d` | `rgba(255, 255, 255, 0.07)` | Harbors harsh legacy GitHub Dark borders. |
| **Lightweight Chart Crosshair** | Default unstyled | Subtle dashed line `rgba(255, 255, 255, 0.15)` | Needs calibrated opacity and label background (`#141d2e`). |
| **Chart.js Global Tooltip** | `rgba(22, 27, 34, 0.9)`, border `#30363d` | Elevated Slate `#141d2e`, border `rgba(255, 255, 255, 0.10)`, padding 8px-12px | Outdated tooltip style with harsh borders and uncalibrated contrast. |
| **Equity Curve Gradient** | Flat fill `rgba(88, 166, 255, 0.12)`, border `#58a6ff` | Vertical Canvas linear gradient (`#38bdf8` at 25% down to `0%`), border `#38bdf8` (Electric Sky) | Lacks institutional FinTech aesthetic (Linear/Bloomberg look). |
| **Equity Curve Typography** | Default proportional font | `'JetBrains Mono', monospace` on ticks and tooltips | Non-tabular numbers cause horizontal jitter and poor alignment. |
| **Monte Carlo Cone Colors** | `#58a6ff` (P50), `#3fb950` (P75/95), `#f85149` (P5/25) | Electric Sky `#38bdf8` (P50), Cyber Emerald `#10b981` (P75/95), Rose Crimson `#f43f5e` (P5/25) | Neon/GitHub colors clash with new design system. |
| **Monte Carlo Lifecycle** | `window.mcChartInst` single global instance | `window[canvasId + 'Inst']` keyed per canvas | Causes instance collisions/memory leaks between Smart and Advanced mode canvases. |
| **Diagnostic Bar Colors** | `#58a6ff`, `#a371f7`, `#d2a8ff`, `#3fb950` | Electric Sky `#38bdf8`, Quantum Amethyst `#a855f7`, Cyber Emerald `#10b981`, Golden Amber `#f59e0b` | Uses obsolete color hex codes. |
| **Diagnostic Grids & Axes** | Hardcoded grid `#30363d`, raw font | Subtle grid `rgba(255, 255, 255, 0.04)`, `'JetBrains Mono'` for numerical values | Axes lines too dark/heavy, non-tabular font. |
| **Correlation Heatmap Colors** | Red for positive, Blue for negative | Calibrated Palette: Obsidian `#0e1420` (neutral $r \approx 0$), Cyber Emerald `#10b981` (uncorrelated/negative), Rose Crimson `#f43f5e` (high positive risk) | Color mapping needs to align with quantitative risk semantics. |
| **Correlation Heatmap Numbers** | `Inter, sans-serif` | `'JetBrains Mono', monospace` | Font does not support strict tabular numeral alignment. |

---

## 7. Step-by-Step Implementation Strategy for Worker

### Phase 1: Institutional Design Tokens & Global Chart Defaults
1. Update `Chart.defaults`:
   - Text color: `#94a3b8` (`--text-secondary`).
   - Font family: `'Inter', sans-serif`.
   - Tooltip background: `#141d2e` (`--bg-surface-elevated`).
   - Tooltip title/body color: `#f0f6fc` (`--text-primary`).
   - Tooltip border: `rgba(255, 255, 255, 0.10)`.
   - Tooltip padding: `8px 12px`, corner radius `6px`.

### Phase 2: Lightweight Charts Refactoring
1. Update `createCandlestickChart(containerId)`:
   - Text color: `#94a3b8`.
   - Grid vert/horz colors: `rgba(255, 255, 255, 0.03)`.
   - TimeScale & RightPriceScale border color: `rgba(255, 255, 255, 0.07)`.
   - Candlestick colors: `upColor: '#10b981'`, `downColor: '#f43f5e'`, `wickUpColor: '#10b981'`, `wickDownColor: '#f43f5e'`.
2. Update `buildChartMarkers` & `addSignalMarkers`:
   - CALL arrow: `#10b981` (Cyber Emerald).
   - PUT arrow: `#f43f5e` (Rose Crimson).
   - WIN exit: `#10b981`, LOSS exit: `#f43f5e`.
3. Update `highlightTradeOnChart`:
   - Entry & exit price line colors to `#10b981` / `#f43f5e`.

### Phase 3: Chart.js Renderers Refactoring & Bug Fixes
1. Refactor `createEquityCurve`:
   - Inject vertical linear gradient for dataset fill:
     ```javascript
     const gradient = ctx.createLinearGradient(0, 0, 0, ctx.canvas.clientHeight || 300);
     gradient.addColorStop(0, 'rgba(56, 189, 248, 0.25)');
     gradient.addColorStop(1, 'rgba(56, 189, 248, 0.00)');
     ```
   - Border color: `#38bdf8`, borderWidth: `2`.
   - Scale ticks font: `'JetBrains Mono', monospace`, color `#94a3b8`.
   - Grid lines: `rgba(255, 255, 255, 0.04)`.
2. Refactor `createMonteCarloChart`:
   - Change instance tracking from `window.mcChartInst` to `window[canvasId + 'Inst']`.
   - Update percentile curve colors:
     - P95: `rgba(16, 185, 129, 0.85)` (Cyber Emerald dashed)
     - P75: `rgba(16, 185, 129, 0.45)` (Cyber Emerald solid)
     - P50: `#38bdf8` (Electric Sky solid, width 3)
     - P25: `rgba(244, 63, 94, 0.45)` (Rose Crimson solid)
     - P5: `rgba(244, 63, 94, 0.85)` (Rose Crimson dashed)
   - Ticks font: `'JetBrains Mono', monospace`. Grid lines: `rgba(255, 255, 255, 0.04)`.
3. Refactor `createBarChart` & `createGrowthRateChart`:
   - Change `createGrowthRateChart` instance tracking to `window[canvasId + 'Inst']`.
   - Standardize bar colors:
     - Default bar: `#38bdf8` (Electric Sky)
     - Optimal N: `#10b981` (Cyber Emerald)
     - Autocorr / Market state: `#a855f7` (Quantum Amethyst)
     - Kelly fraction: `#10b981` (Cyber Emerald)
   - Grid lines: `rgba(255, 255, 255, 0.04)`. Ticks font: `'JetBrains Mono', monospace`.

### Phase 4: Canvas 2D Correlation Heatmap Enhancement
1. Update `createCorrelationHeatmap`:
   - Neutral base color: `#0e1420` (Surface Base).
   - Positive correlation ramp: Blend to `#f43f5e` (Rose Crimson / concentration risk) or `#38bdf8`.
   - Negative / low correlation ramp: Blend to `#10b981` (Cyber Emerald / diversification).
   - Numeric overlay font: `bold ${fontSize}px 'JetBrains Mono', monospace`.
   - Axis labels font: `500 ${labelFontSize}px 'JetBrains Mono', monospace`, color `#94a3b8`.
   - Empty state text: `12px 'Inter', sans-serif`, color `#64748b`.

### Phase 5: Verification & Zero-Regression Protocol
1. Verify no console errors during initial page load and tab transitions.
2. Verify candlestick chart renders in both Smart Mode and Advanced Mode.
3. Verify backtest execution renders equity curve and all 5 diagnostic charts without canvas reuse warnings.
4. Verify genetic optimizer runs and renders Paroli ladder, Monte Carlo cones, and correlation heatmap.
5. Execute full backend test suite (`python -m pytest tests/`).

---
