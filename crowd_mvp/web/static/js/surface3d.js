'use strict';
// surface3d.js — Plotly.js 3D density surface panel
// Requires Plotly.js to be loaded before this script.

let _surfaceReady = false;
let _surfaceDivId = null;

function initSurface(divId) {
    _surfaceDivId = divId;
    const emptyGrid = Array.from({ length: 40 }, () => Array(60).fill(0));

    const data = [{
        type: 'surface',
        z: emptyGrid,
        colorscale: 'Plasma',
        showscale: false,
        hoverinfo: 'none',
        contours: {
            x: { show: false },
            y: { show: false },
            z: { show: false },
        },
        lighting: {
            ambient:   0.75,
            diffuse:   0.5,
            roughness: 0.55,
            specular:  0.08,
            fresnel:   0.1,
        },
        lightposition: { x: 100, y: 200, z: 500 },
    }];

    const layout = {
        paper_bgcolor: '#0b0f1a',
        scene: {
            bgcolor: '#0b0f1a',
            xaxis: { visible: false, showgrid: false, zeroline: false },
            yaxis: { visible: false, showgrid: false, zeroline: false },
            zaxis: { visible: false, showgrid: false, zeroline: false },
            camera: {
                eye:    { x: 1.45, y: -1.45, z: 1.05 },
                center: { x: 0,    y: 0,      z: -0.1 },
                up:     { x: 0,    y: 0,      z: 1    },
            },
            aspectmode: 'manual',
            aspectratio: { x: 1.5, y: 1.0, z: 0.5 },
        },
        margin: { l: 0, r: 0, t: 0, b: 0 },
    };

    Plotly.newPlot(divId, data, layout, {
        displayModeBar: false,
        responsive:     true,
        staticPlot:     false,   // keep rotation enabled — looks cool on screen
    });

    _surfaceReady = true;
}

function updateSurface(divId, densityGrid) {
    if (!_surfaceReady || !densityGrid) return;
    // restyle is cheaper than react/relayout — only updates z data
    Plotly.restyle(divId, { z: [densityGrid] }, [0]);
}

function resetSurface(divId) {
    _surfaceReady = false;
    initSurface(divId);
}
