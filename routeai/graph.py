"""Road graph + A* search + travel model."""
from __future__ import annotations
import heapq
from .geo import haversine_km

ROAD_FACTOR = 1.3  # road distance is longer than straight line

# mode: (speed km/h, cost INR per km)
MODES = {
    "walk": (4.5, 0.0),
    "bike": (25.0, 3.0),
    "auto": (20.0, 15.0),
    "cab": (24.0, 14.0),
}


class RoadGraph:
    """Sparse graph: each node linked to its k nearest nodes, then
    components are bridged so the graph is always connected."""

    def __init__(self, coords: dict[str, tuple[float, float]], k: int = 4):
        self.coords = coords
        self.adj: dict[str, dict[str, float]] = {n: {} for n in coords}
        ids = list(coords)
        for a in ids:
            near = sorted((b for b in ids if b != a), key=lambda b: self._h(a, b))[:k]
            for b in near:
                self._link(a, b)
        self._connect_components()

    def _h(self, a, b) -> float:
        return haversine_km(*self.coords[a], *self.coords[b])

    def _link(self, a, b):
        w = self._h(a, b) * ROAD_FACTOR
        self.adj[a][b] = w
        self.adj[b][a] = w

    def _components(self):
        seen, comps = set(), []
        for n in self.adj:
            if n in seen:
                continue
            stack, comp = [n], set()
            while stack:
                x = stack.pop()
                if x in comp:
                    continue
                comp.add(x)
                stack.extend(self.adj[x])
            seen |= comp
            comps.append(comp)
        return comps

    def _connect_components(self):
        comps = self._components()
        while len(comps) > 1:
            base = comps[0]
            best = min(((self._h(a, b), a, b) for a in base for c in comps[1:] for b in c))
            self._link(best[1], best[2])
            comps = self._components()

    def astar(self, start: str, goal: str) -> tuple[float, list[str]]:
        """A* with straight-line (haversine) heuristic - admissible because
        every edge costs >= straight-line distance."""
        if start == goal:
            return 0.0, [start]
        open_heap = [(self._h(start, goal), 0.0, start)]
        g = {start: 0.0}
        parent: dict[str, str] = {}
        closed = set()
        while open_heap:
            _, gc, node = heapq.heappop(open_heap)
            if node in closed:
                continue
            if node == goal:
                path = [node]
                while node in parent:
                    node = parent[node]
                    path.append(node)
                return gc, path[::-1]
            closed.add(node)
            for nb, w in self.adj[node].items():
                ng = gc + w
                if ng < g.get(nb, float("inf")):
                    g[nb] = ng
                    parent[nb] = node
                    heapq.heappush(open_heap, (ng + self._h(nb, goal), ng, nb))
        raise ValueError(f"No path {start} -> {goal}")


class TravelModel:
    """Cached travel distance / time / cost between nodes using A*."""

    def __init__(self, graph: RoadGraph, mode: str = "cab"):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {list(MODES)}")
        self.graph = graph
        self.speed, self.rate = MODES[mode]
        self._cache: dict[tuple[str, str], tuple[float, list[str]]] = {}

    def _get(self, a, b):
        key = (a, b)
        if key not in self._cache:
            self._cache[key] = self.graph.astar(a, b)
        return self._cache[key]

    def km(self, a, b) -> float:
        return self._get(a, b)[0]

    def path(self, a, b) -> list[str]:
        return self._get(a, b)[1]

    def minutes(self, a, b) -> float:
        return self.km(a, b) / self.speed * 60.0

    def cost(self, a, b) -> float:
        return self.km(a, b) * self.rate
