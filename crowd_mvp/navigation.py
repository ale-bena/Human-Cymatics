# crowd_mvp/navigation.py
# Path planning + wall collision for agents that must respect rooms and doors.
# Pure python/numpy — no pygame. Used by people.py during update().
#
# Public surface:
#   astar(graph, start_room, end_room, room_centers) -> list[str]
#   build_waypoints(path, graph, target_pos) -> list[tuple[float, float]]
#   clip_to_walls(pos, intended_pos, walls, eps=1.0) -> tuple[float, float]
#   segment_intersection(p1, p2, p3, p4) -> tuple[float, float] | None

import heapq
import math


def _euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def astar(graph, start_room, end_room, room_centers):
    """Find a shortest room sequence from start_room to end_room.

    Args:
        graph: {room_id: [(neighbor_room_id, door_id, (cx, cy)), ...]}
        start_room: room id where the agent currently is
        end_room:   room id containing the target POI
        room_centers: {room_id: (cx, cy)} used for the heuristic + edge cost

    Returns:
        list[str] of room ids from start to end inclusive, or [start_room] if
        start == end, or [] if no path exists / start is unknown.
    """
    if start_room == end_room:
        return [start_room]
    if start_room not in graph or end_room not in graph:
        return []

    # A* with f = g + h, h = euclidean(room_center, end_center)
    end_center = room_centers.get(end_room)
    open_heap = []
    counter = 0  # tie-breaker so heapq doesn't compare dicts
    heapq.heappush(open_heap, (0.0, counter, start_room))
    came_from = {start_room: None}
    g_score = {start_room: 0.0}

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current == end_room:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            return list(reversed(path))

        cur_center = room_centers.get(current)
        for neighbor, _door_id, door_center in graph.get(current, []):
            # Edge cost: distance from current room center through door to neighbor center
            n_center = room_centers.get(neighbor)
            if cur_center is None or n_center is None:
                step_cost = 1.0
            else:
                step_cost = _euclid(cur_center, door_center) + _euclid(door_center, n_center)
            tentative_g = g_score[current] + step_cost
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h = _euclid(n_center, end_center) if (n_center and end_center) else 0.0
                counter += 1
                heapq.heappush(open_heap, (tentative_g + h, counter, neighbor))

    return []  # no path


def build_waypoints(path, graph, target_pos):
    """Turn a room path into a list of (x, y) waypoints ending at target_pos.

    For path [r0, r1, ..., rn]: emits the door center between each adjacent
    pair, then target_pos as the final waypoint. If path has length <= 1 the
    only waypoint is target_pos itself (target in same room as agent).

    Args:
        path: list of room ids (output of astar)
        graph: same adjacency as astar
        target_pos: (x, y) final destination — POI position

    Returns:
        list[tuple[float, float]]
    """
    waypoints = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        # Find door connecting a -> b
        door_center = None
        for neighbor, _door_id, center in graph.get(a, []):
            if neighbor == b:
                door_center = center
                break
        if door_center is not None:
            waypoints.append((float(door_center[0]), float(door_center[1])))
    waypoints.append((float(target_pos[0]), float(target_pos[1])))
    return waypoints


def segment_intersection(p1, p2, p3, p4):
    """Return intersection point of segments p1->p2 and p3->p4, or None.

    Standard 2D segment-segment intersection by parametric form. Endpoints
    touching (t in {0, 1}) count as intersections.
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None  # parallel or coincident
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def clip_to_walls(pos, intended_pos, walls, eps=1.0, max_iter=2):
    """Clip movement against walls, sliding along surfaces when blocked.

    On contact with a wall, the agent stops eps pixels short and the residual
    displacement is projected onto the wall's tangent — so the agent slides
    along the surface instead of bunching against its face. max_iter caps the
    number of slide bounces per frame (handles L-shaped corners).

    Args:
        pos: (x, y) current position
        intended_pos: (x, y) where the agent wants to go this frame
        walls: iterable of {'x0','y0','x1','y1'} dicts
        eps: pixels to back off from each wall on contact
        max_iter: maximum number of contact bounces resolved per call

    Returns:
        (x, y) — clipped/slid position
    """
    for _ in range(max_iter):
        dx = intended_pos[0] - pos[0]
        dy = intended_pos[1] - pos[1]
        seg_len = math.hypot(dx, dy)
        if seg_len < 1e-6:
            return pos

        # Find the nearest wall this movement would cross
        nearest_t = 1.0
        hit_wall = None
        for w in walls:
            ipt = segment_intersection(
                pos, intended_pos,
                (w['x0'], w['y0']), (w['x1'], w['y1']),
            )
            if ipt is None:
                continue
            t_hit = ((ipt[0] - pos[0]) * dx + (ipt[1] - pos[1]) * dy) / (seg_len * seg_len)
            if t_hit < nearest_t:
                nearest_t = t_hit
                hit_wall = w

        if hit_wall is None:
            return intended_pos  # clear path

        # Stop just before the wall
        t_clipped = max(0.0, nearest_t - eps / seg_len)
        new_pos = (pos[0] + t_clipped * dx, pos[1] + t_clipped * dy)

        # Project the remaining displacement onto the wall's tangent (slide)
        t_residual = 1.0 - t_clipped
        if t_residual <= 1e-6:
            return new_pos
        wx = hit_wall['x1'] - hit_wall['x0']
        wy = hit_wall['y1'] - hit_wall['y0']
        w_len = math.hypot(wx, wy)
        if w_len < 1e-6:
            return new_pos
        tx = wx / w_len
        ty = wy / w_len
        res_dx = dx * t_residual
        res_dy = dy * t_residual
        dot = res_dx * tx + res_dy * ty
        slide_dx = dot * tx
        slide_dy = dot * ty

        # Next iteration tries the slide displacement (might hit another wall)
        pos = new_pos
        intended_pos = (new_pos[0] + slide_dx, new_pos[1] + slide_dy)

    return intended_pos
