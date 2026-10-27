"""Constraint checking + timeline simulation for one day."""
from __future__ import annotations
from dataclasses import dataclass, field
from .expert import time_bonus
from .models import Place

DIVERSITY_PENALTY = 0.75   # per earlier stop of the same category
TRAVEL_PENALTY = 0.02      # fitness cost per travel minute


@dataclass
class Context:
    places: dict[str, Place]
    static: dict[str, tuple[float, list[str]]]
    profile: object
    travel: object
    start_id: str
    day_start: int
    day_end: int
    budget: float
    return_home: bool = True


@dataclass
class Stop:
    place: Place
    path: list[str]
    travel_km: float
    travel_min: float
    travel_cost: float
    arrive: float
    start: float
    depart: float
    wait: float
    utility: float
    reasons: list[str]


@dataclass
class DayPlan:
    stops: list[Stop] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    utility: float = 0.0
    spent: float = 0.0
    travel_min: float = 0.0
    travel_km: float = 0.0
    finish: float = 0.0
    back_home: float = 0.0

    @property
    def order(self):
        return [s.place.id for s in self.stops]

    @property
    def fitness(self):
        return self.utility - TRAVEL_PENALTY * self.travel_min


def simulate(order: list[str], ctx: Context) -> DayPlan:
    """Walk through `order`; skip any stop that violates a hard constraint
    (opening hours, day end, budget)."""
    tm = ctx.travel
    plan = DayPlan(finish=ctx.day_start)
    t, loc, counts = float(ctx.day_start), ctx.start_id, {}
    for pid in order:
        p = ctx.places[pid]
        km, mins, tcost = tm.km(loc, pid), tm.minutes(loc, pid), tm.cost(loc, pid)
        arrive = t + mins
        start = max(arrive, p.open)
        end = start + p.duration
        back = tm.minutes(pid, ctx.start_id) if ctx.return_home else 0.0
        if end > p.close or end + back > ctx.day_end or plan.spent + tcost + p.cost > ctx.budget:
            plan.skipped.append(pid)
            continue
        static, reasons = ctx.static[pid]
        tb, treasons = time_bonus(p, ctx.profile, start)
        n = counts.get(p.category, 0)
        free = 1 if p.category == "food" else 0
        util = static + tb - DIVERSITY_PENALTY * max(0, n - free)
        counts[p.category] = n + 1
        plan.stops.append(Stop(p, tm.path(loc, pid), km, mins, tcost, arrive, start, end,
                               start - arrive, util, reasons + treasons))
        plan.utility += util
        plan.spent += tcost + p.cost
        plan.travel_min += mins
        plan.travel_km += km
        t, loc = end, pid
    plan.finish = t
    plan.back_home = t + (tm.minutes(loc, ctx.start_id) if ctx.return_home else 0.0)
    if ctx.return_home and plan.stops:
        plan.travel_km += tm.km(loc, ctx.start_id)
        plan.travel_min += tm.minutes(loc, ctx.start_id)
        plan.spent += tm.cost(loc, ctx.start_id)
    return plan
