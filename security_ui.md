# Safety UI — Web app (FastAPI + HTML/Tailwind/JS)

## Context

Costruiamo la prima delle 3 UI prodotto del crowd-monitoring: la **Safety screen**. Il simulatore Python è già headless (`Simulation` non importa pygame, espone `get_snapshot()` / `get_room_density()` / `get_door_flow()`), quindi la UI gira come web app che consuma quegli snapshot via WebSocket. Stack: FastAPI backend + HTML/Tailwind/JS frontend (Tailwind via CDN, no toolchain JS), look da prodotto SaaS — obiettivo: pitch a investitori e clienti.

La pygame app esistente resta come dev/debug tool; questa è la nuova superficie prodotto.

**Decisioni lockate** (rispondendo alle domande precedenti):
- Stack: **web app** (FastAPI + HTML/Tailwind/JS via CDN)
- Modalità: **live di default** (sim nel backend) + bottone "Load scenario" per replay
- **Tutti e 5 i tipi di alert**: capacity, bottleneck, surge, evacuation risk, data quality
- Layout mappe: **una sola mappa visibile** con **tab toggle** tra "KDE Heatmap" e "WiFi Estimate"
- Menu sinistro a hamburger collassabile: Safety (attiva) · Sponsor Analytics (disabled) · Simulation Suite (disabled) · Account (disabled)
- **Deploy target: Hugging Face Spaces (Docker SDK)** — single-container, simulation e website nello stesso processo Python. Vincoli architetturali derivati: porta 7860, no DB esterno, no message queue, no state filesystem persistente.

## Approccio

### Architettura

Processo singolo Python via `uvicorn`. Dentro FastAPI:

