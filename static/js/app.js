// app.js - BinSim Frontend (conectado a API real)

const API = '/api';

function generatePineScriptV5(strat) {
    const bg = strat.best_genome || strat.params || {};
    const name = strat.name ? strat.name.replace(/[^a-zA-Z0-9\s]/g, '').trim() : 'Estrategia BinSim';
    
    const isDailyConfluence = (strat.type === 'daily_confluence') || (strat.name && strat.name.includes('Confluencia')) || bg.pullback_tolerance !== undefined;

    if (isDailyConfluence) {
        const pullbackTol = (bg.pullback_tolerance || 0.015).toFixed(3);
        const rsiMinCall = (bg.rsi_min_call || 25.0).toFixed(1);
        const rsiMaxCall = (bg.rsi_max_call || 55.0).toFixed(1);
        const wickRatio = (bg.pinbar_wick_ratio || bg.wick_rejection_ratio || 0.35).toFixed(2);
        const emaWPeriod = bg.ema_weekly_period || 50;
        const emaDPeriod = bg.ema_daily_period || 20;

        return `//@version=5
indicator("BinSim - Confluencia Diaria Multi-Activo (CALL)", overlay=true)

// --- INPUTS DE CONFIGURACIÓN ---
ema_w_period  = input.int(${emaWPeriod}, "Periodo EMA Semanal")
ema_d_period  = input.int(${emaDPeriod}, "Periodo EMA Diaria")
rsi_period    = input.int(14, "Periodo RSI")
pullback_tol  = input.float(${pullbackTol}, "Tolerancia Pullback EMA (0.015 = 1.5%)")
rsi_min_call  = input.float(${rsiMinCall}, "RSI Mínimo CALL")
rsi_max_call  = input.float(${rsiMaxCall}, "RSI Máximo CALL")
wick_ratio    = input.float(${wickRatio}, "Ratio Mínimo Rechazo Mecha (Pinbar)")
exclude_wknd  = input.bool(true, "Excluir Fines de Semana (Sáb/Dom)")

// --- INDICADORES SEMANALES Y DIARIOS SIN LOOK-AHEAD ---
ema_weekly      = request.security(syminfo.tickerid, "W", ta.ema(close, ema_w_period), barmerge.gaps_off, barmerge.lookahead_off)
close_weekly    = request.security(syminfo.tickerid, "W", close, barmerge.gaps_off, barmerge.lookahead_off)
ema_weekly_dir  = ta.change(ema_weekly)
weekly_bull     = close_weekly > ema_weekly and ema_weekly_dir > 0

ema_daily       = ta.ema(close, ema_d_period)
rsi_daily       = ta.rsi(close, rsi_period)

// --- RECHAZO DE MECHA Y PULLBACK ---
candle_range    = high - low
lower_wick      = math.min(open, close) - low
wick_call       = candle_range > 0 and (lower_wick / candle_range) >= wick_ratio

pullback_call   = (low <= ema_daily * (1 + pullback_tol)) and (close >= ema_daily * (1 - pullback_tol))
rsi_call        = rsi_daily >= rsi_min_call and rsi_daily <= rsi_max_call
valid_day       = not exclude_wknd or (dayofweek != dayofweek.saturday and dayofweek != dayofweek.sunday)

// --- CONDICIÓN DE SEÑAL CALL (COMPRA) ---
call_signal     = weekly_bull and pullback_call and rsi_call and wick_call and valid_day

// --- VISUALIZACIÓN ---
plot(ema_daily, title="EMA 20 Diaria", color=color.orange, linewidth=2)
plot(ema_weekly, title="EMA 50 Semanal", color=color.purple, linewidth=3)
plotshape(call_signal, title="Señal CALL Confluencia", style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, text="CALL")

// --- ALERTAS NATIVAS DE TRADINGVIEW ---
alertcondition(call_signal, title="Alerta CALL Confluencia BinSim", message="⚡ Señal CALL Confluencia Diaria: Entrada a 2 Velas")`;
    }

    const rsiP = bg.rsi_period || 14;
    const rsiOversold = bg.rsi_oversold || 30.0;
    const rsiOverbought = bg.rsi_overbought || 70.0;
    const rsiEnabled = bg.rsi_enabled !== false;

    const bbP = bg.bb_period || 20;
    const bbStd = bg.bb_std || 2.0;
    const bbEnabled = bg.bb_enabled !== false;

    const emaFastP = bg.ema_fast_period || 9;
    const emaSlowP = bg.ema_slow_period || 21;
    const emaEnabled = bg.ema_enabled === true;

    const rejectionEnabled = bg.rejection_filter_enabled === true;
    const volatilityEnabled = bg.volatility_filter_enabled === true;

    return `//@version=5
indicator("BinSim - ${name}", overlay=true)

// --- INPUTS DE CONFIGURACIÓN ---
use_rsi       = input.bool(${rsiEnabled}, "Activar Filtro RSI")
rsi_period    = input.int(${rsiP}, "Periodo RSI")
rsi_oversold  = input.float(${rsiOversold.toFixed(1)}, "RSI Sobreventa (CALL)")
rsi_overbought= input.float(${rsiOverbought.toFixed(1)}, "RSI Sobrecompra (PUT)")

use_bb        = input.bool(${bbEnabled}, "Activar Bandas Bollinger")
bb_period     = input.int(${bbP}, "Periodo Bollinger")
bb_std        = input.float(${bbStd.toFixed(1)}, "Desviación Estándar BB")

use_ema       = input.bool(${emaEnabled}, "Activar Filtro Tendencia EMA")
ema_fast_p    = input.int(${emaFastP}, "EMA Rápida")
ema_slow_p    = input.int(${emaSlowP}, "EMA Lenta")

use_pinbar    = input.bool(${rejectionEnabled}, "Filtro Rechazo Mecha (Pinbar)")
use_squeeze   = input.bool(${volatilityEnabled}, "Filtro Squeeze Volatilidad")

// --- CÁLCULO DE INDICADORES ---
rsi_val       = ta.rsi(close, rsi_period)
[bb_mid, bb_upper, bb_lower] = ta.bb(close, bb_period, bb_std)
ema_fast_val  = ta.ema(close, ema_fast_p)
ema_slow_val  = ta.ema(close, ema_slow_p)

// Cálculo de Mecha Rechazo (Pinbar)
candle_range  = high - low
upper_wick    = high - math.max(open, close)
lower_wick    = math.min(open, close) - low
pinbar_bull   = candle_range > 0 and (lower_wick / candle_range) >= 0.55
pinbar_bear   = candle_range > 0 and (upper_wick / candle_range) >= 0.55

// Cálculo Squeeze Volatilidad (Compresión de Bandas)
bb_width      = (bb_upper - bb_lower) / bb_mid
squeeze_active= bb_width < 0.006

// --- CONDICIONES DE ENTRADA (EXPIRACIÓN 2 VELAS) ---
cond_rsi_call = not use_rsi or (rsi_val <= rsi_oversold)
cond_rsi_put  = not use_rsi or (rsi_val >= rsi_overbought)

cond_bb_call  = not use_bb or (low <= bb_lower or close <= bb_lower)
cond_bb_put   = not use_bb or (high >= bb_upper or close >= bb_upper)

cond_ema_call = not use_ema or (ema_fast_val > ema_slow_val and close > ema_slow_val)
cond_ema_put  = not use_ema or (ema_fast_val < ema_slow_val and close < ema_slow_val)

cond_pin_call = not use_pinbar or pinbar_bull
cond_pin_put  = not use_pinbar or pinbar_bear

cond_sqz_call = not use_squeeze or (not squeeze_active and squeeze_active[1] and close > open)
cond_sqz_put  = not use_squeeze or (not squeeze_active and squeeze_active[1] and close < open)

call_signal   = cond_rsi_call and cond_bb_call and cond_ema_call and cond_pin_call and cond_sqz_call
put_signal    = cond_rsi_put  and cond_bb_put  and cond_ema_put  and cond_pin_put  and cond_sqz_put

// --- VISUALIZACIÓN ---
plotshape(call_signal, title="Señal CALL (Compra)", style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, text="CALL")
plotshape(put_signal, title="Señal PUT (Venta)", style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, text="PUT")

plot(use_ema ? ema_fast_val : na, title="EMA Rápida", color=color.blue)
plot(use_ema ? ema_slow_val : na, title="EMA Lenta", color=color.orange)

// --- ALERTAS NATIVAS ---
alertcondition(call_signal, title="Alerta CALL BinSim", message="⚡ Señal CALL BinSim: Entrada a 2 Velas")
alertcondition(put_signal, title="Alerta PUT BinSim", message="⚡ Señal PUT BinSim: Entrada a 2 Velas")`;
}

function generateAIPrompt(strat) {
    const bg = strat.best_genome || strat.params || {};
    const name = strat.name || 'Estrategia BinSim';
    const isDailyConfluence = (strat.type === 'daily_confluence') || (strat.name && strat.name.includes('Confluencia')) || bg.pullback_tolerance !== undefined;

    if (isDailyConfluence) {
        return `Actúa como un Desarrollador Experto en Pine Script (TradingView v5) y Opciones Binarias.
Genera el código ejecutable completo para la Estrategia de Confluencia Diaria Multi-Activo (CALL):

NOMBRE ESTRATEGIA: ${name}
DESCRIPCIÓN OPERATIVA EXACTA:
${strat.natural_description || 'Estrategia de confluencia técnica basada en tendencia semanal, EMA 20 diaria, RSI y rechazo mecha Pinbar.'}

REGLAS DE SEÑAL CALL (Expiración 2 Velas):
1. Tendencia Semanal Alcista: Precio semanal > EMA 50 Semanal y pendiente de la EMA 50 Semanal positiva (request.security sin lookahead).
2. Pullback a la EMA 20 Diaria: Mínimo diario prueba la zona de la EMA 20 Diaria (+/- 1.5%).
3. RSI Diario: En rango relativo [25.0 - 55.0].
4. Filtro de Mecha Inferior (Pinbar): Mecha inferior representa >= 35% del tamaño total de la vela diaria.
5. Exclusión de Fines de Semana: Solamente operar de Lunes a Viernes.

ENTREGABLES:
1. Código Pine Script v5 limpio con indicator("...", overlay=true).
2. Variables input.int e input.float configurables.
3. Señales plotshape con triángulos verdes (CALL) y alertcondition para automatización de alertas en TradingView.`;
    }

    const rsiP = bg.rsi_period || 14;
    const rsiOversold = bg.rsi_oversold || 30.0;
    const rsiOverbought = bg.rsi_overbought || 70.0;
    const bbP = bg.bb_period || 20;
    const bbStd = bg.bb_std || 2.0;
    const emaFastP = bg.ema_fast_period || 9;
    const emaSlowP = bg.ema_slow_period || 21;

    return `Actúa como un Desarrollador Experto en Pine Script (TradingView v5) y Opciones Binarias.
Genera el código ejecutable completo para el siguiente indicador cuantitativo:

NOMBRE ESTRATEGIA: ${name}
DESCRIPCIÓN OPERATIVA EXACTA:
${strat.natural_description || 'Estrategia optimizada mediante algoritmos genéticos.'}

CONFIGURACIÓN DE PARÁMETROS:
1. RSI: Periodo=${rsiP}, Sobreventa CALL=${rsiOversold}, Sobrecompra PUT=${rsiOverbought} (${bg.rsi_enabled !== false ? 'Activo' : 'Inactivo'})
2. Bandas de Bollinger: Periodo=${bbP}, Desviación=${bbStd}σ (${bg.bb_enabled !== false ? 'Activo' : 'Inactivo'})
3. EMA Tendencial: EMA Rápida=${emaFastP}, EMA Lenta=${emaSlowP} (${bg.ema_enabled ? 'Activo' : 'Inactivo'})
4. Filtro Mecha Pinbar: ${bg.rejection_filter_enabled ? 'Activo (Mecha >= 55% del tamaño de vela)' : 'Inactivo'}
5. Volatilidad Squeeze: ${bg.volatility_filter_enabled ? 'Activo (Expansión tras compresión)' : 'Inactivo'}

REGLAS DE SEÑAL:
- Entrada CALL (Operación al alza, expiración 2 velas):
  * Precio en o por debajo de la Banda BB Inferior.
  * RSI <= ${rsiOversold}.
  ${bg.ema_enabled ? `* EMA Rápida (${emaFastP}) > EMA Lenta (${emaSlowP}) y Cierre > EMA Lenta.` : ''}
  ${bg.rejection_filter_enabled ? '* Mecha de rechazo inferior prominente.' : ''}

- Entrada PUT (Operación a la baja, expiración 2 velas):
  * Precio en o por encima de la Banda BB Superior.
  * RSI >= ${rsiOverbought}.
  ${bg.ema_enabled ? `* EMA Rápida (${emaFastP}) < EMA Lenta (${emaSlowP}) y Cierre < EMA Lenta.` : ''}
  ${bg.rejection_filter_enabled ? '* Mecha de rechazo superior prominente.' : ''}

ENTREGABLES:
1. Código Pine Script v5 limpio con indicator("...", overlay=true).
2. Opciones input.bool e input.int en la interfaz de TradingView.
3. Señales plotshape con triángulos verdes (CALL) y rojos (PUT) y alertcondition.`;
}

