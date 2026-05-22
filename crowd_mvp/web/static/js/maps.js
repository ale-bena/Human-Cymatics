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
};

const POI_SHORT = {
    entrance:      'IN',
    exit:          'OUT',
    bar:           'BAR',
    sponsor_stand: 'S',
    bathroom:      'WC',
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

    // POIs
    (data.pois || []).forEach(p => {
        const [px, py] = p.pos;
        const fill = POI_FILL[p.category] || '#888';
        const short = POI_SHORT[p.category] || p.category.substring(0, 3).toUpperCase();
        const g = svgEl('g', {});
        g.appendChild(svgEl('rect', {
            x: px - 12, y: py - 9, width: 24, height: 18,
            fill, rx: 3, opacity: 0.9,
        }));
        g.appendChild(svgText(short, px, py, '#fff', 8, '600'));
        layerPois.appendChild(g);
    });
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
