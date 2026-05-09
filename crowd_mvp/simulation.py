# crowd_mvp/simulation.py
# Simulation class: owns agents, sniffers, frame counter, and scene render.
# D-09: main.py creates Simulation and calls sim.update() + sim.draw(surface) each frame.
# LOOP-01: update advances positions every frame; draw renders map + agents + sniffers.
# LOOP-02: every SNIFFER_TICK_FRAMES frames, sniffers recount and update estimates.
# SIM-07: after duration seconds, sim stops updating and shows "Simulation complete".

import math

import pygame

from crowd_mvp.config import (
    FPS, N_PEOPLE, SIM_DURATION, SIGMA_ERROR, SNIFFER_TICK_FRAMES,
    AGENT_RADIUS,
    COLOUR_BG, COLOUR_ZONE_FILL, COLOUR_ZONE_BORDER,
    COLOUR_AGENT, COLOUR_SNIFFER,
    COLOUR_POI_ENTRANCE, COLOUR_POI_EXIT, COLOUR_POI_BAR,
    COLOUR_POI_STAND, COLOUR_POI_BATHROOM,
    COLOUR_OVERLAY_BG, COLOUR_TEXT, COLOUR_LABEL,
    FONT_SIZE_LABEL, FONT_SIZE_OVERLAY,
)
from crowd_mvp.maps import get_sniffer_positions, find_zone_for_point
from crowd_mvp.people import Agent, GoalAgent, SocialAgent, WandererAgent
from crowd_mvp.sniffers import Sniffer


# POI category -> colour lookup
_POI_COLOURS = {
    'entrance':      COLOUR_POI_ENTRANCE,
    'exit':          COLOUR_POI_EXIT,
    'bar':           COLOUR_POI_BAR,
    'sponsor_stand': COLOUR_POI_STAND,
    'bathroom':      COLOUR_POI_BATHROOM,
}

# POI category -> short label text
_POI_LABELS = {
    'entrance':      'EN',
    'exit':          'EX',
    'bar':           'BAR',
    'sponsor_stand': 'STD',
    'bathroom':      'WC',
}


