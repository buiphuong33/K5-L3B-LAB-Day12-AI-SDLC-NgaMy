"""Deterministic multi-day soak runner for the Phase 4 release check."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import tempfile
import time

from .contract import load_contract
from .errors import BadInput
from .ids import sort_by_id
from .inputs import InputState
from .rng import Streams
from .sim.day import DaySim

MAX_DAYS = 10


def _extend_day_plans(tuning, days):
    """Return private tuning with D1–D5 repeated for days 6–10."""
    extended = copy.deepcopy(tuning)
    base = {plan["day"]: plan for plan in tuning["day_plan"]}
    extended["day_plan"] = []
    for day in range(1, days + 1):
        source = base[(day - 1) % 5 + 1]
        extended["day_plan"].append(dict(copy.deepcopy(source), day=day))
    return extended


def _ingredient_fixture(tuning, plan=None):
    plan = tuning["day_plan"][0] if plan is None else plan
    stock = []
    next_id = 1
    for kind in sorted(plan["ingredients"]):
        for _ in range(plan["ingredients"][kind]):
            stock.append({"id": f"I{next_id}", "kind": kind,
                          "fresh": tuning["freshness"]["initial"]})
            next_id += 1
    return stock


def _input_for(sim):
    """A fixed policy: dock at once, cook oldest orders, serve, then close Shop."""
    if sim.phase == "gather":
        if sim.phase_tick == 0:
            return InputState((0.0, 0.0), {}, {"interact"})
        return InputState((0.0, 0.0), {}, set())
    if sim.phase == "shop":
        return InputState((0.0, 0.0), {}, {"shop_done"})

    quan = sim.sub
    target = None
    if quan.hand is not None:
        customer = next((c for c in quan.customers
                         if c["id"] == quan.hand["order_id"]), None)
        if customer is not None:
            target = next(t for t in quan.tables if t["id"] == customer["table_id"])
    if target is None:
        ready = sort_by_id([s for s in quan.stoves if s["state"] == "ready"])
        if ready:
            target = ready[0]
    if target is None and any(c["order_status"] == "reserved" for c in quan.customers):
        idle = sort_by_id([s for s in quan.stoves if s["state"] == "idle"])
        if idle:
            target = idle[0]
    if target is None:
        return InputState((0.0, 0.0), {}, set())

    dx = target["pos"][0] - quan.pos[0]
    dz = target["pos"][1] - quan.pos[1]
    distance = math.hypot(dx, dz)
    if distance <= max(0.1, quan.t["interact_radius"] - 0.35):
        return InputState((0.0, 0.0), {}, {"interact"})
    speed_scale = min(1.0, max(0.15, distance * 0.8))
    move = (dx / distance * speed_scale, dz / distance * speed_scale)
    return InputState(move, {}, set())


def run_soak(seed=1, days=10, tuning=None):
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= MAX_DAYS:
        raise BadInput(f"days must be an integer in [1, {MAX_DAYS}]")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise BadInput("seed must be an integer")
    started = time.perf_counter()
    if tuning is None:
        tuning = load_contract()["tuning"]
    soak_tuning = _extend_day_plans(tuning, days)
    scenario = {"gather": {"hold": _ingredient_fixture(soak_tuning),
                           "random_fish": False}}
    sim = DaySim(soak_tuning, scenario, Streams(seed), days=days)
    results = []
    crashes = 0
    tick_limit = days * (int(round((soak_tuning["gather"]["duration_s"] +
                                    soak_tuning["quan"]["duration_s"]) * 60)) +
                         soak_tuning["shop"]["max_ticks"] + 1)
    ticks = 0
    try:
        while not sim.done and ticks < tick_limit:
            if sim.phase == "shop" and sim.shop_left == 1 and sim.day < days:
                next_plan = soak_tuning["day_plan"][sim.day]
                sim.g_template = {"hold": _ingredient_fixture(soak_tuning, next_plan),
                                  "random_fish": False}
            events = sim.step(_input_for(sim))
            ticks += 1
            for event in events:
                if event[0] == "shop_end":
                    day = event[3]
                    earned = sim.earned
                    reputation = sim.reputation
                    results.append({"day": day, "earned": earned,
                                    "reputation": reputation,
                                    "score": earned + soak_tuning["score"]["reputation_multiplier"] *
                                    math.floor(reputation)})
        if not sim.done or sim.days_completed != days:
            crashes += 1
    except Exception as exc:  # The artifact reports a partial run and a crash count.
        crashes += 1
        print(f"soak crashed: {type(exc).__name__}: {exc}", file=sys.stderr)
    return {"days": days, "days_completed": sim.days_completed, "crashes": crashes,
            "results": results, "duration_s": round(time.perf_counter() - started, 3)}


def _write_result(path, result):
    target = os.path.abspath(path)
    directory = os.path.dirname(target) or os.curdir
    fd, temporary = tempfile.mkstemp(prefix=".soak-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(prog="chonoi.soak")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--days", required=True, type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if not 1 <= args.days <= MAX_DAYS:
        parser.error(f"--days must be in [1, {MAX_DAYS}]")
    try:
        result = run_soak(args.seed, args.days)
        _write_result(args.out, result)
    except (BadInput, OSError) as exc:
        print(f"soak error: {exc}", file=sys.stderr)
        return 2
    return 1 if result["crashes"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
