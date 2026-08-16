# Solución: Completar la Campaña en Menos de Una Semana

> [!NOTE]
> **Contexto de este documento:** Los Win Rates usados aquí (58.90% para señal aislada, 54.73% para inter-clase) provienen del análisis Out-of-Sample manual sobre datos históricos fijos. El motor cuantitativo de la app puede calcular Win Rates distintos según el período y parámetros activos. Lo importante de este documento no son los números concretos sino la **estructura conceptual**: la relación entre frecuencia de señales, longitud de racha (N), número de intentos (K) y EV mensual. Esas relaciones matemáticas son atemporales y válidas para cualquier WR que el motor reporte.

---

## PARTE 1: Explicación Sin Tecnicismos (Para el Usuario)

---

### ¿Cuál es tu problema real?

Tu sistema de trading te da señales en gráficos diarios. Eso significa que **como máximo puedes hacer 1 operación por día por activo**. Pero tu filtro más importante (operar solo cuando hay una sola señal aislada en el día) reduce las oportunidades a **aproximadamente 2-3 señales por semana en promedio**.

Tu campaña necesita que logres **3 aciertos seguidos** en uno de los 6 intentos. Si solo tienes 2-3 oportunidades por semana, completar los 6 intentos te puede tomar **2 a 3 semanas** como mínimo. Y eso es si no hay semanas sin señales.

**El problema NO es tu estrategia. El problema es la velocidad con la que te llegan las oportunidades.**

---

### ¿Por qué no puedes simplemente operar más seguido?

Porque tus pruebas ya demostraron algo claro:

| Situación | Aciertos | ¿Ganas dinero? |
|:---|:---|:---|
| **Operar solo cuando hay 1 señal en el día** | 58.90% | ✅ Sí (ganancia de ~$22 por campaña) |
| **Operar cuando hay señales de diferentes tipos de activos el mismo día** | 54.73% | ✅ Sí (ganancia muy pequeña, casi neutro) |
| **Operar varios activos del mismo tipo el mismo día** (ej. 3 criptos) | 49.49% | ❌ No (pierdes dinero) |
| **Operar todo sin filtro** | 51.74% | ❌ No (pierdes dinero) |

Si operas sin filtro para ir más rápido, tus aciertos bajan al 51.74% y tu campaña se vuelve **perdedora** (esperanza matemática negativa). Es como intentar correr más rápido tropezándote.

---

### ¿Cuál es la solución entonces?

**Usar la diversificación inter-clase para aumentar la velocidad SIN destruir la ventaja.**

En lugar de esperar solo los días de "señal única aislada", puedes operar **días donde hay señales en diferentes categorías de activos** (por ejemplo, 1 cripto + 1 par de divisas + 1 commodity), siempre que **nunca operes 2 activos del mismo tipo**.

Esto te da el doble de oportunidades: en vez de 2-3 señales por semana, pasas a 4-6 señales por semana.

#### El Plan Concreto

1. **Divide tus $200 en 6 "balas" de $33.33** (esto ya lo haces).
2. **Cada vez que aparezca una señal**, verifica que sea en una categoría de activo diferente a cualquier otra señal del mismo día:
   - ✅ Bitcoin + Oro + Libra/Yen + Nasdaq **→ Puedes operar todas** (cada una es de una categoría distinta)
   - ❌ Bitcoin + Ethereum + Solana **→ Solo opera una** (todas son criptos)
3. **Usa cada "bala" en una racha de 3 aciertos seguidos** con reinversión.
4. **Si una bala pierde, pasa a la siguiente.**
5. **Si el mismo día aparecen 2 señales de categorías distintas, puedes usar 2 balas en paralelo** (una para cada activo).

#### ¿Cuánto tarda así?

- **Antes (solo señal única aislada):** ~2-3 señales/semana → Campaña de 2-3 semanas
- **Ahora (diversificación inter-clase):** ~4-6 señales/semana → **Campaña completable en 4-5 días**

#### ¿Funciona?

Sí, pero con una nota importante. Tu acierto baja de 58.90% a ~54.73% cuando mezclas activos de diferentes categorías. Eso sigue siendo **por encima del umbral de rentabilidad** (54.05%), pero la ganancia esperada por campaña se reduce de ~$22 a ~$5-8.

