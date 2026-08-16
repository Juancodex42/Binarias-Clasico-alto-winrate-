## 2026-08-16T19:48:51Z
You are the Explorer for Milestone 2 (Institutional HTML5 Workspace Architecture & Template Refactoring) of the Binary Options Quantitative Terminal UI/UX Redesign project.
Your working directory is: c:\Users\juanc\Desktop\prueba\.agents\explorer_m2\

You MUST read:
1. c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
2. c:\Users\juanc\Desktop\prueba\PROJECT.md
3. c:\Users\juanc\Desktop\prueba\.agents\survey_spec_miner\survey_spec_report.md
4. c:\Users\juanc\Desktop\prueba\.agents\survey_frontend_explorer\survey_frontend_report.md
5. c:\Users\juanc\Desktop\prueba\templates\index.html
6. c:\Users\juanc\Desktop\prueba\static\css\style.css

Your task is to produce an exhaustive implementation plan for upgrading `templates/index.html`:
1. Typography & Fonts head links: Google Fonts for Inter (300, 400, 500, 600, 700) and JetBrains Mono (400, 500, 600, 700).
2. Institutional Header:
   - Logo with glowing gradient ("Binarias Simulator" / "QUANT TERMINAL").
   - Telemetry pills: Rust Quantitative Core active status badge + Live WebSocket pulse badge (`#live-badge`, `#live-badge-text`, `.pulse-dot`).
   - Mode Switcher: pill container with `#mode-smart` and `#mode-advanced`.
   - Advanced tabs nav (`.tabs-nav`) with data-tab buttons (`#btn-resultados`, `#btn-estadisticas`, `#btn-optimizador`, etc.).
3. Smart Mode Workspace:
   - High-density control bar: `#smart-preset-select`, Universe checkboxes with `.asset-wr-badge` spans, numeric inputs (`#smart-streak-length`, `#smart-base-capital`, `#smart-profit-pct`, `#smart-risk-capital`, `#smart-attempts`, `#smart-payout`, `#smart-generations`, `#smart-population`), and primary CTA button `#btn-smart-run`.
   - Live telemetry cyberpunk console: `#smart-console-box`, `#smart-progress-bar-fill`, `#smart-console-logs`.
   - Multi-panel results layout: Top-5 strategy ranking pills `#smart-top-5-box` / `#smart-top-5-list`, Paroli ladder container `#smart-ladder-content`, strategy recommendation banner `#smart-rec-content`, correlation heatmap canvas `#smart-correlation-canvas`, low-correlation assets table `#smart-selected-assets-table`, equity curve canvas `#smart-equity-chart-canvas`, Monte Carlo canvas `#smart-mc-chart-canvas`, asset selector `#smart-asset-selector`, Lightweight Charts container `#smart-tv-chart` with empty overlay `#smart-tv-chart-empty`, Markov table `#smart-markov-table` and explanation `#smart-markov-explanation`.
4. Advanced Mode Workspace:
   - Mercado tab (`#dashboard`): `#pair-selector`, `#interval-selector`, `#source-selector`, `#tv-chart`, `#chart-loader`.
   - Backtest tab (`#backtest`): `#backtest-form`, `#run-backtest-btn`, `#save-backtest-btn`, `#strategy-selector`, `#dynamic-params`, `#expiry-candles`, `#payout`, Barbell capital controls (`#backtest-n-consecutive`, `#backtest-cycle-prob`, `#backtest-bet-fraction`), Rust genetic controls (`#gen-generations`, `#gen-population`, `#gen-min-trades`, `#optimize-genetic-btn`, `#genetic-progress-fill`, `#genetic-progress-text`, `#genetic-progress-eta`, `#genetic-feedback`), backtest progress (`#backtest-progress-fill`), Quick stats cards (`#stat-winrate`, `#stat-trades`, `#stat-pnl`, `#stat-mw`, `#stat-ml`), `#equity-chart`, and `#trades-table`.
   - Historial tab (`#resultados`): `#btn-clear-history`, `#history-list`, `#saved-list`.
   - Estadísticas tab (`#estadisticas`): `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#cond-probs`, `#market-state-chart`, `#markov-table`.
   - Optimizador tab (`#optimizador`): Inputs (`#opt-winrate`, `#opt-payout`, `#opt-base-capital`, `#opt-profit-pct`, `#opt-risk-capital`, `#opt-target-capital`, `#opt-attempts`), `#btn-calc-streak`, `#streak-progress-fill`, `#streak-recommendation-content`, `#bet-ladder-container`, `#streak-alternatives-table`, and `#mc-chart`.
5. Preservation Guarantee:
   - 100% retention of all 89 IDs, 37 input names/types/attributes, 16 buttons, and script imports (`charts.js`, `app.js`).

Write your detailed plan to `c:\Users\juanc\Desktop\prueba\.agents\explorer_m2\m2_plan.md` and write `handoff.md`.
Send a completion message to the caller when done.
