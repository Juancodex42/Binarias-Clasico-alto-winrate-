# PLAN MAESTRO DE IMPLEMENTACIÓN: ARQUITECTURA WORKSPACE HTML5 Y REFACTORIZACIÓN DE TEMPLATES (MILESTONE 2)

**Proyecto**: Binary Options Quantitative Terminal & Strategy Simulator  
**Módulo**: `templates/index.html` Refactoring & Layout Architecture  
**Fecha**: 2026-08-16  
**Estado**: Plan de Implementación Exhaustivo Aprobado  
**Directorio de Trabajo**: `c:\Users\juanc\Desktop\prueba\.agents\explorer_m2\`  

---

## 1. RESUMEN EJECUTIVO Y OBJETIVOS ARQUITECTÓNICOS

El propósito del **Milestone 2** es refactorizar integralmente la plantilla principal `templates/index.html` para convertir la interfaz en un **Terminal Institucional de Analítica Cuantitativa y Trading Cuántico de Grado Profesional** (benchmarks: Linear.app, TradingView Pro, Bloomberg B-Pipe, Vercel Geist), garantizando una **preservación del 100% de los identificadores DOM (IDs), selectores de formulario, clases funcionales y contratos de JavaScript/SSE/WebSocket**.

### 1.1 Pilares de la Refactorización
1. **Tipografía Dual & Head Metadata**: Carga asíncrona y de alto rendimiento de `Inter` (300, 400, 500, 600, 700) para la interfaz y `JetBrains Mono` (400, 500, 600, 700) para cifras tabulares cuantitativas (`font-variant-numeric: tabular-nums`).
2. **Header Institucional Unificado**: Barra superior con logotipo con gradiente esmeralda/cielo (`Binarias Simulator`), pill de telemetría de motor Rust (`Motor Cuantitativo: ACTIVO`), badge de pulso WebSocket (`#live-badge`, `#live-badge-text`, `.pulse-dot`), selector de modo híbrido (`#mode-smart`, `#mode-advanced`) y navegación por tabs avanzada (`.tabs-nav`).
3. **Workspace de Modo Inteligente (Piloto Automático)**: Barra de control compacta de alta densidad con presets Barbell (`#smart-preset-select`), checkboxes del universo con badges de Win Rate (`.asset-wr-badge`), 8 inputs numéricos, consola cyberpunk con streaming SSE (`#smart-console-box`, `#smart-progress-bar-fill`, `#smart-console-logs`) y área de resultados asimétrica en 4 niveles (Top-5 Ranking, Plan de Rachas + Escalera Paroli, Heatmap de Correlación + Activos Seleccionados, Curva de Capital + Conos Monte Carlo, Velas TradingView + Matriz de Markov).
4. **Workspace de Modo Avanzado (Manual)**: 5 paneles especializados (`#dashboard`, `#backtest`, `#resultados`, `#estadisticas`, `#optimizador`) organizados con sub-tabs, cards de estadísticas rápidas, tablas de operaciones interactivas y matrices diagnósticas.
5. **Garantía Inviolable de Preservación (Zero Regressions)**: 105 IDs estáticos, 37 inputs de formulario, 16 botones de acción y todos los hooks globales en `window`.

---

## 2. ESPECIFICACIÓN DEL HEAD Y RECURSOS EXTERNOS

### 2.1 Metadatos y Carga de Fuentes
El `<head>` debe contener la optimización de pre-conexión y carga de Google Fonts con ambas familias tipográficas requeridas:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binarias Simulator - Terminal Cuantitativo Institucional</title>
    
    <!-- Favicons -->
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="apple-touch-icon" href="/static/favicon.png">
    
    <!-- Preconnect & Google Fonts: Inter (UI) + JetBrains Mono (Data & Tabular Numbers) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Design System Global Stylesheet -->
    <link rel="stylesheet" href="/static/css/style.css">
    
    <!-- Third-Party Charting Engines -->
    <script src="https://unpkg.com/lightweight-charts@4/dist/lightweight-charts.standalone.production.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
```

---

## 3. ARQUITECTURA DEL HEADER INSTITUCIONAL

El Header unifica branding, selector de modo y telemetría de conexión en una barra sticky de 64px de altura.

```html
<header class="app-header">
    <!-- Logotipo y Branding -->
    <div class="logo">
        <h1>Binarias <span>Simulator</span></h1>
        <span class="badge badge-quant">QUANT TERMINAL PRO</span>
    </div>
    
    <!-- Selector de Modo Híbrido -->
    <div class="mode-switch-container">
        <button class="mode-btn active" id="mode-smart" data-mode="smart">⚡ Modo Inteligente (Piloto Automático)</button>
        <button class="mode-btn" id="mode-advanced" data-mode="advanced">⚙️ Modo Avanzado (Manual)</button>
    </div>
    
    <!-- Telemetría en Vivo y Navegación Avanzada -->
    <div class="header-right-actions">
        <!-- Telemetry Pills -->
        <div class="telemetry-badges-group">
            <div class="status-pill rust-engine-pill" title="Motor cuantitativo de backtesting y algoritmos genéticos en Rust">
                <span class="pulse-dot text-green">●</span>
                <span class="pill-label">Rust Core: <strong>ACTIVO</strong></span>
            </div>
            
            <span id="live-badge" class="live-badge-span" style="display: none;">
                <span class="pulse-dot">●</span>
                <span id="live-badge-text">En Vivo</span>
            </span>
        </div>

        <!-- Advanced Mode Tabs Navigation (Oculto por defecto en Smart Mode) -->
        <nav class="tabs-nav" style="display: none;">
            <button class="tab-btn" data-tab="dashboard">Mercado</button>
            <button class="tab-btn" data-tab="backtest">Backtest</button>
            <button class="tab-btn" data-tab="resultados" id="btn-resultados">Resultados</button>
            <button class="tab-btn" data-tab="estadisticas" id="btn-estadisticas" disabled>Estadísticas</button>
            <button class="tab-btn" data-tab="optimizador" id="btn-optimizador" disabled>Optimizador</button>
        </nav>
    </div>
</header>
```

---

## 4. WORKSPACE DE MODO INTELIGENTE (`#smart-dashboard`)

El contenedor `#smart-dashboard` alberga la experiencia 1-clic con la barra de control compacta superior y el área de resultados asimétrica.

### 4.1 Barra de Control Compacta de Alta Densidad (`.smart-sidebar.glass-card`)
Estructura en una sola tarjeta glassmorphic:
1. **Fila Superior de Título y Acción Primaria**:
   - Título: `⚡ Optimización Inteligente`
   - Subtítulo explicativo: Detalle de protección de capital base mediante arbitraje P2P.
   - Botón CTA de ejecución: `<button type="button" class="btn-primary" id="btn-smart-run">⚡ Auto-Optimizar Estrategia</button>`.
2. **Contenedor de Inputs (`.smart-inputs-container`)**:
   - **Universo de Activos (`.smart-universe-wrapper`)**: Label con tooltip + Contenedor `.smart-universe-select` con 9 checkboxes `name="smart-universe"` y spans `.asset-wr-badge`:
     - `WTI` (checked)
     - `NASDAQ` (checked)
     - `GBPJPY` (checked)
     - `XAUUSD` (checked)
     - `DOGEUSDT` (checked)
     - `ADAUSDT` (checked)
     - `BTCUSDT` (checked)
     - `BNBUSDT` (checked)
     - `ETHUSDT` (unchecked)
   - **Selector de Presets Barbell (`.smart-preset-wrapper`)**: Label destacado con tooltip explicativo + Dropdown `<select id="smart-preset-select" class="form-control">`:
     - `preset_33_6`: 🚀 [MÁXIMA EFICIENCIA QUANT] 6 Balas de $33.33 / Mes (Rachas N=3) ➔ Meta: Duplicación +100% de Patrimonio
     - `preset_25_8`: ⚡ [Conservador / 8 Intentos] 8 Balas de $25.00 / Mes (Rachas N=3) ➔ Meta: Duplicación +100% de Patrimonio
     - `preset_200_1`: 🎯 [Retorno Directo / 1 Intento] 1 Bala de $200 / Mes (Racha N=3) ➔ Ganancia: +$1,066.33 (Capital Final: $2,066 USDT)
   - **Controles Numéricos Compactos (`.smart-numeric-inputs`)**:
     - `smart-streak-length`: Racha (N), default `3`, min `1`, max `15`.
     - `smart-base-capital`: Capital Base ($), default `1000`, min `10`, con tooltip.
     - `smart-profit-pct`: Rend. Mensual (%), default `20`, min `1`, max `100`.
     - `smart-risk-capital`: Cap. Riesgo (Arbitraje P2P), default `200`, readonly, clase `input-readonly`.
     - `smart-attempts`: Intentos / Balas (X), default `6`, min `1`, max `50`.
     - `smart-payout`: Payout Broker, default `0.85`, min `0.1`, max `1.0`, step `0.01`.
     - `smart-generations`: Generaciones Rust, default `50`, min `5`, max `200`, con tooltip.
     - `smart-population`: Población Rust, default `150`, min `10`, max `500`, con tooltip.
3. **Consola Cyberpunk con Streaming SSE (`#smart-console-box`)**:
   - Encabezado con puntos estilo macOS (`.console-dot.red`, `.yellow`, `.green`) y título `PROCESADOR CUANTITATIVO`.
   - Barra de progreso con shimmer: `.smart-progress-bar-container` + `<div class="smart-progress-bar-fill" id="smart-progress-bar-fill"></div>`.
   - Cuerpo de logs: `<div class="console-body" id="smart-console-logs"></div>`.

### 4.2 Tablero de Resultados Asimétrico (`.smart-results-area`)
Organizado verticalmente en 5 bloques:
1. **Ranking Top-5 de Estrategias Optimizadas**:
   - Contenedor `#smart-top-5-box` (`.top-strategies-wrapper.glass-card`), display none inicial.
   - Header con título 🏆 y subtítulo interactivo.
   - Lista dinámica de pills: `<div id="smart-top-5-list"></div>`.
2. **Nivel 1: Plan de Rachas & Escalera Paroli (`.smart-row-top`)**:
   - Tarjeta Izquierda: `.chart-card.glass-card.smart-card-rec` con título `📊 Plan de Rachas Optimizado` y contenedor `#smart-rec-content` (`.smart-rec-text`).
   - Tarjeta Derecha: `.chart-card.glass-card.smart-card-ladder` con título `🪜 Escalera de Apuestas` (tooltip Paroli) y contenedor con scroll `#smart-ladder-content`.
