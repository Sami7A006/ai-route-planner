"""Flask backend: serves the frontend and exposes the Python AI planner as an API.
Run:  pip install flask  &&  python server.py   ->  http://localhost:5000
"""
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from routeai import Profile, load_places, plan_trip
from routeai.models import hhmm_to_min, min_to_hhmm

ROOT = Path(__file__).parent
PLACES = load_places(ROOT / "data" / "places.json")
app = Flask(__name__, static_folder=str(ROOT / "static"), static_url_path="/static")


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/places")
def places():
    return jsonify([{"id": p.id, "name": p.name, "category": p.category} for p in PLACES])


@app.post("/api/plan")
def plan():
    d = request.get_json(force=True)
    start = {"name": "Start", "lat": d.get("lat", 17.3894), "lon": d.get("lon", 78.4740)}
    profile = Profile(
        interests=d.get("interests", []), group=d.get("group", "solo"),
        kids=bool(d.get("kids")), senior=bool(d.get("senior")),
        budget_level=d.get("budgetLevel", "medium"),
        must_visit=d.get("must", []), avoid=d.get("avoid", []),
    )
    plans = plan_trip(
        PLACES, profile, start, days=int(d.get("days", 1)),
        day_start=hhmm_to_min(d.get("dayStart", "09:00")),
        day_end=hhmm_to_min(d.get("dayEnd", "20:00")),
        budget=float(d.get("budget", 3000)), mode=d.get("mode", "cab"),
        iters=int(d.get("iters", 4000)),
    )
    days = []
    for p in plans:
        days.append({
            "cost": round(p.spent), "km": round(p.travel_km, 1), "score": round(p.utility, 1),
            "backHome": min_to_hhmm(p.back_home) if p.stops else None,
            "stops": [{
                "name": s.place.name, "category": s.place.category,
                "lat": s.place.lat, "lon": s.place.lon, "cost": s.place.cost,
                "start": min_to_hhmm(s.start), "end": min_to_hhmm(s.depart),
                "travelKm": round(s.travel_km, 1), "travelMin": round(s.travel_min),
                "wait": round(s.wait), "reasons": s.reasons,
            } for s in p.stops],
        })
    return jsonify({"start": start, "days": days})


if __name__ == "__main__":
    app.run(debug=True)
