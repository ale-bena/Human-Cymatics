'use strict';

const analyticsState = {
    history: { t: [], totalPct: [], standCounts: {} },
    dwellState: {},
    dwellAccum: {},
    stands: [],
    venueChart: null,
    standChart: null,
    totalCap: 0,
};

const HISTORY_CAP = 600;
const ZONE_PAD = 25;

function _agentInZone(ax, ay, rect) {
    const [ox, oy, ow, oh] = rect;
    return ax >= ox - ZONE_PAD && ax <= ox + ow + ZONE_PAD &&
           ay >= oy - ZONE_PAD && ay <= oy + oh + ZONE_PAD;
}

function initAnalytics(geometry) {
    const obstacles = geometry.obstacles || [];
    analyticsState.stands = obstacles.filter(o =>
        o.type === 'booth' || o.id === 'bar_counter' || o.id === 'info_desk'
    );

    analyticsState.totalCap = (geometry.rooms || []).reduce((s, r) => s + (r.capacity || 0), 0);

    analyticsState.stands.forEach(s => {
        analyticsState.history.standCounts[s.id] = [];
        analyticsState.dwellAccum[s.id] = { sum: 0, count: 0 };
    });

    const sel = document.getElementById('stand-select');
    if (sel) {
        sel.innerHTML = '';
        analyticsState.stands.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.label || s.id;
            sel.appendChild(opt);
        });
        sel.addEventListener('change', _refreshStandChart);
    }

    const btnReport = document.getElementById('btn-report');
    if (btnReport) btnReport.addEventListener('click', generateReport);

    _initCharts();
}

