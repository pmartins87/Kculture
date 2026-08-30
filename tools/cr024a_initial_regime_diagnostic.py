"""CR024A Stage-A-only diagnostic for raw-backbone harmful regimes.

Uses only the already-open CR023 raw Stage-A seeds.  Seed is used solely to join
an offline outcome label; candidate runtime features are public initial-state
features only.  No Stage-B or held-out seed is touched here.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import math
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
CR008 = ROOT / "candidates/cr008_adaptive_frontrun.py"
OUT = ROOT / "artifacts/cr024a_regime_diagnostic/report.json"

# Derived from the already-open CR023 Stage-A paired result: every unfavorable
# top11/top19 W/L conversion occurred on one of these two economic seeds.
# This is an OFFLINE LABEL ONLY.  It is never exposed to a candidate agent.
HARMFUL_STAGE_A_SEEDS = {1250543639, 62034274}


def load_agent(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.agent


def num(d: dict, key: str) -> float:
    try:
        x = float((d or {}).get(key, 0) or 0)
        return x if math.isfinite(x) else 0.0
    except Exception:
        return 0.0


def public_initial_features(obs: dict) -> dict[str, float]:
    market = obs.get("market") or {}
    prices = market.get("prices") or {}
    inv = market.get("inventory") or {}
    town = obs.get("town") or {}
    products = sorted(set(prices) | set(inv))
    f: dict[str, float] = {
        "shop_count": float(len(town.get("unlocked_shops") or [])),
    }
    price_values = []
    inv_values = []
    for product in products:
        p = num(prices, product)
        q = num(inv, product)
        lo = str(product).lower()
        f[f"price_{lo}"] = p
        f[f"inventory_{lo}"] = q
        price_values.append(p)
        inv_values.append(q)
    if price_values:
        f["price_sum"] = sum(price_values)
        f["price_min"] = min(price_values)
        f["price_max"] = max(price_values)
        f["price_range"] = max(price_values) - min(price_values)
    if inv_values:
        f["inventory_sum"] = sum(inv_values)
        f["inventory_min"] = min(inv_values)
        f["inventory_max"] = max(inv_values)
        f["inventory_range"] = max(inv_values) - min(inv_values)
    return f


def capture_initial(seed: int) -> dict[str, float]:
    captured: dict[str, float] = {}
    base0 = load_agent(CR008, f"cr024a_a_{seed}")
    base1 = load_agent(CR008, f"cr024a_b_{seed}")

    def recorder(obs, config=None):
        if not captured:
            captured.update(public_initial_features(copy.deepcopy(obs)))
        return base0(obs, config)

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run([recorder, base1])
    if not captured:
        raise RuntimeError(f"no initial observation captured for seed {seed}")
    return captured


def candidate_thresholds(rows: list[dict]) -> list[dict]:
    names = sorted({k for r in rows for k in r["features"]})
    out = []
    for name in names:
        vals = sorted({float(r["features"].get(name, 0.0)) for r in rows})
        if len(vals) < 2:
            continue
        mids = [(a + b) / 2.0 for a, b in zip(vals, vals[1:]) if a != b]
        for threshold in mids:
            for direction in ("le", "ge"):
                tp = tn = fp = fn = 0
                for r in rows:
                    x = float(r["features"].get(name, 0.0))
                    pred = x <= threshold if direction == "le" else x >= threshold
                    y = bool(r["harmful"])
                    if pred and y: tp += 1
                    elif pred and not y: fp += 1
                    elif not pred and y: fn += 1
                    else: tn += 1
                tpr = tp / max(1, tp + fn)
                tnr = tn / max(1, tn + fp)
                bal = 0.5 * (tpr + tnr)
                out.append({
                    "feature": name,
                    "direction": direction,
                    "threshold": threshold,
                    "tp": tp, "tn": tn, "fp": fp, "fn": fn,
                    "balanced_accuracy": bal,
                })
    out.sort(key=lambda d: (-d["balanced_accuracy"], d["fp"] + d["fn"], d["feature"], d["threshold"]))
    return out


def main():
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    seeds = [int(x) for x in cfg["raw_backbone_stage_a_seeds"]]
    assert not (set(seeds) & set(cfg["raw_backbone_stage_b_seeds"])), "Stage A/B overlap"
    rows = []
    for seed in seeds:
        rows.append({
            "seed": seed,
            "harmful": seed in HARMFUL_STAGE_A_SEEDS,
            "features": capture_initial(seed),
        })
    rules = candidate_thresholds(rows)
    payload = {
        "experiment": "CR024A",
        "stage": "INITIAL_REGIME_DIAGNOSTIC_STAGE_A_ONLY",
        "runtime_identity_features_used": False,
        "runtime_seed_feature_allowed": False,
        "stage_b_touched": False,
        "held_out_touched": False,
        "harmful_label_count": sum(bool(r["harmful"]) for r in rows),
        "safe_label_count": sum(not bool(r["harmful"]) for r in rows),
        "rows": rows,
        "top_univariate_public_rules": rules[:30],
        "policy": "Diagnostic only. No rule is promoted without mechanistic review and a frozen fresh Stage-B test.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("experiment", "stage", "harmful_label_count", "safe_label_count", "stage_b_touched", "held_out_touched")}, indent=2))
    print(json.dumps(payload["top_univariate_public_rules"][:10], indent=2))


if __name__ == "__main__":
    main()