class Simulation:
    """Central simulation orchestrator.

    Usage:
        sim = Simulation(map_def, n_people=50, sigma=2.0, duration=300)
        # each frame:
        sim.update()
        sim.draw(screen_surface)
        if sim.is_complete:
            ...
    """

    def __init__(self, map_def, n_people=N_PEOPLE, sigma=SIGMA_ERROR, duration=SIM_DURATION, behavior='wanderer'):
        """
        Args:
            map_def:   map definition dict (SMALL_MAP or future maps)
            n_people:  number of agents to spawn (SIM-06)
            sigma:     Gaussian noise std dev for all sniffers (SNF-03)
            duration:  seconds before auto-stop (SIM-07)
            behavior:  agent behavior type: 'wanderer' | 'goal' | 'social' (D-09)
        """
        self.map_def = map_def
        self.n_people = n_people
        self.sigma = sigma
        self.duration = duration
        self.duration_frames = int(duration * FPS)

        self.behavior = behavior  # 'wanderer' | 'goal' | 'social'
        self.frame_count = 0
        self._complete = False

        # Pygame font — initialised lazily on first draw() call
        self._font_label = None
        self._font_overlay = None

        map_size = map_def['size']
        poi_list = map_def['poi']
        map_w, map_h = map_size

        # Select agent class by behavior (D-09: all agents share one behavior per run)
        _AGENT_CLASSES = {
            'wanderer': WandererAgent,
            'goal':     GoalAgent,
            'social':   SocialAgent,
        }
        agent_cls = _AGENT_CLASSES.get(behavior, WandererAgent)
        self._is_social = (behavior == 'social')

        # Spawn agents at random positions across the map with a small margin.
        # Spreading them out avoids the "explosion from entrance" burst and is
        # critical for SocialAgent: if all agents spawn at the same pixel, the
        # centroid equals self.pos and they never escape (stuck at spawn).
        import random as _random
        margin = 20
        self.agents = [
            agent_cls(
                (_random.uniform(margin, map_w - margin),
                 _random.uniform(margin, map_h - margin)),
                poi_list, map_size
            )
            for _ in range(n_people)
        ]

        # Create sniffers at zone centres (SNF-01)
        sniffer_defs = get_sniffer_positions(map_def)
        self.sniffers = [
            Sniffer(s['zone_id'], s['pos'], sigma=sigma)
            for s in sniffer_defs
        ]

        # Traffic matrix: accumulated zone-to-zone transition counts (D-05).
        # Keys: zone_id strings from map_def['zones'].
        zone_ids = [z['id'] for z in map_def['zones']]
        self._zone_ids = zone_ids
        # matrix[i][j] = count of transitions from zone_ids[i] to zone_ids[j]
        self.traffic_matrix = {zi: {zj: 0 for zj in zone_ids} for zi in zone_ids}

        # Tracked agents subset: randomly select 10-15 agents (D-07).
        import random as _rnd2
        n_track = min(len(self.agents), _rnd2.randint(10, 15))
        self.tracked_agents = _rnd2.sample(self.agents, n_track)
        for a in self.tracked_agents:
            a._track = True
            a.pos_history.append((a.x, a.y))  # seed with initial position

        # Per-agent last-known zone for transition detection (D-05).
        self._agent_last_zone = {}
        for a in self.agents:
            zid = find_zone_for_point(map_def, a.x, a.y)
            self._agent_last_zone[id(a)] = zid

    @property
    def is_complete(self):
        """True after duration has elapsed (SIM-07)."""
        return self._complete

    def update(self):
        """Advance simulation one frame (LOOP-01).

        - If complete, do nothing.
        - Update all agent positions.
        - Every SNIFFER_TICK_FRAMES, tick all sniffers (LOOP-02).
        - Check for end condition (SIM-07).
        """
        if self._complete:
            return

        # Advance all agents (D-09: behavior-specific update)
        if self._is_social:
            for agent in self.agents:
                agent.update_social(self.agents)
        else:
            for agent in self.agents:
                agent.update()

        # Sniffer tick every ~1 second (D-10, LOOP-02)
        if self.frame_count % SNIFFER_TICK_FRAMES == 0:
            self._tick_sniffers()
            self._update_traffic_matrix()  # D-05: per-tick is sufficient; matrix only read at tick cadence

        self.frame_count += 1

        # Auto-stop check (SIM-07)
        if self.frame_count >= self.duration_frames:
            self._complete = True

    def _tick_sniffers(self):
        """Recount agents per zone and update noisy estimates (LOOP-02)."""
        for sniffer in self.sniffers:
            sniffer.tick(self.agents, self.map_def, self.frame_count)

    def _update_traffic_matrix(self):
        """Detect agent zone transitions and increment traffic_matrix[from][to] (D-05)."""
        for agent in self.agents:
            aid = id(agent)
            current_zone = find_zone_for_point(self.map_def, agent.x, agent.y)
            prev_zone = self._agent_last_zone.get(aid)
            if (current_zone is not None and prev_zone is not None
                    and current_zone != prev_zone
                    and current_zone in self.traffic_matrix
                    and prev_zone in self.traffic_matrix):
                self.traffic_matrix[prev_zone][current_zone] += 1
            if current_zone is not None:
                self._agent_last_zone[aid] = current_zone

    def get_heatmap_data(self):
        """Return sniffer positions and estimated counts for heatmap rendering (D-16).

        Called by main.py every sniffer tick (same cadence as _tick_sniffers).
        Returns data in native map pixel coordinates — main.py applies scale transform.

        Returns:
            positions: list of (x, y) tuples — sniffer positions in map pixels
            counts:    list of float         — estimated_count per sniffer (same order)
        """
        positions = [s.pos for s in self.sniffers]
        counts = [float(s.estimated_count) for s in self.sniffers]
        return positions, counts

    def get_zone_counts(self):
        """Return real and estimated agent counts keyed by zone_id (D-01, D-04).

        Returns:
            real_counts:      dict[zone_id -> int]  — ground truth from sniffers
            estimated_counts: dict[zone_id -> int]  — noisy sniffer estimates
        """
        real_counts      = {s.zone_id: s.real_count      for s in self.sniffers}
        estimated_counts = {s.zone_id: s.estimated_count for s in self.sniffers}
        return real_counts, estimated_counts

    @property
    def map_size(self):
        """Native map size (width, height) in pixels."""
        return self.map_def['size']

    def draw(self, surface):
        """Render entire scene to surface (LOOP-01).

        Draw order (back-to-front):
          1. Background fill
          2. Zone fills and borders
          3. POI icons and labels
          4. Agent dots
          5. Sniffer WiFi icons and count labels
          6. Completion overlay (if complete)
        """
        self._ensure_fonts()

        # 1. Background
        surface.fill(COLOUR_BG)

        map_w, map_h = self.map_def['size']

        # 2. Zones (D-08)
        for zone in self.map_def['zones']:
            x, y, w, h = zone['rect']
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(surface, COLOUR_ZONE_FILL, rect)
            pygame.draw.rect(surface, COLOUR_ZONE_BORDER, rect, 1)

        # 3. POI icons and labels (D-14)
        for poi in self.map_def['poi']:
            colour = _POI_COLOURS.get(poi['category'], (200, 200, 200))
            px, py = poi['pos']
            # Small filled square, 8x8 px centred on pos
            poi_rect = pygame.Rect(px - 4, py - 4, 8, 8)
            pygame.draw.rect(surface, colour, poi_rect)
            # Short label below
            label = _POI_LABELS.get(poi['category'], '?')
            txt_surf = self._font_label.render(label, True, COLOUR_LABEL)
            surface.blit(txt_surf, (px - txt_surf.get_width() // 2, py + 6))

        # 4. Agents — filled circles (D-05)
        for agent in self.agents:
            pygame.draw.circle(surface, COLOUR_AGENT, (agent.x, agent.y), AGENT_RADIUS)

        # 5. Sniffer icons and count labels (D-06, D-07, VIZ-04)
        for sniffer in self.sniffers:
            self._draw_sniffer(surface, sniffer)

        # 6. End overlay (D-11, SIM-07)
        if self._complete:
            self._draw_completion_overlay(surface, map_w, map_h)

    def draw_map_scaled(self, surface, canvas_w, canvas_h):
        """Render map geometry only (zones + POI) scaled to fit canvas — no agents or sniffers.

        Used as the underlay for the heatmap right panel.
        """
        map_w, map_h = self.map_def['size']
        scale = min(canvas_w / map_w, canvas_h / map_h)

        surface.fill(COLOUR_BG)

        for zone in self.map_def.get('zones', []):
            x, y, w, h = zone['rect']
            scaled_rect = pygame.Rect(int(x * scale), int(y * scale),
                                      int(w * scale), int(h * scale))
            pygame.draw.rect(surface, COLOUR_ZONE_FILL, scaled_rect)
            pygame.draw.rect(surface, COLOUR_ZONE_BORDER, scaled_rect, 1)

        for poi in self.map_def.get('poi', []):
            px, py = poi['pos']
            colour = _POI_COLOURS.get(poi['category'], (200, 200, 200))
            pygame.draw.circle(surface, colour,
                               (int(px * scale), int(py * scale)),
                               max(3, int(6 * scale)))

    def draw_scaled(self, surface, canvas_w, canvas_h):
        """Render simulation to surface scaled to fit canvas_w x canvas_h (D-05).

        Computes a uniform scale factor so the native map fits within the canvas
        without overflow. All coordinates — zones, POI, agents, sniffers — are
        transformed before drawing. Called by main.py instead of draw() for the
        left panel.

        Args:
            surface:   pygame.Surface to draw onto (subsurface of left panel)
            canvas_w:  int — target canvas width in pixels (e.g. CANVAS_W = 600)
            canvas_h:  int — target canvas height in pixels (e.g. CANVAS_H = 400)
        """
        map_w, map_h = self.map_def['size']
        scale = min(canvas_w / map_w, canvas_h / map_h)

        # Background
        surface.fill(self.map_def.get('bg_colour', (30, 30, 30)))

        # Zones
        for zone in self.map_def.get('zones', []):
            x, y, w, h = zone['rect']
            scaled_rect = pygame.Rect(
                int(x * scale), int(y * scale),
                int(w * scale), int(h * scale),
            )
            colour = zone.get('colour', (60, 60, 80))
            pygame.draw.rect(surface, colour, scaled_rect)
            pygame.draw.rect(surface, (100, 100, 120), scaled_rect, 1)

            # Zone label (optional)
            label = zone.get('label')
            if label and hasattr(self, '_font_zone'):
                txt = self._font_zone.render(label, True, (200, 200, 200))
                surface.blit(txt, (scaled_rect.x + 2, scaled_rect.y + 2))

        # POI markers
        for poi in self.map_def.get('pois', self.map_def.get('poi', [])):
            px, py = poi['pos']
            pygame.draw.circle(
                surface, (255, 220, 50),
                (int(px * scale), int(py * scale)),
                max(3, int(6 * scale)),
            )

        # Agents
        for agent in self.agents:
            ax = int(agent.x * scale)
            ay = int(agent.y * scale)
            r = max(2, int(3 * scale))
            pygame.draw.circle(surface, (220, 220, 255), (ax, ay), r)

        # Sniffers
        for sniffer in self.sniffers:
            sx = int(sniffer.pos[0] * scale)
            sy = int(sniffer.pos[1] * scale)
            sr = max(4, int(8 * scale))
            pygame.draw.circle(surface, (80, 200, 120), (sx, sy), sr, 2)
            # Estimated count label
            if hasattr(self, '_font_sniffer'):
                ct = self._font_sniffer.render(str(sniffer.estimated_count), True, (80, 200, 120))
                surface.blit(ct, (sx + sr + 1, sy - ct.get_height() // 2))

    def _ensure_fonts(self):
        """Initialise fonts on first draw call (Pygame must already be initialised)."""
        if self._font_label is None:
            self._font_label = pygame.font.SysFont(None, FONT_SIZE_LABEL)
        if self._font_overlay is None:
            self._font_overlay = pygame.font.SysFont(None, FONT_SIZE_OVERLAY)

    def _draw_sniffer(self, surface, sniffer):
        """Draw WiFi arc icon + count label for one sniffer (D-06, D-07, VIZ-04).

        WiFi icon: 3 concentric arcs at radii 6, 10, 14 px, centred on sniffer.pos.
        Arcs span a ~90 deg fan pointing upward (Pygame y-axis flipped: angles 225 to 315 deg).
        Count label: estimated_count integer drawn directly below icon (D-07).
        """
        sx, sy = sniffer.pos

        # Draw 3 arcs of increasing radius (D-06)
        for r in (6, 10, 14):
            rect = pygame.Rect(sx - r, sy - r, r * 2, r * 2)
            # Arc fan pointing upward: 225 deg to 315 deg in Pygame convention
            # (Pygame angles: 0=right, CCW positive; screen y flips so 225-315 = upward fan)
            pygame.draw.arc(surface, COLOUR_SNIFFER, rect,
                            math.radians(225), math.radians(315), 2)

        # Centre dot
        pygame.draw.circle(surface, COLOUR_SNIFFER, (sx, sy), 3)

        # Count label (D-07): raw integer below icon
        count_str = str(sniffer.estimated_count)
        txt_surf = self._font_label.render(count_str, True, COLOUR_SNIFFER)
        surface.blit(txt_surf, (sx - txt_surf.get_width() // 2, sy + 16))

    def _draw_completion_overlay(self, surface, map_w, map_h):
        """Semi-transparent dark overlay with 'Simulation complete' text (D-11)."""
        overlay = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        overlay.fill(COLOUR_OVERLAY_BG)
        surface.blit(overlay, (0, 0))

        msg = self._font_overlay.render("Simulation complete", True, COLOUR_TEXT)
        cx = map_w // 2 - msg.get_width() // 2
        cy = map_h // 2 - msg.get_height() // 2
        surface.blit(msg, (cx, cy))
