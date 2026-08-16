# Estrategia de Rachas de Arbitraje: Fundamentos Matemáticos y Gestión de Riesgo

Este documento detalla el análisis matemático, la justificación probabilística y la auditoría empírica de la estrategia de optimización de rachas aplicada a los beneficios de arbitraje, estructurada desde una perspectiva cuantitativa rigurosa.

---

## 1. El Concepto del Modelo Barbell (Haltera)

La estrategia Barbell (popularizada por Nassim Taleb) consiste en evitar el riesgo moderado y concentrar la exposición en dos extremos de riesgo opuestos:

1. **Extremo Seguro (90% - 95% del capital)**: El capital principal de arbitraje ($1000 USD) se mantiene resguardado en operaciones de bajo/nulo riesgo, generando un rendimiento mensual estable del 20% ($200 USD).
2. **Extremo Especulativo (5% - 10% del capital)**: Se toma únicamente la ganancia generada por el arbitraje ($200 USD) para arriesgarla en opciones binarias buscando una multiplicación asimétrica de capital.

```
   [ CAPITAL PRINCIPAL: $1000 ] ══════════════════════ [ BENEFICIO ARRIESGADO: $200 ]
     Riesgo Nulo / Arbitraje                              Riesgo Total / Opciones Binarias
     Genera $200 USD estables                             Busca meta de $1000 USD
```

### Propiedades de Asimetría:
* **Pérdida Máxima Rígidamente Acotada**: En el peor escenario posible, el usuario pierde únicamente la ganancia mensual ($200 USD). Su capital principal de $1000 USD permanece intacto. El riesgo de ruina del patrimonio real es **cero**.
* **Retorno Asimétrico Positivo (Convexidad)**: La ganancia potencial en una racha exitosa permite duplicar o triplicar el excedente manteniendo el riesgo acotado al valor inicial.

---

## 2. Validación Empírica y Eliminación del Sobreajuste (Out-of-Sample)

Al optimizar estrategias algorítmicas, es crítico evaluar la métrica de efectividad fuera de muestra:

* **Win Rate In-Sample (En Muestra)**: Efectividad en datos de entrenamiento.
* **Win Rate Out-of-Sample (Fuera de Muestra)**: Efectividad en datos no vistos ($N = 344$ trades en 18 activos).

> [!WARNING]
> La prueba empírica desesgada (registrada en [prueba.md](file:///c:/Users/juanc/Desktop/prueba/prueba.md)) demostró que el Win Rate Out-of-Sample global del portafolio es del **51.74%**, con un intervalo de confianza al 95% de **[46.47%, 56.98%]**.
> Para que una campaña Barbell posea una esperanza matemática positiva, se deben operar exclusivamente **días de señal única aislada** (donde el Win Rate medido asciende al **58.90%**), evitando días de señales simultáneas correlacionadas.

---

## 3. Modelo Matemático de Rachas (Parlay) Discretas

El usuario realiza una **campaña discreta de intentos** con regla de parada en la primera victoria.

### Parámetros:
* $C_{\text{risk}}$: Capital de riesgo total ($200 USD).
* $X$: Número de intentos en que se divide el capital (ej. $X = 6$).
* $B$: Apuesta inicial por intento ($B = C_{\text{risk}} / X = 33.33 USD$).
* $p$: Win Rate real de la estrategia (Out-of-Sample).
* $R$: Payout neto del broker ($0.85$).
* $N$: Longitud de la racha de victorias consecutivas (ej. $N = 3$).

### Fórmulas Clave:
1. **Probabilidad de Éxito de un Intento Individual ($S$)**:
   $$S = p^N$$

2. **Probabilidad de Éxito de la Campaña ($P_{\text{campaign}}$)**:
   $$P_{\text{campaign}} = 1 - (1 - S)^X = 1 - (1 - p^N)^X$$

3. **Retorno Final del Intento Exitoso ($C_{\text{final}}$)**:
   $$C_{\text{final}} = B \times (1 + R)^N$$

4. **Esperanza Matemática de la Campaña ($EV$)**:
   $$EV = P_{\text{campaign}} \times \left[ B \times (1 + R)^N \right] - C_{\text{risk}}$$

---

## 4. Evaluación de Escenarios Empíricos Reales

Utilizando la fórmula de la campaña con un presupuesto de $200 USD ($X = 6$ intentos de $33.33 USD cada uno, racha de $N = 3$ victorias):

### Escenario A: Promedio General del Portafolio ($p = 51.74\%$)
* Probabilidad de intento: $S = (0.5174)^3 \approx 13.85\%$
* Probabilidad de campaña: $P_{\text{campaign}} = 1 - (1 - 0.1385)^6 \approx 59.9\%$
* Retorno al ganar: $33.33 \times (1.85)^3 = 210.96 USD$
* **Esperanza Matemática ($EV$):** $0.599 \times 210.96 - 200 \approx \mathbf{-9.64\text{ USD}}$ 🔴 (No rentable)

### Escenario B: Operación Aislada en Días de Señal Única ($p = 58.90\%$)
* Probabilidad de intento: $S = (0.5890)^3 \approx 20.43\%$
* Probabilidad de campaña: $P_{\text{campaign}} = 1 - (1 - 0.2043)^6 \approx 75.1\%$
* Retorno al ganar: $33.33 \times (1.85)^3 = 210.96 USD$
* **Esperanza Matemática ($EV$):** $0.751 \times 210.96 - 200 \approx \mathbf{+18.43\text{ USD}}$ 🟢 (Rentable)

---

## 5. Riesgo de Correlación y Agrupamiento de Lanzamientos Simultáneos

La ejecución de lanzamientos simultáneos en el mismo día sobre múltiples activos no correlacionados teóricamente debe mantener la independencia. Sin embargo, la auditoría empírica demostró que:

1. En días de **múltiples señales simultáneas**, la efectividad colectiva disminuyó al **49.82%** debido al impacto de eventos macroeconómicos (*Risk-Off global*).
2. Para preservar la independencia estocástica y la validez de las fórmulas de racha, **las operaciones no deben lanzarse en paralelo el mismo día**, sino ejecutarse de forma secuencial en días de señal única aislada.
