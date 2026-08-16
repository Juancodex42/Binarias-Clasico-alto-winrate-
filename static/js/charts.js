// charts.js
// Default Chart.js defaults
Chart.defaults.color = '#8b949e';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(22, 27, 34, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#c9d1d9';
Chart.defaults.plugins.tooltip.bodyColor = '#c9d1d9';
Chart.defaults.plugins.tooltip.borderColor = '#30363d';
Chart.defaults.plugins.tooltip.borderWidth = 1;

function createCandlestickChart(containerId) {
    const el = document.getElementById(containerId);
    const chart = LightweightCharts.createChart(el, {
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#8b949e',
            fontSize: 12,
            fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        },
        grid: {
            vertLines: { color: 'rgba(48, 54, 61, 0.3)' },
            horzLines: { color: 'rgba(48, 54, 61, 0.3)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: '#30363d',
            rightOffset: 10,
            barSpacing: 10,
            minBarSpacing: 0.5,
            autoScale: true,
            shiftVisibleRangeOnNewBar: true,
        },
        rightPriceScale: {
            borderColor: '#30363d',
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
        upColor: '#00f5a0',
        downColor: '#ff4d4d',
        borderVisible: false,
        wickUpColor: '#00f5a0',
        wickDownColor: '#ff4d4d',
        priceFormat: {
            type: 'price',
            precision: 5,
            minMove: 0.00001,
        },
    });

    return { chart, candleSeries };
}

function addSignalMarkers(series, signals) {
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
            color: dir === 'CALL' ? '#00f5a0' : '#ff4d4d',
            shape: dir === 'CALL' ? 'arrowUp' : 'arrowDown',
            text: dir
        };
    });
    series.setMarkers(markers);
}


