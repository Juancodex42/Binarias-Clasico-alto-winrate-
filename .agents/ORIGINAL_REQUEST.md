# Original User Request

## 2026-08-12T14:15:44Z

Search space exploration y resolución de bugs de software en el simulador y motor de optimización de estrategias cuantitativas de opciones binarias para alcanzar un win rate y esperanza matemática (EV) superiores.

Working directory: c:/Users/juanc/Desktop/prueba
Integrity mode: development

## Requirements

### R1. Detección y corrección de bugs de software en el motor cuantitativo
Identificar y corregir inconsistencias, bugs o errores de cálculo en el motor de simulación (`BinarySimulator`), la extracción de features (`BinaryFeatureExtractor`), detección de régimen (`RegimeDetector` / `CUSUMMonitor`), etiquetadores (`MetaLabeler`) y la generación de señales/filtros en `engine/` y `strategies/`.

### R2. Exploración exhaustiva del espacio de búsqueda (Search Space Exploration)
Diseñar y ejecutar un esquema de exploración sistemática de espacio de parámetros (grid search, algoritmos genéticos y/o Optuna) evaluando combinaciones de hiperparámetros, temporalidades, regímenes de mercado y meta-filtros sobre los datos históricos para hallar las configuraciones con máximo Win Rate (>65%) y EV positiva Out-Of-Sample.

### R3. Verificación de robustez y prevención de sesgos cuantitativos
Asegurar que todas las simulaciones y el cálculo de indicadores/features respeten la estricta causalidad temporal (prevenir look-ahead bias y data leakage) en los splits de train/test y en la ejecución del backtest.

## Acceptance Criteria

### Integridad y Corrección de Software
- [ ] La suite de pruebas unitarias (`test_high_winrate_mechanisms.py` y nuevos tests de integridad) se ejecuta sin ningún fallo ni advertencia crítica.
- [ ] Se corrigen los errores y cuellos de botella en la ejecución del motor de optimización y simulación.

### Resultados de la Búsqueda y Estrategia
- [ ] Se encuentran y reportan las configuraciones de parámetros y filtros cuantitativos que optimizan el Win Rate (>65%) y la EV por trade out-of-sample.
- [ ] Se provee un script ejecutable de verificación/backtesting que demuestra de forma empírica y reproducible el rendimiento obtenido.
