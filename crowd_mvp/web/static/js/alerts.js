'use strict';

const SEVERITY = {
    critical: { border: 'border-red-400',    bg: 'bg-red-50',     icon: '🔴', badge: 'text-red-500'    },
    warning:  { border: 'border-yellow-400', bg: 'bg-yellow-50',  icon: '🟡', badge: 'text-yellow-600' },
    ok:       { border: 'border-green-400',  bg: 'bg-green-50',   icon: '🟢', badge: 'text-green-600'  },
};

const SEV_ORDER = { critical: 0, warning: 1, ok: 2 };

let _lastAlerts = [];

function renderAlerts(alerts, filter) {
    _lastAlerts = alerts;
    const list = document.getElementById('alerts-list');

    const filtered = filter === 'all' ? alerts : alerts.filter(a => a.severity === filter);
    // Sort: critical first, then newest (smallest since) first within same severity
    const sorted = [...filtered].sort((a, b) => {
        const sd = (SEV_ORDER[a.severity] ?? 1) - (SEV_ORDER[b.severity] ?? 1);
        return sd !== 0 ? sd : (a.since ?? 0) - (b.since ?? 0);
    });

    // Update count badges
    const crit = alerts.filter(a => a.severity === 'critical').length;
    const warn = alerts.filter(a => a.severity === 'warning').length;
    const critBadge = document.getElementById('badge-critical');
    const warnBadge = document.getElementById('badge-warning');
    if (critBadge) critBadge.textContent = crit || '';
    if (warnBadge) warnBadge.textContent = warn || '';

    if (sorted.length === 0) {
        list.innerHTML = '<div class="text-slate-500 text-sm text-center py-10">No active alerts</div>';
        return;
    }

    // Clear the "no alerts" placeholder if it's there
    if (!list.querySelector('[data-alert-id]')) list.innerHTML = '';

    // Build a map of currently rendered cards
    const existingMap = new Map(
        [...list.querySelectorAll('[data-alert-id]')].map(el => [el.dataset.alertId, el])
    );
    const incomingIds = new Set(sorted.map(a => a.id));

    // Remove cards that are no longer active
    for (const [id, el] of existingMap) {
        if (!incomingIds.has(id)) el.remove();
    }

    // Insert or update cards and enforce sorted DOM order
    for (let i = 0; i < sorted.length; i++) {
        const alert = sorted[i];
        const cfg = SEVERITY[alert.severity] || SEVERITY.warning;
        const sinceText = alert.since != null ? `${Math.round(alert.since)}s` : '';

        let card = existingMap.get(alert.id);

        if (!card) {
            // New alert — create with fade-in animation
            card = document.createElement('div');
            card.dataset.alertId = alert.id;
            card.className = `alert-card rounded-lg p-3 border-l-4 ${cfg.border} ${cfg.bg}`;
            card.innerHTML = _cardHTML(alert, cfg, sinceText);
        } else {
            // Existing alert — update the since timer only, no re-animation
            const sinceEl = card.querySelector('[data-since]');
            if (sinceEl) sinceEl.textContent = sinceText;
            // Ensure class stays stable (no alert-card = no animation replay)
            card.className = `rounded-lg p-3 border-l-4 ${cfg.border} ${cfg.bg}`;
        }

        // Move card to the correct position if needed
        const nodeAtIndex = list.children[i];
        if (nodeAtIndex !== card) list.insertBefore(card, nodeAtIndex || null);
    }
}

function _cardHTML(alert, cfg, sinceText) {
    return `
        <div class="flex items-start gap-2">
            <span class="text-sm mt-0.5 shrink-0">${cfg.icon}</span>
            <div class="flex-1 min-w-0">
                <div class="flex items-baseline justify-between gap-2">
                    <span class="font-semibold text-sm text-slate-700 truncate">${escHtml(alert.title)}</span>
                    <span class="text-xs text-slate-500 shrink-0" data-since>${sinceText}</span>
                </div>
                <div class="text-xs text-slate-600 mt-0.5">${escHtml(alert.description)}</div>
                <div class="text-xs text-slate-400 mt-1 italic">${escHtml(alert.suggestion)}</div>
            </div>
        </div>`;
}

function escHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function getLastAlerts() { return _lastAlerts; }
