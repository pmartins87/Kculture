"""CR038: coherent temporal localization of the CR029 -> rank5 advantage.

CR036 showed that farmer/hands/market cannot be grafted independently. CR037
showed that a late public-state switch at clock 432 is too late: the alternate
advantage is path dependent. This screen therefore keeps all three action
channels coherent and varies only *when* the frozen rank5 tape is active.

No fresh-validation or held-out scenarios are touched. The classifier, CR029
base tape, rank5 alternate tape, scenario panel, and source artifacts are all
frozen from CR035/CR036.
"""
from __future__ import annotations

import argparse
import copy
import json
import statistics
from pathlib import Path

from kaggle_environments import make

import cr035_public_regime_selector_shard as core

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr031_elite_round_robin.json"
SPEC = ROOT / "configs/cr038_coherent_temporal_localization.json"
OUT = ROOT / "artifacts/cr038_coherent_temporal_localization"
COMPONENTS = ("farmer", "hands", "market")


def _resolve(x: str) -> Path:
    p = Path(x)
    return p if p.is_absolute() else ROOT / p


def _copy_components(base_action: dict, alt_action: dict) -> dict:
    action = copy.deepcopy(base_action)
    for comp in COMPONENTS:
        if comp == "farmer":
            if "farmer" in alt_action:
                action["farmer"] = copy.deepcopy(alt_action.get("farmer"))
            else:
                action.pop("farmer", None)
        else:
            action[comp] = copy.deepcopy(alt_action.get(comp) or [])
    return action


def _temporal_agent(base: list[dict], alt: list[dict], family: str, cut: int):
    state = {"classified": False, "predicted_team": None, "self_money_at_24": None, "alt_steps": 0}

    def agent(obs, config=None):
        s = max(0, min(718, core._clock(obs)))
        if not state["classified"] and s >= core.SWITCH_CLOCK:
            money = core._self_money(obs)
            state["classified"] = True
            state["self_money_at_24"] = money
            state["predicted_team"] = "keiz" if money > core.SELF_MONEY_THRESHOLD else "Jesse Bullard"
        action = copy.deepcopy(base[s])
        if state["classified"] and state["predicted_team"] == "keiz":
            use_alt = (family == "prefix" and s < cut) or (family == "suffix" and s >= cut)
            if use_alt:
                action = _copy_components(action, alt[s])
                state["alt_steps"] += 1
        return action

    return agent, state


def _verify_bundle(bundle: dict, cfg: dict, spec: dict):
    frozen = bundle.get("classifier") or {}
    classifier = spec["classifier"]
    if int(frozen.get("switch_clock")) != int(classifier["switch_clock"]):
        raise RuntimeError("bundle/spec switch clock mismatch")
    if float(frozen.get("threshold")) != float(classifier["threshold"]):
        raise RuntimeError("bundle/spec classifier threshold mismatch")
    recent = cfg["recent_top"]
    br = bundle["recent_top"]
    base = br["tape"]
    if len(base) != 719 or core._tape_sha(base) != recent["tape_sha256"]:
        raise RuntimeError("CR029 bundle provenance mismatch")
    scenarios = {}
    for s in cfg["scenarios"]:
        rank = int(s["rank"])
        b = bundle["scenarios"][str(rank)]
        tape = b["tape"]
        if (int(b["episode_id"]) != int(s["episode_id"]) or int(b["seed"]) != int(s["seed"])
                or b["team"] != s["team"] or len(tape) != 719 or core._tape_sha(tape) != s["tape_sha256"]):
            raise RuntimeError(f"scenario r{rank} provenance mismatch")
        scenarios[rank] = {"rank": rank, "team": s["team"], "episode_id": int(s["episode_id"]),
                           "seed": int(s["seed"]), "configuration": b.get("configuration") or {}, "tape": tape}
    alt_rank = int(spec["alternate_rank"])
    return base, scenarios[alt_rank]["tape"], scenarios


def _load_cr036(path: str, expected_variant: str) -> dict:
    doc = json.loads(_resolve(path).read_text(encoding="utf-8"))
    if doc.get("experiment") != "CR036_RANK5_COMPONENT_GRAFT_V1" or doc.get("variant_name") != expected_variant:
        raise RuntimeError(f"wrong CR036 artifact: expected {expected_variant}")
    if not doc.get("mechanical_complete") or len(doc.get("rows") or []) != 24:
        raise RuntimeError("incomplete CR036 artifact")
    return doc


