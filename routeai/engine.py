"""Top-level planner: builds graph, scores places, plans each day."""
from __future__ import annotations
from .expert import Profile, score_place
from .graph import RoadGraph, TravelModel
from .models import Place
from .optimizer import anneal
from .scheduler import Context, DayPlan, simulate


def plan_trip(places: list[Place], profile: Profile, start: dict, days: int = 1,
              day_start: int = 9 * 60, day_end: int = 20 * 60, budget: float = 3000,
              mode: str = "cab", seed: int = 42, iters: int = 6000,
              return_home: bool = True) -> list[DayPlan]:
    """start = {"name": str, "lat": float, "lon": float}"""
    start_id = "__start__"
    coords = {p.id: (p.lat, p.lon) for p in places}
    coords[start_id] = (start["lat"], start["lon"])
    travel = TravelModel(RoadGraph(coords), mode)

    static = {p.id: score_place(p, profile) for p in places}
    pool = {p.id: p for p in places if p.id not in profile.avoid}
    plans: list[DayPlan] = []
    remaining = budget

    for d in range(days):
        ctx = Context(places={p.id: p for p in places}, static=static, profile=profile,
                      travel=travel, start_id=start_id, day_start=day_start, day_end=day_end,
                      budget=remaining / (days - d), return_home=return_home)
        order = anneal(list(pool), ctx, iters=iters, seed=seed + d)
        plan = simulate(order, ctx)
        plans.append(plan)
        remaining -= plan.spent
        for pid in plan.order:
            pool.pop(pid, None)
    return plans
