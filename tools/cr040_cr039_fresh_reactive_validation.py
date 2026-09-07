"""CR040: fresh reactive validation of the CR039 state-adaptive selector.

Uses fresh preregistered seeds, both seats, and the same exact pinned reactive
opponents used in CR027. Compares CR029, the full rank5 selector, and the frozen
CR039 rule. No held-out rows and no runtime identity features.
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
import cr039_state_adaptive_rank5_exit as cr039

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr040_cr039_fresh_reactive_validation.json"
CR031 = ROOT / "configs/cr031_elite_round_robin.json"


def _load(path: str) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def _seed_values(obj) -> set[int]:
    out: set[int] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "seed" in str(k).lower():
                vals = v if isinstance(v, list) else [v]
                for x in vals:
                    try:
                        out.add(int(x))
                    except Exception:
                        pass
            out |= _seed_values(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= _seed_values(v)
    return out


def _seed_firewall(seeds: list[int]) -> list[int]:
    used: set[int] = set()
    for p in sorted((ROOT / "configs").glob("*.json")):
        if p.resolve() == CFG.resolve():
            continue
        try:
            used |= _seed_values(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return sorted(set(seeds) & used)


def _verify_bundle(bundle: dict) -> tuple[list[dict], list[dict]]:
    cfg31 = json.loads(CR031.read_text(encoding="utf-8"))
    recent = cfg31["recent_top"]
    base = bundle["recent_top"]["tape"]
    if len(base) != 719 or core._tape_sha(base) != recent["tape_sha256"]:
        raise RuntimeError("CR029 tape provenance mismatch")
    s5 = next(x for x in cfg31["scenarios"] if int(x["rank"]) == 5)
    b5 = bundle["scenarios"]["5"]
    rank5 = b5["tape"]
    if len(rank5) != 719 or core._tape_sha(rank5) != s5["tape_sha256"]:
        raise RuntimeError("rank5 tape provenance mismatch")
    return base, rank5


def _agent(base: list[dict], rank5: list[dict], mode: str, rule: dict):
    state = {"classified": False, "keiz": False, "exited": False, "decision_value": None}
    switch = int(rule["switch_clock"])
    money_th = float(rule["keiz_if_self_money_gt"])
    horizon = int(rule["exit_horizon"])
    exit_th = float(rule["exit_if_lte"])

    def agent(obs, config=None):
        s = max(0, min(718, core._clock(obs)))
        if mode == "cr029":
            return copy.deepcopy(base[s])
        if not state["classified"] and s >= switch:
            state["classified"] = True
            state["keiz"] = core._self_money(obs) > money_th
        if mode == "cr039" and state["keiz"] and not state["exited"] and s >= horizon:
            val = float(cr039._public_features(obs).get("opp_animal_sheep", 0.0))
            state["decision_value"] = val
            state["exited"] = val <= exit_th
        tape = base if (not state["keiz"] or state["exited"]) else rank5
        return copy.deepcopy(tape[s])

    return agent, state


def _play(base, rank5, mode, rule, opp_path: Path, seed: int, seat: int) -> dict:
    own, state = _agent(base, rank5, mode, rule)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run([own, str(opp_path)] if seat == 0 else [str(opp_path), own])
    rep = env.toJSON()
    steps = rep.get("steps") or []
    if len(steps) != 720:
        raise RuntimeError(f"short game {len(steps)}")
    final = steps[-1]
    if [final[i].get("status") for i in (0, 1)] != ["DONE", "DONE"]:
        raise RuntimeError("non-DONE")
    rewards = [float(final[i].get("reward")) for i in (0, 1)]
    if not all(math.isfinite(x) for x in rewards):
        raise RuntimeError("non-finite reward")
    delta = rewards[seat] - rewards[1-seat]
    return {
        "score": core._wl(delta),
        "delta": delta,
        "self_reward": rewards[seat],
        "opp_reward": rewards[1-seat],
        "state": copy.deepcopy(state),
    }


def _summary(rows: list[dict]) -> dict:
    scores = [float(r["result"]["score"]) for r in rows]
    deltas = [float(r["result"]["delta"]) for r in rows]
    return {
        "games": len(rows),
        "wins": sum(x == 1.0 for x in scores),
        "losses": sum(x == 0.0 for x in scores),
        "ties": sum(x == 0.5 for x in scores),
        "score_total": sum(scores),
        "score_rate": sum(scores)/len(scores) if scores else None,
        "mean_delta": statistics.mean(deltas) if deltas else None,
        "median_delta": statistics.median(deltas) if deltas else None,
    }


def _paired(a: list[dict], b: list[dict]) -> dict:
    aa = {(r["opponent"], r["seed"], r["seat"]): r for r in a}
    bb = {(r["opponent"], r["seed"], r["seat"]): r for r in b}
    keys = sorted(set(aa) & set(bb))
    gains, favorable, unfavorable = [], 0, 0
    for k in keys:
        ar, br = aa[k]["result"], bb[k]["result"]
        favorable += float(ar["score"]) > float(br["score"])
        unfavorable += float(ar["score"]) < float(br["score"])
        gains.append(float(ar["delta"]) - float(br["delta"]))
    return {
        "paired_games": len(keys),
        "score_gain": sum(float(aa[k]["result"]["score"]) - float(bb[k]["result"]["score"]) for k in keys),
        "improvements": favorable,
        "regressions": unfavorable,
        "net_conversions": favorable-unfavorable,
        "mean_delta_gain": statistics.mean(gains) if gains else None,
        "positive_margin_rows": sum(x > 0 for x in gains),
        "negative_margin_rows": sum(x < 0 for x in gains),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    seeds = [int(x) for x in cfg["fresh_seeds"]]
    overlap = _seed_firewall(seeds)
    if overlap:
        raise RuntimeError(f"fresh seed firewall overlap: {overlap}")

    bundle = _load(args.source_bundle)
    base, rank5 = _verify_bundle(bundle)
    opp_dir = Path(args.opponent_dir)
    rows = {"cr029": [], "full_rank5": [], "cr039": []}
    errors = []

    for om in cfg["opponents"]:
        opp = opp_dir / f"{om['id']}.py"
        if not opp.is_file():
            raise FileNotFoundError(opp)
        for seed in seeds:
            for seat in (0, 1):
                for mode in rows:
                    try:
                        result = _play(base, rank5, mode, cfg["candidate_rule"], opp, seed, seat)
                        rows[mode].append({"opponent": om["id"], "seed": seed, "seat": seat, "result": result})
                    except Exception as exc:
                        errors.append({"mode": mode, "opponent": om["id"], "seed": seed, "seat": seat, "error": repr(exc)[:500]})

    expected = len(cfg["opponents"]) * len(seeds) * 2
    mechanical = not errors and all(len(v) == expected for v in rows.values())
    summaries = {k: _summary(v) for k, v in rows.items()}
    vs_cr029 = _paired(rows["cr039"], rows["cr029"])
    vs_full = _paired(rows["cr039"], rows["full_rank5"])
    full_vs_cr029 = _paired(rows["full_rank5"], rows["cr029"])
    gate = cfg["gate"]
    checks = {
        "mechanical": mechanical,
        "score_vs_cr029": mechanical and vs_cr029["score_gain"] >= float(gate["candidate_score_gain_vs_cr029_min"]),
        "margin_vs_cr029": mechanical and vs_cr029["mean_delta_gain"] >= float(gate["candidate_mean_delta_gain_vs_cr029_min"]),
        "regressions_vs_cr029": mechanical and vs_cr029["regressions"] <= int(gate["candidate_regressions_vs_cr029_max"]),
        "score_vs_full_rank5": mechanical and vs_full["score_gain"] >= float(gate["candidate_score_gain_vs_full_rank5_min"]),
    }
    decision = "CR040_PROMOTE_CR039_TO_PACKAGE_PREFLIGHT" if all(checks.values()) else "CR040_DO_NOT_PROMOTE_CR039"
    out = {
        "experiment": cfg["experiment"],
        "fresh_seeds": seeds,
        "seed_firewall_overlap": overlap,
        "expected_games_per_strategy": expected,
        "errors": errors,
        "mechanical_complete": mechanical,
        "summaries": summaries,
        "cr039_vs_cr029": vs_cr029,
        "cr039_vs_full_rank5": vs_full,
        "full_rank5_vs_cr029": full_vs_cr029,
        "checks": checks,
        "decision": decision,
        "runtime_identity_features": False,
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
        "rows": rows,
    }
    p = Path(args.output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k != "rows"}, indent=2, sort_keys=True))
    if not mechanical:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
