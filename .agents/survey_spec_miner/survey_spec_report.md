# REPORTE DE ESPECIFICACIÓN TÉCNICA UI/UX: TERMINAL CUANTITATIVO PRO
**Documento de Extracción de Especificaciones de Diseño, Ergonomía Visual, Arquitectura de Componentes y Matriz de Preservación**
*Proyecto: Binary Options Quantitative Terminal & Strategy Simulator*
*Fecha: 2026-08-16 | Estado: Especificación Minada Autoritativa*

---

## 1. RESUMEN EJECUTIVO Y ALCANCE DE LA ESPECIFICACIÓN

El presente documento constituye la especificación canónica y exhaustiva para el rediseño de interfaz de usuario (UI/UX) del **Terminal Cuantitativo de Opciones Binarias y Simulador de Estrategias**, fundamentado en los requerimientos de `ORIGINAL_REQUEST.md` y la investigación científica y ergonómica de `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`.

### 1.1 Objetivo del Rediseño
Transformar el simulador existente en un **Terminal Institucional de Analítica Cuantitativa y Soporte de Decisiones de Alto Rendimiento** (categoría *Institutional-Grade Quantitative Fintech Terminal*), aplicando los más estrictos estándares de la industria (benchmarks: Linear.app, TradingView Pro, Vercel Geist, Bloomberg B-Pipe, Stripe Radar).

### 1.2 Principios Rectores Inmutables
1. **Ergonomía Visual Libre de Fatiga**: Eliminación total del contraste blanco puro sobre negro absoluto (prevención de halación astigmática) y de la vibración óptica por saturación desbalanceada (prevención de cromoestereopsis).
2. **Máxima Precisión Numérica (Data-to-Ink Ratio)**: Uso obligatorio de tipografía monoespaciada con cifras tabulares (`tabular-nums`) en todas las tablas, matrices de Markov, correlaciones y métricas financieras.
3. **Composición de Alta Densidad y Jerarquía 8-Point Grid**: Distribución de controles en un flujo armónico de 1 clic (Modo Inteligente con Presets Pre-calculados) y navegación profunda de análisis (Modo Avanzado).
4. **Preservación Funcional 100% (Zero Regressions)**: Mantenimiento estricto e inviolable de todos los identificadores HTML (`id`, selectores de clase funcionales), campos de formulario, botones de acción, funciones dinámicas JavaScript y contratos de API REST / SSE.

---

## 2. SISTEMA DE DISEÑO VISUAL Y PALETA CROMÁTICA INSTITUCIONAL

### 2.1 Arquitectura de Capas de Superficie (FinTech Slate & Obsidian)
La interfaz se estructura en tres capas de profundidad visual con bordes de 1px translúcidos para generar relieve y jerarquía sin saturar la retina:

| Token / Capa | Código HEX / RGBA | Uso en la Interfaz | Justificación Perceptual |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | `#080b11` | Fondo general de la ventana y viewport | Obsidiana profunda; descanso ocular y eliminación de glare. |
| **Surface Card Base** | `#0e1420` | Tarjetas, contenedores principales y paneles | Slate oscuro; contenedor sólido que delimita módulos con claridad. |
| **Surface Elevated / Nav** | `#141d2e` | Header principal, toolbars, modales flotantes | Elevación sutil que indica interactividad y jerarquía superior. |
| **Surface Hover / Input** | `#1c273d` | Inputs, selects, botones secundarios, hover rows | Respuesta táctil limpia con contraste optimizado frente a la base. |
| **Border Subtle** | `rgba(255, 255, 255, 0.07)` | Delimitación perimetral de módulos y divisores | Borde nítido de 1px que guía el ojo sin generar ruido visual. |
| **Border Active / Focus** | `rgba(56, 189, 248, 0.35)` | Enfoque de inputs, tarjetas activas y tabs | Indicador visual de foco nítido y moderno (Electric Sky). |
| **Overlay / Backdrop** | `rgba(8, 11, 17, 0.85)` | Fondo de modales y tooltips con `backdrop-filter: blur(12px)` | Aislamiento focal sin perder contexto de fondo. |

### 2.2 Jerarquía Tipográfica y Escala de Contraste (WCAG 2.2 AAA & APCA)
Para evitar el "sangrado de luz" (irradiation effect / halación), se prohíbe el uso de `#FFFFFF` puro sobre fondos oscuros:

| Nivel Tipográfico | Token CSS | Código HEX | Razón de Contraste vs `#080b11` | Rol en la Interfaz |
| :--- | :--- | :--- | :--- | :--- |
| **Text Primary** | `--text-primary` | `#f0f6fc` | 15.8:1 (Cumple AAA) | Títulos H1/H2, métricas clave (Win Rate, Capital), valores principales. |
| **Text Secondary** | `--text-secondary` | `#94a3b8` | 7.6:1 (Cumple AAA) | Subtítulos, etiquetas de formulario (`label`), encabezados de tabla. |
| **Text Muted / Tertiary** | `--text-muted` | `#64748b` | 4.6:1 (Cumple AA) | Timestamps, unidades de medida (`USDT`, `s`), ayudas secundarias. |
| **Text Disabled** | `--text-disabled` | `#475569` | 3.1:1 | Estados inactivos, botones deshabilitados, placeholders. |

