# Human Cymatics — Crowd Monitoring Simulator MVP

A local Pygame simulator that demonstrates WiFi-sniffing-based crowd monitoring for events and venues. Built as a pitch demo: investors see in real time how a sniffer network estimates crowd density — and how accurate (or noisy) those estimates are.

---

## How to Run

### Local (Python)

**Requirements:** Python 3.10+, then install dependencies:

```bash
pip install pygame numpy scipy matplotlib
```

**Launch:**

```bash
python crowd_mvp/main.py
```

### Web (browser, no install)

Build a self-contained HTML page with [Pygbag](https://pygame-web.github.io/):

```bash
pip install pygbag
pygbag .
```

This produces a `build/web/` folder. Open `build/web/index.html` locally, or host the folder on any static host (GitHub Pages, Netlify, itch.io) for a shareable link — no Python or install required on the viewer's end.

> **Note:** The KDE heatmap (Tab 1) may show a flat colour in the browser build — SciPy's gaussian_kde has limited WASM support. Tabs 2 and 3 are fully functional.

The simulation starts automatically. Use the control panel on the right to adjust parameters, switch maps, and change agent behavior. Press **Pause** to freeze the demo mid-presentation, **Reset** to restart with current settings.

---

## What Was Built

**Simulation engine** — agents (people) move across a venue map with three configurable behaviors: random wandering, goal-oriented (walk to a POI, linger, move on), and social clustering. A network of WiFi sniffer nodes estimates zone density every second by counting nearby agents and adding Gaussian noise.

**Three venue maps** — small (4 zones), medium (8 zones), large (12 zones) — selectable from the control panel.

**Three visualization tabs:**

- **Tab 1** — Live KDE heatmap (viridis/hot colormap) blended over the map, updated from sniffer estimates.
- **Tab 2** — Side-by-side comparison: real agent density (ground truth) vs sniffer estimates. The colour difference between panels is the core pitch moment — drag the `sigma_err` slider high to exaggerate the WiFi noise.
- **Tab 3** — Accumulated traffic matrix showing zone-to-zone flow (plasma colormap) + "long-exposure" trajectory traces for a tracked subset of agents.

**Playback controls** — Pause/Resume toggle, Reset, elapsed/total timer, and a semi-transparent end-of-simulation overlay at 300 s.

---

## Controls

| Control | Description |
|---------|-------------|
| Map selector | Switch between Small / Medium / Large venue |
| Behavior selector | Wanderer / Goal-oriented / Social |
| `n_people` slider | Number of agents (takes effect on Reset) |
| `sigma_err` slider | WiFi sniffer noise level |
| `sigma_kernel` slider | KDE smoothing bandwidth |
| Tab buttons / keys 1–3 | Switch visualization tab |
| Pause / Resume | Freeze or resume simulation and timer |
| Reset | Rebuild simulation with current settings |