def _row_index(rows: list[dict]) -> dict:
    out = {}
    for r in rows:
        key = (int(r["opponent_rank"]), int(r["seat"]))
        if key in out:
            raise RuntimeError(f"duplicate row {key}")
        out[key] = r
    return out


def _paired(candidate_rows: list[dict], baseline_idx: dict) -> dict:
    favorable = unfavorable = 0
    gains = []
    for r in candidate_rows:
        key = (int(r["opponent_rank"]), int(r["seat"]))
        b = baseline_idx[key]
        bs = float(b["score"]); cs = float(r["score"])
        if cs > bs:
            favorable += 1
        elif cs < bs:
            unfavorable += 1
        gains.append(float(r["delta"]) - float(b["delta"]))
    return {
        "favorable": favorable,
        "unfavorable": unfavorable,
        "net": favorable - unfavorable,
        "mean_paired_delta_gain": statistics.mean(gains) if gains else 0.0,
        "worst_paired_delta_gain": min(gains) if gains else 0.0,
        "best_paired_delta_gain": max(gains) if gains else 0.0,
    }


def _run_one(base, alt, scenarios, family: str, cut: int, keys):
    rows, errors = [], []
    for rank, seat in keys:
        sc = scenarios[rank]
        try:
            own, state = _temporal_agent(base, alt, family, cut)
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
            sr = rew[seat]; orun = rew[1-seat]; delta = sr - orun
            rows.append({
                "family": family, "cut": cut, "opponent_rank": rank, "opponent_team": sc["team"],
                "episode_id": sc["episode_id"], "seed": sc["seed"], "seat": seat,
                "self_reward": sr, "opp_reward": orun, "delta": delta, "score": core._wl(delta),
                "predicted_team": state["predicted_team"], "self_money_at_24": state["self_money_at_24"],
                "alt_steps": int(state["alt_steps"]),
            })
        except Exception as exc:
            errors.append({"family": family, "cut": cut, "opponent_rank": rank, "seat": seat, "error": repr(exc)})
    return rows, errors


def _phase1_sort_key(x: dict):
    p = x["paired"]
    return (p["net"], p["favorable"], -p["unfavorable"], p["mean_paired_delta_gain"],
            x["family"] == "prefix", -x["cut"])


