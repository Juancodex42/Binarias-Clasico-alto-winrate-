// charts.js - Binary Options Quantitative Terminal Charting Engine (Milestone 3)

// Default Chart.js defaults
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
if (Chart.defaults.plugins && Chart.defaults.plugins.tooltip) {
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(20, 29, 46, 0.95)';
    Chart.defaults.plugins.tooltip.titleColor = '#f0f6fc';
    Chart.defaults.plugins.tooltip.bodyColor = '#94a3b8';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.08)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
    Chart.defaults.plugins.tooltip.titleFont = { size: 11, weight: '600', family: "'JetBrains Mono', monospace" };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 11, family: "'JetBrains Mono', monospace" };
}

function createCandlestickChart(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return null;

    const chart = LightweightCharts.createChart(el, {
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#94a3b8',
            fontSize: 12,
            fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        },
        grid: {
            vertLines: { color: 'rgba(255, 255, 255, 0.03)' },
            horzLines: { color: 'rgba(255, 255, 255, 0.03)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                color: 'rgba(56, 189, 248, 0.4)',
                style: 3,
                labelBackgroundColor: '#141d2e',
            },
            horzLine: {
                color: 'rgba(56, 189, 248, 0.4)',
                style: 3,
                labelBackgroundColor: '#141d2e',
            },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: 'rgba(255, 255, 255, 0.07)',
            rightOffset: 10,
            barSpacing: 10,
            minBarSpacing: 0.5,
            autoScale: true,
            shiftVisibleRangeOnNewBar: true,
        },
        rightPriceScale: {
            borderColor: 'rgba(255, 255, 255, 0.07)',
            autoScale: true,
            scaleMargins: {
                top: 0.1,
                bottom: 0.1,
            },
        },
        handleScroll: {
            mouseWheel: true,
            pressedMove: true,
            horzTouchDrag: true,
            vertTouchDrag: true,
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
        },
    });

    const candleSeries = chart.addCandlestickSeries({
        upColor: '#10b981',
        downColor: '#f43f5e',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#f43f5e',
        priceFormat: {
            type: 'price',
            precision: 5,
            minMove: 0.00001,
        },
    });

    return { chart, candleSeries };
}

function updateCandlestickChart(series, candle) {
    if (series && candle) {
        try {
            series.update(candle);
        } catch (e) {
            console.warn('[Chart] Error updating candlestick:', e);
        }
    }
}

function addSignalMarkers(series, signals) {
    if (!series || !signals) return;
    if (typeof buildChartMarkers === 'function') {
        const markers = buildChartMarkers(signals);
        series.setMarkers(markers);
        return;
    }
    const markers = signals.map(signal => {
        const dir = signal.direction || signal.type;
        return {
            time: signal.time,
            position: dir === 'CALL' ? 'belowBar' : 'aboveBar',
            color: dir === 'CALL' ? '#10b981' : '#f43f5e',
            shape: dir === 'CALL' ? 'arrowUp' : 'arrowDown',
            text: dir
        };
    });
    series.setMarkers(markers);
}

function formatYAxisTick(value, useLog) {
    if (value === 0) return '$0.00';
    const absVal = Math.abs(value);
    
    if (useLog) {
        // Filter out intermediate sub-ticks (like 5, 50, 500, 5000) so labels don't collide vertically
        const log10 = Math.log10(absVal);
        if (Math.abs(log10 - Math.round(log10)) > 1e-4) {
            return null;
        }
    }
    
    const prefix = value < 0 ? '-$' : '$';
    if (absVal >= 1000000) {
        return prefix + (absVal / 1000000).toFixed(absVal % 1000000 === 0 ? 0 : 1) + 'M';
    }
    if (absVal >= 1000) {
        return prefix + (absVal / 1000).toFixed(absVal % 1000 === 0 ? 0 : 1) + 'k';
    }
    if (absVal >= 1) {
        return prefix + (absVal % 1 === 0 ? absVal.toFixed(0) : absVal.toFixed(2));
    }
    return prefix + absVal.toFixed(2);
}