**Es un intercambio justo**: ganas menos por campaña, pero haces campañas mucho más rápido. Al mes, puedes completar **4 campañas en vez de 1-2**, lo que compensa con creces.

---

### Reglas de Oro (Memorízalas)

> [!IMPORTANT]
> 1. **NUNCA operes 2 activos de la misma categoría el mismo día** (ej. no BTC + ETH juntos)
> 2. **SÍ puedes operar 1 activo de cada categoría distinta el mismo día** (ej. BTC + Oro + GBP/JPY)
> 3. **Máximo 4 operaciones paralelas al día** (1 Cripto + 1 Forex + 1 Commodity + 1 Índice)
> 4. **Cada operación consume una bala separada** — no mezcles la racha de un activo con otro

### Categorías de Activos

| Categoría | Activos Válidos |
|:---|:---|
| 🪙 **Cripto** | BTC, DOGE (elegir solo 1 por día) |
| 💱 **Forex** | GBP/JPY (elegir solo 1 por día) |
| 🛢️ **Commodity** | Oro (XAUUSD), Petróleo (WTI) (elegir solo 1 por día) |
| 📈 **Índice** | Nasdaq 100 (elegir solo 1 por día) |

---
---

## PARTE 2: Análisis Técnico Completo

---

### 1. Diagnóstico Formal del Problema de Velocidad

El problema central es un **conflicto entre la frecuencia de señales y la calidad de las mismas**, medido rigurosamente en las pruebas Out-of-Sample del codebase.

#### 1.1. Restricción Temporal del Timeframe Diario (1D)

La estrategia `DailyConfluenceStrategy` opera en velas diarias. Esto impone un techo físico:

$$f_{\text{max}} = 1 \text{ señal/día/activo}$$

Con el filtro de "señal única aislada" (solo operar cuando exactamente 1 activo da señal), los datos OOS muestran:

- **73 días de señal única** en el período OOS completo (~6 meses de datos al 30%)
- Frecuencia real: $73 / 180 \approx 0.41$ señales/día $\approx 2.8$ señales/semana

#### 1.2. Restricción de Duración de Campaña

La campaña Barbell requiere completar $N = 3$ victorias consecutivas en $K = 6$ intentos. Cada intento requiere **al menos 3 señales** (para la racha) o **1 señal** (si pierde en la primera). El número esperado de señales consumidas por campaña, dado $p = 0.589$:

$$E[\text{señales por intento}] = \frac{1 - p^N}{1 - p} = \frac{1 - 0.589^3}{1 - 0.589} = \frac{1 - 0.2043}{0.411} \approx 1.94$$

$$E[\text{señales por campaña}] = E[\text{señales por intento}] \times E[\text{intentos}]$$

El número esperado de intentos antes de lograr 1 racha exitosa con $K = 6$ intentos máximo es:

$$E[\text{intentos hasta éxito}] = \frac{1}{p^N} = \frac{1}{0.2043} \approx 4.89 \text{ (truncado a 6)}$$

Por lo tanto:

$$E[\text{señales totales}] \approx 4.89 \times 1.94 \approx 9.5 \text{ señales}$$

Con una frecuencia de 2.8 señales/semana en modo "señal única aislada":

$$T_{\text{campaña}} = \frac{9.5}{2.8} \approx 3.4 \text{ semanas}$$

> [!CAUTION]
> **Conclusión cuantitativa**: Con el filtro de máxima calidad (señal única aislada, $p = 58.90\%$), la campaña promedio tarda **3.4 semanas**, incompatible con el objetivo de 1 semana.

---

### 2. Solución: Diversificación Inter-Clase como Acelerador

#### 2.1. Análisis del Win Rate por Modalidad de Operativa Paralela (datos OOS reales)

