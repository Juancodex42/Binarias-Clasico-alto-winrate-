# Evaluación Desesgada del Portafolio Multiactivo y Operativa Paralela Diversificada

Este documento detalla las conclusiones empíricas fuera de muestra (**70% In-Sample / 30% Out-of-Sample**) sobre el comportamiento de la operativa en paralelo, diferenciando cuantitativamente la **correlación intra-clase** (operar múltiples criptos o divisas el mismo día) de la **diversificación inter-clase** (operar 1 Cripto + 1 Forex + 1 Commodity + 1 Índice).

---

## 1. Descubrimiento Empírico Clave: Correlación Intra-Clase vs Diversificación Inter-Clase

Al analizar las 344 operaciones Out-of-Sample en los 18 activos reales, se agrupó el rendimiento según si las señales simultáneas pertenecían a la misma clase de activo o a clases independientes:

| Modalidad de Operativa Paralela | Días Evaluados | Operaciones Totales | Win Rate Out-of-Sample | Esperanza ($EV_{85}$) | Evaluación Cuantitativa |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 🔴 **Paralelo Correlacionado Intra-Clase** (ej. BTC + ETH + SOL el mismo día) | 65 días | 97 / 196 | **49.49%** | -$0.084 USD | ❌ **Destruye capital** (Arrastre por Beta/Riesgo Sistémico) |
| 🟢 **Paralelo Diversificado Inter-Clase** (1 activo por clase distinta: Cripto, Forex, Commodity, Índice) | 109 días | 81 / 148 | **54.73%** | **+$0.012 USD** | ✅ **Supera el Break-Even (54.05%)** |
| ⭐ **Señal Única Aislada en el Día** (1 sola clase activa) | 73 días | 43 / 73 | **58.90%** | **+$0.089 USD** | 🟢 **Máxima ventaja cuantitativa** |

> [!IMPORTANT]
> **El Secreto Técnico de la Diversificación:** Lanzar posiciones paralelas en activos de la misma clase (ej. varias altcoins) colapsa el rendimiento al **49.49%** porque se mueven como un solo bloque. La ventaja estadística **únicamente se sostiene** cuando las operaciones paralelas se restringen estrictamente a **clases de activos no correlacionadas** (ej. Bitcoin + Oro XAU + Divisa GBP/JPY + Índice Nasdaq).

---

## 2. Métricas de Campaña Paralela en 1 Día (Inter-Clase Diversificada)

En los 36 días Out-of-Sample donde se presentaron confluencias simultáneas en $\ge 2$ clases de activos totalmente distintas:

* **Probabilidad de lograr al menos 1 intento ganador en el mismo día:** **75.0%** ($27 / 36$ días).
* **Probabilidad de lograr 2 o más intentos ganadores en el mismo día (Multiplicación Convexa):** **30.6%** ($11 / 36$ días).

---

## 3. Reglas de Ejecución para Operativa Paralela

1. **Regla de Exclusión Intra-Clase:** NUNCA abrir dos operaciones simultáneas dentro de la misma categoría (ej. bloquear ETH o SOL si ya hay una posición abierta en BTC).
2. **Matriz de Clases Válidas para Paralelo:**
   * Clase A: Cripto Principal (*BTC / DOGE*)
   * Clase B: Forex Cross (*GBP/JPY*)
   * Clase C: Commodity (*Oro XAUUSD / Petróleo WTI*)
   * Clase D: Índice Accionario (*Nasdaq 100*)
3. **Límite por Jornada:** Máximo 1 posición por clase de activo por día.