### 2.3 Acentos Semánticos y Codificación Funcional Calibrada
Los colores funcionales están calibrados entre 65% y 80% de saturación para evitar saturación de conos retinianos:

| Semántica Operativa | Nombre del Token | Código HEX | Rol y Aplicación en Terminal |
| :--- | :--- | :--- | :--- |
| **Acción Primaria / Foco** | `Electric Sky` | `#38bdf8` | Botones primarios, tab activo, links, indicadores de foco. |
| **Ganancia / CALL / Win** | `Cyber Emerald` | `#10b981` | Señales CALL, Win Rate superior a breakeven, percentil P95 Monte Carlo. |
| **Pérdida / PUT / Riesgo** | `Rose Crimson` | `#f43f5e` | Señales PUT, rachas de pérdida, drawdowns, percentil P5 Monte Carlo. |
| **Optimización / Genética** | `Quantum Amethyst` | `#a855f7` | Motor genético en Rust, ranking de estrategias optimizadas, chips de generación. |
| **Alerta / Arbitraje / Paroli** | `Golden Amber` | `#f59e0b` | Balas de capital, advertencias, tasas de rendimiento P2P, alertas de riesgo. |
| **Correlación Neutra / Grid** | `Cool Slate` | `#64748b` | Rejillas de gráficos, ejes de coordenadas, separadores neutros. |

### 2.4 Reglas Neuro-Ópticas y Ergonómicas Estrictas
1. **Regla Anti-Halación**: Prohibido `#FFFFFF` sobre fondos menores a `#111827`. El texto principal debe ser siempre `#f0f6fc` o `#e6edf3`.
2. **Regla Anti-Cromoestereopsis**: Prohibido colocar rojo puro (`#FF0000`) adyacente a azul/púrpura neón (`#0000FF` / `#7F00FF`) sobre fondos oscuros. Todas las señales deben mantener un delta de luminancia uniforme usando la paleta calibrada (`#10b981`, `#f43f5e`, `#38bdf8`, `#a855f7`).
3. **Regla Data-to-Ink (Edward Tufte)**: Ningún gráfico contendrá rejillas saturadas ni gradientes opacos que oculten los datos. Las rejillas tendrán opacidad máxima de `rgba(255, 255, 255, 0.04)` o `rgba(100, 116, 139, 0.15)`.

---

## 3. ARQUITECTURA DE LAYOUT Y SISTEMA DE ESPACIADO 8-POINT GRID

### 3.1 Escala de Espaciado Métrico (8-Point Grid)
El layout se construye con múltiplos matemáticos estrictos de 4px y 8px:

```css
:root {
    --space-1: 4px;   /* Micro-espaciado: iconos, badges internos */
    --space-2: 8px;   /* Separación interna entre controles y chips */
    --space-3: 12px;  /* Padding vertical/horizontal en inputs y botones */
    --space-4: 16px;  /* Padding interno estándar de tarjetas (glass-card) */
    --space-5: 20px;  /* Gaps entre columnas de paneles */
    --space-6: 24px;  /* Separación de secciones principales */
    --space-8: 32px;  /* Margen perimetral de pantalla */
}
```

### 3.2 Geometría y Psicología de Formas (Curvaturas)
* **Contenedores y Tarjetas Principales (`.glass-card`)**: `border-radius: 8px` a `10px`. Acabado técnico y sobrio.
* **Campos de Formulario, Inputs y Botones (`input`, `select`, `.btn-primary`)**: `border-radius: 6px`. Sensación táctil de precisión instrumental.
* **Badges, Chips y Status Pills (`.badge`, `.status-pill`)**: `border-radius: 9999px`. Forma de píldora compacta (altura 18px - 22px).

### 3.3 Estructura del Header Institucional Unificado
El Header debe unificar:
1. **Identidad Visual**: Logotipo "Binarias **Simulator**" con gradiente esmeralda (`#10b981` a `#38bdf8`).
2. **Selector de Modo Híbrido**:
   - `⚡ Modo Inteligente (Piloto Automático)` (`#mode-smart`)
   - `⚙️ Modo Avanzado (Manual)` (`#mode-advanced`)
3. **Telemetría y Estado del Motor**:
   - Badge de Estado del Motor Rust: `⚡ Motor Cuantitativo: ACTIVO` (Pill con micro-punto esmeralda).
   - Badge de Fuente de Datos / Conexión: `#live-badge` con punto pulsante (`.pulse-dot`).

### 3.4 Barra de Control Compacta de Alta Densidad
En el **Modo Inteligente**, la barra superior organiza los parámetros clave en una cuadrícula horizontal de una sola línea de mando:
- **Selector de Presets Barbell**: Dropdown `#smart-preset-select` con estilos visuales destacados en `Electric Sky`.
- **Selector de Universo de Activos**: Checkboxes en chips interactivos con badges de Win Rate OOS (`.asset-wr-badge`).
- **Controles Numéricos Compactos**: Racha (N), Capital Base, Rendimiento Mensual (%), Capital de Riesgo (Auto), Intentos/Balas, Payout, Generaciones y Población de Rust.
- **Botón de Ejecución Primaria**: `#btn-smart-run` ("⚡ Auto-Optimizar Estrategia") con elevación y foco en gradiente `Electric Sky`.

