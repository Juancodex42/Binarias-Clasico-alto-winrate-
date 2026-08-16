# Plan de Implementación M1: Refactorización Integral del Sistema de Diseño Visual y Hoja de Estilo Global (`style.css`)

**Proyecto:** Binary Options Quantitative Terminal UI/UX Redesign  
**Hito:** Milestone 1 (M1) — Visual Design System & Global Stylesheet Refactor  
**Archivo Destino a Modificar en M1:** `c:\Users\juanc\Desktop\prueba\static\css\style.css`  
**Autor:** Agente Explorer M1  
**Fecha:** 2026-08-16  
**Estado:** Plan de Implementación Listo para Ejecución  

---

## 1. RESUMEN EJECUTIVO Y OBJETIVOS DE M1

El objetivo de este hito es reescribir de forma limpia, estructurada y modular el archivo de estilos global `static/css/style.css`, transformando la interfaz en un **Terminal Institucional de Finanzas Cuantitativas** (*Institutional-Grade Dark FinTech Terminal*) que cumpla al 100% con las directrices neuro-ópticas, de contraste y ergonomía de `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`.

### Principios Fundamentales del Refactor CSS
1. **Ergonomía Visual & Cero Halación**: Supresión total de `#FFFFFF` puro sobre negro profundo; uso de Obsidian `#080b11` en canvas y Slate `#0e1420` en tarjetas con bordes perimetrales de 1px translúcidos (`rgba(255, 255, 255, 0.07)`).
2. **Paleta Semántica Calibrada (Anti-Cromoestereopsis)**: Saturación balanceada (65%-80%) para evitar fatiga retiniana y efecto 3D indeseado (`#38bdf8`, `#10b981`, `#f43f5e`, `#a855f7`, `#f59e0b`).
3. **Alineación Numérica Tabular Inviolable**: Tipografía `JetBrains Mono` con `tabular-nums` y `font-feature-settings: "tnum" 1, "zero" 1` en todas las tablas, matrices de Markov, métricas y datos cuantitativos.
4. **Preservación Total de Selectores (Zero Regressions)**: Mantenimiento y retrocompatibilidad de todos los selectores existentes usados por `index.html` y manipulados dinámicamente por `app.js` (incluyendo clases dinámicas como `.text-green`, `.text-red`, `.top-strat-pill`, `.ladder-step`, `.console-log-line`, `.asset-wr-badge`, etc.).

---

## 2. ESPECIFICACIÓN DETALLADA DE TOKENS EN `:root`

El nuevo bloque `:root` contendrá la arquitectura completa de diseño en variables CSS:

