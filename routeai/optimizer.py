"""Heuristic search: greedy construction + simulated annealing.
Simulated annealing is a classic local-search algorithm (physics-inspired),
not machine learning - nothing is trained."""
from __future__ import annotations
import math
import random
from .scheduler import Context, simulate


def greedy(candidates: list[str], ctx: Context) -> list[str]:
    order: list[str] = []
    cur = simulate(order, ctx)
    pool = list(candidates)
    while pool:
        best, best_ratio = None, 0.0
        for c in pool:
            plan = simulate(order + [c], ctx)
            if c not in plan.order:
                continue
            gain = plan.fitness - cur.fitness
            extra = max(plan.finish - cur.finish, 1.0)
            if gain > 0 and gain / extra > best_ratio:
                best, best_ratio = c, gain / extra
        if best is None:
            break
        order.append(best)
        pool.remove(best)
        cur = simulate(order, ctx)
    return order


def anneal(candidates: list[str], ctx: Context, iters: int = 6000, seed: int = 42,
           t0: float = 2.0, t_end: float = 0.01) -> list[str]:
    rng = random.Random(seed)
    cur = greedy(candidates, ctx)
    cur_f = simulate(cur, ctx).fitness
    best, best_f = list(cur), cur_f
    alpha = (t_end / t0) ** (1.0 / max(iters, 1))
    temp = t0
    for _ in range(iters):
        nxt = list(cur)
        unused = [c for c in candidates if c not in nxt]
        move = rng.choice(("swap", "move", "add", "remove"))
        if move == "swap" and len(nxt) >= 2:
            i, j = rng.sample(range(len(nxt)), 2)
            nxt[i], nxt[j] = nxt[j], nxt[i]
        elif move == "move" and len(nxt) >= 2:
            x = nxt.pop(rng.randrange(len(nxt)))
            nxt.insert(rng.randrange(len(nxt) + 1), x)
        elif move == "add" and unused:
            nxt.insert(rng.randrange(len(nxt) + 1), rng.choice(unused))
        elif move == "remove" and nxt:
            nxt.pop(rng.randrange(len(nxt)))
        else:
            continue
        f = simulate(nxt, ctx).fitness
        d = f - cur_f
        if d >= 0 or rng.random() < math.exp(d / temp):
            cur, cur_f = nxt, f
            if f > best_f:
                best, best_f = list(nxt), f
        temp *= alpha
    return simulate(best, ctx).order  # drop skipped stops