### 3.5 Workspace de Múltiples Paneles Asimétricos
El área de resultados se organiza en paneles adaptativos:
- **Panel Superior**: Ranking de Estrategias Optimizadas Top-N (`#smart-top-5-box`) + Plan de Rachas (`#smart-rec-content`) + Escalera Paroli (`#smart-ladder-content`).
- **Panel Intermedio**: Heatmap de Correlación de Retornos (`#smart-correlation-canvas`) + Tabla de Activos Seleccionados con filtro `< 0.40` (`#smart-selected-assets-table`).
- **Panel de Curvas Cuantitativas**: Curva de Capital Backtest (`#smart-equity-chart-canvas`) + Conos de Crecimiento Monte Carlo 1,000 caminos P5-P95 (`#smart-mc-chart-canvas`).
- **Panel de Validación Técnica**: Gráfico de Velas con Señales TradingView Lightweight Charts (`#smart-tv-chart`) + Matriz de Transición Markoviana (`#smart-markov-table`).

---

## 4. TIPOGRAFÍA Y ARQUITECTURA NUMÉRICA DE DATOS

### 4.1 Familias Tipográficas y Reglas de Carga
```html
<!-- Fuentes de Alta Fidelidad Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- **Tipografía de Interfaz (UI & Labels)**: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`.
- **Tipografía Cuantitativa (Data, Numbers & Tables)**: `'JetBrains Mono', 'Geist Mono', monospace`.

### 4.2 Configuración CSS de Cifras Tabulares (Inviolable)
```css
.tabular-nums, 
.markov-table td, 
.markov-table th, 
.trades-table td, 
.n-table td, 
.stat-card p, 
.console-body {
    font-family: 'JetBrains Mono', monospace;
    font-feature-settings: "tnum" 1, "zero" 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}
```
*Propósito*: Garantizar que cada dígito (0-9) tenga el mismo ancho en píxeles, impidiendo oscilaciones visuales en números dinámicos y asegurando alineación decimal perfecta.

### 4.3 Escala Tipográfica Modular y Densidad de Tablas
| Elemento | Tamaño / Peso | Line-Height | Estilo y Alineación |
| :--- | :--- | :--- | :--- |
| **Display Metric (Win Rate, Total PnL)** | `24px` / `700 Bold` | `1.1` | Tabular numbers, color semántico (`#10b981` / `#f43f5e`) |
| **Section Header (H2)** | `15px` / `600 SemiBold` | `1.3` | Inter, Tracking: `-0.015em`, color `#f0f6fc` |
| **Card Title (H3)** | `13px` / `600 SemiBold` | `1.3` | Inter, color `#f0f6fc` o `#38bdf8` |
| **Table Header (`th`)** | `11px` / `600 SemiBold` | `1.2` | Inter, color `#94a3b8`, padding: `8px 10px`, border-bottom: `1px solid rgba(255,255,255,0.07)` |
| **Table Row Data (`td`)** | `12px` / `400-500` | `1.4` | JetBrains Mono, tabular, padding: `8px 10px`, border-bottom: `1px solid rgba(255,255,255,0.03)` |
| **Table Number Column** | `12px` / `500` | `1.4` | Alineación **Derecha** (`text-align: right`) |
| **Table Text Column** | `12px` / `400` | `1.4` | Alineación **Izquierda** (`text-align: left`) |
| **Console Logs** | `11px` / `400` | `1.45` | JetBrains Mono, color `#38bdf8` / `#10b981` / `#94a3b8` |

---

## 5. TEMAS Y ESPECIFICACIÓN DE SISTEMAS DE GRÁFICOS

### 5.1 TradingView Lightweight Charts (Velas Japonesas y Señales CALL/PUT)
- **Instancias**: `#tv-chart` (Modo Avanzado) y `#smart-tv-chart` (Modo Inteligente).
- **Opciones de Layout**:
  ```javascript
  layout: {
      background: { type: 'solid', color: 'transparent' },
      textColor: '#94a3b8',
      fontSize: 11,
      fontFamily: "'JetBrains Mono', 'Inter', sans-serif"
  }
  ```
- **Rejilla (Gridlines)**:
  ```javascript
  grid: {
      vertLines: { color: 'rgba(255, 255, 255, 0.03)' },
      horzLines: { color: 'rgba(255, 255, 255, 0.03)' }
  }
  ```
- **Serie de Velas (Candlestick Styling)**:
  - `upColor`: `#10b981` (Cyber Emerald)
  - `downColor`: `#f43f5e` (Rose Crimson)
  - `borderVisible`: `false` (o `borderColor: 'transparent'`)
  - `wickUpColor`: `#10b981`
  - `wickDownColor`: `#f43f5e`
- **Marcadores de Señales CALL / PUT (Overlay Badges)**:
  - **CALL**: `position: 'belowBar'`, `color: '#10b981'`, `shape: 'arrowUp'`, `text: 'CALL'`
  - **PUT**: `position: 'aboveBar'`, `color: '#f43f5e'`, `shape: 'arrowDown'`, `text: 'PUT'`
