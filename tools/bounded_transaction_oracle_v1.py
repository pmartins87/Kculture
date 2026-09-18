#!/usr/bin/env python3
"""Bounded transaction oracle headroom gate on the exact current V47 adaptive agent.

Offline-only experiment. A fresh exact V47 episode is replayed for every candidate
intervention. The intervention changes only one turn's market action; farmer/hands and
all later policy calls remain the exact public V47 agent.

Third-party source is downloaded transiently and is never committed or uploaded.
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

EXPECTED_ENGINE = "1.32.7"
CANDIDATE = {
    "key": "modern_v47",
    "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
OPPONENTS = [
    {
        "key": "modern_v47_mirror",
        "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
        "expected_main_sha256": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
    },
    {
        "key": "legacy_v39",
        "handle": "ahmedberatozer/kaggriculture-v39-ready-before-the-rush",
        "expected_main_sha256": "708c7485fa964853b193f175dcd83020602c005e159ce82e38dc350b22e970c8",
    },
]
SEEDS = [62001, 62002]
MIN_STEP = 24
MAX_STEP = 671
MIN_EVENT_SEPARATION = 72
MAX_EVENTS_PER_MATCHUP = 2
MIN_VALID_BRANCH_STATES = 12
PASS_SCORE_DELTA = 0.125
PASS_LOSS_TO_WIN = 2

PASS_ACTION = {"farmer": ["PASS"], "hands": [], "market": []}


def plain(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    if hasattr(x, "items"):
        try:
            return {str(k): plain(v) for k, v in x.items()}
        except Exception:
            pass
    return x


def canonical_action(action: Any) -> dict:
    a = plain(action or PASS_ACTION)
    if not isinstance(a, dict):
        raise RuntimeError(f"agent returned non-dict action: {type(a)}")
    return {
        "farmer": list(a.get("farmer") or ["PASS"]),
        "hands": [list(x) for x in list(a.get("hands") or [])],
        "market": [list(x) for x in list(a.get("market") or [])],
    }


def action_key(action: dict) -> str:
    return json.dumps(canonical_action(action), sort_keys=True, separators=(",", ":"))


def obs_step(obs: Any) -> int:
    try:
        return int(obs["step"])
    except Exception:
        return int(getattr(obs, "step"))


def call_agent(agent, obs, config=None):
    try:
        return agent(obs, config)
    except TypeError:
        return agent(obs)


def is_sell(order: list) -> bool:
    return bool(order) and str(order[0]) == "SELL"


def score(margin: float) -> float:
    return 1.0 if margin > 0 else 0.0 if margin < 0 else 0.5


def proposal_actions(base_action: dict) -> list[dict]:
    """Generate a fixed small proposal set from the exact V47 market list."""
    base = canonical_action(base_action)
    market = copy.deepcopy(base["market"])
    sell_idx = [i for i, o in enumerate(market) if is_sell(o)]
    if not sell_idx:
        return [{"label": "BASE", "action": base}]

    raw: list[tuple[str, list[list]]] = [("BASE", copy.deepcopy(market))]

    if len(sell_idx) >= 2:
        m = copy.deepcopy(market)
        i, j = sell_idx[0], sell_idx[1]
        m[i], m[j] = m[j], m[i]
        raw.append(("SWAP_FIRST_TWO_SELLS", m))

        m = copy.deepcopy(market)
        vals = [copy.deepcopy(m[i]) for i in sell_idx][::-1]
        for i, v in zip(sell_idx, vals):
            m[i] = v
        raw.append(("REVERSE_SELL_SUBSEQUENCE", m))

    m = copy.deepcopy(market)
    i = sell_idx[0]
    order = m.pop(i)
    m.insert(0, order)
    raw.append(("FIRST_SELL_TO_FRONT", m))

    m = copy.deepcopy(market)
    i = sell_idx[-1]
    order = m.pop(i)
    m.insert(0, order)
    raw.append(("LAST_SELL_TO_FRONT", m))

    m = copy.deepcopy(market)
    del m[sell_idx[0]]
    raw.append(("DEFER_FIRST_SELL_ONE_TURN", m))

    m = copy.deepcopy(market)
    del m[sell_idx[-1]]
    raw.append(("DEFER_LAST_SELL_ONE_TURN", m))

    out = []
    seen = set()
    for label, proposed_market in raw:
        a = {
            "farmer": copy.deepcopy(base["farmer"]),
            "hands": copy.deepcopy(base["hands"]),
            "market": proposed_market,
        }
        k = action_key(a)
        if k in seen:
            continue
        seen.add(k)
        out.append({"label": label, "action": a})
    return out


class CandidateWrapper:
    def __init__(
        self,
        main_py: Path,
        *,
        record: bool = False,
        target_step: int | None = None,
        expected_base_action: dict | None = None,
        replacement_action: dict | None = None,
    ):
        self.main_py = main_py
        self.agent = load_public_agent(main_py)
        self.record = record
        self.target_step = target_step
        self.expected_base_action = (
            None if expected_base_action is None else canonical_action(expected_base_action)
        )
        self.replacement_action = (
            None if replacement_action is None else canonical_action(replacement_action)
        )
        self.trace: list[dict] = []
        self.target_seen = False
        self.base_action_mismatch = None

    def __call__(self, obs, config=None):
        step = obs_step(obs)
        base = canonical_action(call_agent(self.agent, obs, config))
        if self.record:
            self.trace.append(
                {
                    "step": step,
                    "action": copy.deepcopy(base),
                    "action_key": action_key(base),
                    "sell_count": sum(is_sell(o) for o in base["market"]),
                }
            )
        if self.target_step is not None and step == int(self.target_step):
            self.target_seen = True
            if self.expected_base_action is None or self.replacement_action is None:
                raise RuntimeError("target step configured without expected/replacement action")
            if action_key(base) != action_key(self.expected_base_action):
                self.base_action_mismatch = {
                    "step": step,
                    "expected": self.expected_base_action,
                    "observed": base,
                }
                raise RuntimeError(f"base action mismatch at intervention step {step}")
            # Physical action parity is a hard invariant.
            if self.replacement_action["farmer"] != base["farmer"]:
                raise RuntimeError("proposal changed farmer action")
            if self.replacement_action["hands"] != base["hands"]:
                raise RuntimeError("proposal changed hand actions")
            if len(self.replacement_action["market"]) > 10:
                raise RuntimeError("proposal exceeds market cardinality")
            return copy.deepcopy(self.replacement_action)
        return base


def episode(
    candidate_main: Path,
    opponent_main: Path,
    *,
    seed: int,
    seat: int,
    record: bool = False,
    target_step: int | None = None,
    expected_base_action: dict | None = None,
    replacement_action: dict | None = None,
) -> dict:
    cand = CandidateWrapper(
        candidate_main,
        record=record,
        target_step=target_step,
        expected_base_action=expected_base_action,
        replacement_action=replacement_action,
    )
    opp = load_public_agent(opponent_main)

    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    t0 = time.perf_counter()
    if seat == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    secs = time.perf_counter() - t0
    payload = env.toJSON()
    statuses = [str(x) for x in payload.get("statuses", [])]
    rewards = [float(x) for x in payload.get("rewards", [])]
    steps = len(payload.get("steps") or [])
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(
            f"episode status failure seed={seed} seat={seat} target={target_step}: {statuses}; "
            f"mismatch={cand.base_action_mismatch}"
        )
    if steps < 720 or len(rewards) != 2 or not all(math.isfinite(v) for v in rewards):
        raise RuntimeError(
            f"invalid episode seed={seed} seat={seat}: steps={steps} rewards={rewards}"
        )
    if target_step is not None and not cand.target_seen:
        raise RuntimeError(f"target step {target_step} not observed")

    mine, other = (
        (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])
    )
    return {
        "rewards": rewards,
        "reward": mine,
        "opponent_reward": other,
        "margin": mine - other,
        "score": score(mine - other),
        "statuses": statuses,
        "steps": steps,
        "seconds": secs,
        "trace": cand.trace if record else None,
    }


def select_events(trace: list[dict]) -> list[dict]:
    eligible = [
        row
        for row in trace
        if MIN_STEP <= int(row["step"]) <= MAX_STEP and int(row["sell_count"]) >= 1
    ]
    selected = []
    for row in eligible:
        if selected and int(row["step"]) - int(selected[-1]["step"]) < MIN_EVENT_SEPARATION:
            continue
        selected.append(row)
        if len(selected) >= MAX_EVENTS_PER_MATCHUP:
            break
    return selected


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


def block_summary(rows: list[dict]) -> dict:
    if not rows:
        return {}
    base_scores = [float(r["base"]["score"]) for r in rows]
    oracle_scores = [float(r["oracle"]["score"]) for r in rows]
    deltas = [float(r["oracle"]["margin"] - r["base"]["margin"]) for r in rows]
    return {
        "branch_states": len(rows),
        "base_score_rate": float(np.mean(base_scores)),
        "oracle_score_rate": float(np.mean(oracle_scores)),
        "score_delta": float(np.mean(oracle_scores) - np.mean(base_scores)),
        "mean_oracle_margin_delta": statistics.mean(deltas),
        "median_oracle_margin_delta": statistics.median(deltas),
        "loss_to_win_flips": sum(
            r["base"]["score"] == 0.0 and r["oracle"]["score"] == 1.0 for r in rows
        ),
        "loss_to_nonloss_flips": sum(
            r["base"]["score"] == 0.0 and r["oracle"]["score"] > 0.0 for r in rows
        ),
        "positive_margin_headroom_states": sum(d > 0 for d in deltas),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/bounded-transaction-oracle-v1/BOUNDED_TRANSACTION_ORACLE_V1.json",
    )
    args = ap.parse_args()

    import kaggle_environments

    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(
            f"kaggle-environments mismatch: {getattr(kaggle_environments, '__version__', None)}"
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    failures: list[dict] = []
    rows: list[dict] = []
    matchup_receipts: list[dict] = []
    provenance = {}
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="bounded-transaction-oracle-") as td:
            tmp = Path(td)
            candidate_main, provenance["candidate"] = acquire(
                CANDIDATE, tmp / "candidate_v47"
            )
            opponent_paths = {}
            for spec in OPPONENTS:
                if spec["expected_main_sha256"] == CANDIDATE["expected_main_sha256"]:
                    # Reuse exact bytes but keep independent module instances per episode.
                    opponent_paths[spec["key"]] = candidate_main
                    provenance[spec["key"]] = {
                        **provenance["candidate"],
                        "key": spec["key"],
                        "role": "opponent",
                        "reused_exact_candidate_bytes": True,
                    }
                else:
                    p, rec = acquire(spec, tmp / f"opponent_{spec['key']}")
                    opponent_paths[spec["key"]] = p
                    provenance[spec["key"]] = rec

            for opp_spec in OPPONENTS:
                opp_key = opp_spec["key"]
                opp_main = opponent_paths[opp_key]
                for seed in SEEDS:
                    for seat in (0, 1):
                        matchup = {
                            "opponent": opp_key,
                            "seed": seed,
                            "seat": seat,
                        }
                        try:
                            base = episode(
                                candidate_main,
                                opp_main,
                                seed=seed,
                                seat=seat,
                                record=True,
                            )
                            parity = episode(
                                candidate_main,
                                opp_main,
                                seed=seed,
                                seat=seat,
                                record=False,
                            )
                            if parity["rewards"] != base["rewards"]:
                                raise RuntimeError(
                                    f"fresh replay parity mismatch: {parity['rewards']} != {base['rewards']}"
                                )
                            events = select_events(base["trace"] or [])
                            matchup.update(
                                {
                                    "base_rewards": base["rewards"],
                                    "base_margin": base["margin"],
                                    "eligible_sell_events": sum(
                                        1
                                        for x in (base["trace"] or [])
                                        if MIN_STEP <= int(x["step"]) <= MAX_STEP
                                        and int(x["sell_count"]) >= 1
                                    ),
                                    "selected_steps": [int(x["step"]) for x in events],
                                    "replay_parity": True,
                                }
                            )
                            matchup_receipts.append(matchup)

                            for event in events:
                                proposals = proposal_actions(event["action"])
                                candidates = [
                                    {
                                        "label": "BASE",
                                        "reward": base["reward"],
                                        "opponent_reward": base["opponent_reward"],
                                        "margin": base["margin"],
                                        "score": base["score"],
                                        "action_key": action_key(event["action"]),
                                    }
                                ]
                                for proposal in proposals:
                                    if proposal["label"] == "BASE":
                                        continue
                                    result = episode(
                                        candidate_main,
                                        opp_main,
                                        seed=seed,
                                        seat=seat,
                                        target_step=int(event["step"]),
                                        expected_base_action=event["action"],
                                        replacement_action=proposal["action"],
                                    )
                                    candidates.append(
                                        {
                                            "label": proposal["label"],
                                            "reward": result["reward"],
                                            "opponent_reward": result["opponent_reward"],
                                            "margin": result["margin"],
                                            "score": result["score"],
                                            "action_key": action_key(proposal["action"]),
                                        }
                                    )
                                oracle = max(
                                    candidates,
                                    key=lambda x: (float(x["score"]), float(x["margin"]), x["label"]),
                                )
                                row = {
                                    "opponent": opp_key,
                                    "seed": seed,
                                    "seat": seat,
                                    "step": int(event["step"]),
                                    "base_action": event["action"],
                                    "proposal_count": len(candidates),
                                    "base": candidates[0],
                                    "oracle": oracle,
                                    "candidates": candidates,
                                }
                                rows.append(row)
                                print(
                                    "TRANSACTION_BRANCH",
                                    json.dumps(
                                        {
                                            "opponent": opp_key,
                                            "seed": seed,
                                            "seat": seat,
                                            "step": event["step"],
                                            "proposals": len(candidates),
                                            "base_margin": candidates[0]["margin"],
                                            "base_score": candidates[0]["score"],
                                            "oracle_label": oracle["label"],
                                            "oracle_margin": oracle["margin"],
                                            "oracle_score": oracle["score"],
                                        },
                                        sort_keys=True,
                                    ),
                                    flush=True,
                                )
                        except Exception as exc:
                            failures.append({**matchup, "error": f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge_package_modules(candidate_main.parent)
                            purge_package_modules(opp_main.parent)

    except Exception as exc:
        failures.append({"phase": "acquisition_or_setup", "error": f"{type(exc).__name__}: {exc}"})

    summary = block_summary(rows)
    by_opponent = {}
    for spec in OPPONENTS:
        rr = [r for r in rows if r["opponent"] == spec["key"]]
        by_opponent[spec["key"]] = block_summary(rr)

    transform_counts = Counter(
        r["oracle"]["label"] for r in rows if r["oracle"]["label"] != "BASE"
    )
    mechanical_pass = (
        not failures
        and len(rows) >= MIN_VALID_BRANCH_STATES
        and all(m.get("replay_parity") for m in matchup_receipts)
    )

    if mechanical_pass and (
        float(summary.get("score_delta", 0.0)) >= PASS_SCORE_DELTA
        or int(summary.get("loss_to_win_flips", 0)) >= PASS_LOSS_TO_WIN
    ):
        decision = "TRANSACTION_ORACLE_WL_HEADROOM_PASS"
    elif mechanical_pass and float(summary.get("mean_oracle_margin_delta", 0.0)) > 0:
        decision = "TRANSACTION_ORACLE_MARGIN_ONLY"
    elif mechanical_pass:
        decision = "TRANSACTION_ORACLE_NO_HEADROOM"
    else:
        decision = "TRANSACTION_ORACLE_MECHANICS_INVALID"

    result = {
        "schema": "kculture-bounded-transaction-oracle-v1",
        "engine": EXPECTED_ENGINE,
        "candidate": CANDIDATE,
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
            "pass_loss_to_win_flips": PASS_LOSS_TO_WIN,
        },
        "provenance": provenance,
        "matchups": matchup_receipts,
        "branch_states": len(rows),
        "candidate_rollouts": sum(max(0, int(r["proposal_count"]) - 1) for r in rows),
        "summary": summary,
        "by_opponent": by_opponent,
        "oracle_nonbase_transform_counts": dict(transform_counts),
        "failures": failures,
        "mechanical_pass": mechanical_pass,
        "decision": decision,
        "seconds": time.perf_counter() - started,
        "rows": rows,
        "offline_oracle_only": True,
        "automatic_kaggle_submission": False,
        "third_party_code_persisted": False,
    }
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print(
        "TRANSACTION_ORACLE_RESULT",
        json.dumps(
            {
                "branch_states": result["branch_states"],
                "candidate_rollouts": result["candidate_rollouts"],
                "mechanical_pass": mechanical_pass,
                "summary": summary,
                "by_opponent": by_opponent,
                "oracle_nonbase_transform_counts": dict(transform_counts),
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
