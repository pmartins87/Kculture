"""KEXP-023: measure late WHEAT plant->same-tile HARVEST timing.
Development and exploratory public-meta seeds only; no strategy mutation.
"""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import Counter
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent


def farm_at(steps, i):
    return steps[i][0]["observation"]["farms"][0]


def actor_ops(entry, farm):
    action = entry.get("action") or {}
    out = []
    if isinstance(farm.get("farmer"), list):
        out.append((tuple(farm["farmer"]), action.get("farmer")))
    for j, pos in enumerate(farm.get("hands") or []):
        ops = action.get("hands") or []
        out.append((tuple(pos), ops[j] if j < len(ops) else None))
    return out


def tile(farm, pos):
    x, y = pos
    return farm["tiles"][y][x]


def analyze(replay, seed, source, start, end):
    steps = replay["steps"]
    rows = []
    for t in range(start, min(end + 1, 719)):
        f = farm_at(steps, t)
        for pos, op in actor_ops(steps[t][0], f):
            if not (isinstance(op, list) and len(op) > 1 and op[:2] == ["PLANT", "WHEAT"]):
                continue
            harvest = None
            crop = None
            for u in range(t + 1, min(719, len(steps))):
                uf = farm_at(steps, u)
                for upos, uop in actor_ops(steps[u][0], uf):
                    if upos == pos and isinstance(uop, list) and uop and uop[0] == "HARVEST":
                        harvest = u
                        ut = tile(uf, pos)
                        crop = ut.get("crop") if isinstance(ut, dict) else None
                        break
                if harvest is not None:
                    break
            delay = None if harvest is None else harvest - t
            if delay is None: cls = "no_harvest"
            elif delay <= 72: cls = "clean_le_72"
            elif delay <= 95: cls = "decay_risk_73_95"
            else: cls = "unsafe_ge_96"
            obs = steps[t][0]["observation"]
            prices = (obs.get("market") or {}).get("prices") or {}
            rows.append({
                "seed": seed, "source": source, "plant_step": t,
                "position": list(pos), "harvest_step": harvest,
                "delay_turns": delay, "crop_before_harvest": crop,
                "timing_class": cls,
                "shops": list(((obs.get("town") or {}).get("unlocked_shops") or [])),
                "wheat_price": prices.get("WHEAT"), "carrot_price": prices.get("CARROT"),
            })
    return rows


def live_seeds(path):
    payload = json.loads(path.read_text())
    found = []
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("seed"), int): found.append(x["seed"])
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(payload)
    return list(dict.fromkeys(found))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--start", type=int, default=576)
    ap.add_argument("--end", type=int, default=647)
    args = ap.parse_args()
    dev = json.loads((ROOT/"configs/seed_partitions.json").read_text())["development"]
    live = live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    rows = []
    episodes = []
    for seed, source in [(s,"development") for s in dev] + [(s,"live_meta") for s in live]:
        candidate = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env = make("kaggriculture", configuration={"episodeSteps":720,"seed":int(seed)}, debug=True)
        env.run([candidate, "starter"])
        replay = env.toJSON()
        rr = analyze(replay, int(seed), source, args.start, args.end)
        rows.extend(rr); episodes.append({"seed":int(seed),"source":source,"plants":len(rr)})
    delays = [r["delay_turns"] for r in rows if isinstance(r["delay_turns"], int)]
    summary = {
        "episode_count": len(episodes), "late_wheat_plants": len(rows),
        "classes": dict(Counter(r["timing_class"] for r in rows)),
        "delay_mean": statistics.mean(delays) if delays else None,
        "delay_median": statistics.median(delays) if delays else None,
        "delay_min": min(delays) if delays else None, "delay_max": max(delays) if delays else None,
    }
    out = ROOT/args.output; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary":summary,"episodes":episodes,"rows":rows},indent=2,sort_keys=True))
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__ == "__main__": main()
