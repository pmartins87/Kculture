"""KEXP-047: winner-vs-loser economic allocation radar in official top episodes.

Observational priority diagnostic only. Uses same-episode winner/loser pairs,
correct replay alignment, and reports phase market allocations plus checkpoint
farm composition by date and overall. No identity-conditioned policy use.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import statistics
import tempfile
from pathlib import Path

import kagglehub

DATES = ("2026-08-24", "2026-08-25", "2026-08-26")
PHASES = ((0, 191), (192, 383), (384, 575), (576, 647), (648, 718))
CHECKPOINTS = (192, 384, 576, 648, 696)
MARKET_METRICS = (
    "HIRE", "BUY_LAND",
    "BUY_ANIMAL:GOOSE", "BUY_ANIMAL:COW", "BUY_ANIMAL:SHEEP",
    "BUY_SEED:WHEAT", "BUY_SEED:CARROT", "BUY_SEED:TOMATO",
    "BUY_SEED:STRAWBERRY", "BUY_SEED:MELON",
    "SELL:WHEAT", "SELL:CARROT", "SELL:TOMATO", "SELL:STRAWBERRY",
    "SELL:MELON", "SELL:EGG", "SELL:MILK", "SELL:WOOL",
)
COMP_METRICS = (
    "money", "hands", "quads", "GOOSE", "COW", "SHEEP",
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "WEED",
)


def dl(handle, filename, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(outdir), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}")
    return p


def csv_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def market_phase(rep, player, a, b):
    q = collections.Counter()
    steps = rep.get("steps") or []
    for t in range(a, min(b + 1, len(steps) - 1)):
        action = steps[t + 1][player].get("action") or {}
        for row in list(action.get("market") or []):
            if not (isinstance(row, list) and row):
                continue
            op = str(row[0])
            item = str(row[1]) if len(row) > 1 else None
            key = f"{op}:{item}" if op in {"BUY_ANIMAL", "BUY_SEED", "SELL"} and item else op
            if len(row) >= 3:
                try:
                    amount = max(0, int(row[2] or 0))
                except Exception:
                    amount = 1
            else:
                amount = 1
            q[key] += amount
    return {k: float(q.get(k, 0)) for k in MARKET_METRICS}


def composition(rep, player, t):
    obs = rep["steps"][t][player].get("observation") or {}
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    c = collections.Counter()
    for row in farm.get("tiles", []) or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            if tile.get("animal"):
                c[str(tile["animal"])] += 1
            elif tile.get("kind") == "PLANT":
                c[str(tile.get("crop"))] += 1
            elif tile.get("kind") == "WEED":
                c["WEED"] += 1
    out = {
        "money": float(farm.get("money", 0) or 0),
        "hands": float(len(farm.get("hands", []) or [])),
        "quads": float(len(farm.get("unlocked_quadrants", []) or [])),
    }
    for k in ("GOOSE", "COW", "SHEEP", "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "WEED"):
        out[k] = float(c.get(k, 0))
    return out


def profile(rep, player, date, eid, cohort, reward):
    return {
        "date": date,
        "episode_id": eid,
        "player": player,
        "cohort": cohort,
        "reward": float(reward),
        "phases": {f"{a}_{b}": market_phase(rep, player, a, b) for a, b in PHASES},
        "checkpoints": {str(t): composition(rep, player, t) for t in CHECKPOINTS},
    }


def mean(rows, getter):
    xs = []
    for r in rows:
        try:
            v = getter(r)
        except Exception:
            continue
        if isinstance(v, (int, float)):
            xs.append(float(v))
    return statistics.mean(xs) if xs else None


def summarize(rows):
    out = {"phases": {}, "checkpoints": {}}
    for a, b in PHASES:
        pk = f"{a}_{b}"
        out["phases"][pk] = {
            m: mean(rows, lambda r, pk=pk, m=m: r["phases"][pk][m])
            for m in MARKET_METRICS
        }
    for t in CHECKPOINTS:
        tk = str(t)
        out["checkpoints"][tk] = {
            m: mean(rows, lambda r, tk=tk, m=m: r["checkpoints"][tk][m])
            for m in COMP_METRICS
        }
    out["mean_reward"] = mean(rows, lambda r: r["reward"])
    out["n"] = len(rows)
    return out


def diff_summary(w, l):
    phases = {}
    for pk in w["phases"]:
        phases[pk] = {
            m: (w["phases"][pk][m] - l["phases"][pk][m])
            for m in MARKET_METRICS
        }
    cps = {}
    for tk in w["checkpoints"]:
        cps[tk] = {
            m: (w["checkpoints"][tk][m] - l["checkpoints"][tk][m])
            for m in COMP_METRICS
        }
    return {"phases": phases, "checkpoints": cps}


def sign(v, eps=1e-9):
    if v > eps:
        return 1
    if v < -eps:
        return -1
    return 0


def consistency(per_date):
    signals = []
    for a, b in PHASES:
        pk = f"{a}_{b}"
        for m in MARKET_METRICS:
            vals = {d: per_date[d]["diff"]["phases"][pk][m] for d in DATES}
            ss = [sign(vals[d]) for d in DATES]
            if ss[0] != 0 and ss.count(ss[0]) == len(ss):
                signals.append({"kind": "phase", "location": pk, "metric": m, "sign": ss[0], "date_diffs": vals, "mean_abs_diff": statistics.mean(abs(v) for v in vals.values())})
    for t in CHECKPOINTS:
        tk = str(t)
        for m in COMP_METRICS:
            vals = {d: per_date[d]["diff"]["checkpoints"][tk][m] for d in DATES}
            ss = [sign(vals[d]) for d in DATES]
            if ss[0] != 0 and ss.count(ss[0]) == len(ss):
                signals.append({"kind": "checkpoint", "location": tk, "metric": m, "sign": ss[0], "date_diffs": vals, "mean_abs_diff": statistics.mean(abs(v) for v in vals.values())})
    signals.sort(key=lambda x: x["mean_abs_diff"], reverse=True)
    return signals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    rows = []
    with tempfile.TemporaryDirectory(prefix="kculture-kexp047-") as tmp:
        root = Path(tmp)
        for date in DATES:
            handle = f"kaggle/kaggriculture-episodes-{date}"
            manifest = sorted(csv_rows(dl(handle, "manifest.csv", root / date / "manifest")), key=lambda r: -float(r["avg_score"]))[:args.top]
            for mr in manifest:
                eid = str(mr["episode_id"])
                rep = json.loads(dl(handle, f"{eid}.json", root / date / eid).read_text(encoding="utf-8"))
                steps = rep.get("steps") or []
                if len(steps) < 720:
                    continue
                rewards = [steps[-1][p].get("reward") for p in (0, 1)]
                if not all(isinstance(x, (int, float)) for x in rewards) or rewards[0] == rewards[1]:
                    continue
                winner = 0 if rewards[0] > rewards[1] else 1
                loser = 1 - winner
                rows.append(profile(rep, winner, date, eid, "winner", rewards[winner]))
                rows.append(profile(rep, loser, date, eid, "loser", rewards[loser]))

    per_date = {}
    for date in DATES:
        wr = [r for r in rows if r["date"] == date and r["cohort"] == "winner"]
        lr = [r for r in rows if r["date"] == date and r["cohort"] == "loser"]
        ws, ls = summarize(wr), summarize(lr)
        per_date[date] = {"winner": ws, "loser": ls, "diff": diff_summary(ws, ls)}

    wr = [r for r in rows if r["cohort"] == "winner"]
    lr = [r for r in rows if r["cohort"] == "loser"]
    ws, ls = summarize(wr), summarize(lr)
    payload = {
        "schema_version": "live-economic-allocation-winloss-v1",
        "dates": list(DATES),
        "top_n_per_date": args.top,
        "alignment": "state t -> action frame t+1",
        "overall": {"winner": ws, "loser": ls, "diff": diff_summary(ws, ls)},
        "per_date": per_date,
        "same_sign_all_dates": consistency(per_date),
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"top_consistent_signals": payload["same_sign_all_dates"][:30], "overall_diff": payload["overall"]["diff"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
