'use strict';

const SVG_NS = 'http://www.w3.org/2000/svg';

const OBSTACLE_FILL = {
    booth:       '#c8903a',
    counter:     '#6a7d8a',
    bar_counter: '#6b4226',
    sofa:        '#8a5252',
    sink:        '#7fb8cc',
};

const POI_FILL = {
    entrance:      '#22c55e',
    exit:          '#ef4444',
    bar:           '#f59e0b',
    sponsor_stand: '#a855f7',
    bathroom:      '#06b6d4',
    table:         '#b58a5a',
};

const POI_SHORT = {
    entrance:      'IN',
    exit:          'OUT',
    bar:           'BAR',
    sponsor_stand: 'S',
    bathroom:      'WC',
    table:         'T',
};

function svgEl(tag, attrs) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
}

function svgText(content, x, y, fill, size, weight) {
    const t = svgEl('text', {
        x, y, fill,
        'font-size': size || 12,
        'font-weight': weight || 'normal',
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',
        'font-family': 'system-ui, -apple-system, sans-serif',
        'pointer-events': 'none',
    });
    t.textContent = content;
    return t;
}

function renderGeometry(data) {
    ['rooms', 'obstacles', 'decor', 'walls', 'doors', 'pois'].forEach(id => {
        const el = document.getElementById('layer-' + id);
        if (el) el.innerHTML = '';
    });

    const layerRooms     = document.getElementById('layer-rooms');
    const layerObstacles = document.getElementById('layer-obstacles');
    const layerDecor     = document.getElementById('layer-decor');
    const layerWalls     = document.getElementById('layer-walls');
    const layerDoors     = document.getElementById('layer-doors');
    const layerPois      = document.getElementById('layer-pois');

    // Rooms
    (data.rooms || []).forEach((r, i) => {
        const [rx, ry, rw, rh] = r.rect;
        const fill = i % 2 === 0 ? '#1e2d45' : '#182338';
        layerRooms.appendChild(svgEl('rect', {
            x: rx, y: ry, width: rw, height: rh,
            fill, stroke: '#3d5a80', 'stroke-width': 1.5,
        }));
        layerRooms.appendChild(svgText(r.name, rx + rw / 2, ry + rh / 2, '#64748b', 14, '500'));
    });

    // Obstacles
    (data.obstacles || []).forEach(o => {
        const [ox, oy, ow, oh] = o.rect;
        const fill = OBSTACLE_FILL[o.type] || '#666';
        layerObstacles.appendChild(svgEl('rect', {
            x: ox, y: oy, width: ow, height: oh,
            fill, stroke: '#3a3a46', 'stroke-width': 1, rx: 2,
        }));
        if (o.label) {
            layerObstacles.appendChild(svgText(o.label, ox + ow / 2, oy + oh / 2, '#1a1a2a', 9));
        }
    });

    // Decor
    (data.decor || []).forEach(d => {
        if (d.type === 'stool') {
            const [px, py] = d.pos;
            layerDecor.appendChild(svgEl('circle', { cx: px, cy: py, r: d.r || 6, fill: '#6e5037' }));
        } else if (d.type === 'plant') {
            const [px, py] = d.pos;
            layerDecor.appendChild(svgEl('circle', { cx: px, cy: py, r: d.r || 10, fill: '#2d6a2d' }));
            layerDecor.appendChild(svgEl('circle', { cx: px, cy: py, r: (d.r || 10) * 0.6, fill: '#3a8a3a' }));
        } else if (d.type === 'table') {
            const [tx, ty, tw, th] = d.rect;
            layerDecor.appendChild(svgEl('rect', { x: tx, y: ty, width: tw, height: th, fill: '#a08060', rx: 2 }));
        } else if (d.type === 'partition') {
            const [x0, y0, x1, y1] = d.line;
            layerDecor.appendChild(svgEl('line', { x1: x0, y1: y0, x2: x1, y2: y1, stroke: '#6b7080', 'stroke-width': 2 }));
        }
    });

    // Walls
    (data.walls || []).forEach(w => {
        layerWalls.appendChild(svgEl('line', {
            x1: w.x0, y1: w.y0, x2: w.x1, y2: w.y1,
            stroke: '#2d3748', 'stroke-width': 3, 'stroke-linecap': 'round',
        }));
    });

    // Doors
    (data.doors || []).forEach(d => {
        layerDoors.appendChild(svgEl('line', {
            x1: d.x0, y1: d.y0, x2: d.x1, y2: d.y1,
            stroke: '#22c55e', 'stroke-width': 4, 'stroke-linecap': 'round',
        }));
    });

    // POIs — entrance/exit render as door frames, tables as small circles,
    // everything else as a labelled chip.
    const [mapW, mapH] = data.map_size || [1000, 700];
    (data.pois || []).forEach(p => {
        const [px, py] = p.pos;
        const fill = POI_FILL[p.category] || '#888';
        const short = POI_SHORT[p.category] || p.category.substring(0, 3).toUpperCase();

        if (p.category === 'entrance' || p.category === 'exit') {
            layerPois.appendChild(renderDoorPoi(px, py, mapW, mapH, fill, short));
        } else if (p.category === 'table') {
            layerPois.appendChild(renderTablePoi(px, py, fill, short));
        } else {
            const g = svgEl('g', {});
            g.appendChild(svgEl('rect', {
                x: px - 12, y: py - 9, width: 24, height: 18,
                fill, rx: 3, opacity: 0.9,
            }));
            g.appendChild(svgText(short, px, py, '#fff', 8, '600'));
            layerPois.appendChild(g);
        }
    });
}

