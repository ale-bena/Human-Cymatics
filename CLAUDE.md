# Human Cymatics — Crowd Monitoring Simulator MVP

## Project

Simulatore Pygame local-only per pitch di crowd monitoring e flux estimation in venue per eventi. Demo per investitori e clienti che mostra come il WiFi sniffing stima la densità di folla.

**Core Value:** Il confronto "realtà vs stima WiFi sniffing" deve essere visivamente convincente e immediatamente comprensibile in 30 secondi.

## Stack

- Python 3.10+ · Pygame · NumPy · SciPy · matplotlib
- Nessun backend, web server, o database — single-process locale
- Entry point: `python crowd_mvp/main.py`

## GSD Workflow

This project uses Get Shit Done (GSD) for phase-based execution.

**Planning docs:** `.planning/`
**Current roadmap:** `.planning/ROADMAP.md`
**Requirements:** `.planning/REQUIREMENTS.md`

### Commands

- `/gsd-plan-phase 1` — plan Phase 1: Engine Core
- `/gsd-execute-phase 1` — execute Phase 1
- `/gsd-progress` — check current status
- `/gsd-discuss-phase N` — discuss approach before planning

### Phase Structure

| Phase | Goal |
|-------|------|
| 1: Engine Core | 60 FPS loop, small map, wanderers, sniffer network, basic render |
| 2: Full Venue + Heatmap | All 3 maps, all 3 behaviors, control panel, Tab 1 KDE heatmap |
| 3: Analytics + Polish | Tab 2/3, Start/Pause/Reset, timer, UI polish per pitch |

## Coding Guidelines

- Prioritize visual impact and fluency (60 FPS target) over code elegance
- Default parameter values must produce a convincing demo without any user configuration
- Keep modules small and focused (see `crowd_mvp/` structure)
- Leave σ-per-node as a hook in code but default to uniform σ
- Use NumPy arrays for heatmap computation (no matplotlib embed in main loop)