```css
:root {
    /* ==========================================================================
       1. SUPERFICIES Y FONDOS (FinTech Slate & Obsidian Architecture)
       ========================================================================== */
    --bg-canvas: #080b11;            /* Fondo principal del viewport (Obsidian) */
    --bg-card: #0e1420;              /* Tarjetas base y paneles contenedores (Slate) */
    --bg-elevated: #141d2e;          /* Header, toolbars, modales flotantes */
    --bg-hover: #1c273d;             /* Inputs, selects, hovers y estados activos */
    --bg-overlay: rgba(8, 11, 17, 0.85); /* Backdrops de modales y overlays */
    
    /* Alias de retrocompatibilidad */
    --bg-dark: var(--bg-canvas);
    --bg-panel: var(--bg-card);

    /* ==========================================================================
       2. BORDES Y DELIMITADORES PERIMETRALES
       ========================================================================== */
    --border-subtle: rgba(255, 255, 255, 0.07);  /* Borde estándar de 1px */
    --border-focus: rgba(56, 189, 248, 0.35);    /* Borde en foco o selección activa */
    --border-active: rgba(56, 189, 248, 0.50);   /* Borde activo destacado */
    --focus-ring: rgba(56, 189, 248, 0.20);      /* Halo de enfoque exterior (glow) */
    
    /* Alias de retrocompatibilidad */
    --border-color: var(--border-subtle);
    --border-glow: var(--border-focus);

    /* ==========================================================================
       3. JERARQUÍA TIPOGRÁFICA Y CONTRASTE (WCAG AAA & APCA)
       ========================================================================== */
    --text-primary: #f0f6fc;         /* Títulos, números principales, valores clave */
    --text-secondary: #94a3b8;       /* Labels, headers de tablas, subtítulos */
    --text-muted: #64748b;           /* Timestamps, unidades, placeholders */
    --text-disabled: #475569;        /* Elementos inactivos o deshabilitados */

    /* ==========================================================================
       4. ACENTOS SEMÁNTICOS CALIBRADOS (Anti-Halación & Anti-Cromoestereopsis)
       ========================================================================== */
    --accent-primary: #38bdf8;       /* Electric Sky: Foco, acción primaria, tabs */
    --accent-green: #10b981;         /* Cyber Emerald: CALL, Ganancias, Win Rate alto */
    --accent-red: #f43f5e;           /* Rose Crimson: PUT, Pérdidas, Riesgo */
    --accent-purple: #a855f7;        /* Quantum Amethyst: Optimización genética Rust */
    --accent-amber: #f59e0b;         /* Golden Amber: Balas, Paroli, advertencias */
    --accent-slate: #64748b;         /* Cool Slate: Gridlines, neutros */

    /* Alias de retrocompatibilidad */
    --accent-blue: var(--accent-primary);
    --accent-gold: var(--accent-amber);

    /* ==========================================================================
       5. SISTEMA DE ESPACIADO 8-POINT GRID
       ========================================================================== */
    --space-1: 4px;                  /* Micro-espaciado: badges, iconos */
    --space-2: 8px;                  /* Separación interna de controles y chips */
    --space-3: 12px;                 /* Padding vertical en inputs y botones */
    --space-4: 16px;                 /* Padding estándar de tarjetas glass-card */
    --space-5: 20px;                 /* Separación entre columnas principales */
    --space-6: 24px;                 /* Separación de secciones mayores */
    --space-8: 32px;                 /* Márgenes perimetrales de pantalla */

    /* ==========================================================================
       6. GEOMETRÍA Y RADIOS DE CURVATURA
       ========================================================================== */
    --radius-sm: 4px;                /* Sub-tabs, tags compactos */
    --radius-md: 6px;                /* Inputs, selects, botones de acción */
    --radius-lg: 8px;                /* Sub-paneles y contenedores secundarios */
    --radius-xl: 10px;               /* Tarjetas principales (.glass-card) */
    --radius-pill: 9999px;           /* Badges, mode switcher, pills */

    /* ==========================================================================
       7. TIPOGRAFÍAS DEL SISTEMA
       ========================================================================== */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', 'Geist Mono', 'SF Mono', Consolas, monospace;
    --font-family: var(--font-sans); /* Retrocompatibilidad */

    /* ==========================================================================
       8. TOKENS DE MOVIMIENTO Y TRANSICIONES FÍSICAS
       ========================================================================== */
    --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    --duration-micro: 120ms;         /* Hover, focus, click */
    --duration-state: 180ms;         /* Pestañas, expansión de paneles */
    --duration-reveal: 240ms;        /* Modales, tooltips */
}
```

---

## 3. RESET GLOBAL, CUERPO Y CONFIGURACIÓN TIPOGRÁFICA

```css
/* Box Sizing & Reset */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* Body & Viewport */
body {
    background-color: var(--bg-canvas);
    background-image: 
        radial-gradient(at 15% 15%, rgba(56, 189, 248, 0.03) 0px, transparent 50%),
        radial-gradient(at 85% 85%, rgba(168, 85, 247, 0.03) 0px, transparent 50%);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 14px;
    line-height: 1.5;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: hidden;
}

/* Regla Inviolable de Cifras Tabulares (Data-to-Ink Precision) */
.tabular-nums, 
.markov-table td, 
.markov-table th, 
.trades-table td, 
.n-table td, 
.stat-card p, 
.console-body,
.ladder-step-amount,
.smart-rec-item p,
.recommendation-stat p,
.backtest-item-metrics span strong,
.asset-wr-badge {
    font-family: var(--font-mono);
    font-feature-settings: "tnum" 1, "zero" 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}
```