- **Crosshair & Scales**:
  - `crosshair.mode`: `LightweightCharts.CrosshairMode.Normal`
  - `crosshair.vertLine.color`: `rgba(56, 189, 248, 0.4)`
  - `crosshair.horzLine.color`: `rgba(56, 189, 248, 0.4)`
  - `rightPriceScale.borderColor`: `rgba(255, 255, 255, 0.07)`
  - `timeScale.borderColor`: `rgba(255, 255, 255, 0.07)`

### 5.2 Chart.js: Curva de Capital (Equity Curve)
- **Instancias**: `#smart-equity-chart-canvas` y `#equity-chart`.
- **Configuración Visual**:
  - `type`: `'line'`
  - `borderColor`: `'#38bdf8'` (Electric Sky)
  - `backgroundColor`: Gradiente vertical de `rgba(56, 189, 248, 0.18)` a `rgba(56, 189, 248, 0.00)`
  - `borderWidth`: `2`
  - `fill`: `true`
  - `tension`: `0.1` (suavizado sutil de spline sin deformar picos reales)
  - `pointRadius`: `0` (hover radius `4px`)
- **Escalas Dinámicas y Eje Y Logarítmico**:
  - Auto-escalado a escala logarítmica si `(maxVal / minVal) > 100` y `minVal >= 1.0`.
  - Formato de ticks en Eje Y: `$1k`, `$10k`, `$100k`, `$1M` usando función `formatYAxisTick`.
  - Rejillas: `color: 'rgba(255, 255, 255, 0.04)'`.

### 5.3 Chart.js: Conos de Crecimiento Monte Carlo (1,000 Caminos P5-P95)
- **Instancias**: `#smart-mc-chart-canvas` y `#mc-chart`.
- **Paleta de Percentiles**:
  - **P95 (Optimista Superior)**: `borderColor: '#10b981'`, `borderDash: [4, 4]`, `borderWidth: 1.5`
  - **P75 (Favorable)**: `borderColor: 'rgba(16, 185, 129, 0.4)'`, `borderWidth: 1.5`
  - **P50 (Mediana / Escenario Central)**: `borderColor: '#38bdf8'`, `borderWidth: 2.5`
  - **P25 (Desfavorable)**: `borderColor: 'rgba(244, 63, 94, 0.4)'`, `borderWidth: 1.5`
  - **P5 (Peor Caso / Riesgo Extremo)**: `borderColor: '#f43f5e'`, `borderDash: [4, 4]`, `borderWidth: 1.5`
- **Tooltips & Leyendas**: Tooltips oscuros con fondo `#141d2e`, borde `rgba(255, 255, 255, 0.1)` y texto `#f0f6fc`.

### 5.4 Canvas Nativo: Heatmap de Correlación de Retornos
- **Instancia**: `#smart-correlation-canvas`.
- **Renderizado 2D Optimizado**:
  - Escalado por `window.devicePixelRatio` para nitidez Retina.
  - Celdas con interpolación de color HSL / RGB:
    - Correlación positiva (`0` a `1.0`): interpolación desde `#141d2e` hacia `#f43f5e` (o `#38bdf8`).
    - Correlación negativa (`-1.0` a `0`): interpolación hacia `#10b981`.
  - Tipografía de celdas: `JetBrains Mono`, `bold`, centrado perfecto, color `#f0f6fc` para valores $> 0.40$ y `#94a3b8` para valores bajos.

---

## 6. MICRO-INTERACCIONES, MOVIMIENTO Y ESTADOS DINÁMICOS

### 6.1 Tokens de Movimiento y Física Visual
```css
:root {
    --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    --duration-micro: 120ms;   /* Hover, Focus, Clics */
    --duration-state: 180ms;   /* Transición de pestañas, expansión de paneles */
    --duration-reveal: 240ms;  /* Aparición de modales, alertas */
}
```

### 6.2 Especificación de Estados Interactivos
1. **Hover en Tarjetas y Pills**:
   - `transform: translateY(-1px)`
   - `border-color: rgba(56, 189, 248, 0.25)`
   - `box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08)`
2. **Focus en Campos de Formulario (`input:focus`, `select:focus`)**:
   - `border-color: #38bdf8`
   - `box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2)`
   - `background: #1c273d`
3. **Barra de Progreso Genético (`#smart-progress-bar-fill`, `#genetic-progress-fill`)**:
   - Fondo: `linear-gradient(90deg, #a855f7 0%, #38bdf8 50%, #10b981 100%)`
   - Animación: Shimmer de gradiente continuo (`1.5s linear infinite`) durante la ejecución de optimizaciones.
4. **Punto Pulsante de Conexión En Vivo (`.pulse-dot`)**:
   - Animación de respiración suave: `@keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.85); } }` (Ciclo de 2.0s).

---

## 7. MATRIZ DE PRESERVACIÓN Y REQUISITOS NO-FUNCIONALES

### 7.1 Matriz Completa de Identificadores DOM Críticos (100% Inviolable)
Para asegurar compatibilidad absoluta con la lógica en `static/js/app.js` y `static/js/charts.js`, todos los siguientes IDs y clases deben existir con su funcionalidad preservada:

