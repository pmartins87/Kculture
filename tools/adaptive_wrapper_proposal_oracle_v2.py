#!/usr/bin/env python3
"""Oracle gate over market proposals emitted by strong adaptive modern wrappers.

V47 is the executed organism. Shadow public agents observe the same live V47 trajectory
and may propose a one-turn market action only when their farmer/hands exactly match V47.
The exact engine evaluates each unique proposal from a fresh replay.

Offline only. Third-party source remains transient.
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
from collections import Counter
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
    score,
)

EXPECTED_ENGINE = "1.32.7"
BASE = {
    "key": "v47",
    "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
PROPOSERS = [
    {
        "key": "ready_stock",
        "handle": "alperen5252525/kaggriculture-ready-stock-earlier-sales",
        "expected_main_sha256": "45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017",
    },
    {
        "key": "market_smart",
        "handle": "tetsutani/market-smart-farming-kaggriculture",
        "expected_main_sha256": "f6a756cfb900b9d5f499905d596b63f1fde2445342ac4b1ae04e353739bd62d2",
    },
    {
        "key": "v46_microstructure",
        "handle": "ahmedberatozer/kaggriculture-v46-first-turn-microstructure-and-s",
        "expected_main_sha256": "735c370383b70d3bf3aac792f2c147e0afc99166fc9f253ede10e8a030acedb6",
    },
    {
        "key": "v48_queue",
        "handle": "ahmedberatozer/kaggriculture-v48-clear-the-queue",
        "expected_main_sha256": "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
    },
    {
        "key": "shop_aware",
        "handle": "tetsutani/shop-aware-farming-kaggriculture",
        "expected_main_sha256": "411875c97d6a178ec4df59b696b13708ba2fac754cae924851395a0578ca983d",
    },
]
OPPONENTS = [
    {
        "key": "v47_mirror",
        "handle": BASE["handle"],
        "expected_main_sha256": BASE["expected_main_sha256"],
    },
    {
        "key": "v48_opponent",
        "handle": "ahmedberatozer/kaggriculture-v48-clear-the-queue",
        "expected_main_sha256": "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
    },
]
SEEDS = [63001, 63002]
MIN_STEP = 0
MAX_STEP = 671
MIN_EVENT_SEPARATION = 72
MAX_EVENTS_PER_MATCHUP = 2
MIN_VALID_BRANCH_STATES = 8
PASS_SCORE_DELTA = 0.125
PASS_NONWIN_TO_WIN = 2


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


def same_physical(a: dict, b: dict) -> bool:
    return a["farmer"] == b["farmer"] and a["hands"] == b["hands"]


def admissible_shadow_proposals(base: dict, shadow_actions: dict[str, dict]) -> list[dict]:
    """Deduplicate non-base market actions that preserve exact physical actions."""
    base = canonical_action(base)
    base_key = action_key(base)
    grouped: dict[str, dict] = {}
    for source, raw in shadow_actions.items():
        a = canonical_action(raw)
        if not same_physical(base, a):
            continue
        if len(a["market"]) > 10:
            continue
        k = action_key(a)
        if k == base_key:
            continue
        if k not in grouped:
            grouped[k] = {
                "action_key": k,
                "action": a,
                "sources": [source],
            }
        else:
            grouped[k]["sources"].append(source)
    return sorted(grouped.values(), key=lambda x: (x["sources"][0], x["action_key"]))


class DiscoveryWrapper:
    def __init__(self, base_main: Path, proposer_paths: dict[str, Path]):
        self.base = load_public_agent(base_main)
        self.shadows = {
            key: load_public_agent(proposer_paths[key])
            for key in sorted(proposer_paths)
        }
        self.trace: list[dict] = []

    def __call__(self, obs, config=None):
        step = obs_step(obs)
        base = canonical_action(call_agent(self.base, obs, config))
        shadows = {
            key: canonical_action(call_agent(agent, obs, config))
            for key, agent in self.shadows.items()
        }
        proposals = admissible_shadow_proposals(base, shadows)
        self.trace.append(
            {
                "step": step,
                "base_action": copy.deepcopy(base),
                "base_action_key": action_key(base),
                "proposals": copy.deepcopy(proposals),
            }
        )
        return base


class BaseWrapper:
    def __init__(self, base_main: Path):
        self.base = load_public_agent(base_main)

    def __call__(self, obs, config=None):
        return canonical_action(call_agent(self.base, obs, config))


class BranchWrapper:
    """Reproduce all shadow memories, then execute one exact shadow proposal once."""

    def __init__(
        self,
        base_main: Path,
        proposer_paths: dict[str, Path],
        *,
        target_step: int,
        expected_base_key: str,
        selected_source: str,
        expected_proposal_key: str,
    ):
        self.base = load_public_agent(base_main)
        self.shadows = {
            key: load_public_agent(proposer_paths[key])
            for key in sorted(proposer_paths)
        }
        self.target_step = int(target_step)
        self.expected_base_key = expected_base_key
        self.selected_source = selected_source
        self.expected_proposal_key = expected_proposal_key
        self.target_seen = False

    def __call__(self, obs, config=None):
        step = obs_step(obs)
        base = canonical_action(call_agent(self.base, obs, config))
        shadow_actions = {
            key: canonical_action(call_agent(agent, obs, config))
            for key, agent in self.shadows.items()
        }
        if step != self.target_step:
            return base

        self.target_seen = True
        if action_key(base) != self.expected_base_key:
            raise RuntimeError(
                f"base action mismatch at step {step}: {action_key(base)} != {self.expected_base_key}"
            )
        selected = shadow_actions[self.selected_source]
        if action_key(selected) != self.expected_proposal_key:
            raise RuntimeError(
                f"shadow proposal mismatch source={self.selected_source} step={step}"
            )
        if not same_physical(base, selected):
            raise RuntimeError("selected shadow changed physical action at branch")
        if len(selected["market"]) > 10:
            raise RuntimeError("selected shadow proposal exceeds market cardinality")
        return selected


def finish(env, seat: int, wrapper=None) -> dict:
    payload = env.toJSON()
    statuses = [str(x) for x in payload.get("statuses", [])]
    rewards = [float(x) for x in payload.get("rewards", [])]
    steps = len(payload.get("steps") or [])
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"episode status failure: {statuses}")
    if steps < 720 or len(rewards) != 2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode result steps={steps} rewards={rewards}")
    if wrapper is not None and hasattr(wrapper, "target_seen") and not wrapper.target_seen:
        raise RuntimeError(f"branch target {wrapper.target_step} not seen")
    mine, opp = (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])
    return {
        "rewards": rewards,
        "reward": mine,
        "opponent_reward": opp,
        "margin": mine - opp,
        "score": score(mine - opp),
        "statuses": statuses,
        "steps": steps,
    }


def run_discovery(
    base_main: Path,
    proposer_paths: dict[str, Path],
    opponent_main: Path,
    *,
    seed: int,
    seat: int,
) -> dict:
    cand = DiscoveryWrapper(base_main, proposer_paths)
    opp = load_public_agent(opponent_main)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    if seat == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    out = finish(env, seat)
    out["trace"] = cand.trace
    return out


def run_base(
    base_main: Path,
    opponent_main: Path,
    *,
    seed: int,
    seat: int,
) -> dict:
    cand = BaseWrapper(base_main)
    opp = load_public_agent(opponent_main)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    if seat == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    return finish(env, seat)


def run_branch(
    base_main: Path,
    proposer_paths: dict[str, Path],
    opponent_main: Path,
    *,
    seed: int,
    seat: int,
    event: dict,
    proposal: dict,
) -> dict:
    source = sorted(proposal["sources"])[0]
    cand = BranchWrapper(
        base_main,
        proposer_paths,
        target_step=int(event["step"]),
        expected_base_key=str(event["base_action_key"]),
        selected_source=source,
        expected_proposal_key=str(proposal["action_key"]),
    )
    opp = load_public_agent(opponent_main)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    if seat == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    return finish(env, seat, cand)


def select_events(trace: list[dict]) -> list[dict]:
    eligible = [
        row
        for row in trace
        if MIN_STEP <= int(row["step"]) <= MAX_STEP and row["proposals"]
    ]
    selected = []
    for row in eligible:
        if selected and int(row["step"]) - int(selected[-1]["step"]) < MIN_EVENT_SEPARATION:
            continue
        selected.append(row)
        if len(selected) >= MAX_EVENTS_PER_MATCHUP:
            break
    return selected


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {}
    bs = [float(r["base"]["score"]) for r in rows]
    os = [float(r["oracle"]["score"]) for r in rows]
    md = [float(r["oracle"]["margin"] - r["base"]["margin"]) for r in rows]
    return {
        "branch_states": len(rows),
        "base_score_rate": float(np.mean(bs)),
        "oracle_score_rate": float(np.mean(os)),
        "score_delta": float(np.mean(os) - np.mean(bs)),
        "mean_oracle_margin_delta": statistics.mean(md),
        "median_oracle_margin_delta": statistics.median(md),
        "nonwin_to_win_flips": sum(
            r["base"]["score"] < 1.0 and r["oracle"]["score"] == 1.0 for r in rows
        ),
        "loss_to_win_flips": sum(
            r["base"]["score"] == 0.0 and r["oracle"]["score"] == 1.0 for r in rows
        ),
        "positive_margin_headroom_states": sum(x > 0 for x in md),
    }


def purge_all(paths: list[Path]) -> None:
    for p in paths:
        purge_package_modules(p.parent)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/adaptive-wrapper-proposal-v2/ADAPTIVE_WRAPPER_PROPOSAL_V2.json",
    )
    args = ap.parse_args()

    import kaggle_environments

    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(
            f"kaggle-environments mismatch: {getattr(kaggle_environments, '__version__', None)}"
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    failures: list[dict] = []
    rows: list[dict] = []
    matchup_receipts: list[dict] = []
    provenance: dict[str, Any] = {}
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="adaptive-wrapper-proposal-v2-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")
            proposer_paths: dict[str, Path] = {}
            for spec in PROPOSERS:
                p, rec = acquire(spec, tmp / f"proposal_{spec['key']}")
                proposer_paths[spec["key"]] = p
                provenance[spec["key"]] = rec

            opponent_paths: dict[str, Path] = {}
            proposer_by_sha = {
                spec["expected_main_sha256"]: spec["key"] for spec in PROPOSERS
            }
            for spec in OPPONENTS:
                if spec["expected_main_sha256"] == BASE["expected_main_sha256"]:
                    opponent_paths[spec["key"]] = base_main
                    provenance[spec["key"]] = {
                        **provenance["base"],
                        "key": spec["key"],
                        "role": "opponent",
                        "reused_exact_base_bytes": True,
                    }
                elif spec["expected_main_sha256"] in proposer_by_sha:
                    src_key = proposer_by_sha[spec["expected_main_sha256"]]
                    opponent_paths[spec["key"]] = proposer_paths[src_key]
                    provenance[spec["key"]] = {
                        **provenance[src_key],
                        "key": spec["key"],
                        "role": "opponent",
                        "reused_exact_proposer_bytes": src_key,
                    }
                else:
                    p, rec = acquire(spec, tmp / f"opponent_{spec['key']}")
                    opponent_paths[spec["key"]] = p
                    provenance[spec["key"]] = rec

            all_paths = [base_main, *proposer_paths.values(), *opponent_paths.values()]

            for opp_spec in OPPONENTS:
                opp_key = opp_spec["key"]
                opp_main = opponent_paths[opp_key]
                for seed in SEEDS:
                    for seat in (0, 1):
                        key = {"opponent": opp_key, "seed": seed, "seat": seat}
                        try:
                            purge_all(all_paths)
                            discovery = run_discovery(
                                base_main,
                                proposer_paths,
                                opp_main,
                                seed=seed,
                                seat=seat,
                            )
                            purge_all(all_paths)
                            parity = run_base(
                                base_main,
                                opp_main,
                                seed=seed,
                                seat=seat,
                            )
                            if discovery["rewards"] != parity["rewards"]:
                                raise RuntimeError(
                                    f"shadow discovery changed final rewards: "
                                    f"{discovery['rewards']} != {parity['rewards']}"
                                )

                            events = select_events(discovery["trace"])
                            matchup_receipts.append(
                                {
                                    **key,
                                    "replay_parity": True,
                                    "base_rewards": discovery["rewards"],
                                    "base_margin": discovery["margin"],
                                    "disagreement_states": sum(
                                        1 for x in discovery["trace"] if x["proposals"]
                                    ),
                                    "selected_steps": [int(x["step"]) for x in events],
                                    "selected_proposal_counts": [
                                        len(x["proposals"]) for x in events
                                    ],
                                }
                            )

                            for event in events:
                                candidates = [
                                    {
                                        "label": "BASE",
                                        "sources": ["v47"],
                                        "action_key": event["base_action_key"],
                                        "reward": discovery["reward"],
                                        "opponent_reward": discovery["opponent_reward"],
                                        "margin": discovery["margin"],
                                        "score": discovery["score"],
                                    }
                                ]
                                for proposal in event["proposals"]:
                                    purge_all(all_paths)
                                    res = run_branch(
                                        base_main,
                                        proposer_paths,
                                        opp_main,
                                        seed=seed,
                                        seat=seat,
                                        event=event,
                                        proposal=proposal,
                                    )
                                    candidates.append(
                                        {
                                            "label": sorted(proposal["sources"])[0],
                                            "sources": sorted(proposal["sources"]),
                                            "action_key": proposal["action_key"],
                                            "reward": res["reward"],
                                            "opponent_reward": res["opponent_reward"],
                                            "margin": res["margin"],
                                            "score": res["score"],
                                        }
                                    )

                                oracle = max(
                                    candidates,
                                    key=lambda x: (
                                        float(x["score"]),
                                        float(x["margin"]),
                                        ",".join(x["sources"]),
                                    ),
                                )
                                row = {
                                    **key,
                                    "step": int(event["step"]),
                                    "proposal_count": len(candidates),
                                    "base": candidates[0],
                                    "oracle": oracle,
                                    "candidates": candidates,
                                }
                                rows.append(row)
                                print(
                                    "WRAPPER_PROPOSAL_BRANCH",
                                    json.dumps(
                                        {
                                            **key,
                                            "step": event["step"],
                                            "proposals": len(candidates),
                                            "base_score": candidates[0]["score"],
                                            "base_margin": candidates[0]["margin"],
                                            "oracle_sources": oracle["sources"],
                                            "oracle_score": oracle["score"],
                                            "oracle_margin": oracle["margin"],
                                        },
                                        sort_keys=True,
                                    ),
                                    flush=True,
                                )
                        except Exception as exc:
                            failures.append(
                                {**key, "error": f"{type(exc).__name__}: {exc}"}
                            )
                        finally:
                            purge_all(all_paths)

    except Exception as exc:
        failures.append(
            {"phase": "acquisition_or_setup", "error": f"{type(exc).__name__}: {exc}"}
        )

    overall = summarize(rows)
    by_opponent = {
        spec["key"]: summarize([r for r in rows if r["opponent"] == spec["key"]])
        for spec in OPPONENTS
    }
    oracle_sources = Counter()
    for row in rows:
        if row["oracle"]["label"] != "BASE":
            for src in row["oracle"]["sources"]:
                oracle_sources[src] += 1

    mechanical_pass = (
        not failures
        and len(rows) >= MIN_VALID_BRANCH_STATES
        and all(x.get("replay_parity") for x in matchup_receipts)
    )
    if mechanical_pass and (
        float(overall.get("score_delta", 0.0)) >= PASS_SCORE_DELTA
        or int(overall.get("nonwin_to_win_flips", 0)) >= PASS_NONWIN_TO_WIN
    ):
        decision = "WRAPPER_PROPOSAL_WL_HEADROOM_PASS"
    elif mechanical_pass and float(overall.get("mean_oracle_margin_delta", 0.0)) > 0:
        decision = "WRAPPER_PROPOSAL_MARGIN_ONLY"
    elif mechanical_pass:
        decision = "WRAPPER_PROPOSAL_NO_HEADROOM"
    else:
        decision = "WRAPPER_PROPOSAL_MECHANICS_INVALID"

    result = {
        "schema": "kculture-adaptive-wrapper-proposal-oracle-v2b",
        "engine": EXPECTED_ENGINE,
        "base": BASE,
        "proposers": PROPOSERS,
        "opponents": OPPONENTS,
        "seeds": SEEDS,
        "event_rule": {
            "min_step": MIN_STEP,
            "max_step": MAX_STEP,
            "min_event_separation": MIN_EVENT_SEPARATION,
            "max_events_per_matchup": MAX_EVENTS_PER_MATCHUP,
        },
        "gate": {
            "min_valid_branch_states": MIN_VALID_BRANCH_STATES,
            "pass_score_delta": PASS_SCORE_DELTA,
            "pass_nonwin_to_win_flips": PASS_NONWIN_TO_WIN,
        },
        "provenance": provenance,
        "matchups": matchup_receipts,
        "branch_states": len(rows),
        "candidate_rollouts": sum(max(0, r["proposal_count"] - 1) for r in rows),
        "summary": overall,
        "by_opponent": by_opponent,
        "oracle_source_counts": dict(oracle_sources),
        "failures": failures,
        "mechanical_pass": mechanical_pass,
        "decision": decision,
        "seconds": time.perf_counter() - started,
        "rows": rows,
        "offline_oracle_only": True,
        "automatic_kaggle_submission": False,
        "third_party_code_persisted": False,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print(
        "WRAPPER_PROPOSAL_RESULT",
        json.dumps(
            {
                "branch_states": result["branch_states"],
                "candidate_rollouts": result["candidate_rollouts"],
                "mechanical_pass": mechanical_pass,
                "summary": overall,
                "by_opponent": by_opponent,
                "oracle_source_counts": dict(oracle_sources),
                "failures": len(failures),
                "decision": decision,
                "seconds": result["seconds"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