function _initCharts() {
    const venueCtx = document.getElementById('chart-venue');
    const standCtx = document.getElementById('chart-stand');
    if (!venueCtx || !standCtx || typeof Chart === 'undefined') return;

    if (analyticsState.venueChart) analyticsState.venueChart.destroy();
    if (analyticsState.standChart) analyticsState.standChart.destroy();

    const baseDataset = {
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 2,
    };

    analyticsState.venueChart = new Chart(venueCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                ...baseDataset,
                label: 'Venue occupancy %',
                data: [],
                borderColor: '#60a5fa',
                backgroundColor: 'rgba(96,165,250,0.1)',
                fill: true,
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#6b7280', maxTicksLimit: 8 }, grid: { color: '#e5e7eb' } },
                y: { min: 0, max: 100, ticks: { color: '#6b7280' }, grid: { color: '#e5e7eb' } }
            },
            plugins: { legend: { display: false } }
        }
    });

    analyticsState.standChart = new Chart(standCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                ...baseDataset,
                label: 'Stand visitors',
                data: [],
                borderColor: '#34d399',
                backgroundColor: 'rgba(52,211,153,0.1)',
                fill: true,
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#6b7280', maxTicksLimit: 8 }, grid: { color: '#e5e7eb' } },
                y: { min: 0, ticks: { color: '#6b7280' }, grid: { color: '#e5e7eb' } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function updateAnalytics(snap) {
    const agents = snap.agents || [];
    const tLabel = snap.t != null ? snap.t.toFixed(0) + 's' : '';
    const totalAgents = agents.length;
    const totalPct = analyticsState.totalCap > 0
        ? Math.round(100 * totalAgents / analyticsState.totalCap) : 0;

    const h = analyticsState.history;
    h.t.push(tLabel);
    h.totalPct.push(totalPct);

    const standCounts = {};
    analyticsState.stands.forEach(s => {
        let cnt = 0;
        agents.forEach((ag, idx) => {
            const inZone = _agentInZone(ag[0], ag[1], s.rect);
            const key = s.id + '_' + idx;
            const wasIn = analyticsState.dwellState[key];
            if (inZone && !wasIn) {
                analyticsState.dwellState[key] = snap.t;
            } else if (!inZone && wasIn != null) {
                const dwell = snap.t - wasIn;
                if (dwell > 0) {
                    analyticsState.dwellAccum[s.id].sum += dwell;
                    analyticsState.dwellAccum[s.id].count += 1;
                }
                delete analyticsState.dwellState[key];
            }
            if (inZone) cnt++;
        });
        standCounts[s.id] = cnt;
        if (!h.standCounts[s.id]) h.standCounts[s.id] = [];
        h.standCounts[s.id].push(cnt);
    });

    if (h.t.length > HISTORY_CAP) {
        h.t.shift();
        h.totalPct.shift();
        analyticsState.stands.forEach(s => {
            if (h.standCounts[s.id]) h.standCounts[s.id].shift();
        });
    }

    const venueKpiEl = document.getElementById('analytics-venue-pct');
    if (venueKpiEl) venueKpiEl.textContent = totalPct + '%';

    const sel = document.getElementById('stand-select');
    const selectedId = sel ? sel.value : null;

    if (selectedId && standCounts[selectedId] != null) {
        const currentVisEl = document.getElementById('analytics-current-visitors');
        if (currentVisEl) currentVisEl.textContent = standCounts[selectedId];

        const acc = analyticsState.dwellAccum[selectedId];
        const avgPerm = acc && acc.count > 0 ? Math.round(acc.sum / acc.count) : 0;
        const avgPermEl = document.getElementById('analytics-avg-permanence');
        if (avgPermEl) avgPermEl.textContent = avgPerm + 's';
    }

    _updateCharts(h, selectedId);
}

function _updateCharts(h, selectedId) {
    const vc = analyticsState.venueChart;
    if (vc) {
        vc.data.labels = h.t;
        vc.data.datasets[0].data = h.totalPct;
        vc.update('none');
    }
    const sc = analyticsState.standChart;
    if (sc && selectedId && h.standCounts[selectedId]) {
        sc.data.labels = h.t;
        sc.data.datasets[0].data = h.standCounts[selectedId];
        sc.update('none');
    }
}

function _refreshStandChart() {
    const h = analyticsState.history;
    const sel = document.getElementById('stand-select');
    if (!sel) return;
    const selectedId = sel.value;
    _updateCharts(h, selectedId);
}

function generateReport() {
    const stands = analyticsState.stands;
    const h = analyticsState.history;
    const now = new Date().toLocaleString();

    let rows = '';
    stands.forEach(s => {
        const acc = analyticsState.dwellAccum[s.id];
        const avgPerm = acc && acc.count > 0 ? Math.round(acc.sum / acc.count) : 0;
        const counts = h.standCounts[s.id] || [];
        const currentVis = counts.length > 0 ? counts[counts.length - 1] : 0;

        const maxC = Math.max(...counts, 1);
        const svgW = 300;
        const svgH = 60;
        const pts = counts.map((c, i) => {
            const x = counts.length > 1 ? (i / (counts.length - 1)) * svgW : 0;
            const y = svgH - (c / maxC) * svgH;
            return x + ',' + y;
        }).join(' ');
        const sparkline = counts.length > 1
            ? '<svg width="' + svgW + '" height="' + svgH + '" style="border:1px solid #e2e8f0;border-radius:4px"><polyline points="' + pts + '" fill="none" stroke="#2563eb" stroke-width="1.5"/></svg>'
            : '<span style="color:#9ca3af">No data</span>';

        rows += '<tr style="border-bottom:1px solid #f1f5f9">' +
            '<td style="padding:10px 12px;font-weight:600">' + (s.label || s.id) + '</td>' +
            '<td style="padding:10px 12px;text-align:center">' + currentVis + '</td>' +
            '<td style="padding:10px 12px;text-align:center">' + avgPerm + 's</td>' +
            '<td style="padding:10px 12px">' + sparkline + '</td>' +
            '</tr>';
    });

    const html = '<!DOCTYPE html><html><head>' +
        '<meta charset="UTF-8"><title>Analytics Report — HumanCymatics</title>' +
        '<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">' +
        '</head><body class="bg-white text-gray-900 p-8">' +
        '<h1 class="text-2xl font-bold mb-1">Sponsor Analytics Report</h1>' +
        '<p class="text-gray-500 text-sm mb-6">Generated: ' + now + '</p>' +
        '<table style="width:100%;border-collapse:collapse;font-size:14px">' +
        '<thead><tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0">' +
        '<th style="padding:10px 12px;text-align:left">Stand</th>' +
        '<th style="padding:10px 12px;text-align:center">Current Visitors</th>' +
        '<th style="padding:10px 12px;text-align:center">Avg Permanence</th>' +
        '<th style="padding:10px 12px;text-align:left">15-min Trend</th>' +
        '</tr></thead><tbody>' + rows + '</tbody></table>' +
        '<p class="text-xs text-gray-400 mt-6">HumanCymatics — Crowd Monitoring Demo</p>' +
        '</body></html>';

    const w = window.open('', '_blank');
    if (w) { w.document.write(html); w.document.close(); }
}