function showToast(message, type = 'info', duration = 3000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; pointer-events: none;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-message toast-${type}`;
    
    let borderColor = 'rgba(56, 189, 248, 0.35)';
    if (type === 'success') {
        borderColor = 'rgba(16, 185, 129, 0.4)';
    } else if (type === 'error') {
        borderColor = 'rgba(244, 63, 94, 0.4)';
    }

    toast.style.cssText = `
        background: #141d2e;
        color: #f0f6fc;
        border: 1px solid ${borderColor};
        border-radius: 6px;
        padding: 10px 16px;
        font-size: 0.82rem;
        font-family: 'Inter', system-ui, sans-serif;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        gap: 8px;
        opacity: 0;
        transform: translateY(10px);
        transition: opacity 180ms cubic-bezier(0.16, 1, 0.3, 1), transform 180ms cubic-bezier(0.16, 1, 0.3, 1);
        pointer-events: auto;
    `;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => {
            if (toast.parentElement) toast.parentElement.removeChild(toast);
        }, 200);
    }, duration);
}
window.showToast = showToast;

window.togglePineScriptModal = function(id) {
    const el = document.getElementById(`pinescript-box-${id}`);
    if (el) {
        el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }
};

window.copyPineScript = function(id) {
    const txt = document.getElementById(`pinescript-code-${id}`);
    if (txt) {
        navigator.clipboard.writeText(txt.value);
        showToast('✅ Código Pine Script (v5) copiado al portapapeles.', 'success');
    }
};

window.copyAIPrompt = function(id) {
    const txt = document.getElementById(`ai-prompt-${id}`);
    if (txt) {
        navigator.clipboard.writeText(txt.value);
        showToast('✅ Prompt estructurado para IA copiado al portapapeles.', 'success');
    }
};

const state = {
    currentTab: 'dashboard',
    candles: [],
    strategies: [],
    backtestResults: null,
    optimizerResults: null,
    selectedStrategy: null,
    lastWinRate: 0.5,
    currentBacktestData: null,
    loadedBacktestId: null
};

let mainChart, candleSeries;
let smartChart, smartCandleSeries;

let liveWs = null;
let livePollTimer = null;

function stopLiveStream() {
    if (liveWs) {
        try {
            liveWs.onclose = null;
            liveWs.close();
        } catch (e) {}
        liveWs = null;
    }
    if (livePollTimer) {
        clearInterval(livePollTimer);
        livePollTimer = null;
    }
    updateLiveBadge(false);
}

function updateLiveBadge(active, text = 'En Vivo') {
    const badge = document.getElementById('live-badge');
    const badgeText = document.getElementById('live-badge-text');
    if (!badge) return;
    if (active) {
        badge.style.display = 'inline-flex';
        if (badgeText) badgeText.textContent = text;
    } else {
        badge.style.display = 'none';
    }
}

function updateLiveCandleInChart(updatedCandle) {
    if (!updatedCandle || isNaN(updatedCandle.time) || isNaN(updatedCandle.close)) return;

    if (state.candles && state.candles.length > 0) {
        const lastCandle = state.candles[state.candles.length - 1];
        if (updatedCandle.time >= lastCandle.time) {
            const prevClose = state.candles.length > 1 ? state.candles[state.candles.length - 2].close : updatedCandle.open;
            let isBearish = false;
            if (updatedCandle.close < updatedCandle.open) {
                isBearish = true;
            } else if (updatedCandle.close === updatedCandle.open && updatedCandle.close < prevClose) {
                isBearish = true;
            }

            const barColor = isBearish ? '#f43f5e' : (updatedCandle.close > updatedCandle.open || updatedCandle.close > prevClose ? '#10b981' : '#94a3b8');
            const candleWithColor = {
                ...updatedCandle,
                color: barColor,
                wickColor: barColor,
                borderColor: barColor
            };

            if (updatedCandle.time === lastCandle.time) {
                state.candles[state.candles.length - 1] = candleWithColor;
            } else {
                state.candles.push(candleWithColor);
            }

            try {
                if (candleSeries) candleSeries.update(candleWithColor);
                if (smartCandleSeries) smartCandleSeries.update(candleWithColor);
            } catch (err) {
                console.warn('[Chart] Error actualizando vela en vivo:', err);
            }
            const displayPrice = updatedCandle.close < 1 ? updatedCandle.close.toFixed(5) : updatedCandle.close.toFixed(2);
            updateLiveBadge(true, `En Vivo: $${displayPrice}`);
        }
    }
}

function connectLiveStream(pair, interval) {
    stopLiveStream();

    const source = document.getElementById('source-selector')?.value;
    if (source !== 'live') return;

    const streamPair = pair.toLowerCase();
    const wsUrl = `wss://stream.binance.com:9443/ws/${streamPair}@kline_${interval}`;
    
    updateLiveBadge(true, 'Conectando...');

    try {
        liveWs = new WebSocket(wsUrl);

        liveWs.onopen = () => {
            console.log(`[Binance WS] Conectado a ${streamPair}@kline_${interval}`);
            updateLiveBadge(true, 'En Vivo (Binance WS)');
        };

        liveWs.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.e === 'kline' && msg.k) {
                    const k = msg.k;
                    const candleTime = Math.floor(k.t / 1000);
                    const updatedCandle = {
                        time: candleTime,
                        open: parseFloat(k.o),
                        high: parseFloat(k.h),
                        low: parseFloat(k.l),
                        close: parseFloat(k.c),
                        volume: parseFloat(k.v)
                    };
                    updateLiveCandleInChart(updatedCandle);
                }
            } catch (err) {
                console.error('[Binance WS] Error procesando mensaje:', err);
            }
        };

        liveWs.onerror = (err) => {
            console.warn('[Binance WS] Error en WebSocket, usando polling:', err);
            startFallbackPolling(pair, interval);
        };

        liveWs.onclose = (evt) => {
            const currentSource = document.getElementById('source-selector')?.value;
            if (currentSource === 'live') {
                startFallbackPolling(pair, interval);
            } else {
                updateLiveBadge(false);
            }
        };
    } catch (e) {
        console.error('[Binance WS] Error al instanciar WebSocket:', e);
        startFallbackPolling(pair, interval);
    }
}

function startFallbackPolling(pair, interval) {
    if (livePollTimer) clearInterval(livePollTimer);
    updateLiveBadge(true, 'En Vivo (Polling)');

    livePollTimer = setInterval(async () => {
        const source = document.getElementById('source-selector')?.value;
        if (source !== 'live') {
            clearInterval(livePollTimer);
            livePollTimer = null;
            updateLiveBadge(false);
            return;
        }

        try {
            const res = await fetch(`https://api.binance.com/api/v3/klines?symbol=${pair}&interval=${interval}&limit=2`);
            if (!res.ok) return;
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                const latest = data[data.length - 1];
                const updatedCandle = {
                    time: Math.floor(latest[0] / 1000),
                    open: parseFloat(latest[1]),
                    high: parseFloat(latest[2]),
                    low: parseFloat(latest[3]),
                    close: parseFloat(latest[4]),
                    volume: parseFloat(latest[5])
                };
                updateLiveCandleInChart(updatedCandle);
            }
        } catch (e) {
            console.error('Error polling Binance live klines:', e);
        }
    }, 3000);
}

function buildChartMarkers(signals) {
    if (!signals || signals.length === 0) return [];
    
    const sorted = [...signals].sort((a, b) => a.time - b.time);
    const markers = [];
    const seenKeys = new Set();
    
    sorted.forEach(s => {
        const key = `${s.time}_${s.direction}_${s.result || ''}`;
        if (seenKeys.has(key)) return;
        seenKeys.add(key);
        
        const priceStr = s.entry_price ? ` @ ${formatPrice(s.entry_price)}` : '';
        const exitPriceStr = s.exit_price ? ` @ ${formatPrice(s.exit_price)}` : '';
        const pnlStr = (s.pnl !== undefined && s.pnl !== null) ? ` (${s.pnl >= 0 ? '+' : ''}${s.pnl.toFixed(2)}$)` : '';

        if (s.direction === 'CALL') {
            markers.push({
                time: s.time,
                position: 'belowBar',
                color: '#10b981',
                shape: 'arrowUp',
                text: `CALL${priceStr}`
            });
        } else if (s.direction === 'PUT') {
            markers.push({
                time: s.time,
                position: 'aboveBar',
                color: '#f43f5e',
                shape: 'arrowDown',
                text: `PUT${priceStr}`
            });
        } else if (s.direction === 'EXIT') {
            const isWin = s.result === 'WIN';
            const tradeDir = s.trade_direction || 'CALL';
            
            // Posicionamiento dinámico: WIN en la dirección favorable, LOSS en la desfavorable
            let exitPos = 'aboveBar';
            if (tradeDir === 'CALL') {
                exitPos = isWin ? 'aboveBar' : 'belowBar';
            } else {
                exitPos = isWin ? 'belowBar' : 'aboveBar';
            }
            
            markers.push({
                time: s.time,
                position: exitPos,
                color: isWin ? '#10b981' : '#f43f5e',
                shape: 'circle',
                text: isWin ? `WIN${exitPriceStr}${pnlStr}` : `LOSS${exitPriceStr}${pnlStr}`
            });
        }
    });
    
    return markers;
}


document.addEventListener('DOMContentLoaded', () => initApp());

async function initApp() {
    // Mode Switch listeners
    const btnSmart = document.getElementById('mode-smart');
    const btnAdvanced = document.getElementById('mode-advanced');
    if (btnSmart && btnAdvanced) {
        btnSmart.addEventListener('click', () => {
            btnSmart.classList.add('active');
            btnAdvanced.classList.remove('active');
            document.querySelector('.tabs-nav').style.display = 'none';
            switchTab('smart-dashboard');
        });
        btnAdvanced.addEventListener('click', () => {
            btnAdvanced.classList.add('active');
            btnSmart.classList.remove('active');
            document.querySelector('.tabs-nav').style.display = 'flex';
            switchTab('dashboard'); // Default advanced tab
        });
    }

    // Tab listeners
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!e.target.disabled) switchTab(e.target.dataset.tab);
        });
    });

    // Init TradingView chart (Advanced)
    const chartObj = createCandlestickChart('tv-chart');
    mainChart = chartObj.chart;
    candleSeries = chartObj.candleSeries;

    new ResizeObserver(entries => {
        if (entries.length === 0) return;
        const r = entries[0].contentRect;
        if (mainChart) mainChart.applyOptions({ height: r.height, width: r.width });
    }).observe(document.getElementById('tv-chart'));

    // Init TradingView chart (Smart)
    const smartChartObj = createCandlestickChart('smart-tv-chart');
    smartChart = smartChartObj.chart;
    smartCandleSeries = smartChartObj.candleSeries;

    new ResizeObserver(entries => {
        if (entries.length === 0) return;
        const r = entries[0].contentRect;
        if (smartChart) smartChart.applyOptions({ height: r.height, width: r.width });
    }).observe(document.getElementById('smart-tv-chart'));

    // Observe Correlation Canvas container for High-DPI responsive redraw
    const smartCorrCanvas = document.getElementById('smart-correlation-canvas');
    if (smartCorrCanvas && smartCorrCanvas.parentElement) {
        new ResizeObserver(entries => {
            if (entries.length === 0) return;
            if (smartCorrCanvas._lastMatrix && smartCorrCanvas._lastLabels) {
                createCorrelationHeatmap('smart-correlation-canvas', smartCorrCanvas._lastMatrix, smartCorrCanvas._lastLabels);
            }
        }).observe(smartCorrCanvas.parentElement);
    }

    // Auto-calculate risk capital for Smart Mode
    const smartBaseCap = document.getElementById('smart-base-capital');
    const smartProfitPct = document.getElementById('smart-profit-pct');
    const smartRiskCap = document.getElementById('smart-risk-capital');
    if (smartBaseCap && smartProfitPct && smartRiskCap) {
        const updateSmartRisk = () => {
            const base = parseFloat(smartBaseCap.value) || 1000;
            const pct = parseFloat(smartProfitPct.value) || 20;
            smartRiskCap.value = (base * pct / 100).toFixed(2);
        };
        smartBaseCap.addEventListener('input', updateSmartRisk);
        smartProfitPct.addEventListener('input', updateSmartRisk);
        updateSmartRisk();
    }

    // Smart Optimization run button listener
    const btnSmartRun = document.getElementById('btn-smart-run');
    if (btnSmartRun) {
        btnSmartRun.addEventListener('click', runSmartOptimization);
    }

    // Event listeners
    document.getElementById('backtest-form').addEventListener('submit', runBacktest);
    
    const btnCalcStreak = document.getElementById('btn-calc-streak');
    if (btnCalcStreak) btnCalcStreak.addEventListener('click', runStreakPlanner);
    
    // Auto-calculate risk capital from base and percent
    const baseCapInput = document.getElementById('opt-base-capital');
    const profitPctInput = document.getElementById('opt-profit-pct');
    const riskCapInput = document.getElementById('opt-risk-capital');
    if (baseCapInput && profitPctInput && riskCapInput) {
        const targetCapInput = document.getElementById('opt-target-capital');
        const updateRiskAndTarget = () => {
            const base = parseFloat(baseCapInput.value) || 1000;
            const pct = parseFloat(profitPctInput.value) || 20;
            riskCapInput.value = (base * pct / 100).toFixed(2);
            // Auto-sync target = base capital (goal: duplicate patrimony)
            if (targetCapInput && (parseFloat(targetCapInput.value) === parseFloat(targetCapInput.dataset.lastBase || 1000) || !targetCapInput.dataset.userModified)) {
                targetCapInput.value = base;
                targetCapInput.dataset.lastBase = base;
            }
        };
        // Mark if user manually modifies target
        if (document.getElementById('opt-target-capital')) {
            document.getElementById('opt-target-capital').addEventListener('input', function() {
                this.dataset.userModified = '1';
            });
        }
        baseCapInput.addEventListener('input', updateRiskAndTarget);
        profitPctInput.addEventListener('input', updateRiskAndTarget);
        baseCapInput.addEventListener('change', updateRiskAndTarget);
        profitPctInput.addEventListener('change', updateRiskAndTarget);
        // Run initial calculation
        updateRiskAndTarget();
    }

    document.getElementById('pair-selector').addEventListener('change', () => onPairChanged());
    document.getElementById('interval-selector').addEventListener('change', () => loadCandles());
    document.getElementById('source-selector').addEventListener('change', () => loadCandles());
    
    // Results tab listeners
    const saveBtn = document.getElementById('save-backtest-btn');
    if (saveBtn) saveBtn.addEventListener('click', saveCurrentBacktest);
    const clearHistoryBtn = document.getElementById('btn-clear-history');
    if (clearHistoryBtn) clearHistoryBtn.addEventListener('click', clearHistory);
    
    // Listeners for cycle probability calculation
    const nConsecInput = document.getElementById('backtest-n-consecutive');
    if (nConsecInput) {
        nConsecInput.addEventListener('input', updateCycleProbability);
        nConsecInput.addEventListener('change', updateCycleProbability);
    }

    // Load data from API
    await loadPairs();
    updatePairTimeframeRestrictions();
    await loadStrategies();
    await loadCandles();
    
    // Initial probability calculation
    updateCycleProbability();
    
    // Render persisted backtests
    renderResultsLists();
    
    // Genetic optimizer in Rust listener
    const geneticBtn = document.getElementById('optimize-genetic-btn');
    if (geneticBtn) geneticBtn.addEventListener('click', runGeneticOptimizer);

    // Barbell survival simulation listener
    const barbellBtn = document.getElementById('btn-sim-barbell');
    if (barbellBtn && typeof runBarbellSimulation === 'function') barbellBtn.addEventListener('click', runBarbellSimulation);
}

