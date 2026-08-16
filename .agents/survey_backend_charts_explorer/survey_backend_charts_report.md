# Comprehensive Survey Report: Backend APIs, Simulation Engines, Charting Integrations & Test Infrastructure

**Document Version**: 1.0.0  
**Project**: Binary Options Quantitative Terminal & Simulator (UI/UX Redesign)  
**Author**: Backend & Charts Explorer Agent  
**Date**: 2026-08-16  

---

## Executive Summary

This report delivers an exhaustive, line-by-line architectural survey of the backend systems, APIs, WebSocket streams, Server-Sent Events (SSE), simulation engines, charting libraries (TradingView Lightweight Charts v4 and Chart.js v4), and automated testing harnesses across `c:\Users\juanc\Desktop\prueba`.

The system operates as a hybrid full-stack quantitative financial terminal:
- **Backend Core**: Python 3.11 / Flask server (`app.py`), orchestrating mathematical engines (`BinarySimulator`, `CapitalOptimizer`, `StatisticsEngine`, `CorrelationEngine`, `RegimeDetector`, `MetaLabeler`, `BinaryMLMetaFilter`) and an ultra-fast compiled Rust sub-engine (`genetic_optimizer.exe`) executed via optimized subprocess pipelines with real-time stdout progress parsing.
- **Frontend Core**: High-density reactive client (`static/js/app.js`, `static/js/charts.js`, `templates/index.html`) featuring dual operating modes (*Modo Inteligente / Piloto Automático* and *Modo Avanzado / Manual*), live WebSocket Kline feeds from Binance API, SSE real-time streaming for long-running optimizations/backtests, Lightweight Charts candlestick renderers with dynamic trade marker overlays, and Chart.js analytical charts (Equity Curves with peak-preserving log/linear scales, Monte Carlo P5-P95 probability cones, custom 2D Canvas Pearson correlation heatmaps, and Markov transition matrices).
- **Test Infrastructure**: Fully compliant 4-tier opaque-box test suite (`pytest.ini`, 264 automated tests in `tests/` passing with 0 failures) plus an empirical Out-Of-Sample verification script (`verify_high_winrate_oos.py`).

---

## 1. Backend APIs, HTTP Endpoints & WebSocket Architecture

### 1.1 HTTP REST Endpoints (Flask)

The Flask server is initialized in `app.py` with CORS support (`CORS(app)`) and runs on port `5001`.

