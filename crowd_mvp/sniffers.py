# crowd_mvp/sniffers.py
# Sniffer class: counts agents in its zone + adds Gaussian noise (SNF-02).
# σ is a uniform global parameter (SNF-03). Per-node σ hook left in code as comment.
# Sniffer exposes: zone_id, position, estimated_count, timestamp (SNF-04).

import numpy as np
from crowd_mvp.config import SIGMA_ERROR


class Sniffer:
    """WiFi sniffer node placed at the centre of one map zone.

    Attributes:
        zone_id (str):          zone this sniffer covers (e.g. 'A')
        pos (tuple):            (x, y) pixel position of sniffer icon (SNF-01)
        sigma (float):          Gaussian noise std dev (SNF-03, uniform default)
        estimated_count (int):  last computed noisy estimate (SNF-04)
        real_count (int):       last actual agent count in zone (ground truth)
        timestamp (int):        frame number of last tick (SNF-04)

    Note:
        σ-per-node hook: to enable heterogeneous noise in future (SIM-V2-02),
        pass per-node sigma values instead of the global SIGMA_ERROR default.
        # σ-per-node hook: replace `sigma=SIGMA_ERROR` arg with per-node dict lookup
    """

    def __init__(self, zone_id, pos, sigma=SIGMA_ERROR):
        """
        Args:
            zone_id: str identifier matching a zone in the map definition
            pos:     (x, y) pixel tuple — centre of the zone (SNF-01)
            sigma:   Gaussian noise std dev; defaults to global SIGMA_ERROR (SNF-03)
                     # σ-per-node hook: caller can pass per-node value here
        """
        self.zone_id = zone_id
        self.pos = pos
        self.sigma = sigma       # σ-per-node hook: stored per instance for future override
        self.estimated_count = 0
        self.real_count = 0
        self.timestamp = 0       # frame number of last tick (SNF-04)

    def tick(self, agents, map_def, frame_number):
        """Count agents in zone and compute noisy estimate. Call once per second (SNF-02).

        Formula (SNF-02): estimated = max(0, round(real_count + N(0, σ)))

        Args:
            agents:       list of Agent instances
            map_def:      map definition dict (used to determine zone membership)
            frame_number: current frame number (stored as timestamp)
        """
        from crowd_mvp.maps import find_zone_for_point

        # Count real agents in this zone
        real = sum(
            1 for a in agents
            if find_zone_for_point(map_def, a.x, a.y) == self.zone_id
        )
        self.real_count = real
        self.timestamp = frame_number

        # Add Gaussian noise — SNF-02 formula
        noise = np.random.normal(0.0, self.sigma)
        self.estimated_count = max(0, round(real + noise))

    @property
    def data(self):
        """Return SNF-04 tuple: (zone_id, position, estimated_count, timestamp)."""
        return (self.zone_id, self.pos, self.estimated_count, self.timestamp)
