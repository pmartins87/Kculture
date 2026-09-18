#!/usr/bin/env python3
"""First-party causal gate for an early ready-WOOL sale on exact V47.

The treatment is intentionally tiny and independent of Ready Stock source code:
if V47's current market list is empty and current own shed already contains at least
2 WOOL, add exactly SELL WOOL 2 for that turn only. Farmer/hands remain exact V47.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,
    load_public_agent,
    purge_package_modules,
    sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import (
    action_key,
    call_agent,
    canonical_action,
    obs_step,
    plain,
    score,
)

EXPECTED_ENGINE = "1.32.7"
LOADER_CONTRACT = "official_get_last_callable"
BASE = {
    "key": "v47",
    "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
OPPONENTS = [
    {
        "key": "v47_mirror",
        "handle": BASE["handle"],
        "expected_main_sha256": BASE["expected_main_sha256"],
    },
    {
        "key": "v48",
        "handle": "ahmedberatozer/kaggriculture-v48-clear-the-queue",
        "expected_main_sha256": "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
    },
    {
        "key": "tactical_memory",
        "handle": "web3cainiao/kaggriculture-v21-tactical-memory",
        "expected_main_sha256": "630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054",
    },
]
SEEDS = [64001, 64002, 64003, 64004]
MAX_STEP = 671
MIN_EVENT_SEPARATION = 72
MAX_EVENTS_PER_MATCHUP = 2
MIN_VALID_BRANCH_STATES = 24


def getv(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except Exception:
        return getattr(obj, key, default)


def own_wool(obs: Any) -> int:
    p = plain(obs)
    private = getv(p, "private", {}) or {}
    shed = getv(private, "shed", {}) or {}
    try:
        return max(0, int(getv(shed, "WOOL", 0) or 0))
    except Exception:
        return 0


def eligible(obs: Any, base_action: dict) -> bool:
    step = obs_step(obs)
    if step < 0 or step > MAX_STEP:
        return False
    a = canonical_action(base_action)
    return a["market"] == [] and own_wool(obs) >= 2


def treated_action(base_action: dict) -> dict:
    a = canonical_action(base_action)
    if a["market"] != []:
        raise RuntimeError("O-RW1 requires exact empty V47 market")
    return {
        "farmer": copy.deepcopy(a["farmer"]),
        "hands": copy.deepcopy(a["hands"]),
        "market": [["SELL", "WOOL", 2]],
    }


def acquire(spec: dict, tmp: Path) -> tuple[Path, dict]:
    main, receipt = acquire_public_main(spec["handle"], tmp)
    observed = sha256_bytes(main.read_bytes())
    if observed != spec["expected_main_sha256"]:
        raise RuntimeError(
            f"{spec['key']} identity mismatch: {observed} != {spec['expected_main_sha256']}"
        )
    return main, {
        "key": spec["key"],
        "handle": spec["handle"],
        "expected_main_sha256": spec["expected_main_sha256"],
        "observed_main_sha256": observed,
        **receipt,
    }


class Discovery:
    def __init__(self, main_py: Path):
        self.agent = load_public_agent(main_py)
        self.trace: list[dict] = []

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        if eligible(obs, base):
            self.trace.append({
                "step": obs_step(obs),
                "base_action": copy.deepcopy(base),
                "base_action_key": action_key(base),
                "wool": own_wool(obs),
            })
        return base


class BaseWrapper:
    def __init__(self, main_py: Path):
        self.agent = load_public_agent(main_py)

    def __call__(self, obs, config=None):
        return canonical_action(call_agent(self.agent, obs, config))


class Treatment:
    def __init__(self, main_py: Path, event: dict):
        self.agent = load_public_agent(main_py)
        self.target_step = int(event["step"])
        self.expected_base_key = str(event["base_action_key"])
        self.target_seen = False

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        if obs_step(obs) != self.target_step:
            return base
        self.target_seen = True
        if action_key(base) != self.expected_base_key:
            raise RuntimeError("V47 base action mismatch at O-RW1 target")
        if not eligible(obs, base):
            raise RuntimeError(
                f"O-RW1 target no longer eligible step={self.target_step} wool={own_wool(obs)} market={base['market']}"
            )
        out = treated_action(base)
        if out["farmer"] != base["farmer"] or out["hands"] != base["hands"]:
            raise RuntimeError("O-RW1 changed physical action")
        return out


def finish(env, seat: int, wrapper=None) -> dict:
    p = env.toJSON()
    statuses = [str(x) for x in p.get("statuses", [])]
    rewards = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"episode status failure: {statuses}")
    if steps < 720 or len(rewards) != 2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode result steps={steps} rewards={rewards}")
    if wrapper is not None and hasattr(wrapper, "target_seen") and not wrapper.target_seen:
        raise RuntimeError(f"O-RW1 target {wrapper.target_step} not reached")
    mine, opp = (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])
    margin = mine - opp
    return {
        "rewards": rewards,
        "reward": mine,
        "opponent_reward": opp,
        "margin": margin,
        "score": score(margin),
        "statuses": statuses,
        "steps": steps,
    }


def run_episode(base_main: Path, opp_main: Path, *, seed: int, seat: int, mode: str, event=None):
    if mode == "discovery":
        cand = Discovery(base_main)
    elif mode == "base":
        cand = BaseWrapper(base_main)
    elif mode == "treatment":
        cand = Treatment(base_main, event)
    else:
        raise ValueError(mode)
    opp = load_public_agent(opp_main)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    if seat == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    out = finish(env, seat, cand if mode == "treatment" else None)
    if mode == "discovery":
        out["trace"] = cand.trace
    return out


def select_events(trace: list[dict]) -> list[dict]:
    selected = []
    for row in trace:
        if selected and int(row["step"]) - int(selected[-1]["step"]) < MIN_EVENT_SEPARATION:
            continue
        selected.append(row)
        if len(selected) >= MAX_EVENTS_PER_MATCHUP:
            break
    return selected


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {}
    deltas = [float(r["treatment"]["score"] - r["base"]["score"]) for r in rows]
    margins = [float(r["treatment"]["margin"] - r["base"]["margin"]) for r in rows]
    return {
        "branch_states": len(rows),
        "mean_score_delta": statistics.mean(deltas),
        "mean_margin_delta": statistics.mean(margins),
        "median_margin_delta": statistics.median(margins),
        "positive_wl_states": sum(d > 0 for d in deltas),
        "negative_wl_states": sum(d < 0 for d in deltas),
        "neutral_wl_states": sum(d == 0 for d in deltas),
        "positive_margin_states": sum(d > 0 for d in margins),
        "negative_margin_states": sum(d < 0 for d in margins),
        "nonwin_to_win_flips": sum(
            r["base"]["score"] < 1.0 and r["treatment"]["score"] == 1.0 for r in rows
        ),
        "win_to_nonwin_regressions": sum(
            r["base"]["score"] == 1.0 and r["treatment"]["score"] < 1.0 for r in rows
        ),
        "loss_to_win_flips": sum(
            r["base"]["score"] == 0.0 and r["treatment"]["score"] == 1.0 for r in rows
        ),
        "steps": sorted({int(r["step"]) for r in rows}),
    }


def purge(paths: list[Path]):
    for p in paths:
        purge_package_modules(p.parent)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/ready-wool-causal/READY_WOOL_CAUSAL_GATE.json",
    )
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(f"engine mismatch: {getattr(kaggle_environments,'__version__',None)}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    provenance = {}
    failures = []
    matchups = []
    rows = []
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="ready-wool-causal-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")
            opp_paths = {}
            for spec in OPPONENTS:
                if spec["expected_main_sha256"] == BASE["expected_main_sha256"]:
                    opp_paths[spec["key"]] = base_main
                    provenance[spec["key"]] = {
                        **provenance["base"],
                        "key": spec["key"],
                        "role": "opponent",
                        "reused_exact_base_bytes": True,
                    }
                else:
                    p, rec = acquire(spec, tmp / f"opp_{spec['key']}")
                    opp_paths[spec["key"]] = p
                    provenance[spec["key"]] = rec
            all_paths = [base_main, *opp_paths.values()]

            for ospec in OPPONENTS:
                opp_key = ospec["key"]
                opp_main = opp_paths[opp_key]
                for seed in SEEDS:
                    for seat in (0,1):
                        key = {"opponent": opp_key, "seed": seed, "seat": seat}
                        try:
                            purge(all_paths)
                            d = run_episode(base_main, opp_main, seed=seed, seat=seat, mode="discovery")
                            purge(all_paths)
                            b = run_episode(base_main, opp_main, seed=seed, seat=seat, mode="base")
                            if d["rewards"] != b["rewards"]:
                                raise RuntimeError(f"fresh replay parity mismatch {d['rewards']} != {b['rewards']}")
                            events = select_events(d["trace"])
                            matchups.append({
                                **key,
                                "base_rewards": d["rewards"],
                                "base_margin": d["margin"],
                                "eligible_states": len(d["trace"]),
                                "selected_steps": [int(e["step"]) for e in events],
                                "selected_wool": [int(e["wool"]) for e in events],
                                "replay_parity": True,
                            })
                            for event in events:
                                purge(all_paths)
                                tr = run_episode(
                                    base_main, opp_main, seed=seed, seat=seat,
                                    mode="treatment", event=event
                                )
                                row = {
                                    **key,
                                    "step": int(event["step"]),
                                    "wool": int(event["wool"]),
                                    "base": {
                                        "reward": d["reward"],
                                        "opponent_reward": d["opponent_reward"],
                                        "margin": d["margin"],
                                        "score": d["score"],
                                    },
                                    "treatment": {
                                        "reward": tr["reward"],
                                        "opponent_reward": tr["opponent_reward"],
                                        "margin": tr["margin"],
                                        "score": tr["score"],
                                    },
                                }
                                rows.append(row)
                                print("READY_WOOL_BRANCH", json.dumps({
                                    **key,
                                    "step": row["step"],
                                    "wool": row["wool"],
                                    "base_score": row["base"]["score"],
                                    "treatment_score": row["treatment"]["score"],
                                    "score_delta": row["treatment"]["score"]-row["base"]["score"],
                                    "margin_delta": row["treatment"]["margin"]-row["base"]["margin"],
                                }, sort_keys=True), flush=True)
                        except Exception as exc:
                            failures.append({**key, "error": f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge(all_paths)

    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    overall = summarize(rows)
    by_opp = {
        spec["key"]: summarize([r for r in rows if r["opponent"] == spec["key"]])
        for spec in OPPONENTS
    }
    mechanical_pass = (
        not failures
        and len(rows) >= MIN_VALID_BRANCH_STATES
        and all(x.get("replay_parity") for x in matchups)
    )

    positive_blocks = sum(
        1 for v in by_opp.values()
        if v and float(v.get("mean_score_delta",0.0)) >= 0.0
    )
    if mechanical_pass and (
        float(overall.get("mean_score_delta",0.0)) > 0.0
        and int(overall.get("nonwin_to_win_flips",0)) >= 2
        and int(overall.get("win_to_nonwin_regressions",0)) == 0
        and positive_blocks >= 2
    ):
        decision = "READY_WOOL_CAUSAL_PASS_SAFE_OPTION"
    elif mechanical_pass and (
        int(overall.get("positive_wl_states",0)) > 0
        and (
            int(overall.get("negative_wl_states",0)) > 0
            or any(v and float(v.get("mean_score_delta",0.0)) < 0 for v in by_opp.values())
        )
    ):
        decision = "READY_WOOL_CAUSAL_HETEROGENEOUS"
    elif mechanical_pass and float(overall.get("mean_margin_delta",0.0)) > 0:
        decision = "READY_WOOL_MARGIN_ONLY"
    elif mechanical_pass:
        decision = "READY_WOOL_NO_HEADROOM"
    else:
        decision = "READY_WOOL_MECHANICS_INVALID"

    result = {
        "schema":"kculture-first-party-ready-wool-causal-v1",
        "engine":EXPECTED_ENGINE,
        "loader_contract":LOADER_CONTRACT,
        "base":BASE,
        "opponents":OPPONENTS,
        "seeds":SEEDS,
        "operator":{
            "eligibility":"V47 market exactly empty and current own shed WOOL >= 2",
            "treatment_market":[["SELL","WOOL",2]],
            "max_step":MAX_STEP,
            "max_events_per_matchup":MAX_EVENTS_PER_MATCHUP,
            "min_event_separation":MIN_EVENT_SEPARATION,
        },
        "provenance":provenance,
        "matchups":matchups,
        "branch_states":len(rows),
        "failures":failures,
        "mechanical_pass":mechanical_pass,
        "summary":overall,
        "by_opponent":by_opp,
        "decision":decision,
        "seconds":time.perf_counter()-started,
        "rows":rows,
        "automatic_kaggle_submission":False,
    }
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
    print("READY_WOOL_RESULT", json.dumps({
        "branch_states":len(rows),
        "mechanical_pass":mechanical_pass,
        "summary":overall,
        "by_opponent":by_opp,
        "failures":len(failures),
        "decision":decision,
        "seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
