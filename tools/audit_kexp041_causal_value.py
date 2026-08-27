"""KEXP-046: causal decomposition of KEXP-041 vs frozen R4B.

For each development and exploratory live-meta environmental seed, in both
candidate seats, run two worlds:

  A: KEXP-041 vs R4B
  B: R4B vs R4B

The worlds are identical up to KEXP-041's bounded mutation at state 614.
Compare same-seat own reward, opponent reward and relative reward to separate
farm-value gain from market/opponent externality. Diagnostic only; no
validation/held-out access.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_episode import resolve_agent

CAND = "file:candidates/r4d_jit_carrot_one.py:agent"
BASE = "file:candidates/r4b_ablation_market_only.py:agent"
BUY_STEP = 614
PLANT_STEP = 615


def live_seeds(path: Path) -> list[int]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: list[int] = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int):
                out.append(v["seed"])
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(obj)
    return list(dict.fromkeys(out))


def run_world(seed: int, seat: int, candidate: bool):
    c = resolve_agent(CAND if candidate else BASE)
    o = resolve_agent(BASE)
    agents = [c, o] if seat == 0 else [o, c]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    return env.toJSON()


def frame_action(rep, state_step: int, player: int) -> dict:
    steps = rep.get("steps") or []
    if state_step + 1 >= len(steps):
        return {}
    a = steps[state_step + 1][player].get("action")
    return a if isinstance(a, dict) else {}


def count_market(action: dict, op: str, item: str) -> int:
    total = 0
    for row in list(action.get("market") or []):
        if isinstance(row, list) and len(row) >= 3 and row[:2] == [op, item]:
            try:
                total += max(0, int(row[2] or 0))
            except Exception:
                pass
    return total


def count_plant(action: dict, crop: str) -> int:
    ops = [action.get("farmer"), *list(action.get("hands") or [])]
    return sum(
        isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", crop]
        for op in ops
    )


def final_state(rep, player: int):
    x = rep["steps"][-1][player]
    return x.get("status"), x.get("reward")


def safe_mean(xs):
    xs = [float(x) for x in xs if isinstance(x, (int, float))]
    return statistics.mean(xs) if xs else None


def safe_median(xs):
    xs = [float(x) for x in xs if isinstance(x, (int, float))]
    return statistics.median(xs) if xs else None


def summarize(rows: list[dict]) -> dict:
    valid = [r for r in rows if not r["error"]]
    triggered = [r for r in valid if r["triggered"]]
    quiet = [r for r in valid if not r["triggered"]]

    def block(rr):
        return {
            "n": len(rr),
            "mean_own_causal_delta": safe_mean([r["own_causal_delta"] for r in rr]),
            "median_own_causal_delta": safe_median([r["own_causal_delta"] for r in rr]),
            "mean_opponent_externality": safe_mean([r["opponent_externality"] for r in rr]),
            "mean_relative_causal_delta": safe_mean([r["relative_causal_delta"] for r in rr]),
            "positive_own_fraction": (
                sum(r["own_causal_delta"] > 0 for r in rr) / len(rr) if rr else None
            ),
            "positive_relative_fraction": (
                sum(r["relative_causal_delta"] > 0 for r in rr) / len(rr) if rr else None
            ),
        }

    return {
        "n": len(rows),
        "errors": len(rows) - len(valid),
        "triggered_n": len(triggered),
        "quiet_n": len(quiet),
        "all": block(valid),
        "triggered": block(triggered),
        "quiet": block(quiet),
        "seat0_triggered": block([r for r in triggered if r["candidate_seat"] == 0]),
        "seat1_triggered": block([r for r in triggered if r["candidate_seat"] == 1]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    rows = []

    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        for seat in (0, 1):
            cand = run_world(seed, seat, True)
            base = run_world(seed, seat, False)
            opp = 1 - seat
            cs, cr = final_state(cand, seat)
            cos, cor = final_state(cand, opp)
            bs, br = final_state(base, seat)
            bos, bor = final_state(base, opp)
            error = not (
                cs == cos == bs == bos == "DONE"
                and all(isinstance(x, (int, float)) for x in (cr, cor, br, bor))
            )

            ca614 = frame_action(cand, BUY_STEP, seat)
            ba614 = frame_action(base, BUY_STEP, seat)
            ca615 = frame_action(cand, PLANT_STEP, seat)
            ba615 = frame_action(base, PLANT_STEP, seat)
            added_buy = count_market(ca614, "BUY_SEED", "CARROT") - count_market(ba614, "BUY_SEED", "CARROT")
            dcarrot = count_plant(ca615, "CARROT") - count_plant(ba615, "CARROT")
            dwheat = count_plant(ca615, "WHEAT") - count_plant(ba615, "WHEAT")
            triggered = added_buy > 0 and dcarrot > 0 and dwheat < 0

            if error:
                own = ext = rel = None
            else:
                own = float(cr) - float(br)
                ext = float(cor) - float(bor)
                rel = (float(cr) - float(cor)) - (float(br) - float(bor))

            rows.append({
                "seed": int(seed),
                "source": source,
                "candidate_seat": seat,
                "triggered": triggered,
                "added_carrot_buy": added_buy,
                "delta_carrot_plants": dcarrot,
                "delta_wheat_plants": dwheat,
                "candidate_reward": cr,
                "candidate_opponent_reward": cor,
                "base_reward_same_seat": br,
                "base_opponent_reward": bor,
                "own_causal_delta": own,
                "opponent_externality": ext,
                "relative_causal_delta": rel,
                "error": error,
            })

    summary = {
        "development": summarize([r for r in rows if r["source"] == "development"]),
        "live_meta": summarize([r for r in rows if r["source"] == "live_meta"]),
        "all": summarize(rows),
    }
    payload = {
        "schema_version": "kexp041-causal-value-v1",
        "candidate": CAND,
        "baseline": BASE,
        "alignment": "state t -> action frame t+1",
        "summary": summary,
        "rows": rows,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