---

## 4. ESPECIFICACIÓN DE COMPONENTES UI Y BLOQUES VISUALES

### 4.1 Layout General y Header Institucional
- `.app-container`: Contenedor vertical flexible (`display: flex; flex-direction: column; min-height: 100vh;`).
- `.app-header`: Header sticky institucional (`height: 64px; background: var(--bg-elevated); border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center; padding: 0 var(--space-6); backdrop-filter: blur(12px); z-index: 50; position: sticky; top: 0;`).
- `.logo h1`: Logotipo del terminal (`font-size: 1.2rem; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: var(--space-2);`).
- `.logo h1 span`: Gradiente esmeralda/cielo (`background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-primary) 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;`).
- `.content-area`: Área principal desplazable (`flex: 1; padding: var(--space-5); position: relative;`).
- `.tab-pane`: Paneles con animación de revelado suave (`display: none; animation: fadeIn var(--duration-state) var(--ease-out-expo);`).
- `.tab-pane.active`: `display: block;`.

### 4.2 Selector de Modo Híbrido y Navegación
- `.mode-switch-container`: Píldora de encapsulación (`display: inline-flex; background: var(--bg-canvas); border: 1px solid var(--border-subtle); border-radius: var(--radius-pill); padding: 3px; gap: 4px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);`).
- `.mode-btn`: Botón de modo (`background: transparent; border: none; color: var(--text-secondary); padding: 6px 16px; font-size: 0.82rem; font-weight: 600; border-radius: var(--radius-pill); cursor: pointer; transition: all var(--duration-micro) var(--ease-out-expo);`).
- `.mode-btn.active`: Fondo activo en gradiente cuántico (`background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-primary) 100%); color: #ffffff; box-shadow: 0 2px 10px rgba(168, 85, 247, 0.35);`).
- `.tabs-nav`: Navegador de pestañas de Modo Avanzado (`display: flex; gap: var(--space-2);`).
- `.tab-btn`: Botón de pestaña (`background: transparent; border: 1px solid transparent; color: var(--text-secondary); padding: 6px 14px; font-size: 0.85rem; font-weight: 500; border-radius: var(--radius-md); cursor: pointer; transition: all var(--duration-micro) var(--ease-out-expo);`).
- `.tab-btn.active`: `color: var(--accent-primary); background: rgba(56, 189, 248, 0.1); border-color: var(--border-focus); box-shadow: 0 0 12px rgba(56, 189, 248, 0.12); font-weight: 600;`.

### 4.3 Tarjetas Glassmórficas (`.glass-card`)
- `.glass-card`: Superficie Slate (`background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); padding: var(--space-4); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.04); backdrop-filter: blur(12px); transition: border-color var(--duration-micro) ease, box-shadow var(--duration-micro) ease, transform var(--duration-micro) var(--ease-out-expo);`).
- `.glass-card:hover`: Micro-elevación (`border-color: rgba(56, 189, 248, 0.2);`).

### 4.4 Formularios, Inputs y Selectores
- `label`, `.smart-input-label`: Etiquetas de control (`display: block; margin-bottom: var(--space-1); font-size: 0.78rem; color: var(--text-secondary); font-weight: 500;`).
- `input`, `select`, `textarea`, `.form-control`: Campos de entrada táctiles (`width: 100%; background: var(--bg-hover); border: 1px solid var(--border-subtle); color: var(--text-primary); padding: 8px 12px; border-radius: var(--radius-md); font-family: var(--font-sans); font-size: 0.85rem; outline: none; transition: border-color var(--duration-micro) ease, box-shadow var(--duration-micro) ease, background var(--duration-micro) ease;`).
- `input:focus`, `select:focus`, `textarea:focus`, `.form-control:focus`: Foco luminoso (`border-color: var(--accent-primary); box-shadow: 0 0 0 3px var(--focus-ring); background: var(--bg-hover);`).
- `.input-readonly`, `input[readonly]`: Entradas bloqueadas (`background: rgba(255, 255, 255, 0.03) !important; color: var(--accent-primary) !important; font-weight: 600; cursor: default;`).

