# Análisis Detallado de Arquitectura UI/UX y Flujos de Interacción Frontend
**Módulo:** `static/js/app.js`, `templates/index.html`, `app.py`, `static/js/charts.js`  
**Fecha:** 2026-08-16  
**Investigador:** `explorer_m3_app` (Teamwork Explorer Archetype)  
**Milestone:** M3 (UI/Frontend, Charting & App Interaction Layer)

---

## Resumen Ejecutivo

Se realizó una investigación exhaustiva del código fuente del frontend (`static/js/app.js`, `templates/index.html`, `static/js/charts.js`) y del backend de streaming / REST de Flask (`app.py`). 

La aplicación opera como una Single-Page Application (SPA) con dos modos principales:
1. **Modo Inteligente (`#mode-smart`)**: Piloto automático 1-click para optimización de cartera multi-activo con algoritmo genético en Rust v1.82, selección por matriz de correlación de Pearson, simulación Barbell multi-activo, ranking dinámico de estrategias (Top 5+), escaleras Paroli compuestas, matrices de Markov y proyecciones Monte Carlo de 5,000 caminos vía SSE (`/api/smart-optimize-v2-stream`).
2. **Modo Avanzado (`#mode-advanced`)**: Control granular manual para pares específicos, intervalos, hiperparámetros dinámicos de estrategias, backtest Barbell individual con streaming SSE (`/api/backtest-stream`), búsqueda genética aislada en Rust vía SSE (`/api/genetic/run-stream`), planificador de rachas (`/api/optimize-streak`), y visualización estadística diagnóstica completa.

---

## 1. Smart Mode UI: Flujo de Interacción y Telemetría

### 1.1. Selector de Presets Barbell (`#smart-preset-select`)
- **Ubicación DOM**: `templates/index.html:101-120`
- **Controlador JS**: `static/js/app.js:1940-1967`
- **Mecanismo**:
  - Evento `change` sincroniza en tiempo real los inputs numéricos:
    - `preset_33_6`: `#smart-attempts = 6`, `#smart-streak-length = 3` (6 balas de $33.33 / mes, Racha N=3).
    - `preset_25_8`: `#smart-attempts = 8`, `#smart-streak-length = 3` (8 balas de $25.00 / mes, Racha N=3).
    - `preset_200_1`: `#smart-attempts = 1`, `#smart-streak-length = 3` (1 bala directa de $200).
  - Se ejecuta sincronización inicial durante `DOMContentLoaded` para garantizar coherencia desde el arranque.

### 1.2. Universo de Activos (`input[name="smart-universe"]`) y Validación
- **Ubicación DOM**: `templates/index.html:87-98`
- **Controlador JS**: `static/js/app.js:2017-2025`, `2093-2113`
- **Mecanismo**:
  - Checkboxes con 9 activos preconfigurados (WTI, NASDAQ, GBPJPY, XAUUSD, DOGEUSDT, ADAUSDT, BTCUSDT, BNBUSDT, ETHUSDT).
  - Al presionar `#btn-smart-run`, valida que al menos 3 activos estén marcados; de lo contrario aborta y notifica al usuario.
  - Al completarse el stream, los spans `.asset-wr-badge` adyacentes a cada checkbox se actualizan dinámicamente con la tasa de acierto OOS (`asset_win_rates`) y estrellas de rendimiento (`⭐⭐⭐ >=70%` en dorado `#fbbf24`, `⭐⭐ >=60%` en celeste `#38bdf8`, `⭐` en verde `#00f5a0`).

### 1.3. Live Sync de Capital de Riesgo (`#smart-risk-capital`)
- **Ubicación DOM**: `templates/index.html:129-150`
- **Controlador JS**: `static/js/app.js:524-536`
- **Mecanismo**:
  - Escucha eventos `input` en `#smart-base-capital` (def: $1000) y `#smart-profit-pct` (def: 20%).
  - Calcula en tiempo real: `risk = (base * pct) / 100` y actualiza el input de sólo lectura `#smart-risk-capital` ($200.00).

### 1.4. Conexión Streaming SSE (`/api/smart-optimize-v2-stream`)
- **Ubicación Backend**: `app.py:1413-2083`
- **Controlador JS**: `static/js/app.js:1969-2581`
- **Parámetros**: `base_capital`, `profit_pct`, `attempts`, `payout`, `streak_length`, `generations`, `population`, `universe` (JSON).
- **Tipos de Eventos SSE**:
  1. `log`: Mensaje de progreso textual para la consola.
  2. `progress`: Objeto con `progress` (0% a 100%), `eta` (segundos restantes estimados) y `log`.
  3. `error`: Notificación de fallo (cierra stream y reactiva botón).
  4. `result`: Payload final con `streak_plan`, `top_strategies`, `correlation_matrix`, `selected_assets`, `asset_win_rates`, `asset_info`, `mc_paths`, `sim_summary`, `equity_curve`, `trades`, `signals`.

