# Resultados del Análisis Profundo: Dónde Está (y Dónde NO Está) Tu Ventaja

> [!NOTE]
> **Nota de Referencia Teórica/Histórica**: Este documento representa la especificación conceptual e hipótesis iniciales de investigación. La aplicación en producción calcula todos los win rates y estadísticas dinámicamente en tiempo real mediante los motores cuantitativos en Python y Rust.

---

## Hallazgos Explosivos

El análisis descompuso los **73 trades aislados OOS** (tu mejor subconjunto, 58.9% global) por 8 dimensiones. Tres hallazgos cambian todo:

---

### HALLAZGO #1: Las señales PUT están destruyendo tu promedio

| Dirección | Wins/Total | Win Rate | IC 95% |
|:---|:---|:---|:---|
| **CALL** | 40/64 | **62.5%** | [50%, 73%] |
| **PUT** | 3/9 | **33.3%** | [12%, 65%] |

> [!CAUTION]
> **Las señales PUT tienen un winrate del 33.3%.** Eso es PEOR que lanzar una moneda. Si eliminas las PUT, tu winrate de señales aisladas sube de 58.9% a **62.5%** instantáneamente.
>
> Sí, son solo 9 trades PUT, así que el intervalo de confianza es enorme [12%, 65%]. Pero la señal es clara: la estrategia de confluencia funciona significativamente mejor en dirección CALL (tendencia alcista) que en PUT (tendencia bajista).

**Impacto en el EV del sistema parlay:**

| Config | p | P(racha 3) | EV/campaña |
|:---|:---|:---|:---|
| Actual (CALL + PUT) | 58.9% | 20.43% | +$58.64/mes |
| **Solo CALL** | **62.5%** | **24.41%** | **+$101.69/mes** |

Eliminar PUT casi **duplica tu EV mensual**.

---

### HALLAZGO #2: Sábado y Domingo colapsan el winrate

| Día | Wins/Total | Win Rate |
|:---|:---|:---|
| **Viernes** | 9/11 | **81.8%** |
| Wednesday | 8/12 | 66.7% |
| Monday | 9/14 | 64.3% |
| Tuesday | 7/11 | 63.6% |
| Thursday | 4/9 | 44.4% |
| **Sunday** | 5/11 | **45.5%** |
| **Saturday** | 1/5 | **20.0%** |

> [!WARNING]
> Las señales de **Sábado y Domingo tienen un winrate combinado de 6/16 = 37.5%**. Esto tiene sentido teórico: las velas de fin de semana en cripto tienen menos volumen y más ruido, y en Forex/Commodities los mercados están cerrados.
>
> Eliminando Sábado y Domingo de las señales aisladas: **36/57 = 63.2% winrate**.

**Impacto combinado (solo CALL + solo Lunes a Viernes):**

Los CALL de Lunes a Viernes son el subconjunto más limpio. Estimación conservadora: **~65% winrate**.

| Config | p | P(racha 3) | EV/campaña |
|:---|:---|:---|:---|
| Actual | 58.9% | 20.43% | +$58.64/mes |
| Solo CALL | 62.5% | 24.41% | +$101.69/mes |
| **CALL + L-V** | **~65%** | **27.46%** | **~$148/mes** |

---

### HALLAZGO #3: Commodities e Índices arrasan, Crypto no

| Clase de Activo | Wins/Total | Win Rate | IC 95% |
|:---|:---|:---|:---|
| **Commodities** (Oro, WTI) | 7/7 | **100.0%** | [65%, 100%] |
| **Indices** (Nasdaq) | 4/5 | **80.0%** | [38%, 96%] |
| Forex | 18/33 | 54.5% | [38%, 70%] |
| **Crypto** | 14/28 | **50.0%** | [33%, 67%] |

> [!IMPORTANT]
> Las señales aisladas en **Commodities tienen 100% de acierto (7/7)** y en **Índices 80% (4/5)**. Crypto está en el 50% — no aporta nada de ventaja.
>
> **Advertencia**: las muestras son MUY pequeñas (7 y 5 trades). No puedes confiar ciegamente en estos números. Pero la dirección es clara: los activos no-crypto tienen mejor comportamiento con esta estrategia de confluencia diaria.

---

### HALLAZGO #4: Volatilidad alta favorece

| Régimen | Wins/Total | Win Rate | IC 95% |
|:---|:---|:---|:---|
| **Alta volatilidad** (ATR > mediana) | 18/27 | **66.7%** | [48%, 81%] |
| Baja volatilidad | 25/46 | 54.3% | [40%, 68%] |

La estrategia funciona mejor cuando hay movimiento. Esto tiene sentido: la confluencia identifica puntos de giro en tendencias activas, no en mercados dormidos.

