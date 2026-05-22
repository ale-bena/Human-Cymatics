'use strict';

const state = {
    tab: 'kde',
    filter: 'all',
    running: true,
    geometry: null,
    lastKde: '',
    lastEst: '',
};

let ws = null;
let reconnectTimer = null;

// ------------------------------------------------------------------
// WebSocket
// ------------------------------------------------------------------
function connect() {
    clearTimeout(reconnectTimer);
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${proto}//${location.host}/ws`);

    ws.onopen = () => setStatus('connected');

    ws.onmessage = ({ data }) => {
        let msg;
        try { msg = JSON.parse(data); } catch { return; }
        if (msg.type === 'geometry') {
            state.geometry = msg;
            renderGeometry(msg);
        } else {
            updateFromSnapshot(msg);
        }
    };

    ws.onclose = () => {
        setStatus('disconnected');
        reconnectTimer = setTimeout(connect, 2000);
    };

    ws.onerror = () => ws.close();
}

// ------------------------------------------------------------------
// Snapshot handler
// ------------------------------------------------------------------
function updateFromSnapshot(snap) {
    // Time display
    document.getElementById('sim-time').textContent = `t: ${snap.t.toFixed(1)}s`;

    // Pause / resume button visibility
    state.running = snap.running;
    document.getElementById('btn-pause').classList.toggle('hidden', !snap.running);
    document.getElementById('btn-resume').classList.toggle('hidden', snap.running);

    // Agents + heatmap
    updateAgents(snap.agents);

    state.lastKde = snap.kde_png_b64 || '';
    state.lastEst = snap.estimate_png_b64 || '';
    updateHeatmapOverlay();

    // Scenario label + sync dropdown
    const scenarioLabel = document.getElementById('scenario-name');
    if (scenarioLabel) {
        scenarioLabel.textContent = snap.scenario.replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    }
    const sel = document.getElementById('scenario-select');
    if (sel && sel.value !== snap.scenario) sel.value = snap.scenario;

    // Status bar
    document.getElementById('status-agents').textContent = `${snap.agents.length} agents`;

    // Alerts
    renderAlerts(snap.alerts || [], state.filter);
}

function updateHeatmapOverlay() {
    const overlay = document.getElementById('heatmap-overlay');
    if (!overlay) return;
    overlay.src = state.tab === 'kde' ? state.lastKde : state.lastEst;
}

// ------------------------------------------------------------------
// Tabs
// ------------------------------------------------------------------
document.getElementById('tab-kde').addEventListener('click', () => {
    state.tab = 'kde';
    setTabActive('kde');
    updateHeatmapOverlay();
});
document.getElementById('tab-est').addEventListener('click', () => {
    state.tab = 'estimate';
    setTabActive('estimate');
    updateHeatmapOverlay();
});
function setTabActive(tab) {
    document.getElementById('tab-kde').classList.toggle('tab-active', tab === 'kde');
    document.getElementById('tab-est').classList.toggle('tab-active', tab === 'estimate');
}

// ------------------------------------------------------------------
// Controls (REST)
// ------------------------------------------------------------------
document.getElementById('btn-pause').addEventListener('click', () =>
    fetch('/sim/pause', { method: 'POST' }));
document.getElementById('btn-resume').addEventListener('click', () =>
    fetch('/sim/resume', { method: 'POST' }));
document.getElementById('btn-reset').addEventListener('click', () =>
    fetch('/sim/reset', { method: 'POST' }));
document.getElementById('scenario-select').addEventListener('change', e =>
    fetch(`/sim/scenario/${e.target.value}`, { method: 'POST' }));

// ------------------------------------------------------------------
// Hamburger
// ------------------------------------------------------------------
document.getElementById('hamburger-btn').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('expanded');
});

// ------------------------------------------------------------------
// Filter chips
// ------------------------------------------------------------------
document.querySelectorAll('.filter-chip').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.filter = btn.dataset.filter;
        renderAlerts(getLastAlerts(), state.filter);
    });
});

// ------------------------------------------------------------------
// Status bar helpers
// ------------------------------------------------------------------
function setStatus(status) {
    const el = document.getElementById('status-conn');
    if (!el) return;
    el.textContent = status === 'connected' ? '● Connected' : '○ Reconnecting…';
    el.className = status === 'connected' ? 'text-green-500' : 'text-slate-500';
}

// ------------------------------------------------------------------
// Boot
// ------------------------------------------------------------------
setTabActive('kde');
connect();
