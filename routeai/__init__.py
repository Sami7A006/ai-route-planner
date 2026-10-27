"""RouteAI - classical (non-ML) AI tourist route planner.

Techniques used: A* graph search, rule-based expert system,
simulated annealing (local search), constraint checking.
"""
from .models import Place, load_places
from .expert import Profile
from .engine import plan_trip

__all__ = ["Place", "load_places", "Profile", "plan_trip"]