| Route | Method | Purpose | Request Parameters / Body | Response JSON Schema |
|---|---|---|---|---|
| `/` | `GET` | Web GUI Root | None | HTML template (`index.html`) |
| `/favicon.ico` | `GET` | Static Favicon | None | Icon file (`image/vnd.microsoft.icon`) |
| `/api/data/pairs` | `GET` | Catalog of available asset pairs and timeframes | None | `{"pairs": list[str], "intervals": list[str]}` (sorted logically: 1d, 4h, 2h, 1h, 30m, 15m, 5m, 3m, 1m) |
| `/api/data/candles` | `GET` | Historical OHLCV candle feed (local CSV or on-the-fly Binance fetch) | Query: `pair` (str, default: 'BTCUSDT'), `interval` (str, default: '1h'), `limit` (int, default: 500) | `{"candles": [{"time": int, "open": float, "high": float, "low": float, "close": float, "volume": float}]}` |
| `/api/strategies` | `GET` | Strategy catalog and parameter schema | None | `{"strategies": [{"name": str, "display_name": str, "description": str, "params": list[dict]}]}` |
| `/api/backtest` | `POST` | Synchronous single-asset backtest | JSON Body: `{"strategy": str, "params": dict, "pair": str, "interval": str, "expiry_candles": int, "payout": float, "mode": str, "n_consecutive": int, "bet_fraction": float, "allow_overlapping": bool, "max_concurrent_trades": int, "tie_rule": str}` | `{"trades": list[dict], "equity_curve": list[dict], "stats": dict, "signals": list[dict], "summary": dict}` |
| `/api/optimize` | `POST` | Single-asset N streak growth optimizer | JSON Body: `{"win_rate": float, "payout": float, "max_n": int}` | `{"optimal_n": int, "optimal_kelly": float, "optimal_growth": float, "results_by_n": list[dict]}` |
| `/api/montecarlo` | `POST` | Standard continuous Monte Carlo simulation | JSON Body: `{"win_rate": float, "payout": float, "n": int, "kelly_f": float, "num_simulations": int, "num_cycles": int}` | `{"paths": list[list[float]], "final_equity": dict, "ruin_probability": float, "max_drawdowns": dict}` |
| `/api/genetic/run` | `POST` | Synchronous Rust genetic optimizer execution | JSON Body: `{"pair": str, "interval": str, "expiry": int, "min_trades": float, "generations": int, "population": int}` | `{"in_sample_win_rate": float, "out_of_sample_win_rate": float, "neighbour_stability_is": float, "parameters": dict, "overfitting_status": str, ...}` |
| `/api/montecarlo-discrete` | `POST` | Discrete campaign Monte Carlo simulation | JSON Body: `{"win_rate": float, "payout": float, "n_consecutive": int, "bet_fraction": float, "risk_capital": float, "target_capital": float, "num_simulations": int}` | `{"success_probability": float, "ruin_probability": float, "expected_value": float, "mean_final_capital": float}` |
| `/api/optimize-streak` | `POST` | Binomial streak planning and bet ladder computation | JSON Body: `{"win_rate": float, "payout": float, "risk_capital": float, "target_capital": float, "attempts": int, "base_capital": float}` | `{"best_n_for_target": int, "results_by_n": list[dict]}` |
| `/api/smart-optimize` | `POST` | Synchronous smart optimization combining Rust genetic + multi-strategy Python evaluation | JSON Body: `{"pair": str, "interval": str, "base_capital": float, "profit_pct": float, "attempts": int, "payout": float, "expiry": int, "min_trades": float, "generations": int, "population": int}` | Consolidates best genome, win rates, streak plan, Barbell simulation, Monte Carlo paths, and statistics. |
| `/api/smart-optimize-v2` | `POST` | Multi-asset portfolio optimizer with In-Sample correlation gating and strategy ranking | JSON Body: `{"base_capital": float, "profit_pct": float, "attempts": int, "payout": float, "streak_length": int, "generations": int, "population": int, "universe": list[str]}` | Consolidates Top 5 strategies, asset win rates, correlation matrix, Barbell multi-asset simulation, streak plan, and Monte Carlo results. |

---

### 1.2 Streaming SSE Endpoints (Server-Sent Events)

Streaming endpoints are implemented with `mimetype='text/event-stream'`, `Cache-Control: no-cache`, and `Connection: keep-alive`. The client consumes them via native `EventSource`.

#### 1. `GET /api/smart-optimize-v2-stream`
- **Query Parameters**: `base_capital`, `profit_pct`, `attempts`, `payout`, `streak_length`, `generations`, `population`, `universe` (JSON string or comma-separated).
- **Event Types Emitted**:
  - `data: {"type": "log", "message": str}` (Step notifications)
  - `data: {"type": "progress", "progress": float (0.0 to 100.0), "eta": float (seconds), "log": str}`
  - `data: {"type": "error", "message": str}`
  - `data: {"type": "result", "data": <SmartResultPayload>}`
- **Execution Pipeline**:
  1. `Paso [1/5]`: `CorrelationEngine.load_universe()` & Pearson correlation matrix computation on 70% In-Sample data.
  2. `Paso [2/5]`: Greedy asset selection (< 0.65 correlation threshold).
  3. `Paso [3/5]`: Subprocess spawn of Rust `genetic_optimizer.exe` with real-time `PROGRESS: gen/total` parsing.
  4. `Paso [4/5]`: High-throughput grid evaluation across 13 candidate quantitative strategy profiles (ISLG, Climax Reversal, DEESR, Volatility Squeeze ML, Daily Confluence, S/R, Mean Reversion, RSI Extremes, Bollinger Bounce, MTF TCVE, etc.).
  5. `Paso [5/5]`: Multi-asset Barbell simulation, Out-Of-Sample validation split (70% IS / 30% OOS), binomial streak calculation, and 5,000-path Monte Carlo campaign simulation.