| Módulo / Sección | Identificador HTML (ID / Class) | Tipo de Elemento | Evento / Rol JS |
| :--- | :--- | :--- | :--- |
| **Header & Modo** | `#mode-smart` | `<button>` | Alterna a `smart-dashboard` y actualiza clase `active` |
| **Header & Modo** | `#mode-advanced` | `<button>` | Alterna a navegación de pestañas avanzadas |
| **Header & Modo** | `.tabs-nav` | `<nav>` | Contenedor de botones de tabs de Modo Avanzado |
| **Smart Mode** | `#btn-smart-run` | `<button>` | Dispara `/api/smart-optimize-v2-stream` / `/api/smart-optimize` |
| **Smart Mode** | `input[name="smart-universe"]`| `<input type="checkbox">` | Universo de activos seleccionados (mínimo 3) |
| **Smart Mode** | `.asset-wr-badge` | `<span>` | Inserta dinámicamente badge de Win Rate por activo |
| **Smart Mode** | `#smart-preset-select` | `<select>` | Evento `change`: actualiza inputs numéricos según preset |
| **Smart Mode** | `#smart-streak-length` | `<input type="number">` | Longitud de racha consecutiva N |
| **Smart Mode** | `#smart-base-capital` | `<input type="number">` | Capital base a proteger ($) |
| **Smart Mode** | `#smart-profit-pct` | `<input type="number">` | Rendimiento mensual de arbitraje P2P (%) |
| **Smart Mode** | `#smart-risk-capital` | `<input type="number">` | Capital de riesgo mensual calculado (readonly) |
| **Smart Mode** | `#smart-attempts` | `<input type="number">` | Cantidad de intentos / balas |
| **Smart Mode** | `#smart-payout` | `<input type="number">` | Payout neto del broker |
| **Smart Mode** | `#smart-generations` | `<input type="number">` | Generaciones del optimizador genético en Rust |
| **Smart Mode** | `#smart-population` | `<input type="number">` | Tamaño de población genética |
| **Smart Mode** | `#smart-console-box` | `<div>` | Contenedor de consola de telemetría |
| **Smart Mode** | `#smart-progress-bar-fill` | `<div>` | Barra de progreso SSE |
| **Smart Mode** | `#smart-console-logs` | `<div>` | Contenedor de streaming de logs |
| **Smart Mode** | `#smart-top-5-box` | `<div>` | Contenedor del ranking de mejores estrategias |
| **Smart Mode** | `#smart-top-5-list` | `<div>` | Lista de chips interactivos de estrategias |
| **Smart Mode** | `#smart-rec-content` | `<div>` | Contenido del plan de rachas recomendado |
| **Smart Mode** | `#smart-ladder-content` | `<div>` | Contenedor de escalera Paroli paso a paso |
| **Smart Mode** | `#smart-correlation-canvas` | `<canvas>` | Canvas de heatmap de correlación |
| **Smart Mode** | `#smart-selected-assets-table` | `<table>` | Tabla de activos con baja correlación |
| **Smart Mode** | `#smart-selected-assets-body` | `<tbody>` | Cuerpo dinámico de tabla de activos |
| **Smart Mode** | `#smart-equity-chart-canvas` | `<canvas>` | Gráfica Chart.js de Curva de Capital Barbell |
| **Smart Mode** | `#smart-mc-chart-canvas` | `<canvas>` | Gráfica Chart.js de Conos Monte Carlo P5-P95 |
| **Smart Mode** | `#smart-asset-selector` | `<select>` | Selector dinámico de activo para velas |
| **Smart Mode** | `#smart-tv-chart` | `<div>` | Contenedor de gráfico TradingView Lightweight |
| **Smart Mode** | `#smart-tv-chart-empty` | `<div>` | Overlay de estado vacío sin datos |
| **Smart Mode** | `#smart-markov-table` | `<table>` | Tabla de probabilidades de transición de Markov |
| **Smart Mode** | `#smart-markov-explanation`| `<div>` | Explicación dinámica de probabilidades condicionales |
| **Advanced Mercado**| `#pair-selector` | `<select>` | Selector de par de divisas/cripto |
| **Advanced Mercado**| `#interval-selector` | `<select>` | Selector de temporalidad (1d, 4h, 1h, 30m, 15m, 5m, 1m) |
| **Advanced Mercado**| `#source-selector` | `<select>` | Selector de fuente: `historical` o `live` |
| **Advanced Mercado**| `#live-badge` | `<span>` | Badge de estado de conexión en vivo |
| **Advanced Mercado**| `#live-badge-text` | `<span>` | Texto de precio o estado en vivo |
| **Advanced Mercado**| `#tv-chart` | `<div>` | Contenedor del gráfico principal TradingView |
| **Advanced Mercado**| `#chart-loader` | `<div>` | Spinner de carga de velas |
| **Advanced Backtest**| `#backtest-form` | `<form>` | Formulario de ejecución de backtest manual |
| **Advanced Backtest**| `#run-backtest-btn` | `<button>` | Botón submit de backtest |
| **Advanced Backtest**| `#save-backtest-btn` | `<button>` | Guardar en favoritos |
| **Advanced Backtest**| `#strategy-selector` | `<select>` | Selector de estrategia |
| **Advanced Backtest**| `#dynamic-params` | `<div>` | Contenedor horizontal de inputs de parámetros |
| **Advanced Backtest**| `#expiry-candles` | `<input>` | Velas de expiración de la opción |
| **Advanced Backtest**| `#payout` | `<input>` | Payout del broker en modo avanzado |
| **Advanced Backtest**| `#backtest-n-consecutive`| `<input>` | Racha N consecutiva |
| **Advanced Backtest**| `#backtest-cycle-prob` | `<small>` | Probabilidad calculada de ciclo |
| **Advanced Backtest**| `#backtest-bet-fraction`| `<input>` | Fracción de capital inicial de ciclo |
| **Advanced Backtest**| `#optimize-genetic-btn`| `<button>` | Dispara `/api/genetic/run-stream` |
| **Advanced Backtest**| `#gen-generations` | `<input>` | Generaciones genéticas |
| **Advanced Backtest**| `#gen-population` | `<input>` | Población genética |
| **Advanced Backtest**| `#gen-min-trades` | `<input>` | Mínimo de trades/día |
| **Advanced Backtest**| `#genetic-progress-fill`| `<div>` | Barra de progreso genético |
| **Advanced Backtest**| `#genetic-progress-text`| `<span>` | % de progreso genético |
| **Advanced Backtest**| `#genetic-progress-eta` | `<span>` | Tiempo estimado restante (ETA) |
| **Advanced Backtest**| `#genetic-feedback` | `<div>` | Panel de resumen genético |
| **Advanced Backtest**| `#backtest-progress-fill`| `<div>` | Barra de progreso backtest |
| **Advanced Backtest**| `#stat-winrate` | `<p>` | Métrica de Win Rate |
| **Advanced Backtest**| `#stat-trades` | `<p>` | Métrica de Total Trades |
| **Advanced Backtest**| `#stat-pnl` | `<p>` | Métrica de P&L Neto |
| **Advanced Backtest**| `#stat-mw` | `<p>` | Métrica de Max Win Streak |
| **Advanced Backtest**| `#stat-ml` | `<p>` | Métrica de Max Loss Streak |
| **Advanced Backtest**| `#equity-chart` | `<canvas>` | Canvas de curva de capital |
| **Advanced Backtest**| `#trades-table` | `<table>` | Tabla de historial de operaciones |
| **Advanced Historial**| `#btn-clear-history` | `<button>` | Limpieza de historial local |
| **Advanced Historial**| `#history-list` | `<div>` | Lista de optimizaciones históricas |
| **Advanced Historial**| `#saved-list` | `<div>` | Lista de backtests favoritos |
| **Advanced Estadísticas**| `#autocorr-chart` | `<canvas>` | Gráfica de autocorrelación (lags 1-10) |
| **Advanced Estadísticas**| `#streaks-chart` | `<canvas>` | Gráfica de distribución de rachas |
| **Advanced Estadísticas**| `#hourly-chart` | `<canvas>` | Gráfica de Win Rate por hora |
| **Advanced Estadísticas**| `#cond-probs` | `<div>` | Grid 2x2 de probabilidades condicionales |
| **Advanced Estadísticas**| `#market-state-chart` | `<canvas>` | Gráfica de Win Rate por régimen de mercado |
| **Advanced Estadísticas**| `#markov-table` | `<table>` | Matriz de transición de Markov completa |
| **Advanced Optimizador**| `#opt-winrate` | `<input>` | Win Rate manual (%) |
| **Advanced Optimizador**| `#opt-payout` | `<input>` | Payout manual |
| **Advanced Optimizador**| `#opt-base-capital` | `<input>` | Capital base |
| **Advanced Optimizador**| `#opt-profit-pct` | `<input>` | % Rendimiento mensual |
| **Advanced Optimizador**| `#opt-risk-capital` | `<input>` | Capital de riesgo |
| **Advanced Optimizador**| `#opt-target-capital`| `<input>` | Meta de duplicación ($) |
| **Advanced Optimizador**| `#opt-attempts` | `<input>` | Intentos / ciclos |
| **Advanced Optimizador**| `#btn-calc-streak` | `<button>` | Dispara cálculo de plan de rachas |
| **Advanced Optimizador**| `#streak-progress-fill`| `<div>` | Barra de progreso racha |
| **Advanced Optimizador**| `#streak-recommendation-content`| `<div>` | Recomendación calculada |
| **Advanced Optimizador**| `#bet-ladder-container`| `<div>` | Escalera de apuestas detallada |
| **Advanced Optimizador**| `#streak-alternatives-table`| `<table>` | Tabla comparativa por Racha N |
| **Advanced Optimizador**| `#mc-chart` | `<canvas>` | Canvas de Monte Carlo 5,000 caminos |
| **Modales Dinámicos** | `pinescript-box-${id}`| `<div>` | Caja de exportación Pine Script v5 |
| **Modales Dinámicos** | `pinescript-code-${id}`| `<textarea>` | Código fuente Pine Script |
| **Modales Dinámicos** | `ai-prompt-${id}` | `<textarea>` | Prompt estructurado para IA |