def _final_sort_key(x: dict):
    p = x["paired"]
    return (x["score_gain_vs_cr029"], p["net"], -p["unfavorable"],
            p["mean_paired_delta_gain"], p["worst_paired_delta_gain"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--cr036-control", required=True)
    ap.add_argument("--cr036-full", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    bundle = json.loads(_resolve(args.source_bundle).read_text(encoding="utf-8"))
    control = _load_cr036(args.cr036_control, "control_cr029")
    full = _load_cr036(args.cr036_full, "full_rank5_reference")
    base, alt, scenarios = _verify_bundle(bundle, cfg, spec)

    baseline_idx = _row_index(control["rows"])
    full_idx = _row_index(full["rows"])
    all_keys = sorted(baseline_idx)
    if all_keys != sorted(full_idx) or len(all_keys) != 24:
        raise RuntimeError("CR036 row domains differ")
    sensitive_keys = [k for k in all_keys if float(baseline_idx[k]["score"]) != float(full_idx[k]["score"])]
    expected = [(1, 1), (5, 0), (5, 1), (12, 0), (12, 1)]
    if sensitive_keys != expected:
        raise RuntimeError(f"unexpected CR036 conversion set: {sensitive_keys}")
    full_paired = _paired(full["rows"], baseline_idx)
    if (full_paired["favorable"], full_paired["unfavorable"], full_paired["net"]) != (4, 1, 3):
        raise RuntimeError(f"CR036 full reference drift: {full_paired}")

    candidates = [{"family": family, "cut": int(cut)} for family in ("prefix", "suffix") for cut in spec["cutpoints"]]
    phase1, all_errors, cache = [], [], {}
    for c in candidates:
        rows, errors = _run_one(base, alt, scenarios, c["family"], c["cut"], sensitive_keys)
        all_errors.extend(errors)
        idx = _row_index(rows)
        cache[(c["family"], c["cut"])] = idx
        p = _paired(rows, baseline_idx) if len(rows) == len(sensitive_keys) else {}
        phase1.append({**c, "mechanical_complete": not errors and len(rows) == len(sensitive_keys), "paired": p, "rows": rows})

    mechanically_ok = [x for x in phase1 if x["mechanical_complete"]]
    shortlist = sorted(mechanically_ok, key=_phase1_sort_key, reverse=True)[:int(spec["phase1_shortlist"])]
    remaining_keys = [k for k in all_keys if k not in sensitive_keys]
    finalists = []
    for c in shortlist:
        more, errors = _run_one(base, alt, scenarios, c["family"], c["cut"], remaining_keys)
        all_errors.extend(errors)
        idx = dict(cache[(c["family"], c["cut"])])
        idx.update(_row_index(more))
        rows = [idx[k] for k in all_keys if k in idx]
        p = _paired(rows, baseline_idx) if len(rows) == 24 else {}
        score_total = sum(float(r["score"]) for r in rows)
        score_gain = score_total - float(control["all"]["score_total"])
        margin_better_than_full = bool(p) and p["mean_paired_delta_gain"] > full_paired["mean_paired_delta_gain"]
        gate = spec["promotion_gate"]
        screen_pass = bool(p) and len(rows) == 24 and not errors and (
            p["unfavorable"] <= int(gate["unfavorable_max"])
            and p["net"] >= int(gate["net_min"])
            and (score_gain >= float(gate["score_gain_strong_min"])
                 or (score_gain >= float(gate["score_gain_min"]) and margin_better_than_full))
        )
        finalists.append({
            "family": c["family"], "cut": c["cut"], "mechanical_complete": not errors and len(rows) == 24,
            "score_total": score_total, "score_gain_vs_cr029": score_gain, "summary": core._summary(rows),
            "paired": p, "margin_better_than_full_rank5": margin_better_than_full,
            "screen_pass": screen_pass, "rows": rows,
        })

    ranked = sorted(finalists, key=_final_sort_key, reverse=True)
    promoted = [x for x in ranked if x["screen_pass"]]
    if all_errors:
        decision = "CR038_MECHANICAL_FAIL__REPAIR_ONLY"
    elif promoted:
        decision = "CR038_TEMPORAL_CANDIDATE_FOUND__FRESH_VALIDATE"
    else:
        decision = "CR038_NO_TEMPORAL_CUT_PROMOTION__TREAT_RANK5_AS_PATH_DEPENDENT_LINEAGE"

    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "experiment": "CR038_COHERENT_TEMPORAL_LOCALIZATION_V1", "decision": decision,
        "sensitive_rows_from_frozen_cr036": [
            {"opponent_rank": k[0], "seat": k[1], "cr029_score": baseline_idx[k]["score"],
             "cr029_delta": baseline_idx[k]["delta"], "full_rank5_score": full_idx[k]["score"],
             "full_rank5_delta": full_idx[k]["delta"]} for k in sensitive_keys
        ],
        "cr029_control": control["all"], "full_rank5_reference": {"summary": full["all"], "paired": full_paired},
        "phase1_candidate_count": len(candidates), "phase1_shortlist_count": len(shortlist),
        "phase1_ranking": [{k:v for k,v in x.items() if k != "rows"}
                           for x in sorted(mechanically_ok, key=_phase1_sort_key, reverse=True)],
        "final_ranking": [{k:v for k,v in x.items() if k != "rows"} for x in ranked],
        "promoted": [{k:v for k,v in x.items() if k != "rows"} for x in promoted],
        "errors": all_errors, "source_scenarios_already_open": True, "fresh_validation_touched": False,
        "held_out_touched": False, "runtime_identity_features": False, "all_three_action_channels_coherent": True,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    summary = {
        "experiment": report["experiment"], "decision": decision,
        "full_rank5_reference": report["full_rank5_reference"],
        "best": ({k:v for k,v in ranked[0].items() if k != "rows"} if ranked else None),
        "promoted": report["promoted"], "errors": len(all_errors),
        "fresh_validation_touched": False, "held_out_touched": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if all_errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
