# Human Cymatics — Crowd Monitoring Simulator MVP

## What This Is

Un simulatore Pygame local-only che funge da demo di pitch per una startup di crowd monitoring e flux estimation in venue per eventi, basata su WiFi/Bluetooth sniffing. Mostra in tempo reale come agenti-persona si muovono nel venue, come i nodi sniffer stimano la densità di zona con errore gaussiano, e confronta ground truth con stima attraverso heatmap interattive. Il prodotto è pensato per investitori e potenziali clienti (organizzatori di eventi, gestori di venue).

## Core Value

Il confronto "realtà vs stima WiFi sniffing" deve essere visivamente convincente e immediatamente comprensibile in 30 secondi — la demo deve dimostrare che il sistema sa dove si trovano le persone nel venue.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 3 mappe preset selezionabili (small 4 sniffer, medium 8, large 12) con zone rettangolari, POI e sniffer posizionati
- [ ] Agenti persona con posizione (x,y), velocità e 3 behavior: wanderer, goal-oriented, social/clusterer
- [ ] Rete sniffer con stima rumorosa per zona: `max(0, round(count_reale + N(0, σ)))`
- [ ] Tab 1: Heatmap KDE bivariato calcolata dalle stime sniffer, con alpha blending sulla mappa
- [ ] Tab 2: Confronto ground truth vs stima (split o overlay semitrasparente)
- [ ] Tab 3: Matrice di traffico accumulata nel tempo + traiettorie subset persone
- [ ] Pannello di controllo: selezione mappa/behavior, sliders (n_people, σ_error, σ_kernel), Start/Pause/Reset, timer
- [ ] Loop 60 FPS con tick sniffer ogni secondo; pausa automatica a fine simulazione

### Out of Scope

- Backend, web server, database — app completamente locale e single-process
- Muri interni complessi — solo bordi della planimetria nell'MVP
- σ diverso per nodo sniffer — codice con hook ma default uniforme
- Real WiFi/Bluetooth sniffing — pura simulazione per pitch

## Context

Questo è un MVP dimostrativo, non il prodotto finale. La priorità assoluta è l'impatto visivo nel pitch. I valori di default devono essere calibrati affinché premendo "Start" senza modifiche nulla parta una simulazione visivamente convincente. La struttura file suggerita è `crowd_mvp/` con sottodirectory `viz/` e `ui/`.

**Stack tecnico fisso:**
- Python 3.10+
- Pygame (rendering e UI)
- NumPy + SciPy (KDE bivariato gaussiano)
- Matplotlib (colormap viridis/hot/plasma → Pygame Surface)

**Layout file suggerito:**
```
crowd_mvp/
├── main.py
├── config.py
├── maps.py
├── people.py
├── sniffers.py
├── viz/heatmap.py, compare.py, traffic.py
├── ui/controls.py, theme.py
└── README.md
```

## Constraints

- **Tech Stack**: Pygame + NumPy + SciPy + matplotlib — nessuna dipendenza web o database
- **Timeline**: 1-2 giorni di sviluppo — scelte orientate a velocità e impatto visivo
- **Scope**: MVP pitch demo — non scalabilità, non produzione, non architettura enterprise
- **Platform**: Desktop locale, single-process, Python 3.10+

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pygame (no web) | Single-process, niente setup backend, facilmente packagable per demo | — Pending |
| KDE via NumPy→Surface (no matplotlib embed) | Più performante a 60 FPS, evita conflitti di thread matplotlib | — Pending |
| 3 behavior come parametro globale per run | Semplifica MVP — ogni persona ha stesso behavior nel run | — Pending |
| σ uniforme con hook per eterogeneità futura | Velocità di sviluppo + estendibilità segnalata nel codice | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-08 after initialization*
