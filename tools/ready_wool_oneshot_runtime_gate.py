#!/usr/bin/env python3
"""Fresh full-episode transfer gate for frozen first-party O-RW1.

Treatment = exact V47 plus one-shot:
  if current V47 market == [] and current own shed.WOOL >= 2 and step <= 671:
      execute SELL WOOL 2
  then disable O-RW1 for the rest of the episode.

No Ready Stock source is used by the treatment.
"""
from __future__ import annotations

import argparse
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
    plain,
    score,
)
from tools.first_party_ready_wool_causal_gate import (
    eligible,
    own_wool,
    treated_action,
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
    {
        "key": "ready_stock",
        "handle": "alperen5252525/kaggriculture-ready-stock-earlier-sales",
        "expected_main_sha256": "45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017",
    },
]
SEEDS = list(range(65001, 65009))


def obs_hash(obs: Any) -> str:
    b = json.dumps(plain(obs), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(b).hexdigest()


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


class BaseTrace:
    def __init__(self, main_py: Path):
        self.agent = load_public_agent(main_py)
        self.trace: list[tuple[str, str]] = []

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        self.trace.append((obs_hash(obs), action_key(base)))
        return base


class OneShotReadyWool:
    def __init__(self, main_py: Path):
        self.agent = load_public_agent(main_py)
        self.trace: list[tuple[str, str]] = []
        self.used = False
        self.trigger_step: int | None = None
        self.trigger_wool: int | None = None

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        self.trace.append((obs_hash(obs), action_key(base)))
        if not self.used and eligible(obs, base):
            self.used = True
            try:
                self.trigger_step = int(plain(obs).get("step", len(self.trace)-1))
            except Exception:
                self.trigger_step = len(self.trace)-1
            self.trigger_wool = own_wool(obs)
            out = treated_action(base)
            if out["farmer"] != base["farmer"] or out["hands"] != base["hands"]:
                raise RuntimeError("O-RW1 changed farmer/hands")
            return out
        return base


def finish(env, seat: int) -> dict:
    p = env.toJSON()
    statuses = [str(x) for x in p.get("statuses", [])]
    rewards = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"episode status failure: {statuses}")
    if steps < 720 or len(rewards) != 2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode result steps={steps} rewards={rewards}")
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


def run_episode(
    base_main: Path,
    opp_main: Path,
    *,
    seed: int,
    seat: int,
    treatment: bool,
) -> dict:
    cand = OneShotReadyWool(base_main) if treatment else BaseTrace(base_main)
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
    out = finish(env, seat)
    out["trace"] = cand.trace
    out["triggered"] = bool(getattr(cand, "used", False))
    out["trigger_step"] = getattr(cand, "trigger_step", None)
    out["trigger_wool"] = getattr(cand, "trigger_wool", None)
    return out


def parity_check(base: dict, tr: dict) -> dict:
    bt = base["trace"]
    tt = tr["trace"]
    if len(bt) != len(tt):
        return {"ok": False, "reason": f"trace length mismatch {len(bt)} != {len(tt)}"}
    trigger = tr["trigger_step"]
    if trigger is None:
        for i, (b, t) in enumerate(zip(bt, tt)):
            if b != t:
                return {"ok": False, "reason": f"no-trigger trace mismatch at {i}"}
        if base["rewards"] != tr["rewards"]:
            return {"ok": False, "reason": "no-trigger final rewards differ"}
        return {"ok": True, "checked_through_step": len(bt)-1, "triggered": False}

    limit = min(int(trigger), len(bt)-1, len(tt)-1)
    for i in range(limit + 1):
        if bt[i] != tt[i]:
            return {
                "ok": False,
                "reason": f"pre-trigger obs/base-action mismatch at {i}",
                "trigger_step": trigger,
            }
    return {"ok": True, "checked_through_step": limit, "triggered": True}


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {}
    base_scores = [float(r["base_score"]) for r in rows]
    tr_scores = [float(r["treatment_score"]) for r in rows]
    score_deltas = [t-b for b,t in zip(base_scores,tr_scores)]
    margin_deltas = [float(r["margin_delta"]) for r in rows]
    triggers = [r for r in rows if r["triggered"]]
    return {
        "pairs": len(rows),
        "base_score_rate": statistics.mean(base_scores),
        "treatment_score_rate": statistics.mean(tr_scores),
        "score_delta": statistics.mean(score_deltas),
        "mean_margin_delta": statistics.mean(margin_deltas),
        "median_margin_delta": statistics.median(margin_deltas),
        "positive_score_pairs": sum(x > 0 for x in score_deltas),
        "negative_score_pairs": sum(x < 0 for x in score_deltas),
        "neutral_score_pairs": sum(x == 0 for x in score_deltas),
        "nonwin_to_win_flips": sum(
            r["base_score"] < 1.0 and r["treatment_score"] == 1.0 for r in rows
        ),
        "win_to_nonwin_regressions": sum(
            r["base_score"] == 1.0 and r["treatment_score"] < 1.0 for r in rows
        ),
        "triggered_pairs": len(triggers),
        "trigger_rate": len(triggers)/len(rows),
        "trigger_steps": sorted({int(r["trigger_step"]) for r in triggers}),
        "mean_trigger_step": (
            statistics.mean(int(r["trigger_step"]) for r in triggers) if triggers else None
        ),
        "positive_margin_pairs": sum(x > 0 for x in margin_deltas),
        "negative_margin_pairs": sum(x < 0 for x in margin_deltas),
    }