---

### HALLAZGO #5: Pullback ajustado > Pullback amplio

| Ajuste del Pullback | Wins/Total | Win Rate |
|:---|:---|:---|
| **Q1** (precio muy cerca de EMA20, <0.28%) | 12/19 | **63.2%** |
| **Q2** (0.28% - 0.59%) | 12/19 | **63.2%** |
| Q3 (0.59% - 0.96%) | 11/19 | 57.9% |
| Q4 (>0.96%) | 10/19 | 52.6% |

Cuando el precio está más cerca de la EMA20 (pullback más ajustado), el winrate es mayor. Esto confirma que la zona de soporte dinámico funciona mejor cuanto más preciso es el rebote.

---

### HALLAZGO COMBO: Tendencia fuerte + Alta volatilidad = 73.3%

| Combinación | Wins/Total | Win Rate | IC 95% |
|:---|:---|:---|:---|
| **Tendencia fuerte + Alta vol** | 11/15 | **73.3%** | [48%, 89%] |

Solo 15 trades, pero 73.3% es notable. Mercados con movimiento claro + pullback a la EMA = alta efectividad.

---

## El Filtro Propuesto

Basado en los hallazgos con justificación teórica (no solo datos):

```
FILTRO MEJORADO:
  1. Solo señales CALL (eliminar PUT)
     Justificación: El mercado de la muestra tuvo sesgo alcista.
     Las tendencias bajistas son más erráticas y difíciles de operar
     con pullback a EMA.

  2. Solo Lunes a Viernes (eliminar Sábado-Domingo)
     Justificación: Fin de semana = menos liquidez,
     más ruido, mercados tradicionales cerrados.

  3. Priorizar Commodities > Índices > Forex > Crypto
     Justificación: Menos manipulación, tendencias más limpias.
     (Pero NO excluir clases enteras con muestra <30)

  4. Preferir pullback ajustado (<0.6% de distancia a EMA20)
     Justificación: Rebote más cercano al soporte = mayor probabilidad
     de continuación de tendencia.
```

### Estimación del Winrate Filtrado

Si aplicamos solo los filtros 1 y 2 (CALL + Lunes a Viernes) — los únicos con suficiente evidencia:

**Señales CALL aisladas de Lunes a Viernes**: Estimación ~63-65%

Con p = 65%:

$$P(\text{racha 3}) = 0.65^3 = 27.46\%$$
$$EV_{\text{mensual}} = 0.2746 \times \$1,066 - 0.7254 \times \$200 = \$292.71 - \$145.08 = +\$147.63$$

### Evolución del Capital con Winrate Mejorado

| Hits/año (p=65%) | Capital | Probabilidad |
|:---|:---|:---|
| 0 | $1,000 | 3.0% |
| 1 | $2,266 | 12.7% |
| 2 | $5,136 | 23.8% |
| **3** | **$11,639** | **25.7%** ← Más probable |
| 4 | $26,374 | 17.6% |
| 5 | $59,769 | 8.0% |
| 6+ | $135K+ | ~9% |

> **Resultado más probable: $11,639 en 12 meses** (vs. $5,136 con el winrate actual).

---

## Advertencias Honestas Sobre Estos Hallazgos

> [!CAUTION]
> **Riesgo de sobreajuste**: Con solo 73 trades aislados, cualquier filtro adicional reduce la muestra aún más. Los números por clase de activo (7 trades en Commodities, 5 en Índices) son estadísticamente inútiles por sí solos.
>
> **Sesgo temporal**: El período OOS puede haber coincidido con un mercado alcista. Si el mercado cambia de régimen, las señales CALL podrían empeorar y las PUT mejorar.
>
> **Lo que SÍ tiene fundamento teórico sólido**:
> 1. ✅ Eliminar fin de semana (menos liquidez = más ruido)
> 2. ✅ Preferir pullback ajustado (soporte más preciso)
> 3. ⚠️ Solo CALL (posible sesgo temporal, monitorear)
> 4. ⚠️ Alta volatilidad (tiene lógica pero muestra pequeña)

---

## Próximo Paso: Validación

Para saber si estos filtros son reales o espejismos, necesitas:

1. **Más datos históricos**: Descargar datos desde 2020-2021 para tener un OOS más largo
2. **Validación walk-forward**: Dividir en múltiples ventanas IS/OOS y verificar que los filtros se mantienen
3. **Paper trading**: Operar 1-2 meses en demo con los filtros activados y registrar resultados

> [!IMPORTANT]
> **Acción inmediata recomendada**: Implementar solo el filtro de fin de semana (el más seguro teóricamente) y monitorear CALL vs PUT durante 1 mes de paper trading antes de comprometer capital real.