### 4.5 Botones de Acción (`.btn-primary`, `.btn-secondary`)
- `.btn-primary`: Botón primario de foco institucional (`background: linear-gradient(135deg, var(--accent-primary) 0%, #0284c7 100%); color: #080b11; font-weight: 600; padding: 10px 18px; border-radius: var(--radius-md); border: none; cursor: pointer; box-shadow: 0 2px 10px rgba(56, 189, 248, 0.25); transition: all var(--duration-micro) var(--ease-out-expo);`).
- `.btn-primary:hover`: `background: linear-gradient(135deg, #7dd3fc 0%, var(--accent-primary) 100%); box-shadow: 0 4px 16px rgba(56, 189, 248, 0.4); transform: translateY(-1px);`.
- `.btn-secondary`: Botón de acción secundaria (`background: rgba(255, 255, 255, 0.04); color: var(--text-primary); border: 1px solid var(--border-subtle); padding: 10px 18px; border-radius: var(--radius-md); font-weight: 500; cursor: pointer; transition: all var(--duration-micro) var(--ease-out-expo);`).
- `.btn-secondary:hover`: `background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.15); transform: translateY(-1px);`.
- `#btn-smart-run`: Botón de auto-optimización (`background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-primary) 100%); color: #080b11; font-weight: 700; padding: 12px 24px; border-radius: var(--radius-lg); border: none; cursor: pointer; font-size: 0.88rem; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3); transition: all var(--duration-micro) var(--ease-out-expo);`).

### 4.6 Consola de Telemetría y Shimmer Progress Bar
- `.smart-console-wrapper`: Contenedor terminal (`background: #06090e; border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); overflow: hidden; margin-top: var(--space-3);`).
- `.console-header`: Barra de título de consola con micro-botones (`background: var(--bg-card); padding: 6px 12px; display: flex; align-items: center; border-bottom: 1px solid var(--border-subtle);`).
- `.console-dot.red`: `background: var(--accent-red);` | `.yellow`: `background: var(--accent-amber);` | `.green`: `background: var(--accent-green);`.
- `.smart-progress-bar-container`: Contenedor de barra de progreso (`background: rgba(255, 255, 255, 0.03); height: 4px; border-bottom: 1px solid var(--border-subtle); position: relative; width: 100%; overflow: hidden;`).
- `.smart-progress-bar-fill`: Animación shimmer de gradiente continuo (`background: linear-gradient(90deg, var(--accent-purple) 0%, var(--accent-primary) 50%, var(--accent-green) 100%); background-size: 200% 100%; width: 0%; height: 100%; transition: width 0.2s ease; animation: progressShimmer 2s linear infinite;`).
- `.console-body`: Contenedor de logs con scroll personalizado (`background: #06090e; font-family: var(--font-mono); font-size: 0.72rem; color: var(--accent-green); padding: 10px 12px; height: 150px; overflow-y: auto; line-height: 1.45;`).
- `.console-log-line.info`: `color: var(--accent-primary);` | `.success`: `color: var(--accent-green); font-weight: 600;` | `.error`: `color: var(--accent-red);` | `.warning`: `color: var(--accent-amber);`.

### 4.7 Ranking Top-5 y Chips de Estrategias
- `.top-strategies-wrapper`: Tarjeta contenedora de ranking (`padding: var(--space-3); border-color: rgba(168, 85, 247, 0.35); background: var(--bg-card);`).
- `.top-strat-pill`: Chips interactivos de estrategia (`background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-subtle); color: var(--text-secondary); border-radius: var(--radius-lg); padding: 8px 12px; cursor: pointer; text-align: left; transition: all var(--duration-micro) var(--ease-out-expo); width: 100%; font-family: var(--font-sans);`).
- `.top-strat-pill:hover`: `border-color: rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.08); transform: translateY(-1px);`.
- `.top-strat-pill.active`: `background: rgba(168, 85, 247, 0.15); border-color: var(--accent-purple); color: #ffffff; box-shadow: 0 0 12px rgba(168, 85, 247, 0.2);`.

