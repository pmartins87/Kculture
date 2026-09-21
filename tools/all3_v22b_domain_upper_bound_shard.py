#!/usr/bin/env python3
"""V22B fresh-frontier domain upper-bound shard over frozen V22A hard contexts."""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.programme_adaptive_expert_gate import (
    EXPECTED_ENGINE,
    acquire_public_main,
    load_public_agent,
    purge_package_modules,
    sha256_bytes,
)
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent, canonical_action, score
from tools.first_party_option_host_v1 import OptionHostState, apply_option_host

MODES = ("BASE", "MARKET_ONLY", "PHYSICAL_ONLY", "FULL_SHADOW")


def acquire_exact(ref, expected, tmp, attempts=8):
    last = None
    for i in range(attempts):
        try:
            main, receipt = acquire_public_main(ref, tmp / f"try{i}")
            h = sha256_bytes(main.read_bytes())
            if h != expected:
                raise RuntimeError(f"source SHA drift {h} != {expected}")
            return main, receipt
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                # Mechanical retry hardening for transient Kaggle HTTP 429 only.
                # Does not alter source identity, context population, modes, or gate.
                time.sleep(min(60.0, 5.0 * (2 ** i)))
    raise last


def hand_diff_count(a, b):
    aa = list(a or [])
    bb = list(b or [])
    n = max(len(aa), len(bb))
    return sum(
        (aa[i] if i < len(aa) else None) != (bb[i] if i < len(bb) else None)
        for i in range(n)
    )


class HybridCandidate:
    def __init__(self, base_main, teacher_main, mode):
        purge_package_modules(base_main.parent)
        purge_package_modules(teacher_main.parent)
        self.base = load_public_agent(base_main)
        purge_package_modules(teacher_main.parent)
        self.teacher = None if mode == "BASE" else load_public_agent(teacher_main)
        self.state = OptionHostState()
        self.mode = mode
        self.stats = {
            "turns": 0,
            "market_diff_turns": 0,
            "farmer_diff_turns": 0,
            "hand_diff_total": 0,
            "hybrid_changed_turns": 0,
            "teacher_evaluations": 0,
        }

    def __call__(self, obs, config=None):
        self.stats["turns"] += 1
        exact = canonical_action(call_agent(self.base, obs, config))
        all3 = apply_option_host(
            obs,
            config,
            exact,
            self.state,
            use_rw=True,
            use_tw=True,
            use_lq2=True,
        )
        if self.mode == "BASE":
            return all3

        shadow = canonical_action(call_agent(self.teacher, obs, config))
        self.stats["teacher_evaluations"] += 1

        if all3.get("market") != shadow.get("market"):
            self.stats["market_diff_turns"] += 1
        if all3.get("farmer") != shadow.get("farmer"):
            self.stats["farmer_diff_turns"] += 1
        self.stats["hand_diff_total"] += hand_diff_count(all3.get("hands"), shadow.get("hands"))

        if self.mode == "MARKET_ONLY":
            out = copy.deepcopy(all3)
            out["market"] = copy.deepcopy(shadow.get("market") or [])
        elif self.mode == "PHYSICAL_ONLY":
            out = copy.deepcopy(all3)
            out["farmer"] = copy.deepcopy(shadow.get("farmer"))
            out["hands"] = copy.deepcopy(shadow.get("hands") or [])
        elif self.mode == "FULL_SHADOW":
            out = copy.deepcopy(shadow)
        else:
            raise RuntimeError(f"unknown mode {self.mode}")

        if out != all3:
            self.stats["hybrid_changed_turns"] += 1
        return out


def load_independent(main_py):
    purge_package_modules(main_py.parent)
    return load_public_agent(main_py)