function prepareCandles(candles) {
    if (!Array.isArray(candles) || candles.length === 0) return [];
    const sorted = [...candles].sort((a, b) => a.time - b.time);
    const clean = [];
    let lastT = null;
    let prevClose = null;

    for (const c of sorted) {
        if (c && typeof c.time === 'number' && !isNaN(c.time) && c.time !== lastT && !isNaN(c.close)) {
            const open = parseFloat(c.open);
            const close = parseFloat(c.close);
            const high = parseFloat(c.high);
            const low = parseFloat(c.low);
            const volume = parseFloat(c.volume || 0);

            let isBearish = false;
            if (close < open) {
                isBearish = true;
            } else if (close === open && prevClose !== null && close < prevClose) {
                isBearish = true;
            }

            const barColor = isBearish ? '#f43f5e' : (close > open || (prevClose !== null && close > prevClose) ? '#10b981' : '#94a3b8');

            clean.push({
                time: c.time,
                open: open,
                high: high,
                low: low,
                close: close,
                volume: volume,
                color: barColor,
                wickColor: barColor,
                borderColor: barColor
            });

            lastT = c.time;
            prevClose = close;
        }
    }
    return clean;
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const pane = document.getElementById(tabId);
    if (pane) pane.classList.add('active');
    const tabBtn = document.querySelector(`[data-tab="${tabId}"]`);
    if (tabBtn) tabBtn.classList.add('active');
    state.currentTab = tabId;

    setTimeout(() => {
        ['tv-chart', 'smart-tv-chart'].forEach(id => {
            const el = document.getElementById(id);
            if (el && el.clientWidth > 0 && el.clientHeight > 0) {
                const targetChart = id === 'tv-chart' ? mainChart : smartChart;
                if (targetChart) {
                    targetChart.applyOptions({ width: el.clientWidth, height: el.clientHeight });
                    targetChart.timeScale().fitContent();
                }
            }
        });

        const smartCorr = document.getElementById('smart-correlation-canvas');
        if (smartCorr && smartCorr._lastMatrix && smartCorr._lastLabels) {
            createCorrelationHeatmap('smart-correlation-canvas', smartCorr._lastMatrix, smartCorr._lastLabels);
        }
    }, 50);
}

// ==================== DATA ====================

async function loadPairs() {
    try {
        const res = await fetch(`${API}/data/pairs`);
        const data = await res.json();
        const pairSel = document.getElementById('pair-selector');
        const intSel = document.getElementById('interval-selector');
        
        const currentPair = pairSel.value;
        const currentInt = intSel.value;

        if (data.pairs && data.pairs.length > 0) {
            pairSel.innerHTML = data.pairs.map(p => `<option value="${p}">${p}</option>`).join('');
            if (data.pairs.includes(currentPair)) pairSel.value = currentPair;
        }

        const intervalOrder = { '1d': 1, '4h': 2, '2h': 3, '1h': 4, '30m': 5, '15m': 6, '5m': 7, '3m': 8, '1m': 9 };
        const rawIntervals = data.intervals || ['1d', '4h', '1h', '30m', '15m', '5m', '1m'];
        const sortedIntervals = [...new Set(rawIntervals)].sort(
            (a, b) => (intervalOrder[a] || 99) - (intervalOrder[b] || 99)
        );

        intSel.innerHTML = sortedIntervals.map(i => `<option value="${i}">${i}</option>`).join('');
        if (sortedIntervals.includes(currentInt)) {
            intSel.value = currentInt;
        }

        updatePairTimeframeRestrictions();
    } catch (e) {
        console.error('Error loading pairs:', e);
    }
}

function updatePairTimeframeRestrictions() {
    const pair = document.getElementById('pair-selector')?.value || 'BTCUSDT';
    const intSel = document.getElementById('interval-selector');
    const sourceSel = document.getElementById('source-selector');
    const isCrypto = pair.endsWith('USDT');

    if (!isCrypto) {
        // Traditional / Forex / Yahoo Finance asset: restricted to 1d+ timeframes and historical source
        if (intSel) {
            Array.from(intSel.options).forEach(opt => {
                if (opt.value !== '1d') {
                    opt.disabled = true;
                } else {
                    opt.disabled = false;
                }
            });
            if (intSel.value !== '1d') {
                intSel.value = '1d';
            }
        }
        if (sourceSel && sourceSel.value === 'live') {
            sourceSel.value = 'historical';
        }
    } else {
        // Crypto asset: enable all timeframes
        if (intSel) {
            Array.from(intSel.options).forEach(opt => {
                opt.disabled = false;
            });
        }
    }
}

function onPairChanged() {
    updatePairTimeframeRestrictions();
    loadCandles();
}

async function loadCandles() {
    stopLiveStream();
    updatePairTimeframeRestrictions();

    const pair = document.getElementById('pair-selector')?.value || 'BTCUSDT';
    const interval = document.getElementById('interval-selector')?.value || '1h';
    const source = document.getElementById('source-selector')?.value || 'historical';
    const loader = document.getElementById('chart-loader');
    if (loader) loader.classList.add('active');

    try {
        let candles = [];
        if (source === 'live') {
            try {
                const res = await fetch(`https://api.binance.com/api/v3/klines?symbol=${pair}&interval=${interval}&limit=1000`);
                const data = await res.json();
                if (Array.isArray(data)) {
                    candles = data.map(c => ({
                        time: Math.floor(c[0] / 1000),
                        open: parseFloat(c[1]),
                        high: parseFloat(c[2]),
                        low: parseFloat(c[3]),
                        close: parseFloat(c[4]),
                        volume: parseFloat(c[5])
                    }));
                } else {
                    console.warn('Respuesta de Binance no es lista, usando fallback a histórico local:', data);
                    const sourceSel = document.getElementById('source-selector');
                    if (sourceSel) sourceSel.value = 'historical';
                    const fallbackRes = await fetch(`${API}/data/candles?pair=${pair}&interval=${interval}&limit=1000`);
                    const fallbackData = await fallbackRes.json();
                    candles = fallbackData.candles || [];
                }
            } catch (err) {
                console.warn('Error cargando velas de Binance, usando fallback a histórico local:', err);
                const sourceSel = document.getElementById('source-selector');
                if (sourceSel) sourceSel.value = 'historical';
                const fallbackRes = await fetch(`${API}/data/candles?pair=${pair}&interval=${interval}&limit=1000`);
                const fallbackData = await fallbackRes.json();
                candles = fallbackData.candles || [];
            }
        } else {
            const res = await fetch(`${API}/data/candles?pair=${pair}&interval=${interval}&limit=1000`);
            const data = await res.json();
            candles = data.candles || [];
        }

        const cleanCandles = prepareCandles(candles);
        if (cleanCandles.length > 0) {
            state.candles = cleanCandles;
            if (candleSeries) {
                candleSeries.setData(cleanCandles);
                candleSeries.setMarkers([]);
            }
            
            setTimeout(() => {
                const totalBars = cleanCandles.length;
                const visibleBars = Math.min(120, totalBars);
                if (mainChart) {
                    mainChart.timeScale().setVisibleLogicalRange({
                        from: totalBars - visibleBars,
                        to: totalBars + 5
                    });
                }
            }, 30);
        }

        const activeSource = document.getElementById('source-selector')?.value;
        if (activeSource === 'live' && cleanCandles.length > 0) {
            connectLiveStream(pair, interval);
        }
    } catch (e) {
        console.error('Error loading candles:', e);
    }
    if (loader) loader.classList.remove('active');
}

// ==================== STRATEGIES ====================

async function loadStrategies() {
    try {
        const res = await fetch(`${API}/strategies`);
        const data = await res.json();
        state.strategies = data.strategies || [];
        const sel = document.getElementById('strategy-selector');
        sel.innerHTML = state.strategies.map(s =>
            `<option value="${s.name}">${s.display_name || s.name}</option>`
        ).join('');
        sel.addEventListener('change', () => renderStrategyParams(sel.value));
        if (state.strategies.length > 0) renderStrategyParams(state.strategies[0].name);
    } catch (e) {
        console.error('Error loading strategies:', e);
    }
}

// Subtab navigation in Backtest section
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.subtab-btn');
    if (!btn) return;
    const targetTab = btn.dataset.subtab;
    if (!targetTab) return;
    
    document.querySelectorAll('.subtab-btn').forEach(b => {
        if (b === btn) {
            b.classList.add('active');
        } else {
            b.classList.remove('active');
        }
    });

    document.querySelectorAll('.subtab-pane').forEach(pane => {
        if (pane.id === targetTab) {
            pane.style.display = 'block';
        } else {
            pane.style.display = 'none';
        }
    });
});

function renderStrategyParams(strategyName) {
    state.selectedStrategy = strategyName;
    const strat = state.strategies.find(s => s.name === strategyName);
    const container = document.getElementById('dynamic-params');
    if (!strat || !strat.params) { container.innerHTML = ''; return; }

    container.innerHTML = strat.params.map(p => `
        <div class="control-group">
            <label for="param-${p.name}">${p.description || p.name}
                <span class="tooltip">?
                    <span class="tooltip-text">${p.description || p.name} (Rango sugerido: ${p.min !== undefined ? p.min : 'min'} a ${p.max !== undefined ? p.max : 'max'}).</span>
                </span>
            </label>
            <input type="number" id="param-${p.name}" data-param="${p.name}"
                   value="${p.default}" min="${p.min || ''}" max="${p.max || ''}"
                   step="${p.step || 'any'}" required>
        </div>
    `).join('');
}

// ==================== BACKTEST ====================

async function runBacktest(e) {
    e.preventDefault();
    const btn = document.getElementById('run-backtest-btn');
    btn.textContent = 'Ejecutando...';
    btn.disabled = true;

    const saveBtn = document.getElementById('save-backtest-btn');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Guardar en Favoritos';
    }

    // Collect params
    const params = {};
    document.querySelectorAll('#dynamic-params input[data-param]').forEach(inp => {
        const val = parseFloat(inp.value);
        params[inp.dataset.param] = isNaN(val) ? inp.value : val;
    });

    const strategy = state.selectedStrategy || document.getElementById('strategy-selector').value;
    const pair = document.getElementById('pair-selector').value;
    const interval = document.getElementById('interval-selector').value;
    const expiry_candles = parseInt(document.getElementById('expiry-candles').value) || 1;
    const payout = parseFloat(document.getElementById('payout').value) || 0.92;
    const mode = 'BARBELL';
    const n_consecutive = parseInt(document.getElementById('backtest-n-consecutive').value) || 4;
    const bet_fraction = parseFloat(document.getElementById('backtest-bet-fraction').value) || 0.1;
    
    // Construct query parameters
    const queryParams = new URLSearchParams({
        strategy: strategy,
        params: JSON.stringify(params),
        pair: pair,
        interval: interval,
        expiry_candles: expiry_candles,
        payout: payout,
        mode: mode,
        n_consecutive: n_consecutive,
        bet_fraction: bet_fraction
    });

    // Show progress bar
    const progressContainer = document.getElementById('backtest-progress-container');
    const progressBarFill = document.getElementById('backtest-progress-fill');
    const progressText = document.getElementById('backtest-progress-text');
    const progressEta = document.getElementById('backtest-progress-eta');

    if (progressContainer) progressContainer.style.display = 'block';
    if (progressBarFill) progressBarFill.style.width = '0%';
    if (progressText) progressText.textContent = 'Progreso: 0%';
    if (progressEta) progressEta.textContent = 'ETA: --s';

    const eventSource = new EventSource(`${API}/backtest-stream?${queryParams.toString()}`);

    eventSource.onmessage = (event) => {
        const item = JSON.parse(event.data);
        if (item.type === 'log') {
            console.log(item.message);
        } else if (item.type === 'progress') {
            const pct = item.progress.toFixed(1);
            if (progressBarFill) progressBarFill.style.width = `${pct}%`;
            if (progressText) progressText.textContent = `Progreso: ${pct}%`;
            if (progressEta) {
                progressEta.textContent = `Restante: ${item.eta.toFixed(1)}s`;
            }
        } else if (item.type === 'error') {
            alert('Error: ' + item.message);
            eventSource.close();
            btn.textContent = 'Ejecutar Backtest Barbell';
            btn.disabled = false;
            if (progressContainer) progressContainer.style.display = 'none';
        } else if (item.type === 'result') {
            eventSource.close();
            if (progressContainer) progressContainer.style.display = 'none';
            
            const data = item.data;
            state.backtestResults = data;
            displayBacktestResults(data);
            displayStatistics(data.stats || {});
            
            // Add signal markers to chart
            if (data.signals && data.signals.length > 0) {
                const markers = buildChartMarkers(data.signals);
                candleSeries.setMarkers(markers);
            }
            
            // Enable tabs
            document.getElementById('btn-estadisticas').disabled = false;
            document.getElementById('btn-optimizador').disabled = false;
            
            // Auto-fill optimizer
            const wr = data.summary?.win_rate || data.stats?.basic?.win_rate || 0;
            document.getElementById('opt-winrate').value = (wr * 100).toFixed(2);
            document.getElementById('opt-payout').value = payout;
            
            // Save current backtest inputs and results
            const inputs = {
                strategy: strategy,
                strategy_display: document.getElementById('strategy-selector').options[document.getElementById('strategy-selector').selectedIndex].text,
                params: params,
                pair: pair,
                interval: interval,
                expiry_candles: expiry_candles,
                payout: payout,
                mode: mode,
                n_consecutive: n_consecutive,
                bet_fraction: bet_fraction
            };
            
            state.currentBacktestData = {
                id: 'bt_' + Date.now(),
                timestamp: Date.now(),
                inputs: inputs,
                results: data,
                optimizer: null,
                montecarlo: null
            };
            
            // Show save button
            const backtestSaveBtn = document.getElementById('save-backtest-btn');
            if (backtestSaveBtn) {
                backtestSaveBtn.style.display = 'block';
                backtestSaveBtn.textContent = 'Guardar en Favoritos';
                backtestSaveBtn.disabled = false;
            }
            
            // Append to history in localStorage
            const historyList = getHistory();
            historyList.unshift(state.currentBacktestData);
            if (historyList.length > 50) historyList.pop();
            setHistory(historyList);
            renderResultsLists();

            btn.textContent = 'Ejecutar Backtest Barbell';
            btn.disabled = false;
        }
    };

    eventSource.onerror = (err) => {
        console.error('SSE Error:', err);
        eventSource.close();
        alert('Error de conexión con el servidor.');
        btn.textContent = 'Ejecutar Backtest Barbell';
        btn.disabled = false;
        if (progressContainer) progressContainer.style.display = 'none';
    };
}

function formatPrice(price) {
    if (price === undefined || price === null || isNaN(price)) return '--';
    const p = parseFloat(price);
    return Math.abs(p) < 10 ? p.toFixed(4) : p.toFixed(2);
}

