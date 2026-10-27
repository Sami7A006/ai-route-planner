"""Rule-based expert system: IF-THEN rules score each place and
explain why. No training, no data fitting - rules are written by hand."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from .models import Place

BUDGET_LIMIT = {"low": 150, "medium": 800, "high": float("inf")}  # per-place INR


@dataclass
class Profile:
    interests: list[str] = field(default_factory=list)
    group: str = "solo"              # solo | couple | family | friends
    kids: bool = False
    senior: bool = False
    budget_level: str = "medium"     # low | medium | high
    must_visit: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)


@dataclass
class Rule:
    name: str
    when: Callable[[Place, Profile], bool]
    weight: float
    reason: str


@dataclass
class TimeRule:
    name: str
    when: Callable[[Place, Profile, float], bool]   # (place, profile, start minute)
    weight: float
    reason: str


def _in(t, a, b):
    return a * 60 <= t < b * 60


RULES = [
    Rule("interest", lambda p, f: p.category in f.interests, 3.0, "matches your interest in {category}"),
    Rule("top_rated", lambda p, f: p.rating >= 4.5, 1.0, "top rated ({rating})"),
    Rule("iconic", lambda p, f: "iconic" in p.tags, 1.0, "iconic landmark"),
    Rule("kids", lambda p, f: f.kids and "kid_friendly" in p.tags, 1.5, "kid friendly"),
    Rule("senior_walk", lambda p, f: f.senior and "walking_heavy" in p.tags, -2.0, "lots of walking"),
    Rule("romantic", lambda p, f: f.group == "couple" and "romantic" in p.tags, 1.0, "good for couples"),
    Rule("friends_fun", lambda p, f: f.group == "friends" and p.category in ("entertainment", "shopping", "food"), 1.0, "fun with friends"),
    Rule("free_low_budget", lambda p, f: f.budget_level == "low" and p.cost == 0, 1.0, "free entry"),
    Rule("too_expensive", lambda p, f: p.cost > BUDGET_LIMIT[f.budget_level], -2.0, "costs Rs.{cost:.0f}, above your budget level"),
    Rule("must_visit", lambda p, f: p.id in f.must_visit, 10.0, "marked must-visit"),
    Rule("avoid", lambda p, f: p.id in f.avoid, -50.0, "marked avoid"),
]

TIME_RULES = [
    TimeRule("meal_time", lambda p, f, t: p.category == "food" and (_in(t, 12, 15) or _in(t, 19, 22)), 2.0, "good meal time"),
    TimeRule("off_meal", lambda p, f, t: p.category == "food" and not (_in(t, 12, 15) or _in(t, 19, 22)), -1.5, "not a meal time"),
    TimeRule("midday_heat", lambda p, f, t: "outdoor" in p.tags and _in(t, 12, 15.5) and p.category != "food", -1.0, "outdoors in midday heat"),
    TimeRule("golden_hour", lambda p, f, t: "evening" in p.tags and _in(t, 16, 20), 1.0, "best in the evening"),
]


def score_place(place: Place, profile: Profile) -> tuple[float, list[str]]:
    """Static score (time independent) with human-readable reasons."""
    score = place.rating - 3.0  # base sightseeing value
    reasons = []
    info = dict(category=place.category, rating=place.rating, cost=place.cost)
    for r in RULES:
        if r.when(place, profile):
            score += r.weight
            reasons.append(r.reason.format(**info))
    return score, reasons


def time_bonus(place: Place, profile: Profile, start_min: float) -> tuple[float, list[str]]:
    bonus, reasons = 0.0, []
    for r in TIME_RULES:
        if r.when(place, profile, start_min):
            bonus += r.weight
            reasons.append(r.reason)
    return bonus, reasons