def run_one(base_main, teacher_main, ctx, mode):
    cand = HybridCandidate(base_main, teacher_main, mode)
    opp = load_independent(teacher_main)
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(ctx["seed"])},
        debug=False,
    )
    t0 = time.perf_counter()
    if int(ctx["seat"]) == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    secs = time.perf_counter() - t0

    p = env.toJSON()
    statuses = [str(x) for x in p.get("statuses", [])]
    rewards = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    if (
        statuses != ["DONE", "DONE"]
        or len(rewards) != 2
        or steps < 720
        or not all(math.isfinite(x) for x in rewards)
    ):
        raise RuntimeError(
            f"invalid episode mode={mode} statuses={statuses} rewards={rewards} steps={steps}"
        )

    mine, other = (
        (rewards[0], rewards[1])
        if int(ctx["seat"]) == 0
        else (rewards[1], rewards[0])
    )
    margin = mine - other
    return {
        "score": float(score(margin)),
        "margin": float(margin),
        "result": "W" if margin > 0 else ("L" if margin < 0 else "T"),
        "rewards": rewards,
        "steps": steps,
        "seconds": secs,
        "diff_stats": cand.stats,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hard-config", required=True)
    ap.add_argument("--shard-index", type=int, required=True)
    ap.add_argument("--num-shards", type=int, default=4)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    cfg = json.loads(Path(args.hard_config).read_text())
    contexts = list(cfg.get("hard_contexts") or [])
    selected = [(i, c) for i, c in enumerate(contexts) if i % args.num_shards == args.shard_index]

    rows = []
    failures = []
    provenance = {}
    started = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix=f"v22b-s{args.shard_index}-") as td:
        root = Path(td)

        try:
            base_main, base_receipt = acquire_exact(
                BASE["handle"],
                BASE["expected_main_sha256"],
                root / "base",
            )
            provenance["base"] = {
                "ref": BASE["handle"],
                "sha": BASE["expected_main_sha256"],
                "receipt": base_receipt,
            }
        except Exception as exc:
            base_main = None
            failures.append(
                {"phase": "base_acquire", "error": f"{type(exc).__name__}: {exc}"}
            )

        teachers = {}
        if base_main is not None:
            for _idx, ctx in selected:
                sha = str(ctx["main_sha256"])
                if sha in teachers:
                    continue
                try:
                    main, receipt = acquire_exact(
                        str(ctx["ref"]),
                        sha,
                        root / f"teacher_{len(teachers)}",
                    )
                    teachers[sha] = main
                    provenance[sha] = {
                        "ref": ctx["ref"],
                        "sha": sha,
                        "receipt": receipt,
                    }
                except Exception as exc:
                    failures.append(
                        {
                            "phase": "teacher_acquire",
                            "context_id": ctx.get("context_id"),
                            "ref": ctx.get("ref"),
                            "sha": sha,
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )

        for key in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"):
            os.environ.pop(key, None)

        if base_main is not None:
            for _idx, ctx in selected:
                teacher = teachers.get(str(ctx["main_sha256"]))
                if teacher is None:
                    continue

                base_result = None
                for mode in MODES:
                    try:
                        purge_package_modules(base_main.parent)
                        purge_package_modules(teacher.parent)
                        rr = run_one(base_main, teacher, ctx, mode)

                        if mode == "BASE":
                            if (
                                float(rr["score"]) != float(ctx["base_score"])
                                or float(rr["margin"]) != float(ctx["base_margin"])
                            ):
                                raise RuntimeError(
                                    "BASE replay mismatch "
                                    f"{(rr['score'], rr['margin'])} != "
                                    f"{(ctx['base_score'], ctx['base_margin'])}"
                                )
                            base_result = rr

                        if base_result is None:
                            raise RuntimeError("BASE must run first")

                        row = {
                            "context_id": ctx["context_id"],
                            "source_rank": ctx.get("rank"),
                            "ref": ctx["ref"],
                            "main_sha256": ctx["main_sha256"],
                            "seed": int(ctx["seed"]),
                            "seat": int(ctx["seat"]),
                            "mode": mode,
                            "base_score": float(base_result["score"]),
                            "treatment_score": float(rr["score"]),
                            "score_delta": float(rr["score"]) - float(base_result["score"]),
                            "base_margin": float(base_result["margin"]),
                            "treatment_margin": float(rr["margin"]),
                            "margin_delta": float(rr["margin"]) - float(base_result["margin"]),
                            "diff_stats": rr["diff_stats"],
                        }
                        rows.append(row)
                        print(
                            "V22B_MODE",
                            json.dumps(
                                {k: row[k] for k in (
                                    "context_id", "source_rank", "seed", "seat",
                                    "mode", "score_delta", "margin_delta"
                                )},
                                sort_keys=True,
                            ),
                            flush=True,
                        )
                    except Exception as exc:
                        failures.append(
                            {
                                "phase": "episode",
                                "context_id": ctx["context_id"],
                                "mode": mode,
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                        )

    expected = len(selected) * len(MODES)
    mechanical_pass = not failures and len(rows) == expected

    result = {
        "schema": "kculture-all3-v22b-domain-upper-bound-shard-v1",
        "engine": EXPECTED_ENGINE,
        "mechanical_pass": mechanical_pass,
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
        "contexts_assigned": len(selected),
        "expected_rows": expected,
        "rows": rows,
        "failures": failures,
        "provenance": provenance,
        "credentials_removed_before_third_party_execution": True,
        "third_party_code_persisted": False,
        "automatic_kaggle_submission": False,
        "seconds": time.perf_counter() - started,
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(
        "V22B_SHARD_RESULT",
        json.dumps(
            {
                "shard": args.shard_index,
                "mechanical_pass": mechanical_pass,
                "contexts": len(selected),
                "rows": len(rows),
                "failures": len(failures),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