function displayBacktestResults(data) {
    const s = data.summary || data.stats?.basic || data.stats || {};
    const wr = s.win_rate !== undefined ? s.win_rate : (data.stats?.win_rate !== undefined ? data.stats.win_rate : (data.stats?.basic?.win_rate || 0));
    state.lastWinRate = wr;
    updateCycleProbability();
    
    document.getElementById('stat-winrate').textContent = (wr * 100).toFixed(2) + '%';
    document.getElementById('stat-trades').textContent = s.total_trades || s.total || data.stats?.total_trades || data.stats?.basic?.total_trades || 0;

    const pnl = s.net_pnl !== undefined ? s.net_pnl : (data.stats?.net_pnl !== undefined ? data.stats.net_pnl : (data.stats?.basic?.net_pnl || 0));
    const pnlEl = document.getElementById('stat-pnl');
    pnlEl.textContent = (pnl > 0 ? '+' : '') + pnl.toFixed(2);
    pnlEl.className = pnl > 0 ? 'text-green' : 'text-red';

    const maxWin = s.max_win_streak !== undefined ? s.max_win_streak : (data.stats?.max_win_streak !== undefined ? data.stats.max_win_streak : (data.stats?.streaks?.max_win_streak));
    const maxLoss = s.max_loss_streak !== undefined ? s.max_loss_streak : (data.stats?.max_loss_streak !== undefined ? data.stats.max_loss_streak : (data.stats?.streaks?.max_loss_streak));
    document.getElementById('stat-mw').textContent = maxWin !== undefined ? maxWin : '--';
    document.getElementById('stat-ml').textContent = maxLoss !== undefined ? maxLoss : '--';


    // Equity curve
    if (data.equity_curve && data.equity_curve.length > 0) {
        createEquityCurve('equity-chart', data.equity_curve);
    }

    // Trades table (last 100) con interacción de líneas de precio exactas
    const tbody = document.querySelector('#trades-table tbody');
    const trades = (data.trades || []).slice(-100);
    tbody.innerHTML = trades.map((t, idx) => {
        const date = t.time ? new Date(t.time * 1000).toISOString().slice(0, 16).replace('T', ' ') : '--';
        return `<tr data-trade-idx="${idx}" style="cursor: pointer;" title="Haz clic para ver líneas exactas de entrada y salida en el gráfico">
            <td>${date}</td>
            <td>${t.direction}</td>
            <td>${formatPrice(t.entry_price)}</td>
            <td>${formatPrice(t.exit_price)}</td>
            <td class="${t.result === 'WIN' ? 'text-green' : 'text-red'}">${t.result}</td>
            <td class="${(t.pnl || 0) > 0 ? 'text-green' : 'text-red'}">${(t.pnl || 0) > 0 ? '+' : ''}${(t.pnl || 0).toFixed(2)}</td>
        </tr>`;
    }).join('');

    tbody.querySelectorAll('tr').forEach(row => {
        row.addEventListener('click', (e) => {
            const idx = parseInt(e.currentTarget.dataset.tradeIdx);
            const trade = trades[idx];
            if (!trade) return;
            tbody.querySelectorAll('tr').forEach(r => r.style.background = 'transparent');
            row.style.background = 'rgba(168, 85, 247, 0.15)';
            highlightTradeOnChart(trade, mainChart, candleSeries);
        });
    });
}

let activeChartPriceLines = [];
function highlightTradeOnChart(trade, chartObj, seriesObj) {
    if (!seriesObj || !trade) return;
    
    // Eliminar líneas de precio anteriores
    activeChartPriceLines.forEach(line => {
        try { seriesObj.removePriceLine(line); } catch (e) {}
    });
    activeChartPriceLines = [];
    
    if (trade.entry_price) {
        const entryLine = seriesObj.createPriceLine({
            price: trade.entry_price,
            color: trade.direction === 'CALL' ? '#10b981' : '#f43f5e',
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Dashed,
            axisLabelVisible: true,
            title: `Entrada ${trade.direction}: ${formatPrice(trade.entry_price)}`
        });
        activeChartPriceLines.push(entryLine);
    }
    
    if (trade.exit_price) {
        const exitLine = seriesObj.createPriceLine({
            price: trade.exit_price,
            color: trade.result === 'WIN' ? '#10b981' : '#f43f5e',
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Dotted,
            axisLabelVisible: true,
            title: `Salida ${trade.result}: ${formatPrice(trade.exit_price)} (${(trade.pnl || 0) >= 0 ? '+' : ''}${(trade.pnl || 0).toFixed(2)}$)`
        });
        activeChartPriceLines.push(exitLine);
    }
}

function displayStatistics(stats) {
    if (!stats) return;

    // Autocorrelation: Quantum Amethyst for positive, Rose Crimson for negative
    const ac = stats.dependency?.autocorrelation || [];
    if (ac.length > 0) {
        const labels = ac.map((_, i) => `Lag ${i + 1}`);
        const colors = ac.map(v => v >= 0 ? '#a855f7' : '#f43f5e');
        createBarChart('autocorr-chart', labels, ac, 'Autocorrelación', colors);
    }

    // Streak distribution: Electric Sky #38bdf8
    const sd = stats.streaks?.streak_distribution || {};
    if (Object.keys(sd).length > 0) {
        const sortedKeys = Object.keys(sd).map(Number).sort((a, b) => a - b);
        createBarChart('streaks-chart', sortedKeys.map(String), sortedKeys.map(k => sd[k]), 'Frecuencia de Rachas', '#38bdf8');
    }

    // Win rate by hour: Cyber Emerald for >= 58.8%, Electric Sky for 50-58.8%, Rose Crimson for < 50%
    const bh = stats.temporal?.by_hour || {};
    if (Object.keys(bh).length > 0) {
        const hours = Object.keys(bh).map(Number).sort((a, b) => a - b);
        const values = hours.map(h => bh[h]);
        const colors = values.map(wr => {
            const pct = wr > 1 ? wr : wr * 100;
            if (pct >= 58.8) return '#10b981';
            if (pct >= 50.0) return '#38bdf8';
            return '#f43f5e';
        });
        createBarChart('hourly-chart', hours.map(h => h + 'h'), values, 'Win Rate por Hora', colors);
    }

    // Conditional probabilities
    const dep = stats.dependency || {};
    const probsHtml = `
        <div><span>P(W|W)</span><strong class="text-green">${((dep.p_win_given_win || 0) * 100).toFixed(1)}%</strong></div>
        <div><span>P(W|L)</span><strong>${((dep.p_win_given_loss || 0) * 100).toFixed(1)}%</strong></div>
        <div><span>P(L|W)</span><strong>${((dep.p_loss_given_win || 0) * 100).toFixed(1)}%</strong></div>
        <div><span>P(L|L)</span><strong class="text-red">${((dep.p_loss_given_loss || 0) * 100).toFixed(1)}%</strong></div>
    `;
    const condEl = document.getElementById('cond-probs');
    if (condEl) condEl.innerHTML = probsHtml;

    // Market state: Regime tokens
    const ms = stats.market_state || {};
    if (Object.values(ms).some(v => v > 0)) {
        createBarChart('market-state-chart',
            ['Alta Vol', 'Baja Vol', 'Tendencia', 'Rango'],
            [ms.high_vol_wr || 0, ms.low_vol_wr || 0, ms.trending_wr || 0, ms.ranging_wr || 0],
            'Win Rate por Régimen',
            ['#f59e0b', '#38bdf8', '#10b981', '#a855f7']
        );
    }

    // Markov table
    const mt = stats.markov?.transition_matrix || [];
    if (mt.length > 0) {
        const tbl = document.getElementById('markov-table');
        if (tbl) {
            let html = '<thead><tr><th>Si el anterior fue...</th><th>Siguiente: Win</th><th>Siguiente: Loss</th></tr></thead><tbody>';
            const labels = ['Win', 'Loss'];
            mt.forEach((row, i) => {
                html += `<tr><td><strong>${labels[i] || i}</strong></td>`;
                (row || []).forEach(v => { html += `<td>${(v * 100).toFixed(1)}%</td>`; });
                html += '</tr>';
            });
            html += '</tbody>';
            tbl.innerHTML = html;
        }
    }
}

// ==================== OPTIMIZER ====================