### 1.5. Consola Cuantitativa Cyberpunk (`#smart-console-box`, `#smart-console-logs`, `#smart-progress-bar-fill`)
- **Ubicación DOM**: `templates/index.html:182-196`
- **Controlador JS**: `static/js/app.js:1990-2014`
- **Mecanismo**:
  - Al iniciar la optimización, se hace visible `#smart-console-box` y se hace scroll suave.
  - La barra `#smart-progress-bar-fill` anima su ancho entre 0% y 100% con transiciones CSS.
  - La función `log(text, type)` crea elementos `.console-log-line` con timestamps `[HH:MM:SS]` formateados y auto-scroll vertical (`consoleLogs.scrollTop = consoleLogs.scrollHeight`).

### 1.6. Ranking Dinámico de Estrategias (`#smart-top-5-box`, `#smart-top-5-list`)
- **Ubicación DOM**: `templates/index.html:201-217`
- **Controlador JS**: `static/js/app.js:2116-2467`
- **Mecanismo**:
  - Backend evalúa más de 12 perfiles de estrategia (S/R Cuántico, Mean Reversion, ISLG/RS Liquidity, Daily Confluence, Volatility Squeeze ML, RSI Extremes, Bollinger Bounce, DEESR, Climax Reversal, MTF TCVE, EMA Cross, Genetic Composite) en el universo no correlacionado y los ordena descendentemente por Win Rate OOS.
  - El frontend renderiza píldoras interactivas con insignias (🥇, 🥈, 🥉, #N), nombre, Win Rate OOS, total de operaciones y probabilidad de racha.
  - Al hacer clic en cualquier píldora:
    - Se actualiza el estilo activo (borde violeta `#a371f7`, fondo elevado).
    - Se invoca `renderStrategyView(selectedStrat)`, refrescando instantáneamente:
      1. Plan de rachas recomendado (`#smart-rec-content`).
      2. Escalera de apuestas Paroli (`#smart-ladder-content`).
      3. Curva de capital (`#smart-equity-chart-canvas`).
      4. Monte Carlo (`#smart-mc-chart-canvas`).
      5. Velas de precio con señales del activo objetivo (`#smart-tv-chart`).
      6. Matriz de transición de Markov (`#smart-markov-table`) y su explicación (`#smart-markov-explanation`).

### 1.7. Escalera de Apuestas Paroli (`#smart-ladder-content`)
- **Ubicación DOM**: `templates/index.html:228-244`
- **Controlador JS**: `static/js/app.js:2234-2279`
- **Mecanismo**:
  - Renderiza cada paso del ciclo Paroli: número de operación (1 a N), importe de entrada (`bet_size`), retorno neto si gana (`payout_return`), y monto acumulado para la siguiente operación.
  - Incluye paso final de consolidación (`ladder-step completed`) que indica el capital final alcanzado, la ganancia neta retirada y el reinicio del ciclo.

### 1.8. Matriz de Markov (`#smart-markov-table`, `#smart-markov-explanation`)
- **Ubicación DOM**: `templates/index.html:356-382`
- **Controlador JS**: `static/js/app.js:2362-2408`
- **Mecanismo**:
  - Muestra probabilidades condicionales: `P(W|W)` (Win tras Win), `P(L|W)` (Loss tras Win), `P(W|L)` (Win tras Loss), `P(L|L)` (Loss tras Loss).
  - Cuadro explicativo dinámico que detalla la probabilidad por trade individual en contraste con la probabilidad global acumulada de la campaña.

### 1.9. Tabla de Activos Seleccionados (`#smart-selected-assets-table`, `#smart-selected-assets-body`)
- **Ubicación DOM**: `templates/index.html:266-292`
- **Controlador JS**: `static/js/app.js:2474-2524`
- **Mecanismo**:
  - Activos no correlacionados (<0.65 threshold) se marcan con badge verde "No Correlacionado", mostrando rango temporal (~2021-2026, 1,250 velas) y Win Rate OOS con desglose de operaciones ganadas/totales.
  - Activos correlacionados descartados se muestran al final atenuados (opacidad 0.5) con etiqueta roja "Descartado (Correlacionado)".

---

## 2. Advanced Mode UI: Flujo de Interacción Manual

### 2.1. Selector de Par, Temporalidad y Fuente
- **Ubicación DOM**: `templates/index.html:390-428`
- **Controlador JS**: `static/js/app.js:686-831`
- **Mecanismo**:
  - `#pair-selector`: Carga pares desde `/api/data/pairs`.
  - `#interval-selector`: Carga intervalos disponibles ordenados (`1d`, `4h`, `2h`, `1h`, `30m`, `15m`, `5m`, `3m`, `1m`).
  - `#source-selector`: Permite elegir entre `historical` (CSV local) o `live` (Binance API / WebSocket).
  - `updatePairTimeframeRestrictions()`: Activos tradicionales/Forex (sin sufijo `USDT`) se restringen automáticamente a temporalidad `1d` y fuente histórica.

### 2.2. Parámetros Dinámicos de Estrategia (`#dynamic-params`)
- **Ubicación DOM**: `templates/index.html:475-477`
- **Controlador JS**: `static/js/app.js:875-893`
- **Mecanismo**:
  - Al cambiar `#strategy-selector`, consulta el schema (`get_params_schema()`) y renderiza dinámicamente inputs numéricos con atributos `data-param`, valores por defecto, mínimos, máximos y tooltips explicativos.

### 2.3. Ejecución de Backtest Streaming (`/api/backtest-stream`)
- **Ubicación Backend**: `app.py:2086-2260`
- **Controlador JS**: `static/js/app.js:897-1043`
- **Mecanismo**:
  - Form submit recolecta los valores dinámicos de `#dynamic-params`, expiry, payout, modo Barbell, racha N y fracción de apuesta.
  - Abre EventSource a `/api/backtest-stream`.
  - Actualiza la barra `#backtest-progress-fill` y el tiempo restante ETA.
  - Al recibir `result`, invoca:
    - `displayBacktestResults(data)`: Actualiza tarjetas de estadísticas rápidas (`#stat-winrate`, `#stat-trades`, `#stat-pnl`, `#stat-mw`, `#stat-ml`), curva de equidad (`#equity-chart`) y tabla de 100 trades (`#trades-table`).
    - `displayStatistics(stats)`: Actualiza gráficos de autocorrelación (`#autocorr-chart`), distribución de rachas (`#streaks-chart`), winrate horario (`#hourly-chart`), probabilidades condicionales (`#cond-probs`), estados de mercado (`#market-state-chart`) y matriz de Markov (`#markov-table`).
    - Añade marcadores de señales de compra/venta y salida en el gráfico de velas.
    - Habilita pestañas antes deshabilitadas (`#btn-estadisticas`, `#btn-optimizador`).

### 2.4. Optimizador Genético en Rust (`/api/genetic/run-stream`)
- **Ubicación Backend**: `app.py:2263-2347`
- **Controlador JS**: `static/js/app.js:1824-1938`
- **Mecanismo**:
  - Envía parámetros (`generations`, `population`, `min_trades`, `expiry`, etc.) al subproceso de Rust (`genetic_optimizer.exe`).
  - Transmite el progreso generación a generación vía SSE (`PROGRESS: gen/total`).
  - Al finalizar, selecciona automáticamente la estrategia `genetic_composite`, inyecta los genes óptimos calculados en `#dynamic-params`, presenta el cuadro de feedback con métricas OOS vs IS (`#genetic-feedback`) y dispara automáticamente el backtest para mostrar los resultados en pantalla.

### 2.5. Planificador de Rachas (`/api/optimize-streak`) y Monte Carlo (`/api/montecarlo`)
- **Ubicación Backend**: `app.py:505-544`, `645-680`
- **Controlador JS**: `static/js/app.js:1198-1427`
- **Mecanismo**:
  - `#btn-calc-streak` envía POST a `/api/optimize-streak` con win rate, payout broker, capital base, % rendimiento mensual, capital de riesgo, capital objetivo y número de intentos.
  - Renderiza recomendación óptima (`#streak-recommendation-content`), escalera de apuestas (`#bet-ladder-container`) y tabla comparativa de N=1..15 (`#streak-alternatives-table`).
  - Ejecuta simulación Monte Carlo de 5,000 caminos (`simulateCampaignMonteCarlo`) calculando percentiles P95, P75, P50 (mediana), P25 y P5 en `#mc-chart`.

### 2.6. Tabla de Operaciones (`#trades-table`) e Interacción con el Gráfico
- **Ubicación DOM**: `templates/index.html:596-613`
- **Controlador JS**: `static/js/app.js:1077-1136`
- **Mecanismo**:
  - Muestra las últimas 100 operaciones con fecha, dirección (CALL/PUT), precio de entrada, precio de salida, resultado (WIN/LOSS) y P&L.
  - Al hacer clic en cualquier fila de la tabla, resalta la fila y llama a `highlightTradeOnChart` dibujando líneas de precio horizontales punteadas exactas (verde para CALL/WIN, rojo para PUT/LOSS) en el gráfico de velas.

### 2.7. Historial y Favoritos (`#history-list`, `#saved-list`)
- **Ubicación DOM**: `templates/index.html:617-641`
- **Controlador JS**: `static/js/app.js:1441-1820`
- **Mecanismo**:
  - Almacena en `localStorage` (`binsim_history` y `binsim_saved`).
  - Permite guardar en favoritos (`#save-backtest-btn` / `.btn-save-item`), eliminar entradas (`.btn-delete-item`), limpiar historial completo (`#btn-clear-history`).
  - Al hacer clic en cualquier tarjeta del historial/favoritos, `loadBacktestState(backtestObj)` restaura la totalidad de los parámetros del formulario, cambia de pestaña y regenera todos los gráficos y tablas instantáneamente.

---

## 3. Micro-interacciones y Diálogos Modales

### 3.1. Exportación de Pine Script v5 y Prompt para IA
- **Funciones Generadoras**:
  - `generatePineScriptV5(strat)` (`static/js/app.js:5-144`): Genera código Pine Script v5 listo para pegar en el editor de TradingView con `indicator(..., overlay=true)`, inputs tipados, cálculos multitemporales sin look-ahead (`request.security(..., barmerge.lookahead_off)`), condiciones CALL/PUT y alertas nativas `alertcondition`.
  - `generateAIPrompt(strat)` (`static/js/app.js:146-211`): Construye un prompt detallado y estructurado para LLMs (Claude, ChatGPT, DeepSeek) con la especificación matemática, reglas de expiración, pesos y parámetros de la estrategia.
- **Manejadores Globales en Window**:
  - `window.togglePineScriptModal(id)`: Alterna la visibilidad del contenedor modal `#pinescript-box-${id}`.
  - `window.copyPineScript(id)`: Copia el código Pine Script al portapapeles (`navigator.clipboard.writeText`) y notifica confirmación.
  - `window.copyAIPrompt(id)`: Copia el prompt para IA al portapapeles.

### 3.2. Navegación por Pestañas y Modos
- **Selector de Modo Principal**:
  - `#mode-smart`: Muestra `#smart-dashboard`, oculta la barra de navegación avanzada `.tabs-nav`.
  - `#mode-advanced`: Muestra `#dashboard` (o la pestaña activa de avanzado), hace visible `.tabs-nav`.
- **Navegación de Pestañas Avanzadas (`.tabs-nav`)**:
  - Pestañas: `Mercado`, `Backtest`, `Resultados`, `Estadísticas`, `Optimizador`.
  - La función `switchTab(tabId)` activa el panel correspondiente y dispara `applyOptions` + `timeScale().fitContent()` en los gráficos TradingView tras un pequeño delay (50ms) para garantizar renderizado correcto ante cambios de visibilidad del contenedor.
- **Sub-pestañas de Configuración de Backtest (`.subtabs-nav`)**:
  - `🔵 Activo y Estrategia` (`#sec-strategy`), `🟢 Gestión Barbell` (`#sec-barbell`), `🟣 Búsqueda Genética (Rust)` (`#sec-genetic`).
  - Navegación ágil dentro de la tarjeta de configuración sin recargar la página.

---

## 4. WebSocket Feed en Vivo y Telemetría de Conexión

### 4.1. Conexión WebSocket a Binance (`wss://stream.binance.com:9443`)
- **Controlador JS**: `static/js/app.js:251-379`
- **Flujo de Vida**:
  1. Si `#source-selector` está en `live`, `connectLiveStream(pair, interval)` cierra conexiones previas mediante `stopLiveStream()`.
  2. Abre conexión a `wss://stream.binance.com:9443/ws/${streamPair}@kline_${interval}`.
  3. Al abrir (`onopen`), actualiza el badge a "En Vivo (Binance WS)".
  4. Al recibir mensajes (`kline`), procesa `k.o`, `k.h`, `k.l`, `k.c`, `k.v` y timestamp `k.t`.
  5. Determina el color de la vela en tiempo real (verde `#00f5a0`, rojo `#ff4d4d`) e invoca `candleSeries.update(candleWithColor)` y `smartCandleSeries.update(candleWithColor)`.
  6. Actualiza el badge con el precio en tiempo real (ej. `En Vivo: $96,450.20`).

### 4.2. Mecanismo de Resiliencia y Fallback a Polling REST
- **Controlador JS**: `static/js/app.js:380-413`
- **Mecanismo**:
  - Si el WebSocket sufre error (`onerror`) o se cierra inesperadamente (`onclose`) mientras el modo `live` sigue activo, `startFallbackPolling(pair, interval)` toma el control automáticamente.
  - Inicia un timer a 3,000ms consultando `https://api.binance.com/api/v3/klines?symbol=${pair}&interval=${interval}&limit=2`.
  - Actualiza el badge `#live-badge` indicando `En Vivo (Polling)`.

### 4.3. Badge de Estado en Header (`#live-badge`, `#live-badge-text`)
- **Ubicación DOM**: `templates/index.html:48-50`
- **Controlador JS**: `static/js/app.js:269-279`
- **Mecanismo**:
  - Estructurado como un badge institucional con punto pulsante (`.pulse-dot`) y texto dinámico.
  - Se muestra únicamente cuando la fuente de datos está en modo en vivo y se oculta limpiamente al alternar a histórico.

---

## 5. Hallazgos Específicos e Inconsistencias Detectadas

| # | Archivo | Línea(s) | Observación / Inconsistencia | Impacto | Recomendación de Corrección |
|---|---|---|---|---|---|
| 1 | `static/js/app.js` | 1098 | Se llama `highlightTradeOnChart(trade, tvChart, candleSeries)` pasando `tvChart` en vez de `mainChart` | Menor (actualmente la función usa el 3er argumento `seriesObj`), pero es una referencia a una variable no definida | Reemplazar `tvChart` por `mainChart` en línea 1098 |
| 2 | `static/js/app.js` | 224-233, 963, 1214, 1248, 1392, 1491, 1514, 1541, 1873, 2022, 2077 | Uso de `alert()` y `confirm()` nativos del navegador | Experiencia de usuario bloqueante que rompe la estética de terminal oscuro institucional | Crear un sistema de notificaciones Toast no intrusivo y modal de confirmación |
| 3 | `static/js/app.js` | 614-615 | Escucha `#btn-sim-barbell` que no existe en `index.html` (control heredado de versiones previas) | Inocuo (incluye chequeo `if (barbellBtn)`), pero es código muerto | Limpiar o unificar |
| 4 | `static/js/app.js` | 1704-1765 | En `loadBacktestState`, chequeos defensivos para `gn-chart`, `kelly-chart`, `opt-recommendation`, `n-table` | Inocuo (los IDs ya fueron actualizados a `streak-recommendation-content`, etc.), pero conviene consolidar | Mantener soporte defensivo asegurando que los nuevos elementos se rendericen siempre |

---

## 6. Plan de Implementación Concreto para Milestone 3 & 4

### Fase 1: Corrección de Micro-Bugs y Refinamiento de Binding JS
1. Corregir la referencia `tvChart` -> `mainChart` en `static/js/app.js:1098`.
2. Implementar un helper Toast institucional no bloqueante (`showToast(message, type, duration)`) para reemplazar los `alert()` al copiar Pine Script, Prompt de IA y guardar favoritos.

### Fase 2: Robustecimiento de Renderizado de Gráficos y Tablas
1. Verificar sincronización de redibujado de Canvas (`smart-correlation-canvas`) al alternar entre pestañas o redimensionar la ventana (añadir `ResizeObserver` para el contenedor del heatmap).
2. Asegurar que las cifras en todas las tablas de `app.js` apliquen clases `tabular-nums` y alineación a la derecha en columnas numéricas.

### Fase 3: Integración E2E y Pruebas de Estrés
1. Ejecutar el pipeline de pruebas backend (`pytest`) para validar que todos los endpoints SSE y REST respondan con contratos JSON válidos.
2. Comprobar la consola del navegador ante el flujo completo: Modo Inteligente -> Auto-Optimizar -> Cambio a Modo Avanzado -> Ejecutar Backtest -> Búsqueda Genética -> Planificador de Rachas -> Historial.

---
**Fin del Documento de Análisis**
