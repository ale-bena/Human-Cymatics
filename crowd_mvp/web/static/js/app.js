'use strict';

// ── App state ────────────────────────────────────────────────────────────
const state = {
    heatmapTab:    'kde',   // 'kde' | 'estimate' — sub-tab inside map panel
    activeTab:     'map',   // 'map' | 'surface' | 'path'
    running:       true,
    geometry:      null,
    lastKde:       '',
    lastEst:       '',
    firstSnapshot: true,
};

const SCENARIO_N_PEOPLE = {
    baseline:         150,
    concert_peak:     300,
    evacuation_drill: 200,
};

// ── Lazy panel singletons ────────────────────────────────────────────────
// Initialised on first visit to each tab.
let _surfaceInited  = false;
let _trajectory     = null;
let _pathInited     = false;

let ws             = null;
let reconnectTimer = null;

// ─────────────────────────────────────────────────────────────────────────
// Tab switching
// ─────────────────────────────────────────────────────────────────────────
function showTab(tabName) {
    if (state.activeTab === tabName) return;
    state.activeTab = tabName;

    ['map', 'surface', 'path'].forEach(t => {
        document.getElementById('panel-' + t).classList.toggle('hidden', t !== tabName);
        const btn = document.getElementById('tab-btn-' + t);
        btn.classList.toggle('main-tab-active', t === tabName);
    });

    if (tabName === 'surface') {
        if (!_surfaceInited) {
            initSurface('surface-div');
            _surfaceInited = true;
        } else {
            // Resize Plotly to fit the now-visible container
            requestAnimationFrame(() => resizeSurface('surface-div'));
        }
    }

    if (tabName === 'path') {
        if (!_pathInited && state.geometry) {
            _initTrajectory();
        }
    }
}

function _initTrajectory() {
    if (_trajectory || !state.geometry) return;
    const canvas = document.getElementById('trajectory-canvas');
    if (!canvas) return;
    const [mW, mH] = state.geometry.map_size;
    _trajectory = new TrajectoryCanvas(canvas, mW, mH);
    _pathInited = true;
}

// ─────────────────────────────────────────────────────────────────────────
// WebSocket
// ─────────────────────────────────────────────────────────────────────────
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

            // Re-init surface and trajectory on map reset / scenario change
            if (_surfaceInited) {
                resetSurface('surface-div');
            }
            if (_trajectory) {
                _trajectory.reset();
            }
            if (state.activeTab === 'path' && !_trajectory) {
                _initTrajectory();
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

// ─────────────────────────────────────────────────────────────────────────
// Snapshot handling
// ─────────────────────────────────────────────────────────────────────────
function updateFromSnapshot(snap) {
    document.getElementById('sim-time').textContent = `t: ${snap.t.toFixed(1)}s`;

    state.running = snap.running;
    document.getElementById('btn-pause').classList.toggle('hidden', !snap.running);
    const resumeBtn = document.getElementById('btn-resume');
    resumeBtn.classList.toggle('hidden', snap.running);
    resumeBtn.classList.toggle('flex',  !snap.running);

    // Map panel always updated in background (keeps heatmap fresh when tab is revisited)
    updateAgents(snap.agents);
    state.lastKde = snap.kde_png_b64 || '';
    state.lastEst = snap.estimate_png_b64 || '';
    updateHeatmapOverlay();

    // 3D surface — update whenever surface is initialised (even if tab is hidden)
    if (snap.density_grid && _surfaceInited) {
        updateSurface('surface-div', snap.density_grid);
    }

    // Trajectory — always accumulate if initialised
    if (_trajectory && snap.agents && snap.agents.length) {
        _trajectory.addAgents(snap.agents);
        if (state.activeTab === 'path') {
            _trajectory.render();
        }
    }

    // Scenario label
    const scenarioLabel = document.getElementById('scenario-name');
    if (scenarioLabel) {
        scenarioLabel.textContent = snap.scenario
            .replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    }
    const sel = document.getElementById('scenario-select');
    if (sel && sel.value !== snap.scenario) sel.value = snap.scenario;

    // Sync n_people once after connect / reset
    if (state.firstSnapshot && snap.n_people != null) {
        const inp = document.getElementById('n-people-input');
        if (inp) inp.value = snap.n_people;
        state.firstSnapshot = false;
    }

    document.getElementById('status-agents').textContent = `${snap.agents.length} agents`;
}

function updateHeatmapOverlay() {
    const overlay = document.getElementById('heatmap-overlay');
    if (!overlay) return;
    overlay.setAttribute('href', state.heatmapTab === 'kde' ? state.lastKde : state.lastEst);
}

// ─────────────────────────────────────────────────────────────────────────
// Sub-tabs (KDE / WiFi Estimate)
// ─────────────────────────────────────────────────────────────────────────
document.getElementById('tab-kde').addEventListener('click', () => {
    state.heatmapTab = 'kde';
    document.getElementById('tab-kde').classList.add('subtab-active');
    document.getElementById('tab-est').classList.remove('subtab-active');
    updateHeatmapOverlay();
});
document.getElementById('tab-est').addEventListener('click', () => {
    state.heatmapTab = 'estimate';
    document.getElementById('tab-est').classList.add('subtab-active');
    document.getElementById('tab-kde').classList.remove('subtab-active');
    updateHeatmapOverlay();
});

// ─────────────────────────────────────────────────────────────────────────
// Controls
// ─────────────────────────────────────────────────────────────────────────
document.getElementById('btn-pause').addEventListener('click', () =>
    fetch('/sim/pause', { method: 'POST' }));

document.getElementById('btn-resume').addEventListener('click', () =>
    fetch('/sim/resume', { method: 'POST' }));

document.getElementById('btn-reset').addEventListener('click', () => {
    const n = parseInt(document.getElementById('n-people-input')?.value || 150, 10);
    state.firstSnapshot = true;
    if (_trajectory) _trajectory.reset();
    fetch(`/sim/reset?n_people=${Math.max(10, Math.min(700, n))}`, { method: 'POST' });
});

document.getElementById('scenario-select').addEventListener('change', e => {
    const scenario = e.target.value;
    const inp = document.getElementById('n-people-input');
    if (inp && SCENARIO_N_PEOPLE[scenario] != null) inp.value = SCENARIO_N_PEOPLE[scenario];
    if (_trajectory) _trajectory.reset();
    fetch(`/sim/scenario/${scenario}`, { method: 'POST' });
});

document.getElementById('btn-clear-path').addEventListener('click', () => {
    if (_trajectory) _trajectory.reset();
});

// ─────────────────────────────────────────────────────────────────────────
// Status helpers
// ─────────────────────────────────────────────────────────────────────────
function setStatus(status) {
    const el = document.getElementById('status-conn');
    if (!el) return;
    el.textContent = status === 'connected' ? '● Connected' : '○ Reconnecting…';
    el.className   = status === 'connected'
        ? 'text-xs text-green-500'
        : 'text-xs text-gray-400';
}

// ─────────────────────────────────────────────────────────────────────────
// Boot
// ─────────────────────────────────────────────────────────────────────────
connect();
