'use strict';

function renderSafetyBars(snap) {
    const rooms = snap.rooms || [];
    const total = rooms.reduce((s, r) => s + (r.density || 0), 0);
    const cap   = rooms.reduce((s, r) => s + (r.capacity || 0), 0);

    const totalNumEl = document.getElementById('safety-total-number');
    const totalPctEl = document.getElementById('safety-total-pct');
    if (totalNumEl) totalNumEl.textContent = total;
    if (totalPctEl) totalPctEl.textContent = cap ? Math.round(100 * total / cap) + '%' : '—';

    rooms.forEach(r => {
        const barEl   = document.getElementById('bar-fill-' + r.id);
        const countEl = document.getElementById('bar-count-' + r.id);
        if (!barEl || !countEl) return;
        const pct = r.capacity ? Math.min(100, Math.round(100 * r.density / r.capacity)) : 0;
        barEl.style.width = pct + '%';
        barEl.className = 'occ-bar-fill ' + (pct >= 90 ? 'fill-red' : pct >= 70 ? 'fill-yellow' : 'fill-green');
        countEl.textContent = r.density + ' / ' + r.capacity;
    });
}

function buildSafetyBarsDOM(rooms) {
    const panel = document.getElementById('safety-bars');
    if (!panel) return;
    panel.innerHTML = '';

    const heading = document.createElement('h3');
    heading.textContent = 'Occupancy';
    panel.appendChild(heading);

    const totalBlock = document.createElement('div');
    totalBlock.className = 'safety-total-block';
    totalBlock.innerHTML =
        '<div class="total-num"><span id="safety-total-number">0</span></div>' +
        '<div class="total-pct">of capacity — <span id="safety-total-pct">—</span></div>';
    panel.appendChild(totalBlock);

    (rooms || []).forEach(r => {
        const row = document.createElement('div');
        row.className = 'occ-bar-row';
        row.innerHTML =
            '<div class="occ-bar-header">' +
              '<span class="occ-bar-name">' + (r.name || r.id) + '</span>' +
              '<span class="occ-bar-count" id="bar-count-' + r.id + '">0 / ' + (r.capacity || '?') + '</span>' +
            '</div>' +
            '<div class="occ-bar-track"><div class="occ-bar-fill fill-green" id="bar-fill-' + r.id + '" style="width:0%"></div></div>';
        panel.appendChild(row);
    });
}