### 7.2 Funciones Globales en `window` Preservadas
- `window.togglePineScriptModal(id)`
- `window.copyPineScript(id)`
- `window.copyAIPrompt(id)`

### 7.3 Contratos de API Backend Soportados
| Endpoint | Método | Tipo de Comunicación | Payload / Parámetros |
| :--- | :--- | :--- | :--- |
| `/api/data/pairs` | GET | JSON REST | `{}` ➔ lista de pares disponibles |
| `/api/data/candles` | GET | JSON REST | `?pair=BTCUSDT&interval=1d&source=historical` ➔ array de velas |
| `/api/strategies` | GET | JSON REST | `{}` ➔ catálogo de estrategias y parámetros |
| `/api/backtest` | POST | JSON REST | Configuración de estrategia y capital ➔ métricas y trades |
| `/api/backtest-stream` | GET (SSE) | Server-Sent Events | Query params de backtest ➔ streaming de progreso y resultado |
| `/api/smart-optimize-v2` | POST | JSON REST | `{ base_capital, profit_pct, universe, streak_length, ... }` ➔ resultados optimizados |
| `/api/smart-optimize-v2-stream` | GET (SSE) | Server-Sent Events | Parámetros Smart Mode ➔ streaming de logs, progreso y resultados |
| `/api/genetic/run-stream` | GET (SSE) | Server-Sent Events | Parámetros genéticos ➔ streaming evolutivo y mejor genoma |
| `/api/optimize-streak` | POST | JSON REST | Parámetros de racha ➔ escalera y tabla comparativa N |
| `/api/montecarlo` | POST | JSON REST | Parámetros de simulación ➔ caminos y percentiles P5-P95 |