#### 2. `GET /api/backtest-stream`
- **Query Parameters**: `strategy`, `params` (JSON string), `pair`, `interval`, `expiry_candles`, `payout`, `mode`, `n_consecutive`, `bet_fraction`.
- **Worker Pipeline**: Runs `BinarySimulator.run` in a background daemon thread with a thread-safe `queue.Queue` emitting real-time progress ratios and ETAs.

#### 3. `GET /api/genetic/run-stream`
- **Query Parameters**: `pair`, `interval`, `expiry`, `min_trades`, `generations`, `population`.
- **Execution Pipeline**: Launches Rust optimizer via `subprocess.Popen(bufsize=1)`, reading stdout line-by-line. Lines matching `PROGRESS: X/Y` generate SSE progress events. When finished, `extract_json_from_output` extracts the JSON genome payload.

---

### 1.3 WebSocket Architecture (Binance Real-Time Kline Feed)

- **Endpoint**: `wss://stream.binance.com:9443/ws/${pair.toLowerCase()}@kline_${interval}` (e.g., `wss://stream.binance.com:9443/ws/btcusdt@kline_1h`).
- **Trigger**: Activated when the user selects `Fuente de Datos: En Vivo (Binance API)` (`#source-selector = 'live'`) on crypto assets ending in `USDT`.
- **Message Payload**:
  ```json
  {
    "e": "kline",
    "E": 1672531200000,
    "s": "BTCUSDT",
    "k": {
      "t": 1672531200000,
      "T": 1672534799999,
      "s": "BTCUSDT",
      "i": "1h",
      "o": "16500.00",
      "c": "16520.50",
      "h": "16535.00",
      "l": "16490.00",
      "v": "142.50",
      "x": false
    }
  }
  ```
- **Handler Actions**:
  1. Parses OHLCV numbers from strings.
  2. Computes bar color (Green `#00f5a0` for bull, Red `#ff4d4d` for bear, Gray `#8b949e` for flat).
  3. Updates current candle or appends new candle in `state.candles`.
  4. Calls `candleSeries.update(candleWithColor)` and `smartCandleSeries.update(candleWithColor)`.
  5. Updates `#live-badge-text` with `En Vivo: $<price>`.
- **Fallback Mechanism**: On WebSocket error or disconnect, automatically transitions to polling `https://api.binance.com/api/v3/klines?symbol=${pair}&interval=${interval}&limit=2` every 3,000 ms.

---

## 2. Data Models, Simulation Payloads & Statistics Structures

### 2.1 Backtest & Multi-Asset Simulation Payload (`sim_results`)

```typescript
interface BacktestResponse {
  trades: Array<{
    pair?: string;
    time: number;          // Unix timestamp in seconds
    entry_time?: number;
    exit_time?: number;
    direction: 'CALL' | 'PUT';
    entry_price: number;
    exit_price: number;
    result: 'WIN' | 'LOSS' | 'TIE';
    pnl: number;           // Net profit/loss in USD
    bet_size?: number;
  }>;
  equity_curve: Array<{
    time: number | null;   // Unix timestamp in seconds (or ms for smart stream)
    equity: number;        // Account balance in USD
  }>;
  signals: Array<{
    time: number;          // Timestamp in seconds
    direction: 'CALL' | 'PUT' | 'EXIT';
    entry_price?: number;
    exit_price?: number;
    result?: 'WIN' | 'LOSS' | 'TIE';
    trade_direction?: 'CALL' | 'PUT';
    pnl?: number;
    bet_size?: number;
  }>;
  summary: {
    total_trades: number;
    wins: number;
    losses: number;
    ties: number;
    win_rate: number;             // Gross win rate (wins / total)
    win_rate_effective: number;   // Effective win rate (wins / (wins + losses))
    net_pnl: number;
    max_drawdown: number;         // 0.0 to 1.0 fraction
    expected_value_per_trade: number;
  };
  stats: StatisticsEngineReport;
}
```

### 2.2 Statistics Engine Report (`stats`)

