"""CR071 initial-regime stump search.

Preregistered before the 64-seed CR053-vs-CR070A forensic run is opened.

Purpose
-------
Test whether *step-0 shared environment state* contains a simple, causal regime
signal for choosing the complete CR053 route versus the complete CR070A/Tetsu
route before those policies diverge.

Firewall
--------
- first 32 paired seeds: discovery (already open in historical league)
- remaining 32 paired seeds: one-shot fresh validation
- allowed features: step-0 shared market prices, shared market inventory, shop count
- forbidden: seed value, player/opponent identity, names/ranks, any checkpoint > 0,
  own/opp farm state, private shed/seeds, final margins as a tuning target
- model class: one scalar threshold stump only
- primary discovery target: paired route-winner classification score; a seed where
  CR053 and CR070A split seats contributes 0.5 regardless of prediction
- this tool can only nominate a route-selector hypothesis. It cannot promote a
  Kaggle candidate; any selector must later run as an actual agent through the
  exact-reference multi-opponent panel and then receive larger-seed confirmation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _feature_map(snapshot: dict) -> dict[str, float]:
    out: dict[str, float] = {}
    for item, value in sorted((snapshot.get("market_prices") or {}).items()):
        try:
            out[f"price_{item}"] = float(value)
        except Exception:
            pass
    for item, value in sorted((snapshot.get("market_inventory") or {}).items()):
        try:
            out[f"inventory_{item}"] = float(value)
        except Exception:
            pass
    out["shop_count"] = float(len(snapshot.get("shops") or []))
    return out


def _seed_rows(payload: dict) -> list[dict]:
    grouped: dict[int, list[dict]] = {}
    for row in payload.get("rows", []):
        grouped.setdefault(int(row["seed"]), []).append(row)
    result = []
    for seed, rows in grouped.items():
        if len(rows) != 2:
            continue
        snaps = [r.get("checkpoints", {}).get("0") for r in rows]
        if any(s is None for s in snaps):
            continue
        f0 = _feature_map(snaps[0])
        f1 = _feature_map(snaps[1])
        # Only shared step-0 features are legal, so seat views must agree exactly.
        shared = {k: v for k, v in f0.items() if k in f1 and f1[k] == v}
        pair_score_a = sum(float(r["score_a"]) for r in rows) / 2.0
        result.append({
            "seed": seed,  # retained only for audit; never used as a feature
            "score_a": pair_score_a,
            "features": shared,
        })
    return result


def _choice_score(rows: list[dict], feature: str | None = None, threshold: float | None = None,
                  left_choice: str = "B") -> tuple[float, int, int]:
    total = 0.0
    choose_a = 0
    choose_b = 0
    for row in rows:
        if feature is None:
            choice = left_choice
        else:
            x = row["features"].get(feature)
            if x is None:
                continue
            choice = left_choice if x <= float(threshold) else ("B" if left_choice == "A" else "A")
        choose_a += choice == "A"
        choose_b += choice == "B"
        s = float(row["score_a"])
        if s == 0.5:
            total += 0.5
        elif (s > 0.5 and choice == "A") or (s < 0.5 and choice == "B"):
            total += 1.0
    return total / len(rows) if rows else 0.0, choose_a, choose_b


def _candidate_thresholds(values: list[float]) -> list[float]:
    xs = sorted(set(values))
    if not xs:
        return []
    if len(xs) == 1:
        return [xs[0]]
    return [(a + b) / 2.0 for a, b in zip(xs, xs[1:])]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--discovery-count", type=int, default=32)
    args = ap.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = _seed_rows(payload)
    if len(rows) < args.discovery_count + 1:
        raise SystemExit(f"need >{args.discovery_count} usable paired seeds; got {len(rows)}")

    discovery = rows[: args.discovery_count]
    validation = rows[args.discovery_count :]
    features = sorted(set.intersection(*(set(r["features"]) for r in discovery)))

    const_a = _choice_score(discovery, left_choice="A")[0]
    const_b = _choice_score(discovery, left_choice="B")[0]
    best_constant = max(const_a, const_b)

    candidates = []
    for feature in features:
        thresholds = _candidate_thresholds([r["features"][feature] for r in discovery])
        for threshold in thresholds:
            for left_choice in ("A", "B"):
                score, ca, cb = _choice_score(discovery, feature, threshold, left_choice)
                candidates.append({
                    "feature": feature,
                    "threshold": threshold,
                    "left_choice": left_choice,
                    "discovery_score": score,
                    "discovery_choose_a": ca,
                    "discovery_choose_b": cb,
                })
    candidates.sort(key=lambda x: (-x["discovery_score"], x["feature"], x["threshold"], x["left_choice"]))
    best = candidates[0] if candidates else None
    if best is None:
        raise SystemExit("no legal stump candidates")

    val_score, va, vb = _choice_score(validation, best["feature"], best["threshold"], best["left_choice"])
    val_const_a = _choice_score(validation, left_choice="A")[0]
    val_const_b = _choice_score(validation, left_choice="B")[0]

    # This is a research gate, not promotion. Require meaningful discovery gain,
    # both branches to be exercised, and no collapse on fresh validation.
    min_branch = max(4, int(0.15 * len(discovery)))
    research_gate = bool(
        best["discovery_score"] >= best_constant + 0.0625
        and best["discovery_choose_a"] >= min_branch
        and best["discovery_choose_b"] >= min_branch
        and val_score >= max(val_const_a, val_const_b)
    )

    report = {
        "schema_version": "kculture-cr071-initial-regime-stump-v1",
        "a": payload.get("a"),
        "b": payload.get("b"),
        "legal_checkpoint": 0,
        "legal_features": "shared market prices, shared market inventory, shop_count only",
        "discovery_seeds": len(discovery),
        "validation_seeds": len(validation),
        "discovery_constant_a": const_a,
        "discovery_constant_b": const_b,
        "discovery_best_constant": best_constant,
        "best_stump_frozen_on_discovery": best,
        "validation_score_one_shot": val_score,
        "validation_choose_a": va,
        "validation_choose_b": vb,
        "validation_constant_a": val_const_a,
        "validation_constant_b": val_const_b,
        "research_gate_pass": research_gate,
        "decision": "BUILD_ACTUAL_SELECTOR_SCREEN" if research_gate else "NO_INITIAL_STUMP_SIGNAL",
        "top10_discovery_stumps": candidates[:10],
        "promotion_warning": "This analysis cannot promote a candidate. An actual selector must be simulated on the exact-reference multi-opponent panel and confirmed on more seeds before hosted use.",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