- **SimulationManager** (background asyncio task) avanza `sim.update()` a 60 Hz. Ogni ~500 ms costruisce uno snapshot esteso (geometria + agenti + heatmap PNG + alert) e fa broadcast ai WS client connessi.
- **AlertEngine** valuta i 5 detector contro lo snapshot prima di emetterlo.
- **WebSocket `/ws`** push live.
- **REST control endpoints**: `POST /sim/pause`, `POST /sim/resume`, `POST /sim/reset`, `POST /sim/scenario/{name}`.
- **GET /** serve `index.html`. Static su `/static`.

Frontend senza build step: Tailwind via CDN, JS vanilla. Mappe = **SVG** per geometrie (stanze/muri/porte/POI/ostacoli/decor) + **`<img>` sovrapposto** per heatmap (PNG rigenerato server-side a 2 Hz, mandato base64 nel payload WS).

### Backend (Python)

| File | Cosa fa |
|------|--------|
| `crowd_mvp/web/__init__.py` | NUOVO — pacchetto |
| `crowd_mvp/web/server.py` | NUOVO — FastAPI app, mount static, WS `/ws`, REST control. Avvio: `uvicorn crowd_mvp.web.server:app`. |
| `crowd_mvp/web/state.py` | NUOVO — `SimulationManager`: tiene un `Simulation`, asyncio task che chiama `update()` a 60 Hz, broadcast a 2 Hz, gestisce pause/reset/load_scenario. Riusa direttamente la `Simulation` esistente da `crowd_mvp/simulation.py`. |
| `crowd_mvp/web/alerts.py` | NUOVO — `AlertEngine` con history rolling per stanza (deque snapshot ultimi 30s a 2 Hz). 5 detector → lista `Alert{id, severity, type, room, title, description, suggestion, since}`. |
| `crowd_mvp/web/scenarios.py` | NUOVO — 3 preset: `baseline`, `concert_peak`, `evacuation_drill`. |
| `crowd_mvp/web/heatmap_png.py` | NUOVO — wrap di `viz/heatmap.py:build_heatmap_surface` (esistente) → serializza Surface a PNG via `pygame.image.save` (pygame caricato solo qui, non in `Simulation`) → base64. Una funzione per KDE (input agent positions), una per "estimate" (zone-fill stile `viz/compare.py`). |

#### 5 alert detector (in `alerts.py`)

Severità: `critical | warning | ok`. Soglie in `config.py`.

- **Capacity**: `density / capacity` ≥ 1.0 → critical · ≥ 0.8 → warning. Suggestion: "Limit incoming flow at door X".
- **Bottleneck**: `door_flow[d]` < 50% del baseline (media mobile 30s) **AND** upstream room density > 70% capacity → warning. Suggestion: "Open secondary route".
- **Surge**: `(density_now - density_10s_ago) / max(1, density_10s_ago)` ≥ 0.5 → critical. Suggestion: "Deploy staff to room Y".
- **Evacuation risk**: per ogni room: avg distanza euclidea agenti→POI `exit` più vicino (semplificato: distanza diretta, no A*). Se density > 60% capacity AND avg_dist > threshold → warning. Suggestion: "Direct toward Exit X".
- **Data quality**: `|real - estimated| / max(real, 1)` > 0.3 per qualsiasi zona → warning. Suggestion: "Check sniffer N calibration".

`Alert.id` stabile (`{type}:{room}`) — il frontend deduplica e mantiene `since` tra tick.

#### Payload WS

```json
{
  "t": 12.5, "running": true, "scenario": "concert_peak",
  "rooms": [{"id":"vip","name":"VIP","rect":[700,280,300,220],"density":28,"capacity":25}],
  "doors": [{"id":"d_hall_vip","x0":700,"y0":370,"x1":700,"y1":400,"flow":1.2}],
  "agents": [[x,y,room_id], ...],
  "walls": [...], "obstacles": [...], "decor": [...], "pois": [...],
  "kde_png_b64": "data:image/png;base64,...",
  "estimate_png_b64": "data:image/png;base64,...",
  "alerts": [{"id":"capacity:vip","severity":"critical","type":"capacity",
              "room":"vip","title":"VIP over capacity","description":"28/25 people",
              "suggestion":"Limit flow at d_hall_vip","since":8.2}]
}
```

PNG rigenerate a 2 Hz (non ogni frame). Geometria statica (walls/obstacles/decor) inviata solo al `connect` e a ogni `reset` — non in ogni payload.

### Frontend (no build step)

Layout CSS grid 3 colonne: `[sidebar 56/220px] [main flex] [alerts 340px]`.

| File | Cosa fa |
|------|--------|
| `crowd_mvp/web/static/index.html` | NUOVO — markup: top bar (logo + Play/Pause/Reset + scenario dropdown + badge "Demo data"), hamburger sidebar (4 voci con icone + label che appare on expand), main area (header con tab toggle KDE/Estimate + nome scenario + tempo, SVG mappa + img heatmap overlay, legenda colori), alerts panel (header + filter chips + lista scrollabile). Tailwind via `<script src="https://cdn.tailwindcss.com">`. |
| `crowd_mvp/web/static/js/app.js` | NUOVO — WS client (auto-reconnect su disconnect), state globale (snapshot + tab attiva + filtri), bind dei bottoni control (REST POST), bind del menu hamburger (toggle classe `expanded`). |
| `crowd_mvp/web/static/js/maps.js` | NUOVO — render SVG: stanze (rect + nome centrale), ostacoli (rect tipo-colored, colori coerenti con `config.OBSTACLE_COLORS`), decor (stool/plant come `<circle>`, table come `<rect>`, partition come `<line>`), muri (`<line>` scuro), porte (`<line>` verde), POI (rect + label corto), agenti (`<circle>` r=3 aggiornati ogni snapshot via `selectAll().data()` style update). Tab toggle: swappa l'`<img>` overlay tra `kde_png_b64` e `estimate_png_b64`. |
| `crowd_mvp/web/static/js/alerts.js` | NUOVO — render lista alert card (icona severità + room name + title + description + suggestion in piccolo). Filter chips (All / Critical / Warning). Nuovi alert: fade-in via classe CSS. |
| `crowd_mvp/web/static/css/custom.css` | NUOVO — regole non-Tailwind: animazione fade-in alert, transition slide hamburger, scrollbar custom. |

#### Hamburger collassabile

Stato default: collapsed (56px), solo icone. Click su ☰ → espande a 220px mostrando label, transizione 200ms. Voci non-Safety hanno `aria-disabled="true"` + classe `opacity-40 cursor-not-allowed` + no click handler. Account in fondo con icona avatar.

#### Tab toggle mappe

Sopra l'area mappa: due bottoni segmentati `[KDE Heatmap | WiFi Estimate]`. Stato selezionato evidenziato. Click → cambia solo l'`<img>` overlay (la SVG sotto è la stessa).

### Modifiche minime al codice esistente

| File | Modifica |
|------|----------|
| `crowd_mvp/maps.py` | Aggiungere campo opzionale `capacity` ai room dict di `ROOMED_MAP` (lobby 60, hall 80, bar 30, vip 25, rest 20). Helper `get_room_capacity(map_def, room_id)`. Niente breaking change — capacity manca → detector capacity disabilitato per quel room. |
| `crowd_mvp/config.py` | Aggiungere `ALERT_CAPACITY_WARN=0.8`, `ALERT_CAPACITY_CRIT=1.0`, `ALERT_SURGE_RATIO=0.5`, `ALERT_BOTTLENECK_RATIO=0.5`, `ALERT_EVAC_DISTANCE=300`, `ALERT_DATAQUAL_RATIO=0.3`. |
| `requirements.txt` (o crearlo) | Aggiungere `fastapi`, `uvicorn[standard]`. |

`crowd_mvp/simulation.py`, `crowd_mvp/render.py`, `crowd_mvp/people.py`, `crowd_mvp/main.py` (pygame app) **non vengono toccati**.

### Deployment — Hugging Face Spaces

Target: **HF Spaces con Docker SDK** (l'unico SDK HF che supporta WebSocket persistenti + FastAPI). Conseguenze architetturali che il piano rispetta già:

- **Singolo container, singolo processo**: simulazione e website nello stesso processo Python avviato da `uvicorn`. `SimulationManager` è un **singleton globale** dentro `server.py` — tutti i visitatori vedono la stessa simulazione live. Per il pitch è anzi un vantaggio (effetto "live room": più persone connesse vedono lo stesso evento).
- **Porta 7860** (default HF). Comando di avvio nel container: `uvicorn crowd_mvp.web.server:app --host 0.0.0.0 --port 7860`.
- **No persistenza filesystem**: niente DB, niente file di sessione. Tutto in memoria. Scenari preset sono codice, non dati su disco.
- **Risorse free tier (CPU basic, 16GB RAM)**: il pipeline KDE esistente gira già a ~1 Hz su CPU; verificare in fase di esecuzione che 200 ppl (scenario `concert_peak`) reggano. Se rallenta, ridurre `n_people` per HF o downscalare la griglia KDE in `viz/heatmap.py` (parametri già presenti).
- **Tailwind via CDN**: HF Spaces ha rete outbound, quindi il CDN Tailwind funziona. Stesso per Google Fonts se servono.

#### File aggiuntivi per il deploy

| File | Contenuto |
|------|-----------|
| `Dockerfile` (root) | NUOVO — base `python:3.11-slim`, `apt install` di libsdl2 + dipendenze pygame (servono perché `heatmap_png.py` usa `pygame.image.save`), `COPY` del codice, `pip install -r requirements.txt`, `EXPOSE 7860`, `CMD ["uvicorn", "crowd_mvp.web.server:app", "--host", "0.0.0.0", "--port", "7860"]`. |
| `README.md` (root, frontmatter HF Spaces) | NUOVO/EDIT — frontmatter YAML: `title`, `sdk: docker`, `app_port: 7860`, `pinned: false`. Il contenuto markdown sotto resta come README normale del progetto. HF parsea il frontmatter automaticamente. |
| `.dockerignore` (root) | NUOVO — esclude `__pycache__/`, `.git/`, `.planning/`, `*.pyc`, `crowd_mvp/__pycache__/`, `cymotion.html`. Container snello. |

#### Workflow di deploy

1. Repo GitHub esistente push su un **remote secondario** HF: `git remote add space https://huggingface.co/spaces/<user>/<space-name>`. Il push su `space main` triggera il build su HF.
2. HF rileva il `Dockerfile`, builda, espone su `https://<user>-<space-name>.hf.space`.
3. Aprire l'URL → la Safety UI carica già live.

#### Vincoli architetturali NON applicabili (già rispettati dal piano)

- Niente endpoint multi-tenant per visitatore: una sola `Simulation` condivisa è OK per demo.
- Niente background worker separato: l'asyncio task del `SimulationManager` gira nello stesso event loop di FastAPI.
- Niente reverse proxy / nginx: uvicorn serve direttamente static + API + WS.

### Scenari preset (`scenarios.py`)

Ognuno una funzione `apply_to_manager(manager)`:

- **`baseline`**: 50 ppl, wanderer, σ=2.0 su ROOMED_MAP. Distribuzione naturale, alert sporadici.
- **`concert_peak`**: 200 ppl, social, σ=1.5. Cluster forti → surge + capacity exceeded su VIP e Bar.
- **`evacuation_drill`**: 150 ppl, behavior `goal` con override runtime: `_GOAL_CATEGORIES = ('exit',)` (monkey-patch su istanze GoalAgent appena create). Tutti puntano POI exit della lobby → evacuation risk + bottleneck su d_lobby_hall.

## File critici

| File | Stato |
|------|-------|
| `crowd_mvp/web/__init__.py` | NUOVO |
| `crowd_mvp/web/server.py` | NUOVO (FastAPI app) |
| `crowd_mvp/web/state.py` | NUOVO (SimulationManager + async loop + broadcast) |
| `crowd_mvp/web/alerts.py` | NUOVO (5 detector + history) |
| `crowd_mvp/web/scenarios.py` | NUOVO (3 preset) |
| `crowd_mvp/web/heatmap_png.py` | NUOVO (Surface → PNG base64) |
| `crowd_mvp/web/static/index.html` | NUOVO |
| `crowd_mvp/web/static/js/app.js` | NUOVO |
| `crowd_mvp/web/static/js/maps.js` | NUOVO |
| `crowd_mvp/web/static/js/alerts.js` | NUOVO |
| `crowd_mvp/web/static/css/custom.css` | NUOVO |
| `crowd_mvp/maps.py` | EDIT — capacity opzionale + helper |
| `crowd_mvp/config.py` | EDIT — soglie alert |
| `requirements.txt` | NUOVO o EDIT — fastapi + uvicorn |
| `Dockerfile` | NUOVO (HF Spaces deploy) |
| `README.md` | NUOVO/EDIT — frontmatter YAML per HF Spaces |
| `.dockerignore` | NUOVO |

Codice esistente riusato senza modifiche:
- `crowd_mvp.simulation.Simulation` — istanziato dal manager, chiamato `update()` + `get_snapshot()` + `get_room_density()` + `get_door_flow()` + `get_zone_counts()`
- `crowd_mvp.viz.heatmap.build_heatmap_surface` — usato dentro `heatmap_png.py` per KDE
- `crowd_mvp.maps.ROOMED_MAP` + helper esistenti (`build_room_graph`, `find_room_for_point`)

## Verifica

1. **Avvio**: `uvicorn crowd_mvp.web.server:app --reload --port 8000`. Apri `http://localhost:8000` — Safety screen carica entro 1s, hamburger visibile, mappa già live con `baseline`.
2. **Live data flow**: SVG mostra agenti che si muovono, heatmap KDE aggiornata ogni ~500ms, alerts compaiono entro 5s.
3. **Tab toggle mappe**: click su "WiFi Estimate" → cambia solo l'overlay, geometrie sotto restano. Click su "KDE Heatmap" → torna.
4. **Scenario switch**: dropdown "Concert peak" → entro 10s vedere critical capacity su VIP + surge su Bar nel pannello alerts.
5. **Pause/Resume/Reset**: i bottoni controllano la sim. Reset spinge i client a riconnettersi e ricevere snapshot iniziale.
6. **Hamburger**: click su ☰ → espande mostrando label. Voci disabled non cliccabili (verifica visivo + tentativo di click che non naviga).
7. **Alert filter**: chip "Critical" → solo critical visibili.
8. **Backend isolato**: `python -c "import asyncio; from crowd_mvp.web.state import SimulationManager; m = SimulationManager(); asyncio.run(m.run_for(3.0)); print(len(m.last_snapshot()['alerts']))"` — stampa numero alert dopo 3s.
9. **Unit test detector**: snapshot finto con `density={'vip': 30}` + `capacity={'vip': 25}` → `AlertEngine.evaluate(snap)` deve restituire alert con `id='capacity:vip'` e `severity='critical'`.
10. **Docker build locale**: `docker build -t cymotion-safety .` poi `docker run -p 7860:7860 cymotion-safety` — aprire `http://localhost:7860` e ripetere i passi 1-7. Se passa qui passerà su HF Spaces.
11. **Deploy su HF Spaces**: push del repo (incluso `Dockerfile` e `README.md`) sul remote `space` → attendere build (~3-5 min) → aprire `https://<user>-<space-name>.hf.space` → ripetere passi 1-7 sulla URL pubblica.