Produced by `StatisticsEngine.analyze(trades, df)`:
- `basic`: `win_rate`, `win_rate_effective`, `wilson_ci_95` `[low, high]`, `wilson_ci_gross_95`, `expected_value_per_trade`, `avg_trade_pnl`, `total`, `wins`, `losses`, `ties`, `decisive`, `net_pnl`.
- `streaks`: `max_win_streak`, `max_loss_streak`, `avg_win_streak`, `avg_loss_streak`, `win_streak_distribution` (dict `{streak_length: count}`), `loss_streak_distribution`, `streak_distribution` (combined).
- `dependency`: `autocorrelation` (list of Pearson autocorrelation values for lags 1 to 10), `p_win_given_win`, `p_win_given_loss`, `p_loss_given_win`, `p_loss_given_loss`.
- `market_state`: `high_vol_wr`, `low_vol_wr`, `trending_wr`, `ranging_wr`.
- `temporal`: `by_hour` (dict `{hour: win_rate}`), `by_day_of_week` (dict `{day: win_rate}`).
- `markov`: `states` `['WIN', 'LOSS']`, `transition_matrix` `[[P(W|W), P(L|W)], [P(W|L), P(L|L)]]`.
- `drawdown`: `max_drawdown`, `drawdown_duration_max`, `drawdown_duration_avg`.

### 2.3 Streak Plan & Barbell Allocation Model (`streak_plan`)

Calculated by `CapitalOptimizer.calculate_streak_plan`:
- `best_n_for_target`: Mathematically optimal consecutive streak length $N$ maximizing campaign success.
- `needed_streaks`: $M$ successful $N$-streaks required to achieve target capital duplication ($+100\%$).
- `prob_duplication_pct`: Binomial survival probability of achieving $\ge M$ streaks across $K$ attempts.
- `prob_at_least_1_streak_pct`: Probability of achieving $\ge 1$ successful $N$-streak in $K$ attempts ($1 - (1 - WR^N)^K$).
- `expected_monthly_net_profit`: Net EV in USD.
- `expected_final_patrimony`: Base capital + expected net profit.
- `results_by_n`: Array comparing $N \in [1..15]$ with $P(\text{single})$, $P(\text{campaign})$, Bet per attempt, Final capital, Net profit, and exact Bet Ladder (`[{"step": int, "bet_size": float, "payout_return": float}]`).

### 2.4 Monte Carlo Model (`mc_discrete` & `mc_paths`)

- `mc_discrete`: Success probability, ruin probability, expected final value, and mean final capital.
- `mc_paths`: 30 representative simulation trajectories scaled to risk capital, subsampled to 100 points each for fast network transfer.

---

## 3. Charting Integrations & Technical Configurations

The terminal uses two distinct charting engines:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CHARTING ENGINES ARCHITECTURE                         │
├──────────────────────────────────────┬──────────────────────────────────────────┤
│ TradingView Lightweight Charts (v4) │ Chart.js (v4) + Custom Canvas 2D         │
├──────────────────────────────────────┼──────────────────────────────────────────┤
│ • Main Candlestick (`#tv-chart`)     │ • Equity Curves (Lin / Log auto-detect)  │
│ • Smart Candlestick (`#smart-tv-chart`)│ • Monte Carlo Percentiles (P5..P95 Cones)│
│ • CALL / PUT / EXIT Signal Markers   │ • Correlation Heatmap (Canvas 2D DPI)    │
│ • Active Trade Entry/Exit PriceLines │ • Autocorrelation & Streaks Distribution │
│ • Crosshairs, Dynamic TimeScale      │ • Hourly WR & Market State Bar Charts    │
└──────────────────────────────────────┴──────────────────────────────────────────┘
```

### 3.1 TradingView Lightweight Charts (v4)

#### Initialization (`createCandlestickChart(containerId)`)
- **Container IDs**: `tv-chart` (Advanced mode) and `smart-tv-chart` (Smart mode).
- **Options**:
  - `layout.background`: `{ type: 'solid', color: 'transparent' }`
  - `layout.textColor`: `'#8b949e'` (Slate gray)
  - `layout.fontFamily`: `"'Inter', system-ui, -apple-system, sans-serif"`
  - `grid.vertLines.color` / `grid.horzLines.color`: `'rgba(48, 54, 61, 0.3)'`
  - `crosshair.mode`: `LightweightCharts.CrosshairMode.Normal`
  - `timeScale`: `timeVisible: true`, `secondsVisible: false`, `borderColor: '#30363d'`, `rightOffset: 10`, `barSpacing: 10`, `minBarSpacing: 0.5`, `autoScale: true`
  - `rightPriceScale`: `borderColor: '#30363d'`, `autoScale: true`, `scaleMargins: { top: 0.1, bottom: 0.1 }`

#### Candlestick Series (`addCandlestickSeries`)
- `upColor`: `#00f5a0` (Cyber Emerald)
- `downColor`: `#ff4d4d` (Rose Crimson)
- `wickUpColor`: `#00f5a0`
- `wickDownColor`: `#ff4d4d`
- `borderVisible`: `false`
- `priceFormat`: `{ type: 'price', precision: 5, minMove: 0.00001 }`

