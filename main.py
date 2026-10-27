"""CLI for the AI tourist route planner.

Examples:
  python main.py --interests heritage food --days 2 --budget 4000
  python main.py --interactive
  python main.py --list
"""
import argparse
import json
from pathlib import Path

from routeai import Profile, load_places, plan_trip
from routeai.models import hhmm_to_min
from routeai.graph import MODES
from routeai.report import format_itinerary, to_dict

DATA = Path(__file__).parent / "data" / "places.json"


def ask(prompt, default=""):
    v = input(f"{prompt} [{default}]: ").strip()
    return v or default


def main():
    ap = argparse.ArgumentParser(description="AI tourist route planner (A* + expert rules + simulated annealing)")
    ap.add_argument("--places", default=str(DATA))
    ap.add_argument("--list", action="store_true", help="list places and categories")
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--interests", nargs="*", default=[])
    ap.add_argument("--group", default="solo", choices=["solo", "couple", "family", "friends"])
    ap.add_argument("--kids", action="store_true")
    ap.add_argument("--senior", action="store_true")
    ap.add_argument("--budget-level", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--must", nargs="*", default=[], help="place ids to force")
    ap.add_argument("--avoid", nargs="*", default=[], help="place ids to skip")
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--budget", type=float, default=3000, help="total trip budget in INR")
    ap.add_argument("--mode", default="cab", choices=list(MODES))
    ap.add_argument("--day-start", default="09:00")
    ap.add_argument("--day-end", default="20:00")
    ap.add_argument("--start-name", default="Hotel (Abids)")
    ap.add_argument("--start-lat", type=float, default=17.3894)
    ap.add_argument("--start-lon", type=float, default=78.4740)
    ap.add_argument("--no-return", action="store_true", help="do not return to start")
    ap.add_argument("--iters", type=int, default=6000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--json", help="save itinerary to this JSON file")
    a = ap.parse_args()

    places = load_places(a.places)
    cats = sorted({p.category for p in places})

    if a.list:
        print("Categories:", ", ".join(cats))
        for p in places:
            print(f"  {p.id:16s} {p.name} [{p.category}] Rs.{p.cost:.0f}")
        return

    if a.interactive:
        print("Categories:", ", ".join(cats))
        a.interests = ask("Interests (space separated)", "heritage food").split()
        a.group = ask("Group (solo/couple/family/friends)", a.group)
        a.kids = ask("Kids? (y/n)", "n").lower().startswith("y")
        a.senior = ask("Senior travellers? (y/n)", "n").lower().startswith("y")
        a.days = int(ask("Days", str(a.days)))
        a.budget = float(ask("Total budget INR", str(a.budget)))
        a.mode = ask("Mode (walk/bike/auto/cab)", a.mode)

    profile = Profile(interests=a.interests, group=a.group, kids=a.kids, senior=a.senior,
                      budget_level=a.budget_level, must_visit=a.must, avoid=a.avoid)
    plans = plan_trip(
        places, profile,
        {"name": a.start_name, "lat": a.start_lat, "lon": a.start_lon},
        days=a.days, day_start=hhmm_to_min(a.day_start), day_end=hhmm_to_min(a.day_end),
        budget=a.budget, mode=a.mode, seed=a.seed, iters=a.iters, return_home=not a.no_return,
    )
    print(format_itinerary(plans, {p.id: p for p in places}, a.start_name))
    if a.json:
        Path(a.json).write_text(json.dumps(to_dict(plans), indent=2), encoding="utf-8")
        print(f"\nSaved {a.json}")


if __name__ == "__main__":
    main()
