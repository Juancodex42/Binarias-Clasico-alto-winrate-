# Original User Request

## Initial Request — 2026-08-12T13:15:30Z

You are the Project Orchestrator for the binary options quantitative strategy simulator and optimization engine project.

Your Working Directory: c:\Users\juanc\Desktop\prueba\.agents\orchestrator_1
Project Workspace: c:\Users\juanc\Desktop\prueba
Original Request File: c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md

Mission & Requirements:
1. R1. Detección y corrección de bugs de software en el motor cuantitativo:
   Identificar y corregir inconsistencias, bugs o errores de cálculo en BinarySimulator, BinaryFeatureExtractor, RegimeDetector / CUSUMMonitor, MetaLabeler, y la generación de señales/filtros en engine/ y strategies/.
2. R2. Exploración exhaustiva del espacio de búsqueda (Search Space Exploration):
   Diseñar y ejecutar un esquema de exploración sistemática de espacio de parámetros (grid search, algoritmos genéticos y/o Optuna) evaluando combinaciones de hiperparámetros, temporalidades, regímenes de mercado y meta-filtros sobre los datos históricos para hallar las configuraciones con máximo Win Rate (>65%) y EV positiva Out-Of-Sample.
3. R3. Verificación de robustez y prevención de sesgos cuantitativos:
   Asegurar que todas las simulaciones y el cálculo de indicadores/features respeten la estricta causalidad temporal (prevenir look-ahead bias y data leakage) en los splits de train/test y en la ejecución del backtest.

Acceptance Criteria:
- Unit test suite (test_high_winrate_mechanisms.py and new integrity tests) executes with zero failures or critical warnings.
- Execution errors and bottlenecks in optimization and simulation engines are resolved.
- Optimal parameter configurations and quantitative filters with Out-Of-Sample Win Rate > 65% and positive EV per trade are identified and reported.
- An executable verification/backtest script demonstrating empirical and reproducible results is provided.

Operating Guidelines:
- Create your working directory c:\Users\juanc\Desktop\prueba\.agents\orchestrator_1 and initialize your BRIEFING.md and plan.md.
- Maintain progress.md in your working directory updated with real-time status so Sentinel can monitor project health.
- Dispatch specialist subagents as needed for exploration, bug fixing, test suite expansion, and verification.
- When all milestones are complete, report victory back to Sentinel.

## 2026-08-16T19:17:27Z

Rediseño integral de la interfaz de usuario (UI/UX) del Terminal Cuantitativo y Simulador de Opciones Binarias, implementando con máxima fidelidad el sistema de diseño, ergonomía visual en modo oscuro y principios neuropsicológicos detallados en `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`.

Working directory: c:\Users\juanc\Desktop\prueba
Integrity mode: development

Reference Document: `c:\Users\juanc\Desktop\prueba\documentos_md\GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`

## Requirements

### R1. Implementación del Sistema de Diseño Visual y Paleta Cromática Institucional
- Aplicar la arquitectura de color en capas: Canvas de fondo (`#080b11`), Superficie de tarjetas base (`#0e1420`), Superficies elevadas (`#141d2e`), bordes sutiles de 1px (`rgba(255, 255, 255, 0.07)`), y acentos semánticos calibrados (`#38bdf8` acción/foco, `#10b981` ganancias/CALL, `#f43f5e` pérdidas/PUT, `#a855f7` optimización cuántica, `#f59e0b` arbitraje/balas).
- Eliminar la halación retiniana (astigmatismo) y la cromoestereopsis (evitar contrastes agresivos de blanco puro sobre negro puro y suprimir la vibración óptica rojo-azul neón).

### R2. Arquitectura de Layout, Densidad de Datos y Composición Geométrica
- Reorganizar el layout en módulos armónicos siguiendo el sistema de espaciado 8-point grid y curvaturas sobrias (`8px - 10px` para tarjetas, `6px` para botones/inputs, `9999px` para pills de estado).
- Diseñar un Header institucional unificado con selector de modo (Modo Inteligente / Modo Avanzado) y badges de estado.
- Estructurar la barra de control compacta de alta densidad con presets inteligentes claros y controles numéricos ordenados.

### R3. Tipografía y Alineación Numérica Tabular
- Configurar tipografía `Inter` / `Geist Sans` para la interfaz y `JetBrains Mono` con cifras tabulares (`font-variant-numeric: tabular-nums`) para todas las tablas (Markov, correlaciones, balances y métricas clave).

### R4. Integración y Armonización de Gráficos y Micro-interacciones
- Adaptar visualmente TradingView Lightweight Charts (velas y señales CALL/PUT) y gráficos Chart.js (Curva de Capital, Conos Monte Carlo P5-P95, Heatmap de Correlación) para que se fundan elegantemente en el nuevo tema oscuro sin fondos contrastantes molestos.
- Implementar micro-interacciones ágiles (hover, estados activos, transiciones suaves de 150ms-220ms con `cubic-bezier(0.16, 1, 0.3, 1)`).

### R5. Preservación Total de la Funcionalidad y Endpoints del Backend
- Mantener intactos todos los identificadores HTML (`id`, `class` funcionales), formularios, selectores de activos, botones de ejecución (`⚡ Auto-Optimizar Estrategia`, `Ejecutar Backtest`) y eventos JavaScript para que el 100% de la lógica de backtest, optimización genética en Rust y llamadas a la API de Flask sigan funcionando sin errores.

## Acceptance Criteria

### Visual & Theme Compliance
- [ ] La interfaz utiliza rigurosamente la paleta de colores, bordes y tipografías definidas en `GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`.
- [ ] No existen textos con blanco puro `#FFFFFF` sobre fondo negro `#000000` ni elementos con vibración óptica cromoestereóptica.

### Typography & Numerical Alignment
- [ ] Todos los valores numéricos en tablas (Markov, Activos seleccionados), métricas y cards utilizan tipografía monoespaciada con cifras tabulares alineadas verticalmente.

### Data Visualization & Charts
- [ ] El gráfico de velas japonesas (Lightweight Charts), la curva de equity, las proyecciones Monte Carlo y el heatmap de correlación renderizan sin errores en consola y se adaptan fluidamente al tamaño del contenedor.

### Functional Integrity & Usability
- [ ] El cambio entre "Modo Inteligente" y "Modo Avanzado" funciona de forma fluida.
- [ ] Los botones de optimización y backtest ejecutan sus respectivas rutinas y muestran el progreso en la consola y las gráficas actualizadas.
- [ ] Cero errores en la consola de JavaScript del navegador durante la carga y la interacción estándar.

