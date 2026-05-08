---
phase: 02-full-venue-heatmap
plan: "02"
subsystem: agent-behaviors
tags: [agents, behavior, goal-oriented, social, clustering, people]
dependency_graph:
  requires: []
  provides: [GoalAgent, SocialAgent, WandererAgent]
  affects: [crowd_mvp/simulation.py]
tech_stack:
  added: []
  patterns: [inheritance override, pre-super init pattern, K-nearest centroid steering]
key_files:
  created: []
  modified:
    - crowd_mvp/people.py
decisions:
  - "_goal_pois must be set before super().__init__() because Agent.__init__ calls _pick_random_poi() which GoalAgent overrides to call _pick_goal_poi()"
  - "SocialAgent uses update_social(agents) method instead of update() to avoid circular list reference in __init__"
  - "np.argpartition used for O(N) K-nearest selection — avoids O(N log N) full sort"
metrics:
  duration: "~5 min"
  completed: "2026-05-08"
  tasks_completed: 2
  files_changed: 1
---

# Phase 2 Plan 02: Agent Behaviors (GoalAgent + SocialAgent) Summary

Three visually-distinguishable movement behaviors in people.py: Wanderer (existing Agent), GoalAgent steering exclusively to venue feature POIs, and SocialAgent clustering to K=10 nearest neighbours centroid.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add GoalAgent class | 830292f | crowd_mvp/people.py |
| 2 | Add SocialAgent class and WandererAgent alias | aba0c70 | crowd_mvp/people.py |

## What Was Built

**GoalAgent** (SIM-03, D-06): Subclasses Agent. Filters poi_list to bar/sponsor_stand/bathroom categories only, overrides `_pick_random_poi()` to always target these venue-feature POIs. Agents concentrate at bar, sponsor stand, and bathroom — producing visible POI clustering in the heatmap (D-08).

**SocialAgent** (SIM-04, D-07): Subclasses Agent. Each frame calls `update_social(agents)` with the full agent list — finds K=10 nearest neighbours via `np.argpartition`, steers toward their centroid at 60% of normal speed plus jitter. Produces emergent crowd clumping visible in the heatmap.

**WandererAgent = Agent**: Module-level alias for backward compatibility and clarity in simulation.py imports.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed GoalAgent initialization order**
- **Found during:** Task 1 verification
- **Issue:** Plan's GoalAgent `__init__` called `super().__init__()` before setting `self._goal_pois`. Since `Agent.__init__()` calls `self._pick_random_poi()`, and GoalAgent overrides that to call `self._pick_goal_poi()`, which reads `self._goal_pois` — this caused `AttributeError: 'GoalAgent' object has no attribute '_goal_pois'`
- **Fix:** Moved `self._goal_pois = [...]` initialization to before `super().__init__()` call. Removed the now-redundant explicit `self.target_pos = self._pick_goal_poi()` line since `super().__init__()` already calls `_pick_random_poi()` which delegates to `_pick_goal_poi()`
- **Files modified:** crowd_mvp/people.py
- **Commit:** 830292f

## Known Stubs

None — both agent classes are fully functional with no placeholder data.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. All code is in-process single-threaded simulation logic.

## Self-Check: PASSED

- crowd_mvp/people.py: FOUND
- .planning/phases/02-full-venue-heatmap/02-02-SUMMARY.md: FOUND
- Commit 830292f (GoalAgent): FOUND
- Commit aba0c70 (SocialAgent + WandererAgent): FOUND
