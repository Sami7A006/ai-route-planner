# AI Tourist Route Planner (classical AI, no ML)

Plans a multi-day sightseeing route under time, opening-hour and budget constraints.
No training, no datasets, no sklearn/torch - every decision comes from search and rules.

## AI techniques used
| Part | Technique | File |
|---|---|---|
| Shortest travel path | A* search (haversine heuristic) | `routeai/graph.py` |
| Place scoring + explanations | Rule-based expert system (IF-THEN) | `routeai/expert.py` |
| Constraint handling | Opening hours, day end, budget checks | `routeai/scheduler.py` |
| Choosing & ordering stops | Greedy construction + simulated annealing | `routeai/optimizer.py` |
| Multi-day split | Day-by-day planning, budget carried over | `routeai/engine.py` |

## Run
```bash
python main.py --list
python main.py --interests heritage food --days 2 --budget 4000 --group family --kids
python main.py --interests entertainment --budget-level high --budget 8000
python main.py --interactive
python main.py --interests nature --json plan.json
```
Optional web UI: `pip install streamlit pandas` then `streamlit run app.py`

## Options
`--interests` categories (see `--list`) | `--group` solo/couple/family/friends | `--kids` | `--senior`
`--budget-level` low/medium/high (per-place) | `--budget` total INR | `--days` | `--mode` walk/bike/auto/cab
`--day-start/--day-end` HH:MM | `--must/--avoid` place ids | `--start-lat/--start-lon` | `--no-return`

## Use another city
Edit `data/places.json` (same fields). Add rules in `routeai/expert.py`.

## Modern web frontend
```bash
pip install flask
python server.py        # open http://localhost:5000
```
`server.py` exposes `/api/places` and `/api/plan`; `static/index.html` is the UI (interest chips, day tabs, timeline with reasons, Leaflet map). Needs internet for map tiles.