#### Signal Markers (`buildChartMarkers(signals)`)
Generates marker overlays for entry and exit events:
- **CALL entry**: `position: 'belowBar'`, `color: '#00f5a0'`, `shape: 'arrowUp'`, `text: 'CALL @ <price>'`
- **PUT entry**: `position: 'aboveBar'`, `color: '#ff4d4d'`, `shape: 'arrowDown'`, `text: 'PUT @ <price>'`
- **EXIT WIN**: `position: 'aboveBar'` (for CALL) / `'belowBar'` (for PUT), `color: '#00f5a0'`, `shape: 'circle'`, `text: 'WIN @ <price> (+<pnl>$)'`
- **EXIT LOSS**: `position: 'belowBar'` (for CALL) / `'aboveBar'` (for PUT), `color: '#ff4d4d'`, `shape: 'circle'`, `text: 'LOSS @ <price> (-<pnl>$)'`

#### Interactive PriceLines (`highlightTradeOnChart(trade, chartObj, seriesObj)`)
When a user clicks on a trade row in `#trades-table`, the table triggers `highlightTradeOnChart`:
- Creates a dashed line at `trade.entry_price` (`#00f5a0` for CALL, `#ff4d4d` for PUT).
- Creates a dotted line at `trade.exit_price` (`#00f5a0` for WIN, `#ff4d4d` for LOSS).
- Automatically clears previous lines via `seriesObj.removePriceLine()`.

---

### 3.2 Chart.js (v4) Analytical Visualizations

#### Global Defaults (`charts.js`)
- `Chart.defaults.color = '#8b949e'`
- `Chart.defaults.font.family = "'Inter', sans-serif"`
- `Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(22, 27, 34, 0.9)'`
- `Chart.defaults.plugins.tooltip.borderColor = '#30363d'`

#### 1. Equity Curve (`createEquityCurve(canvasId, equityPoints, rawLabels)`)
- **Canvas IDs**: `equity-chart` (Advanced) and `smart-equity-chart-canvas` (Smart).
- **Logarithmic Auto-Detection**: If $\frac{\max(V)}{\min(V)} > 100$ and $\min(V) \ge 1.0$, automatically switches scale to `'logarithmic'`.
- **Subsampling**: Uses `preserve_peaks_subsample` to preserve local minima and maxima without exceeding 500 points in JSON.
- **Y-Axis Tick Formatter** (`formatYAxisTick`): Filters non-decade sub-ticks in log mode to prevent label collisions; formats values with `$`, `k` ($1,000$), `M` ($1,000,000$).
- **Dataset**: `borderColor: '#58a6ff'`, `backgroundColor: 'rgba(88, 166, 255, 0.12)'`, `fill: true`, `tension: 0.1`, `pointRadius: 0`, `pointHoverRadius: 4`.

#### 2. Monte Carlo Cones (`createMonteCarloChart(canvasId, labels, percentiles)`)
- **Canvas IDs**: `mc-chart` (Advanced) and `smart-mc-chart-canvas` (Smart).
- **5 Percentile Datasets**:
  - `P95`: `borderColor: 'rgba(63, 185, 80, 0.8)'` (Green), `borderDash: [5, 5]`, `fill: false`
  - `P75`: `borderColor: 'rgba(63, 185, 80, 0.4)'` (Light Green), `fill: false`
  - `Mediana (P50)`: `borderColor: '#58a6ff'` (Electric Sky Blue), `borderWidth: 3`, `fill: false`
  - `P25`: `borderColor: 'rgba(248, 81, 73, 0.4)'` (Light Red), `fill: false`
  - `P5`: `borderColor: 'rgba(248, 81, 73, 0.8)'` (Rose Red), `borderDash: [5, 5]`, `fill: false`
