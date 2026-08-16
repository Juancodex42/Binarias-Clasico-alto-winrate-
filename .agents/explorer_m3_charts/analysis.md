# Milestone 3 Analysis Report: Professional Charting Engine & Micro-Interactions
**Document ID**: `M3-CHARTS-ANALYSIS-001`  
**Date**: 2026-08-16  
**Investigator**: Teamwork Explorer (Milestone 3 Charts)  
**Target Files**: `static/js/charts.js`, `static/js/app.js`, `templates/index.html`, `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`

---

## Executive Summary
This report presents an exhaustive investigation of the charting visual system for the Quantitative Terminal & Binary Options Simulator. The visual engine relies on three core rendering technologies:
1. **TradingView Lightweight Charts v4**: Used for real-time and historical candlestick series with algorithmic CALL/PUT and WIN/LOSS signals in both Smart Mode (`#smart-tv-chart`) and Advanced Mode (`#tv-chart`).
2. **Chart.js v4**: Used for Equity Curves (`#equity-chart`, `#smart-equity-chart-canvas`), Monte Carlo Stochastic Probability Cones (`#mc-chart`, `#smart-mc-chart-canvas`), and Statistical Diagnostic Panels (`#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#market-state-chart`, `#gn-chart`, `#kelly-chart`).
3. **HTML5 2D Canvas**: Used for the Cross-Asset Return Correlation Heatmap (`#smart-correlation-canvas`).

The current codebase contains several legacy styling remnants (hardcoded GitHub dark blues `#58a6ff`, fluorescent green `#00f5a0` and neon red `#ff4d4d` causing retinal chromostereopsis, grey `#30363d` gridlines, non-tabular tooltip numbers, and unshaded Monte Carlo paths). This report details the current implementation status, gap analysis against `GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`, exact file locations, and a concrete drop-in implementation plan.

---

## 1. Lightweight Charts Architecture & Theming

### 1.1 Current Implementation State
- **Containers**:
  - `#tv-chart`: In Advanced Mode Mercado tab (`templates/index.html:429`). Features `#chart-loader` spinner.
  - `#smart-tv-chart`: In Smart Mode Workspace (`templates/index.html:349`). Features `#smart-tv-chart-empty` overlay.
- **Initialization**: `createCandlestickChart(containerId)` in `static/js/charts.js:11-72` and observer hooks in `static/js/app.js:501-522`.
- **Signal Markers**: `buildChartMarkers(signals)` in `static/js/app.js:415-470` and fallback `addSignalMarkers(series, signals)` in `static/js/charts.js:74-91`.
- **Candle Pre-processing**: `prepareCandles(candles)` in `static/js/app.js:618-659` and `updateLiveCandleInChart(updatedCandle)` in `static/js/app.js:281-314`.

### 1.2 Identified Deficiencies & Anti-Patterns
1. **Gridline Contrast ("Chartjunk")**:
   - `charts.js:21-22`: `vertLines: { color: 'rgba(48, 54, 61, 0.3)' }`, `horzLines: { color: 'rgba(48, 54, 61, 0.3)' }`.
   - *Design System Requirement*: `rgba(255, 255, 255, 0.03)` (Section 4.1 & 8).
2. **Crosshair Styling**:
   - `charts.js:24-26`: Default crosshair with unstyled grey lines.
   - *Design System Requirement*: Electric Sky dashed lines `rgba(56, 189, 248, 0.4)` with Surface Elevated badge background `#141d2e`.
3. **Candlestick Color Palette & Chromostereopsis**:
   - `charts.js:59-63`, `app.js:295`, `app.js:435,443,462`, `app.js:640`: Hardcoded `#00f5a0` (fluorescent green) and `#ff4d4d` (neon red).
   - *Design System Requirement*: Calibrated semantic tokens:
     - **Cyber Emerald** `#10b981` for Bullish / CALL / WIN.
     - **Rose Crimson** `#f43f5e` for Bearish / PUT / LOSS.
     - **Text Secondary** `#94a3b8` / `#64748b` for Neutral/Doji bars.
     - `borderVisible: true` with matching `borderUpColor: '#10b981'` and `borderDownColor: '#f43f5e'`.