// Door POI: an oriented door frame placed on the nearest map perimeter,
// with a 90° swing arc and a bold IN/OUT label.
function renderDoorPoi(px, py, mapW, mapH, fill, label) {
    // Pick the closest perimeter edge so the door sits naturally on the wall.
    const dN = py, dS = mapH - py, dW = px, dE = mapW - px;
    const minD = Math.min(dN, dS, dW, dE);
    let orient;
    if (minD === dS) orient = 'south';
    else if (minD === dN) orient = 'north';
    else if (minD === dW) orient = 'west';
    else orient = 'east';

    const g = svgEl('g', {});
    const W = 48, T = 10;   // frame width along the wall, thickness across it
    let frameRect, arc;

    if (orient === 'south' || orient === 'north') {
        frameRect = { x: px - W / 2, y: py - T / 2, width: W, height: T };
        const dy = orient === 'south' ? -W / 2 : W / 2;
        arc = `M ${px - W / 2} ${py} A ${W / 2} ${W / 2} 0 0 1 ${px} ${py + dy}`;
    } else {
        frameRect = { x: px - T / 2, y: py - W / 2, width: T, height: W };
        const dx = orient === 'east' ? -W / 2 : W / 2;
        arc = `M ${px} ${py - W / 2} A ${W / 2} ${W / 2} 0 0 1 ${px + dx} ${py}`;
    }

    g.appendChild(svgEl('rect', {
        ...frameRect, fill, rx: 2,
        stroke: '#0f172a', 'stroke-width': 1.5, opacity: 0.95,
    }));
    g.appendChild(svgEl('path', {
        d: arc, fill: 'none', stroke: fill, 'stroke-width': 1.3,
        'stroke-dasharray': '3,3', opacity: 0.75,
    }));

    // Label is offset away from the wall so it doesn't overlap the frame.
    const off = 14;
    let lx = px, ly = py;
    if (orient === 'south') ly = py - off;
    else if (orient === 'north') ly = py + off;
    else if (orient === 'east') lx = px - off;
    else lx = px + off;
    g.appendChild(svgText(label, lx, ly, fill, 10, '700'));
    return g;
}

// Table POI: small filled circle with a "T" — sits naturally on top of the
// table decor rectangle without dominating the room.
function renderTablePoi(px, py, fill, label) {
    const g = svgEl('g', {});
    g.appendChild(svgEl('circle', {
        cx: px, cy: py, r: 8, fill,
        stroke: '#1a1a2a', 'stroke-width': 0.8, opacity: 0.9,
    }));
    g.appendChild(svgText(label, px, py, '#fff', 9, '700'));
    return g;
}

function updateAgents(agents) {
    const layer = document.getElementById('layer-agents');
    if (!layer) return;
    const frag = document.createDocumentFragment();
    for (const [x, y] of agents) {
        const c = document.createElementNS(SVG_NS, 'circle');
        c.setAttribute('cx', x);
        c.setAttribute('cy', y);
        c.setAttribute('r', '3');
        c.setAttribute('fill', '#93c5fd');
        c.setAttribute('opacity', '0.75');
        frag.appendChild(c);
    }
    layer.innerHTML = '';
    layer.appendChild(frag);
}