3. **Nivel 2: Heatmap de Correlación & Selección de Activos (`.smart-row-correlation`)**:
   - Tarjeta Izquierda: `.chart-card.glass-card` con título `🔥 Heatmap de Correlación de Retornos` (tooltip) y canvas `<canvas id="smart-correlation-canvas"></canvas>`.
   - Tarjeta Derecha: `.chart-card.glass-card` con título `📋 Activos Seleccionados (Filtro < 0.40)` y tabla `<table class="markov-table" id="smart-selected-assets-table">` con `tbody#smart-selected-assets-body`.
4. **Nivel 3: Curvas Cuantitativas (`.smart-row-charts`)**:
   - Tarjeta Izquierda: `.chart-card.glass-card` con título `📈 Curva de Capital (Backtest Barbell Histórico)` y canvas `<canvas id="smart-equity-chart-canvas"></canvas>`.
   - Tarjeta Derecha: `.chart-card.glass-card` con título `🎲 Proyección de Crecimiento (Monte Carlo - 1,000 caminos)` y canvas `<canvas id="smart-mc-chart-canvas"></canvas>`.
5. **Nivel 4: Velas con Señales & Matriz de Markov (`.smart-row-bottom`)**:
   - Tarjeta Izquierda: `.chart-card.glass-card` con título `🕯️ Velas de Precio con Señales:` + `<select id="smart-asset-selector"></select>`, contenedor Lightweight Charts `<div class="chart-container" id="smart-tv-chart">` y overlay `<div id="smart-tv-chart-empty">`.
   - Tarjeta Derecha: `.chart-card.glass-card` con título `📊 Matriz de Markov (Estabilidad de Rachas)`, tabla `<table class="markov-table" id="smart-markov-table">` y caja de explicación dinámica `<div id="smart-markov-explanation">`.

---

## 5. WORKSPACE DE MODO AVANZADO

### 5.1 Tab 1: Exploración de Mercado (`#dashboard`)
- Barra de Controles (`.controls-bar.glass-card`):
  - `#pair-selector`: Selector de par (`BTCUSDT`, etc.).
  - `#interval-selector`: Selector de temporalidad (`1d`, `4h`, `1h`, `30m`, `15m`, `5m`, `1m`).
  - `#source-selector`: Selector de fuente (`historical`, `live`).
- Gráfico TradingView (`#tv-chart` con `.chart-container.glass-card`) y spinner `#chart-loader` (`.loading-spinner`).

### 5.2 Tab 2: Backtesting Manual & Algoritmo Genético (`#backtest`)
- Estructura `.backtest-grid`:
  - **Panel de Configuración (`.config-panel.glass-card`)**:
    - Barra superior con Sub-Tabs (`.subtabs-nav`):
      - `button[data-subtab="sec-strategy"]` (`🔵 Activo y Estrategia`)
      - `button[data-subtab="sec-barbell"]` (`🟢 Gestión Barbell`)
      - `button[data-subtab="sec-genetic"]` (`🟣 Búsqueda Genética (Rust)`)
    - Botones de acción: `#run-backtest-btn` (`.btn-primary`), `#save-backtest-btn` (`.btn-secondary`).
    - Formulario `#backtest-form`:
      - Sub-pane 1 `#sec-strategy` (`.subtab-pane.active`): `#strategy-selector`, `#dynamic-params`, `#expiry-candles`, `#payout`.
      - Sub-pane 2 `#sec-barbell` (`.subtab-pane`): `#group-n-consecutive`, `#backtest-n-consecutive`, `#backtest-cycle-prob`, `#backtest-bet-fraction`.
      - Sub-pane 3 `#sec-genetic` (`.subtab-pane`): `#gen-generations`, `#gen-population`, `#gen-min-trades`, `#optimize-genetic-btn`, `#genetic-progress-container`, `#genetic-progress-fill`, `#genetic-progress-text`, `#genetic-progress-eta`, `#genetic-feedback`.
    - Barra de progreso de backtest: `#backtest-progress-container`, `#backtest-progress-fill`, `#backtest-progress-text`, `#backtest-progress-eta`.
  - **Panel de Resultados (`.results-panel`)**:
    - Tarjetas de Estadísticas Rápidas (`#quick-stats` / `.stats-cards`):
      - Win Rate: `#stat-winrate`
      - Trades: `#stat-trades`
      - P&L Neto: `#stat-pnl`
      - Max Win Streak: `#stat-mw`
      - Max Loss Streak: `#stat-ml`
    - Curva de Capital: `.equity-chart-container.glass-card` con canvas `<canvas id="equity-chart"></canvas>`.
    - Tabla de Operaciones: `.trades-table-container.glass-card` con `<table class="trades-table" id="trades-table">`.

### 5.3 Tab 3: Historial y Favoritos (`#resultados`)
- Estructura `.resultados-grid`:
  - Panel Izquierdo (`.resultados-panel.glass-card`): Título `⚡ Optimizaciones Automáticas (Historial)`, botón `#btn-clear-history`, lista `#history-list` (`.backtest-list`).
  - Panel Derecho (`.resultados-panel.glass-card`): Título `⚙️ Backtests Manuales & Favoritos`, lista `#saved-list` (`.backtest-list`).

### 5.4 Tab 4: Estadísticas Cuantitativas Profundas (`#estadisticas`)
- Estructura `.stats-grid` con 6 tarjetas `.chart-card.glass-card`:
  1. Autocorrelación (Lags 1-10): `<canvas id="autocorr-chart"></canvas>`.
  2. Distribución de Rachas: `<canvas id="streaks-chart"></canvas>`.
  3. Win Rate por Hora: `<canvas id="hourly-chart"></canvas>`.
  4. Probabilidades Condicionales: `<div class="cond-probs-grid" id="cond-probs"></div>`.
  5. Win Rate por Estado de Mercado: `<canvas id="market-state-chart"></canvas>`.
  6. Matriz de Transición (Markov): `<table class="markov-table" id="markov-table"></table>`.

### 5.5 Tab 5: Optimizador Barbell de Rachas (`#optimizador`)
- Estructura `.optimizer-grid`:
  - **Sidebar de Parámetros (`.optimizer-sidebar.glass-card`)**:
    - `#opt-winrate`, `#opt-payout`, `#opt-base-capital`, `#opt-profit-pct`, `#opt-risk-capital`, `#opt-target-capital`, `#opt-attempts`.
    - Botón de cálculo: `<button class="btn-primary" id="btn-calc-streak">Calcular Plan de Rachas</button>`.
    - Progreso: `#streak-progress-container`, `#streak-progress-fill`, `#streak-progress-text`, `#streak-progress-eta`.
  - **Paneles Gráficos (`.optimizer-charts`)**:
    - Banner de Recomendación: `#streak-recommendation-content`.
    - Escalera de Apuestas: `#bet-ladder-container`.
    - Tabla de Alternativas por Racha: `<table class="n-table" id="streak-alternatives-table"></table>`.
    - Proyección Monte Carlo 5,000 caminos: `<canvas id="mc-chart"></canvas>`.

---

## 6. MATRIZ DE PRESERVACIÓN EXHAUSTIVA (100% INVIOLABLE)

### 6.1 Catálogo Completo de IDs HTML Estáticos (105 IDs)

