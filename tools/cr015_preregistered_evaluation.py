"""CR-015 preregistered fresh evaluation protocol.

This evaluator is intentionally candidate-agnostic.  Its Stage-A/Stage-B seeds
were frozen before CR-014 completed, so a CR-014-derived refinement cannot pick
its own evaluation distribution.

For each tuple (seed, exact current-meta opponent, seat), run frozen R4B,
frozen CR-011, and the supplied frozen CR-015 candidate.  Close-boundary tuples
are selected using R4B alone; neither CR-011 nor CR-015 may influence selection.
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

CONFIG = ROOT / "configs/cr015_fresh_preregistered_seeds_v1.json"
R4B = ROOT / "candidates/r4b_ablation_market_only.py"
CR011 = ROOT / "candidates/cr011_adaptive_early_order.py"


def load_agent(path: Path):
    spec = importlib.util.spec_from_file_location(
        f"cr015_{path.stem}_{time.time_ns()}", path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.agent


def play(agent_path: Path, opponent_path: Path, seed: int, seat: int):
    own = load_agent(agent_path)
    opp = load_agent(opponent_path)
    agents = [own, opp] if seat == 0 else [opp, own]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=True,
    )
    env.run(agents)
    frame = env.toJSON()["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    rewards = [frame[i].get("reward") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses: {statuses}")
    self_reward = float(rewards[seat])
    opp_reward = float(rewards[1 - seat])
    return self_reward, opp_reward, self_reward - opp_reward


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def contrast(rows, arm: str, control: str):
    rel = [r[arm]["delta"] - r[control]["delta"] for r in rows]
    own = [r[arm]["self"] - r[control]["self"] for r in rows]
    sg = [score(r[arm]["delta"]) - score(r[control]["delta"]) for r in rows]
    fav = sum(x > 0 for x in sg)
    bad = sum(x < 0 for x in sg)
    return {
        "pairs": len(rows),
        "mean_relative_gain": statistics.mean(rel) if rel else 0.0,
        "median_relative_gain": statistics.median(rel) if rel else 0.0,
        "mean_self_gain": statistics.mean(own) if own else 0.0,
        "mean_score_gain": statistics.mean(sg) if sg else 0.0,
        "favorable_outcome_changes": fav,
        "unfavorable_outcome_changes": bad,
        "unchanged_outcomes": len(rows) - fav - bad,
        "positive_relative_fraction": (
            sum(x > 0 for x in rel) / len(rel) if rel else 0.0
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--stage", choices=("a", "b"), required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--close-target", type=int, default=40)
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    seeds = cfg["stage_a_seeds" if args.stage == "a" else "stage_b_seeds"]
    candidate = Path(args.candidate)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    opp_dir = Path(args.opponent_dir)
    if not opp_dir.is_absolute():
        opp_dir = ROOT / opp_dir

    opponents = sorted(p for p in opp_dir.glob("*.py") if p.is_file())
    if not opponents:
        raise SystemExit(f"no opponents in {opp_dir}")

    rows = []
    errors = []
    for seed in seeds:
        for opponent in opponents:
            for seat in (0, 1):
                row = {
                    "seed": int(seed),
                    "opponent": opponent.stem,
                    "seat": seat,
                }
                for key, path in (("r4b", R4B), ("cr011", CR011), ("cr015", candidate)):
                    try:
                        self_reward, opp_reward, delta = play(path, opponent, seed, seat)
                        row[key] = {
                            "self": self_reward,
                            "opp": opp_reward,
                            "delta": delta,
                            "score": score(delta),
                        }
                    except Exception as exc:
                        errors.append(
                            {
                                "seed": int(seed),
                                "opponent": opponent.stem,
                                "seat": seat,
                                "arm": key,
                                "error": repr(exc),
                            }
                        )
                        row[key] = None
                        break
                if all(row.get(k) is not None for k in ("r4b", "cr011", "cr015")):
                    rows.append(row)

    ordered = sorted(rows, key=lambda r: abs(r["r4b"]["delta"]))
    close = ordered[: min(args.close_target, len(ordered))]

    broad_r4b = contrast(rows, "cr015", "r4b")
    broad_cr011 = contrast(rows, "cr015", "cr011")
    close_r4b = contrast(close, "cr015", "r4b")
    close_cr011 = contrast(close, "cr015", "cr011")

    no_net_harm = (
        broad_r4b["mean_score_gain"] >= 0
        and broad_cr011["mean_score_gain"] >= 0
        and close_r4b["unfavorable_outcome_changes"] <= close_r4b["favorable_outcome_changes"]
        and close_cr011["unfavorable_outcome_changes"] <= close_cr011["favorable_outcome_changes"]
    )
    outcome_signal = (
        close_r4b["favorable_outcome_changes"] > close_r4b["unfavorable_outcome_changes"]
        or close_cr011["favorable_outcome_changes"] > close_cr011["unfavorable_outcome_changes"]
        or broad_r4b["mean_score_gain"] > 0
        or broad_cr011["mean_score_gain"] > 0
    )
    relative_supported = broad_r4b["mean_relative_gain"] > 0

    stage_a_supported = (
        args.stage == "a"
        and not errors
        and len(rows) == len(seeds) * len(opponents) * 2
        and no_net_harm
        and outcome_signal
        and relative_supported
    )

    payload = {
        "experiment": "CR-015",
        "stage": args.stage.upper(),
        "candidate": str(candidate.relative_to(ROOT)),
        "seed_config": str(CONFIG.relative_to(ROOT)),
        "seeds": seeds,
        "opponents": [p.stem for p in opponents],
        "expected_pairs": len(seeds) * len(opponents) * 2,
        "completed_pairs": len(rows),
        "errors": errors,
        "close_selection": {
            "rule": "smallest absolute frozen R4B terminal money delta only",
            "target": args.close_target,
            "selected": len(close),
            "mean_abs_r4b_delta": (
                statistics.mean(abs(r["r4b"]["delta"]) for r in close)
                if close
                else None
            ),
        },
        "broad": {
            "cr015_vs_r4b": broad_r4b,
            "cr015_vs_cr011": broad_cr011,
        },
        "close": {
            "cr015_vs_r4b": close_r4b,
            "cr015_vs_cr011": close_cr011,
        },
        "stage_a_gate": {
            "zero_errors": not errors,
            "no_net_wl_harm": no_net_harm,
            "outcome_conversion_signal": outcome_signal,
            "mean_relative_gain_vs_r4b_positive": relative_supported,
            "supported": stage_a_supported,
        },
        "policy": "Stage B may run only for the unchanged frozen candidate if Stage A supported=true. No candidate code/threshold changes between stages.",
        "rows": rows,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {k: v for k, v in payload.items() if k not in ("rows", "errors")}
    compact["error_count"] = len(errors)
    print(json.dumps(compact, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)
    if args.stage == "a" and not stage_a_supported:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