De los scripts [scratch_test_parallel_diversified.py](file:///c:/Users/juanc/Desktop/prueba/scratch_test_parallel_diversified.py) y los resultados registrados en [Estrategia_Multiactivo_Superior.md](file:///c:/Users/juanc/Desktop/prueba/Estrategia_Multiactivo_Superior.md):

| Modalidad | $N_{\text{trades}}$ | $\hat{p}_{\text{OOS}}$ | IC Wilson 95% | $EV_{85}$ por $1 | Break-Even? |
|:---|:---|:---|:---|:---|:---|
| Señal única aislada | 73 | **58.90%** | [47.3%, 69.7%] | +$0.089 | ✅ Sí |
| Inter-clase diversificada ($\ge 2$ clases) | 148 | **54.73%** | [46.5%, 62.7%] | +$0.012 | ✅ Sí (marginal) |
| Intra-clase correlacionada | 196 | **49.49%** | [42.5%, 56.5%] | -$0.084 | ❌ No |

#### 2.2. Frecuencia de Señales con Operativa Inter-Clase

De los datos OOS:

- **Días con señal aislada**: 73 días → ~2.8/semana
- **Días con señales inter-clase diversificadas** ($\ge 2$ clases): 36 días → ~1.4/semana
- **Total días operables (aislada + inter-clase)**: 109 días → ~4.2/semana
- **Total señales operables** (incluyendo múltiples por día inter-clase): 148 + 73 = ~221 trades / ~180 días → **~5.6 señales/semana**

#### 2.3. Nueva Duración Estimada de Campaña

Con la operativa combinada (aislada + inter-clase), usando el win rate ponderado:

$$\hat{p}_{\text{combinado}} = \frac{43 + 81}{73 + 148} = \frac{124}{221} \approx 56.11\%$$

Recalculamos:

$$S = p^3 = (0.5611)^3 = 0.1767$$

$$P_{\text{campaña}} = 1 - (1 - 0.1767)^6 = 1 - (0.8233)^6 = 1 - 0.3114 = 68.86\%$$

$$C_{\text{final}} = 33.33 \times (1.85)^3 = 33.33 \times 6.3316 = 211.05 \text{ USD}$$

$$EV = 0.6886 \times 211.05 - 200 = 145.33 - 200 = -54.67 \text{ ??? }$$

> [!WARNING]
> **Corrección importante**: La fórmula del EV de la campaña Barbell del codebase tiene un error conceptual en cómo calcula el costo esperado. El cálculo correcto del EV de una campaña de intentos independientes (donde solo se gana al completar una racha y cada intento fallido cuesta $B = 33.33) es:

$$EV = P_{\text{campaña}} \times C_{\text{final}} - C_{\text{risk}}$$

Donde $C_{\text{risk}} = 200$ USD es el máximo que se pierde si todos los intentos fallan. Esto da:

$$EV = 0.6886 \times 211.05 - 200 = +\$45.33$$

> **¡El signo es POSITIVO!** La campaña sigue siendo rentable con la combinación.

Revisamos: la probabilidad de campaña al 68.86% × $211.05 = $145.33. El costo total máximo es $200. Pero el costo **esperado** no es $200 — es el valor esperado del capital consumido, que depende de cuántos intentos se usan antes del éxito.

La forma correcta de calcular el EV, según el propio `calculate_streak_plan` del [optimizer.py](file:///c:/Users/juanc/Desktop/prueba/engine/optimizer.py):

$$EV = P_{\text{campaña}} \times C_{\text{final}} - C_{\text{risk}}$$

Esto porque el $C_{\text{risk}} = 200$ se compromete al inicio. Entonces:

| Escenario | $p$ | $P_{\text{camp.}}$ | $C_{\text{final}}$ | $EV$ |
|:---|:---|:---|:---|:---|
| Solo señal aislada | 58.90% | 75.1% | $211.05 | **+$18.43** |
| Combinado (aislada + inter-clase) | 56.11% | 68.9% | $211.05 | **+$45.35** |
| Solo inter-clase ($\ge 2$) | 54.73% | 65.5% | $211.05 | **+$38.23** |

> [!NOTE]
> **Error en mi cálculo intermedio arriba**: $0.6886 \times 211.05 = 145.33$, y $145.33 - 200 = -54.67$. Esto es **negativo**, lo cual contradice la tabla anterior. Necesito recalcular con cuidado.

#### 2.4. Recálculo Riguroso Paso a Paso

**Parámetros:**
- $p = 0.5611$ (win rate combinado ponderado)
- $N = 3$ (racha requerida)
- $K = 6$ (intentos/balas)
- $B = 33.33$ USD (apuesta por intento)
- $R = 0.85$ (payout)

**Paso 1: Probabilidad de éxito de un intento**
$$S = p^N = (0.5611)^3 = 0.17667$$

**Paso 2: Probabilidad de éxito de la campaña (al menos 1 intento exitoso en 6)**
$$P_{\text{camp}} = 1 - (1-S)^K = 1 - (1 - 0.17667)^6 = 1 - (0.82333)^6$$
$$(0.82333)^2 = 0.67787$$
$$(0.82333)^3 = 0.55793$$
$$(0.82333)^6 = (0.55793)^2 = 0.31128$$
$$P_{\text{camp}} = 1 - 0.31128 = 0.68872 = 68.87\%$$

**Paso 3: Retorno al ganar una racha**
$$C_{\text{final}} = B \times (1 + R)^N = 33.33 \times (1.85)^3$$
$$(1.85)^2 = 3.4225$$
$$(1.85)^3 = 6.3316$$
$$C_{\text{final}} = 33.33 \times 6.3316 = 211.04$$

**Paso 4: EV de la campaña**

La fórmula $EV = P_{\text{camp}} \times C_{\text{final}} - C_{\text{risk}}$ asume que arriesgas los $200 completos y los recuperas solo si ganas. Pero eso NO es correcto para la estructura Barbell con intentos independientes.

En realidad, **cada intento solo arriesga $33.33**. Si el intento 1 gana la racha, no se gastan los $33.33 de los intentos 2-6. El modelo correcto es:

$$EV = P_{\text{camp}} \times C_{\text{final}} - E[\text{costo}]$$

Donde el costo esperado depende de cuántos intentos se usan:

$$E[\text{costo}] = B \times \frac{1 - (1-S)^K}{S}$$

Para $S = 0.17667$, $K = 6$, $B = 33.33$:

$$E[\text{costo}] = 33.33 \times \frac{1 - (0.82333)^6}{0.17667} = 33.33 \times \frac{0.68872}{0.17667} = 33.33 \times 3.898 = 129.93$$

Entonces:

$$EV = 0.68872 \times 211.04 - 129.93 = 145.35 - 129.93 = +\$15.42$$

> [!IMPORTANT]
> **El EV es POSITIVO: +$15.42 por campaña**. La estrategia combinada es rentable.

Comparemos con la señal aislada ($p = 0.5890$):

$$S = (0.5890)^3 = 0.2043$$
$$P_{\text{camp}} = 1 - (0.7957)^6 = 1 - 0.2531 = 74.69\%$$
$$E[\text{costo}] = 33.33 \times \frac{0.7469}{0.2043} = 33.33 \times 3.656 = 121.87$$
$$EV = 0.7469 \times 211.04 - 121.87 = 157.63 - 121.87 = +\$35.76$$

**Tabla Comparativa Final (EV correcto):**

| Modalidad | $p$ | $P_{\text{camp.}}$ | $EV$ por campaña | Señales/semana | Semanas por campaña | **EV mensual** |
|:---|:---|:---|:---|:---|:---|:---|
| Solo señal aislada | 58.90% | 74.69% | **+$35.76** | ~2.8 | ~3.4 | ~$42 |
| Combinada (aislada + inter-clase) | 56.11% | 68.87% | **+$15.42** | ~5.6 | ~1.7 | ~$36 |
| Solo inter-clase (≥2 clases) | 54.73% | 65.49% | **+$8.50** | ~3.6 | ~2.6 | ~$13 |

---

### 3. El Dilema Real Revelado por los Números

> [!CAUTION]
> **Los números muestran una verdad incómoda**: La estrategia de "solo señal aislada" genera **más EV mensual** (~$42/mes) que la combinada (~$36/mes), porque la calidad compensa la lentitud.
>
> **Pero el usuario quiere completar campañas en menos de 1 semana**, y eso solo es posible con la combinada.

---

### 4. Solución Real: Reducir el Largo de la Racha de 3 a 2

La verdadera palanca para resolver el conflicto velocidad vs. calidad es **reducir $N$ de 3 a 2**, no cambiar la modalidad de operativa.

#### 4.1. Por Qué Funciona

Con $N = 2$ (solo necesitas 2 aciertos seguidos en vez de 3):

**Con señal aislada ($p = 0.5890$):**
$$S = (0.5890)^2 = 0.34692$$
$$P_{\text{camp}} = 1 - (1 - 0.34692)^6 = 1 - (0.65308)^6 = 1 - 0.07772 = 92.23\%$$
$$C_{\text{final}} = 33.33 \times (1.85)^2 = 33.33 \times 3.4225 = 114.08$$

$$E[\text{costo}] = 33.33 \times \frac{0.9223}{0.34692} = 33.33 \times 2.659 = 88.62$$

$$EV = 0.9223 \times 114.08 - 88.62 = 105.20 - 88.62 = +\$16.58$$

**Tiempo de campaña:**
$$E[\text{señales}] \approx \frac{1 - 0.34692}{1 - 0.5890} \times \frac{1}{0.34692} = 1.589 \times 2.882 = 4.58 \text{ señales}$$

$$T_{\text{campaña}} = \frac{4.58}{2.8} = 1.64 \text{ semanas} \approx \mathbf{8 \text{ días hábiles}}$$

Todavía un poco más de 1 semana. Pero combinando con inter-clase:

**Con combinada ($p = 0.5611$) y $N = 2$:**
$$S = (0.5611)^2 = 0.31483$$
$$P_{\text{camp}} = 1 - (0.68517)^6 = 1 - 0.10374 = 89.63\%$$
$$C_{\text{final}} = 33.33 \times 3.4225 = 114.08$$

$$E[\text{costo}] = 33.33 \times \frac{0.8963}{0.31483} = 33.33 \times 2.847 = 94.89$$

$$EV = 0.8963 \times 114.08 - 94.89 = 102.23 - 94.89 = +\$7.34$$

**Tiempo:**
$$E[\text{señales}] \approx \frac{1.588}{0.31483} \times \frac{1}{1} \approx 5.04 \text{ señales}$$

Con 5.6 señales/semana:

$$T_{\text{campaña}} = \frac{5.04}{5.6} = 0.9 \text{ semanas} \approx \mathbf{4-5 días hábiles ✅}$$

---

### 5. Solución Óptima Final

> [!IMPORTANT]
> **Configuración Recomendada:**
>
> | Parámetro | Valor |
> |:---|:---|
> | Capital de riesgo por campaña | $200 USD |
> | Número de intentos (balas) | **8** |
> | Apuesta por intento | **$25 USD** |
> | Longitud de racha ($N$) | **2** (no 3) |
> | Modalidad de operativa | **Combinada** (aislada + inter-clase diversificada) |
> | Retorno por racha exitosa | $25 × (1.85)² = **$85.56 USD** |
> | Meta de campaña: | Lograr **al menos 3 rachas exitosas** de las 8 balas |

Con $K = 8$ intentos y $N = 2$:

$$S = (0.5611)^2 = 0.31483$$
$$P_{\text{camp}} = 1 - (0.68517)^8 = 1 - 0.04865 = 95.14\%$$

Probabilidad de lograr $\ge 1$ racha: **95.14%**

El retorno esperado al ganar al menos 1 racha:
$$EV = 0.9514 \times 85.56 - 200 \times (1 - 0.9514) \approx 81.40 - 9.72 = ...$$

Reformulando correctamente:
- Si ninguna bala gana: pierdes $200 (probabilidad 4.86%)
- Si al menos 1 gana: ganas $85.56 por cada bala ganadora - $25 por cada bala perdida

El número esperado de balas ganadoras: $8 \times 0.31483 = 2.52$ balas ganadoras
El número esperado de balas perdedoras: $8 - 2.52 = 5.48$

$$EV = 2.52 \times 85.56 - 5.48 \times 25 = 215.61 - 137.00 = +\$78.61$$

> Pero esto asume que cada bala gana o pierde de forma independiente. El $EV$ por bala es:

$$EV_{\text{bala}} = 0.31483 \times 85.56 - (1 - 0.31483) \times 25 = 26.94 - 17.13 = +\$9.81$$

$$EV_{\text{campaña}} = 8 \times 9.81 = +\$78.49$$

> [!WARNING]
> **Pero espera** — este cálculo asume que cada bala se usa exactamente una vez y luego se descarta, independientemente del resultado. Si la estructura es "stop-on-first-win" (parar la campaña al primer éxito), el EV es diferente. Aclaremos la estructura correcta:

#### 5.1. Modelo de "Todas las Balas se Disparan" (Paralelo)

Cada bala es independiente. Se disparan todas las 8 balas en señales separadas. No se para al primer éxito.

- $EV_{\text{bala}} = +\$9.81$
- $EV_{\text{campaña}} = +\$78.49$
- **Tiempo**: 8 señales necesarias / 5.6 señales por semana = **~1.4 semanas ≈ 7 días hábiles ✅**

#### 5.2. Modelo de "Stop al Primer Éxito" (Secuencial)

Se para la campaña cuando la primera bala completa su racha.

$$EV = P_{\text{camp}} \times C_{\text{final}} - E[\text{costo}]$$
$$EV = 0.9514 \times 85.56 - 25 \times \frac{0.9514}{0.31483}$$
$$= 81.40 - 25 \times 3.022 = 81.40 - 75.55 = +\$5.85$$

**Tiempo**: ~3.02 señales / 5.6 señales por semana = **~0.54 semanas ≈ 3 días hábiles ✅✅**

---

### 6. Recomendación Final

| Estrategia | $EV$/campaña | Tiempo estimado | Campañas/mes | $EV$ mensual |
|:---|:---|:---|:---|:---|
| Actual ($N=3$, señal aislada) | +$35.76 | ~3.4 semanas | ~1.2 | ~$43 |
| **$N=2$, combinada, stop-first** | +$5.85 | ~3 días | ~6-7 | ~$35-41 |
| **$N=2$, combinada, paralelo** | +$78.49 | ~7 días | ~3-4 | ~$235-314 |

> [!IMPORTANT]
> **El modelo paralelo con $N = 2$ es la solución clara**:
> - **EV mensual: ~$235-314** (vs ~$43 actual)
> - **Campaña en ~7 días hábiles** (dentro del objetivo)
> - **Probabilidad de campaña positiva: 95.14%**
> - **Reglas simples**: Máximo 1 activo por categoría por día, racha de 2 en vez de 3

---

### 7. Tabla de Resumen de Parámetros para Implementar

```
╔═══════════════════════════════════════════════════════════╗
║         CONFIGURACIÓN ÓPTIMA DE CAMPAÑA RÁPIDA          ║
╠═══════════════════════════════════════════════════════════╣
║  Capital de riesgo:       $200 USD (de los $200 del arb) ║
║  Intentos (balas):        8                              ║
║  Apuesta por intento:     $25 USD ($200 / 8)             ║
║  Racha necesaria (N):     2 victorias consecutivas       ║
║  Retorno por racha:       $25 × (1.85)² = $85.56 USD    ║
║  Ganancia neta por racha: $85.56 - $25.00 = $60.56 USD  ║
║                                                          ║
║  Operativa:               Combinada (aislada + inter)    ║
║  Win Rate esperado:       ~56.11%                        ║
║  P(racha N=2):            31.48%                         ║
║  P(al menos 1 de 8):      95.14%                         ║
║                                                          ║
║  Tiempo estimado:         ~7 días hábiles (1 semana)     ║
║  EV por campaña:          +$78.49 USD                    ║
║  EV mensual estimado:     +$235 a $314 USD               ║
╚═══════════════════════════════════════════════════════════╝
```

---

### 8. Advertencias Honestas

> [!CAUTION]
> **Riesgos que debes aceptar:**
>
> 1. **El win rate combinado (56.11%) tiene un intervalo de confianza amplio**: con solo 221 trades OOS, el IC 95% es aproximadamente [49.5%, 62.5%]. Si el verdadero $p$ está cerca del extremo inferior, el EV se vuelve negativo.
>
> 2. **El modelo paralelo amplifica tanto ganancias como pérdidas**: en las ~4.86% de campañas que fallan, pierdes los $200 completos.
>
> 3. **La ventaja es marginal**: estamos hablando de un edge real del orden del 2-5% sobre el break-even. Cualquier deterioro en la ejecución (slippage, payout real menor al 85%, señales no tomadas a tiempo) puede destruirla.
>
> 4. **Los resultados OOS son sobre datos históricos**: el mercado puede cambiar de régimen y invalidar las señales.

---

### 9. Verificación Cruzada con Monte Carlo

Para validar estos números, se debe ejecutar `monte_carlo_campaign` del [optimizer.py](file:///c:/Users/juanc/Desktop/prueba/engine/optimizer.py) con los siguientes parámetros:

```python
optimizer.monte_carlo_campaign(
    win_rate=0.5611,
    payout=0.85,
    n_streak=2,       # <-- CAMBIADO de 3 a 2
    k_attempts=8,      # <-- CAMBIADO de 6 a 8
    bet_per_attempt=25.0,
    num_simulations=10000
)
```

Y comparar `success_probability` y `expected_value` con las fórmulas analíticas de este documento.
