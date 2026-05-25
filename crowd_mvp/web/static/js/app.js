'use strict';

const state = {
    activeScreen: 'safety',
    filter: 'all',
    running: true,
    geometry: null,
    lastKde: '',
    firstSnapshot: true,
};

const SCREEN_BADGES = {
    safety:     { label: 'Safety',            cls: 'bg-blue-100 text-blue-700' },
    analytics:  { label: 'Sponsor Analytics', cls: 'bg-purple-100 text-purple-700' },
    simulation: { label: 'Simulation Suite',  cls: 'bg-green-100 text-green-700' },
};

let ws = null;
let reconnectTimer = null;

// ------------------------------------------------------------------
// Screen switching
// ------------------------------------------------------------------
function switchScreen(name) {
    state.activeScreen = name;

    document.querySelectorAll('.nav-item[data-screen]').forEach(el => {
        el.classList.toggle('active', el.dataset.screen === name);
    });

    const badge = document.getElementById('screen-badge');
    if (badge && SCREEN_BADGES[name]) {
        badge.textContent = SCREEN_BADGES[name].label;
        badge.className = 'text-xs px-2 py-0.5 rounded-full font-medium ' + SCREEN_BADGES[name].cls;
    }

    const safetyBars  = document.getElementById('safety-bars');
    const alertsAside = document.getElementById('alerts-aside');
    const sharedMap   = document.getElementById('shared-map-area');
    const mapLegend   = document.getElementById('map-legend');
    const analyticsEl = document.getElementById('analytics-screen');
    const simEl       = document.getElementById('simulation-screen');
    const layerAgents = document.getElementById('layer-agents');
    const heatmapEl   = document.getElementById('heatmap-overlay');

    if (name === 'safety') {
        if (safetyBars)  safetyBars.style.display  = 'flex';
        if (alertsAside) alertsAside.style.display  = 'flex';
        if (sharedMap)   sharedMap.style.display    = 'flex';
        if (mapLegend)   mapLegend.style.display    = 'flex';
        if (analyticsEl) analyticsEl.style.display  = 'none';
        if (simEl)       simEl.style.display         = 'none';
        if (layerAgents) layerAgents.style.display   = 'none';
        if (heatmapEl)   heatmapEl.style.display     = '';
    } else if (name === 'analytics') {
        if (safetyBars)  safetyBars.style.display   = 'none';
        if (alertsAside) alertsAside.style.display   = 'none';
        if (sharedMap)   sharedMap.style.display     = 'none';
        if (mapLegend)   mapLegend.style.display     = 'none';
        if (analyticsEl) analyticsEl.style.display   = 'flex';
        if (simEl)       simEl.style.display          = 'none';
    } else if (name === 'simulation') {
        if (safetyBars)  safetyBars.style.display   = 'none';
        if (alertsAside) alertsAside.style.display   = 'none';
        if (sharedMap)   sharedMap.style.display     = 'flex';
        if (mapLegend)   mapLegend.style.display     = 'none';
        if (analyticsEl) analyticsEl.style.display   = 'none';
        // simulation-screen is a sidebar beside the shared map — show it as flex
        if (simEl)       simEl.style.display          = 'flex';
        if (layerAgents) layerAgents.style.display    = '';
        if (heatmapEl)   heatmapEl.style.display      = 'none';
    }
}

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
            buildSafetyBarsDOM(msg.rooms);
            initAnalytics(msg);
            initSimulation();
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
    state.running = snap.running;
    document.getElementById('status-agents').textContent = `${snap.agents.length} agents`;

    state.lastKde = snap.kde_png_b64 || '';

    const active = state.activeScreen;

    if (active === 'safety') {
        updateAgents(snap.agents);
        updateHeatmapOverlay();
        renderSafetyBars(snap);
        renderAlerts(snap.alerts || [], state.filter);
    } else if (active === 'analytics') {
        updateAnalytics(snap);
    } else if (active === 'simulation') {
        updateAgents(snap.agents);
        updateSimulation(snap);
    }
}

function updateHeatmapOverlay() {
    const overlay = document.getElementById('heatmap-overlay');
    if (overlay) overlay.setAttribute('href', state.lastKde);
}

// ------------------------------------------------------------------
// Nav items
// ------------------------------------------------------------------
document.querySelectorAll('.nav-item[data-screen]').forEach(el => {
    el.addEventListener('click', e => {
        e.preventDefault();
        switchScreen(el.dataset.screen);
    });
});

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
    el.className = status === 'connected' ? 'text-green-500 text-xs' : 'text-slate-400 text-xs';
}

// ------------------------------------------------------------------
// Boot
// ------------------------------------------------------------------
switchScreen('safety');
connect();
