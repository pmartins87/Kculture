"""CR-015 causal sanity check on the 16 already-diagnosed CR-014B pairs.

This is NOT validation. It verifies that the frozen CR-015 gate implements the
intended structural choice at the first CR-008/CR-011 divergence and reports
terminal effects on the old diagnostic cases. Fresh preregistered Stage A is the
actual promotion test.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CFG = ROOT / "configs/cr014b_affected_pairs_v1.json"
ARMS = {
    "cr008": ROOT / "candidates/cr008_adaptive_frontrun.py",
    "cr011": ROOT / "candidates/cr011_adaptive_early_order.py",
    "cr015": ROOT / "candidates/cr015_liquidation_phase_early_order.py",
}


def load_agent(path: Path):
    spec = importlib.util.spec_from_file_location(
        f"cr015sanity_{path.stem}_{time.time_ns()}", path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.agent


def play(path: Path, opponent: Path, seed: int, seat: int):
    a = load_agent(path)
    o = load_agent(opponent)
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=True,
    )
    env.run([a, o] if seat == 0 else [o, a])
    return env.toJSON()


def final(rep, seat: int):
    frame = rep["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses {statuses}")
    own = float(frame[seat].get("reward"))
    opp = float(frame[1-seat].get("reward"))
    return own, opp, own - opp


def score(delta: float):
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def action(rep, seat: int, t: int):
    x = rep["steps"][t + 1][seat].get("action")
    return x if isinstance(x, dict) else {}


def observation(rep, seat: int, t: int):
    x = rep["steps"][t][seat].get("observation")
    return x if isinstance(x, dict) else {}


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def first_divergence(rep8, rep11, seat: int):
    n = min(len(rep8["steps"]), len(rep11["steps"])) - 1
    for t in range(n):
        a8 = action(rep8, seat, t)
        a11 = action(rep11, seat, t)
        if a8 != a11:
            return t, a8, a11, observation(rep8, seat, t), observation(rep11, seat, t)
    return None


def base_starts_sell_from_cr008(a8, a11):
    m8 = list(a8.get("market") or [])
    m11 = list(a11.get("market") or [])
    if not m8 or not m11:
        return False
    # CR-011 prefixes the identical adaptive order(s), while CR-008 appends.
    # For the frozen CR-014B cases there is one adaptive product at the first
    # divergence, so dropping CR-008's last order reconstructs the base queue.
    base = m8[:-1]
    first = base[0] if base else None
    return isinstance(first, list) and len(first) >= 2 and first[0] == "SELL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    od = Path(args.opponent_dir)
    if not od.is_absolute():
        od = ROOT / od
    cfg = json.loads(CFG.read_text(encoding="utf-8"))

    rows = []
    errors = []
    gate_errors = []
    for e in cfg["pairs"]:
        opp = od / f"{e['opponent']}.py"
        seed = int(e["seed"])
        seat = int(e["seat"])
        try:
            reps = {k: play(p, opp, seed, seat) for k, p in ARMS.items()}
            vals = {}
            for k, rep in reps.items():
                own, other, delta = final(rep, seat)
                vals[k] = {
                    "self": own,
                    "opp": other,
                    "delta": delta,
                    "score": score(delta),
                }

            fd = first_divergence(reps["cr008"], reps["cr011"], seat)
            if fd is None:
                raise RuntimeError("expected CR008/CR011 divergence not found")
            t, a8, a11, o8, o11 = fd
            if canon(o8) != canon(o11):
                raise RuntimeError("CR008/CR011 observations differ at first action divergence")
            a15 = action(reps["cr015"], seat, t)
            starts_sell = base_starts_sell_from_cr008(a8, a11)
            expected_arm = "cr011" if starts_sell else "cr008"
            expected_action = a11 if starts_sell else a8
            gate_ok = a15 == expected_action
            if not gate_ok:
                gate_errors.append({
                    "opponent": e["opponent"], "seed": seed, "seat": seat,
                    "step": t, "starts_sell": starts_sell,
                    "expected_arm": expected_arm,
                    "cr008_action": a8, "cr011_action": a11, "cr015_action": a15,
                })
            rows.append({
                "opponent": e["opponent"],
                "seed": seed,
                "seat": seat,
                "cr014_score_gain": float(e["score_gain"]),
                "first_difference_step": t,
                "base_starts_with_sell": starts_sell,
                "expected_first_action_arm": expected_arm,
                "first_action_gate_ok": gate_ok,
                "terminal": vals,
                "cr015_vs_cr008": {
                    "relative": vals["cr015"]["delta"] - vals["cr008"]["delta"],
                    "self": vals["cr015"]["self"] - vals["cr008"]["self"],
                    "score": vals["cr015"]["score"] - vals["cr008"]["score"],
                },
                "cr015_vs_cr011": {
                    "relative": vals["cr015"]["delta"] - vals["cr011"]["delta"],
                    "self": vals["cr015"]["self"] - vals["cr011"]["self"],
                    "score": vals["cr015"]["score"] - vals["cr011"]["score"],
                },
            })
        except Exception as exc:
            errors.append({
                "opponent": e["opponent"], "seed": seed, "seat": seat,
                "error": repr(exc),
            })

    def contrast(name):
        xs = [r[name] for r in rows]
        return {
            k: statistics.mean(x[k] for x in xs) if xs else 0.0
            for k in ("relative", "self", "score")
        }

    catastrophic = [r for r in rows if r["cr014_score_gain"] < 0]
    favorable = [r for r in rows if r["cr014_score_gain"] > 0]
    payload = {
        "experiment": "CR-015-diagnostic-sanity",
        "status": "PASS" if not errors and not gate_errors else "FAIL",
        "validation_status": "DIAGNOSTIC_ONLY",
        "pairs": len(rows),
        "errors": errors,
        "gate_errors": gate_errors,
        "sell_first_pairs": sum(r["base_starts_with_sell"] for r in rows),
        "spend_first_pairs": sum(not r["base_starts_with_sell"] for r in rows),
        "all": {
            "cr015_vs_cr008": contrast("cr015_vs_cr008"),
            "cr015_vs_cr011": contrast("cr015_vs_cr011"),
        },
        "catastrophic_original_pairs": [
            {
                "opponent": r["opponent"], "seed": r["seed"], "seat": r["seat"],
                "cr008_score": r["terminal"]["cr008"]["score"],
                "cr011_score": r["terminal"]["cr011"]["score"],
                "cr015_score": r["terminal"]["cr015"]["score"],
                "cr015_delta": r["terminal"]["cr015"]["delta"],
            }
            for r in catastrophic
        ],
        "favorable_original_pairs": [
            {
                "opponent": r["opponent"], "seed": r["seed"], "seat": r["seat"],
                "cr008_score": r["terminal"]["cr008"]["score"],
                "cr011_score": r["terminal"]["cr011"]["score"],
                "cr015_score": r["terminal"]["cr015"]["score"],
                "cr015_delta": r["terminal"]["cr015"]["delta"],
            }
            for r in favorable
        ],
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {k: v for k, v in payload.items() if k not in ("rows", "errors", "gate_errors")}
    compact["error_count"] = len(errors)
    compact["gate_error_count"] = len(gate_errors)
    print(json.dumps(compact, indent=2, sort_keys=True))
    if errors or gate_errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
