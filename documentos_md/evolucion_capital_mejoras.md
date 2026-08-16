# Evolución del Capital, Mejora del Winrate, y El Problema Original Disuelto

---

## 1. El Problema Original Ya No Existe

Tu problema era:

> *"No logro completar las campañas en menos de una semana"*

Ese problema existía porque estabas intentando hacer una campaña COMPLEJA:
- 6 balas de $33.33
- Cada bala necesita 3 aciertos seguidos
- Necesitas señales rápido para gastar las 6 balas
- Con ~2.8 señales/semana → tardabas 3+ semanas

**La nueva perspectiva lo elimina por completo:**

```
ANTES (complejo, lento):                 AHORA (simple, rápido):
                                         
  $200 ÷ 6 balas = $33.33 c/u           $200 → 1 sola bala
  Necesitas: 6 × 3 = 18 señales max     Necesitas: 3 señales max
  Tiempo: 2-3 semanas                   Tiempo: 3-7 días
  Probabilidad: 75% de "completar"      Probabilidad: 20% de GANAR
  pero EV frágil                         pero EV robusto a largo plazo
```

### ¿Por qué funciona mejor?

| Aspecto | Campaña de 6 balas (antes) | 1 bala mensual (ahora) |
|:---|:---|:---|
| Señales necesarias | Hasta 18 | Solo 3 |
| Tiempo de ejecución | 2-3 semanas | 1-7 días |
| Presión psicológica | Alta (muchas decisiones) | Baja (solo 3 operaciones) |
| Si pierdes | Gastaste parte del presupuesto, ¿seguir? | Se acabó el mes. Claro y limpio. |
| Ganancia por éxito | $211 (modesta) | **$1,266** (explosiva) |
| Frecuencia de juego | 1 vez cada 3 semanas | 1 vez por mes |

> [!IMPORTANT]
> **El problema de "campaña lenta" se disuelve porque ya no necesitas una campaña larga.** Solo necesitas 3 señales aisladas en un mes. Con ~11 señales disponibles por mes, encontrar 3 es trivial. La campaña se ejecuta en **3 a 7 días**, y si falla, paras y esperas al mes siguiente.

---

## 2. Evolución del Capital: Mes a Mes

Tu capital crece como una **escalera**: se mantiene plano durante los meses que pierdes, y da un salto grande cada vez que una racha se completa.

### Mecánica del Salto

Cuando ganas la racha de 3, tu base se multiplica:

$$\text{Multiplicador por hit} = 1 + 0.20 \times (1.85)^3 = 1 + 0.20 \times 6.3316 = 1 + 1.2663 = \mathbf{2.2663}$$

Es decir: **cada hit multiplica tu base por 2.27x**.

### Tabla de Capital Según Número de Hits en 12 Meses

El número de hits en 12 meses sigue una distribución Binomial(12, 0.2043):

| Hits en el año | Capital final | Probabilidad exacta | Probabilidad acumulada (≥) |
|:---|:---|:---|:---|
| **0 hits** | $1,000 (sin cambio) | 6.7% | 100% |
| **1 hit** | $2,266 | 20.7% | 93.3% |
| **2 hits** | $5,136 | 29.2% | 72.7% |
| **3 hits** | $11,639 | 25.0% | 43.5% |
| **4 hits** | $26,374 | 14.4% | 18.5% |
| **5 hits** | $59,769 | 5.9% | 4.1% |
| **6+ hits** | $135,000+ | ~2% | ~2% |

### ¿Qué Significa Esto?

```
    Capital ($)
    │
60k ┤                                                    ★ 5 hits (5.9%)
    │
    │
26k ┤                                          ★ 4 hits (14.4%)
    │
    │
12k ┤                                ★ 3 hits (25.0%)
    │
 5k ┤                     ★ 2 hits (29.2%)     ← RESULTADO MÁS PROBABLE
    │
 2k ┤          ★ 1 hit (20.7%)
 1k ┤ ★ 0 hits (6.7%)
    └────────────────────────────────────────────────────
         Peor caso       Mediana         Mejor caso
```

> [!NOTE]
> **El resultado más probable (moda) es 2 hits**: tu capital pasa de $1,000 a ~$5,136 en 12 meses. Eso es un **5.1x** sobre tu patrimonio inicial.
>
> **La mediana** está entre 2 y 3 hits: ~$5,000 a $12,000.
>
> **El peor caso** (6.7%): tu capital no creció pero tampoco bajó. Perdiste $2,400 de ganancias de arbitraje.

### Trayectoria Visual Típica (2 hits en 12 meses)

