#!/usr/bin/env python3
"""Unified option-value dataset V0 pilot on exact hosted-faithful V47.

Rows are state-option counterfactual labels for O-RW1 and O-TW1.
Opponent identity/seed/seat are offline metadata only and never part of model features.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solver.value_features import FEATURE_NAMES, encode_value_features
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
from tools.first_party_ready_wool_causal_gate import (
    eligible as rw_eligible,
    own_wool,
    treated_action as rw_treated_action,
)
from tools.first_party_town_wheat_deferral_causal_gate import (
    eligible as tw_eligible,
    own_wheat,
    town_wheat_demand,
    treated_action as tw_treated_action,
    wheat_sell_qty,
)

EXPECTED_ENGINE = "1.32.7"
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
SEEDS = [69001, 69002]

OPTION_CONTEXT_NAMES = (
    "opt_orw1",
    "opt_otw1",
    "base_market_orders",
    "base_market_empty",
    "base_market_sell_orders",
    "base_sell_wheat_qty",
    "own_wool_units",
    "own_wheat_units",
    "town_wheat_demand_now",
    "option_quantity",
)
MODEL_FEATURE_NAMES = tuple(FEATURE_NAMES) + OPTION_CONTEXT_NAMES
FORBIDDEN_FEATURE_TOKENS = (
    "seed",
    "opponent",
    "rating",
    "episode",
    "hidden",
    "future",
    "submission",
)


def stable_hash(obj: Any) -> str:
    raw = json.dumps(
        plain(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


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


def market_stats(action: dict) -> dict:
    a = canonical_action(action)
    market = list(a["market"] or [])
    sell_orders = 0
    for order in market:
        if isinstance(order, (list, tuple)) and order and str(order[0]) == "SELL":
            sell_orders += 1
    return {
        "base_market_orders": float(len(market)),
        "base_market_empty": 1.0 if not market else 0.0,
        "base_market_sell_orders": float(sell_orders),
        "base_sell_wheat_qty": float(wheat_sell_qty(a)),
    }


def build_features(obs: Any, config: Any, base_action: dict, option_id: str) -> dict:
    feats = {k: float(v) for k, v in encode_value_features(obs, config).items()}
    feats.update(market_stats(base_action))
    step = obs_step(obs)
    feats.update({
        "opt_orw1": 1.0 if option_id == "O-RW1" else 0.0,
        "opt_otw1": 1.0 if option_id == "O-TW1" else 0.0,
        "own_wool_units": float(own_wool(obs)),
        "own_wheat_units": float(own_wheat(obs)),
        "town_wheat_demand_now": float(town_wheat_demand(step, obs, config)),
        "option_quantity": (
            2.0 if option_id == "O-RW1" else float(wheat_sell_qty(base_action))
        ),
    })
    if tuple(feats.keys()) != MODEL_FEATURE_NAMES:
        missing = [x for x in MODEL_FEATURE_NAMES if x not in feats]
        extra = [x for x in feats if x not in MODEL_FEATURE_NAMES]
        raise RuntimeError(f"feature contract mismatch missing={missing} extra={extra}")
    for k, v in feats.items():
        if any(tok in k.lower() for tok in FORBIDDEN_FEATURE_TOKENS):
            raise RuntimeError(f"forbidden feature token in {k}")
        if not math.isfinite(float(v)):
            raise RuntimeError(f"non-finite feature {k}={v}")
    return feats


class Discovery:
    def __init__(self, main_py: Path):
        self.agent = load_public_agent(main_py)
        self.entrypoint = getattr(self.agent, "__name__", None)
        self.events: dict[str, dict] = {}

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        step = obs_step(obs)

        if "O-RW1" not in self.events and rw_eligible(obs, base):
            self.events["O-RW1"] = {
                "option_id": "O-RW1",
                "step": int(step),
                "state_hash": stable_hash(obs),
                "base_action": copy.deepcopy(base),
                "base_action_key": action_key(base),
                "features": build_features(obs, config, base, "O-RW1"),
            }

        if "O-TW1" not in self.events and tw_eligible(obs, config, base):
            self.events["O-TW1"] = {
                "option_id": "O-TW1",
                "step": int(step),
                "state_hash": stable_hash(obs),
                "base_action": copy.deepcopy(base),
                "base_action_key": action_key(base),
                "features": build_features(obs, config, base, "O-TW1"),
                "sell_qty": int(wheat_sell_qty(base)),
                "town_demand": int(town_wheat_demand(step, obs, config)),
            }

        return base


class BaseWrapper:
    def __init__(self, main_py: Path):
        self.agent = load_public_agent(main_py)

    def __call__(self, obs, config=None):
        return canonical_action(call_agent(self.agent, obs, config))


class OptionTreatment:
    def __init__(self, main_py: Path, event: dict):
        self.agent = load_public_agent(main_py)
        self.event = event
        self.target_seen = False

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        if obs_step(obs) != int(self.event["step"]):
            return base

        self.target_seen = True
        if stable_hash(obs) != self.event["state_hash"]:
            raise RuntimeError(
                f"state hash mismatch at {self.event['option_id']} target step"
            )
        if action_key(base) != self.event["base_action_key"]:
            raise RuntimeError(
                f"base action mismatch at {self.event['option_id']} target step"
            )

        if self.event["option_id"] == "O-RW1":
            if not rw_eligible(obs, base):
                raise RuntimeError("O-RW1 target no longer eligible")
            out = rw_treated_action(base)
        elif self.event["option_id"] == "O-TW1":
            if not tw_eligible(obs, config, base):
                raise RuntimeError("O-TW1 target no longer eligible")
            out, removed = tw_treated_action(base)
            if removed != int(self.event["sell_qty"]):
                raise RuntimeError(
                    f"O-TW1 removed qty mismatch {removed} != {self.event['sell_qty']}"
                )
        else:
            raise RuntimeError(f"unknown option {self.event['option_id']}")

        if out["farmer"] != base["farmer"] or out["hands"] != base["hands"]:
            raise RuntimeError(f"{self.event['option_id']} changed physical action")
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
        raise RuntimeError(
            f"target not reached for {wrapper.event['option_id']} "
            f"step={wrapper.event['step']}"
        )
    mine, opp = (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])
    margin = mine - opp
    return {
        "rewards": rewards,
        "reward": mine,
        "opponent_reward": opp,
        "margin": margin,
        "score": score(margin),
        "steps": steps,
        "statuses": statuses,
    }


def run_episode(base_main: Path, opp_main: Path, *, seed: int, seat: int, mode: str, event=None):
    if mode == "discovery":
        cand = Discovery(base_main)
    elif mode == "base":
        cand = BaseWrapper(base_main)
    elif mode == "treatment":
        cand = OptionTreatment(base_main, event)
    else:
        raise ValueError(mode)

    opp = load_public_agent(opp_main)
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    if seat == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    out = finish(env, seat, cand if mode == "treatment" else None)
    if mode == "discovery":
        out["events"] = cand.events
        out["entrypoint"] = cand.entrypoint
    return out


def purge(paths: list[Path]) -> None:
    seen = set()
    for p in paths:
        key = str(p.parent.resolve())
        if key in seen:
            continue
        seen.add(key)
        purge_package_modules(p.parent)


def summarize_rows(rows: list[dict]) -> dict:
    by_opt = {}
    for option_id in ("O-RW1", "O-TW1"):
        rr = [r for r in rows if r["option_id"] == option_id]
        if rr:
            by_opt[option_id] = {
                "rows": len(rr),
                "mean_score_delta": statistics.mean(r["score_delta"] for r in rr),
                "positive": sum(r["score_delta"] > 0 for r in rr),
                "negative": sum(r["score_delta"] < 0 for r in rr),
                "neutral": sum(r["score_delta"] == 0 for r in rr),
                "mean_margin_delta": statistics.mean(r["margin_delta"] for r in rr),
            }
        else:
            by_opt[option_id] = {"rows": 0}
    return by_opt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/option-value-v0/OPTION_VALUE_DATASET_V0_PILOT.json",
    )
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(
            f"engine mismatch: {getattr(kaggle_environments,'__version__',None)}"
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    provenance = {}
    failures = []
    matchups = []
    rows = []
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="option-value-v0-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")
            probe = load_public_agent(base_main)
            base_entrypoint = getattr(probe, "__name__", None)
            purge_package_modules(base_main.parent)
            if base_entrypoint != "_y_agent_shopherd":
                raise RuntimeError(
                    f"unexpected exact V47 hosted entrypoint: {base_entrypoint}"
                )
            provenance["base"]["hosted_entrypoint"] = base_entrypoint

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

            for spec in OPPONENTS:
                opp_key = spec["key"]
                opp_main = opp_paths[opp_key]
                for seed in SEEDS:
                    for seat in (0, 1):
                        key = {"opponent": opp_key, "seed": seed, "seat": seat}
                        try:
                            purge(all_paths)
                            d = run_episode(
                                base_main, opp_main, seed=seed, seat=seat, mode="discovery"
                            )
                            if d.get("entrypoint") != "_y_agent_shopherd":
                                raise RuntimeError(
                                    f"discovery entrypoint mismatch: {d.get('entrypoint')}"
                                )

                            purge(all_paths)
                            b = run_episode(
                                base_main, opp_main, seed=seed, seat=seat, mode="base"
                            )
                            if d["rewards"] != b["rewards"]:
                                raise RuntimeError(
                                    f"discovery/base replay mismatch "
                                    f"{d['rewards']} != {b['rewards']}"
                                )

                            matchup = {
                                **key,
                                "base_rewards": b["rewards"],
                                "base_score": b["score"],
                                "base_margin": b["margin"],
                                "options_found": sorted(d["events"].keys()),
                                "replay_parity": True,
                            }

                            for option_id, event in sorted(d["events"].items()):
                                purge(all_paths)
                                tr = run_episode(
                                    base_main,
                                    opp_main,
                                    seed=seed,
                                    seat=seat,
                                    mode="treatment",
                                    event=event,
                                )
                                row = {
                                    "state_hash": event["state_hash"],
                                    "option_id": option_id,
                                    "features": event["features"],
                                    "base_action_key": event["base_action_key"],
                                    "base_action": event["base_action"],
                                    "step": int(event["step"]),
                                    "base_score": float(b["score"]),
                                    "option_score": float(tr["score"]),
                                    "score_delta": float(tr["score"] - b["score"]),
                                    "base_margin": float(b["margin"]),
                                    "option_margin": float(tr["margin"]),
                                    "margin_delta": float(tr["margin"] - b["margin"]),
                                    "metadata": {
                                        "opponent": opp_key,
                                        "seed": int(seed),
                                        "seat": int(seat),
                                    },
                                }
                                if tuple(row["features"].keys()) != MODEL_FEATURE_NAMES:
                                    raise RuntimeError("row feature contract changed")
                                rows.append(row)
                                print(
                                    "OPTION_VALUE_ROW",
                                    json.dumps(
                                        {
                                            "option_id": option_id,
                                            "opponent": opp_key,
                                            "seed": seed,
                                            "seat": seat,
                                            "step": row["step"],
                                            "score_delta": row["score_delta"],
                                            "margin_delta": row["margin_delta"],
                                        },
                                        sort_keys=True,
                                    ),
                                    flush=True,
                                )

                            matchups.append(matchup)
                        except Exception as exc:
                            failures.append(
                                {**key, "error": f"{type(exc).__name__}: {exc}"}
                            )
                        finally:
                            purge(all_paths)
    except Exception as exc:
        failures.append({"phase": "setup", "error": f"{type(exc).__name__}: {exc}"})

    rows_by_option = {
        x: sum(r["option_id"] == x for r in rows) for x in ("O-RW1", "O-TW1")
    }
    replay_pass = len(matchups) == len(OPPONENTS) * len(SEEDS) * 2 and all(
        x["replay_parity"] for x in matchups
    )
    feature_pass = all(
        tuple(r["features"].keys()) == MODEL_FEATURE_NAMES
        and all(math.isfinite(float(v)) for v in r["features"].values())
        and not any(
            any(tok in k.lower() for tok in FORBIDDEN_FEATURE_TOKENS)
            for k in r["features"]
        )
        for r in rows
    )
    mechanical_pass = (
        not failures
        and replay_pass
        and feature_pass
        and len(rows) >= 8
        and all(rows_by_option[x] >= 2 for x in rows_by_option)
    )
    decision = (
        "OPTION_VALUE_DATASET_V0_PILOT_PASS"
        if mechanical_pass
        else "OPTION_VALUE_DATASET_V0_PILOT_FAIL"
    )

    result = {
        "schema": "kculture-option-value-dataset-v0-pilot",
        "engine": EXPECTED_ENGINE,
        "base": BASE,
        "opponents": OPPONENTS,
        "seeds": SEEDS,
        "model_feature_names": MODEL_FEATURE_NAMES,
        "feature_count": len(MODEL_FEATURE_NAMES),
        "provenance": provenance,
        "matchups": matchups,
        "rows": rows,
        "row_count": len(rows),
        "rows_by_option": rows_by_option,
        "summary_by_option": summarize_rows(rows),
        "replay_pass": replay_pass,
        "feature_pass": feature_pass,
        "failures": failures,
        "mechanical_pass": mechanical_pass,
        "decision": decision,
        "seconds": time.perf_counter() - started,
        "automatic_kaggle_submission": False,
    }
    out_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "OPTION_VALUE_DATASET_V0_RESULT",
        json.dumps(
            {
                "row_count": len(rows),
                "rows_by_option": rows_by_option,
                "summary_by_option": result["summary_by_option"],
                "replay_pass": replay_pass,
                "feature_pass": feature_pass,
                "failures": len(failures),
                "mechanical_pass": mechanical_pass,
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