| # | ID del Elemento | Etiqueta | Contenedor Padre | Propósito y Binding JS |
|---|---|---|---|---|
| 1 | `mode-smart` | `<button>` | `.mode-switch-container` | Alterna a Modo Inteligente (`#smart-dashboard`) |
| 2 | `mode-advanced` | `<button>` | `.mode-switch-container` | Alterna a Modo Avanzado (`#dashboard`) y revela `.tabs-nav` |
| 3 | `live-badge` | `<span>` | Header / `.controls-bar` | Muestra estado y pulso de conexión WebSocket en vivo |
| 4 | `live-badge-text` | `<span>` | `#live-badge` | Texto dinámico de cotización o estado "En Vivo" |
| 5 | `btn-resultados` | `<button>` | `.tabs-nav` | Navegación a tab `#resultados` |
| 6 | `btn-estadisticas` | `<button>` | `.tabs-nav` | Navegación a tab `#estadisticas` (habilitado tras backtest) |
| 7 | `btn-optimizador` | `<button>` | `.tabs-nav` | Navegación a tab `#optimizador` (habilitado tras backtest) |
| 8 | `smart-dashboard` | `<section>` | `.content-area` | Panel contenedor principal de Modo Inteligente |
| 9 | `btn-smart-run` | `<button>` | `.smart-sidebar` | Dispara `runSmartOptimization()` vía SSE |
| 10 | `smart-preset-select` | `<select>` | `.smart-preset-wrapper` | Selector de presets Barbell (33.33/6, 25/8, 200/1) |
| 11 | `smart-streak-length` | `<input>` | `.smart-numeric-inputs` | Input numérico para racha consecutiva N |
| 12 | `smart-base-capital` | `<input>` | `.smart-numeric-inputs` | Input de capital base a resguardar ($) |
| 13 | `smart-profit-pct` | `<input>` | `.smart-numeric-inputs` | Input de % rendimiento mensual de arbitraje |
| 14 | `smart-risk-capital` | `<input>` | `.smart-numeric-inputs` | Input readonly de capital de riesgo autocalculado |
| 15 | `smart-attempts` | `<input>` | `.smart-numeric-inputs` | Input de cantidad de intentos/balas X |
| 16 | `smart-payout` | `<input>` | `.smart-numeric-inputs` | Input de payout neto del broker |
| 17 | `smart-generations` | `<input>` | `.smart-numeric-inputs` | Input de generaciones evolutivas en Rust |
| 18 | `smart-population` | `<input>` | `.smart-numeric-inputs` | Input de población de individuos en Rust |
| 19 | `smart-console-box` | `<div>` | `.smart-sidebar` | Contenedor de consola de telemetría en tiempo real |
| 20 | `smart-progress-bar-fill` | `<div>` | `.smart-progress-bar-container` | Barra de progreso animada de optimización inteligente |
| 21 | `smart-console-logs` | `<div>` | `#smart-console-box` | Terminal de logs de eventos SSE |
| 22 | `smart-top-5-box` | `<div>` | `.smart-results-area` | Contenedor de ranking Top-5 de estrategias |
| 23 | `smart-top-5-list` | `<div>` | `#smart-top-5-box` | Lista dinámica de botones/chips `.top-strat-pill` |
| 24 | `smart-rec-content` | `<div>` | `.smart-card-rec` | Contenedor de recomendación de rachas y modales |
| 25 | `smart-ladder-content` | `<div>` | `.smart-card-ladder` | Progresión de apuestas Paroli paso a paso |
| 26 | `smart-correlation-canvas` | `<canvas>` | `.smart-row-correlation` | Canvas 2D de heatmap de correlación multiactivo |
| 27 | `smart-selected-assets-table` | `<table>` | `.smart-row-correlation` | Tabla de activos con baja correlación (< 0.40) |
| 28 | `smart-selected-assets-body` | `<tbody>` | `#smart-selected-assets-table` | Cuerpo dinámico de activos evaluados |
| 29 | `smart-equity-chart-canvas` | `<canvas>` | `.smart-row-charts` | Canvas de curva de capital Chart.js (Modo Inteligente) |
| 30 | `smart-mc-chart-canvas` | `<canvas>` | `.smart-row-charts` | Canvas de conos Monte Carlo Chart.js (1,000 caminos) |
| 31 | `smart-asset-selector` | `<select>` | `.smart-row-bottom` | Dropdown de activos para cambiar gráfico de velas |
| 32 | `smart-tv-chart` | `<div>` | `.smart-row-bottom` | Contenedor Lightweight Charts (Modo Inteligente) |
| 33 | `smart-tv-chart-empty` | `<div>` | `#smart-tv-chart` | Overlay "Sin datos" de gráfico de velas |
| 34 | `smart-markov-table` | `<table>` | `.smart-row-bottom` | Tabla de probabilidades condicionales de Markov |
| 35 | `smart-markov-explanation` | `<div>` | `.smart-row-bottom` | Nota explicativa de probabilidades condicionales |
| 36 | `dashboard` | `<section>` | `.content-area` | Panel contenedor de Exploración de Mercado |
| 37 | `pair-selector` | `<select>` | `.controls-bar` | Selector de par de activos en modo avanzado |
| 38 | `interval-selector` | `<select>` | `.controls-bar` | Selector de timeframe de velas |
| 39 | `source-selector` | `<select>` | `.controls-bar` | Selector de origen de datos (historical / live) |
| 40 | `tv-chart` | `<div>` | `#dashboard` | Contenedor Lightweight Charts (Modo Avanzado) |
| 41 | `chart-loader` | `<div>` | `#tv-chart` | Spinner de carga animado |
| 42 | `backtest` | `<section>` | `.content-area` | Panel contenedor de Backtest Manual |
| 43 | `backtest-form` | `<form>` | `.config-panel` | Formulario de configuración de backtest |
| 44 | `sec-strategy` | `<div>` | `#backtest-form` | Subtab pane de estrategia y parámetros |
| 45 | `strategy-selector` | `<select>` | `#sec-strategy` | Selector de estrategia cuantitativa |
| 46 | `dynamic-params` | `<div>` | `#sec-strategy` | Contenedor dinámico de hiperparámetros |
| 47 | `expiry-candles` | `<input>` | `#sec-strategy` | Input de velas de expiración |
| 48 | `payout` | `<input>` | `#sec-strategy` | Input de payout neto en backtest |
| 49 | `sec-barbell` | `<div>` | `#backtest-form` | Subtab pane de gestión Barbell |
| 50 | `group-n-consecutive` | `<div>` | `#sec-barbell` | Wrapper del control de racha consecutiva |
| 51 | `backtest-n-consecutive` | `<input>` | `#group-n-consecutive` | Input de racha N en backtest manual |
| 52 | `backtest-cycle-prob` | `<small>` | `#group-n-consecutive` | Probabilidad calculada de ciclo $WR^N$ |
| 53 | `backtest-bet-fraction` | `<input>` | `#sec-barbell` | Input de fracción de capital por ciclo |
| 54 | `sec-genetic` | `<div>` | `#backtest-form` | Subtab pane de optimización genética en Rust |
| 55 | `gen-generations` | `<input>` | `#sec-genetic` | Generaciones de algoritmo genético manual |
| 56 | `gen-population` | `<input>` | `#sec-genetic` | Población de algoritmo genético manual |
| 57 | `gen-min-trades` | `<input>` | `#sec-genetic` | Frecuencia mínima de trades/día |
| 58 | `optimize-genetic-btn` | `<button>` | `#sec-genetic` | Dispara ejecución genética en Rust `/api/genetic/run-stream` |
| 59 | `genetic-progress-container` | `<div>` | `#sec-genetic` | Contenedor de progreso de optimización genética |
| 60 | `genetic-progress-fill` | `<div>` | `#genetic-progress-container` | Barra de progreso de optimizador genético |
| 61 | `genetic-progress-text` | `<span>` | `#genetic-progress-container` | Texto de % de progreso genético |
| 62 | `genetic-progress-eta` | `<span>` | `#genetic-progress-container` | ETA en segundos de proceso genético |
| 63 | `genetic-feedback` | `<div>` | `#sec-genetic` | Resumen de métricas IS/OOS del mejor genoma |
| 64 | `run-backtest-btn` | `<button>` | `.config-panel` | Botón submit para ejecutar backtest |
| 65 | `save-backtest-btn` | `<button>` | `.config-panel` | Botón para guardar en favoritos |
| 66 | `backtest-progress-container`| `<div>` | `.config-panel` | Contenedor de progreso de backtest manual |
| 67 | `backtest-progress-fill` | `<div>` | `#backtest-progress-container`| Barra de progreso de backtest manual |
| 68 | `backtest-progress-text` | `<span>` | `#backtest-progress-container`| Texto de % de backtest |
| 69 | `backtest-progress-eta` | `<span>` | `#backtest-progress-container`| ETA de backtest |
| 70 | `quick-stats` | `<div>` | `.results-panel` | Contenedor de tarjetas de estadísticas rápidas |
| 71 | `stat-winrate` | `<p>` | `#quick-stats` | Métrica de Win Rate (%) |
| 72 | `stat-trades` | `<p>` | `#quick-stats` | Métrica de total de trades |
| 73 | `stat-pnl` | `<p>` | `#quick-stats` | Métrica de P&L neto |
| 74 | `stat-mw` | `<p>` | `#quick-stats` | Métrica de Max Win Streak |
| 75 | `stat-ml` | `<p>` | `#quick-stats` | Métrica de Max Loss Streak |
| 76 | `equity-chart` | `<canvas>` | `.results-panel` | Canvas de curva de capital (Backtest Manual) |
| 77 | `trades-table` | `<table>` | `.results-panel` | Tabla interactiva de operaciones |
| 78 | `resultados` | `<section>` | `.content-area` | Panel contenedor de Historial y Favoritos |
| 79 | `btn-clear-history` | `<button>` | `#resultados` | Botón para purgar historial de localStorage |
| 80 | `history-list` | `<div>` | `#resultados` | Lista de optimizaciones automáticas |
| 81 | `saved-list` | `<div>` | `#resultados` | Lista de backtests favoritos |
| 82 | `estadisticas` | `<section>` | `.content-area` | Panel contenedor de Estadísticas Cuantitativas |
| 83 | `autocorr-chart` | `<canvas>` | `#estadisticas` | Gráfica de autocorrelación lags 1-10 |
| 84 | `streaks-chart` | `<canvas>` | `#estadisticas` | Gráfica de distribución de rachas |
| 85 | `hourly-chart` | `<canvas>` | `#estadisticas` | Gráfica de Win Rate por hora |
| 86 | `cond-probs` | `<div>` | `#estadisticas` | Grilla 2x2 de probabilidades condicionales |
| 87 | `market-state-chart` | `<canvas>` | `#estadisticas` | Gráfica de rendimiento por régimen de mercado |
| 88 | `markov-table` | `<table>` | `#estadisticas` | Matriz de transición de Markov completa |
| 89 | `optimizador` | `<section>` | `.content-area` | Panel contenedor del Optimizador de Rachas |
| 90 | `opt-winrate` | `<input>` | `#optimizador` | Win Rate manual (%) |
| 91 | `opt-payout` | `<input>` | `#optimizador` | Payout manual del broker |
| 92 | `opt-base-capital` | `<input>` | `#optimizador` | Capital base a resguardar ($) |
| 93 | `opt-profit-pct` | `<input>` | `#optimizador` | Rendimiento mensual P2P (%) |
| 94 | `opt-risk-capital` | `<input>` | `#optimizador` | Capital de riesgo mensual calculado |
| 95 | `opt-target-capital` | `<input>` | `#optimizador` | Ganancia neta objetivo / duplicación ($) |
| 96 | `opt-attempts` | `<input>` | `#optimizador` | Intentos / ciclos (X) |
| 97 | `btn-calc-streak` | `<button>` | `#optimizador` | Dispara cálculo `/api/optimize-streak` |
| 98 | `streak-progress-container` | `<div>` | `#optimizador` | Contenedor de progreso de optimizador de rachas |
| 99 | `streak-progress-fill` | `<div>` | `#streak-progress-container` | Barra de progreso de optimizador de rachas |
| 100 | `streak-progress-text` | `<span>` | `#streak-progress-container` | Texto de estado de cálculo de racha |
| 101 | `streak-progress-eta` | `<span>` | `#streak-progress-container` | ETA de cálculo de racha |
| 102 | `streak-recommendation-content`| `<div>` | `#optimizador` | Banner de racha recomendada |
| 103 | `bet-ladder-container` | `<div>` | `#optimizador` | Escalera de apuestas detallada |
| 104 | `streak-alternatives-table` | `<table>` | `#optimizador` | Tabla comparativa por Racha N=1..10 |
| 105 | `mc-chart` | `<canvas>` | `#optimizador` | Canvas Monte Carlo 5,000 caminos |

---

### 6.2 Catálogo de Form Controls e Inputs (37 Estáticos + Dinámicos)

