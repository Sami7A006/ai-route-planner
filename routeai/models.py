from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


def hhmm_to_min(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def min_to_hhmm(m: float) -> str:
    m = int(round(m))
    return f"{(m // 60) % 24:02d}:{m % 60:02d}"


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    category: str
    lat: float
    lon: float
    duration: int      # minutes spent at the place
    cost: float        # entry / typical spend (INR)
    open: int          # minutes from midnight
    close: int
    rating: float      # 0-5, static knowledge (not learned)
    tags: tuple = ()


def load_places(path: str | Path) -> list[Place]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for p in data["places"]:
        out.append(Place(
            id=p["id"], name=p["name"], category=p["category"],
            lat=p["lat"], lon=p["lon"], duration=p["duration"], cost=p["cost"],
            open=hhmm_to_min(p["open"]), close=hhmm_to_min(p["close"]),
            rating=p["rating"], tags=tuple(p.get("tags", [])),
        ))
    return out
