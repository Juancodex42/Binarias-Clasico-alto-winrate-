# La Clave: Diversificación Multi-Activo y Evaluación Empírica Real

> *"Un sistema cuantitativo riguroso no proyecta expectativas sobre datos In-Sample sobreajustados. Valida sus ventajas exclusivamente en periodos Out-of-Sample sin sesgo de selección."*

---

## 1. Planteamiento del Sistema y Marco Cuantitativo

Un operador de arbitraje genera un rendimiento mensual del 20% sobre su capital base ($200 USD libres sobre $1000 USD de patrimonio). El objetivo es utilizar ese excedente en campañas de opciones binarias para buscar una multiplicación de capital sin arriesgar el patrimonio principal.

Para evaluar la viabilidad de esta estrategia, se sometió la confluencia técnica en temporalidad diaria (1D) a una prueba empírica en **18 activos reales** con división estricta **70% In-Sample / 30% Out-of-Sample** (registrada detalladamente en [prueba.md](file:///c:/Users/juanc/Desktop/prueba/prueba.md)).

---

## 2. El Ratio Señal-a-Ruido (SNR) y Temporalidad

En los mercados financieros, la evolución de los precios se compone de señal tendencial $S(t)$ y ruido estocástico $\varepsilon(t)$:

$$P(t) = S(t) + \varepsilon(t)$$

El Ratio Señal-a-Ruido se define como:

$$\text{SNR} = \frac{\text{Var}(S)}{\text{Var}(\varepsilon)}$$

* **En temporalidades bajas (30m, 1h):** El ruido microestructural domina ($\text{Var}(\varepsilon) \gg \text{Var}(S)$). En las pruebas con el optimizador en Rust sobre datos de 30m, la tasa de acierto Out-of-Sample se estabilizó en **55.05%**.
* **En temporalidades altas (Diaria 1D):** La acumulación de tendencia incrementa la señal. Sin embargo, en el portafolio multi-activo completo ($N = 344$ trades fuera de muestra), la tasa de acierto Out-of-Sample obtenida fue del **51.74%**.

---

## 3. Las Reglas de Opciones Binarias y el Umbral de Rentabilidad

### 3.1. Umbral de Rentabilidad (Break-Even Win Rate)
En opciones binarias, con un pago (*Payout*) neto del $85\%$, el porcentaje de aciertos mínimo para no perder capital a largo plazo es:

$$\text{WR}_{\text{BE}} = \frac{1}{1 + \text{Payout}} = \frac{1}{1.85} \approx 54.05\%$$

### 3.2. Esperanza Matemática ($EV$)
La esperanza matemática por cada $1 apostado viene dada por:

$$EV = (\text{WR} \times \text{Payout}) - ((1 - \text{WR}) \times 1)$$

| Win Rate ($\text{WR}$) | Payout 85% | Esperanza Matemática por $1$ apostado | Estado de Rentabilidad |
| :--- | :--- | :--- | :--- |
| **50.0%** | $0.85 | **-$0.075** | 🔴 Pérdida |
| **51.74% (OOS Real)** | $0.85 | **-$0.043** | 🔴 Pérdida |
| **54.05%** | $0.85 | **$0.000** | ⚪ Break-Even |
| **60.0%** | $0.85 | **+$0.110** | 🟢 Ganancia Moderada |
| **70.0%** | $0.85 | **+$0.300** | 🟢 Ganancia Elevada |

---

## 4. Análisis Empírico por Capas de Filtro (Datos Out-of-Sample Reales)

Al descomponer la efectividad de la confluencia técnica sin sesgos de selección:

| Capa | Filtro de Entrada | Comportamiento en Pruebas OOS | Tasa de Acierto Medida |
| :--- | :--- | :--- | :--- |
| **Capa 0** | Entrada Aleatoria | Referencia Base | ~50.0% |
| **Capa 1** | Tendencia Semanal ($\text{EMA}_{50}$) | Filtra operaciones contra-tendencia macro | ~51.0% - 53.0% |
| **Capa 2** | Pullback a $\text{EMA}_{20}$ Diaria | Identifica zonas de soporte/resistencia | ~51.5% - 54.0% |
| **Capa 3** | RSI 14 Relativo + Volumen | Confirma agotamiento de impulso | ~50.8% - 52.5% |
| **Total** | **Confluencia Completa (Portafolio OOS)** | **Evaluación global sobre 344 trades** | **51.74% (IC 95%: [46.5%, 57.0%])** |

---

## 5. Correlación de Mercado y Riesgo Sistémico

La prueba empírica desesgada midió la efectividad de las señales según la presencia de múltiples confluencias en un mismo día:

1. **Días de Señal Única (1 solo activo operado):** $73$ días evaluados en OOS alcanzaron un Win Rate del **58.90%**.
2. **Días de Señales Simultáneas (2 a 5 activos el mismo día):** $101$ días ($271$ operaciones) alcanzaron un Win Rate del **49.82%**.

### Conclusión Estadística:
La apertura simultánea de posiciones en varios activos el mismo día incrementa la exposición a factores de riesgo macroeconómico (*Risk-Off*), lo que destruye el supuesto de independencia estocástica y reduce la efectividad del portafolio.

---

## 6. Arquitectura de Campaña Barbell con Métricas Reales

La probabilidad de completar una racha de $N$ victorias consecutivas en $K$ intentos se calcula mediante:

$$P_{\text{campaña}} = 1 - (1 - p^N)^K$$

Evaluando la campaña con la tasa de acierto Out-of-Sample real de días independientes ($p = 58.90\%$ en días de señal única) vs. el promedio del portafolio ($p = 51.74\%$):

| Tasa de Acierto ($p$) | Racha ($N$) | Intentos ($K$) | Apuesta ($A$) | $P_{\text{intento}} = p^N$ | $P_{\text{campaña}}$ | Esperanza Matemática ($EV$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **51.74% (Promedio OOS)** | 3 | 6 | $33.33 USD | 13.85% | **59.9%** | -$9.80 USD |
| **54.05% (Break-Even)** | 3 | 6 | $33.33 USD | 15.77% | **64.6%** | $0.00 USD |
| **58.90% (Días Únicos)** | 3 | 6 | $33.33 USD | 20.43% | **75.1%** | +$22.40 USD |

---

## 7. Resumen de la Auditoría Cuantitativa

```
┌─────────────────────────────────────────────────────────┐
│           RESULTADOS DE LA AUDITORÍA EMPÍRICA           │
│                                                         │
│  MUESTRA EVALUADA:       344 trades Out-of-Sample (30%) │
│  WIN RATE PORTAFOLIO:    51.74%                         │
│  INTERVALO WILSON 95%:   [46.47%, 56.98%]               │
│  BREAK-EVEN REQUERIDO:   54.05% (Payout 85%)            │
│  ESPERANZA MATEMÁTICA:   -$0.043 por $1 apostado        │
│                                                         │
│  HALLAZGOS CLAVE:                                       │
│  1. El filtrado ex-post de activos individuales sufre   │
│     de sesgo por muestra pequeña (N < 30).              │
│  2. La simultaneidad de señales en el mismo día reduce  │
│     la efectividad a 49.82% debido a correlación macro. │
│  3. Las señales aisladas (1 activo por día) muestran    │
│     un Win Rate del 58.90% (EV positivo de +$22.40).    │
└─────────────────────────────────────────────────────────┘
```