function createEquityCurve(canvasId, equityPoints, rawLabels) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    const ctx = el.getContext('2d');
    
    // Destroy previous if exists
    if (window[canvasId + 'Inst']) window[canvasId + 'Inst'].destroy();
    
    let values = [];
    let labels = [];
    
    if (Array.isArray(equityPoints) && equityPoints.length > 0 && typeof equityPoints[0] === 'object' && equityPoints[0] !== null) {
        values = equityPoints.map(e => e.equity !== undefined ? e.equity : (e.y !== undefined ? e.y : 0));
        labels = equityPoints.map((e, i) => {
            if (e.time) {
                const d = new Date(e.time < 2e9 ? e.time * 1000 : e.time);
                const year = d.getFullYear();
                const month = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                const hours = String(d.getHours()).padStart(2, '0');
                const minutes = String(d.getMinutes()).padStart(2, '0');
                if (hours !== '00' || minutes !== '00') {
                    return `${year}-${month}-${day} ${hours}:${minutes}`;
                }
                return `${year}-${month}-${day}`;
            }
            return `#${i + 1}`;
        });
    } else {
        values = equityPoints || [];
        if (rawLabels && rawLabels.length === values.length) {
            labels = rawLabels;
        } else {
            labels = values.map((_, i) => `#${i + 1}`);
        }
    }
    
    const maxVal = values.length > 0 ? Math.max(...values) : 1000;
    const minVal = values.length > 0 ? Math.min(...values) : 0;
    
    // Switch to logarithmic scale only if values span >100x AND minVal >= 1.0
    const useLog = (maxVal / Math.max(minVal, 0.01)) > 100 && minVal >= 1.0;
    const cleanedData = useLog ? values.map(v => Math.max(v, 1.0)) : values;
    
    window[canvasId + 'Inst'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Capital',
                data: cleanedData,
                borderColor: '#38bdf8',
                backgroundColor: function(context) {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;
                    if (!chartArea) {
                        return 'rgba(56, 189, 248, 0.12)';
                    }
                    const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                    gradient.addColorStop(0, 'rgba(56, 189, 248, 0.22)');
                    gradient.addColorStop(1, 'rgba(56, 189, 248, 0.00)');
                    return gradient;
                },
                borderWidth: 2,
                fill: true,
                tension: 0.15,
                pointRadius: 0,
                pointHoverRadius: 4,
                pointHoverBackgroundColor: '#38bdf8',
                pointHoverBorderColor: '#ffffff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: { 
                    display: true,
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: {
                        color: '#94a3b8',
                        maxTicksLimit: 8,
                        font: { size: 10, family: "'Inter', sans-serif" }
                    },
                    title: {
                        display: true,
                        text: 'Línea de Tiempo (Fechas / Histórico)',
                        color: '#94a3b8',
                        font: { size: 10, weight: '500', family: "'Inter', sans-serif" }
                    }
                },
                y: {
                    type: useLog ? 'logarithmic' : 'linear',
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    min: useLog ? Math.max(1, Math.pow(10, Math.floor(Math.log10(Math.max(minVal, 1))))) : undefined,
                    ticks: {
                        color: '#94a3b8',
                        maxTicksLimit: 6,
                        font: { size: 10, family: "'JetBrains Mono', monospace" },
                        callback: function(value) {
                            return formatYAxisTick(value, useLog);
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(20, 29, 46, 0.95)',
                    titleColor: '#f0f6fc',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 6,
                    titleFont: { size: 11, weight: '600', family: "'JetBrains Mono', monospace" },
                    bodyFont: { size: 11, family: "'JetBrains Mono', monospace" },
                    callbacks: {
                        title: function(items) {
                            if (!items || !items.length) return '';
                            const idx = items[0].dataIndex;
                            const label = items[0].label;
                            return `Op. #${idx + 1} (${label})`;
                        },
                        label: function(context) {
                            const val = Number(context.raw);
                            return `Capital Acumulado: $${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                        }
                    }
                }
            }
        }
    });
}

function createBarChart(canvasId, labels, values, title, color = '#38bdf8') {
    const el = document.getElementById(canvasId);
    if (!el) return;
    const ctx = el.getContext('2d');
    if (window[canvasId + 'Inst']) window[canvasId + 'Inst'].destroy();
    
    const bgColors = Array.isArray(color) ? color : color;

    window[canvasId + 'Inst'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: values,
                backgroundColor: bgColors,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(20, 29, 46, 0.95)',
                    titleColor: '#f0f6fc',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 6,
                    titleFont: { size: 11, weight: '600', family: "'JetBrains Mono', monospace" },
                    bodyFont: { size: 11, family: "'JetBrains Mono', monospace" }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#94a3b8', font: { size: 10, family: "'Inter', sans-serif" } }
                },
                y: { 
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#94a3b8', font: { size: 10, family: "'JetBrains Mono', monospace" } }
                }
            }
        }
    });
}

function createGrowthRateChart(canvasId, ns, g_values, optimal_n) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    const ctx = el.getContext('2d');
    if (window.gnChartInst) window.gnChartInst.destroy();
    if (window[canvasId + 'Inst']) window[canvasId + 'Inst'].destroy();
    
    const colors = ns.map(n => n === optimal_n ? '#10b981' : '#38bdf8');
    
    const inst = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ns,
            datasets: [{
                label: 'G(N)',
                data: g_values,
                backgroundColor: colors,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(20, 29, 46, 0.95)',
                    titleColor: '#f0f6fc',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 6,
                    titleFont: { size: 11, weight: '600', family: "'JetBrains Mono', monospace" },
                    bodyFont: { size: 11, family: "'JetBrains Mono', monospace" },
                    callbacks: {
                        label: function(context) {
                            return `G(${context.label}): ${Number(context.raw).toFixed(4)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#94a3b8', font: { size: 10, family: "'Inter', sans-serif" } }
                },
                y: { 
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#94a3b8', font: { size: 10, family: "'JetBrains Mono', monospace" } }
                }
            }
        }
    });

    window.gnChartInst = inst;
    window[canvasId + 'Inst'] = inst;
}

