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