---

## 8. TABLA DE CARACTERÍSTICAS DESCUBIERTAS (FEATURES DISCOVERED)

| # | Categoría | Feature | Descripción | Inputs | Outputs | Manejo de Errores | Vía de Descubrimiento |
|---|---|---|---|---|---|---|---|
| 1 | Visual Theme | Arquitectura de Capas de Superficie | Paleta calibrada de 3 niveles (`#080b11`, `#0e1420`, `#141d2e`) con bordes translúcidos de 1px | Clases CSS (`.glass-card`, `.app-header`) | Fondos oscuros libres de glare con profundidad visual | Fallback a `#0e1420` sólido si backdrop-filter no está soportado | GUIA_MAESTRA §4.1, style.css |
| 2 | Visual Theme | Acentos Semánticos Anti-Cromoestereopsis | 5 colores funcionales (`#38bdf8`, `#10b981`, `#f43f5e`, `#a855f7`, `#f59e0b`) desaturados a 65-80% | Variables CSS semánticas | Señales y estados claros sin vibración retiniana | Contraste asegurado contra `#080b11` $> 4.5:1$ | GUIA_MAESTRA §3.1, §4.3 |
| 3 | Typography | Cifras Tabulares Monospace | Números alineados verticalmente en tablas con `JetBrains Mono` y `tabular-nums` | Clases `.tabular-nums`, estilos de tabla | Alineación de dígitos idéntica sin desplazamiento horizontal | Fallback a `monospace` estándar | GUIA_MAESTRA §5.1, index.html |
| 4 | Navigation | Selector de Modo Híbrido | Alternancia entre Modo Inteligente (1-clic) y Modo Avanzado (multitab) | Clic en `#mode-smart` o `#mode-advanced` | Visualización fluida del panel correspondiente | Transición fade-in sin parpadeos | ORIGINAL_REQUEST R2, index.html |
| 5 | Control Bar | Presets Barbell Pre-calculados | Configuración instantánea de 6 Balas ($33.33), 8 Balas ($25) o 1 Bala ($200) | Dropdown `#smart-preset-select` | Actualiza `#smart-streak-length`, `#smart-attempts`, etc. | Validación de límites numéricos min/max | GUIA_MAESTRA §2.4, index.html |
| 6 | Telemetry | Consola Cyberpunk con Streaming SSE | Visualización en tiempo real de generaciones genéticas en Rust y cálculo de correlaciones | Conexión SSE `/api/smart-optimize-v2-stream` | Logs coloreados en vivo y barra de progreso animada | Cierre seguro de EventSource ante errores | app.js, index.html |
| 7 | Strategy Rank | Top Strategies Pills Interactivas | Ranking de las 5 mejores estrategias con chips seleccionables | Clic en chips de `#smart-top-5-list` | Actualización atómica de todas las gráficas, tablas y planes | Muestra estado vacío si la lista está vacía | app.js, index.html |
| 8 | Risk Management | Escalera Paroli Paso a Paso | Visualización estructurada de progresión de capital por victoria consecutiva | Datos calculados en optimización | Pasos numerados con monto a apostar y ganancia acumulada | Mensaje "Sin plan activo" si no hay datos | GUIA_MAESTRA §1.3, index.html |
| 9 | Risk Analytics | Heatmap de Correlación Multiactivo | Matriz de correlación cruzada de retornos con filtro $< 0.40$ en Canvas 2D | Matriz de correlación y array de tickers | Grilla interactiva con celdas coloreadas y valores numéricos | Muestra mensaje "Sin datos de correlación" | charts.js, app.js |
| 10 | Charting | Velas Lightweight Charts con CALL/PUT | Gráfico de velas financieras de alto rendimiento con marcadores de señales de compra/venta | Array de velas OHLCV y señales | Gráfico interactivo con zoom, paneo y crosshair pro | Loader animado y overlay de "Sin datos" | charts.js, app.js |
| 11 | Charting | Curva de Capital con Auto-Escala Logarítmica | Gráfico Chart.js con área rellena y conmutación automática a escala log si ratio $> 100$ | Puntos de capital y fechas | Curva nítida con tooltips detallados de operación | Limita valor mínimo a 1.0 en log scale | charts.js, app.js |
| 12 | Probabilities | Conos Monte Carlo (1,000 Caminos) | Gráfico Chart.js con percentiles P5, P25, P50, P75, P95 | Arrays de percentiles | Curvas diferenciadas por color y estilo de línea | Filtrado de valores $\le 0.01$ para evitar $\log(0)$ | charts.js, app.js |
| 13 | Probabilities | Matriz de Transición de Markov | Tabla con probabilidades condicionales $P(W \mid W)$, $P(L \mid W)$, $P(W \mid L)$, $P(L \mid L)$ | Matriz de probabilidad calculada | Tabla tabular con coloreado semántico de celdas | Placeholder "Sin datos" si faltan trades | charts.js, app.js |
| 14 | Code Export | Generador Pine Script v5 y Prompt IA | Modal con código TradingView v5 listo para copiar y prompt para LLMs | Botón "Exportar PineScript / Prompt" | Bloques de código con botón de copiado de 1-clic | Alerta de confirmación y copiado a clipboard | app.js, index.html |
| 15 | Live Feed | Streaming en Vivo de Velas Binance | WebSocket directo a Binance (`@kline`) con fallback a polling HTTP | Selector de fuente `live` | Actualización de la última vela en tiempo real sin recargar | Fallback automático a HTTP si WS falla | app.js, charts.js |