function formatYAxisTick(value, useLog) {
    if (value === 0) return '$0';
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
        return prefix + (absVal % 1 === 0 ? absVal.toFixed(0) : absVal.toFixed(1));
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
                borderColor: '#58a6ff',
                backgroundColor: 'rgba(88, 166, 255, 0.12)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointRadius: 0,
                pointHoverRadius: 4
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
                    grid: { color: 'rgba(48, 54, 61, 0.3)' },
                    ticks: {
                        color: '#8b949e',
                        maxTicksLimit: 8,
                        font: { size: 10 }
                    },
                    title: {
                        display: true,
                        text: 'Línea de Tiempo (Fechas / Histórico)',
                        color: '#8b949e',
                        font: { size: 10, weight: '500' }
                    }
                },
                y: {
                    type: useLog ? 'logarithmic' : 'linear',
                    grid: { color: 'rgba(48, 54, 61, 0.3)' },
                    min: useLog ? Math.max(1, Math.pow(10, Math.floor(Math.log10(Math.max(minVal, 1))))) : undefined,
                    ticks: {
                        color: '#8b949e',
                        maxTicksLimit: 6,
                        font: { size: 10 },
                        callback: function(value) {
                            return formatYAxisTick(value, useLog);
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(items) {
                            if (!items || !items.length) return '';
                            const idx = items[0].dataIndex;
                            const label = items[0].label;
                            return `Op. #${idx + 1} (${label})`;
                        },
                        label: function(context) {
                            return `Capital Acumulado: $${Number(context.raw).toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

function createBarChart(canvasId, labels, values, title, color = '#58a6ff') {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (window[canvasId + 'Inst']) window[canvasId + 'Inst'].destroy();
    
    window[canvasId + 'Inst'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: values,
                backgroundColor: color,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: '#30363d' } }
            }
        }
    });
}

function createGrowthRateChart(canvasId, ns, g_values, optimal_n) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (window.gnChartInst) window.gnChartInst.destroy();
    
    const colors = ns.map(n => n === optimal_n ? '#3fb950' : '#58a6ff');
    
    window.gnChartInst = new Chart(ctx, {
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
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: '#30363d' } }
            }
        }
    });
}

function createMonteCarloChart(canvasId, labels, percentiles) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (window.mcChartInst) window.mcChartInst.destroy();
    
    // Clean arrays to avoid log(0) which stretches scale to -infinity
    const clean = arr => (arr || []).map(v => v <= 0.01 ? 0.01 : v);
    
    const p95_clean = clean(percentiles.p95);
    const p75_clean = clean(percentiles.p75);
    const p50_clean = clean(percentiles.p50);
    const p25_clean = clean(percentiles.p25);
    const p5_clean = clean(percentiles.p5);
    
    // Determine whether to use log scale or linear scale
    const allValues = [...p95_clean, ...p75_clean, ...p50_clean, ...p25_clean, ...p5_clean];
    const maxVal = Math.max(...allValues);
    const minVal = Math.min(...allValues);
    const useLog = (maxVal / (minVal || 1)) > 50 && minVal > 0.01;
    
    window.mcChartInst = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'P95',
                    data: p95_clean,
                    borderColor: 'rgba(63, 185, 80, 0.8)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: 'P75',
                    data: p75_clean,
                    borderColor: 'rgba(63, 185, 80, 0.4)',
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: 'Mediana (P50)',
                    data: p50_clean,
                    borderColor: '#58a6ff',
                    borderWidth: 3,
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: 'P25',
                    data: p25_clean,
                    borderColor: 'rgba(248, 81, 73, 0.4)',
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: 'P5',
                    data: p5_clean,
                    borderColor: 'rgba(248, 81, 73, 0.8)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { display: false },
                y: { 
                    type: useLog ? 'logarithmic' : 'linear', 
                    grid: { color: '#30363d' },
                    min: useLog ? Math.max(1, Math.pow(10, Math.floor(Math.log10(Math.max(minVal, 1))))) : undefined,
                    ticks: {
                        color: '#8b949e',
                        maxTicksLimit: 6,
                        font: { size: 10 },
                        callback: function(value) {
                            return formatYAxisTick(value, useLog);
                        }
                    }
                }
            }
        }
    });
}

function createCorrelationHeatmap(canvasId, matrix, labels) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const parent = canvas.parentElement;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    
    // Use container dimensions if canvas bounding rect is collapsed
    const width = parent ? parent.clientWidth : canvas.clientWidth;
    const height = parent ? parent.clientHeight : canvas.clientHeight;
    
    canvas.width = (width || 400) * dpr;
    canvas.height = (height || 280) * dpr;
    ctx.scale(dpr, dpr);
    
    const w = width || 400;
    const h = height || 280;
    
    ctx.clearRect(0, 0, w, h);
    
    if (!matrix || matrix.length === 0 || !labels || labels.length === 0) {
        ctx.fillStyle = '#8b949e';
        ctx.font = '13px Inter, sans-serif';
        ctx.fillText('Sin datos de correlación', w / 2 - 60, h / 2);
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
            let colorStr = 'rgba(22, 27, 34, 0.9)';

            if (val !== null && val !== undefined && !isNaN(val)) {
                if (val >= 0) {
                    const intensity = Math.pow(val, 1.2);
                    const r = Math.round(22 + intensity * (248 - 22));
                    const g = Math.round(27 + intensity * (81 - 27));
                    const b = Math.round(34 + intensity * (73 - 34));
                    colorStr = `rgb(${r}, ${g}, ${b})`;
                } else {
                    const intensity = Math.pow(Math.abs(val), 1.2);
                    const r = Math.round(22 + intensity * (88 - 22));
                    const g = Math.round(27 + intensity * (166 - 27));
                    const b = Math.round(34 + intensity * (255 - 34));
                    colorStr = `rgb(${r}, ${g}, ${b})`;
                }
            }
            
            ctx.fillStyle = colorStr;
            ctx.fillRect(leftMargin + j * cellW, topMargin + i * cellH, cellW - 1.5, cellH - 1.5);
            
            if (cellW > 18 && cellH > 14 && val !== null && val !== undefined && !isNaN(val)) {
                ctx.fillStyle = Math.abs(val) > 0.4 ? '#ffffff' : '#c9d1d9';
                const fontSize = Math.min(11, Math.max(8, Math.floor(cellH * 0.45)));
                ctx.font = `bold ${fontSize}px Inter, sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(val.toFixed(2), leftMargin + j * cellW + cellW / 2, topMargin + i * cellH + cellH / 2);
            }
        }
    }
    
    const labelFontSize = Math.min(11, Math.max(8, Math.floor(cellH * 0.45)));
    ctx.fillStyle = '#c9d1d9';
    ctx.font = `bold ${labelFontSize}px Inter, sans-serif`;
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
