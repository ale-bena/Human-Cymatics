'use strict';

const state = {
    tab: 'kde',
    running: true,
    geometry: null,
    lastKde: '',
    lastEst: '',
    firstSnapshot: true,
};

const SCENARIO_N_PEOPLE = {
    baseline:         150,
    concert_peak:     300,
    evacuation_drill: 200,
};

let ws = null;
let reconnectTimer = null;

// ── Lazy singletons ─────────────────────────────────────────────────────────
// Initialised once after the first geometry message arrives.
let _surfaceInitialised = false;
let _trajectory = null;

// ------------------------------------------------------------------
// WebSocket
// ------------------------------------------------------------------
function connect() {
    clearTimeout(reconnectTimer);
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${proto}//${location.host}/ws`);

    ws.onopen = () => { setStatus('connected'); state.firstSnapshot = true; };

    ws.onmessage = ({ data }) => {
        let msg;
        try { msg = JSON.parse(data); } catch { return; }

        if (msg.type === 'geometry') {
            state.geometry = msg;
            renderGeometry(msg);
            _initPanels(msg);
            // Reset trajectory + surface when map changes (scenario/reset)
            if (_trajectory) _trajectory.reset();
            if (_surfaceInitialised) {
                resetSurface('surface-div');
            }
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

// ── One-time panel initialisation ───────────────────────────────────────────
function _initPanels(geometry) {
    // 3-D surface
    if (!_surfaceInitialised) {
        initSurface('surface-div');
        _surfaceInitialised = true;
    }

    // Trajectory canvas
    if (!_trajectory) {
        const canvas = document.getElementById('trajectory-canvas');
        if (canvas && geometry.map_size) {
            const [mW, mH] = geometry.map_size;
            _trajectory = new TrajectoryCanvas(canvas, mW, mH);
        }
    }
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
    document.getElementById('btn-resume').classList.toggle('flex', !snap.running);

    // Map agents + heatmap overlay
    updateAgents(snap.agents);
    state.lastKde = snap.kde_png_b64 || '';
    state.lastEst = snap.estimate_png_b64 || '';
    updateHeatmapOverlay();

    // 3-D surface
    if (snap.density_grid && _surfaceInitialised) {
        updateSurface('surface-div', snap.density_grid);
    }

    // Trajectory accumulation
    if (_trajectory && snap.agents && snap.agents.length) {
        _trajectory.addAgents(snap.agents);
        _trajectory.render();
    }

    // Scenario label + sync dropdown
    const scenarioLabel = document.getElementById('scenario-name');
    if (scenarioLabel) {
        scenarioLabel.textContent = snap.scenario
            .replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    }
    const sel = document.getElementById('scenario-select');
    if (sel && sel.value !== snap.scenario) sel.value = snap.scenario;

    // Sync n_people input on first snapshot after connect/reset
    if (state.firstSnapshot && snap.n_people != null) {
        const inp = document.getElementById('n-people-input');
        if (inp) inp.value = snap.n_people;
        state.firstSnapshot = false;
    }

    // Status bar
    document.getElementById('status-agents').textContent = `${snap.agents.length} agents`;

    // Alerts — no panel in this layout; skip rendering
}

function updateHeatmapOverlay() {
    const overlay = document.getElementById('heatmap-overlay');
    if (!overlay) return;
    overlay.setAttribute('href', state.tab === 'kde' ? state.lastKde : state.lastEst);
}

// ------------------------------------------------------------------
// Tabs (KDE / WiFi Estimate)
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

document.getElementById('btn-reset').addEventListener('click', () => {
    const n = parseInt(document.getElementById('n-people-input')?.value || 150, 10);
    const clamped = Math.max(10, Math.min(700, n));
    state.firstSnapshot = true;
    // Reset trajectory immediately on UI side for snappy feedback
    if (_trajectory) _trajectory.reset();
    fetch(`/sim/reset?n_people=${clamped}`, { method: 'POST' });
});

document.getElementById('scenario-select').addEventListener('change', e => {
    const scenario = e.target.value;
    const inp = document.getElementById('n-people-input');
    if (inp && SCENARIO_N_PEOPLE[scenario] != null) inp.value = SCENARIO_N_PEOPLE[scenario];
    if (_trajectory) _trajectory.reset();
    fetch(`/sim/scenario/${scenario}`, { method: 'POST' });
});

// ------------------------------------------------------------------
// Status helpers
// ------------------------------------------------------------------
function setStatus(status) {
    const el = document.getElementById('status-conn');
    if (!el) return;
    el.textContent = status === 'connected' ? '● Connected' : '○ Reconnecting…';
    el.className   = status === 'connected' ? 'text-xs text-green-500' : 'text-xs text-slate-500';
}

// ------------------------------------------------------------------
// Boot
// ------------------------------------------------------------------
setTabActive('kde');
connect();