| # | Etiqueta | ID | Name | Type | Value por Defecto | Restricciones / Atributos |
|---|---|---|---|---|---|---|
| 1-9 | `<input>` | *(none)* | `smart-universe` | `checkbox` | WTI, NASDAQ, GBPJPY, XAUUSD, DOGEUSDT, ADAUSDT, BTCUSDT, BNBUSDT, ETHUSDT | 8 checked, ETHUSDT unchecked |
| 10 | `<select>` | `smart-preset-select` | *(none)* | `select` | `preset_33_6` | Opciones: `preset_33_6`, `preset_25_8`, `preset_200_1` |
| 11 | `<input>` | `smart-streak-length` | *(none)* | `number` | `3` | `min="1"` `max="15"` |
| 12 | `<input>` | `smart-base-capital` | *(none)* | `number` | `1000` | `min="10"` |
| 13 | `<input>` | `smart-profit-pct` | *(none)* | `number` | `20` | `min="1"` `max="100"` |
| 14 | `<input>` | `smart-risk-capital` | *(none)* | `number` | `200` | `readonly`, `.input-readonly` |
| 15 | `<input>` | `smart-attempts` | *(none)* | `number` | `6` | `min="1"` `max="50"` |
| 16 | `<input>` | `smart-payout` | *(none)* | `number` | `0.85` | `min="0.1"` `max="1.0"` `step="0.01"` |
| 17 | `<input>` | `smart-generations` | *(none)* | `number` | `50` | `min="5"` `max="200"` |
| 18 | `<input>` | `smart-population` | *(none)* | `number` | `150` | `min="10"` `max="500"` |
| 19 | `<select>` | `smart-asset-selector` | *(none)* | `select` | *(dinámico)* | Poblado con activos analizados |
| 20 | `<select>` | `pair-selector` | *(none)* | `select` | `BTCUSDT` | Poblado vía `/api/data/pairs` |
| 21 | `<select>` | `interval-selector` | *(none)* | `select` | `30m` | Opciones: `1d`, `4h`, `1h`, `30m`, `15m`, `5m`, `1m` |
| 22 | `<select>` | `source-selector` | *(none)* | `select` | `historical` | Opciones: `historical`, `live` |
| 23 | `<select>` | `strategy-selector` | *(none)* | `select` | *(dinámico)* | Poblado vía `/api/strategies` |
| 24 | `<input>` | `expiry-candles` | *(none)* | `number` | `1` | `min="1"` |
| 25 | `<input>` | `payout` | *(none)* | `number` | `0.92` | `min="0.1"` `step="0.01"` |
| 26 | `<input>` | `backtest-n-consecutive` | *(none)* | `number` | `4` | `min="1"` `max="15"` |
| 27 | `<input>` | `backtest-bet-fraction` | *(none)* | `number` | `0.10` | `min="0.01"` `max="1.0"` `step="0.01"` |
| 28 | `<input>` | `gen-generations` | *(none)* | `number` | `50` | `min="5"` `max="200"` |
| 29 | `<input>` | `gen-population` | *(none)* | `number` | `150` | `min="10"` `max="500"` |
| 30 | `<input>` | `gen-min-trades` | *(none)* | `number` | `5.0` | `min="0.5"` `step="0.5"` |
| 31 | `<input>` | `opt-winrate` | *(none)* | `number` | `""` | `step="0.01"`, `placeholder="Ej. 65.5"` |
| 32 | `<input>` | `opt-payout` | *(none)* | `number` | `0.85` | `step="0.01"` |
| 33 | `<input>` | `opt-base-capital` | *(none)* | `number` | `1000` | `min="10"` |
| 34 | `<input>` | `opt-profit-pct` | *(none)* | `number` | `20` | `min="1"` `max="100"` |
| 35 | `<input>` | `opt-risk-capital` | *(none)* | `number` | `200` | `readonly` |
| 36 | `<input>` | `opt-target-capital` | *(none)* | `number` | `1000` | `min="50"` |
| 37 | `<input>` | `opt-attempts` | *(none)* | `number` | `5` | `min="1"` `max="50"` |
| *(dinámico)* | `<input>` | `param-${p.name}` | *(none)* | `number` | `p.default` | `data-param="${p.name}"`, `required` |

---

### 6.3 Catálogo de Botones y Handlers (16 Botones Estáticos)

| # | ID / Selector | Clases | Data Attributes | Texto / Etiqueta | Evento Bound |
|---|---|---|---|---|---|
| 1 | `#mode-smart` | `.mode-btn.active` | `data-mode="smart"` | `⚡ Modo Inteligente (Piloto Automático)` | Clic: activa Smart Mode, oculta `.tabs-nav` |
| 2 | `#mode-advanced` | `.mode-btn` | `data-mode="advanced"` | `⚙️ Modo Avanzado (Manual)` | Clic: activa Advanced Mode, muestra `.tabs-nav` |
| 3 | `button[data-tab="dashboard"]` | `.tab-btn` | `data-tab="dashboard"` | `Mercado` | Clic: `switchTab('dashboard')` |
| 4 | `button[data-tab="backtest"]` | `.tab-btn` | `data-tab="backtest"` | `Backtest` | Clic: `switchTab('backtest')` |
| 5 | `#btn-resultados` | `.tab-btn` | `data-tab="resultados"` | `Resultados` | Clic: `switchTab('resultados')` |
| 6 | `#btn-estadisticas` | `.tab-btn` | `data-tab="estadisticas"` | `Estadísticas` | Clic: `switchTab('estadisticas')` |
| 7 | `#btn-optimizador` | `.tab-btn` | `data-tab="optimizador"` | `Optimizador` | Clic: `switchTab('optimizador')` |
| 8 | `#btn-smart-run` | `.btn-primary` | *(none)* | `⚡ Auto-Optimizar Estrategia` | Clic: `runSmartOptimization()` |
| 9 | `button[data-subtab="sec-strategy"]` | `.subtab-btn.active` | `data-subtab="sec-strategy"` | `🔵 Activo y Estrategia` | Clic: muestra subtab `#sec-strategy` |
| 10 | `button[data-subtab="sec-barbell"]` | `.subtab-btn` | `data-subtab="sec-barbell"` | `🟢 Gestión Barbell` | Clic: muestra subtab `#sec-barbell` |
| 11 | `button[data-subtab="sec-genetic"]` | `.subtab-btn` | `data-subtab="sec-genetic"` | `🟣 Búsqueda Genética (Rust)` | Clic: muestra subtab `#sec-genetic` |
| 12 | `#run-backtest-btn` | `.btn-primary` | *(none)* | `⚡ Ejecutar Backtest` | Submit de `#backtest-form` (`runBacktest()`) |
| 13 | `#save-backtest-btn` | `.btn-secondary` | *(none)* | `⭐ Favoritos` | Clic: `saveCurrentBacktest()` |
| 14 | `#optimize-genetic-btn` | `.btn-secondary` | *(none)* | `🚀 Ejecutar Búsqueda Rust` | Clic: `runGeneticOptimizer()` |
| 15 | `#btn-clear-history` | `.btn-secondary` | *(none)* | `Limpiar Historial` | Clic: `clearHistory()` |
| 16 | `#btn-calc-streak` | `.btn-primary` | *(none)* | `Calcular Plan de Rachas` | Clic: `runStreakPlanner()` |

---

## 7. ESTRUCTURA COMPLETA PROPUESTA PARA `templates/index.html`

