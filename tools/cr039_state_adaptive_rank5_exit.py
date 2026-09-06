"""CR039: state-adaptive exit from the path-dependent rank5 lineage.

CR038 showed that global temporal cuts cannot preserve the full CR035 rank5
W/L gain.  This screen therefore keeps the exact CR035 path through clock 24
and asks a narrower question: after entering rank5, can a *public-state* rule
identify when to stay in that lineage versus fall back to CR029?

All discovery/evaluation rows are the already-open CR035/CR036 12-scenario
panel. Fresh validation and held-out rows are untouched. Runtime rules use only
current public game state; never opponent identity, rank, seed, episode id, or
submission identity.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import statistics
from pathlib import Path

from kaggle_environments import make

import cr035_public_regime_selector_shard as core

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr031_elite_round_robin.json"
OUT = ROOT / "artifacts/cr039_state_adaptive_rank5_exit"

HORIZONS = (48, 72, 96, 120, 144, 168, 192, 216)
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
FEATURES = (
    "self_money", "opp_money", "gap_money",
    "self_yield_units", "opp_yield_units", "gap_yield_units",
    "self_kind_pasture", "opp_kind_pasture",
    "self_animal_cow", "opp_animal_cow",
    "self_animal_sheep", "opp_animal_sheep",
    "shop_count",
    "price_wheat", "price_strawberry", "price_melon", "price_milk", "price_wool",
)
MAX_SIMULATED_RULES = 8


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except Exception:
        try:
            return obj[key]
        except Exception:
            return default


def _num(obj, key) -> float:
    try:
        x = float(_get(obj, key, 0) or 0)
        return x if math.isfinite(x) else 0.0
    except Exception:
        return 0.0


def _tile_features(farm, prefix: str) -> dict[str, float]:
    out = {
        f"{prefix}money": _num(farm, "money"),
        f"{prefix}quads": float(len(_get(farm, "unlocked_quadrants", []) or [])),
    }
    counts: dict[str, float] = {}
    total_yield = 0.0
    for row in _get(farm, "tiles", []) or []:
        if not isinstance(row, list):
            continue
        for tile in row:
            if not isinstance(tile, dict):
                continue
            kind = str(tile.get("kind") or "NONE").lower()
            counts[f"kind_{kind}"] = counts.get(f"kind_{kind}", 0.0) + 1.0
            animal = tile.get("animal")
            if animal:
                k = f"animal_{str(animal).lower()}"
                counts[k] = counts.get(k, 0.0) + 1.0
            try:
                total_yield += max(0.0, float(tile.get("yield_units", 0) or 0))
            except Exception:
                pass
    out[f"{prefix}yield_units"] = total_yield
    for k, v in counts.items():
        out[f"{prefix}{k}"] = v
    return out


def _public_features(obs) -> dict[str, float]:
    farms = _get(obs, "farms", []) or []
    player = int(_get(obs, "player", 0) or 0)
    other = 1 - player
    if len(farms) < 2:
        return {k: 0.0 for k in FEATURES}
    f: dict[str, float] = {}
    f.update(_tile_features(farms[player], "self_"))
    f.update(_tile_features(farms[other], "opp_"))
    f["gap_money"] = f.get("self_money", 0.0) - f.get("opp_money", 0.0)
    f["gap_yield_units"] = f.get("self_yield_units", 0.0) - f.get("opp_yield_units", 0.0)
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    for p in PRODUCTS:
        f[f"price_{p.lower()}"] = _num(prices, p)
    town = _get(obs, "town", {}) or {}
    f["shop_count"] = float(len(_get(town, "unlocked_shops", []) or []))
    return {k: float(f.get(k, 0.0)) for k in FEATURES}


def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def _summary(rows: list[dict]) -> dict:
    scores = [float(r["score"]) for r in rows]
    deltas = [float(r["delta"]) for r in rows]
    return {
        "games": len(rows),
        "wins": sum(x == 1.0 for x in scores),
        "losses": sum(x == 0.0 for x in scores),
        "ties": sum(x == 0.5 for x in scores),
        "score_total": sum(scores),
        "score_rate": sum(scores) / len(scores) if scores else None,
        "mean_delta": statistics.mean(deltas) if deltas else None,
        "median_delta": statistics.median(deltas) if deltas else None,
    }


def _paired(candidate: list[dict], control_by_key: dict[tuple[int, int], dict]) -> dict:
    favorable = unfavorable = 0
    gains = []
    for r in candidate:
        b = control_by_key[(int(r["opponent_rank"]), int(r["seat"]))]
        cs, bs = float(r["score"]), float(b["score"])
        favorable += cs > bs
        unfavorable += cs < bs
        gains.append(float(r["delta"]) - float(b["delta"]))
    return {
        "favorable": favorable,
        "unfavorable": unfavorable,
        "net": favorable - unfavorable,
        "mean_paired_delta_gain": statistics.mean(gains) if gains else None,
        "best_paired_delta_gain": max(gains) if gains else None,
        "worst_paired_delta_gain": min(gains) if gains else None,
    }


def _verify_bundle(bundle: dict, cfg: dict) -> tuple[list[dict], list[dict], dict[int, dict]]:
    frozen = bundle.get("classifier") or {}
    if int(frozen.get("switch_clock")) != int(core.SWITCH_CLOCK):
        raise RuntimeError("source bundle switch clock mismatch")
    if float(frozen.get("threshold")) != float(core.SELF_MONEY_THRESHOLD):
        raise RuntimeError("source bundle threshold mismatch")
    recent = cfg["recent_top"]
    base = bundle["recent_top"]["tape"]
    if len(base) != 719 or core._tape_sha(base) != recent["tape_sha256"]:
        raise RuntimeError("CR029 source bundle provenance mismatch")
    scenarios: dict[int, dict] = {}
    for s in cfg["scenarios"]:
        rank = int(s["rank"])
        b = bundle["scenarios"][str(rank)]
        tape = b["tape"]
        if (
            int(b["episode_id"]) != int(s["episode_id"])
            or int(b["seed"]) != int(s["seed"])
            or b["team"] != s["team"]
            or len(tape) != 719
            or core._tape_sha(tape) != s["tape_sha256"]
        ):
            raise RuntimeError(f"scenario rank {rank} provenance mismatch")
        scenarios[rank] = {
            "rank": rank,
            "episode_id": int(s["episode_id"]),
            "seed": int(s["seed"]),
            "team": s["team"],
            "configuration": copy.deepcopy(b.get("configuration") or {}),
            "tape": tape,
        }
    return base, scenarios[5]["tape"], scenarios


def _reference_agent(base: list[dict], alt: list[dict], probes: dict[int, dict]):
    state = {"classified": False, "keiz": False, "money24": None}

    def agent(obs, config=None):
        s = max(0, min(718, core._clock(obs)))
        if not state["classified"] and s >= core.SWITCH_CLOCK:
            money = core._self_money(obs)
            state["classified"] = True
            state["money24"] = money
            state["keiz"] = money > core.SELF_MONEY_THRESHOLD
        if state["keiz"] and s in HORIZONS and s not in probes:
            probes[s] = _public_features(obs)
        tape = alt if state["keiz"] else base
        return copy.deepcopy(tape[s])

    return agent, state


def _rule_agent(base: list[dict], alt: list[dict], rule: dict):
    state = {"classified": False, "keiz": False, "exited": False, "decision_value": None}
    horizon = int(rule["horizon"])
    feature = str(rule["feature"])
    threshold = float(rule["threshold"])
    exit_if_high = bool(rule["exit_if_high"])

    def agent(obs, config=None):
        s = max(0, min(718, core._clock(obs)))
        if not state["classified"] and s >= core.SWITCH_CLOCK:
            state["classified"] = True
            state["keiz"] = core._self_money(obs) > core.SELF_MONEY_THRESHOLD
        if state["keiz"] and not state["exited"] and s >= horizon:
            val = float(_public_features(obs).get(feature, 0.0))
            state["decision_value"] = val
            state["exited"] = (val > threshold) if exit_if_high else (val <= threshold)
        tape = base if (not state["keiz"] or state["exited"]) else alt
        return copy.deepcopy(tape[s])

    return agent, state


def _run_agent(agent_factory, scenarios: dict[int, dict]) -> tuple[list[dict], list[dict]]:
    rows, errors = [], []
    for rank, sc in sorted(scenarios.items()):
        for seat in (0, 1):
            try:
                own, state = agent_factory(rank, seat)
                opp = core._tape_agent(sc["tape"])
                conf = copy.deepcopy(sc["configuration"])
                conf["episodeSteps"] = 720
                conf["seed"] = int(sc["seed"])
                env = make("kaggriculture", configuration=conf, debug=True)
                env.run([own, opp] if seat == 0 else [opp, own])
                rep = env.toJSON()
                if not core._final_ok(rep):
                    raise RuntimeError(f"non-DONE steps={len(rep.get('steps') or [])}")
                rew = core._rewards(rep)
                delta = rew[seat] - rew[1 - seat]
                rows.append({
                    "opponent_rank": rank,
                    "opponent_team": sc["team"],
                    "episode_id": sc["episode_id"],
                    "seed": sc["seed"],
                    "seat": seat,
                    "self_reward": rew[seat],
                    "opp_reward": rew[1 - seat],
                    "delta": delta,
                    "score": core._wl(delta),
                    "state": copy.deepcopy(state),
                })
            except Exception as exc:
                errors.append({"opponent_rank": rank, "seat": seat, "error": repr(exc)})
    return rows, errors


def _candidate_rules(probe_rows: list[dict], control_by_key: dict, full_by_key: dict) -> list[dict]:
    enriched = []
    favorable_keys = set()
    regression_keys = set()
    for r in probe_rows:
        key = (int(r["opponent_rank"]), int(r["seat"]))
        b, f = control_by_key[key], full_by_key[key]
        gain = float(f["delta"]) - float(b["delta"])
        if float(f["score"]) > float(b["score"]):
            favorable_keys.add(key)
        if float(f["score"]) < float(b["score"]):
            regression_keys.add(key)
        enriched.append({**r, "key": key, "paired_gain": gain})

    rules = []
    for horizon in HORIZONS:
        hr = [r for r in enriched if int(r["horizon"]) == horizon and r["opponent_team"] == "keiz"]
        if len(hr) != 16:
            continue
        for feature in FEATURES:
            vals = sorted(set(float(r["features"].get(feature, 0.0)) for r in hr))
            if len(vals) < 2:
                continue
            thresholds = [(a + b) / 2.0 for a, b in zip(vals, vals[1:])]
            for threshold in thresholds:
                for exit_if_high in (False, True):
                    exit_keys = {
                        r["key"] for r in hr
                        if ((float(r["features"].get(feature, 0.0)) > threshold) if exit_if_high
                            else (float(r["features"].get(feature, 0.0)) <= threshold))
                    }
                    fav_preserved = sum(k not in exit_keys for k in favorable_keys)
                    regressions_captured = sum(k in exit_keys for k in regression_keys)
                    neg_mass = sum(-r["paired_gain"] for r in hr if r["key"] in exit_keys and r["paired_gain"] < 0)
                    pos_mass = sum(r["paired_gain"] for r in hr if r["key"] in exit_keys and r["paired_gain"] > 0)
                    rules.append({
                        "horizon": horizon,
                        "feature": feature,
                        "threshold": threshold,
                        "exit_if_high": exit_if_high,
                        "favorable_preserved_proxy": fav_preserved,
                        "favorable_total": len(favorable_keys),
                        "regressions_captured_proxy": regressions_captured,
                        "regression_total": len(regression_keys),
                        "negative_margin_mass_targeted": neg_mass,
                        "positive_margin_mass_sacrificed_proxy": pos_mass,
                        "exit_count_proxy": len(exit_keys),
                        "exit_signature": sorted([f"r{k[0]}s{k[1]}" for k in exit_keys]),
                    })
    rules.sort(key=lambda x: (
        x["favorable_preserved_proxy"] == x["favorable_total"],
        x["regressions_captured_proxy"],
        x["favorable_preserved_proxy"],
        x["negative_margin_mass_targeted"] - 2.0 * x["positive_margin_mass_sacrificed_proxy"],
        -x["positive_margin_mass_sacrificed_proxy"],
        -x["exit_count_proxy"],
        -x["horizon"],
        x["feature"],
    ), reverse=True)

    picked = []
    seen = set()
    for r in rules:
        sig = (r["horizon"], tuple(r["exit_signature"]))
        if sig in seen:
            continue
        seen.add(sig)
        picked.append(r)
        if len(picked) >= MAX_SIMULATED_RULES:
            break
    return picked


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--full-rank5", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    bundle = json.loads(_resolve(args.source_bundle).read_text(encoding="utf-8"))
    control = json.loads(_resolve(args.control).read_text(encoding="utf-8"))
    full = json.loads(_resolve(args.full_rank5).read_text(encoding="utf-8"))
    base, alt, scenarios = _verify_bundle(bundle, cfg)

    control_by_key = {(int(r["opponent_rank"]), int(r["seat"])): r for r in control["rows"]}
    full_by_key = {(int(r["opponent_rank"]), int(r["seat"])): r for r in full["rows"]}
    if len(control_by_key) != 24 or len(full_by_key) != 24:
        raise RuntimeError("frozen CR036 row count mismatch")

    probes_by_key: dict[tuple[int, int], dict[int, dict]] = {}
    def ref_factory(rank, seat):
        probes: dict[int, dict] = {}
        probes_by_key[(rank, seat)] = probes
        return _reference_agent(base, alt, probes)

    ref_rows, errors = _run_agent(ref_factory, scenarios)
    ref_by_key = {(int(r["opponent_rank"]), int(r["seat"])): r for r in ref_rows}
    for key, frozen in full_by_key.items():
        live = ref_by_key.get(key)
        if live is None or float(live["delta"]) != float(frozen["delta"]) or float(live["score"]) != float(frozen["score"]):
            errors.append({"key": list(key), "error": "instrumented full-rank5 parity mismatch"})
    if errors:
        raise RuntimeError(json.dumps(errors[:5]))

    probe_rows = []
    for (rank, seat), probes in sorted(probes_by_key.items()):
        sc = scenarios[rank]
        if sc["team"] != "keiz":
            continue
        for h in HORIZONS:
            if h not in probes:
                raise RuntimeError(f"missing probe rank={rank} seat={seat} horizon={h}")
            probe_rows.append({
                "opponent_rank": rank,
                "opponent_team": sc["team"],
                "seat": seat,
                "horizon": h,
                "features": probes[h],
            })

    rules = _candidate_rules(probe_rows, control_by_key, full_by_key)
    candidate_reports = []
    all_errors = []
    for idx, rule in enumerate(rules):
        def fac(rank, seat, rule=rule):
            return _rule_agent(base, alt, rule)
        rows, errs = _run_agent(fac, scenarios)
        all_errors.extend([{"rule_id": idx, **e} for e in errs])
        paired = _paired(rows, control_by_key) if len(rows) == 24 and not errs else {}
        summary = _summary(rows)
        score_gain = float(summary.get("score_total") or 0.0) - float(control["all"]["score_total"])
        mean_gain = paired.get("mean_paired_delta_gain")
        full_mean = float(full.get("all", {}).get("mean_delta", 0.0)) - float(control.get("all", {}).get("mean_delta", 0.0))
        screen_pass = (
            not errs and len(rows) == 24
            and score_gain >= 3.0
            and int(paired.get("favorable", -1)) >= 4
            and int(paired.get("unfavorable", 99)) <= 1
            and mean_gain is not None
            and float(mean_gain) > float(full_mean) + 2000.0
        ) or (
            not errs and len(rows) == 24
            and score_gain >= 4.0
            and int(paired.get("unfavorable", 99)) <= 1
            and mean_gain is not None
            and float(mean_gain) > float(full_mean)
        )
        candidate_reports.append({
            "rule_id": idx,
            "rule": rule,
            "mechanical_complete": not errs and len(rows) == 24,
            "summary": summary,
            "paired_vs_cr029": paired,
            "score_gain_vs_cr029": score_gain,
            "margin_improvement_vs_full_rank5": None if mean_gain is None else float(mean_gain) - float(full_mean),
            "screen_pass": bool(screen_pass),
            "rows": rows,
        })

    candidate_reports.sort(key=lambda r: (
        r["screen_pass"],
        r["score_gain_vs_cr029"],
        r.get("paired_vs_cr029", {}).get("net", -999),
        r.get("paired_vs_cr029", {}).get("mean_paired_delta_gain", -1e99),
    ), reverse=True)
    promoted = [r for r in candidate_reports if r["screen_pass"]]
    best = candidate_reports[0] if candidate_reports else None
    decision = (
        "CR039_PROMOTE_BEST_RULE_TO_FRESH_VALIDATION" if promoted
        else "CR039_NO_STATE_EXIT_PROMOTION__EVOLVE_RANK5_LINEAGE_DIRECTLY"
    )

    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "experiment": "CR039_STATE_ADAPTIVE_RANK5_EXIT_V1",
        "decision": decision,
        "reference_parity_pass": True,
        "control": control["all"],
        "full_rank5_reference": {"summary": full["all"], "paired_vs_cr029": _paired(full["rows"], control_by_key)},
        "horizons": list(HORIZONS),
        "features": list(FEATURES),
        "proxy_rule_count_simulated": len(rules),
        "candidate_reports": candidate_reports,
        "promoted_rule_ids": [r["rule_id"] for r in promoted],
        "best": best,
        "errors": all_errors,
        "source_scenarios_already_open": True,
        "fresh_validation_touched": False,
        "held_out_touched": False,
        "runtime_identity_features": False,
    }
    summary = {
        "experiment": report["experiment"],
        "decision": decision,
        "reference_parity_pass": True,
        "errors": len(all_errors),
        "rules_simulated": len(rules),
        "promoted_rule_ids": report["promoted_rule_ids"],
        "best": None if best is None else {k: v for k, v in best.items() if k != "rows"},
        "full_rank5_reference": report["full_rank5_reference"],
        "fresh_validation_touched": False,
        "held_out_touched": False,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if all_errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