```
Capital
$5,136 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
        │                                               │
        │                           HIT #2              │
$2,266 ─│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ↑─ ─ ─ ─ ─ ─ ─ ─│─
        │                           │                   │
        │              HIT #1       │                   │
$1,000 ─│──────────────↑────────────│───────────────────│─
        │  ╳  ╳  ╳     │  ╳  ╳  ╳  │  ╳                │
        └──1──2──3──4──5──6──7──8──9──10─11─12──────────
                    Meses (╳ = pérdida, ↑ = hit)
```

---

## 3. El Impacto BRUTAL de Mejorar el Winrate

Aquí es donde todo se conecta. Cada punto porcentual que subas el winrate tiene un efecto **desproporcionadamente grande** sobre tu capital, porque se amplifica tres veces:

1. **Se eleva al cubo** (racha de 3): $p → p^3$
2. **Se repite 12 veces** (intentos anuales)
3. **Se compone** (cada hit agranda la base del siguiente)

### Tabla: Impacto de Cada Mejora en el Winrate

| Win Rate | P(racha de 3) | Hits esperados/año | EV mensual | **Capital esperado 12 meses** |
|:---|:---|:---|:---|:---|
| 55.0% | 16.6% | 2.0 | +$10.66 | ~$3,600 |
| **58.9% (actual)** | **20.4%** | **2.5** | **+$58.64** | **~$5,100 - $11,600** |
| 62.0% | 23.8% | 2.9 | +$101.69 | ~$11,600 - $26,000 |
| 65.0% | 27.5% | 3.3 | +$147.63 | ~$11,600 - $26,000 |
| 70.0% | 34.3% | 4.1 | +$234.24 | ~$26,000 - $60,000 |
| 75.0% | 42.2% | 5.1 | +$340.70 | ~$60,000 - $135,000 |

### Visualización: EV Mensual vs. Win Rate

```
EV/mes ($)
  │
340│                                              ●  75%
  │
  │
234│                                    ●  70%
  │
148│                          ●  65%
  │
102│                 ●  62%
  │
 59│        ●  58.9% (TÚ ESTÁS AQUÍ)
  │
 11│  ●  55%
  0├───────────────────────────────────────────────
     55%    59%    62%    65%    70%    75%
                  Win Rate
```

> [!IMPORTANT]
> **Subir tu winrate del 59% al 65% casi TRIPLICA tu EV mensual** ($59 → $148). Y triplica la probabilidad de alcanzar 4+ hits anuales (del 18.5% al ~45%).
>
> Cada punto porcentual adicional de winrate vale aproximadamente **+$25-30/mes** en EV, o **+$300-360/año**.

> [!NOTE]
> **Cómo usar esta tabla:** Los valores de la tabla son una **herramienta de sensibilidad** — muestran cuánto importa conceptualmente cada punto de WR en la estructura del sistema. El Win Rate real de cualquier estrategia activa lo calcula y muestra el motor cuantitativo de la app en tiempo real. Los números de la tabla no pretenden predecir lo que mostrará el UI: son el mapa que explica *por qué* mejorar el WR importa tanto.

---

## 4. ¿Cómo Mejorar el Winrate? (Con lo que tenemos)

El codebase ya tiene pistas. Los datos OOS muestran diferentes winrates según las condiciones:

### 4.1. Lo Que Ya Sabemos (del codebase)

| Condición | Win Rate OOS | Trades | ¿Usable? |
|:---|:---|:---|:---|
| Señal única aislada | **58.90%** | 73 | ✅ Base actual |
| Inter-clase diversificada (≥2 clases) | 54.73% | 148 | ⚠️ Solo para acelerar |
| Intra-clase correlacionada | 49.49% | 196 | ❌ Nunca usar |
| Promedio general | 51.74% | 344 | ❌ |

### 4.2. Caminos Concretos para Subir el Winrate

#### Camino A: Filtrar por Régimen de Mercado