- **Zero Cleaning**: Maps $v \le 0.01 \to 0.01$ to prevent $\log(0) \to -\infty$ scaling bugs.

#### 3. Pearson Correlation Heatmap (`createCorrelationHeatmap(canvasId, matrix, labels)`)
- **Canvas ID**: `smart-correlation-canvas`.
- **Implementation**: Custom HTML5 2D Canvas rendering supporting High-DPI (`window.devicePixelRatio`).
- **Color Mapping**:
  - Positive correlation: Non-linear power ramp `Math.pow(val, 1.2)` shifting from Slate Dark `#161b22` to Rose/Red `rgb(248, 81, 73)`.
  - Negative correlation: Non-linear power ramp shifting to Sky Blue `rgb(88, 166, 255)`.
- **Annotations**: Draws formatted 2-decimal text values (`val.toFixed(2)`) in bold `Inter` with dynamic contrast switching (`#ffffff` vs `#c9d1d9`).

#### 4. Diagnostic Bar Charts (`createBarChart`, `createGrowthRateChart`)
- `autocorr-chart`: Autocorrelation lags 1-10 (`#a371f7`).
- `streaks-chart`: Frequency distribution of consecutive win/loss streaks (`#58a6ff`).
- `hourly-chart`: Win Rate by hour of the day (`#58a6ff`).
- `market-state-chart`: Win rate across High Vol, Low Vol, Trending, Ranging (`#d2a8ff`).
- `gn-chart`: Growth rate $G(N)$ across streak lengths, highlighting optimal $N$ in green `#3fb950`.

---

## 4. Test Infrastructure, Verification & Run Commands

### 4.1 Automated Test Suites (`pytest`)

The test harness is configured in `pytest.ini` and consists of 264 automated unit, integration, and property-based tests:

```
pytest.ini:
  testpaths = tests test_high_winrate_mechanisms.py
  norecursedirs = scratch .agents data
  python_files = test_*.py
```

#### Test Suite Breakdown

| Test File | Test Count | Scope & Coverage |
|---|---|---|
| `test_high_winrate_mechanisms.py` | 5 | Unit tests for `frac_diff_fixed`, `CUSUMMonitor`, `MetaLabeler`, `RegimeDetector`, `BinaryMLMetaFilter`. |
| `tests/test_conftest_integrity.py` | 4 | Verification of test fixtures and boundary data generators. |
| `tests/test_milestone3_features.py` | 7 | Optuna hyperparameter tuning, True Walk-Forward optimization, vectorization speedups. |
| `tests/test_simulator_integrity.py` | 11 | `BinarySimulator` core invariants, tie rules (`RETURN_STAKE`, `LOSS`), Barbell bullet state resets, memory limits. |
| `tests/test_tier1_feature_coverage.py` | 90 | Tier 1 Category-Partition testing (5 test cases per feature across all 18 features). |
| `tests/test_tier2_boundary_corner_cases.py` | 108 | Tier 2 Boundary Value Analysis (6 test cases per feature covering NaNs, 0-capital, 100% loss/win streaks, singular matrices, edge cases). |
| `tests/test_tier3_cross_feature_combinations.py` | 25 | Tier 3 Pairwise Combinatorial testing across features and sub-engines. |
| `tests/test_tier4_real_world_scenarios.py` | 14 | Tier 4 End-to-end multi-asset portfolios, regime switching, and campaign executions. |
| **Total Test Count** | **264** | **100% Passing (0 failures, 2 benign warnings)** |

### 4.2 Executable Run Commands

#### 1. Running the Automated Test Suite
```powershell
pytest
```
*Expected output*: `264 passed in ~2m 37s`.

#### 2. Running Specific Test Sub-Suites
```powershell
pytest tests/test_simulator_integrity.py
pytest test_high_winrate_mechanisms.py
```

#### 3. Running Empirical Out-Of-Sample Verification Script
```powershell
python verify_high_winrate_oos.py
```
*Expected output*: Outputs verified OOS metrics, Wilson 95% lower bounds, and Zero-Cheating Causality attestations.

#### 4. Compiling the Rust Genetic Optimizer
```powershell
cd engine/genetic_optimizer
cargo build --release
```
*Binary output*: `engine/genetic_optimizer/target/release/genetic_optimizer.exe`.

