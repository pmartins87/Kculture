#!/usr/bin/env python3
"""Fresh broad runtime interaction gate for O-RW1 + O-TW1.

Compares exact hosted-faithful V47 under four variants from the same fresh
seed/opponent/seat contexts:
  BASE, O-RW1 only, O-TW1 only, and BOTH.

Offline only. No Kaggle submission. The gate asks whether the two independently
validated one-shot operators compose safely before any learned selector is involved.
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
    eligible as rw_eligible,
    treated_action as rw_treated_action,
)
from tools.first_party_town_wheat_deferral_causal_gate import (
    eligible as tw_eligible,
    treated_action as tw_treated_action,
)
from tools.option_value_dataset_ryzen_v2 import V2_OPPONENTS

EXPECTED_ENGINE = "1.32.7"
BASE = {
    "key": "v47",
    "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
SEEDS = list(range(71001, 71005))
VARIANTS = ("base", "rw1", "tw1", "both")


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


class OptionLibraryWrapper:
    def __init__(self, main_py: Path, *, use_rw: bool, use_tw: bool):
        self.agent = load_public_agent(main_py)
        self.use_rw = bool(use_rw)
        self.use_tw = bool(use_tw)
        self.rw_used = False
        self.tw_used = False
        self.rw_step = None
        self.tw_step = None
        self.trace: list[tuple[str, str]] = []

    @property
    def first_trigger_step(self):
        vals = [x for x in (self.rw_step, self.tw_step) if x is not None]
        return min(vals) if vals else None

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        self.trace.append((obs_hash(obs), action_key(base)))
        p = plain(obs)
        try:
            step = int(p.get("step", len(self.trace) - 1))
        except Exception:
            step = len(self.trace) - 1

        # The two frozen eligibility predicates are mutually exclusive in normal
        # operation (TW1 requires a WHEAT sale; RW1 requires empty market), but
        # use a deterministic priority anyway.
        if self.use_tw and not self.tw_used and tw_eligible(obs, config, base):
            out, removed = tw_treated_action(base)
            if removed <= 0:
                raise RuntimeError("O-TW1 eligible but removed no WHEAT sale")
            if out["farmer"] != base["farmer"] or out["hands"] != base["hands"]:
                raise RuntimeError("O-TW1 changed farmer/hands")
            self.tw_used = True
            self.tw_step = step
            return out

        if self.use_rw and not self.rw_used and rw_eligible(obs, base):
            out = rw_treated_action(base)
            if out["farmer"] != base["farmer"] or out["hands"] != base["hands"]:
                raise RuntimeError("O-RW1 changed farmer/hands")
            self.rw_used = True
            self.rw_step = step
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


def run_variant(base_main: Path, opp_main: Path, *, seed: int, seat: int, variant: str) -> dict:
    use_rw = variant in ("rw1", "both")
    use_tw = variant in ("tw1", "both")
    cand = OptionLibraryWrapper(base_main, use_rw=use_rw, use_tw=use_tw)
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
    out.update({
        "trace": cand.trace,
        "rw_used": cand.rw_used,
        "tw_used": cand.tw_used,
        "rw_step": cand.rw_step,
        "tw_step": cand.tw_step,
        "first_trigger_step": cand.first_trigger_step,
    })
    return out


def pretrigger_parity(base: dict, treatment: dict) -> dict:
    bt, tt = base["trace"], treatment["trace"]
    trigger = treatment["first_trigger_step"]
    if trigger is None:
        ok = bt == tt and base["rewards"] == treatment["rewards"]
        return {"ok": ok, "triggered": False, "checked_through_step": len(bt)-1}
    limit = min(int(trigger), len(bt)-1, len(tt)-1)
    for i in range(limit + 1):
        if bt[i] != tt[i]:
            return {"ok": False, "triggered": True, "mismatch_step": i, "trigger_step": trigger}
    return {"ok": True, "triggered": True, "checked_through_step": limit, "trigger_step": trigger}


def purge(paths: list[Path]) -> None:
    seen = set()
    for p in paths:
        k = str(p.parent.resolve())
        if k in seen:
            continue
        seen.add(k)
        purge_package_modules(p.parent)


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {}
    out = {"contexts": len(rows)}
    for v in VARIANTS:
        vals = [float(r[v]["score"]) for r in rows]
        margins = [float(r[v]["margin"]) for r in rows]
        out[v] = {
            "score_rate": statistics.mean(vals),
            "mean_margin": statistics.mean(margins),
        }
    out["combo_vs_base_score_delta"] = out["both"]["score_rate"] - out["base"]["score_rate"]
    out["rw1_vs_base_score_delta"] = out["rw1"]["score_rate"] - out["base"]["score_rate"]
    out["tw1_vs_base_score_delta"] = out["tw1"]["score_rate"] - out["base"]["score_rate"]
    out["combo_vs_best_single_mean_score_delta"] = (
        out["both"]["score_rate"] - max(out["rw1"]["score_rate"], out["tw1"]["score_rate"])
    )
    out["combo_positive_vs_base"] = sum(r["both"]["score"] > r["base"]["score"] for r in rows)
    out["combo_negative_vs_base"] = sum(r["both"]["score"] < r["base"]["score"] for r in rows)
    out["combo_better_than_both_singles"] = sum(
        r["both"]["score"] > max(r["rw1"]["score"], r["tw1"]["score"]) for r in rows
    )
    out["combo_worse_than_both_singles"] = sum(
        r["both"]["score"] < min(r["rw1"]["score"], r["tw1"]["score"]) for r in rows
    )
    out["rw_trigger_rate"] = statistics.mean(float(r["both"]["rw_used"]) for r in rows)
    out["tw_trigger_rate"] = statistics.mean(float(r["both"]["tw_used"]) for r in rows)
    out["both_trigger_rate"] = statistics.mean(
        float(r["both"]["rw_used"] and r["both"]["tw_used"]) for r in rows
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/option-library-combo-v0/OPTION_LIBRARY_COMBO_V0.json",
    )
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(f"engine mismatch: {getattr(kaggle_environments,'__version__',None)}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows, failures, provenance = [], [], {}
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="option-library-combo-v0-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")
            probe = load_public_agent(base_main)
            if getattr(probe, "__name__", None) != "_y_agent_shopherd":
                raise RuntimeError(f"unexpected V47 entrypoint: {getattr(probe,'__name__',None)}")
            purge_package_modules(base_main.parent)

            opp_paths = {}
            by_sha = {BASE["expected_main_sha256"]: base_main}
            for spec in V2_OPPONENTS:
                if spec["expected_main_sha256"] in by_sha:
                    opp_paths[spec["key"]] = by_sha[spec["expected_main_sha256"]]
                    provenance[spec["key"]] = {
                        **provenance["base"],
                        "key": spec["key"],
                        "family": spec.get("family"),
                        "reused_exact_base_bytes": True,
                    }
                else:
                    p, rec = acquire(spec, tmp / f"opp_{spec['key']}")
                    opp_paths[spec["key"]] = p
                    by_sha[spec["expected_main_sha256"]] = p
                    provenance[spec["key"]] = {**rec, "family": spec.get("family")}

            all_paths = [base_main, *opp_paths.values()]
            for spec in V2_OPPONENTS:
                opp_key = spec["key"]
                for seed in SEEDS:
                    for seat in (0, 1):
                        key = {"opponent": opp_key, "seed": seed, "seat": seat}
                        try:
                            results = {}
                            for variant in VARIANTS:
                                purge(all_paths)
                                results[variant] = run_variant(
                                    base_main, opp_paths[opp_key],
                                    seed=seed, seat=seat, variant=variant,
                                )
                            parities = {
                                v: pretrigger_parity(results["base"], results[v])
                                for v in ("rw1", "tw1", "both")
                            }
                            if not all(x["ok"] for x in parities.values()):
                                raise RuntimeError(f"pretrigger parity failure: {parities}")
                            row = {**key, **results, "parity": parities}
                            rows.append(row)
                            print("OPTION_LIBRARY_COMBO_PAIR", json.dumps({
                                **key,
                                "scores": {v: results[v]["score"] for v in VARIANTS},
                                "both_rw": results["both"]["rw_used"],
                                "both_tw": results["both"]["tw_used"],
                            }, sort_keys=True), flush=True)
                        except Exception as exc:
                            failures.append({**key, "error": f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge(all_paths)
    except Exception as exc:
        failures.append({"phase": "setup", "error": f"{type(exc).__name__}: {exc}"})

    overall = summarize(rows)
    by_opp = {
        spec["key"]: summarize([r for r in rows if r["opponent"] == spec["key"]])
        for spec in V2_OPPONENTS
    }
    expected = len(V2_OPPONENTS) * len(SEEDS) * 2
    mechanical_pass = (
        not failures
        and len(rows) == expected
        and all(all(x["ok"] for x in r["parity"].values()) for r in rows)
    )
    nonnegative_blocks = sum(
        1 for x in by_opp.values()
        if x and float(x.get("combo_vs_base_score_delta", 0.0)) >= 0.0
    )
    worst_block = min(
        (float(x.get("combo_vs_base_score_delta", 0.0)) for x in by_opp.values() if x),
        default=-1.0,
    )

    combo_delta = float(overall.get("combo_vs_base_score_delta", 0.0))
    combo_vs_best = float(overall.get("combo_vs_best_single_mean_score_delta", 0.0))
    if mechanical_pass and combo_delta > 0 and combo_vs_best >= 0 and nonnegative_blocks >= 6:
        decision = "OPTION_LIBRARY_COMBO_ADVANCE"
    elif mechanical_pass and combo_delta > 0 and worst_block >= -0.0625:
        decision = "OPTION_LIBRARY_COMBO_SAFE_BUT_NO_INCREMENT"
    elif mechanical_pass and combo_delta > 0:
        decision = "OPTION_LIBRARY_COMBO_HETEROGENEOUS"
    elif mechanical_pass:
        decision = "OPTION_LIBRARY_COMBO_NO_GAIN"
    else:
        decision = "OPTION_LIBRARY_COMBO_MECHANICS_INVALID"

    result = {
        "schema": "kculture-option-library-combo-runtime-v0",
        "engine": EXPECTED_ENGINE,
        "base": BASE,
        "opponents": V2_OPPONENTS,
        "seeds": SEEDS,
        "variants": VARIANTS,
        "rows": rows,
        "contexts": len(rows),
        "mechanical_pass": mechanical_pass,
        "summary": overall,
        "by_opponent": by_opp,
        "gate_diagnostics": {
            "nonnegative_combo_blocks": nonnegative_blocks,
            "worst_combo_block_score_delta": worst_block,
        },
        "provenance": provenance,
        "failures": failures,
        "decision": decision,
        "seconds": time.perf_counter() - started,
        "automatic_kaggle_submission": False,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OPTION_LIBRARY_COMBO_RESULT", json.dumps({
        "decision": decision,
        "mechanical_pass": mechanical_pass,
        "summary": overall,
        "by_opponent": by_opp,
        "failures": len(failures),
        "seconds": result["seconds"],
    }, sort_keys=True), flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
