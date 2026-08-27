"""KEXP-048: mechanical execution audit for KEXP-045 double JIT CARROT.

Compare candidate and frozen R4B separately vs starter on development and
exploratory live-meta environmental seeds. Verify exact added BUY_SEED CARROT
and +CARROT/-WHEAT PLANT deltas at both 614->615 and 619->620 handshakes.
Diagnostic only; no validation/held-out access.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_episode import resolve_agent

CAND = "file:candidates/r4d_jit_carrot_two.py:agent"
BASE = "file:candidates/r4b_ablation_market_only.py:agent"
PAIRS = ((614, 615), (619, 620))


def live_seeds(path):
    x = json.loads(path.read_text(encoding="utf-8"))
    out = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int): out.append(v["seed"])
            for c in v.values(): walk(c)
        elif isinstance(v, list):
            for c in v: walk(c)
    walk(x)
    return list(dict.fromkeys(out))


def run(agent_ref, seed):
    a = resolve_agent(agent_ref)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run([a, "starter"])
    return env.toJSON()


def action(rep, state_step):
    steps = rep.get("steps") or []
    return (steps[state_step + 1][0].get("action") or {}) if state_step + 1 < len(steps) else {}


def market_qty(a, op, item):
    q = 0
    for row in list((a or {}).get("market") or []):
        if isinstance(row, list) and len(row) >= 3 and row[:2] == [op, item]:
            try: q += max(0, int(row[2] or 0))
            except Exception: pass
    return q


def plant_count(a, crop):
    ops = [(a or {}).get("farmer"), *list((a or {}).get("hands") or [])]
    return sum(isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", crop] for op in ops)


def status(rep):
    return rep["steps"][-1][0].get("status")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    rows = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        cr = run(CAND, seed); br = run(BASE, seed)
        row = {"seed": int(seed), "source": source, "candidate_status": status(cr), "base_status": status(br), "pairs": {}}
        for buy, plant in PAIRS:
            ca, ba = action(cr, buy), action(br, buy)
            cp, bp = action(cr, plant), action(br, plant)
            added_buy = market_qty(ca, "BUY_SEED", "CARROT") - market_qty(ba, "BUY_SEED", "CARROT")
            dc = plant_count(cp, "CARROT") - plant_count(bp, "CARROT")
            dw = plant_count(cp, "WHEAT") - plant_count(bp, "WHEAT")
            try:
                cs = int(cr["steps"][plant][0]["observation"]["private"]["seeds"].get("CARROT", 0) or 0)
                bs = int(br["steps"][plant][0]["observation"]["private"]["seeds"].get("CARROT", 0) or 0)
            except Exception:
                cs = bs = 0
            row["pairs"][f"{buy}_{plant}"] = {
                "added_buy": added_buy,
                "extra_stock": cs - bs,
                "delta_carrot_plants": dc,
                "delta_wheat_plants": dw,
                "converted": bool(dc > 0 and dw < 0),
            }
        rows.append(row)

    summary = {}
    for source in ("development", "live_meta", "all"):
        rr = rows if source == "all" else [r for r in rows if r["source"] == source]
        block = {"episodes": len(rr), "status_errors": sum(r["candidate_status"] != "DONE" or r["base_status"] != "DONE" for r in rr), "pairs": {}}
        for buy, plant in PAIRS:
            k = f"{buy}_{plant}"
            block["pairs"][k] = {
                "added_buy_episodes": sum(r["pairs"][k]["added_buy"] > 0 for r in rr),
                "extra_stock_episodes": sum(r["pairs"][k]["extra_stock"] > 0 for r in rr),
                "converted_episodes": sum(r["pairs"][k]["converted"] for r in rr),
            }
        block["both_converted_episodes"] = sum(all(r["pairs"][f"{b}_{p}"]["converted"] for b,p in PAIRS) for r in rr)
        block["any_conversion_episodes"] = sum(any(r["pairs"][f"{b}_{p}"]["converted"] for b,p in PAIRS) for r in rr)
        summary[source] = block

    gate = {
        "execution_matches_design": bool(
            summary["development"]["status_errors"] == 0 and summary["live_meta"]["status_errors"] == 0
            and all(summary[s]["pairs"][f"{b}_{p}"]["added_buy_episodes"] == summary[s]["pairs"][f"{b}_{p}"]["converted_episodes"] for s in ("development","live_meta") for b,p in PAIRS)
            and summary["development"]["both_converted_episodes"] >= 4
            and summary["live_meta"]["both_converted_episodes"] >= 5
        )
    }
    payload = {"schema_version": "kexp045-execution-v1", "pairs": [list(x) for x in PAIRS], "summary": summary, "gate": gate, "rows": rows}
    out = ROOT / args.output; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"summary": summary, "gate": gate}, indent=2, sort_keys=True))


if __name__ == "__main__": main()
