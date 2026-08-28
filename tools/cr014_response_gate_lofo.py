"""CR-014: identity-free response-value gate with leave-one-family-out testing.

Generate fresh paired CR-011 vs frozen R4B episodes. At the first actual adaptive
sale, encode only public game state plus trigger mechanics. The opponent path/name
is never a model feature. Train on all but one opponent family, test on the held-
out family, and ask whether a conservative gate can choose CR-011 only when its
response is likely to improve terminal relative value.

This is diagnostic research. It never reads validation/held-out seeds and cannot
by itself authorize a hosted submission.
"""
from __future__ import annotations

import argparse, collections, importlib.util, json, math, statistics, sys, time
from pathlib import Path

from kaggle_environments import make
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidates import cr008_adaptive_frontrun as C

SEEDS = ROOT / "configs/cr014_response_gate_seeds_v1.json"
BASE = "candidates/r4b_ablation_market_only.py"
CAND = "candidates/cr011_adaptive_early_order.py"
CONFIDENCE = 0.70
MODEL_KW = dict(max_depth=3, min_samples_leaf=8, class_weight="balanced", random_state=2026082714)


def load_agent(path):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    spec = importlib.util.spec_from_file_location(f"cr014_{p.stem}_{time.time_ns()}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def play(cpath, opath, seed, seat):
    ca, oa = load_agent(cpath), load_agent(opath)
    agents = [ca, oa] if seat == 0 else [oa, ca]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    return env.toJSON()


def final(rep, seat):
    f = rep["steps"][-1]
    st = [f[i].get("status") for i in range(2)]
    rw = [f[i].get("reward") for i in range(2)]
    if st != ["DONE", "DONE"] or not all(isinstance(x, (int, float)) for x in rw):
        return None
    a, b = float(rw[seat]), float(rw[1-seat])
    return a, b, a-b


def action_at(rep, seat, t):
    try:
        x = rep["steps"][t+1][seat].get("action")
        return x if isinstance(x, dict) else {}
    except Exception:
        return {}


def obs_at(rep, seat, t):
    try:
        return rep["steps"][t][seat].get("observation") or {}
    except Exception:
        return {}


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def counter(xs):
    return collections.Counter(canon(x) for x in (xs or []))


def added_orders(a, b):
    out = []
    for s, n in (counter(a.get("market")) - counter(b.get("market"))).items():
        try:
            row = json.loads(s)
        except Exception:
            continue
        out.extend([row] * n)
    return out


def score(delta):
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def first_trigger_features(j, b, seat):
    limit = min(719, len(j.get("steps") or [])-1, len(b.get("steps") or [])-1)
    for t in range(limit):
        ja, ba = action_at(j, seat, t), action_at(b, seat, t)
        if ja == ba:
            continue
        add = [o for o in added_orders(ja, ba)
               if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"
               and o[1] in ("CARROT", "STRAWBERRY")]
        if not add:
            continue
        obs = obs_at(j, seat, t)
        prev = obs_at(j, seat, max(0, t-24))
        feat = C._public_features(obs, prev, seat)
        if not feat:
            return None
        row = add[0]
        market = C._get(obs, "market", {}) or {}
        prices = C._get(market, "prices", {}) or {}
        inv = C._get(market, "inventory", {}) or {}
        try: qty = float(row[2] or 0)
        except Exception: qty = 0.0
        item = str(row[1])
        feat = {k: float(v) if isinstance(v, (int, float)) and math.isfinite(float(v)) else 0.0
                for k, v in feat.items()}
        feat.update({
            "gate_trigger_qty": qty,
            "gate_trigger_price": C._num(prices, item),
            "gate_trigger_market_inventory": C._num(inv, item),
            "gate_base_market_count": float(len(ba.get("market") or [])),
            "gate_is_strawberry": 1.0 if item == "STRAWBERRY" else 0.0,
            "gate_is_carrot": 1.0 if item == "CARROT" else 0.0,
        })
        return {"state": t, "item": item, "features": feat}
    return None


def export_tree(clf, names):
    tr = clf.tree_
    vals = []
    for x in tr.value:
        vals.append([float(v) for v in x[0]])
    return {
        "feature_names": names,
        "confidence": CONFIDENCE,
        "classes": [int(x) for x in clf.classes_],
        "children_left": [int(x) for x in tr.children_left],
        "children_right": [int(x) for x in tr.children_right],
        "feature": [int(x) for x in tr.feature],
        "threshold": [float(x) for x in tr.threshold],
        "value": vals,
        "model_kwargs": MODEL_KW,
    }


def mean(xs):
    return statistics.mean(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", action="append", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model-output", required=True)
    args = ap.parse_args()

    seeds = json.loads(SEEDS.read_text())["seeds"]
    rows, errors = [], 0
    for opp in args.opponent:
        for seed in seeds:
            for seat in (0, 1):
                j, b = play(CAND, opp, seed, seat), play(BASE, opp, seed, seat)
                jf, bf = final(j, seat), final(b, seat)
                if jf is None or bf is None:
                    errors += 1
                    continue
                trig = first_trigger_features(j, b, seat)
                jr, jo, jd = jf; br, bo, bd = bf
                rows.append({
                    "opponent": opp, "seed": seed, "seat": seat,
                    "base_reward": br, "base_delta": bd, "base_score": score(bd),
                    "cand_reward": jr, "cand_delta": jd, "cand_score": score(jd),
                    "self_gain": jr-br, "relative_gain": jd-bd,
                    "score_gain": score(jd)-score(bd),
                    "trigger": trig,
                })

    affected = [r for r in rows if r["trigger"] is not None]
    feature_names = sorted({k for r in affected for k in r["trigger"]["features"]})
    families = sorted({r["opponent"] for r in rows})
    predictions = {}
    fold_reports = {}

    for hold in families:
        train = [r for r in affected if r["opponent"] != hold]
        test = [r for r in affected if r["opponent"] == hold]
        y = [1 if r["relative_gain"] > 0 else 0 for r in train]
        if len(train) < 30 or len(test) < 3 or len(set(y)) < 2:
            fold_reports[hold] = {"evaluable": False, "train": len(train), "test": len(test)}
            continue
        X = [[r["trigger"]["features"].get(k, 0.0) for k in feature_names] for r in train]
        XT = [[r["trigger"]["features"].get(k, 0.0) for k in feature_names] for r in test]
        clf = DecisionTreeClassifier(**MODEL_KW).fit(X, y)
        classes = list(clf.classes_)
        pos = classes.index(1)
        probs = clf.predict_proba(XT)[:, pos]
        enabled = 0; harmful_disabled = 0; harmful = 0; beneficial_enabled = 0; beneficial = 0
        for r, p in zip(test, probs):
            use = bool(float(p) >= CONFIDENCE)
            predictions[(r["opponent"], r["seed"], r["seat"])] = {"prob": float(p), "use": use}
            enabled += int(use)
            harmful += int(r["relative_gain"] < 0)
            harmful_disabled += int(r["relative_gain"] < 0 and not use)
            beneficial += int(r["relative_gain"] > 0)
            beneficial_enabled += int(r["relative_gain"] > 0 and use)
        fold_reports[hold] = {
            "evaluable": True, "train": len(train), "test": len(test), "enabled": enabled,
            "harmful": harmful,
            "harmful_disabled_fraction": harmful_disabled/harmful if harmful else None,
            "beneficial": beneficial,
            "beneficial_enabled_fraction": beneficial_enabled/beneficial if beneficial else None,
        }

    chosen = []
    per = {}
    for r in rows:
        k = (r["opponent"], r["seed"], r["seat"])
        pred = predictions.get(k)
        use = bool(pred and pred["use"])
        chosen_reward = r["cand_reward"] if use else r["base_reward"]
        chosen_delta = r["cand_delta"] if use else r["base_delta"]
        chosen_score = r["cand_score"] if use else r["base_score"]
        chosen.append({**r, "gate_probability": pred["prob"] if pred else None, "gate_use": use,
                       "gated_self_gain": chosen_reward-r["base_reward"],
                       "gated_relative_gain": chosen_delta-r["base_delta"],
                       "gated_score_gain": chosen_score-r["base_score"]})

    for opp in families:
        xs = [r for r in chosen if r["opponent"] == opp]
        per[opp] = {
            "pairs": len(xs), "affected": sum(r["trigger"] is not None for r in xs),
            "enabled": sum(r["gate_use"] for r in xs),
            "mean_self_gain": mean([r["gated_self_gain"] for r in xs]),
            "mean_relative_gain": mean([r["gated_relative_gain"] for r in xs]),
            "mean_score_gain": mean([r["gated_score_gain"] for r in xs]),
        }

    evaluable = [x for x in fold_reports.values() if x.get("evaluable")]
    enabled_rows = [r for r in chosen if r["gate_use"]]
    harmful_rows = [r for r in affected if r["relative_gain"] < 0 and (r["opponent"],r["seed"],r["seat"]) in predictions]
    harmful_disabled = [r for r in harmful_rows if not predictions[(r["opponent"],r["seed"],r["seat"])]["use"]]
    beneficial_rows = [r for r in affected if r["relative_gain"] > 0 and (r["opponent"],r["seed"],r["seat"]) in predictions]
    beneficial_enabled = [r for r in beneficial_rows if predictions[(r["opponent"],r["seed"],r["seat"])]["use"]]

    overall_self = mean([r["gated_self_gain"] for r in chosen])
    overall_rel = mean([r["gated_relative_gain"] for r in chosen])
    overall_score = mean([r["gated_score_gain"] for r in chosen])
    favorable = sum(r["gated_score_gain"] > 0 for r in chosen)
    unfavorable = sum(r["gated_score_gain"] < 0 for r in chosen)
    worst_family_score = min((v["mean_score_gain"] for v in per.values()), default=None)

    gate = {
        "zero_errors": errors == 0,
        "evaluable_families_ge_6": len(evaluable) >= 6,
        "enabled_episodes_ge_15": len(enabled_rows) >= 15,
        "mean_self_gain_positive": overall_self is not None and overall_self > 0,
        "mean_relative_gain_positive": overall_rel is not None and overall_rel > 0,
        "mean_score_gain_nonnegative": overall_score is not None and overall_score >= 0,
        "harmful_suppression_ge_0_60": bool(harmful_rows) and len(harmful_disabled)/len(harmful_rows) >= 0.60,
        "beneficial_retention_ge_0_30": bool(beneficial_rows) and len(beneficial_enabled)/len(beneficial_rows) >= 0.30,
        "no_family_score_regression_gt_0_08": worst_family_score is not None and worst_family_score >= -0.08,
        "favorable_outcome_changes_ge_unfavorable": favorable >= unfavorable,
    }
    passed = all(gate.values())

    # Final deployable tree is fit only after the LOFO evaluation is fully defined.
    final_model = None
    if affected and len(set(1 if r["relative_gain"] > 0 else 0 for r in affected)) == 2:
        X = [[r["trigger"]["features"].get(k, 0.0) for k in feature_names] for r in affected]
        y = [1 if r["relative_gain"] > 0 else 0 for r in affected]
        final_clf = DecisionTreeClassifier(**MODEL_KW).fit(X, y)
        final_model = export_tree(final_clf, feature_names)
        Path(args.model_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.model_output).write_text(json.dumps(final_model, indent=2, sort_keys=True))

    payload = {
        "experiment": "CR-014",
        "status": "IDENTITY_FREE_RESPONSE_GATE_SUPPORTED" if passed else "IDENTITY_FREE_RESPONSE_GATE_NOT_SUPPORTED",
        "pairs": len(rows), "affected_pairs": len(affected), "errors": errors,
        "model": {"confidence": CONFIDENCE, **MODEL_KW},
        "summary": {
            "evaluable_families": len(evaluable), "enabled_episodes": len(enabled_rows),
            "mean_self_gain": overall_self, "mean_relative_gain": overall_rel,
            "mean_score_gain": overall_score,
            "harmful_suppression": len(harmful_disabled)/len(harmful_rows) if harmful_rows else None,
            "beneficial_retention": len(beneficial_enabled)/len(beneficial_rows) if beneficial_rows else None,
            "favorable_outcome_changes": favorable, "unfavorable_outcome_changes": unfavorable,
            "worst_family_score_gain": worst_family_score,
        },
        "folds": fold_reports, "per_opponent": per, "gate": gate,
        "rows": chosen,
        "interpretation": "LOFO uses no opponent identity feature. PASS authorizes one bounded episode-latched response-gate candidate on fresh exploratory seeds; it is not a promotion or held-out authorization."
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps({k:v for k,v in payload.items() if k != "rows"}, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
