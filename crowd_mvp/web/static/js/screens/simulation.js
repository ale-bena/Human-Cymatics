'use strict';

let _evacuating = false;
let _evacuateStart = null;
let _initialAgentCount = null;

function initSimulation() {
    const btnSpawn = document.getElementById('btn-spawn-entrance');
    const btnEvac  = document.getElementById('btn-evacuate');
    if (btnSpawn) {
        btnSpawn.addEventListener('click', () => {
            fetch('/sim/spawn_entrance', { method: 'POST' });
            _evacuating = false;
            _evacuateStart = null;
            _initialAgentCount = null;
            const timerEl = document.getElementById('sim-evac-timer');
            if (timerEl) timerEl.textContent = '—';
        });
    }
    if (btnEvac) {
        btnEvac.addEventListener('click', () => {
            fetch('/sim/evacuate', { method: 'POST' });
            _evacuating = true;
            _evacuateStart = Date.now();
            _initialAgentCount = null;
        });
    }
}

function updateSimulation(snap) {
    const agentCount = (snap.agents || []).length;

    const countEl = document.getElementById('sim-agent-count');
    if (countEl) countEl.textContent = agentCount;

    if (_evacuating) {
        if (_initialAgentCount === null) _initialAgentCount = agentCount;
        const elapsed = Math.round((Date.now() - _evacuateStart) / 1000);
        const timerEl = document.getElementById('sim-evac-timer');
        if (timerEl) timerEl.textContent = elapsed + 's';
        if (_initialAgentCount > 0 && agentCount < _initialAgentCount * 0.05) {
            _evacuating = false;
            if (timerEl) timerEl.textContent += ' ✓';
        }
    }
}