async function runStreakPlanner() {
    const btn = document.getElementById('btn-calc-streak');
    if (!btn) return;
    btn.textContent = 'Calculando...';
    btn.disabled = true;

    const winRate = parseFloat(document.getElementById('opt-winrate').value) / 100;
    const payout = parseFloat(document.getElementById('opt-payout').value) || 0.85;
    const baseCapital = parseFloat(document.getElementById('opt-base-capital').value) || 1000;
    const profitPct = parseFloat(document.getElementById('opt-profit-pct').value) || 20;
    const riskCapital = baseCapital * profitPct / 100;
    const targetCapital = parseFloat(document.getElementById('opt-target-capital').value) || 1000;
    const attempts = parseInt(document.getElementById('opt-attempts').value) || 5;

    if (isNaN(winRate) || winRate <= 0) {
        alert('Por favor, ingresa un Win Rate o ejecuta primero un Backtest.');
        btn.textContent = 'Calcular Plan de Rachas';
        btn.disabled = false;
        return;
    }

    // Show progress bar with smooth transition (since calculation is instant)
    const progressContainer = document.getElementById('streak-progress-container');
    const progressBarFill = document.getElementById('streak-progress-fill');
    const progressText = document.getElementById('streak-progress-text');
    const progressEta = document.getElementById('streak-progress-eta');

    if (progressContainer) progressContainer.style.display = 'block';
    if (progressBarFill) progressBarFill.style.width = '50%';
    if (progressText) progressText.textContent = 'Calculando plan...';
    if (progressEta) progressEta.textContent = 'En proceso';

    const body = {
        win_rate: winRate,
        payout: payout,
        risk_capital: riskCapital,
        target_capital: targetCapital,
        attempts: attempts
    };

    try {
        const res = await fetch(`${API}/optimize-streak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (progressContainer) progressContainer.style.display = 'none';

        if (data.error) {
            alert('Error: ' + data.error);
            btn.textContent = 'Calcular Plan de Rachas';
            btn.disabled = false;
            return;
        }

        const results = data.results_by_n || [];
        const bestN = data.best_n_for_target;
        const bestPlan = results.find(r => r.n === bestN);

        // 1. Render Recommendation
        const recDiv = document.getElementById('streak-recommendation-content');
        if (recDiv && bestPlan) {
            const successProb = (bestPlan.p_success_campaign * 100).toFixed(1);
            const probDup = bestPlan.prob_duplication_pct !== undefined ? bestPlan.prob_duplication_pct.toFixed(1) : (bestPlan.p_success_campaign * 100).toFixed(1);
            const neededM = bestPlan.needed_streaks || 1;
            const expNetProfit = bestPlan.expected_monthly_net_profit !== undefined ? bestPlan.expected_monthly_net_profit : bestPlan.expected_value;
            const expPatrimony = bestPlan.expected_final_patrimony !== undefined ? bestPlan.expected_final_patrimony : (baseCapital + expNetProfit);
            const evClass = expNetProfit >= 0 ? 'green' : 'red';
            const statusIndicator = expNetProfit >= 0 ? '🟢 Esperanza Matemática Positiva' : '⚠️ Esperanza Matemática Negativa';
            
            recDiv.innerHTML = `
                <div style="font-size: 1rem; line-height: 1.5; color: var(--text-primary);">
                    Para tu capital de riesgo de <strong>$${riskCapital.toFixed(2)} USD</strong> dividido en <strong>${attempts} intentos</strong> de <strong>$${bestPlan.bet_per_attempt.toFixed(2)} USD</strong>:
                    La racha óptima es de <strong style="color: var(--accent-green); font-size: 1.1rem;">N = ${bestN} victorias consecutivas</strong> (Requiere <strong>M = ${neededM} racha(s)</strong> para duplicación).
                </div>
                <div class="recommendation-banner" style="margin-top: 15px; display: grid; grid-template-columns: repeat(auto-fit, minmax(105px, 1fr)); gap: 8px;">
                    <div class="recommendation-stat">
                        <h4>Prob. Duplicación</h4>
                        <p class="green">${probDup}%</p>
                        <span style="font-size: 0.72rem; color: var(--text-secondary)">Binomial (&ge; ${neededM} rachas)</span>
                    </div>
                    <div class="recommendation-stat">
                        <h4>Rachas M</h4>
                        <p class="blue">${neededM}</p>
                        <span style="font-size: 0.72rem; color: var(--text-secondary)">para meta</span>
                    </div>
                    <div class="recommendation-stat">
                        <h4>Prob. &ge;1 Racha</h4>
                        <p class="green">${successProb}%</p>
                        <span style="font-size: 0.72rem; color: var(--text-secondary)">en ${attempts} intentos</span>
                    </div>
                    <div class="recommendation-stat">
                        <h4>Ganancia Neta</h4>
                        <p class="${evClass}">${expNetProfit >= 0 ? '+' : ''}$${expNetProfit.toFixed(2)}</p>
                        <span style="font-size: 0.72rem; color: var(--text-secondary)">USD esperados</span>
                    </div>
                    <div class="recommendation-stat">
                        <h4>Patrimonio Final</h4>
                        <p class="blue">$${expPatrimony.toFixed(2)}</p>
                        <span style="font-size: 0.72rem; color: var(--text-secondary)">USD esperados</span>
                    </div>
                </div>
                <div style="margin-top: 15px; font-size: 0.82rem; padding: 10px; border-radius: 6px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); color: var(--text-secondary); line-height: 1.4;">
                    ${statusIndicator}. Con un win rate de <strong>${(winRate*100).toFixed(1)}%</strong> y un payout del <strong>${(payout*100).toFixed(0)}%</strong>, la probabilidad binomial de completar las <strong>M = ${neededM} racha(s)</strong> requeridas es del <strong>${probDup}%</strong>.
                </div>
            `;
        }

        // 2. Render Bet Ladder
        const ladderDiv = document.getElementById('bet-ladder-container');
        if (ladderDiv && bestPlan) {
            let ladderHtml = '<div class="streak-ladder">';
            bestPlan.bet_ladder.forEach(step => {
                ladderHtml += `
                    <div class="ladder-step">
                        <div class="ladder-step-number">${step.step}</div>
                        <div class="ladder-step-info">
                            <div class="ladder-step-title">Operación ${step.step}</div>
                            <div class="ladder-step-meta">Retorno si gana: +$${step.payout_return.toFixed(2)} USD</div>
                        </div>
                        <div class="ladder-step-amount">$${step.bet_size.toFixed(2)}</div>
                    </div>
                `;
            });
            // Final Meta Step
            ladderHtml += `
                <div class="ladder-step completed">
                    <div class="ladder-step-number">✓</div>
                    <div class="ladder-step-info">
                        <div class="ladder-step-title" style="color: var(--accent-green)">¡Meta Alcanzada!</div>
                        <div class="ladder-step-meta" style="color: var(--text-secondary)">Retira y consolida tus ganancias de forma segura</div>
                    </div>
                    <div class="ladder-step-amount">$${bestPlan.final_capital.toFixed(2)}</div>
                </div>
            `;
            ladderHtml += '</div>';
            ladderDiv.innerHTML = ladderHtml;
        }

        // 3. Render Alternatives Table
        const nTable = document.getElementById('streak-alternatives-table').getElementsByTagName('tbody')[0];
        if (nTable) {
            let tableHtml = '';
            results.forEach(r => {
                const isOpt = r.n === bestN;
                const netProfit = r.expected_monthly_net_profit !== undefined ? r.expected_monthly_net_profit : r.expected_value;
                const isPositive = netProfit >= 0;
                const dupProb = r.prob_duplication_pct !== undefined ? r.prob_duplication_pct.toFixed(1) : (r.p_success_campaign * 100).toFixed(1);
                const neededM = r.needed_streaks !== undefined ? r.needed_streaks : 1;
                tableHtml += `
                    <tr style="${isOpt ? 'background: rgba(63,185,80,0.12); border: 1px solid var(--accent-green);' : ''}">
                        <td><strong>${isOpt ? '>> ' : ''}${r.n}</strong></td>
                        <td>${(r.p_success_single * 100).toFixed(1)}%</td>
                        <td>${neededM}</td>
                        <td>${dupProb}%</td>
                        <td>$${r.bet_per_attempt.toFixed(0)}</td>
                        <td>$${r.final_capital.toFixed(0)}</td>
                        <td class="${isPositive ? 'text-green' : 'text-red'}" style="font-weight: 500;">
                            ${isPositive ? '+' : ''}$${netProfit.toFixed(1)}
                        </td>
                    </tr>
                `;
            });
            nTable.innerHTML = tableHtml;
        }

        // 4. Run Campaign Monte Carlo Simulation
        const paths = simulateCampaignMonteCarlo(winRate, payout, bestN, riskCapital, targetCapital, attempts);
        if (paths.length > 0) {
            const labels = Array.from({ length: attempts + 1 }, (_, i) => i === 0 ? 'Inicio' : `Intento ${i}`);
            
            // Calculate percentiles at each step
            const p95 = [], p75 = [], p50 = [], p25 = [], p5 = [];
            for (let step = 0; step <= attempts; step++) {
                const vals = paths.map(p => {
                    if (step >= p.length) {
                        return p[p.length - 1];
                    }
                    return p[step];
                }).sort((a, b) => a - b);
                
                const len = vals.length;
                p5.push(vals[Math.floor(len * 0.05)]);
                p25.push(vals[Math.floor(len * 0.25)]);
                p50.push(vals[Math.floor(len * 0.50)]);
                p75.push(vals[Math.floor(len * 0.75)]);
                p95.push(vals[Math.floor(len * 0.95)]);
            }
            createMonteCarloChart('mc-chart', labels, { p95, p75, p50, p25, p5 });
        }

    } catch (e) {
        console.error('Streak planner error:', e);
        alert('Error calculando el plan de rachas: ' + e.message);
    }

    btn.textContent = 'Calcular Plan de Rachas';
    btn.disabled = false;
}

function simulateCampaignMonteCarlo(winRate, payout, n, riskCapital, targetCapital, attempts) {
    const numSimulations = 5000;
    const betPerAttempt = riskCapital / attempts;
    const singleSuccessProb = Math.pow(winRate, n);
    const finalAttemptCapital = betPerAttempt * Math.pow(1 + payout, n);
    
    const paths = [];
    for (let i = 0; i < numSimulations; i++) {
        let capital = riskCapital;
        const path = [capital];
        
        for (let attempt = 1; attempt <= attempts; attempt++) {
            // Pay for the attempt
            capital -= betPerAttempt;
            
            // Roll for success
            const isSuccess = Math.random() < singleSuccessProb;
            if (isSuccess) {
                capital += finalAttemptCapital;
                path.push(capital);
                break;
            } else {
                path.push(capital);
            }
        }
        paths.push(path);
    }
    return paths;
}

function updateCycleProbability() {
    const nConsecInput = document.getElementById('backtest-n-consecutive');
    if (!nConsecInput) return;
    const n = parseInt(nConsecInput.value) || 5;
    const wr = state.lastWinRate || 0.5;
    const prob = Math.pow(wr, n);
    const probEl = document.getElementById('backtest-cycle-prob');
    if (probEl) {
        probEl.textContent = `Probabilidad de éxito del ciclo: ${(prob * 100).toFixed(2)}% (basado en Win Rate de ${(wr * 100).toFixed(1)}%)`;
    }
}

// ==================== PERSISTENCE & RESULTS TAB ====================

function getHistory() {
    try {
        return JSON.parse(localStorage.getItem('binsim_history')) || [];
    } catch (e) {
        return [];
    }
}

function setHistory(history) {
    localStorage.setItem('binsim_history', JSON.stringify(history));
}

function getSaved() {
    try {
        return JSON.parse(localStorage.getItem('binsim_saved')) || [];
    } catch (e) {
        return [];
    }
}

function setSaved(saved) {
    localStorage.setItem('binsim_saved', JSON.stringify(saved));
}

function updatePersistedBacktest(backtestObj) {
    // Update in history
    let history = getHistory();
    let idx = history.findIndex(x => x.id === backtestObj.id);
    if (idx !== -1) {
        history[idx] = backtestObj;
        setHistory(history);
    }
    
    // Update in saved
    let saved = getSaved();
    idx = saved.findIndex(x => x.id === backtestObj.id);
    if (idx !== -1) {
        saved[idx] = backtestObj;
        setSaved(saved);
    }
    renderResultsLists();
}

function saveCurrentBacktest() {
    if (!state.currentBacktestData) return;
    
    const saved = getSaved();
    if (saved.some(x => x.id === state.currentBacktestData.id)) {
        alert('Este backtest ya está en favoritos.');
        return;
    }
    
    saved.unshift(state.currentBacktestData);
    setSaved(saved);
    
    const saveBtn = document.getElementById('save-backtest-btn');
    if (saveBtn) {
        saveBtn.textContent = '¡Guardado!';
        saveBtn.disabled = true;
    }
    
    renderResultsLists();
}

function saveBacktestById(id) {
    const history = getHistory();
    const item = history.find(x => x.id === id);
    if (!item) return;
    
    const saved = getSaved();
    if (saved.some(x => x.id === id)) {
        alert('Este backtest ya está en favoritos.');
        return;
    }
    
    saved.unshift(item);
    setSaved(saved);
    renderResultsLists();
}

function deleteBacktestById(id, type) {
    if (type === 'history') {
        const history = getHistory().filter(x => x.id !== id);
        setHistory(history);
    } else {
        const saved = getSaved().filter(x => x.id !== id);
        setSaved(saved);
    }
    
    if (state.loadedBacktestId === id) {
        state.loadedBacktestId = null;
        state.currentBacktestData = null;
    }
    
    renderResultsLists();
}

function clearHistory() {
    if (confirm('¿Seguro que deseas limpiar todo el historial de backtests?')) {
        setHistory([]);
        renderResultsLists();
    }
}

function renderBacktestItemHtml(item, type) {
    const activeClass = state.loadedBacktestId === item.id ? 'active' : '';
    const dateStr = new Date(item.timestamp).toLocaleString('es-ES', { 
        day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' 
    });
    const stratName = item.inputs.strategy_display || item.inputs.strategy;
    const isSmart = item.inputs.is_smart || item.id.startsWith('bt_smart_');
    const badgeHtml = isSmart 
        ? `<span style="font-size: 0.65rem; font-weight: bold; background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.4); padding: 2px 6px; border-radius: 4px; margin-right: 6px;">⚡ AUTO-OPTIMIZACIÓN GENÉTICA</span>`
        : `<span style="font-size: 0.65rem; font-weight: bold; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 6px; border-radius: 4px; margin-right: 6px;">⚙️ BACKTEST MANUAL</span>`;

    let actionsHtml = '';
    if (type === 'history') {
        actionsHtml += `<button type="button" class="btn-save-item" data-id="${item.id}">⭐ Favorito</button>`;
    }
    actionsHtml += `<button type="button" class="btn-delete-item" data-id="${item.id}" data-type="${type}">Eliminar</button>`;
    
    const pnl = item.results.summary?.net_pnl || 0;
    const wr = item.results.summary?.win_rate || 0;
    const pnlClass = pnl > 0 ? 'text-green' : 'text-red';
    
    return `
        <div class="backtest-item ${activeClass}" data-id="${item.id}" data-type="${type}">
            <div class="backtest-item-info">
                <div style="margin-bottom: 4px; display: flex; align-items: center; flex-wrap: wrap; gap: 4px;">
                    ${badgeHtml}
                    <span class="backtest-item-title" style="margin: 0;">${stratName} [${item.inputs.pair}]</span>
                </div>
                <span class="backtest-item-meta">${dateStr} | Expiración: ${item.inputs.expiry_candles}v | Racha N=${item.inputs.n_consecutive || 3}</span>
                <div class="backtest-item-metrics">
                    <span>P&L: <strong class="${pnlClass}">${pnl > 0 ? '+' : ''}${pnl.toFixed(2)}</strong></span>
                    <span>Win Rate: <strong>${(wr * 100).toFixed(1)}%</strong></span>
                    <span>Trades: <strong>${item.results.summary?.total_trades || 0}</strong></span>
                </div>
            </div>
            <div class="backtest-item-actions">
                ${actionsHtml}
            </div>
        </div>
    `;
}

function renderResultsLists() {
    const history = getHistory();
    const saved = getSaved();
    
    const historyList = document.getElementById('history-list');
    const savedList = document.getElementById('saved-list');
    
    if (history.length === 0) {
        historyList.innerHTML = '<p class="empty-text">No hay optimizaciones automáticas registradas en el historial.</p>';
    } else {
        historyList.innerHTML = history.map(item => renderBacktestItemHtml(item, 'history')).join('');
    }
    
    if (saved.length === 0) {
        savedList.innerHTML = '<p class="empty-text">No hay simulaciones manuales o favoritas guardadas.</p>';
    } else {
        savedList.innerHTML = saved.map(item => renderBacktestItemHtml(item, 'saved')).join('');
    }
    
    // Bind item click listeners
    document.querySelectorAll('.backtest-item').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') return;
            const id = el.dataset.id;
            const type = el.dataset.type;
            const list = type === 'history' ? getHistory() : getSaved();
            const item = list.find(x => x.id === id);
            if (item) loadBacktestState(item);
        });
    });
    
    // Bind action button listeners
    document.querySelectorAll('.btn-save-item').forEach(el => {
        el.addEventListener('click', (e) => {
            const id = el.dataset.id;
            saveBacktestById(id);
        });
    });
    
    document.querySelectorAll('.btn-delete-item').forEach(el => {
        el.addEventListener('click', (e) => {
            const id = el.dataset.id;
            const type = el.dataset.type;
            deleteBacktestById(id, type);
        });
    });
}

function loadBacktestState(backtestObj) {
    state.loadedBacktestId = backtestObj.id;
    state.currentBacktestData = backtestObj;
    
    // Si estamos en Modo Simple, cambiar a Modo Avanzado
    const btnAdvanced = document.getElementById('mode-advanced');
    if (btnAdvanced && !btnAdvanced.classList.contains('active')) {
        btnAdvanced.click();
    }
    
    // 1. Restore Backtest inputs
    const inp = backtestObj.inputs;
    
    const stratSel = document.getElementById('strategy-selector');
    if (stratSel) {
        stratSel.value = inp.strategy;
        renderStrategyParams(inp.strategy);
        
        setTimeout(() => {
            if (inp.params) {
                Object.keys(inp.params).forEach(k => {
                    const paramInput = document.getElementById(`param-${k}`);
                    if (paramInput) paramInput.value = inp.params[k];
                });
            }
        }, 100);
    }
    
    document.getElementById('pair-selector').value = inp.pair;
    document.getElementById('interval-selector').value = inp.interval;
    document.getElementById('expiry-candles').value = inp.expiry_candles;
    document.getElementById('payout').value = inp.payout;
    document.getElementById('backtest-n-consecutive').value = inp.n_consecutive;
    document.getElementById('backtest-bet-fraction').value = inp.bet_fraction;
    
    // 2. Restore Backtest Results UI
    state.backtestResults = backtestObj.results;
    displayBacktestResults(backtestObj.results);
    displayStatistics(backtestObj.results.stats || {});
    
    // Add signal markers to candles chart
    if (state.candles && state.candles.length > 0 && backtestObj.results.signals) {
        const markers = buildChartMarkers(backtestObj.results.signals);
        candleSeries.setMarkers(markers);
    }
    
    // Enable tabs
    document.getElementById('btn-estadisticas').disabled = false;
    document.getElementById('btn-optimizador').disabled = false;
    
    // Auto-fill optimizer inputs
    const wr = backtestObj.results.summary?.win_rate || backtestObj.results.stats?.basic?.win_rate || 0;
    const optWrEl = document.getElementById('opt-winrate');
    if (optWrEl) optWrEl.value = (wr * 100).toFixed(2);
    const optPayoutEl = document.getElementById('opt-payout');
    if (optPayoutEl) optPayoutEl.value = inp.payout;
    
    // 3. Restore Optimizer UI if it exists in the saved object
    if (backtestObj.optimizer) {
        state.optimizerResults = backtestObj.optimizer;
        const optData = backtestObj.optimizer;
        const results = optData.results_by_n || [];
        const bestN = optData.best_n_for_target || optData.optimal_n;
        const bestPlan = results.find(r => r.n === bestN);

        const ns = results.map(r => r.n);
        const gs = results.map(r => r.growth_per_trade);
        if (document.getElementById('gn-chart')) {
            createGrowthRateChart('gn-chart', ns, gs, optData.optimal_n);
        }
        
        const kellys = results.map(r => r.kelly_f);
        if (document.getElementById('kelly-chart')) {
            createBarChart('kelly-chart', ns, kellys, 'Kelly Fraction', '#10b981');
        }
        
        const rec = document.getElementById('opt-recommendation');
        if (rec) {
            rec.style.display = 'block';
            rec.innerHTML = `
                <div class="stat-card" style="margin-top: 15px; border-left: 3px solid var(--accent-green);">
                    <h3 style="color: var(--accent-green)">Recomendacion Optima</h3>
                    <p style="font-size: 2rem; font-weight: 700;">N = ${optData.optimal_n || bestN}</p>
                    <span style="font-size: 0.9rem; color: var(--text-secondary)">
                        Kelly: ${((optData.optimal_kelly || 0) * 100).toFixed(1)}% |
                        G(N) = ${((optData.optimal_growth || 0) * 100).toFixed(4)}% por trade
                    </span>
                </div>
            `;
        }
        
        const nTable = document.getElementById('n-table');
        if (nTable) {
            let tableHtml = `<thead><tr>
                <th>N</th><th>P(exito)</th><th>Ganancia</th><th>Kelly</th><th>G(N)/trade</th><th>Sharpe</th>
            </tr></thead><tbody>`;
            results.forEach(r => {
                const isOpt = r.n === (optData.optimal_n || bestN);
                tableHtml += `<tr style="${isOpt ? 'background: rgba(16, 185, 129, 0.15);' : ''}">
                    <td>${isOpt ? '>> ' : ''}${r.n}</td>
                    <td>${((r.p_success || r.p_success_single || 0) * 100).toFixed(1)}%</td>
                    <td>${(r.profit_if_win || r.multiplier || 0).toFixed(2)}x</td>
                    <td>${((r.kelly_f || 0) * 100).toFixed(1)}%</td>
                    <td>${((r.growth_per_trade || 0) * 100).toFixed(4)}%</td>
                    <td>${(r.sharpe_ratio || 0).toFixed(3)}</td>
                </tr>`;
            });
            tableHtml += '</tbody>';
            nTable.innerHTML = tableHtml;
        }

        // Render into new streak plan UI elements if present
        const recContent = document.getElementById('streak-recommendation-content');
        if (recContent && bestPlan) {
            recContent.innerHTML = `
                <div style="font-size: 0.9rem; line-height: 1.5; color: var(--text-primary);">
                    Campaña para <strong>$${(bestPlan.final_capital || 0).toFixed(2)} USD</strong> con racha de <strong style="color: var(--accent-green);">N = ${bestN}</strong>.
                </div>
            `;
        }
    } else {
        state.optimizerResults = null;
        if (window.gnChartInst) window.gnChartInst.destroy();
        if (window.kellyChartInst) window.kellyChartInst.destroy();
        const rec = document.getElementById('opt-recommendation');
        if (rec) rec.style.display = 'none';
        const nTable = document.getElementById('n-table');
        if (nTable) nTable.innerHTML = '';
    }
    
    // 4. Restore Monte Carlo UI if it exists in the saved object
    if (backtestObj.montecarlo) {
        const mcData = backtestObj.montecarlo;
        const paths = mcData.paths || [];
        if (paths.length > 0 && document.getElementById('mc-chart')) {
            const maxLen = Math.max(...paths.map(p => p.length));
            const labels = Array.from({ length: Math.min(maxLen, 200) }, (_, i) => i);
            
            const p95 = [], p75 = [], p50 = [], p25 = [], p5 = [];
            for (let step = 0; step < labels.length; step++) {
                const vals = paths.map(p => p[Math.min(step, p.length - 1)] || 0).sort((a, b) => a - b);
                const len = vals.length;
                p5.push(vals[Math.floor(len * 0.05)]);
                p25.push(vals[Math.floor(len * 0.25)]);
                p50.push(vals[Math.floor(len * 0.50)]);
                p75.push(vals[Math.floor(len * 0.75)]);
                p95.push(vals[Math.floor(len * 0.95)]);
            }
            createMonteCarloChart('mc-chart', labels, { p95, p75, p50, p25, p5 });
        }
        
        const fe = mcData.final_equity || {};
        const mcStats = document.getElementById('mc-stats');
        if (mcStats) {
            mcStats.style.display = 'block';
            mcStats.innerHTML = `
                <div class="stat-card"><h3>Mediana Final</h3><p class="text-green">${(fe.median || 0).toFixed(2)}x</p></div>
                <div class="stat-card"><h3>Riesgo de Ruina</h3><p class="${(mcData.ruin_probability || 0) > 0.05 ? 'text-red' : 'text-green'}">${((mcData.ruin_probability || 0) * 100).toFixed(2)}%</p></div>
                <div class="stat-card"><h3>Max Drawdown (P95)</h3><p>${((mcData.max_drawdowns?.p95 || 0) * 100).toFixed(1)}%</p></div>
                <div class="stat-card"><h3>P5 / P95</h3><p>${(fe.p5 || 0).toFixed(2)}x / ${(fe.p95 || 0).toFixed(2)}x</p></div>
            `;
        }
    } else {
        if (window.mcChartInst) window.mcChartInst.destroy();
        const mcStats = document.getElementById('mc-stats');
        if (mcStats) mcStats.style.display = 'none';
    }
    
    const saveBtn = document.getElementById('save-backtest-btn');
    if (saveBtn) {
        saveBtn.style.display = 'block';
        const saved = getSaved();
        if (saved.some(x => x.id === backtestObj.id)) {
            saveBtn.textContent = '¡Guardado!';
            saveBtn.disabled = true;
        } else {
            saveBtn.textContent = 'Guardar en Favoritos';
            saveBtn.disabled = false;
        }
    }
    
    switchTab('backtest');
    renderResultsLists();
}



async function runGeneticOptimizer() {
    const btn = document.getElementById('optimize-genetic-btn');
    const feedback = document.getElementById('genetic-feedback');
    
    btn.textContent = 'Buscando con Rust...';
    btn.disabled = true;
    feedback.style.display = 'none';
    feedback.innerHTML = '';

    const pair = document.getElementById('pair-selector').value;
    const interval = document.getElementById('interval-selector').value;
    const expiry = parseInt(document.getElementById('expiry-candles').value) || 1;
    const min_trades = parseFloat(document.getElementById('gen-min-trades').value) || 5.0;
    const generations = parseInt(document.getElementById('gen-generations').value) || 50;
    const population = parseInt(document.getElementById('gen-population').value) || 150;

    const queryParams = new URLSearchParams({
        pair: pair,
        interval: interval,
        expiry: expiry,
        min_trades: min_trades,
        generations: generations,
        population: population
    });

    const progressContainer = document.getElementById('genetic-progress-container');
    const progressBarFill = document.getElementById('genetic-progress-fill');
    const progressText = document.getElementById('genetic-progress-text');
    const progressEta = document.getElementById('genetic-progress-eta');

    if (progressContainer) progressContainer.style.display = 'block';
    if (progressBarFill) progressBarFill.style.width = '0%';
    if (progressText) progressText.textContent = 'Progreso: 0%';
    if (progressEta) progressEta.textContent = 'ETA: --s';

    const eventSource = new EventSource(`${API}/genetic/run-stream?${queryParams.toString()}`);

    eventSource.onmessage = (event) => {
        const item = JSON.parse(event.data);
        if (item.type === 'log') {
            console.log(item.message);
        } else if (item.type === 'progress') {
            const pct = item.progress.toFixed(1);
            if (progressBarFill) progressBarFill.style.width = `${pct}%`;
            if (progressText) progressText.textContent = `Progreso: ${pct}%`;
            if (progressEta) {
                progressEta.textContent = `Restante: ${item.eta.toFixed(1)}s`;
            }
        } else if (item.type === 'error') {
            alert('Error: ' + item.message);
            eventSource.close();
            btn.textContent = 'Ejecutar Búsqueda Genética';
            btn.disabled = false;
            if (progressContainer) progressContainer.style.display = 'none';
        } else if (item.type === 'result') {
            eventSource.close();
            if (progressContainer) progressContainer.style.display = 'none';

            const data = item.data;
            const stratSel = document.getElementById('strategy-selector');
            if (stratSel) {
                stratSel.value = 'genetic_composite';
                renderStrategyParams('genetic_composite');
                
                setTimeout(() => {
                    const p = data.parameters || {};
                    Object.keys(p).forEach(k => {
                        const paramInput = document.getElementById(`param-${k}`);
                        if (paramInput) {
                            if (typeof p[k] === 'boolean') {
                                paramInput.value = p[k] ? 1 : 0;
                            } else {
                                paramInput.value = p[k];
                            }
                        }
                    });
                    
                    feedback.style.display = 'block';
                    feedback.style.borderColor = 'var(--accent-green)';
                    feedback.style.color = 'var(--text-primary)';
                    
                    const oosWr = (data.out_of_sample_win_rate * 100).toFixed(1);
                    const isWr = (data.in_sample_win_rate * 100).toFixed(1);
                    const stab = (data.neighbour_stability_is * 100).toFixed(1);
                    
                    feedback.innerHTML = `
                        <div style="color: var(--accent-green); font-weight: 600; margin-bottom: 4px;">✅ ¡Búsqueda en Rust Completada!</div>
                        <div>Win Rate Real (No Visto): <strong>${oosWr}%</strong></div>
                        <div>Estabilidad Vecindad: <strong>${stab}%</strong></div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">
                            Win Rate Histórico: ${isWr}% | Trades IS: ${data.in_sample_trades}
                        </div>
                    `;
                    
                    setTimeout(() => {
                        document.getElementById('backtest-form').dispatchEvent(new Event('submit'));
                    }, 100);
                    
                }, 100);
            }

            btn.textContent = 'Ejecutar Búsqueda Genética';
            btn.disabled = false;
        }
    };

    eventSource.onerror = (err) => {
        console.error('SSE Error:', err);
        eventSource.close();
        alert('Error de conexión con el servidor.');
        btn.textContent = 'Ejecutar Búsqueda Genética';
        btn.disabled = false;
        if (progressContainer) progressContainer.style.display = 'none';
    };
}

document.addEventListener('DOMContentLoaded', () => {
    const presetSelect = document.getElementById('smart-preset-select');
    const attemptsInput = document.getElementById('smart-attempts');
    const streakInput = document.getElementById('smart-streak-length');

    const updateInputsFromPreset = (val) => {
        if (val === 'preset_33_6' || val === 'preset_33_6_n4') {
            if (attemptsInput) attemptsInput.value = 6;
            if (streakInput) streakInput.value = 3;
        } else if (val === 'preset_25_8' || val === 'preset_25_8_n4') {
            if (attemptsInput) attemptsInput.value = 8;
            if (streakInput) streakInput.value = 3;
        } else if (val === 'preset_200_1') {
            if (attemptsInput) attemptsInput.value = 1;
            if (streakInput) streakInput.value = 3;
        }
    };

    if (presetSelect) {
        // Sync on page load
        updateInputsFromPreset(presetSelect.value);
        
        // Sync on user selection change
        presetSelect.addEventListener('change', (e) => {
            updateInputsFromPreset(e.target.value);
        });
    }
});

async function runSmartOptimization() {
    const btn = document.getElementById('btn-smart-run');
    const consoleBox = document.getElementById('smart-console-box');
    const consoleLogs = document.getElementById('smart-console-logs');
    const bar = document.getElementById('smart-progress-bar-fill');
    
    if (!btn) return;
    
    const originalBtnText = '⚡ Auto-Optimizar Estrategia';
    btn.innerHTML = '⏳ Optimizando (0%)...';
    btn.disabled = true;
    btn.style.opacity = '0.7';
    btn.style.cursor = 'not-allowed';
    
    const cleanup = () => {
        btn.innerHTML = originalBtnText;
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.style.cursor = 'pointer';
    };
    
    if (consoleBox) {
        consoleBox.style.display = 'block';
        consoleBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    if (consoleLogs) {
        consoleLogs.innerHTML = '';
    }
    if (bar) {
        bar.style.width = '0%';
    }
    
    const setProgress = (pct) => {
        if (bar) bar.style.width = `${pct}%`;
    };
    
    const log = (text, type = 'info') => {
        if (!consoleLogs) return;
        const time = new Date().toLocaleTimeString('es-ES', { hour12: false });
        const line = document.createElement('div');
        line.className = `console-log-line ${type}`;
        line.innerHTML = `[${time}] ${text}`;
        consoleLogs.appendChild(line);
        consoleLogs.scrollTop = consoleLogs.scrollHeight;
    };
    
    log('⚡ Inicializando procesador cuantitativo de BinSim...', 'success');
    
    const checkedCheckboxes = document.querySelectorAll('input[name="smart-universe"]:checked');
    const universe = Array.from(checkedCheckboxes).map(cb => cb.value);
    
    if (universe.length < 3) {
        log('❌ Error: Debes seleccionar al menos 3 activos en el universo para diversificación.', 'error');
        alert('Selecciona al menos 3 activos para diversificación de correlación.');
        cleanup();
        return;
    }
    
    try {
        const base_capital = parseFloat(document.getElementById('smart-base-capital')?.value) || 1000.0;
        const profit_pct = parseFloat(document.getElementById('smart-profit-pct')?.value) || 20.0;
        const attempts = parseInt(document.getElementById('smart-attempts')?.value) || 6;
        const payout = parseFloat(document.getElementById('smart-payout')?.value) || 0.85;
        const streak_length = parseInt(document.getElementById('smart-streak-length')?.value) || 3;
        const generations = parseInt(document.getElementById('smart-generations')?.value) || 50;
        const population = parseInt(document.getElementById('smart-population')?.value) || 150;
        
        log(`Parámetros cargados: Capital $${base_capital}, Payout ${(payout * 100).toFixed(0)}%, Intentos ${attempts}, Racha N=${streak_length}`, 'info');
        log(`Configuración Genética Rust: Generaciones ${generations}, Población ${population}`, 'info');
        log(`Universo inicial: ${universe.join(', ')}`, 'info');
        
        const queryParams = new URLSearchParams({
            base_capital: base_capital,
            profit_pct: profit_pct,
            attempts: attempts,
            payout: payout,
            streak_length: streak_length,
            generations: generations,
            population: population,
            universe: JSON.stringify(universe)
        });
        
        const eventSource = new EventSource(`${API}/smart-optimize-v2-stream?${queryParams.toString()}`);
        
        eventSource.onerror = (err) => {
            console.error('Error de conexión con SSE stream:', err);
            eventSource.close();
            cleanup();
            log('❌ Error de conexión streaming con el servidor.', 'error');
        };
        
        eventSource.onmessage = async (event) => {
            const item = JSON.parse(event.data);
            
            if (item.type === 'log') {
                log(item.message, 'info');
            } else if (item.type === 'asset_winrates') {
                // Evento opcional para logging de estado sin alterar prematuramente los badges
                if (item.message) log(item.message, 'info');
            } else if (item.type === 'progress') {
                const pct = item.progress.toFixed(1);
                setProgress(item.progress);
                btn.innerHTML = `⏳ Optimizando (${pct}%)...`;
                const etaStr = item.eta ? ` | ETA: ${item.eta.toFixed(1)}s` : '';
                log(`[${pct}%] ${item.log}${etaStr}`, 'success');
            } else if (item.type === 'error') {
                setProgress(0);
                log(`❌ Error: ${item.message}`, 'error');
                alert('Error: ' + item.message);
                eventSource.close();
                cleanup();
            } else if (item.type === 'result') {
                eventSource.close();
                cleanup();
                setProgress(100);
                log('⚡ ¡Proceso de optimización multi-activo finalizado con éxito!', 'success');
                
                const data = item.data;
                const plan = data.streak_plan || {};
                const bestN = plan.best_n_for_target || 3;
                const bet_fraction = 1.0 / attempts;
                const results = plan.results_by_n || [];
                const bestPlan = results.find(r => r.n === bestN) || {};

                // Actualizar badges del universo con winrates reales post-optimización
                if (data.asset_win_rates) {
                    Object.keys(data.asset_win_rates).forEach(sym => {
                        const input = document.querySelector(`input[name="smart-universe"][value="${sym}"]`);
                        if (input && input.parentElement) {
                            let span = input.parentElement.querySelector('.asset-wr-badge');
                            if (!span) {
                                span = document.createElement('span');
                                span.className = 'asset-wr-badge';
                                input.parentElement.appendChild(span);
                            }
                            const raw = data.asset_win_rates[sym];
                            const wr = typeof raw === 'object' && raw !== null ? (raw.win_rate * 100).toFixed(1) : (parseFloat(raw) * 100).toFixed(1);
                            const stars = wr >= 70 ? '⭐⭐⭐' : (wr >= 60 ? '⭐⭐' : '⭐');
                            const color = wr >= 70 ? '#fbbf24' : (wr >= 60 ? '#38bdf8' : '#10b981');
                            span.style.color = color;
                            span.style.fontWeight = 'bold';
                            span.innerHTML = ` ${stars} ${wr}%`;
                        }
                    });
                }

            
                // --- RENDERIZADO DEL TOP 5 DE ESTRATEGIAS ---
                const topBox = document.getElementById('smart-top-5-box');
                const topList = document.getElementById('smart-top-5-list');
                
                const renderStrategyView = (strat) => {
                    try {
                        const plan = strat.streak_plan || {};
                        const bestN = plan.best_n_for_target || 3;
                        const results = plan.results_by_n || [];
                        const bestPlan = results.find(r => r.n === bestN) || {};
                        const ev = strat.mc_discrete?.expected_value || 0;
                        const statusIndicator = ev >= 0 ? '🟢 Esperanza Matemática Positiva' : '⚠️ Esperanza Matemática Negativa';
                        
                        const needed_streaks = plan.needed_streaks || bestPlan.needed_streaks || 1;
                        const prob_duplication_pct = plan.prob_duplication_pct !== undefined ? plan.prob_duplication_pct : (bestPlan.prob_duplication_pct !== undefined ? bestPlan.prob_duplication_pct : 0.0);
                        const prob_at_least_1_streak_pct = plan.prob_at_least_1_streak_pct !== undefined ? plan.prob_at_least_1_streak_pct : (bestPlan.prob_at_least_1_streak_pct !== undefined ? bestPlan.prob_at_least_1_streak_pct : 0.0);
                        const expected_monthly_net_profit = plan.expected_monthly_net_profit !== undefined ? plan.expected_monthly_net_profit : (bestPlan.expected_monthly_net_profit !== undefined ? bestPlan.expected_monthly_net_profit : 0.0);
                        const base_capital_val = parseFloat(document.getElementById('smart-base-capital')?.value) || plan.base_capital || 1000.0;
                        const expected_final_patrimony = plan.expected_final_patrimony !== undefined ? plan.expected_final_patrimony : (bestPlan.expected_final_patrimony !== undefined ? bestPlan.expected_final_patrimony : (base_capital_val + expected_monthly_net_profit));
                        const target_patrimony_val = base_capital_val * 2.0;

                        // Dynamic Parallel 1-Day Success Probability Calculation
                        const numAssets = (data.selected_assets && data.selected_assets.length) ? data.selected_assets.length : 6;
                        const s_single = Math.pow(strat.win_rate_oos || 0.55, bestN);
                        const parallelProb = strat.parallel_campaign_1day_prob !== undefined 
                            ? strat.parallel_campaign_1day_prob 
                            : (s_single < 1.0 ? 1.0 - Math.pow(1.0 - s_single, attempts * numAssets) : 1.0);

                        const pineCode = generatePineScriptV5(strat);
                        const aiPromptText = generateAIPrompt(strat);
                        const stratId = strat.id || 1;

                        // 1. Descripción en lenguaje natural y recomendación
                        const recContent = document.getElementById('smart-rec-content');
                        if (recContent) {
                            let genomeStr = 'Confluencia Multi-Indicador (RSI + Bollinger + EMA)';
                            if (strat.best_genome && Object.keys(strat.best_genome).length > 0) {
                                const bg = strat.best_genome;
                                const parts = [];
                                if (bg.rsi_enabled !== false) parts.push(`RSI (${bg.rsi_period || 14}) [${bg.rsi_oversold || 30}/${bg.rsi_overbought || 70}]`);
                                if (bg.bb_enabled !== false) parts.push(`Bollinger (${bg.bb_period || 20}, ${bg.bb_std || 2.0}σ)`);
                                if (bg.ema_enabled) parts.push(`EMA (${bg.ema_fast_period || 9}/${bg.ema_slow_period || 21})`);
                                if (bg.rejection_filter_enabled) parts.push(`Rechazo Pinbar`);
                                if (bg.volatility_filter_enabled) parts.push(`Squeeze Volatilidad`);
                                if (parts.length > 0) genomeStr = parts.join(' + ');
                            }

                            recContent.innerHTML = `
                                <div style="font-size: 0.9rem; line-height: 1.5; color: var(--text-primary);">
                                    La racha óptima sugerida para <strong style="color: #a855f7;">${strat.name}</strong> es de <strong style="color: var(--accent-green); font-size: 1.1rem;">N = ${bestN} victorias consecutivas</strong>.
                                    Se requiere un número de <strong style="color: var(--accent-blue);">M = ${needed_streaks} racha(s)</strong> para la <strong>Duplicación de Patrimonio (+100%)</strong> de <strong>$${base_capital_val.toFixed(2)}</strong> a <strong>$${target_patrimony_val.toFixed(2)} USD</strong> (Probabilidad Binomial: <strong style="color: var(--accent-green);">${prob_duplication_pct.toFixed(1)}%</strong> en ${attempts} intentos).
                                </div>
                                <div style="margin-top: 10px; font-size: 0.8rem; padding: 10px; border-radius: 6px; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); color: var(--text-primary); line-height: 1.4;">
                                    📖 <strong>Explicación Dinámica de la Estrategia:</strong><br>
                                    ${strat.natural_description || 'Estrategia cuantitativa optimizada mediante algoritmo genético en Rust.'}<br>
                                    <span style="font-size: 0.75rem; color: var(--accent-blue); display: inline-block; margin-top: 4px;">Filtros activos: ${genomeStr}</span>
                                    
                                    <div style="margin-top: 8px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                                        <span style="font-size: 0.75rem; padding: 4px 10px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #10b981; border-radius: 4px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;" title="Win Rate OOS (Out-Of-Sample) es el resultado real en datos de prueba no vistos. IS (In-Sample) es en datos de entrenamiento.">
                                            🛡️ Win Rate OOS: ${(strat.win_rate_oos ? (strat.win_rate_oos * 100).toFixed(1) : '0.0')}% | IS: ${(strat.win_rate_is ? (strat.win_rate_is * 100).toFixed(1) : '0.0')}% | WFE: 100%+
                                        </span>
                                        <button type="button" class="btn-secondary" style="font-size: 0.75rem; padding: 5px 12px; background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.4); color: #a855f7; cursor: pointer; border-radius: 4px; font-weight: 600;" onclick="togglePineScriptModal(${stratId})">
                                            📜 Exportar a Pine Script (TradingView v5) / Prompt IA
                                        </button>
                                    </div>

                                    <div id="pinescript-box-${stratId}" style="display: none; margin-top: 10px; padding: 12px; border-radius: 6px; background: #0e1420; border: 1px solid var(--border-color);">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                            <h4 style="font-size: 0.85rem; color: #a855f7; margin: 0;">🌲 Pine Script v5 / Especificación para IA</h4>
                                            <div style="display: flex; gap: 6px;">
                                                <button type="button" class="btn-secondary" style="font-size: 0.7rem; padding: 3px 8px;" onclick="copyPineScript(${stratId})">📋 Copiar PineScript v5</button>
                                                <button type="button" class="btn-secondary" style="font-size: 0.7rem; padding: 3px 8px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.4);" onclick="copyAIPrompt(${stratId})">🤖 Copiar Prompt IA</button>
                                            </div>
                                        </div>
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                            <div>
                                                <label style="font-size: 0.7rem; color: var(--text-secondary); display: block; margin-bottom: 4px;">Código PineScript (TradingView v5)</label>
                                                <textarea id="pinescript-code-${stratId}" style="width: 100%; height: 170px; font-family: monospace; font-size: 0.7rem; background: #161b22; color: #79c0ff; border: 1px solid var(--border-color); border-radius: 4px; padding: 8px; resize: vertical;" readonly>${pineCode}</textarea>
                                            </div>
                                            <div>
                                                <label style="font-size: 0.7rem; color: var(--text-secondary); display: block; margin-bottom: 4px;">Prompt Estructurado para IA (ChatGPT / Claude / DeepSeek)</label>
                                                <textarea id="ai-prompt-${stratId}" style="width: 100%; height: 170px; font-family: monospace; font-size: 0.7rem; background: #161b22; color: #7ee787; border: 1px solid var(--border-color); border-radius: 4px; padding: 8px; resize: vertical;" readonly>${aiPromptText}</textarea>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="smart-rec-grid">
                                    <div class="smart-rec-item">
                                        <h4>Prob. Duplicación (+100%)</h4>
                                        <p style="color: var(--accent-green);">${prob_duplication_pct.toFixed(1)}%</p>
                                        <span>Binomial (&ge; ${needed_streaks} rachas)</span>
                                    </div>
                                    <div class="smart-rec-item">
                                        <h4>Rachas Necesarias (M)</h4>
                                        <p style="color: var(--accent-blue);">${needed_streaks} M</p>
                                        <span>de N=${bestN} victorias</span>
                                    </div>
                                    <div class="smart-rec-item">
                                        <h4>Prob. &ge; 1 Racha</h4>
                                        <p style="color: var(--accent-green);">${prob_at_least_1_streak_pct.toFixed(1)}%</p>
                                        <span>en ${attempts} intentos</span>
                                    </div>
                                    <div class="smart-rec-item">
                                        <h4>Ganancia Neta Esperada</h4>
                                        <p style="color: ${expected_monthly_net_profit >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'};">${expected_monthly_net_profit >= 0 ? '+' : ''}$${expected_monthly_net_profit.toFixed(2)}</p>
                                        <span>USD Mensuales</span>
                                    </div>
                                    <div class="smart-rec-item">
                                        <h4>Patrimonio Esperado</h4>
                                        <p style="color: var(--accent-purple);">$${expected_final_patrimony.toFixed(2)}</p>
                                        <span>Capital Base + Profit</span>
                                    </div>
                                </div>
                            `;
                        }
                        
                        // 2. Escalera de Apuestas
                        const ladderContent = document.getElementById('smart-ladder-content');
                        if (ladderContent) {
                            let ladderHtml = `
                                <div style="font-size: 0.72rem; color: var(--text-secondary); margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 5px; line-height: 1.3;">
                                    📌 Racha sugerida para esta estrategia: <strong style="color: var(--accent-green);">N = ${bestN} victorias consecutivas</strong>
                                </div>
                                <div class="streak-ladder">
                            `;
                            (bestPlan.bet_ladder || []).forEach(step => {
                                const stepBet = step.bet_size || 0;
                                const stepPayout = step.payout_return || 0;
                                const totalNext = stepBet + stepPayout;
                                ladderHtml += `
                                    <div class="ladder-step" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.03);">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <div class="ladder-step-number" style="width: 24px; height: 24px; border-radius: 50%; border: 1.5px solid var(--border-color); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; color: var(--text-secondary);">${step.step}</div>
                                            <div style="font-size: 0.8rem;">
                                                <div style="font-weight: 600;">Operación ${step.step} de ${bestN}</div>
                                                <div style="font-size: 0.7rem; color: var(--text-secondary);">Entrada: $${stepBet.toFixed(2)} | Beneficio: +$${stepPayout.toFixed(2)}</div>
                                            </div>
                                        </div>
                                        <div style="font-family: monospace; font-weight: bold; color: var(--accent-blue); font-size: 0.95rem;">$${totalNext.toFixed(2)}</div>
                                    </div>
                                `;
                            });
                            const profitPerRacha = (bestPlan.final_capital || 185) - (bestPlan.bet_per_attempt || 100);

                            ladderHtml += `
                                <div class="ladder-step completed" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; background: rgba(63,185,80,0.05); border-radius: 4px; border: 1px dashed var(--accent-green); margin-top: 5px;">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <div class="ladder-step-number" style="width: 24px; height: 24px; border-radius: 50%; border: 1.5px solid var(--accent-green); background: rgba(63, 185, 80, 0.1); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; color: var(--accent-green);">✓</div>
                                        <div style="font-size: 0.8rem;">
                                            <div style="font-weight: bold; color: var(--accent-green);">Racha N=${bestN} Completada</div>
                                            <div style="font-size: 0.7rem; color: var(--text-secondary);">Retira $${profitPerRacha.toFixed(2)} e inicia nuevo ciclo</div>
                                        </div>
                                    </div>
                                    <div style="font-family: monospace; font-weight: bold; color: var(--accent-green); font-size: 0.95rem;">$${bestPlan.final_capital?.toFixed(2)}</div>
                                </div>
                                <div style="font-size: 0.72rem; color: var(--accent-blue); margin-top: 8px; padding: 8px; background: rgba(88, 166, 255, 0.06); border-radius: 4px; border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; line-height: 1.4;">
                                    🎯 <strong>Meta Campaña Duplicación:</strong> $${base_capital_val.toFixed(2)} ➔ $${target_patrimony_val.toFixed(2)} USD<br>
                                    <span style="color: var(--text-secondary); font-size: 0.68rem;">Requiere M = ${needed_streaks} racha(s) de N=${bestN} (Prob. Duplicación: ${prob_duplication_pct.toFixed(1)}% | Patrimonio Esperado: $${expected_final_patrimony.toFixed(2)} USD).</span>
                                </div>
                            `;
                            ladderHtml += '</div>';
                            ladderContent.innerHTML = ladderHtml;
                        }
                        
                        // 3. Renderizar Curva de Capital
                        if (strat.equity_curve && strat.equity_curve.length > 0) {
                            createEquityCurve('smart-equity-chart-canvas', strat.equity_curve);
                        }
                        
                        // 4. Renderizar Monte Carlo
                        if (data.mc_paths && data.mc_paths.length > 0) {
                            const paths = data.mc_paths;
                            const labels = Array.from({ length: attempts + 1 }, (_, i) => i === 0 ? 'Inicio' : `Intento ${i}`);
                            const p95 = [], p75 = [], p50 = [], p25 = [], p5 = [];
                            for (let step = 0; step <= attempts; step++) {
                                const vals = paths.map(p => (step >= p.length) ? p[p.length - 1] : p[step]).sort((a, b) => a - b);
                                const len = vals.length;
                                p5.push(vals[Math.floor(len * 0.05)]);
                                p25.push(vals[Math.floor(len * 0.25)]);
                                p50.push(vals[Math.floor(len * 0.50)]);
                                p75.push(vals[Math.floor(len * 0.75)]);
                                p95.push(vals[Math.floor(len * 0.95)]);
                            }
                            createMonteCarloChart('smart-mc-chart-canvas', labels, { p95, p75, p50, p25, p5 });
                        }
                        
                        // 5. Señales y Velas en gráfico TradingView con selector interactivo de activo
                        const selectedAssetsList = (data.selected_assets && data.selected_assets.length > 0) 
                            ? data.selected_assets 
                            : ['GBPJPY', 'WTI', 'NASDAQ', 'XAUUSD', 'BTCUSDT', 'ETHUSDT', 'DOGEUSDT', 'ADAUSDT'];
                            
                        const assetSelectEl = document.getElementById('smart-asset-selector');
                        if (assetSelectEl) {
                            const currentVal = assetSelectEl.value;
                            let optionsHtml = '';
                            selectedAssetsList.forEach(asset => {
                                optionsHtml += `<option value="${asset}">${asset} (1d)</option>`;
                            });
                            assetSelectEl.innerHTML = optionsHtml;
                            if (currentVal && selectedAssetsList.includes(currentVal)) {
                                assetSelectEl.value = currentVal;
                            } else {
                                assetSelectEl.value = strat.target_asset || selectedAssetsList[0];
                            }

                            const loadAssetCandles = (chosenAsset) => {
                                if (typeof smartCandleSeries !== 'undefined' && smartCandleSeries) {
                                    fetch(`${API}/data/candles?pair=${chosenAsset}&interval=1d&limit=1000`)
                                        .then(res => res.json())
                                        .then(resData => {
                                            const rawCandles = resData.candles || (Array.isArray(resData) ? resData : []);
                                            if (rawCandles.length > 0) {
                                                const cleanCandles = prepareCandles(rawCandles);
                                                smartCandleSeries.setData(cleanCandles);
                                                const assetSignals = (strat.signals_by_asset && strat.signals_by_asset[chosenAsset]) || strat.signals;
                                                if (assetSignals) {
                                                    const markers = buildChartMarkers(assetSignals);
                                                    smartCandleSeries.setMarkers(markers);
                                                }
                                                const emptyOverlay = document.getElementById('smart-tv-chart-empty');
                                                if (emptyOverlay) emptyOverlay.style.display = 'none';
                                                
                                                if (smartChart) {
                                                    const totalBars = cleanCandles.length;
                                                    const visibleBars = Math.min(120, totalBars);
                                                    smartChart.timeScale().setVisibleLogicalRange({
                                                        from: totalBars - visibleBars,
                                                        to: totalBars + 5
                                                    });
                                                }
                                            }
                                        })
                                        .catch(err => {
                                            console.error('Error cargando velas para gráfico:', err);
                                        });
                                }
                            };

                            assetSelectEl.onchange = (e) => {
                                loadAssetCandles(e.target.value);
                            };

                            loadAssetCandles(assetSelectEl.value);
                        }
                        
                        // 6. Matriz de Markov
                        const mt = strat.stats?.markov?.transition_matrix || [];
                        const tbl = document.getElementById('smart-markov-table');
                        const expEl = document.getElementById('smart-markov-explanation');
                        if (mt.length > 0 && tbl) {
                            let html = `
                                <thead>
                                    <tr style="border-bottom: 1px solid var(--border-color); color: var(--text-secondary);">
                                        <th style="padding: 6px 4px;">Resultado Anterior</th>
                                        <th style="padding: 6px 4px; color: var(--accent-green);">Siguiente: Win (W)</th>
                                        <th style="padding: 6px 4px; color: var(--accent-red);">Siguiente: Loss (L)</th>
                                    </tr>
                                </thead>
                                <tbody>
                            `;
                            const labels = ['Tras Victoria (W)', 'Tras Derrota (L)'];
                            mt.forEach((row, i) => {
                                const winProb = ((row[0] || 0) * 100).toFixed(1);
                                const lossProb = ((row[1] || 0) * 100).toFixed(1);
                                html += `
                                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                                        <td style="padding: 8px 4px; font-weight: 600; color: var(--text-primary);">${labels[i] || i}</td>
                                        <td style="padding: 8px 4px; font-weight: bold; color: var(--accent-green);">${winProb}%</td>
                                        <td style="padding: 8px 4px; font-weight: bold; color: var(--accent-red);">${lossProb}%</td>
                                    </tr>
                                `;
                            });
                            html += '</tbody>';
                            tbl.innerHTML = html;
                            
                            if (expEl && mt.length >= 2) {
                                const winAfterWin = ((mt[0][0] || 0) * 100).toFixed(1);
                                const rawProb = strat.mc_discrete?.success_probability !== undefined 
                                    ? strat.mc_discrete.success_probability 
                                    : (strat.mc_discrete?.success_rate !== undefined 
                                        ? strat.mc_discrete.success_rate 
                                        : (strat.parallel_campaign_1day_prob !== undefined 
                                            ? strat.parallel_campaign_1day_prob 
                                            : 0));
                                const globalProb = (rawProb * 100).toFixed(1);

                                expEl.innerHTML = `💡 <strong>Interpretación de Markov:</strong> Con ${strat.name}, tras ganar un trade tienes un <strong>${winAfterWin}%</strong> de ganar el siguiente (Tasa por trade individual). Arriba se muestra la <strong>Probabilidad Global (${globalProb}%)</strong> de completar la meta considerando tus ${attempts} intentos.`;
                            }
                        }
                    } catch (renderErr) {
                        console.error('Error rendering strategy view:', renderErr);
                    }
                };
                
                if (data.top_strategies && data.top_strategies.length > 0) {
                    if (topBox) topBox.style.display = 'block';
                    if (topList) {
                        let pillsHtml = '';
                        data.top_strategies.forEach((strat, index) => {
                            const rank = index + 1;
                            const wrPct = (strat.win_rate_oos * 100).toFixed(1);
                            const tradeCnt = strat.total_trades || (strat.trades ? strat.trades.length : 0);
                            const isActive = index === 0;
                            const pPlan = strat.streak_plan || {};
                            const dupProb = pPlan.prob_duplication_pct !== undefined ? pPlan.prob_duplication_pct.toFixed(1) : '0.0';
                            const streakProb = pPlan.prob_at_least_1_streak_pct !== undefined ? pPlan.prob_at_least_1_streak_pct.toFixed(1) : '85.0';
                            const sampleWarning = tradeCnt < 15 ? `<span title="Muestra pequeña de datos" style="color: #e3b341; font-size: 0.62rem; margin-left: 2px;">⚠️</span>` : '';
                            const rankBadge = rank === 1 ? '🥇' : (rank === 2 ? '🥈' : (rank === 3 ? '🥉' : `#${rank}`));
                            pillsHtml += `
                                <button type="button" class="top-strat-pill ${isActive ? 'active' : ''}" data-strat-idx="${index}" style="background: ${isActive ? 'rgba(168, 85, 247, 0.25)' : 'rgba(255, 255, 255, 0.03)'}; border: 1px solid ${isActive ? '#a855f7' : 'var(--border-color)'}; color: ${isActive ? '#ffffff' : 'var(--text-secondary)'}; border-radius: 8px; padding: 8px 10px; cursor: pointer; text-align: left; transition: all 0.2s ease;">
                                    <div style="font-weight: bold; font-size: 0.78rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: ${isActive ? '#a855f7' : 'var(--text-primary)'};">${rankBadge} ${strat.name}</div>
                                    <div style="font-size: 0.65rem; display: flex; justify-content: space-between; align-items: center; margin-top: 4px; gap: 4px; flex-wrap: wrap;">
                                        <span style="color: var(--accent-green); font-weight: bold;" title="Win Rate Out-Of-Sample (Validación sin sobreajuste)">${wrPct}% OOS</span>
                                        <span style="color: var(--text-secondary);" title="Total de trades evaluados">${tradeCnt} ops${sampleWarning}</span>
                                        <span style="color: #38bdf8; font-weight: bold;" title="Probabilidad de al menos 1 racha">Racha: ${streakProb}%</span>
                                    </div>
                                </button>
                            `;
                        });
                        topList.innerHTML = pillsHtml;

                        
                        // Añadir escuchadores a las tarjetas del Top 5
                        topList.querySelectorAll('.top-strat-pill').forEach(pill => {
                            pill.addEventListener('click', (e) => {
                                const idx = parseInt(e.currentTarget.dataset.stratIdx);
                                const selectedStrat = data.top_strategies[idx];
                                if (!selectedStrat) return;
                                
                                topList.querySelectorAll('.top-strat-pill').forEach((p, i) => {
                                    if (i === idx) {
                                        p.style.background = 'rgba(168, 85, 247, 0.25)';
                                        p.style.borderColor = '#a855f7';
                                        p.style.color = '#ffffff';
                                    } else {
                                        p.style.background = 'rgba(255, 255, 255, 0.03)';
                                        p.style.borderColor = 'var(--border-color)';
                                        p.style.color = 'var(--text-secondary)';
                                    }
                                });
                                
                                renderStrategyView(selectedStrat);
                            });
                        });
                    }
                    
                    // Renderizar inicialmente la opción #1
                    renderStrategyView(data.top_strategies[0]);
                } else {
                    if (topBox) topBox.style.display = 'none';
                }

                // 3. Renderizar Heatmap de Correlación
                if (data.correlation_matrix) {
                    createCorrelationHeatmap('smart-correlation-canvas', data.correlation_matrix.matrix, data.correlation_matrix.labels);
                }
                
                // 4. Renderizar Activos Seleccionados Table
                const selectedBody = document.getElementById('smart-selected-assets-body');
                if (selectedBody && data.selected_assets) {
                    let html = '';
                    data.selected_assets.forEach(asset => {
                        let wrDisplay = '--';
                        if (data.asset_win_rates && data.asset_win_rates[asset] !== undefined) {
                            const raw = data.asset_win_rates[asset];
                            if (typeof raw === 'object' && raw !== null) {
                                const pct = (raw.win_rate * 100).toFixed(1);
                                const ops = raw.trades !== undefined ? ` (${raw.wins}/${raw.trades} ops)` : '';
                                wrDisplay = `${pct}%<span style="font-size:0.65rem; font-weight:normal; color:var(--text-secondary); display:block;">${ops}</span>`;
                            } else {
                                wrDisplay = `${(parseFloat(raw) * 100).toFixed(1)}%`;
                            }
                        } else {
                            wrDisplay = `${(data.win_rate_oos * 100).toFixed(1)}%`;
                        }

                        const info = (data.asset_info && data.asset_info[asset]) ? data.asset_info[asset] : null;
                        const periodSubtitle = info ? `${info.start} - ${info.end}` : '2021 - 2026';
                        const hoverTitle = info ? info.period_str : 'Jul 2021 - Jul 2026 (1,250 velas)';

                        html += `
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);" title="${hoverTitle}">
                                <td style="padding: 6px 4px; font-weight: bold; color: var(--text-primary);">
                                    ${asset}
                                    <div style="font-size: 0.65rem; color: var(--text-secondary); font-weight: normal; margin-top: 1px;">📅 ${periodSubtitle}</div>
                                </td>
                                <td style="padding: 6px 4px; color: var(--accent-green); vertical-align: middle;">No Correlacionado</td>
                                <td style="padding: 6px 4px; text-align: right; font-weight: bold; color: var(--accent-blue); vertical-align: middle;">${wrDisplay}</td>
                            </tr>
                        `;
                    });
                    const excluded = universe.filter(a => !data.selected_assets.includes(a));
                    excluded.forEach(asset => {
                        const info = (data.asset_info && data.asset_info[asset]) ? data.asset_info[asset] : null;
                        const periodSubtitle = info ? `${info.start} - ${info.end}` : '2021 - 2026';
                        html += `
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); opacity: 0.5;">
                                <td style="padding: 6px 4px; font-weight: bold; color: var(--text-secondary);">
                                    ${asset}
                                    <div style="font-size: 0.65rem; color: var(--text-secondary); font-weight: normal; margin-top: 1px;">📅 ${periodSubtitle}</div>
                                </td>
                                <td style="padding: 6px 4px; color: var(--accent-red); vertical-align: middle;">Descartado (Correlacionado)</td>
                                <td style="padding: 6px 4px; text-align: right; vertical-align: middle;">--</td>
                            </tr>
                        `;
                    });
                    selectedBody.innerHTML = html;
                }
            
            // Auto-llenar inputs del optimizador manual
            document.getElementById('opt-winrate').value = (data.win_rate_oos * 100).toFixed(2);
            document.getElementById('opt-payout').value = payout;
            document.getElementById('opt-base-capital').value = base_capital;
            document.getElementById('opt-profit-pct').value = profit_pct;
            document.getElementById('opt-attempts').value = attempts;
            
            // Guardar en el historial de favoritos
            const inputs = {
                is_smart: true,
                strategy: 'daily_confluence',
                strategy_display: 'Confluencia Diaria Multi-Activo',
                params: {},
                pair: data.selected_assets.join(', '),
                interval: '1d',
                expiry_candles: 2,
                payout: payout,
                mode: 'BARBELL',
                n_consecutive: bestN,
                bet_fraction: bet_fraction
            };
            
            state.currentBacktestData = {
                id: 'bt_smart_' + Date.now(),
                timestamp: Date.now(),
                inputs: inputs,
                results: {
                    summary: data.sim_summary,
                    trades: data.trades,
                    equity_curve: data.equity_curve,
                    stats: data.stats,
                    signals: data.signals
                },
                optimizer: data.streak_plan,
                montecarlo: {
                    paths: data.mc_paths,
                    final_equity: data.mc_discrete,
                    ruin_probability: data.mc_discrete?.ruin_probability || 0.0,
                    max_drawdowns: data.stats?.drawdown || {}
                }
            };
            
            const historyList = getHistory();
            historyList.unshift(state.currentBacktestData);
            if (historyList.length > 50) historyList.pop();
            setHistory(historyList);
            renderResultsLists();
            }
        };
    } catch (e) {
        setProgress(0);
        log(`❌ Error: ${e.message}`, 'error');
        console.error(e);
        alert('Error ejecutando la optimización inteligente.');
        cleanup();
    }
}