---

## 9. TABLA DE CASOS LÍMITE (EDGE CASES)

| # | Feature | Input / Condición Límite | Comportamiento Observado / Especificado |
|---|---|---|---|
| 1 | Curva de Capital (Chart.js) | Crecimiento exponencial extremo ($1,000 \rightarrow \$2,000,000$) | Conmutación automática a eje Y logarítmico; ticks filtrados con `formatYAxisTick` para evitar colisión vertical de etiquetas. |
| 2 | Curva de Capital (Chart.js) | Capital cae a \$0 o negativo | Escala lineal forzada si valores son $\le 0$; tooltips muestran `-$X.XX` sin romper el gráfico. |
| 3 | Conos Monte Carlo | Caminos con quiebra total (valores 0.0) | Función `clean()` normaliza valores a `0.01` mínimo para evitar error de asíntota $-\infty$ en escala logarítmica. |
| 4 | Heatmap de Correlación | Contenedor colapsado o redimensionado (Resize) | Canvas escala dinámicamente usando `clientWidth` de contenedor y `devicePixelRatio` para evitar pixelado en pantallas Retina. |
| 5 | Heatmap de Correlación | Activos con matriz incompleta o valores `NaN` | Celda renderizada con color neutro de fondo (`#141d2e`) y texto de fallback sin interrumpir el pintado del resto de la grilla. |
| 6 | Velas Lightweight Charts | Lista vacía de velas (`[]`) | Se oculta el lienzo de TradingView y se muestra el overlay `#smart-tv-chart-empty` con mensaje central "Sin datos". |
| 7 | Velas en Vivo (WebSocket) | Desconexión repentina de red o caída de Binance WS | Evento `onerror` y `onclose` activan temporizador `startFallbackPolling` a intervalos de 2s actualizando `#live-badge`. |
| 8 | Streaming SSE (Consola) | Error o interrupción en el servidor Python | EventSource gestiona el evento `onerror`, desbloquea el botón `#btn-smart-run` y restaura el estado interactivo de la interfaz. |
| 9 | Universo de Activos | Menos de 3 activos seleccionados | Validación en JavaScript alerta al usuario y previene el envío de la petición de optimización multiactivo. |
| 10 | Tablas Numéricas | Pantallas compactas / móviles | Contenedores de tabla con `overflow-x: auto` y barras de scroll discretas en color `#1c273d` para evitar desbordamiento horizontal. |

---

## 10. GUÍA DE IMPLEMENTACIÓN PARA EL AGENTE CONSTRUCTOR

1. **Variables CSS Globales**: Implementar la jerarquía de tokens en `static/css/style.css` respetando exactamente los códigos HEX y unidades especificadas en este reporte.
2. **Estructura HTML**: Mantener los 846 identificadores y atributos funcionales en `templates/index.html`, organizando visualmente los contenedores bajo el 8-point grid y clases `.glass-card`.
3. **Módulo Gráficos (`charts.js`)**: Actualizar la inicialización de Lightweight Charts y Chart.js para adoptar fondos transparentes, paleta semántica desaturada y tipografía `JetBrains Mono`.
4. **Verificación de Cero Errores**: Probar en navegador la carga limpia sin advertencias ni errores en la consola de JavaScript.