4. **Active Trade Price Lines**:
   - `app.js:1114-1134` (`highlightTradeOnChart`): Entry line `#00f5a0` / `#ff4d4d`, exit line `#00f5a0` / `#ff4d4d`.
   - *Design System Requirement*: Entry line in Electric Sky `#38bdf8` (dashed), Exit line in Cyber Emerald `#10b981` (WIN) / Rose Crimson `#f43f5e` (LOSS) (dotted).
5. **Empty State Overlay**:
   - `#smart-tv-chart-empty` in `index.html:350-353` and `style.css:1449-1462`. Displays correctly on initialization and is hidden when candle data is loaded (`app.js:2337`).

---

## 2. Chart.js Equity Curve Architecture

### 2.1 Current Implementation State
- **Render Function**: `createEquityCurve(canvasId, equityPoints, rawLabels)` in `static/js/charts.js:119-234`.
- **Target Canvases**:
  - `#equity-chart` in Advanced Mode (`templates/index.html:593`, invoked at `app.js:1073`).
  - `#smart-equity-chart-canvas` in Smart Mode (`templates/index.html:309`, invoked at `app.js:2283`).

### 2.2 Identified Deficiencies & Anti-Patterns
1. **Line Color & Fill Gradient**:
   - `charts.js:170-171`: `borderColor: '#58a6ff'`, `backgroundColor: 'rgba(88, 166, 255, 0.12)'`. Flat background fill without vertical fade.
   - *Design System Requirement*:
     - Line stroke: Electric Sky `#38bdf8` (width 2px, tension 0.15).
     - Area fill: Vertical canvas linear gradient from `rgba(56, 189, 248, 0.22)` at top down to `rgba(56, 189, 248, 0.00)` at bottom.
2. **Log-Scale Switching & Dynamic Ticks**:
   - `charts.js:94-117` (`formatYAxisTick`) and `charts.js:159-162`: Log-scale threshold `(maxVal / Math.max(minVal, 0.01)) > 100 && minVal >= 1.0` functions, but tick formatting should cleanly support sub-dollar and multi-million tabular values (`$1.2k`, `$15.4k`, `$1.2M`).
3. **Tooltip Theming & Numerical Alignment**:
   - `charts.js:218-231`: Tooltip styling uses default dark box.
   - *Design System Requirement*:
     - Background: `#141d2e` (Surface Elevated).
     - Border: `1px solid rgba(56, 189, 248, 0.25)`.
     - Corner radius: `6px`, padding: `10px`.
     - Title: `#f0f6fc` (`'Inter', sans-serif`, weight 600).
     - Body: `#94a3b8` with tabular figures in `'JetBrains Mono', monospace` (`font-variant-numeric: tabular-nums`).
     - Value formatting: `$1,245.80` with localized currency separators.

---

## 3. Chart.js Monte Carlo Stochastic Probability Cones

### 3.1 Current Implementation State
- **Render Function**: `createMonteCarloChart(canvasId, labels, percentiles)` in `static/js/charts.js:290-375`.
- **Target Canvases**:
  - `#mc-chart` in Advanced Mode Optimizer tab (`templates/index.html:855`, invoked at `app.js:1387, 1785`).
  - `#smart-mc-chart-canvas` in Smart Mode (`templates/index.html:330`, invoked at `app.js:2300`).

### 3.2 Identified Deficiencies & Anti-Patterns
1. **Missing Probability Cone Area Fills (Fan Chart)**:
   - Current datasets are 5 isolated lines without shaded bands between percentiles.
   - *Design System Requirement*: Fill areas between percentiles using `fill: '+1'` to create visual probability distribution cones:
     - P95 $\rightarrow$ P75: Cyber Emerald gradient `rgba(16, 185, 129, 0.06)`
     - P75 $\rightarrow$ P50: Electric Sky gradient `rgba(52, 211, 153, 0.06)`
     - P50 $\rightarrow$ P25: Light Coral gradient `rgba(251, 113, 133, 0.06)`
     - P25 $\rightarrow$ P5: Rose Crimson gradient `rgba(244, 63, 94, 0.06)`