### 4.8 Escalera de Apuestas Paroli (`.ladder-step`)
- `.streak-ladder`: Contenedor vertical (`display: flex; flex-direction: column; gap: 8px; padding: 4px 0;`).
- `.ladder-step`: Paso de la escalera (`display: flex; align-items: center; justify-content: space-between; background: var(--bg-hover); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 8px 12px; transition: all var(--duration-micro) ease;`).
- `.ladder-step:hover`: `border-color: var(--border-focus); transform: translateX(3px);`.
- `.ladder-step.completed`: Paso meta completado (`border-color: rgba(16, 185, 129, 0.35); background: rgba(16, 185, 129, 0.08);`).
- `.ladder-step-number`: Círculo de paso (`font-family: var(--font-mono); font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); width: 26px; height: 26px; border-radius: 50%; border: 1.5px solid var(--border-subtle); display: flex; align-items: center; justify-content: center; flex-shrink: 0;`).
- `.ladder-step.completed .ladder-step-number`: `border-color: var(--accent-green); color: var(--accent-green); background: rgba(16, 185, 129, 0.12);`.
- `.ladder-step-amount`: `font-family: var(--font-mono); font-size: 0.95rem; font-weight: 700; color: var(--accent-primary);`.

### 4.9 Tablas Cuantitativas (`.markov-table`, `.trades-table`, `.n-table`)
- `table`: `width: 100%; border-collapse: collapse;`.
- `th`: Encabezados pegajosos (`padding: 8px 10px; color: var(--text-secondary); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.03em; border-bottom: 1px solid var(--border-subtle); background: var(--bg-card); position: sticky; top: 0; z-index: 2;`).
- `td`: Celdas tabulares (`padding: 8px 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: var(--text-primary); font-size: 0.8rem;`).
- `tr:hover td`: `background: rgba(255, 255, 255, 0.02);`.

### 4.10 Tarjetas de Métricas Estadísticas (`.stat-card`)
- `.stats-cards`: Cuadrícula auto-ajustable (`display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: var(--space-4);`).
- `.stat-card`: Tarjeta compacta (`background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 12px 14px; text-align: center; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); transition: all var(--duration-micro) ease;`).
- `.stat-card:hover`: `border-color: rgba(56, 189, 248, 0.25); transform: translateY(-1px);`.
- `.stat-card h3`: `font-size: 0.72rem; color: var(--text-secondary); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; font-family: var(--font-sans);`.
- `.stat-card p`: `font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em;`.

### 4.11 Badges, Pulso En Vivo y Tooltips
- `.live-badge-span`: Badge de conexión (`display: inline-flex; align-items: center; gap: 4px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 8px; border-radius: var(--radius-pill); font-size: 0.72rem; color: var(--accent-green);`).
- `.pulse-dot`: Micro-punto pulsante (`display: inline-block; color: var(--accent-green); font-size: 0.65rem; animation: livePulse 2s infinite ease-in-out;`).
- `@keyframes livePulse`: `0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.35; transform: scale(0.85); }`.
- `.tooltip`: Disparador de ayuda (`position: relative; display: inline-flex; align-items: center; justify-content: center; width: 15px; height: 15px; border-radius: 50%; background-color: rgba(255, 255, 255, 0.08); color: var(--text-secondary); font-size: 10px; font-weight: 600; cursor: help; margin-left: 6px; vertical-align: middle; transition: all var(--duration-micro) ease;`).
- `.tooltip:hover`: `background-color: var(--accent-primary); color: #080b11;`.
- `.tooltip .tooltip-text`: Contenedor emergente contextual (`visibility: hidden; width: 260px; background-color: var(--bg-elevated); color: var(--text-primary); text-align: left; border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 10px 12px; position: absolute; z-index: 9999; bottom: 130%; left: -10px; opacity: 0; transition: opacity var(--duration-micro) ease; font-weight: normal; font-size: 0.75rem; line-height: 1.4; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6); pointer-events: none; white-space: normal;`).
- `.tooltip:hover .tooltip-text`: `visibility: visible; opacity: 1;`.

