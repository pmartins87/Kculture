#!/usr/bin/env python3
from __future__ import annotations

"""Compile-time/runtime gate for Kculture's L2 VecGame prototype.

This is not a training job.  It verifies that the numpy transport preserves kagsim
state/action semantics and measures how much of the ~62k x L0/L1 headroom the first
vectorized interface recovers before neural-network inference is added.
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT / "native" / "l2"
sys.path.insert(0, str(L2))

import kagvec  # noqa: E402
import kagsim  # noqa: E402

OP = {
    "PASS": 0, "NORTH": 1, "SOUTH": 2, "EAST": 3, "WEST": 4,
    "PICKUP": 5, "DROP": 6, "PLACE": 7, "PLANT": 8, "WATER": 9,
    "HARVEST": 10, "FERTILIZE": 11, "DIG": 12, "BUILD_COOP": 13,
    "BUILD_PASTURE": 14, "FEED": 15, "COLLECT_FERTILIZER": 16,
    "CARE": 17,
}
ITEM = {
    "WHEAT": 0, "CARROT": 1, "TOMATO": 2, "STRAWBERRY": 3, "MELON": 4,
    "EGG": 5, "MILK": 6, "WOOL": 7, "FERTILIZER": 8,
    "GOOSE": 9, "COW": 10, "SHEEP": 11,
}
MOP = {"HIRE": 1, "BUY_LAND": 2, "BUY_SEED": 3, "BUY_PRODUCT": 4, "BUY_ANIMAL": 5, "SELL": 6}
KINDS = {None: 0, "LOCKED": 1, "WEED": 2, "COOP": 3, "PASTURE": 4, "PLANT": 5}
SHOPS = ["BAKERY", "BRUNCH_SPOT", "FARMERS_MARKET", "ICE_CREAM_SHOP", "PET_CAFE", "PIZZA_SHOP", "SMOOTHIE_SHOP", "YARN_STORE"]
ITEM_NAMES = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER", "GOOSE", "COW", "SHEEP"]
CROP_NAMES = ITEM_NAMES[:5]


def encode_action(d):
    row = np.zeros(int(kagvec.ACTION_WIDTH), dtype=np.int32)
    farmer = d.get("farmer") or ["PASS"]
    hands = d.get("hands") or []
    units = [farmer] + list(hands)
    row[0] = min(len(units), int(kagvec.MAX_UNITS))
    for u, act in enumerate(units[: int(kagvec.MAX_UNITS)]):
        off = 1 + 3 * u
        if not isinstance(act, list) or not act:
            continue
        row[off] = OP.get(str(act[0]), 18)
        if len(act) >= 2:
            row[off + 1] = ITEM.get(str(act[1]), 255)
        if len(act) >= 3:
            row[off + 2] = int(act[2])
        elif str(act[0]) in {"PICKUP", "DROP", "PLACE"}:
            row[off + 2] = 1
    ob = 1 + int(kagvec.MAX_UNITS) * 3
    orders = list(d.get("market") or [])[: int(kagvec.MAX_ORDER_SLOTS)]
    row[ob] = len(orders)
    for i, order in enumerate(orders):
        off = ob + 1 + 3 * i
        if not isinstance(order, list) or not order:
            continue
        row[off] = MOP.get(str(order[0]), 0)
        if str(order[0]) in {"HIRE", "BUY_LAND"}:
            row[off + 2] = 1
        elif len(order) >= 3:
            row[off + 1] = ITEM.get(str(order[1]), 255)
            row[off + 2] = int(order[2])
    return row


def _tile_expected(tile):
    if tile is None:
        return [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1]
    if tile == "LOCKED":
        return [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1]
    kind = tile.get("kind")
    if kind == "WEED":
        return [2, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1]
    what = -1
    has_animal = int(bool(tile.get("animal")))
    if kind == "PLANT":
        what = ITEM[tile["crop"]]
    elif has_animal:
        what = ITEM[tile["animal"]]
    return [
        KINDS[kind], what, has_animal,
        int(bool(tile.get("watered_today", False))),
        int(bool(tile.get("fed_today", False))),
        int(bool(tile.get("cared_today", False))),
        int(bool(tile.get("fertilizer_available", False))),
        int(tile.get("consecutive_unwatered", tile.get("consecutive_unfed", 0))),
        int(tile.get("yield_units", 0)),
        int(tile.get("planted_day", tile.get("placed_day", 0))),
        int(tile.get("max_lifespan_step", -1)),
        int(tile.get("fertilized_until_day", -1)),
    ]


def assert_observation_equal(vobs, real, player):
    g = vobs["global"][0]
    own, opp = player, 1 - player
    fo, fx = real["farms"][own], real["farms"][opp]
    expected_global = [
        real.get("step", real["day"] * 24 + real["hour"]), real["day"], real["hour"],
        fo["money"], fx["money"], 1 + len(fo.get("hands", [])), 1 + len(fx.get("hands", [])),
        len(fo.get("unlocked_quadrants", [])), len(fx.get("unlocked_quadrants", [])),
        fo.get("hires_today", 0), fx.get("hires_today", 0),
    ]
    expected_global += [real["market"]["inventory"][x] for x in ITEM_NAMES[:9]]
    expected_global += [real["market"]["prices"][x] for x in ITEM_NAMES[:9]]
    expected_global += [list(real["town"].get("unlocked_shops", [])).count(s) for s in SHOPS]
    if not np.array_equal(g, np.asarray(expected_global, dtype=np.float32)):
        raise AssertionError(f"global mismatch\nvec={g.tolist()}\nreal={expected_global}")

    for rel, abs_p in enumerate((own, opp)):
        farm = real["farms"][abs_p]
        for y in range(10):
            for x in range(10):
                got = vobs["tiles"][0, rel, y, x].tolist()
                exp = _tile_expected(farm["tiles"][y][x])
                if got != exp:
                    raise AssertionError(f"tile mismatch p={abs_p} x={x} y={y}: {got} != {exp}")
        poss = [farm["farmer"]] + list(farm.get("hands", []))
        for u in range(int(kagvec.MAX_UNITS)):
            got = vobs["units"][0, rel, u].tolist()
            exp = [int(poss[u][0]), int(poss[u][1]), 1] if u < len(poss) else [-1, -1, 0]
            if got != exp:
                raise AssertionError(f"unit mismatch p={abs_p} u={u}: {got} != {exp}")

    private = real["private"]
    exp_priv = [int(private["shed"].get(x, 0)) for x in ITEM_NAMES]
    exp_priv += [int(private["seeds"].get(x, 0)) for x in CROP_NAMES]
    invs = list(private.get("inventories", []))
    for u in range(int(kagvec.MAX_UNITS)):
        inv = invs[u] if u < len(invs) else {}
        exp_priv += [int(inv.get(x, 0)) for x in ITEM_NAMES]
    got_priv = vobs["private"][0].tolist()
    if got_priv != exp_priv:
        raise AssertionError("private tensor mismatch")


def semantic_gate(seed=314159):
    vg = kagvec.VecGame([seed])
    kg = kagsim.Game(seed)

    scripted = [
        {
            "farmer": ["PASS"], "hands": [],
            "market": [["BUY_SEED", "WHEAT", 4], ["BUY_ANIMAL", "COW", 1], ["HIRE"], ["HIRE"]],
        },
        {"farmer": ["PLANT", "WHEAT"], "hands": [["PASS"], ["PASS"]], "market": []},
        {"farmer": ["WEST"], "hands": [["NORTH"], ["WEST"]], "market": []},
        {"farmer": ["BUILD_PASTURE"], "hands": [["PASS"], ["PASS"]], "market": []},
    ]
    idle = {"farmer": ["PASS"], "hands": [], "market": []}

    checks = 0
    for t in range(12):
        for p in (0, 1):
            assert_observation_equal(vg.observe(p), kg.observe(p), p)
            checks += 1
        a0 = scripted[t] if t < len(scripted) else idle
        a1 = idle
        e0 = encode_action(a0)[None, :]
        e1 = encode_action(a1)[None, :]
        vg.step(e0, e1, threads=1)
        kg.step(a0, a1)
        rr = vg.rewards()[0].tolist()
        kr = [kg.reward(0), kg.reward(1)]
        if rr != kr:
            raise AssertionError(f"reward mismatch at t={t}: {rr} != {kr}")
    return {"seed": seed, "observation_checks": checks, "rewards": vg.rewards()[0].tolist(), "pass": True}


def pass_actions(batch):
    x = np.zeros((batch, int(kagvec.ACTION_WIDTH)), dtype=np.int32)
    x[:, 0] = 1  # farmer exists and PASSes
    return x


def bench(batch, steps, threads, observe_seats):
    seeds = list(range(1_000_000, 1_000_000 + batch))
    vg = kagvec.VecGame(seeds, steps=steps)
    a = pass_actions(batch)
    transitions = max(1, steps - 1)
    t0 = time.perf_counter()
    for _ in range(transitions):
        if observe_seats >= 1:
            vg.observe(0)
        if observe_seats >= 2:
            vg.observe(1)
        vg.step(a, a, threads=threads)
    elapsed = time.perf_counter() - t0
    rewards = vg.rewards()
    if not np.all(rewards == 3000.0):
        raise AssertionError("PASS-vs-PASS should finish at 3000/3000")
    return {
        "batch": batch,
        "steps": steps,
        "observe_seats": observe_seats,
        "threads": threads,
        "seconds": elapsed,
        "episodes_per_second": batch / elapsed,
        "sim_steps_per_second": batch * transitions / elapsed,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", default="256,1024,4096")
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--out", default="runs/l2_vec_gate_v0/L2_VEC_GATE.json")
    args = ap.parse_args()

    batches = [int(x) for x in args.batches.split(",") if x.strip()]
    print("L2_VEC_GATE_START", json.dumps({
        "schema": str(kagvec.SCHEMA), "engine": str(kagvec.ENGINE_VERSION),
        "action_width": int(kagvec.ACTION_WIDTH), "batches": batches,
    }, sort_keys=True), flush=True)

    sem = semantic_gate()
    print("SEMANTIC", json.dumps(sem, sort_keys=True), flush=True)

    rows = []
    for b in batches:
        for seats in (0, 1, 2):
            row = bench(b, args.steps, args.threads, seats)
            rows.append(row)
            print("L2_BENCH", json.dumps(row, sort_keys=True), flush=True)

    two = [r for r in rows if r["observe_seats"] == 2]
    best_two = max(two, key=lambda r: r["episodes_per_second"])
    l1_eps = 1.4700230744759935
    speedup = best_two["episodes_per_second"] / l1_eps
    result = {
        "schema": "prize-solver-l2-vec-gate-v0",
        "semantic": sem,
        "benchmarks": rows,
        "best_two_seat": best_two,
        "baseline_l1_eps": l1_eps,
        "two_seat_speedup_vs_l1": speedup,
        "target_speedup": 100.0,
        "pass": bool(sem["pass"] and speedup >= 100.0),
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("L2_VEC_GATE_RESULT", json.dumps({
        "pass": result["pass"],
        "best_batch": best_two["batch"],
        "two_seat_eps": best_two["episodes_per_second"],
        "speedup_vs_l1": speedup,
        "out": str(out),
    }, sort_keys=True), flush=True)
    if not result["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