2. **Harmonic Percentile Palette**:
   - P95: Cyber Emerald `#10b981` (`borderDash: [4, 4]`, width 1.5).
   - P75: Mint Emerald `#34d399` (solid, width 1.5).
   - P50 (Mediana): Electric Sky `#38bdf8` (solid, width 2.5, prominent central path).
   - P25: Coral Rose `#fb7185` (solid, width 1.5).
   - P5: Rose Crimson `#f43f5e` (`borderDash: [4, 4]`, width 1.5).
3. **Initial Capital Baseline**:
   - No baseline reference is drawn.
   - *Design System Requirement*: Draw a dashed neutral reference line at Initial Capital (`data: Array(N).fill(initialCapital)`, `borderColor: 'rgba(255, 255, 255, 0.3)'`, `borderDash: [6, 6]`) so users immediately discern in-the-money vs out-of-the-money simulation trajectories.

---

## 4. Canvas 2D Correlation Heatmap

### 4.1 Current Implementation State
- **Render Function**: `createCorrelationHeatmap(canvasId, matrix, labels)` in `static/js/charts.js:377-469`.
- **Target Canvas**: `#smart-correlation-canvas` in Smart Mode (`templates/index.html:360`, invoked at `app.js:2471`).

### 4.2 Identified Deficiencies & Anti-Patterns
1. **High-DPI Retina Scaling**:
   - `charts.js:389-391`: Sets `canvas.width` and `canvas.height` but omits explicit CSS pixel sizing (`canvas.style.width = width + 'px'`, `canvas.style.height = height + 'px'`), causing potential canvas scaling distortion in flexbox layouts.
2. **Color Interpolation Inversion**:
   - `charts.js:423-435`: Currently interpolates positive values to red `(248, 81, 73)` and negative to blue `(88, 166, 255)`.
   - *Design System Requirement*:
     - Neutral ($\rho = 0.0$): Dark Base `#141d2e` (`rgb(20, 29, 46)`).
     - Positive ($\rho > 0.0 \rightarrow +1.0$): Cyber Emerald `#10b981` (`rgb(16, 185, 129)`).
     - Negative ($\rho < 0.0 \rightarrow -1.0$): Electric Sky `#38bdf8` (`rgb(56, 189, 248)`) or Rose Crimson `#f43f5e` (`rgb(244, 63, 94)`).
3. **Typography & Cell Aesthetics**:
   - `charts.js:444`: Numeric values are rendered in `Inter, sans-serif`.
   - *Design System Requirement*: Monospaced tabular numerals in `'JetBrains Mono', monospace` (`font-weight: 600`), centered within crisp rounded cells (`ctx.roundRect(x, y, w, h, 3)`).
4. **Dynamic Resizing**:
   - Heatmap should store its last matrix/labels payload and re-render seamlessly when container dimensions change (e.g. window resize or tab switch).

---

## 5. Statistical Diagnostics Charts in Advanced Mode

### 5.1 Current Implementation State
- **Target Canvases**:
  - `#autocorr-chart` (`templates/index.html:654`, `app.js:1144`): Autocorrelation of returns.
  - `#streaks-chart` (`templates/index.html:665`, `app.js:1151`): Win/loss streak distribution.
  - `#hourly-chart` (`templates/index.html:676`, `app.js:1158`): Win rate by hour (0h..23h).
  - `#market-state-chart` (`templates/index.html:698`, `app.js:1174`): Win rate / trade distribution by market regime.
  - `#gn-chart` (`templates/index.html:809`, `app.js:1705`): Compound growth rate $G(N)$ vs streak length.
  - `#kelly-chart` (`templates/index.html:822`, `app.js:1710`): Kelly fraction.

### 5.2 Identified Deficiencies & Anti-Patterns
1. **Generic Bar Chart Helper**:
   - `createBarChart` (`charts.js:236-260`) applies a single hardcoded color `#58a6ff` and `#30363d` gridlines.
