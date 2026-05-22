'use strict';

const SEVERITY = {
    critical: { border: 'border-red-500',    bg: 'bg-red-950',    icon: '🔴', badge: 'text-red-400'    },
    warning:  { border: 'border-yellow-500', bg: 'bg-yellow-950', icon: '🟡', badge: 'text-yellow-400' },
    ok:       { border: 'border-green-500',  bg: 'bg-green-950',  icon: '🟢', badge: 'text-green-400'  },
};

let _lastAlerts = [];

function renderAlerts(alerts, filter) {
    _lastAlerts = alerts;
    const list = document.getElementById('alerts-list');

    const filtered = filter === 'all'
        ? alerts
        : alerts.filter(a => a.severity === filter);

    const sorted = [...filtered].sort((a, b) =>
        a.severity === 'critical' && b.severity !== 'critical' ? -1 :
        b.severity === 'critical' && a.severity !== 'critical' ? 1 : 0
    );

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

    // Preserve existing cards to avoid removing/re-adding unnecessarily
    const existingIds = new Set([...list.querySelectorAll('[data-alert-id]')].map(el => el.dataset.alertId));
    const incomingIds = new Set(sorted.map(a => a.id));

    // Remove stale cards
    for (const id of existingIds) {
        if (!incomingIds.has(id)) {
            const el = list.querySelector(`[data-alert-id="${id}"]`);
            if (el) el.remove();
        }
    }

    // Rebuild cards in sorted order
    list.innerHTML = '';
    for (const alert of sorted) {
        const cfg = SEVERITY[alert.severity] || SEVERITY.warning;
        const sinceText = alert.since != null ? `${Math.round(alert.since)}s` : '';

        const card = document.createElement('div');
        card.className = `alert-card rounded-lg p-3 border-l-4 ${cfg.border} ${cfg.bg}`;
        card.dataset.alertId = alert.id;
        card.innerHTML = `
            <div class="flex items-start gap-2">
                <span class="text-sm mt-0.5 shrink-0">${cfg.icon}</span>
                <div class="flex-1 min-w-0">
                    <div class="flex items-baseline justify-between gap-2">
                        <span class="font-semibold text-sm text-slate-100 truncate">${escHtml(alert.title)}</span>
                        <span class="text-xs text-slate-500 shrink-0">${sinceText}</span>
                    </div>
                    <div class="text-xs text-slate-300 mt-0.5">${escHtml(alert.description)}</div>
                    <div class="text-xs text-slate-500 mt-1 italic">${escHtml(alert.suggestion)}</div>
                </div>
            </div>`;
        list.appendChild(card);
    }
}

function escHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function getLastAlerts() { return _lastAlerts; }