A continuación se presenta la arquitectura HTML5 integral lista para el constructor:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binarias Simulator - Terminal Cuantitativo Institucional</title>
    
    <!-- Favicons -->
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="apple-touch-icon" href="/static/favicon.png">
    
    <!-- Preconnect & Google Fonts: Inter (UI) + JetBrains Mono (Data & Tabular Numbers) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Design System Global Stylesheet -->
    <link rel="stylesheet" href="/static/css/style.css">
    
    <!-- Third-Party Charting Engines -->
    <script src="https://unpkg.com/lightweight-charts@4/dist/lightweight-charts.standalone.production.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="app-container">
        <!-- Header Institucional Unificado -->
        <header class="app-header">
            <div class="logo">
                <h1>Binarias <span>Simulator</span></h1>
                <span class="badge badge-quant">QUANT TERMINAL PRO</span>
            </div>
            
            <!-- Selector de Modo Híbrido -->
            <div class="mode-switch-container">
                <button class="mode-btn active" id="mode-smart" data-mode="smart">⚡ Modo Inteligente (Piloto Automático)</button>
                <button class="mode-btn" id="mode-advanced" data-mode="advanced">⚙️ Modo Avanzado (Manual)</button>
            </div>
            
            <!-- Telemetría en Vivo y Navegación Avanzada -->
            <div class="header-right-actions" style="display: flex; align-items: center; gap: 12px;">
                <div class="telemetry-badges-group" style="display: flex; align-items: center; gap: 8px;">
                    <div class="status-pill rust-engine-pill" style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); color: var(--accent-green); padding: 3px 10px; border-radius: var(--radius-pill); font-size: 0.72rem; font-weight: 500; display: inline-flex; align-items: center; gap: 5px;">
                        <span class="pulse-dot text-green">●</span>
                        <span>Motor Cuantitativo: <strong>ACTIVO (Rust v1.82)</strong></span>
                    </div>
                    
                    <span id="live-badge" class="live-badge-span" style="display: none;">
                        <span class="pulse-dot">●</span> <span id="live-badge-text">En Vivo</span>
                    </span>
                </div>

                <nav class="tabs-nav" style="display: none;">
                    <button class="tab-btn" data-tab="dashboard">Mercado</button>
                    <button class="tab-btn" data-tab="backtest">Backtest</button>
                    <button class="tab-btn" data-tab="resultados" id="btn-resultados">Resultados</button>
                    <button class="tab-btn" data-tab="estadisticas" id="btn-estadisticas" disabled>Estadísticas</button>
                    <button class="tab-btn" data-tab="optimizador" id="btn-optimizador" disabled>Optimizador</button>
                </nav>
            </div>
        </header>

        <main class="content-area">
            <!-- Pestaña 0: Tablero Inteligente (Smart Mode) -->
            <section id="smart-dashboard" class="tab-pane active">
                <div class="smart-grid">
                    <!-- Control Bar Horizontal de Optimización -->
                    <div class="smart-sidebar glass-card">
                        <div class="smart-header-row">
                            <div class="smart-title-area">
                                <h2>⚡ Optimización Inteligente</h2>
                                <p class="section-desc">
                                    Ingresa los datos de tu capital y el motor cuantitativo evaluará la estrategia óptima usando algoritmos genéticos y simulaciones Monte Carlo, protegiendo tu capital base con ganancias de arbitraje P2P externo.
                                </p>
                            </div>
                            <div class="smart-action-area">
                                <button type="button" class="btn-primary" id="btn-smart-run">
                                    ⚡ Auto-Optimizar Estrategia
                                </button>
                            </div>
                        </div>
                        
                        <div class="smart-inputs-container">
                            <!-- Universo de Activos -->
                            <div class="smart-universe-wrapper">
                                <label class="smart-input-label">Universo de Activos (Selecciona al menos 3)</label>
                                <div class="smart-universe-select">
                                    <label><input type="checkbox" name="smart-universe" value="WTI" checked> WTI <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="NASDAQ" checked> NASDAQ <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="GBPJPY" checked> GBPJPY <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="XAUUSD" checked> XAUUSD <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="DOGEUSDT" checked> DOGEUSDT <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="ADAUSDT" checked> ADAUSDT <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="BTCUSDT" checked> BTCUSDT <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="BNBUSDT" checked> BNBUSDT <span class="asset-wr-badge"></span></label>
                                    <label><input type="checkbox" name="smart-universe" value="ETHUSDT"> ETHUSDT <span class="asset-wr-badge"></span></label>
                                </div>
                            </div>
                            
                            <!-- Preset Selector Barbell -->
                            <div class="smart-preset-wrapper">
                                <label class="smart-input-label" style="color: var(--accent-primary); font-weight: 700; display: flex; align-items: center; gap: 6px;">
                                    🎯 Estrategia de Disparo y Presupuesto de Campaña (Configuración Óptima)
                                    <span class="tooltip">?
                                        <span class="tooltip-text" style="width: 360px;">
                                            <strong>¿Por qué 6 Balas de $33.33 con Racha N=3?</strong><br>
                                            Es la estrategia matemáticamente más rápida, robusta y equilibrada.<br><br>
                                            • <strong>6 Intentos de $33.33</strong> financiada por el 20% de ganancia de arbitraje ($200).<br>
                                            • <strong>Probabilidad de éxito de la campaña: 98.6%</strong>.<br>
                                            • <strong>Retorno por racha victoriosa: +$177.70 netos</strong>.<br>
                                            • Puedes modificar manualmente las balas o la racha (N) en los controles numéricos inferiores en cualquier momento.
                                        </span>
                                    </span>
                                </label>
                                <select id="smart-preset-select" class="form-control">
                                    <option value="preset_33_6" selected>🚀 [MÁXIMA EFICIENCIA QUANT] 6 Balas de $33.33 / Mes (Rachas N=3) ➔ Meta: Duplicación +100% de Patrimonio</option>
                                    <option value="preset_25_8">⚡ [Conservador / 8 Intentos] 8 Balas de $25.00 / Mes (Rachas N=3) ➔ Meta: Duplicación +100% de Patrimonio</option>
                                    <option value="preset_200_1">🎯 [Retorno Directo / 1 Intento] 1 Bala de $200 / Mes (Racha N=3) ➔ Ganancia: +$1,066.33 (Capital Final: $2,066 USDT)</option>
                                </select>
                            </div>

                            <!-- Inputs Numéricos en Fila Grid -->
                            <div class="smart-numeric-inputs">
                                <div class="control-group">
                                    <label for="smart-streak-length">Racha (N)</label>
                                    <input type="number" id="smart-streak-length" value="3" min="1" max="15">
                                </div>
                                
                                <div class="control-group">
                                    <label for="smart-base-capital">Capital Base ($)
                                        <span class="tooltip">?
                                            <span class="tooltip-text">Capital principal a proteger.</span>
                                        </span>
                                    </label>
                                    <input type="number" id="smart-base-capital" value="1000" min="10">
                                </div>
                                
                                <div class="control-group">
                                    <label for="smart-profit-pct">Rend. Mensual (%)</label>
                                    <input type="number" id="smart-profit-pct" value="20" min="1" max="100">
                                </div>
                                
                                <div class="control-group">
                                    <label for="smart-risk-capital">Cap. Riesgo (Arbitraje P2P)
                                        <span class="tooltip">?
                                            <span class="tooltip-text">Ganancias obtenidas por arbitraje P2P externo destinadas a arriesgar en la campaña.</span>
                                        </span>
                                    </label>
                                    <input type="number" id="smart-risk-capital" value="200" readonly class="input-readonly">
                                </div>
                                
                                <div class="control-group">
                                    <label for="smart-attempts">Intentos / Balas (X)</label>
                                    <input type="number" id="smart-attempts" value="6" min="1" max="50">
                                </div>
                                
                                <div class="control-group">
                                    <label for="smart-payout">Payout Broker</label>
                                    <input type="number" id="smart-payout" value="0.85" min="0.1" max="1.0" step="0.01">
                                </div>

                                <div class="control-group">
                                    <label for="smart-generations" style="color: var(--accent-purple);">Generaciones
                                        <span class="tooltip">?
                                            <span class="tooltip-text">Ciclos evolutivos que correrá el motor genético en Rust.</span>
                                        </span>
                                    </label>
                                    <input type="number" id="smart-generations" value="50" min="5" max="200">
                                </div>

                                <div class="control-group">
                                    <label for="smart-population" style="color: var(--accent-purple);">Población
                                        <span class="tooltip">?
                                            <span class="tooltip-text">Cantidad de individuos procesados por generación.</span>
                                        </span>
                                    </label>
                                    <input type="number" id="smart-population" value="150" min="10" max="500">
                                </div>
                            </div>
                        </div>
                        
                        <!-- Consola de Progreso Cyberpunk -->
                        <div class="smart-console-wrapper" id="smart-console-box" style="display: none;">
                            <div class="console-header">
                                <span class="console-dot red"></span>
                                <span class="console-dot yellow"></span>
                                <span class="console-dot green"></span>
                                <span class="console-title">PROCESADOR CUANTITATIVO</span>
                            </div>
                            <div class="smart-progress-bar-container">
                                <div class="smart-progress-bar-fill" id="smart-progress-bar-fill"></div>
                            </div>
                            <div class="console-body" id="smart-console-logs">
                                <!-- Logs dynamically added -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Tablero de Resultados -->
                    <div class="smart-results-area">
                        <!-- Selector de Ranking de Estrategias Optimizadas -->
                        <div class="top-strategies-wrapper glass-card" id="smart-top-5-box" style="display: none;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap; gap: 6px;">
                                <h3 style="font-size: 0.95rem; color: var(--accent-purple); font-weight: 700; display: flex; align-items: center; gap: 6px; margin-bottom: 0;">
                                    🏆 Ranking de Estrategias Optimizadas
                                    <span class="tooltip">?
                                        <span class="tooltip-text">
                                            Ranking cuantitativo de todas las estrategias evaluadas con validación Out-Of-Sample. Haz clic en cualquiera para actualizar automáticamente todas las gráficas, probabilidades y resultados de la pantalla.
                                        </span>
                                    </span>
                                </h3>
                                <span style="font-size: 0.75rem; color: var(--accent-primary); font-weight: 500;">👈 Selecciona una estrategia para alternar el tablero completo</span>
                            </div>
                            <div id="smart-top-5-list">
                                <!-- Dynamic pills -->
                            </div>
                        </div>

                        <!-- Recomendación y Escalera -->
                        <div class="smart-row-top">
                            <div class="chart-card glass-card smart-card-rec">
                                <h3 style="color: var(--accent-primary); font-size: 1rem; margin-bottom: 10px;">📊 Plan de Rachas Optimizado</h3>
                                <div id="smart-rec-content" class="smart-rec-text">
                                    <p class="empty-text">Introduce tus datos a la izquierda y presiona "Auto-Optimizar" para ver el plan.</p>
                                </div>
                            </div>
                            
                            <div class="chart-card glass-card smart-card-ladder">
                                <h3 style="font-size: 1rem; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                                    <span>🪜 Escalera de Apuestas</span>
                                    <span class="tooltip">?
                                        <span class="tooltip-text" style="width: 290px;">
                                            <strong>¿Qué es la Escalera de Apuestas?</strong><br>
                                            Es un plan de interés compuesto (Paroli) para acumular ganancias dentro de una racha.<br><br>
                                            • <strong>¿Qué es N?</strong> Es el número de victorias consecutivas necesarias para completar 1 ciclo.<br>
                                            • <strong>¿Por qué cambia N según la estrategia?</strong> El optimizador calcula matemáticamente la racha óptima N (1, 2, 3...) según la tasa de acierto de cada estrategia para maximizar la rentabilidad esperada.<br>
                                            • <strong>Gestión de Riesgo:</strong> Si pierdes en cualquier paso, solo pierdes 1 intento inicial ($100), jamás todo tu patrimonio.
                                        </span>
                                    </span>
                                </h3>
                                <div id="smart-ladder-content" style="overflow-y: auto; max-height: 380px;">
                                    <p class="empty-text">Sin plan activo.</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Matriz de Correlación y Activos Seleccionados -->
                        <div class="smart-row-correlation">
                            <div class="chart-card glass-card">
                                <h3 style="font-size: 0.95rem; margin-bottom: 10px; color: var(--accent-primary); display: flex; align-items: center; gap: 6px;">
                                    🔥 Heatmap de Correlación de Retornos
                                    <span class="tooltip">?
                                        <span class="tooltip-text">
                                            Muestra la relación estadística entre los activos del universo:<br>
                                            • <strong>1.00</strong>: Se mueven de forma idéntica.<br>
                                            • <strong>0.00</strong>: Movimiento totalmente independiente.<br>
                                            • <strong>&lt; 0.40</strong>: Baja correlación (ideal para diversificar los intentos de la racha sin que caigan todos al mismo tiempo).
                                        </span>
                                    </span>
                                </h3>
                                <div style="flex: 1; min-height: 290px; width: 100%; display: flex; align-items: center; justify-content: center; position: relative;">
                                    <canvas id="smart-correlation-canvas" style="width: 100%; height: 290px; min-height: 290px;"></canvas>
                                </div>
                            </div>
                            
                            <div class="chart-card glass-card">
                                <h3 style="font-size: 0.95rem; margin-bottom: 10px; color: var(--accent-green); display: flex; align-items: center; justify-content: space-between;">
                                    <span style="display: flex; align-items: center; gap: 6px;">
                                        📋 Activos Seleccionados (Filtro &lt; 0.40)
                                        <span class="tooltip">?
                                            <span class="tooltip-text">
                                                Lista de activos filtrados automáticamente por baja correlación. Muestra el rango de fechas históricas evaluadas por activo (~5 años / 1,250 velas diarias).
                                            </span>
                                        </span>
                                    </span>
                                    <span class="badge" style="background: rgba(255,255,255,0.04); color: var(--text-secondary); border: 1px solid var(--border-subtle);">📅 Muestra: 2021 - 2026</span>
                                </h3>
                                <div style="flex: 1; overflow-y: auto; max-height: 290px;">
                                    <table class="markov-table" id="smart-selected-assets-table">
                                        <thead>
                                            <tr>
                                                <th>Activo</th>
                                                <th>Estado</th>
                                                <th style="text-align: right;">Win Rate OOS</th>
                                            </tr>
                                        </thead>
                                        <tbody id="smart-selected-assets-body">
                                            <tr><td colspan="3" class="empty-text">Sin datos</td></tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Gráficas Principales -->
                        <div class="smart-row-charts">
                            <!-- Curva de Capital del Backtest -->
                            <div class="chart-card glass-card">
                                <h3 style="font-size: 0.95rem; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                                    📈 Curva de Capital (Backtest Barbell Histórico)
                                    <span class="tooltip">?
                                        <span class="tooltip-text">
                                            Muestra la evolución del capital a lo largo del tiempo.<br>
                                            <strong>¿Por qué puede decrecer?</strong> Ocurre cuando una racha de N victorias seguidas no se completa a tiempo y se agota el capital de riesgo asignado a ese intento/ciclo.
                                        </span>
                                    </span>
                                </h3>
                                <div class="chart-wrapper">
                                    <canvas id="smart-equity-chart-canvas"></canvas>
                                </div>
                            </div>
                            
                            <!-- Monte Carlo Campaña -->
                            <div class="chart-card glass-card">
                                <h3 style="font-size: 0.95rem; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                                    🎲 Proyección de Crecimiento (Monte Carlo - 1,000 caminos)
                                    <span class="tooltip">?
                                        <span class="tooltip-text">
                                            Simula 1,000 trayectorias aleatorias de tu capital.<br>
                                            <strong>Significado de los percentiles (P):</strong><br>
                                            • <strong>P95 (Verde punteado)</strong>: Escenario muy optimista (el 95% rinde igual o menos).<br>
                                            • <strong>P75 (Verde claro)</strong>: Escenario favorable (75% por debajo).<br>
                                            • <strong>P50 (Azul - Mediana)</strong>: Resultado central / el más probable.<br>
                                            • <strong>P25 (Rojo claro)</strong>: Escenario desfavorable.<br>
                                            • <strong>P5 (Rojo punteado)</strong>: Escenario de máximo riesgo / peor caso (5%).
                                        </span>
                                    </span>
                                </h3>
                                <div class="chart-wrapper">
                                    <canvas id="smart-mc-chart-canvas"></canvas>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Gráfico de Precios con Señales y Markov -->
                        <div class="smart-row-bottom">
                            <div class="chart-card glass-card">
                                <h3 style="font-size: 0.95rem; margin-bottom: 5px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                                    <span style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                                        🕯️ Velas de Precio con Señales:
                                        <select id="smart-asset-selector" class="form-control" style="width: auto; padding: 3px 8px; font-size: 0.82rem; font-weight: 600;"></select>
                                    </span>
                                    <span class="tooltip">?
                                        <span class="tooltip-text">
                                            Selecciona libremente cualquiera de los activos analizados para visualizar sus velas de precio 1D y la ubicación de sus señales de entrada (CALL/PUT).
                                        </span>
                                    </span>
                                </h3>
                                <div class="chart-container" id="smart-tv-chart" style="margin-top: 10px;">
                                    <div id="smart-tv-chart-empty">
                                        <p class="empty-text">Sin datos</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="chart-card glass-card">
                                <h3 style="font-size: 0.95rem; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                                    📊 Matriz de Markov (Estabilidad de Rachas)
                                    <span class="tooltip">?
                                        <span class="tooltip-text">
                                            Calcula la probabilidad condicional de ganar o perder la SIGUIENTE operación dependiendo de si la operación ANTERIOR fue Victoria (Win) o Derrota (Loss).
                                        </span>
                                    </span>
                                </h3>
                                <div style="flex: 1; overflow-y: auto; width: 100%;">
                                    <table class="markov-table" id="smart-markov-table">
                                        <thead>
                                            <tr>
                                                <th>Resultado Anterior</th>
                                                <th style="color: var(--accent-green);">Siguiente: Win (W)</th>
                                                <th style="color: var(--accent-red);">Siguiente: Loss (L)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr><td colspan="3" class="empty-text">Sin datos</td></tr>
                                        </tbody>
                                    </table>
                                    <div id="smart-markov-explanation" style="margin-top: 10px; font-size: 0.72rem; color: var(--text-secondary); line-height: 1.4; padding: 6px 8px; background: rgba(255,255,255,0.02); border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                                        💡 <em>Muestra la probabilidad de la siguiente operación según el resultado previo.</em>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Tab 1: Dashboard (Mercado) -->
            <section id="dashboard" class="tab-pane">
                <div class="controls-bar glass-card">
                    <div class="control-group">
                        <label for="pair-selector">Par
                            <span class="tooltip">?
                                <span class="tooltip-text">El par de criptomonedas o divisa sobre el cual se cargan las velas de precios (ej. BTCUSDT).</span>
                            </span>
                        </label>
                        <select id="pair-selector">
                            <option value="BTCUSDT">BTCUSDT</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="interval-selector">Intervalo
                            <span class="tooltip">?
                                <span class="tooltip-text">La duración de tiempo de cada vela japonesa (ej. 1h o 30m).</span>
                            </span>
                        </label>
                        <select id="interval-selector">
                            <option value="1d">1d</option>
                            <option value="4h">4h</option>
                            <option value="1h">1h</option>
                            <option value="30m" selected>30m</option>
                            <option value="15m">15m</option>
                            <option value="5m">5m</option>
                            <option value="1m">1m</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="source-selector">Fuente de Datos
                            <span class="tooltip">?
                                <span class="tooltip-text">Selecciona si deseas simular usando datos históricos locales estables (recomendado) o datos en vivo vía Binance API.</span>
                            </span>
                        </label>
                        <select id="source-selector">
                            <option value="historical">Histórico (Local)</option>
                            <option value="live">En Vivo (Binance API)</option>
                        </select>
                    </div>
                </div>
                <div class="chart-container glass-card" id="tv-chart">
                    <div class="loading-spinner" id="chart-loader"></div>
                </div>
            </section>

            <!-- Tab 2: Backtest -->
            <section id="backtest" class="tab-pane">
                <div class="backtest-grid">
                    <div class="config-panel glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                                <h2 style="font-size: 1.05rem; color: var(--accent-primary); margin: 0; white-space: nowrap;">⚙️ Configuración</h2>
                                
                                <!-- Sub-Tabs de Navegación -->
                                <div class="subtabs-nav">
                                    <button type="button" class="subtab-btn active" data-subtab="sec-strategy">
                                        🔵 Activo y Estrategia
                                    </button>
                                    <button type="button" class="subtab-btn" data-subtab="sec-barbell">
                                        🟢 Gestión Barbell
                                    </button>
                                    <button type="button" class="subtab-btn" data-subtab="sec-genetic">
                                        🟣 Búsqueda Genética (Rust)
                                    </button>
                                </div>
                            </div>

                            <!-- Botones de Acción Inline -->
                            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                                <button type="submit" form="backtest-form" class="btn-primary" id="run-backtest-btn" style="width: auto; padding: 7px 18px; font-size: 0.82rem;">⚡ Ejecutar Backtest</button>
                                <button type="button" class="btn-secondary" id="save-backtest-btn" style="border-color: var(--accent-green); color: var(--accent-green); width: auto; padding: 7px 14px; font-size: 0.82rem;" disabled>⭐ Favoritos</button>
                            </div>
                        </div>

                        <form id="backtest-form" style="display: flex; flex-direction: column; gap: 10px;">
                            <!-- Sub-Pane 1: Activo y Estrategia -->
                            <div id="sec-strategy" class="subtab-pane active">
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; align-items: end;">
                                    <div class="control-group" style="margin-bottom: 0;">
                                        <label for="strategy-selector">Estrategia
                                            <span class="tooltip">?
                                                <span class="tooltip-text">Selecciona la lógica matemática para la generación de señales. La 'Estrategia Genética Combinada' es la recomendada para cargar los resultados optimizados en Rust.</span>
                                            </span>
                                        </label>
                                        <select id="strategy-selector"></select>
                                    </div>
                                    <div id="dynamic-params" class="dynamic-params">
                                        <!-- Generated inputs go here horizontally -->
                                    </div>
                                    <div class="control-group" style="margin-bottom: 0;">
                                        <label for="expiry-candles">Velas de Expiración
                                            <span class="tooltip">?
                                                <span class="tooltip-text">La cantidad de velas/minutos que transcurren antes de que expire la opción binaria.</span>
                                            </span>
                                        </label>
                                        <input type="number" id="expiry-candles" value="1" min="1">
                                    </div>
                                    <div class="control-group" style="margin-bottom: 0;">
                                        <label for="payout">Payout (%)
                                            <span class="tooltip">?
                                                <span class="tooltip-text">El porcentaje de ganancia neta pagado por el broker (ej. 0.92 para 92%).</span>
                                            </span>
                                        </label>
                                        <input type="number" id="payout" value="0.92" min="0.1" step="0.01">
                                    </div>
                                </div>
                            </div>

                            <!-- Sub-Pane 2: Gestión Barbell -->
                            <div id="sec-barbell" class="subtab-pane">
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; align-items: end;">
                                    <div class="control-group" style="margin-bottom: 0;" id="group-n-consecutive">
                                        <label for="backtest-n-consecutive">Racha N (Victorias consecutivas)
                                            <span class="tooltip">?
                                                <span class="tooltip-text">El número de victorias consecutivas necesarias en el ciclo para consolidar ganancias.</span>
                                            </span>
                                        </label>
                                        <input type="number" id="backtest-n-consecutive" value="4" min="1" max="15">
                                        <small class="info-text" id="backtest-cycle-prob" style="display: block; margin-top: 4px; color: var(--accent-green); font-weight: 500; font-size: 0.72rem;">
                                            Probabilidad de éxito del ciclo: --%
                                        </small>
                                    </div>
                                    <div class="control-group" style="margin-bottom: 0;">
                                        <label for="backtest-bet-fraction">Fracción de Apuesta
                                            <span class="tooltip">?
                                                <span class="tooltip-text">La fracción del capital asignado al ciclo de riesgo que se apuesta en la primera operación.</span>
                                            </span>
                                        </label>
                                        <input type="number" id="backtest-bet-fraction" value="0.10" min="0.01" max="1.0" step="0.01">
                                    </div>
                                </div>
                            </div>

                            <!-- Sub-Pane 3: Búsqueda Genética (Rust) -->
                            <div id="sec-genetic" class="subtab-pane">
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; align-items: end;">
                                    <div class="control-group" style="margin-bottom: 0;">
                                        <label for="gen-generations">Generaciones
                                            <span class="tooltip">?
                                                <span class="tooltip-text">Número de ciclos evolutivos que correrá el algoritmo genético.</span>
                                            </span>
                                        </label>
                                        <input type="number" id="gen-generations" value="50" min="5" max="200">
                                    </div>
                                    <div class="control-group" style="margin-bottom: 0;">
                                        <label for="gen-population">Población
                                            <span class="tooltip">?
                                                <span class="tooltip-text">Cantidad de combinaciones aleatorias iniciales.</span>
                                            </span>
                                        </label>
                                        <input type="number" id="gen-population" value="150" min="10" max="500">
                                    </div>
                                    <div class="control-group" style="margin-bottom: 0;">
                                        <label for="gen-min-trades">Frecuencia Min. (trades/día)
                                            <span class="tooltip">?
                                                <span class="tooltip-text">Número mínimo de trades al día requeridos.</span>
                                            </span>
                                        </label>
                                        <input type="number" id="gen-min-trades" value="5.0" min="0.5" step="0.5">
                                    </div>
                                    <div>
                                        <button type="button" class="btn-secondary" id="optimize-genetic-btn" style="border-color: var(--accent-purple); color: var(--accent-purple); background: rgba(168, 85, 247, 0.1);">🚀 Ejecutar Búsqueda Rust</button>
                                    </div>
                                </div>
                                <div class="progress-container" id="genetic-progress-container" style="display: none;">
                                    <div class="progress-bar-bg">
                                        <div class="progress-bar-fill" id="genetic-progress-fill"></div>
                                    </div>
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 5px; display: flex; justify-content: space-between;">
                                        <span id="genetic-progress-text">Progreso: 0%</span>
                                        <span id="genetic-progress-eta">ETA: --s</span>
                                    </div>
                                </div>
                                <div id="genetic-feedback" style="display: none; font-size: 0.8rem; padding: 10px; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); background: var(--bg-canvas); margin-top: 10px; line-height: 1.4;"></div>
                            </div>

                            <div class="progress-container" id="backtest-progress-container" style="display: none;">
                                <div class="progress-bar-bg">
                                    <div class="progress-bar-fill" id="backtest-progress-fill"></div>
                                </div>
                                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 5px; display: flex; justify-content: space-between;">
                                    <span id="backtest-progress-text">Progreso: 0%</span>
                                    <span id="backtest-progress-eta">ETA: --s</span>
                                </div>
                            </div>
                        </form>
                    </div>
                    
                    <div class="results-panel">
                        <div class="stats-cards" id="quick-stats">
                            <div class="stat-card"><h3>Win Rate</h3><p id="stat-winrate">--</p></div>
                            <div class="stat-card"><h3>Trades</h3><p id="stat-trades">--</p></div>
                            <div class="stat-card"><h3>P&L Neto</h3><p id="stat-pnl">--</p></div>
                            <div class="stat-card"><h3>Max Win Streak</h3><p id="stat-mw">--</p></div>
                            <div class="stat-card"><h3>Max Loss Streak</h3><p id="stat-ml">--</p></div>
                        </div>
                        <div class="equity-chart-container glass-card">
                            <h3>
                                Curva de Capital (Equity Curve)
                                <span class="tooltip">?
                                    <span class="tooltip-text">Muestra cómo sube o baja tu dinero a lo largo del tiempo. Sirve para ver el rendimiento general y si la estrategia es ganadora a largo plazo.</span>
                                </span>
                            </h3>
                            <div class="chart-wrapper">
                                <canvas id="equity-chart"></canvas>
                            </div>
                        </div>
                        <div class="trades-table-container glass-card">
                            <table class="trades-table" id="trades-table">
                                <thead>
                                    <tr>
                                        <th>Fecha</th>
                                        <th>Tipo</th>
                                        <th style="text-align: right;">Precio Entrada</th>
                                        <th style="text-align: right;">Precio Salida</th>
                                        <th>Resultado</th>
                                        <th style="text-align: right;">P&L</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- Populated dynamically -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Tab 2.5: Resultados -->
            <section id="resultados" class="tab-pane">
                <div class="resultados-grid">
                    <!-- Izquierda: Optimizaciones Automáticas -->
                    <div class="resultados-panel glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 8px;">
                            <h2 style="font-size: 1.2rem; color: var(--accent-primary);">⚡ Optimizaciones Automáticas (Historial)</h2>
                            <button type="button" class="btn-secondary" id="btn-clear-history" style="width: auto; padding: 6px 12px; font-size: 0.8rem; border-color: var(--accent-red); color: var(--accent-red);">Limpiar Historial</button>
                        </div>
                        <div class="backtest-list" id="history-list">
                            <p class="empty-text">No hay optimizaciones automáticas registradas.</p>
                        </div>
                    </div>

                    <!-- Derecha: Backtests Manuales & Favoritos -->
                    <div class="resultados-panel glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h2 style="font-size: 1.2rem; color: var(--accent-purple);">⚙️ Backtests Manuales & Favoritos</h2>
                        </div>
                        <div class="backtest-list" id="saved-list">
                            <p class="empty-text">No hay simulaciones manuales o favoritas guardadas.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Tab 3: Estadisticas -->
            <section id="estadisticas" class="tab-pane">
                <div class="stats-grid">
                    <div class="chart-card glass-card">
                        <h3>
                            Autocorrelación (Lags 1-10)
                            <span class="tooltip">?
                                <span class="tooltip-text">Mide si ganar o perder ahora influye en las próximas operaciones. Si las barras son altas, significa que hay patrones repetitivos y las rachas no son por pura suerte.</span>
                            </span>
                        </h3>
                        <div class="chart-wrapper">
                            <canvas id="autocorr-chart"></canvas>
                        </div>
                    </div>
                    <div class="chart-card glass-card">
                        <h3>
                            Distribución de Rachas
                            <span class="tooltip">?
                                <span class="tooltip-text">Muestra cuántas veces seguidas has ganado o perdido. Sirve para saber qué tan largas suelen ser tus rachas buenas y malas y prepararte para ellas.</span>
                            </span>
                        </h3>
                        <div class="chart-wrapper">
                            <canvas id="streaks-chart"></canvas>
                        </div>
                    </div>
                    <div class="chart-card glass-card">
                        <h3>
                            Win Rate por Hora
                            <span class="tooltip">?
                                <span class="tooltip-text">Muestra qué porcentaje de acierto tienes según la hora del día. Sirve para identificar las mejores y peores horas para operar.</span>
                            </span>
                        </h3>
                        <div class="chart-wrapper">
                            <canvas id="hourly-chart"></canvas>
                        </div>
                    </div>
                    <div class="chart-card glass-card">
                        <h3>
                            Probabilidades Condicionales
                            <span class="tooltip">?
                                <span class="tooltip-text">Calcula la probabilidad de ganar o perder dependiendo de si la operación anterior fue ganadora o perdedora. Te ayuda a ver si hay rachas lógicas o si el mercado cambia.</span>
                            </span>
                        </h3>
                        <div class="cond-probs-grid" id="cond-probs">
                            <!-- 2x2 grid -->
                        </div>
                    </div>
                    <div class="chart-card glass-card">
                        <h3>
                            Win Rate por Estado de Mercado
                            <span class="tooltip">?
                                <span class="tooltip-text">Compara tu efectividad cuando el mercado tiene mucha o poca velocidad (volatilidad) y cuando está en tendencia o lateral. Sirve para saber en qué condiciones te va mejor.</span>
                            </span>
                        </h3>
                        <div class="chart-wrapper">
                            <canvas id="market-state-chart"></canvas>
                        </div>
                    </div>
                    <div class="chart-card glass-card">
                        <h3>
                            Matriz de Transición (Markov)
                            <span class="tooltip">?
                                <span class="tooltip-text">Te muestra la probabilidad exacta de pasar de una victoria a otra victoria (o derrota), y de una derrota a otra. Sirve para entender cómo se encadenan tus resultados.</span>
                            </span>
                        </h3>
                        <div style="flex: 1; overflow-y: auto; width: 100%;">
                            <table class="markov-table" id="markov-table">
                                <!-- populated -->
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Tab 4: Optimizador -->
            <section id="optimizador" class="tab-pane">
                <div class="optimizer-grid">
                    <div class="optimizer-sidebar glass-card">
                        <h2>Plan de Rachas (Arbitraje)</h2>
                        <div class="control-group">
                            <label for="opt-winrate">Win Rate de la Estrategia (%)
                                <span class="tooltip">?
                                    <span class="tooltip-text">La efectividad de acierto histórica de la estrategia cargada del backtest.</span>
                                </span>
                            </label>
                            <input type="number" id="opt-winrate" step="0.01" placeholder="Ej. 65.5">
                        </div>
                        <div class="control-group">
                            <label for="opt-payout">Payout del Broker (ej. 0.85)
                                <span class="tooltip">?
                                    <span class="tooltip-text">El porcentaje neto pagado por el broker por cada operación ganada (85% = 0.85).</span>
                                </span>
                            </label>
                            <input type="number" id="opt-payout" step="0.01" value="0.85">
                        </div>
                        <hr>
                        <div class="control-group">
                            <label for="opt-base-capital">💰 Capital Base (P2P Arbitraje, $)
                                <span class="tooltip">?
                                    <span class="tooltip-text">Tu capital principal resguardado en arbitraje P2P (ej. $1000). Este es el patrimonio que quieres DUPLICAR. No se arriesga.</span>
                                </span>
                            </label>
                            <input type="number" id="opt-base-capital" value="1000" min="10">
                        </div>
                        <div class="control-group">
                            <label for="opt-profit-pct">📈 Rendimiento Mensual Arbitraje (%)
                                <span class="tooltip">?
                                    <span class="tooltip-text">El % mensual que genera tu P2P (ej. 20% = $200 de ganancia). ESTE dinero es el que arriesgas en opciones binarias.</span>
                                </span>
                            </label>
                            <input type="number" id="opt-profit-pct" value="20" min="1" max="100">
                        </div>
                        <div class="control-group">
                            <label for="opt-risk-capital">🎯 Capital de Riesgo Mensual (auto, $)
                                <span class="tooltip">?
                                    <span class="tooltip-text">Ganancia mensual de arbitraje que asignas a opciones binarias. Autocalculado (Base × Rendimiento%). Si pierdes todo, tu capital base sigue intacto.</span>
                                </span>
                            </label>
                            <input type="number" id="opt-risk-capital" value="200" readonly class="input-readonly">
                        </div>
                        <hr>
                        <div class="control-group">
                            <label for="opt-target-capital" style="color: var(--accent-green); font-weight: 700;">🏆 Meta: Duplicar Patrimonio (Ganancia Neta Objetivo, $)
                                <span class="tooltip">?
                                    <span class="tooltip-text">Ganancia neta que debes lograr con las rachas para DUPLICAR tu capital base. Por defecto = Capital Base ($1000). Si logras esto, tu patrimonio pasa de $1000 a $2000+.</span>
                                </span>
                            </label>
                            <input type="number" id="opt-target-capital" value="1000" min="50" style="border-color: var(--accent-green); color: var(--accent-green); font-weight: 700;">
                            <small style="color: var(--text-secondary); margin-top: 4px; display: block; font-size: 0.72rem;">💡 Mantén igual al Capital Base para calcular duplicación exacta</small>
                        </div>
                        <div class="control-group">
                            <label for="opt-attempts">Intentos / Ciclos (X)
                                <span class="tooltip">?
                                    <span class="tooltip-text">El número de intentos en que vas a dividir tu capital de riesgo mensual (ej. 5 intentos de $40).</span>
                                </span>
                            </label>
                            <input type="number" id="opt-attempts" value="5" min="1" max="50">
                        </div>
                        
                        <button class="btn-primary" id="btn-calc-streak" style="background: linear-gradient(135deg, var(--accent-green) 0%, #059669 100%); color: #080b11; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);">Calcular Plan de Rachas</button>
                        <div class="progress-container" id="streak-progress-container" style="display: none;">
                            <div class="progress-bar-bg">
                                <div class="progress-bar-fill" id="streak-progress-fill" style="background: var(--accent-green);"></div>
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 5px; display: flex; justify-content: space-between;">
                                <span id="streak-progress-text">Progreso: 0%</span>
                                <span id="streak-progress-eta">ETA: --s</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="optimizer-charts">
                        <!-- Tarjeta de Plan Recomendado -->
                        <div class="chart-card glass-card" style="grid-column: span 2; height: auto; min-height: auto;">
                            <h2 style="font-size: 1.15rem; color: var(--accent-primary); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                                📊 Plan de Rachas Recomendado
                            </h2>
                            <div id="streak-recommendation-content">
                                <p class="empty-text" style="text-align: left; padding: 10px 0;">Ejecuta "Calcular Plan de Rachas" para ver la recomendación óptima para tu capital de riesgo.</p>
                            </div>
                        </div>

                        <!-- Escalera de Apuestas -->
                        <div class="chart-card glass-card">
                            <h3>
                                🪜 Escalera de Apuestas Paso a Paso
                                <span class="tooltip">?
                                    <span class="tooltip-text">Sigue esta progresión de apuestas en tu broker. Si ganas todas las operaciones de la racha de forma consecutiva, completas el ciclo con éxito y retiras. Si pierdes alguna operación, pierdes ese intento y comienzas el siguiente intento desde el Paso 1.</span>
                                </span>
                            </h3>
                            <div id="bet-ladder-container" style="overflow-y: auto; max-height: 380px; padding-right: 5px;">
                                <p class="empty-text">No hay plan activo.</p>
                            </div>
                        </div>

                        <!-- Tabla Comparativa de Alternativas -->
                        <div class="chart-card glass-card">
                            <h3>
                                🔍 Tabla Comparativa por Racha (N)
                                <span class="tooltip">?
                                    <span class="tooltip-text">Compara qué pasa con diferentes tamaños de rachas (N). A menor racha, mayor probabilidad de éxito pero menor multiplicación del capital. La racha recomendada se resalta en verde.</span>
                                </span>
                            </h3>
                            <div style="flex: 1; overflow-y: auto; width: 100%;">
                                <table class="n-table" id="streak-alternatives-table">
                                    <thead>
                                        <tr>
                                            <th>Racha (N)</th>
                                            <th style="text-align: right;">P(1 Racha)</th>
                                            <th style="text-align: right;">M (Rachas)</th>
                                            <th style="text-align: right;">P(Duplicación)</th>
                                            <th style="text-align: right;">Apuesta</th>
                                            <th style="text-align: right;">Final</th>
                                            <th style="text-align: right;">EV (USD)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr><td colspan="7" class="empty-text">Sin datos</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- Monte Carlo de Campaña (Percentiles) -->
                        <div class="chart-card glass-card" style="grid-column: span 2;">
                            <h3>
                                📈 Proyección de Crecimiento de Campaña (Monte Carlo)
                                <span class="tooltip">?
                                    <span class="tooltip-text">Simulación de 5,000 campañas aleatorias del plan de rachas. Muestra cómo se comportaría tu capital de riesgo de $200 a lo largo de los intentos. Si cruzas la meta de $1000, ganas. Si tocas $0 en todos los intentos, quiebras.</span>
                                </span>
                            </h3>
                            <div class="chart-wrapper">
                                <canvas id="mc-chart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>
    
    <!-- Application Scripts -->
    <script src="/static/js/charts.js"></script>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