function createMonteCarloChart(canvasId, labels, percentiles, initialCapital) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    const ctx = el.getContext('2d');
    if (window.mcChartInst) window.mcChartInst.destroy();
    if (window[canvasId + 'Inst']) window[canvasId + 'Inst'].destroy();
    
    // Clean arrays to avoid log(0) which stretches scale to -infinity
    const clean = arr => (arr || []).map(v => v <= 0.01 ? 0.01 : v);
    
    const p95_clean = clean(percentiles?.p95);
    const p75_clean = clean(percentiles?.p75);
    const p50_clean = clean(percentiles?.p50);
    const p25_clean = clean(percentiles?.p25);
    const p5_clean = clean(percentiles?.p5);
    
    // Determine whether to use log scale or linear scale
    const allValues = [...p95_clean, ...p75_clean, ...p50_clean, ...p25_clean, ...p5_clean];
    const maxVal = allValues.length > 0 ? Math.max(...allValues) : 1000;
    const minVal = allValues.length > 0 ? Math.min(...allValues) : 1;
    const useLog = (maxVal / (minVal || 1)) > 50 && minVal > 0.01;
    
    const datasets = [
        {
            label: 'P95 (Top 5%)',
            data: p95_clean,
            borderColor: 'rgba(16, 185, 129, 0.85)',
            borderDash: [5, 5],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false
        },
        {
            label: 'P75 (Cuartil Superior)',
            data: p75_clean,
            borderColor: 'rgba(16, 185, 129, 0.45)',
            borderWidth: 1,
            pointRadius: 0,
            fill: '+1',
            backgroundColor: 'rgba(16, 185, 129, 0.05)'
        },
        {
            label: 'Mediana (P50)',
            data: p50_clean,
            borderColor: '#38bdf8',
            borderWidth: 2.5,
            pointRadius: 0,
            fill: false
        },
        {
            label: 'P25 (Cuartil Inferior)',
            data: p25_clean,
            borderColor: 'rgba(244, 63, 94, 0.45)',
            borderWidth: 1,
            pointRadius: 0,
            fill: '+1',
            backgroundColor: 'rgba(244, 63, 94, 0.05)'
        },
        {
            label: 'P5 (Riesgo Cola 5%)',
            data: p5_clean,
            borderColor: 'rgba(244, 63, 94, 0.85)',
            borderDash: [5, 5],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false
        }
    ];

    // Add baseline for initial capital if provided or inferred
    const initCap = initialCapital || (p50_clean.length > 0 ? p50_clean[0] : null);
    if (initCap !== null && labels && labels.length > 0) {
        datasets.push({
            label: 'Capital Inicial',
            data: Array(labels.length).fill(initCap),
            borderColor: 'rgba(255, 255, 255, 0.25)',
            borderDash: [6, 6],
            borderWidth: 1,
            pointRadius: 0,
            fill: false
        });
    }

    const inst = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: { 
                    display: true,
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: {
                        color: '#94a3b8',
                        maxTicksLimit: 8,
                        font: { size: 10, family: "'Inter', sans-serif" }
                    }
                },
                y: { 
                    type: useLog ? 'logarithmic' : 'linear', 
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    min: useLog ? Math.max(1, Math.pow(10, Math.floor(Math.log10(Math.max(minVal, 1))))) : undefined,
                    ticks: {
                        color: '#94a3b8',
                        maxTicksLimit: 6,
                        font: { size: 10, family: "'JetBrains Mono', monospace" },
                        callback: function(value) {
                            return formatYAxisTick(value, useLog);
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 10, family: "'Inter', sans-serif" },
                        boxWidth: 12,
                        padding: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(20, 29, 46, 0.95)',
                    titleColor: '#f0f6fc',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 6,
                    titleFont: { size: 11, weight: '600', family: "'JetBrains Mono', monospace" },
                    bodyFont: { size: 11, family: "'JetBrains Mono', monospace" },
                    callbacks: {
                        label: function(context) {
                            const val = Number(context.raw);
                            return `${context.dataset.label}: $${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                        }
                    }
                }
            }
        }
    });

    window.mcChartInst = inst;
    window[canvasId + 'Inst'] = inst;
}

function createCorrelationHeatmap(canvasId, matrix, labels) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const parent = canvas.parentElement;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    
    // Store data on canvas for re-renders on resize
    canvas._lastMatrix = matrix;
    canvas._lastLabels = labels;
    
    // Sizing
    const width = parent ? parent.clientWidth : (canvas.clientWidth || 400);
    const height = parent ? parent.clientHeight : (canvas.clientHeight || 280);
    
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    canvas.width = (width || 400) * dpr;
    canvas.height = (height || 280) * dpr;
    ctx.scale(dpr, dpr);
    
    const w = width || 400;
    const h = height || 280;
    
    ctx.clearRect(0, 0, w, h);
    
    if (!matrix || matrix.length === 0 || !labels || labels.length === 0) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '13px "Inter", sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Sin datos de correlación', w / 2, h / 2);
        return;
    }
    
    const n = Math.min(matrix.length, labels.length);
    const leftMargin = 70;
    const topMargin = 15;
    const rightMargin = 15;
    const bottomMargin = 35;
    
    const gridW = Math.max(100, w - leftMargin - rightMargin);
    const gridH = Math.max(100, h - topMargin - bottomMargin);
    
    const cellW = gridW / n;
    const cellH = gridH / n;
    
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            const val = (matrix[i] && matrix[i][j] !== undefined) ? matrix[i][j] : null;
            let colorStr = 'rgba(20, 29, 46, 0.95)';

            if (val !== null && val !== undefined && !isNaN(val)) {
                if (val >= 0) {
                    // Positive correlation: interpolate from base dark (#141d2e -> 20, 29, 46) to Rose Crimson (#f43f5e -> 244, 63, 94)
                    const intensity = Math.pow(Math.abs(val), 1.2);
                    const r = Math.round(20 + intensity * (244 - 20));
                    const g = Math.round(29 + intensity * (63 - 29));
                    const b = Math.round(46 + intensity * (94 - 46));
                    colorStr = `rgb(${r}, ${g}, ${b})`;
                } else {
                    // Negative correlation: interpolate from base dark (#141d2e -> 20, 29, 46) to Electric Sky (#38bdf8 -> 56, 189, 248)
                    const intensity = Math.pow(Math.abs(val), 1.2);
                    const r = Math.round(20 + intensity * (56 - 20));
                    const g = Math.round(29 + intensity * (189 - 29));
                    const b = Math.round(46 + intensity * (248 - 46));
                    colorStr = `rgb(${r}, ${g}, ${b})`;
                }
            }
            
            ctx.fillStyle = colorStr;
            const cellX = leftMargin + j * cellW;
            const cellY = topMargin + i * cellH;
            const cellWidth = cellW - 1.5;
            const cellHeight = cellH - 1.5;

            // Draw rounded cell rect if supported, else standard fillRect
            if (typeof ctx.roundRect === 'function') {
                ctx.beginPath();
                ctx.roundRect(cellX, cellY, cellWidth, cellHeight, 3);
                ctx.fill();
            } else {
                ctx.fillRect(cellX, cellY, cellWidth, cellHeight);
            }
            
            if (cellW > 18 && cellH > 14 && val !== null && val !== undefined && !isNaN(val)) {
                ctx.fillStyle = Math.abs(val) > 0.4 ? '#f0f6fc' : '#94a3b8';
                const fontSize = Math.min(11, Math.max(8, Math.floor(cellH * 0.45)));
                ctx.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(val.toFixed(2), cellX + cellW / 2, cellY + cellH / 2);
            }
        }
    }
    
    const labelFontSize = Math.min(11, Math.max(8, Math.floor(cellH * 0.45)));
    ctx.fillStyle = '#94a3b8';
    ctx.font = `bold ${labelFontSize}px "Inter", sans-serif`;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i < n; i++) {
        let label = labels[i].replace('USDT', '').replace('=X', '');
        ctx.fillText(label, leftMargin - 6, topMargin + i * cellH + cellH / 2);
    }
    
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    for (let j = 0; j < n; j++) {
        let label = labels[j].replace('USDT', '').replace('=X', '');
        ctx.fillText(label, leftMargin + j * cellW + cellW / 2, h - bottomMargin + 6);
    }
}

function renderDiagnosticsCharts(statsData) {
    if (!statsData) return;
    
    // Autocorrelation
    const ac = statsData.dependency?.autocorrelation || [];
    if (ac.length > 0 && document.getElementById('autocorr-chart')) {
        const labels = ac.map((_, i) => `Lag ${i + 1}`);
        const colors = ac.map(v => v >= 0 ? '#a855f7' : '#f43f5e');
        createBarChart('autocorr-chart', labels, ac, 'Autocorrelación', colors);
    }

    // Streak distribution
    const sd = statsData.streaks?.streak_distribution || {};
    if (Object.keys(sd).length > 0 && document.getElementById('streaks-chart')) {
        const sortedKeys = Object.keys(sd).map(Number).sort((a, b) => a - b);
        createBarChart('streaks-chart', sortedKeys.map(String), sortedKeys.map(k => sd[k]), 'Frecuencia de Rachas', '#38bdf8');
    }

    // Win rate by hour
    const bh = statsData.temporal?.by_hour || {};
    if (Object.keys(bh).length > 0 && document.getElementById('hourly-chart')) {
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

    // Market state
    const ms = statsData.market_state || {};
    if (Object.values(ms).some(v => v > 0) && document.getElementById('market-state-chart')) {
        createBarChart('market-state-chart',
            ['Alta Vol', 'Baja Vol', 'Tendencia', 'Rango'],
            [ms.high_vol_wr || 0, ms.low_vol_wr || 0, ms.trending_wr || 0, ms.ranging_wr || 0],
            'Win Rate por Régimen',
            ['#f59e0b', '#38bdf8', '#10b981', '#a855f7']
        );
    }
}

// Global window export aliases
window.createCandlestickChart = createCandlestickChart;
window.initLightweightChart = createCandlestickChart;
window.updateCandlestickChart = updateCandlestickChart;
window.addSignalMarkers = addSignalMarkers;
window.formatYAxisTick = formatYAxisTick;
window.createEquityCurve = createEquityCurve;
window.renderEquityCurve = createEquityCurve;
window.createBarChart = createBarChart;
window.createGrowthRateChart = createGrowthRateChart;
window.createMonteCarloChart = createMonteCarloChart;
window.renderMonteCarloCones = createMonteCarloChart;
window.createCorrelationHeatmap = createCorrelationHeatmap;
window.renderCorrelationHeatmap = createCorrelationHeatmap;
window.renderDiagnosticsCharts = renderDiagnosticsCharts;