def purge(paths: list[Path]) -> None:
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:
            continue
        seen.add(k)
        purge_package_modules(p.parent)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/ready-wool-runtime/READY_WOOL_ONESHOT_RUNTIME_GATE.json",
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
    rows = []
    failures = []
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="ready-wool-runtime-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp/"base")
            probe = load_public_agent(base_main)
            hosted_entrypoint = getattr(probe, "__name__", None)
            purge_package_modules(base_main.parent)
            if hosted_entrypoint != "_y_agent_shopherd":
                raise RuntimeError(f"unexpected exact V47 hosted entrypoint: {hosted_entrypoint}")
            provenance["base"]["hosted_entrypoint"] = hosted_entrypoint
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
                    p, rec = acquire(spec, tmp/f"opp_{spec['key']}")
                    opp_paths[spec["key"]] = p
                    provenance[spec["key"]] = rec

            all_paths = [base_main, *opp_paths.values()]
            for spec in OPPONENTS:
                opp_key = spec["key"]
                opp_main = opp_paths[opp_key]
                for seed in SEEDS:
                    for seat in (0,1):
                        key = {"opponent":opp_key,"seed":seed,"seat":seat}
                        try:
                            purge(all_paths)
                            base = run_episode(
                                base_main,opp_main,seed=seed,seat=seat,treatment=False
                            )
                            purge(all_paths)
                            tr = run_episode(
                                base_main,opp_main,seed=seed,seat=seat,treatment=True
                            )
                            parity = parity_check(base,tr)
                            if not parity["ok"]:
                                raise RuntimeError(f"mechanical parity failure: {parity}")
                            row = {
                                **key,
                                "base_score":base["score"],
                                "treatment_score":tr["score"],
                                "score_delta":tr["score"]-base["score"],
                                "base_margin":base["margin"],
                                "treatment_margin":tr["margin"],
                                "margin_delta":tr["margin"]-base["margin"],
                                "base_rewards":base["rewards"],
                                "treatment_rewards":tr["rewards"],
                                "triggered":tr["triggered"],
                                "trigger_step":tr["trigger_step"],
                                "trigger_wool":tr["trigger_wool"],
                                "parity":parity,
                            }
                            rows.append(row)
                            print("READY_WOOL_RUNTIME_PAIR",json.dumps({
                                **key,
                                "triggered":row["triggered"],
                                "trigger_step":row["trigger_step"],
                                "base_score":row["base_score"],
                                "treatment_score":row["treatment_score"],
                                "score_delta":row["score_delta"],
                                "margin_delta":row["margin_delta"],
                            },sort_keys=True),flush=True)
                        except Exception as exc:
                            failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge(all_paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    overall=summarize(rows)
    by_opp={
        spec["key"]:summarize([r for r in rows if r["opponent"]==spec["key"]])
        for spec in OPPONENTS
    }
    mechanical_pass = (
        not failures
        and len(rows)==len(OPPONENTS)*len(SEEDS)*2
        and all(r["parity"]["ok"] for r in rows)
    )
    nonneg_blocks=sum(
        1 for x in by_opp.values() if x and float(x.get("score_delta",0.0))>=0.0
    )
    worst_block=min(
        (float(x.get("score_delta",0.0)) for x in by_opp.values() if x),
        default=-1.0,
    )

    if mechanical_pass and (
        float(overall.get("score_delta",0.0))>0.0
        and int(overall.get("nonwin_to_win_flips",0))>=4
        and int(overall.get("win_to_nonwin_regressions",0))<=1
        and nonneg_blocks>=3
        and worst_block>=-0.0625
    ):
        decision="READY_WOOL_RUNTIME_PASS"
    elif mechanical_pass and (
        int(overall.get("positive_score_pairs",0))>0
        and (
            int(overall.get("negative_score_pairs",0))>0
            or worst_block < -0.0625
        )
    ):
        decision="READY_WOOL_RUNTIME_HETEROGENEOUS"
    elif mechanical_pass and (
        abs(float(overall.get("score_delta",0.0)))<1e-15
        and float(overall.get("mean_margin_delta",0.0))>0.0
        and worst_block>=-0.0625
    ):
        decision="READY_WOOL_RUNTIME_MARGIN_ONLY"
    elif mechanical_pass:
        decision="READY_WOOL_RUNTIME_FAIL"
    else:
        decision="READY_WOOL_RUNTIME_MECHANICS_INVALID"

    result={
        "schema":"kculture-ready-wool-oneshot-runtime-v1",
        "engine":EXPECTED_ENGINE,
        "loader_contract":LOADER_CONTRACT,
        "base":BASE,
        "opponents":OPPONENTS,
        "seeds":SEEDS,
        "operator":{
            "id":"O-RW1",
            "eligibility":"first state where V47 market == [] and own private shed.WOOL >= 2 and step <= 671",
            "action":[["SELL","WOOL",2]],
            "max_fires_per_episode":1,
        },
        "provenance":provenance,
        "pairs":len(rows),
        "episodes":len(rows)*2,
        "mechanical_pass":mechanical_pass,
        "summary":overall,
        "by_opponent":by_opp,
        "gate_diagnostics":{
            "nonnegative_blocks":nonneg_blocks,
            "worst_block_score_delta":worst_block,
        },
        "failures":failures,
        "decision":decision,
        "seconds":time.perf_counter()-started,
        "rows":rows,
        "automatic_kaggle_submission":False,
    }
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
    print("READY_WOOL_RUNTIME_RESULT",json.dumps({
        "pairs":len(rows),
        "mechanical_pass":mechanical_pass,
        "summary":overall,
        "by_opponent":by_opp,
        "gate_diagnostics":result["gate_diagnostics"],
        "failures":len(failures),
        "decision":decision,
        "seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