2. **Chart-Specific Requirements**:
   - **`#autocorr-chart`**: Quantum Amethyst `#a855f7` for positive autocorrelation, Rose Crimson `#f43f5e` for negative autocorrelation. Zero-line reference at $y = 0$.
   - **`#streaks-chart`**: Electric Sky `#38bdf8` gradient bars with rounded corners `borderRadius: 4`.
   - **`#hourly-chart`**: Color-coded bars: Cyber Emerald `#10b981` for $\text{WR} \ge 58.8\%$ (profitable hurdle), Electric Sky `#38bdf8` for $50\% \le \text{WR} < 58.8\%$, Rose Crimson `#f43f5e` for $\text{WR} < 50\%$.
   - **`#market-state-chart`**: Multi-color regime palette (Bullish Trend `#10b981`, Bearish Trend `#f43f5e`, Mean-Reverting `#38bdf8`, High Volatility `#f59e0b`).
   - **`#gn-chart` & `#kelly-chart`**: Optimal $N^*$ highlighted in Cyber Emerald `#10b981`, remaining bars in Electric Sky `#38bdf8`.

---

## 6. Comprehensive Implementation Plan for Milestone 3

### Step 1: Upgrade `static/js/charts.js`
1. Set global `Chart.defaults` to Design System tokens:
   - Color: `#94a3b8`
   - Font family: `'Inter', sans-serif`
   - Tooltip background: `#141d2e`, border: `rgba(255, 255, 255, 0.08)`, text: `#f0f6fc` / `#94a3b8`
2. Update `createCandlestickChart(containerId)`:
   - Gridlines: `rgba(255, 255, 255, 0.03)`
   - Crosshairs: `rgba(56, 189, 248, 0.4)` dashed with `#141d2e` badges
   - Scales: `rgba(255, 255, 255, 0.07)` borders, `#94a3b8` font
   - Series: `#10b981` (up) and `#f43f5e` (down)
3. Update `createEquityCurve(canvasId, equityPoints, rawLabels)`:
   - Electric Sky line `#38bdf8` + vertical linear gradient fill
   - Tabular tooltip with currency formatting
   - Axis ticks in `'JetBrains Mono', monospace`
4. Update `createMonteCarloChart(canvasId, labels, percentiles, initialCapital)`:
   - Calibrated 5-percentile palette (P95 `#10b981`, P75 `#34d399`, P50 `#38bdf8`, P25 `#fb7185`, P5 `#f43f5e`)
   - Shaded probability cone fills (`fill: '+1'`)
   - Dashed baseline at Initial Capital (`$1000` or first value)
5. Update `createCorrelationHeatmap(canvasId, matrix, labels)`:
   - High-DPI physical-to-CSS pixel scaling
   - Diverging color interpolation (Rose `#f43f5e` $\rightarrow$ Dark `#141d2e` $\rightarrow$ Emerald `#10b981`)
   - Tabular numerals in `'JetBrains Mono', monospace`
   - Window resize handler for automatic redraw
6. Update `createBarChart` and `createGrowthRateChart`:
   - Design System palette, dark tooltips, subtle gridlines `rgba(255, 255, 255, 0.03)`.

### Step 2: Synchronize Signal Markers & Candlestick Colors in `static/js/app.js`
1. Update `prepareCandles(candles)`:
   - Replace `#ff4d4d` $\rightarrow$ `#f43f5e`, `#00f5a0` $\rightarrow$ `#10b981`, `#8b949e` $\rightarrow$ `#94a3b8`.
2. Update `updateLiveCandleInChart(updatedCandle)`:
   - Replace `#ff4d4d` $\rightarrow$ `#f43f5e`, `#00f5a0` $\rightarrow$ `#10b981`, `#8b949e` $\rightarrow$ `#94a3b8`.
3. Update `buildChartMarkers(signals)`:
   - CALL $\rightarrow$ `#10b981`, PUT $\rightarrow$ `#f43f5e`, WIN $\rightarrow$ `#10b981`, LOSS $\rightarrow$ `#f43f5e`.
4. Update `highlightTradeOnChart(trade, chartObj, seriesObj)`:
   - Entry line $\rightarrow$ `#38bdf8`, Exit line $\rightarrow$ `isWin ? '#10b981' : '#f43f5e'`.
5. Update `renderDiagnosticsCharts(statsData)`:
   - Pass calibrated color arrays to `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, and `#market-state-chart`.

### Step 3: Verification & Regression Testing
1. Execute full test suite `pytest` (ensure 322/322 tests pass).
2. Validate zero console errors and clean rendering across both Smart Mode and Advanced Mode.