Tu [statistics.py](file:///c:/Users/juanc/Desktop/prueba/engine/statistics.py) ya mide el winrate en mercados tendenciales vs. laterales (líneas 146-188). Si el winrate en mercados tendenciales es significativamente mayor, podrías añadir un filtro de régimen más estricto.

**Hipótesis**: En mercados con movimiento claro de la EMA semanal (>0.5% en 4 semanas en vez del 0.2% actual en [daily_confluence.py](file:///c:/Users/juanc/Desktop/prueba/strategies/daily_confluence.py#L112)), el winrate debería ser mayor porque la tendencia semanal tiene más convicción.

#### Camino B: Filtrar por Día de la Semana

El módulo de estadísticas también descompone resultados por día ([statistics.py línea 129](file:///c:/Users/juanc/Desktop/prueba/engine/statistics.py#L129)). Si ciertos días tienen winrate significativamente mayor (por ejemplo, martes y miércoles suelen tener más continuación de tendencia), podrías restringir operaciones a esos días.

#### Camino C: Subir Tolerancia del Pullback

Actualmente `pullback_tolerance = 0.015` (1.5%). Un pullback más ajustado (ej. 0.8%) daría menos señales pero potencialmente de mayor calidad, ya que el precio está más cerca del soporte dinámico.

#### Camino D: Más Datos y Más Activos

Con solo 73 trades OOS para señales aisladas, el intervalo de confianza es amplio (~47% a 70%). Más datos históricos o más activos descorrelacionados reducirían la incertidumbre sobre el verdadero winrate.

> [!WARNING]
> **Trampa crítica**: Cualquier filtro adicional que pruebes en los datos existentes puede crear **sobreajuste**. Si pruebas 10 filtros y te quedas con el que da mejor resultado, estás haciendo cherry-picking.
>
> **Regla**: Solo implementar filtros que tengan **justificación teórica** (ej. "los mercados laterales producen señales falsas de tendencia" tiene lógica) y luego validarlos en datos **nuevos** (no los mismos 344 trades).

---

## 5. El Nuevo Mapa Completo

```
 ┌──────────────────────────────────────────────────────────────────────┐
 │                     TU SISTEMA COMPLETO                             │
 │                                                                      │
 │  ┌─────────────────────┐     ┌─────────────────────────────────┐    │
 │  │  MOTOR DE INGRESOS  │     │  MULTIPLICADOR DE CAPITAL       │    │
 │  │  (Arbitraje)        │────▶│  (Binarias - Parlay mensual)    │    │
 │  │                     │     │                                  │    │
 │  │  $1,000 base        │     │  Riesgo: $200/mes (el profit)   │    │
 │  │  20% mensual        │     │  Estructura: 1 bala, racha 3    │    │
 │  │  Riesgo: ~0         │     │  P(éxito): ~20%                 │    │
 │  │  Genera: $200/mes   │     │  Payoff: $1,266 (6.3x)          │    │
 │  └─────────────────────┘     └──────────────┬──────────────────┘    │
 │          ▲                                   │                       │
 │          │              ┌────────────────────┘                       │
 │          │              ▼                                            │
 │          │    ┌───────────────────┐                                  │
 │          │    │  COMPOUNDING      │                                  │
 │          └────│                   │                                  │
 │               │  Hit → +$1,066   │                                  │
 │               │  al arbitraje    │                                  │
 │               │  Base crece      │                                  │
 │               │  Bala crece      │                                  │
 │               │  Todo se acelera │                                  │
 │               └───────────────────┘                                  │
 │                                                                      │
 │  PALANCA DE MEJORA:                                                  │
 │  ┌────────────────────────────────────────────────────────┐         │
 │  │  Subir winrate del 59% al 65%                          │         │
 │  │  → P(racha) sube de 20.4% a 27.5%                     │         │
 │  │  → EV mensual sube de $59 a $148 (+150%)               │         │
 │  │  → Capital anual esperado sube de ~$5K a ~$15K (+200%) │         │
 │  └────────────────────────────────────────────────────────┘         │
 │                                                                      │
 └──────────────────────────────────────────────────────────────────────┘
```

---

## 6. Respuesta Final a Tu Pregunta

> *"¿Cómo afecta la nueva perspectiva al problema original?"*

### Antes (perspectiva vieja):
- **Problema**: La campaña tarda mucho → necesito más señales → bajo la calidad → pierdo dinero
- **Trampa**: Velocidad vs. Calidad = conflicto sin solución

### Ahora (perspectiva nueva):
- **No hay problema de velocidad**: Solo necesitas 3 señales al mes (tienes ~11)
- **Máxima calidad**: Usas solo señales aisladas (58.90%)
- **Si pierdes rápido, mejor**: Fallo en paso 1 = 1 día gastado, esperas al mes siguiente
- **El dinero viene del SISTEMA REPETIDO**, no de una campaña individual

### El Trabajo Real Ahora Es:
1. ✅ ~~Resolver velocidad de campaña~~ → **RESUELTO** (3 señales, 3-7 días)
2. 🔄 **Mejorar el winrate** → Cada +1% = +$25-30/mes de EV → esto es donde invertir esfuerzo
3. 🔄 **Validar con más datos** → Más activos, más historia, intervalos de confianza más estrechos
4. ✅ **Ejecutar con disciplina** → 1 intento/mes, solo señales aisladas, stop si pierdes

> [!IMPORTANT]
> **El problema original se disolvió.** No necesitabas una campaña más rápida. Necesitabas una campaña **más simple**. Y ahora tu único trabajo real es subir el winrate del 59% al 65%+. Eso es pura investigación de señales, no un problema de velocidad.