---

## 5. MATRIZ DE PRESERVACIÓN Y COMPROBACIÓN DE SELECTORES

Para garantizar **cero regresiones funcionales o visuales**, se verifica que el nuevo archivo `style.css` mantenga y estructure todos los selectores existentes:

| Selector en `style.css` | Uso en `index.html` / `app.js` | Estado en Plan M1 | Justificación |
| :--- | :--- | :--- | :--- |
| `:root` | Variables globales de la app | **Expandido y calibrado** | Nuevos tokens institucionales + aliases de retrocompatibilidad. |
| `.glass-card` | Contenedores y paneles | **Actualizado** | Fondo Slate `#0e1420`, bordes de 1px `rgba(255,255,255,0.07)`, blur 12px. |
| `.app-container` | Layout raíz de la app | **Preservado** | Flexbox vertical con `min-height: 100vh`. |
| `.app-header` | Encabezado superior | **Actualizado** | Altura 64px, fondo `#141d2e`, sticky. |
| `.logo h1`, `.logo h1 span` | Logotipo institucional | **Actualizado** | Gradiente esmeralda a cielo sin resplandores excesivos. |
| `.mode-switch-container` | Selector de Modo Híbrido | **Actualizado** | Píldora con fondo canvas y sombra interna. |
| `.mode-btn`, `.mode-btn.active` | Botones Inteligente / Avanzado | **Actualizado** | Transición suave y foco en gradiente cuántico. |
| `.tabs-nav`, `.tab-btn`, `.tab-btn.active` | Pestañas de navegación | **Actualizado** | Foco en `Electric Sky` con bordes nítidos. |
| `.content-area`, `.tab-pane`, `.tab-pane.active` | Contenedor de contenido | **Preservado** | Transición fade-in de 180ms. |
| `.control-group`, `label`, `input`, `select` | Formularios y campos | **Actualizado** | Altura compacta, fondo `#1c273d`, foco `#38bdf8`. |
| `.btn-primary`, `.btn-secondary` | Botones de acción | **Actualizado** | Elevación táctil, sombras sutiles. |
| `#btn-smart-run` | Botón auto-optimizar | **Actualizado** | Gradiente esmeralda/cielo con sombra verde translúcida. |
| `.smart-grid`, `.smart-sidebar` | Layout Modo Inteligente | **Actualizado** | 8-point grid, espaciado armónico. |
| `.smart-universe-wrapper`, `.smart-universe-select` | Selector de universo | **Actualizado** | Chips interactivos con checkboxes. |
| `.asset-wr-badge` | Badges de Win Rate dinámicos | **Preservado** | Cifras tabulares `JetBrains Mono`. |
| `.smart-numeric-inputs`, `.input-readonly` | Inputs de parámetros | **Actualizado** | Grid ordenado, cifras monospace. |
| `.smart-console-wrapper`, `.console-header` | Consola de telemetría | **Actualizado** | Fondo `#06090e`, micro-dots coloreados. |
| `.smart-progress-bar-fill` | Barra de progreso SSE | **Actualizado** | Animación shimmer con gradiente púrpura/cielo/esmeralda. |
| `.console-body`, `.console-log-line` | Logs dinámicos | **Actualizado** | Tipografía `JetBrains Mono` con clases `.info`, `.success`, `.error`, `.warning`. |
| `.top-strategies-wrapper`, `.top-strat-pill` | Ranking de estrategias | **Actualizado** | Chips interactivos con bordes púrpuras. |
| `.smart-rec-grid`, `.smart-rec-item` | Plan de rachas optimizado | **Actualizado** | Cifras tabulares, métricas de duplicación. |
| `.streak-ladder`, `.ladder-step` | Escalera Paroli | **Actualizado** | Pasos numerados, estado `.completed` en esmeralda. |
| `.recommendation-banner`, `.recommendation-stat` | Banner de recomendaciones | **Actualizado** | Cifras monoespaciadas en grid adaptativo. |
| `.markov-table`, `.trades-table`, `.n-table` | Tablas de datos | **Actualizado** | Cifras tabulares alineadas a la derecha, sticky headers. |
| `.stats-cards`, `.stat-card` | Métricas y estadísticas | **Actualizado** | Números grandes en `JetBrains Mono`. |
| `.cond-probs-grid` | Grid de probabilidades | **Actualizado** | Celdas 2x2 con cifras tabulares. |
| `.subtabs-nav`, `.subtab-btn` | Sub-pestañas de Backtest | **Preservado** | Navegación horizontal compacta. |
| `.backtest-item`, `.backtest-list` | Historial y favoritos | **Actualizado** | Tarjetas de historial interactivas. |
| `.btn-save-item`, `.btn-delete-item` | Acciones de historial | **Preservado** | Micro-botones de acción. |
| `.live-badge-span`, `.pulse-dot` | Badge de telemetría en vivo | **Actualizado** | Punto pulsante con ciclo de 2s. |
| `.tooltip`, `.tooltip-text` | Sistema de tooltips de ayuda | **Actualizado** | Posicionamiento superior con flecha inferior y fondo `#141d2e`. |
| `.text-green`, `.text-red` | Utilidades de color | **Actualizado** | Calibrados a `#10b981` y `#f43f5e`. |
| `::-webkit-scrollbar` | Scrollbars personalizados | **Actualizado** | Scrollbars discretos de 6px en `#1c273d`. |