#### 5. Starting the Backend Server
```powershell
python app.py
```
Or double-clicking the startup script:
```powershell
run_binarias_simulator.bat
```
*Server URL*: `http://127.0.0.1:5001`.

---

## 5. Potential Integration Risks, DOM Contracts & Invariants

To guarantee 100% functional integrity during the UI/UX redesign (Requirement R5), the redesign must strictly preserve all JavaScript DOM selectors, element IDs, form bindings, and data attribute contracts.

### 5.1 Critical DOM Element ID Inventory

#### 1. Mode Switcher & Navigation
- `#mode-smart`: Button toggling Smart Mode (`data-mode="smart"`).
- `#mode-advanced`: Button toggling Advanced Mode (`data-mode="advanced"`).
- `.tabs-nav`: Navigation bar containing tabs (hidden in Smart mode, visible in Advanced mode).
- `.tab-btn[data-tab="..."]`: Tabs: `dashboard`, `backtest`, `resultados`, `estadisticas`, `optimizador`.
- `.tab-pane`: Panes: `#smart-dashboard`, `#dashboard`, `#backtest`, `#resultados`, `#estadisticas`, `#optimizador`.
- `.subtab-btn[data-subtab="..."]`: Subtabs: `sec-strategy`, `sec-barbell`, `sec-genetic`.
- `.subtab-pane`: Subpanes: `#sec-strategy`, `#sec-barbell`, `#sec-genetic`.

#### 2. Smart Mode Controls & Form Inputs
- `input[name="smart-universe"]`: Checkboxes for assets (`WTI`, `NASDAQ`, `GBPJPY`, `XAUUSD`, `DOGEUSDT`, `ADAUSDT`, `BTCUSDT`, `BNBUSDT`, `ETHUSDT`). Requires minimum 3 checked.
- `.asset-wr-badge`: Span sibling to universe checkboxes updated dynamically with stars and win rates (`⭐⭐⭐ 74.2%`).
- `#smart-preset-select`: Dropdown for preset selection (`preset_33_6`, `preset_25_8`, `preset_200_1`).
- `#smart-streak-length`: Input for streak $N$.
- `#smart-base-capital`: Base capital input (default 1000).
- `#smart-profit-pct`: Profit percentage input (default 20).
- `#smart-risk-capital`: Readonly risk capital input (auto-calculated as $\text{base} \times \text{pct} / 100$).
- `#smart-attempts`: Attempts / bullets $K$ input (default 6).
- `#smart-payout`: Payout input (default 0.85).
- `#smart-generations`: Genetic generations input (default 50).
- `#smart-population`: Genetic population input (default 150).
- `#btn-smart-run`: Button initiating `runSmartOptimization()`.

#### 3. Smart Mode Results & Display Elements
- `#smart-top-5-box`: Container for strategy ranking pills.
- `#smart-top-5-list`: Dynamic list populated with `.top-strat-pill[data-strat-idx="..."]`.
- `#smart-rec-content`: Div populated with natural language explanation, Wilson OOS WR badges, and export buttons.
- `#smart-ladder-content`: Div populated with step-by-step Paroli ladder progression.
- `#smart-selected-assets-table` & `#smart-selected-assets-body`: Table displaying filtered assets, date ranges, and per-asset OOS win rates.
- `#smart-asset-selector`: Dropdown for selecting which asset's candles and trade signals to render in `#smart-tv-chart`.
- `#smart-tv-chart-empty`: Overlay removed when candles load.
- `#smart-markov-table`: Markov transition matrix table.
- `#smart-markov-explanation`: Markov text explanation.
- `#smart-console-box`, `#smart-console-logs`, `#smart-progress-bar-fill`: Streaming logs terminal and progress bar.