---

## 8. MÉTODO DE VERIFICACIÓN INDEPENDIENTE

Para validar la correcta implementación del Milestone 2:

### 8.1 Verificación de Preservación de IDs y Form Inputs (Automática)
Ejecutar el siguiente script de verificación en PowerShell para garantizar cero IDs faltantes:

```powershell
$expectedIds = @(
    "mode-smart", "mode-advanced", "live-badge", "live-badge-text", "btn-resultados", "btn-estadisticas", "btn-optimizador",
    "smart-dashboard", "btn-smart-run", "smart-preset-select", "smart-streak-length", "smart-base-capital", "smart-profit-pct",
    "smart-risk-capital", "smart-attempts", "smart-payout", "smart-generations", "smart-population", "smart-console-box",
    "smart-progress-bar-fill", "smart-console-logs", "smart-top-5-box", "smart-top-5-list", "smart-rec-content",
    "smart-ladder-content", "smart-correlation-canvas", "smart-selected-assets-table", "smart-selected-assets-body",
    "smart-equity-chart-canvas", "smart-mc-chart-canvas", "smart-asset-selector", "smart-tv-chart", "smart-tv-chart-empty",
    "smart-markov-table", "smart-markov-explanation", "dashboard", "pair-selector", "interval-selector", "source-selector",
    "tv-chart", "chart-loader", "backtest", "backtest-form", "sec-strategy", "strategy-selector", "dynamic-params",
    "expiry-candles", "payout", "sec-barbell", "group-n-consecutive", "backtest-n-consecutive", "backtest-cycle-prob",
    "backtest-bet-fraction", "sec-genetic", "gen-generations", "gen-population", "gen-min-trades", "optimize-genetic-btn",
    "genetic-progress-container", "genetic-progress-fill", "genetic-progress-text", "genetic-progress-eta", "genetic-feedback",
    "run-backtest-btn", "save-backtest-btn", "backtest-progress-container", "backtest-progress-fill", "backtest-progress-text",
    "backtest-progress-eta", "quick-stats", "stat-winrate", "stat-trades", "stat-pnl", "stat-mw", "stat-ml", "equity-chart",
    "trades-table", "resultados", "btn-clear-history", "history-list", "saved-list", "estadisticas", "autocorr-chart",
    "streaks-chart", "hourly-chart", "cond-probs", "market-state-chart", "markov-table", "optimizador", "opt-winrate",
    "opt-payout", "opt-base-capital", "opt-profit-pct", "opt-risk-capital", "opt-target-capital", "opt-attempts",
    "btn-calc-streak", "streak-progress-container", "streak-progress-fill", "streak-progress-text", "streak-progress-eta",
    "streak-recommendation-content", "bet-ladder-container", "streak-alternatives-table", "mc-chart"
)

$actualHtml = Get-Content .\templates\index.html -Raw
$missing = @()
foreach ($id in $expectedIds) {
    if ($actualHtml -notmatch "id=['`"]$id['`"]") {
        $missing += $id
    }
}
if ($missing.Count -eq 0) {
    Write-Host "✅ VERIFICACIÓN EXITOSA: 100% de los 105 IDs presentes en index.html" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Faltan $($missing.Count) IDs: $($missing -join ', ')" -ForegroundColor Red
}
```

### 8.2 Verificación de la Suite de Pruebas Backend
Ejecutar la suite de tests existente para certificar que el servidor Flask y endpoints sirven la plantilla sin excepciones:

```powershell
pytest tests/ -v
```

---

## 9. CONCLUSIÓN Y ENTREGABLES

El presente plan establece la hoja de ruta exhaustiva e inequívoca para la ejecución del **Milestone 2**. La arquitectura HTML5 especificada:
1. Elimina todo elemento de fatiga visual y adopta el sistema de diseño Slate & Obsidian.
2. Garantiza la carga de las fuentes Google Fonts `Inter` y `JetBrains Mono`.
3. Ofrece una composición de alta densidad en Modo Inteligente con presets Barbell y telemetría en tiempo real.
4. Mantiene intactos el 100% de los 105 IDs estáticos, 37 controles de formulario y 16 botones de acción.