---

## 6. ESTRUCTURA MODULAR DEL ARCHIVO `static/css/style.css`

El archivo `static/css/style.css` resultante estará estructurado en las siguientes 14 secciones claramente delimitadas por comentarios de bloque:

1. **Section 01**: CSS Variables & Design System Tokens (`:root`)
2. **Section 02**: CSS Reset, Base Elements & Tabular Typography Rules
3. **Section 03**: Layout Architecture & Institutional Header
4. **Section 04**: Hybrid Mode Switcher & Tabs Navigation
5. **Section 05**: Glassmorphic Containers & Card Primitives (`.glass-card`)
6. **Section 06**: Form Controls, Numeric Inputs & Custom Selects
7. **Section 07**: Button System & Micro-Interactions
8. **Section 08**: Smart Mode Dashboard & Barbell Control Bar
9. **Section 09**: Telemetry Console, SSE Logs & Shimmer Progress Bar
10. **Section 10**: Top Strategy Ranking Pills & Recommendation Cards
11. **Section 11**: Paroli Ladder & Step-by-Step Risk Engine
12. **Section 12**: Data Tables (Markov Transition, Trades History & N-Table)
13. **Section 13**: Stats Cards, Diagnostic Charts & Results Panels
14. **Section 14**: Status Indicators, Badges, Tooltips, Custom Scrollbars & Responsive Queries

---

## 7. MÉTODO DE VERIFICACIÓN INDEPENDIENTE

Para verificar que la refactorización de `style.css` cumple con todos los criterios de calidad de M1:

1. **Verificación de Tipografías y Cifras Tabulares**:
   - Inspeccionar con DevTools que las fuentes cargadas sean `Inter` y `JetBrains Mono`.
   - Comprobar que todas las celdas de `.markov-table`, `.trades-table`, `.n-table` y `.stat-card p` tengan aplicada la propiedad `font-variant-numeric: tabular-nums` y los dígitos queden perfectamente alineados verticalmente.
2. **Verificación de Contraste y Ausencia de Halación**:
   - Validar que no existan valores `#FFFFFF` aplicados directamente sobre fondos `#000000`.
   - Comprobar que el contraste del texto primario (`#f0f6fc`) contra la superficie base (`#0e1420`) cumpla WCAG AAA ($> 15:1$).
3. **Verificación de Selectores y Cero Regresiones**:
   - Verificar que todos los 89 IDs de `index.html` y las clases generadas dinámicamente en `app.js` rendericen con estilos coherentes y sin solapamientos.
4. **Verificación de Ejecución de Pruebas Unitarias del Backend**:
   - Ejecutar la suite de pruebas del proyecto (`pytest`) para garantizar que la estructura del servidor y endpoints se mantengan 100% operativos.