#### 4. Advanced Mode Controls & Form Inputs
- `#pair-selector`: Select element populated dynamically via `/api/data/pairs`.
- `#interval-selector`: Select element populated with intervals (`1d`, `4h`, `1h`, etc.).
- `#source-selector`: Select element (`historical` vs `live`).
- `#live-badge` & `#live-badge-text`: Live pulse badge for WebSocket connection.
- `#strategy-selector`: Strategy dropdown.
- `#dynamic-params`: Container where strategy parameter inputs are injected (`input[data-param="..."]`).
- `#expiry-candles`: Candle expiry input.
- `#payout`: Payout input.
- `#backtest-n-consecutive`: Streak length input with `#backtest-cycle-prob` helper text.
- `#backtest-bet-fraction`: Bet fraction input.
- `#gen-generations`, `#gen-population`, `#gen-min-trades`: Inputs for Rust genetic search.
- `#optimize-genetic-btn`: Button to run Rust search.
- `#genetic-progress-container`, `#genetic-progress-fill`, `#genetic-progress-text`, `#genetic-progress-eta`: Rust search progress bar.
- `#genetic-feedback`: Feedback box for Rust search results.
- `#backtest-progress-container`, `#backtest-progress-fill`, `#backtest-progress-text`, `#backtest-progress-eta`: Backtest progress bar.
- `#run-backtest-btn`: Form submit button.
- `#save-backtest-btn`: Favorites save button.

#### 5. Advanced Mode Results & Diagnostic Displays
- `#stat-winrate`, `#stat-trades`, `#stat-pnl`, `#stat-mw`, `#stat-ml`: Quick metric summary cards.
- `#trades-table tbody`: Table rows (`tr[data-trade-idx="..."]`) with click-to-highlight price lines.
- `#history-list` & `#saved-list`: Saved and historical backtest cards with `#btn-clear-history`.
- `#cond-probs`: Conditional probability grid.
- `#markov-table`: Transition matrix table.
- `#opt-winrate`, `#opt-payout`, `#opt-base-capital`, `#opt-profit-pct`, `#opt-risk-capital`, `#opt-target-capital`, `#opt-attempts`, `#btn-calc-streak`: Streak optimizer form.
- `#streak-recommendation-content`, `#bet-ladder-container`, `#streak-alternatives-table`: Streak results elements.

#### 6. Canvases & Lightweight Charts Containers
- `#tv-chart` (Div container for Lightweight Charts)
- `#smart-tv-chart` (Div container for Lightweight Charts)
- `#equity-chart` (Canvas)
- `#smart-equity-chart-canvas` (Canvas)
- `#mc-chart` (Canvas)
- `#smart-mc-chart-canvas` (Canvas)
- `#smart-correlation-canvas` (Canvas 2D)
- `#autocorr-chart` (Canvas)
- `#streaks-chart` (Canvas)
- `#hourly-chart` (Canvas)
- `#market-state-chart` (Canvas)
- `#gn-chart` (Canvas)
- `#kelly-chart` (Canvas)

---

## 6. Architectural Recommendations for UI/UX Redesign

1. **Strict ID & Attribute Preservation**: Maintain 100% of the IDs, classes, data-attributes, and form structures listed in Section 5. The redesign should focus purely on aesthetic CSS architecture, container hierarchy, Dark Obsidian surfaces (`#080b11`, `#0e1420`, `#141d2e`), APCA-calibrated text (`#f0f6fc`, `#94a3b8`), and semantic color tokens (`#38bdf8`, `#10b981`, `#f43f5e`, `#a855f7`, `#f59e0b`).
2. **Tabular Figures for Numbers**: Apply `font-variant-numeric: tabular-nums` with `JetBrains Mono` across `#trades-table`, `#smart-selected-assets-table`, `#smart-markov-table`, `#streak-alternatives-table`, and all metrics cards.
3. **Seamless Chart Container Sizing**: Ensure all chart canvas parent containers have explicit heights or flex configurations (`flex: 1`, `min-height: 220px`) with `position: relative` so `ResizeObserver` and Chart.js `responsive: true` maintain proper scaling without collapsing.
4. **Lightweight Charts Theme Alignment**: In `charts.js`, align the TradingView Lightweight Charts background from `transparent` to `#0e1420` / `#080b11`, update grid lines to `rgba(255, 255, 255, 0.04)`, and set price scale borders to `rgba(255, 255, 255, 0.07)` to seamlessly blend with the new surface elevation system.
5. **Correlation Heatmap Canvas Styling**: Update `createCorrelationHeatmap` in `charts.js` to draw on `#0e1420` surface with calibrated cell borders (`rgba(255, 255, 255, 0.05)`), ensuring zero optical vibration.

---

*Report compiled and verified by Backend & Charts Explorer Agent.*
