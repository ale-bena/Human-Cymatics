'use strict';
// surface3d.js — Plotly.js two-subplot 3D surface panel.
//
// Left subplot  (scene)  — real-time density   — plasma colormap
// Right subplot (scene2) — time-averaged density — viridis colormap
//
// Running average is computed client-side: no backend change needed.

let _surfaceReady  = false;
let _avgGrid       = null;   // running sum (40×60)
let _avgCount      = 0;

const _ROWS = 40;
const _COLS = 60;

// ── Shared scene config (white bg, hidden axes, nice camera) ─────────────
function _sceneConfig(domainX) {
    return {
        bgcolor: 'white',
        xaxis: { visible: false, showgrid: false, zeroline: false, showspikes: false },
        yaxis: { visible: false, showgrid: false, zeroline: false, showspikes: false },
        zaxis: { visible: false, showgrid: false, zeroline: false, showspikes: false },
        camera: {
            eye:    { x: 1.5, y: -1.5, z: 1.0 },
            center: { x: 0,   y: 0,    z: -0.1 },
            up:     { x: 0,   y: 0,    z: 1    },
        },
        aspectmode:  'manual',
        aspectratio: { x: 1.5, y: 1.0, z: 0.5 },
        domain: { x: domainX, y: [0.0, 1.0] },
    };
}

// ── Shared lighting config ────────────────────────────────────────────────
const _LIGHTING = {
    ambient:   0.8,
    diffuse:   0.5,
    roughness: 0.5,
    specular:  0.07,
    fresnel:   0.1,
};

const _EMPTY = Array.from({ length: _ROWS }, () => Array(_COLS).fill(0));

// ─────────────────────────────────────────────────────────────────────────
function initSurface(divId) {
    const data = [
        {   // Trace 0 — real-time, plasma
            type: 'surface',
            z: _EMPTY.map(r => [...r]),
            colorscale: 'Plasma',
            showscale: false,
            hoverinfo: 'none',
            scene: 'scene',
            opacity: 1.0,
            lighting: _LIGHTING,
            lightposition: { x: 100, y: 200, z: 500 },
            contours: { x: { show: false }, y: { show: false }, z: { show: false } },
        },
        {   // Trace 1 — time average, viridis
            type: 'surface',
            z: _EMPTY.map(r => [...r]),
            colorscale: 'Viridis',
            showscale: false,
            hoverinfo: 'none',
            scene: 'scene2',
            opacity: 1.0,
            lighting: _LIGHTING,
            lightposition: { x: 100, y: 200, z: 500 },
            contours: { x: { show: false }, y: { show: false }, z: { show: false } },
        },
    ];

    const layout = {
        paper_bgcolor: 'white',
        scene:  _sceneConfig([0.01, 0.48]),
        scene2: _sceneConfig([0.52, 0.99]),
        annotations: [
            {
                text: 'Real-time Density',
                x: 0.245, y: 1.03,
                xref: 'paper', yref: 'paper',
                showarrow: false,
                font: { size: 13, color: '#374151', family: 'system-ui, sans-serif', weight: 600 },
                xanchor: 'center',
            },
            {
                text: 'Time-Averaged Density',
                x: 0.755, y: 1.03,
                xref: 'paper', yref: 'paper',
                showarrow: false,
                font: { size: 13, color: '#374151', family: 'system-ui, sans-serif', weight: 600 },
                xanchor: 'center',
            },
        ],
        margin: { l: 0, r: 0, t: 38, b: 0 },
    };

    Plotly.newPlot(divId, data, layout, {
        displayModeBar: false,
        responsive:     true,
        staticPlot:     false,
    });

    _surfaceReady = true;
}

// ─────────────────────────────────────────────────────────────────────────
function updateSurface(divId, densityGrid) {
    if (!_surfaceReady || !densityGrid) return;

    // ── Update running average ──────────────────────────────────────────
    if (!_avgGrid) {
        // First frame — clone
        _avgGrid  = densityGrid.map(row => [...row]);
        _avgCount = 1;
    } else {
        for (let r = 0; r < _ROWS; r++) {
            for (let c = 0; c < _COLS; c++) {
                _avgGrid[r][c] += densityGrid[r][c];
            }
        }
        _avgCount++;
    }

    // Normalise average to [0, 1]
    const avgNorm = _avgGrid.map(row => row.map(v => v / _avgCount));

    // ── Single restyle call for both traces ─────────────────────────────
    Plotly.restyle(divId, { z: [densityGrid, avgNorm] }, [0, 1]);
}

// ─────────────────────────────────────────────────────────────────────────
function resetSurface(divId) {
    _avgGrid      = null;
    _avgCount     = 0;
    _surfaceReady = false;
    initSurface(divId);
}

// ─────────────────────────────────────────────────────────────────────────
function resizeSurface(divId) {
    if (!_surfaceReady) return;
    Plotly.Plots.resize(document.getElementById(divId));
}
