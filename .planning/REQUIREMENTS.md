# Requirements: Crowd Monitoring Simulator MVP

**Defined:** 2026-05-08
**Core Value:** Il confronto "realtà vs stima WiFi sniffing" deve essere visivamente convincente e immediatamente comprensibile in 30 secondi

## v1 Requirements

### Maps

- [ ] **MAP-01**: Utente può selezionare mappa small (600×400 px, 4 zone/sniffer, 5 POI) prima o durante la simulazione
- [ ] **MAP-02**: Utente può selezionare mappa medium (900×600 px, 8 zone/sniffer, 10 POI)
- [ ] **MAP-03**: Utente può selezionare mappa large (1200×800 px, 12 zone/sniffer, 15 POI)
- [ ] **MAP-04**: Ogni mappa ha zone rettangolari adiacenti che coprono l'intera planimetria
- [ ] **MAP-05**: Ogni mappa ha POI delle categorie: ingresso/biglietteria, uscita, stand sponsor, bar, bagno

### Simulation

- [ ] **SIM-01**: Ogni persona è un agente con posizione (x,y), velocità e behavior assegnato
- [ ] **SIM-02**: Behavior "Wanderer": random walk con attrazione verso POI casuali, cambia target ogni N secondi
- [ ] **SIM-03**: Behavior "Goal-oriented": sceglie POI (bar/bagno/stand), ci va, sosta, poi sceglie altro POI
- [ ] **SIM-04**: Behavior "Social/clusterer": si muove verso aree ad alta densità di altre persone
- [ ] **SIM-05**: Le persone restano nei bordi della planimetria (nessun muro interno)
- [ ] **SIM-06**: Numero di persone configurabile via slider (default: 50 small / 150 medium / 300 large)
- [ ] **SIM-07**: Simulazione si ferma automaticamente allo scadere del tempo (default 5 min) mostrando "Simulation complete"

### Sniffers

- [ ] **SNF-01**: Ogni sniffer è posizionato al centro della propria zona
- [ ] **SNF-02**: Ogni secondo, ogni sniffer conta le persone nella sua zona e aggiunge rumore: `stima = max(0, round(count_reale + N(0, σ)))`
- [ ] **SNF-03**: σ è un parametro globale configurabile via slider dalla UI (stesso valore per tutti i nodi)
- [ ] **SNF-04**: Ogni sniffer espone (zone_id, position, estimated_count, timestamp)

### Visualization

- [ ] **VIZ-01**: Tab 1 — Heatmap KDE bivariato calcolata dalle stime sniffer, aggiornata in tempo reale, sovrapposta alla mappa con alpha blending (colormap viridis o hot)
- [ ] **VIZ-02**: Tab 2 — Confronto ground truth (persone reali + zone colorate per count_reale) vs stima (zone colorate per estimated_count), split-screen o overlay semitrasparente
- [ ] **VIZ-03**: Tab 3 — Matrice di traffico accumulata nel tempo, renderizzata come heatmap (colormap plasma), con traiettorie di un subset di persone come linee colorate
- [ ] **VIZ-04**: Icone sniffer sempre visibili sulla mappa in tutte e tre le tab
- [ ] **VIZ-05**: Switching tra tab con tasti 1/2/3 o bottoni nella UI

### Controls

- [ ] **CTR-01**: Pannello laterale sempre visibile con: selezione mappa, selezione behavior, slider n_people, slider σ_error, slider σ_kernel
- [ ] **CTR-02**: Bottoni Start / Pause / Reset funzionanti
- [ ] **CTR-03**: Display tempo trascorso / tempo totale simulazione
- [ ] **CTR-04**: Input/slider durata simulazione (default 300 secondi)

### Loop

- [ ] **LOOP-01**: Main loop a 60 FPS: aggiorna posizioni persone, renderizza mappa + persone + sniffer + tab attiva + UI
- [ ] **LOOP-02**: Ogni 60 frame (1 secondo simulato): ricalcola stime sniffer, aggiorna matrice traffico

## v2 Requirements

### Advanced Simulation

- **SIM-V2-01**: Distribuzione configurabile dei behavior per persona (% wanderer / % goal / % social)
- **SIM-V2-02**: σ diverso per ogni nodo sniffer (già hook nel codice)
- **SIM-V2-03**: Muri interni e ostacoli nella planimetria

### Export

- **EXP-V2-01**: Export screenshot/video della simulazione
- **EXP-V2-02**: Export CSV delle stime sniffer nel tempo

## Out of Scope

| Feature | Reason |
|---------|--------|
| Backend / web server | Single-process local app per design — niente setup per il pitch |
| Database | Nessuna persistenza necessaria nell'MVP |
| Real WiFi/BT sniffing | È un simulatore, non il prodotto finale |
| Mobile app | Desktop-only per il pitch |
| Muri interni complessi | Complessità non necessaria nell'MVP — solo bordi mappa |
| Multi-processo / threading | Single-process per semplicità |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| MAP-01 | Phase 2 | Pending |
| MAP-02 | Phase 2 | Pending |
| MAP-03 | Phase 2 | Pending |
| MAP-04 | Phase 2 | Pending |
| MAP-05 | Phase 2 | Pending |
| SIM-01 | Phase 1 | Pending |
| SIM-02 | Phase 1 | Pending |
| SIM-03 | Phase 2 | Pending |
| SIM-04 | Phase 2 | Pending |
| SIM-05 | Phase 1 | Pending |
| SIM-06 | Phase 1 | Pending |
| SIM-07 | Phase 1 | Pending |
| SNF-01 | Phase 1 | Pending |
| SNF-02 | Phase 1 | Pending |
| SNF-03 | Phase 1 | Pending |
| SNF-04 | Phase 1 | Pending |
| VIZ-01 | Phase 2 | Pending |
| VIZ-02 | Phase 3 | Pending |
| VIZ-03 | Phase 3 | Pending |
| VIZ-04 | Phase 1 | Pending |
| VIZ-05 | Phase 2 | Pending |
| CTR-01 | Phase 2 | Pending |
| CTR-02 | Phase 3 | Pending |
| CTR-03 | Phase 3 | Pending |
| CTR-04 | Phase 3 | Pending |
| LOOP-01 | Phase 1 | Pending |
| LOOP-02 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-08*
*Last updated: 2026-05-08 after roadmap creation*
