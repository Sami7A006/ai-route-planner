from __future__ import annotations
from .models import min_to_hhmm


def format_itinerary(plans, places_by_id, start_name: str) -> str:
    lines = []
    total_cost = 0.0
    for i, plan in enumerate(plans, 1):
        lines.append(f"\n=== DAY {i} ===")
        if not plan.stops:
            lines.append("  (nothing feasible - try a bigger budget / longer day)")
            continue
        loc = start_name
        for s in plan.stops:
            via = [places_by_id[x].name for x in s.path[1:-1] if x in places_by_id]
            via_txt = f" via {', '.join(via)}" if via else ""
            lines.append(f"  [travel] {loc} -> {s.place.name}: {s.travel_km:.1f} km, "
                         f"{s.travel_min:.0f} min{via_txt}")
            wait = f" (wait {s.wait:.0f} min for opening)" if s.wait > 0 else ""
            lines.append(f"  {min_to_hhmm(s.start)}-{min_to_hhmm(s.depart)}  {s.place.name} "
                         f"[{s.place.category}] Rs.{s.place.cost:.0f}{wait}")
            if s.reasons:
                lines.append(f"      why: {'; '.join(s.reasons)}")
            loc = s.place.name
        lines.append(f"  Back at {start_name} around {min_to_hhmm(plan.back_home)}")
        lines.append(f"  Day total: {plan.travel_km:.1f} km, Rs.{plan.spent:.0f}, score {plan.utility:.1f}")
        total_cost += plan.spent
    lines.append(f"\nTRIP TOTAL: Rs.{total_cost:.0f}")
    return "\n".join(lines)


def to_dict(plans) -> list[dict]:
    out = []
    for plan in plans:
        out.append({
            "total_cost": round(plan.spent, 2),
            "total_km": round(plan.travel_km, 2),
            "score": round(plan.utility, 2),
            "stops": [{
                "id": s.place.id, "name": s.place.name, "category": s.place.category,
                "lat": s.place.lat, "lon": s.place.lon,
                "arrive": min_to_hhmm(s.arrive), "start": min_to_hhmm(s.start),
                "depart": min_to_hhmm(s.depart), "travel_km": round(s.travel_km, 2),
                "reasons": s.reasons,
            } for s in plan.stops],
        })
    return out
