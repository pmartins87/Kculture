"""Aggregate the full CR-002 league and test calibration against hosted history."""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/competitive_reset_league_v1.json")
    ap.add_argument("--reports-dir", default="artifacts/cr002/reports")
    ap.add_argument("--output", default="artifacts/cr002/league_result.json")
    args = ap.parse_args()

    cfg = json.loads((ROOT / args.config).read_text(encoding="utf-8"))
    ids = [x["id"] for x in cfg["public_agents"]] + [x["id"] for x in cfg["local_agents"]]
    public_scores = {x["id"]: float(x["historical_score"]) for x in cfg["public_agents"]}
    hosted_local = {x["id"]: float(x["hosted_snapshot"]) for x in cfg["local_agents"]}
    idx = {a: i for i, a in enumerate(ids)}

    reports = []
    for path in sorted((ROOT / args.reports_dir).glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("league_id") == cfg["league_id"]:
            reports.append(d)

    expected_pairs = len(ids) * (len(ids) - 1) // 2
    pair_keys = {tuple(sorted((r["agent_a"], r["agent_b"]))) for r in reports}
    duplicate_count = len(reports) - len(pair_keys)
    error_count = sum(int(r["overall_from_a_perspective"].get("errors", 0) or 0) for r in reports)

    pair_obs = []
    direct = {}
    for r in reports:
        a, b = r["agent_a"], r["agent_b"]
        s = r["overall_from_a_perspective"]
        n = int(s["valid_episodes"])
        wins = int(s["wins"])
        losses = int(s["losses"])
        ties = int(s["ties"])
        score_a = wins + 0.5 * ties
        pair_obs.append((idx[a], idx[b], n, score_a))
        direct[f"{a}__vs__{b}"] = {
            "a": a, "b": b, "games": n,
            "wins_a": wins, "losses_a": losses, "ties": ties,
            "score_a": score_a / n if n else None,
            "mean_money_delta_a": s.get("mean_money_delta"),
        }

    def unpack(x: np.ndarray) -> np.ndarray:
        theta = np.zeros(len(ids), dtype=float)
        theta[1:] = x
        return theta

    def objective(x: np.ndarray) -> float:
        theta = unpack(x)
        loss = 0.0
        for i, j, n, score_i in pair_obs:
            d = float(np.clip(theta[i] - theta[j], -30, 30))
            p = sigmoid(d)
            p = min(max(p, 1e-12), 1 - 1e-12)
            loss -= score_i * math.log(p) + (n - score_i) * math.log(1 - p)
        # tiny ridge prevents divergence on near-separated subsets
        loss += 1e-5 * float(np.dot(theta, theta))
        return loss

    if reports:
        opt = minimize(objective, np.zeros(len(ids) - 1), method="BFGS")
        theta = unpack(opt.x)
        theta -= float(np.mean(theta))
    else:
        opt = None
        theta = np.zeros(len(ids))

    elo_scale = 400.0 / math.log(10.0)
    rows = []
    for a in ids:
        t = float(theta[idx[a]])
        rows.append({
            "id": a,
            "bt_log_strength": t,
            "bt_elo_centered": t * elo_scale,
            "historical_public_score": public_scores.get(a),
            "hosted_kculture_snapshot": hosted_local.get(a),
        })
    rows.sort(key=lambda r: r["bt_log_strength"], reverse=True)
    for rank, row in enumerate(rows, 1):
        row["local_bt_rank"] = rank

    public_rows = [r for r in rows if r["id"] in public_scores]
    if len(public_rows) >= 3:
        hist = [r["historical_public_score"] for r in public_rows]
        local = [r["bt_log_strength"] for r in public_rows]
        corr_obj = spearmanr(hist, local)
        spearman = float(corr_obj.statistic)
        spearman_p = float(corr_obj.pvalue)
    else:
        spearman = float("nan")
        spearman_p = float("nan")

    ordered_correct = 0.0
    ordered_total = 0
    for a, b in itertools.combinations(public_scores, 2):
        historical_sign = 1 if public_scores[a] > public_scores[b] else -1
        local_diff = float(theta[idx[a]] - theta[idx[b]])
        if abs(local_diff) < 1e-12:
            ordered_correct += 0.5
        elif (local_diff > 0 and historical_sign > 0) or (local_diff < 0 and historical_sign < 0):
            ordered_correct += 1.0
        ordered_total += 1
    order_accuracy = ordered_correct / ordered_total if ordered_total else None

    # Majority-edge rock-paper-scissors triangles are a compact non-transitivity diagnostic.
    majority = {}
    for r in direct.values():
        if r["score_a"] is None or r["score_a"] == 0.5:
            continue
        winner, loser = (r["a"], r["b"]) if r["score_a"] > 0.5 else (r["b"], r["a"])
        majority[(winner, loser)] = True
    cycles = []
    for a, b, c in itertools.combinations(ids, 3):
        if ((a, b) in majority and (b, c) in majority and (c, a) in majority):
            cycles.append([a, b, c])
        elif ((b, a) in majority and (c, b) in majority and (a, c) in majority):
            cycles.append([b, a, c])

    gate_cfg = cfg["calibration_gate"]
    completeness_pass = len(pair_keys) == expected_pairs and duplicate_count == 0
    zero_errors_pass = error_count == 0
    spearman_pass = math.isfinite(spearman) and spearman >= float(gate_cfg["public_spearman_min"])
    order_pass = order_accuracy is not None and order_accuracy >= float(gate_cfg["public_pair_order_accuracy_min"])
    gate_pass = completeness_pass and zero_errors_pass and spearman_pass and order_pass

    result = {
        "experiment": "CR-002",
        "league_id": cfg["league_id"],
        "status": "CALIBRATED_PASS" if gate_pass else "CALIBRATION_FAIL",
        "pair_reports_found": len(reports),
        "unique_pairs_found": len(pair_keys),
        "expected_pairs": expected_pairs,
        "duplicate_pair_reports": duplicate_count,
        "runtime_error_count": error_count,
        "fit": {
            "optimizer_success": bool(opt.success) if opt is not None else False,
            "optimizer_message": str(opt.message) if opt is not None else "no reports",
            "objective": float(opt.fun) if opt is not None else None,
        },
        "calibration": {
            "public_spearman": spearman,
            "public_spearman_p": spearman_p,
            "public_bt_order_accuracy": order_accuracy,
            "public_agent_count": len(public_rows),
            "gate_thresholds": gate_cfg,
            "gate_components": {
                "complete_pair_matrix": completeness_pass,
                "zero_runtime_errors": zero_errors_pass,
                "spearman": spearman_pass,
                "order_accuracy": order_pass,
            },
        },
        "ranking": rows,
        "direct_pairs": direct,
        "majority_cycle_count": len(cycles),
        "majority_cycles": cycles[:100],
        "interpretation": (
            "This proxy league is calibrated enough to become a promotion signal."
            if gate_pass
            else "Do not use this proxy league for promotion yet; expand/reweight the field or episode design."
        ),
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "pairs": [len(pair_keys), expected_pairs],
        "errors": error_count,
        "public_spearman": spearman,
        "public_bt_order_accuracy": order_accuracy,
        "majority_cycle_count": len(cycles),
        "ranking": [(r["local_bt_rank"], r["id"], round(r["bt_elo_centered"], 2), r["historical_public_score"], r["hosted_kculture_snapshot"]) for r in rows],
    }, indent=2))

    if not completeness_pass or not zero_errors_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
