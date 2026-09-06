"""CR037: public-state hard-keiz fingerprint + coherent rank5 routing screen.

All discovery and screening use only the already-open CR035 source bundle.
Diagnostic labels (rank/team) are never available to the runtime router.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG31 = ROOT / "configs/cr031_elite_round_robin.json"
SPEC = ROOT / "configs/cr037_hard_keiz_public_router.json"
OUT = ROOT / "artifacts/cr037_hard_keiz_public_router"


def _get(obj: Any, key: Any, default=None):
    try:
        return obj.get(key, default)
    except Exception:
        try:
            return obj[key]
        except Exception:
            return default


def _clock(obs: Any) -> int:
    raw = _get(obs, "step", None)
    if raw is not None:
        try:
            return max(0, int(raw))
        except Exception:
            pass
    try:
        return max(0, int(_get(obs, "day", 0) or 0)) * 24 + max(0, int(_get(obs, "hour", 0) or 0))
    except Exception:
        return 0


def _canon(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def _tape_sha(tape: list[dict]) -> str:
    return hashlib.sha256(_canon(tape).encode("utf-8")).hexdigest()


def _final_ok(rep: dict) -> bool:
    steps = rep.get("steps") or []
    return len(steps) == 720 and [steps[-1][i].get("status") for i in (0, 1)] == ["DONE", "DONE"]


def _rewards(rep: dict) -> list[float]:
    steps = rep.get("steps") or []
    return [float(steps[-1][i].get("reward")) for i in (0, 1)]


def _wl(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def _self_money(obs: Any) -> float:
    try:
        farms = _get(obs, "farms", []) or []
        player = int(_get(obs, "player", 0) or 0)
        v = float(_get(farms[player], "money", 0) or 0)
        return v if math.isfinite(v) else 0.0
    except Exception:
        return 0.0


def _tape_agent(tape: list[dict]):
    def agent(obs, config=None):
        s = max(0, min(len(tape) - 1, _clock(obs)))
        return copy.deepcopy(tape[s])
    return agent


def _flatten_numeric(obj: Any, prefix: str, out: dict[str, float], depth: int = 0) -> None:
    if depth > 8:
        return
    if isinstance(obj, bool):
        out[prefix] = float(obj)
        return
    if isinstance(obj, (int, float)):
        v = float(obj)
        if math.isfinite(v):
            out[prefix] = v
        return
    if isinstance(obj, dict):
        out[f"{prefix}.__len__"] = float(len(obj))
        for k in sorted(obj, key=lambda x: str(x)):
            ks = str(k)
            if ks.lower() in {"seed", "episode_id", "submission_id", "team", "rank", "winner_seat"}:
                continue
            _flatten_numeric(obj[k], f"{prefix}.{ks}", out, depth + 1)
        return
    if isinstance(obj, (list, tuple)):
        out[f"{prefix}.__len__"] = float(len(obj))
        for i, v in enumerate(obj[:64]):
            _flatten_numeric(v, f"{prefix}[{i}]", out, depth + 1)


def _public_features(obs: Any) -> dict[str, float]:
    farms = _get(obs, "farms", []) or []
    player = int(_get(obs, "player", 0) or 0)
    self_farm = farms[player] if len(farms) > player else {}
    opp_i = 1 - player
    opp_farm = farms[opp_i] if len(farms) > opp_i else {}
    sm = float(_get(self_farm, "money", 0) or 0)
    om = float(_get(opp_farm, "money", 0) or 0)
    out: dict[str, float] = {
        "self_money": sm,
        "opp_money": om,
        "lead": sm - om,
    }
    _flatten_numeric(self_farm, "self_farm", out)
    _flatten_numeric(opp_farm, "opp_farm", out)
    _flatten_numeric(_get(obs, "market", {}) or {}, "market", out)
    return out


def _probe_agent(base: list[dict], horizons: set[int]):
    state: dict[str, Any] = {"captures": {}}

    def agent(obs, config=None):
        s = max(0, min(len(base) - 1, _clock(obs)))
        if s in horizons and str(s) not in state["captures"]:
            state["captures"][str(s)] = _public_features(obs)
        return copy.deepcopy(base[s])

    return agent, state


def _rule_pred(v: float, threshold: float, direction: str) -> bool:
    return v <= threshold if direction == "le" else v > threshold


def _thresholds(values: list[float]) -> list[float]:
    xs = sorted(set(values))
    return [(a + b) / 2.0 for a, b in zip(xs, xs[1:]) if a != b]


def _eval_rule(rows: list[dict], feature: str, threshold: float, direction: str) -> dict:
    preds = []
    tp = fp = tn = fn = 0
    for r in rows:
        pred = _rule_pred(float(r["features"][feature]), threshold, direction)
        truth = bool(r["hard"])
        preds.append((r, pred, truth))
        if pred and truth:
            tp += 1
        elif pred and not truth:
            fp += 1
        elif not pred and truth:
            fn += 1
        else:
            tn += 1
    by_rank: dict[int, list[bool]] = {}
    for r, pred, truth in preds:
        by_rank.setdefault(int(r["rank"]), []).append(pred == truth)
    scenario_correct = sum(all(v) for v in by_rank.values())
    seat_correct = tp + tn
    vals = [float(r["features"][feature]) for r in rows]
    scale = max(vals) - min(vals)
    min_margin = min(abs(v - threshold) for v in vals) if vals else 0.0
    norm_margin = min_margin / scale if scale > 0 else 0.0
    return {
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "seat_correct": seat_correct,
        "scenario_correct": scenario_correct,
        "min_margin": min_margin,
        "normalized_margin": norm_margin,
    }


def _feature_simplicity(name: str) -> int:
    if name in {"self_money", "opp_money", "lead"}:
        return 0
    if name.startswith("self_farm.money") or name.startswith("opp_farm.money"):
        return 1
    if name.startswith("self_farm") or name.startswith("opp_farm"):
        return 2
    return 3


def _fit_threshold(train: list[dict], feature: str, direction: str) -> float | None:
    vals = [float(r["features"][feature]) for r in train]
    best = None
    for t in _thresholds(vals):
        m = _eval_rule(train, feature, t, direction)
        key = (m["scenario_correct"], m["seat_correct"], m["tp"], -m["fp"], m["normalized_margin"])
        if best is None or key > best[0]:
            best = (key, t)
    return None if best is None else float(best[1])


def _loso(rows: list[dict], feature: str, direction: str) -> dict:
    ranks = sorted({int(r["rank"]) for r in rows})
    correct = 0
    fold_rows = []
    thresholds = []
    for hold in ranks:
        train = [r for r in rows if int(r["rank"]) != hold]
        test = [r for r in rows if int(r["rank"]) == hold]
        t = _fit_threshold(train, feature, direction)
        if t is None:
            fold_rows.append({"holdout_rank": hold, "correct": False, "threshold": None})
            continue
        thresholds.append(t)
        ok = all(_rule_pred(float(r["features"][feature]), t, direction) == bool(r["hard"]) for r in test)
        correct += int(ok)
        fold_rows.append({"holdout_rank": hold, "correct": bool(ok), "threshold": t})
    return {"correct": correct, "folds": fold_rows, "thresholds": thresholds}


def _discover(probes: list[dict], horizons: list[int]) -> tuple[list[dict], dict | None]:
    candidates: list[dict] = []
    keiz = [r for r in probes if r["team"] == "keiz"]
    for h in horizons:
        rows = [r for r in keiz if int(r["horizon"]) == h]
        if len(rows) != 16:
            continue
        common = set(rows[0]["features"])
        for r in rows[1:]:
            common &= set(r["features"])
        for feature in sorted(common):
            vals = [float(r["features"][feature]) for r in rows]
            if len(set(vals)) < 2:
                continue
            for direction in ("le", "gt"):
                for t in _thresholds(vals):
                    m = _eval_rule(rows, feature, t, direction)
                    if m["fn"]:
                        continue
                    c = {
                        "horizon": h, "feature": feature, "direction": direction,
                        "threshold": t, **m,
                        "feature_simplicity": _feature_simplicity(feature),
                    }
                    candidates.append(c)
    candidates.sort(key=lambda c: (
        c["scenario_correct"], c["seat_correct"], c["tp"], -c["fp"],
        c["normalized_margin"], -c["feature_simplicity"], -c["horizon"], c["feature"], c["direction"]
    ), reverse=True)
    for c in candidates[:200]:
        rows = [r for r in keiz if int(r["horizon"]) == int(c["horizon"])]
        cv = _loso(rows, c["feature"], c["direction"])
        c["loso_correct"] = cv["correct"]
        c["loso_folds"] = cv["folds"]
    for c in candidates[200:]:
        c["loso_correct"] = -1
        c["loso_folds"] = []
    candidates.sort(key=lambda c: (
        c["loso_correct"], c["scenario_correct"], c["seat_correct"], c["tp"], -c["fp"],
        c["normalized_margin"], -c["feature_simplicity"], -c["horizon"], c["feature"], c["direction"]
    ), reverse=True)
    return candidates, (candidates[0] if candidates else None)


def _router_agent(base: list[dict], alternate: list[dict], first: dict, rule: dict):
    state = {
        "stage1_decided": False, "stage1_keiz": False, "hard_decided": False,
        "hard_keiz": False, "switched": False, "feature_value": None,
    }

    def agent(obs, config=None):
        s = max(0, min(len(base) - 1, _clock(obs)))
        if not state["stage1_decided"] and s >= int(first["clock"]):
            state["stage1_decided"] = True
            state["stage1_keiz"] = _self_money(obs) > float(first["threshold"])
        if state["stage1_keiz"] and not state["hard_decided"] and s >= int(rule["horizon"]):
            feats = _public_features(obs)
            v = feats.get(rule["feature"])
            state["hard_decided"] = True
            if v is not None and math.isfinite(float(v)):
                state["feature_value"] = float(v)
                state["hard_keiz"] = _rule_pred(float(v), float(rule["threshold"]), rule["direction"])
                state["switched"] = bool(state["hard_keiz"])
        tape = alternate if state["switched"] else base
        return copy.deepcopy(tape[s])

    return agent, state


def _run_match(own_agent, opp_tape: list[dict], configuration: dict, seed: int, seat: int) -> tuple[dict, list[float]]:
    conf = copy.deepcopy(configuration)
    conf["episodeSteps"] = 720
    conf["seed"] = int(seed)
    opp = _tape_agent(opp_tape)
    env = make("kaggriculture", configuration=conf, debug=True)
    env.run([own_agent, opp] if seat == 0 else [opp, own_agent])
    rep = env.toJSON()
    if not _final_ok(rep):
        raise RuntimeError(f"non-DONE steps={len(rep.get('steps') or [])}")
    return rep, _rewards(rep)


def _summary(rows: list[dict], prefix: str) -> dict:
    scores = [float(r[prefix + "_score"]) for r in rows]
    deltas = [float(r[prefix + "_delta"]) for r in rows]
    return {
        "games": len(rows), "wins": sum(x == 1 for x in scores),
        "losses": sum(x == 0 for x in scores), "ties": sum(x == 0.5 for x in scores),
        "score_total": sum(scores), "score_rate": sum(scores) / len(scores) if scores else None,
        "mean_delta": statistics.mean(deltas) if deltas else None,
        "median_delta": statistics.median(deltas) if deltas else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG31.read_text(encoding="utf-8"))
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    bundle_path = Path(args.source_bundle)
    if not bundle_path.is_absolute():
        bundle_path = ROOT / bundle_path
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    errors: list[dict] = []
    base = bundle["recent_top"]["tape"]
    recent = cfg["recent_top"]
    if len(base) != 719 or _tape_sha(base) != recent["tape_sha256"]:
        raise RuntimeError("CR029 source-bundle provenance mismatch")
    if bundle.get("classifier") != {"feature": "self_money", "switch_clock": 24, "threshold": 35.5}:
        raise RuntimeError("CR035 frozen classifier mismatch")

    scenarios: dict[int, dict] = {}
    for s in cfg["scenarios"]:
        rank = int(s["rank"])
        b = bundle["scenarios"][str(rank)]
        tape = b["tape"]
        if len(tape) != 719 or _tape_sha(tape) != s["tape_sha256"]:
            raise RuntimeError(f"scenario r{rank} tape provenance mismatch")
        if int(b["seed"]) != int(s["seed"]) or b["team"] != s["team"]:
            raise RuntimeError(f"scenario r{rank} metadata provenance mismatch")
        scenarios[rank] = b
    alternate = scenarios[int(spec["alternate_complete_tape_rank"])]["tape"]

    horizons = [int(x) for x in spec["probe_horizons"]]
    horizon_set = set(horizons)
    hard_ranks = {int(x) for x in spec["hard_keiz_diagnostic_ranks"]}
    probes: list[dict] = []
    stage1_correct = 0
    stage1_total = 0

    for rank, sc in sorted(scenarios.items()):
        for seat in (0, 1):
            try:
                probe, state = _probe_agent(base, horizon_set)
                rep, rewards = _run_match(probe, sc["tape"], sc.get("configuration") or {}, int(sc["seed"]), seat)
                captures = state["captures"]
                if any(str(h) not in captures for h in horizons):
                    raise RuntimeError(f"missing probe horizons r{rank} seat{seat}")
                p24 = captures[str(int(spec["first_stage"]["clock"]))]
                pred_keiz = float(p24["self_money"]) > float(spec["first_stage"]["threshold"])
                truth_keiz = sc["team"] == "keiz"
                stage1_total += 1
                stage1_correct += int(pred_keiz == truth_keiz)
                for h in horizons:
                    probes.append({
                        "rank": rank, "team": sc["team"], "seat": seat, "horizon": h,
                        "hard": rank in hard_ranks, "features": captures[str(h)],
                    })
            except Exception as exc:
                errors.append({"phase": "probe", "rank": rank, "seat": seat, "error": repr(exc)})

    candidates, selected = _discover(probes, horizons) if not errors else ([], None)
    fg = spec["fingerprint_gate"]
    fingerprint_pass = bool(selected) and (
        int(selected["tp"]) >= int(fg["hard_seat_recall_min"]) and
        int(selected["fp"]) <= int(fg["easy_seat_false_positives_max"]) and
        int(selected["loso_correct"]) >= int(fg["leave_one_scenario_out_correct_min"]) and
        stage1_correct == stage1_total == 24
    )

    screen_rows: list[dict] = []
    if fingerprint_pass and selected is not None:
        for rank, sc in sorted(scenarios.items()):
            for seat in (0, 1):
                try:
                    control = _tape_agent(base)
                    crep, cr = _run_match(control, sc["tape"], sc.get("configuration") or {}, int(sc["seed"]), seat)
                    cd = cr[seat] - cr[1 - seat]
                    cscore = _wl(cd)
                    router, rstate = _router_agent(base, alternate, spec["first_stage"], selected)
                    rrep, rr = _run_match(router, sc["tape"], sc.get("configuration") or {}, int(sc["seed"]), seat)
                    rd = rr[seat] - rr[1 - seat]
                    rscore = _wl(rd)
                    screen_rows.append({
                        "rank": rank, "team": sc["team"], "seat": seat,
                        "control_delta": cd, "control_score": cscore,
                        "router_delta": rd, "router_score": rscore,
                        "paired_delta_gain": rd - cd, "score_gain": rscore - cscore,
                        "stage1_keiz": bool(rstate["stage1_keiz"]),
                        "hard_keiz": bool(rstate["hard_keiz"]), "switched": bool(rstate["switched"]),
                        "feature_value": rstate["feature_value"],
                    })
                except Exception as exc:
                    errors.append({"phase": "screen", "rank": rank, "seat": seat, "error": repr(exc)})

    screen_complete = fingerprint_pass and not errors and len(screen_rows) == 24
    favorable = sum(float(r["score_gain"]) > 0 for r in screen_rows)
    unfavorable = sum(float(r["score_gain"]) < 0 for r in screen_rows)
    score_gain = sum(float(r["score_gain"]) for r in screen_rows)
    paired = [float(r["paired_delta_gain"]) for r in screen_rows]
    mean_paired = statistics.mean(paired) if paired else None
    worst_paired = min(paired) if paired else None
    rg = spec["route_screen_gate"]
    route_pass = bool(screen_complete) and (
        score_gain >= float(rg["paired_score_gain_vs_cr029_min"]) and
        favorable - unfavorable >= int(rg["net_favorable_conversions_min"]) and
        unfavorable <= int(rg["unfavorable_conversions_max"]) and
        mean_paired is not None and mean_paired >= float(rg["paired_mean_delta_gain_min"])
    )

    if errors:
        decision = "CR037_MECHANICAL_FAIL__FIX_ONLY_MECHANICS"
    elif not fingerprint_pass:
        decision = "CR037_NO_ROBUST_HARD_KEIZ_FINGERPRINT__MOVE_TO_COHERENT_TEMPORAL_SPLICE"
    elif route_pass:
        decision = "CR037_PROMOTE_ROUTER_TO_FRESH_VALIDATION"
    else:
        decision = "CR037_FINGERPRINT_FOUND_BUT_ROUTE_SCREEN_FAIL__DO_NOT_PROMOTE"

    report = {
        "experiment": "CR037_HARD_KEIZ_PUBLIC_ROUTER_V1",
        "decision": decision,
        "mechanical_complete": not errors and stage1_total == 24,
        "errors": errors,
        "stage1": {"correct": stage1_correct, "total": stage1_total, "pass": stage1_correct == stage1_total == 24},
        "fingerprint_pass": fingerprint_pass,
        "selected_rule": selected,
        "top_candidates": candidates[:25],
        "probe_rows": probes,
        "route_screen": {
            "complete": screen_complete,
            "control": _summary(screen_rows, "control") if screen_rows else None,
            "router": _summary(screen_rows, "router") if screen_rows else None,
            "score_gain_vs_cr029": score_gain,
            "favorable_conversions": favorable,
            "unfavorable_conversions": unfavorable,
            "net_favorable_conversions": favorable - unfavorable,
            "mean_paired_delta_gain": mean_paired,
            "worst_paired_delta_gain": worst_paired,
            "switched_games": sum(bool(r["switched"]) for r in screen_rows),
            "rows": screen_rows,
            "pass": route_pass,
        },
        "source_scenarios_already_open": True,
        "fresh_validation_touched": False,
        "held_out_touched": False,
        "runtime_identity_features": False,
    }
    summary = {k: v for k, v in report.items() if k not in {"probe_rows", "top_candidates"}}
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
