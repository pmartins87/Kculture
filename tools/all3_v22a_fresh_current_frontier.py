#!/usr/bin/env python3
"""V22A fresh current-frontier hard-population refresh.

Read-only/current-frontier discovery:
1) list current Kaggriculture Top-30 by score;
2) acquire public packages transiently and deduplicate exact main.py bytes;
3) remove Kaggle credentials before executing third-party code;
4) smoke-test each unique source in both seats;
5) choose up to 12 unique executable sources by current representative rank only;
6) run exact ALL3 on untouched seeds 79101..79106 in both seats.

No third-party source is persisted. No Kaggle submission.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.kaggle_meta_scout_cli import csv_rows, normkey
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

DISCOVERY_SEEDS = (79101, 79102, 79103, 79104, 79105, 79106)
SEATS = (0, 1)
TOP_N = 30
MAX_REPS = 12
MIN_REPS = 8
SMOKE_SEED = 79100


def ref_value(row):
    for k, v in row.items():
        if normkey(k) == "ref" and str(v).strip():
            return str(v).strip()
    for _k, v in row.items():
        s = str(v or "").strip()
        if "/" in s and " " not in s:
            return s
    return None


def list_current_top30():
    cmd = [
        "kaggle", "kernels", "list",
        "--competition", "kaggriculture",
        "--sort-by", "scoreDescending",
        "--page-size", "100",
        "-v",
    ]
    p = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if p.returncode != 0:
        raise RuntimeError(f"kaggle kernels list failed rc={p.returncode}: {p.stderr[-4000:]}")
    rows = csv_rows(p.stdout)
    refs = []
    seen = set()
    for row in rows:
        ref = ref_value(row)
        if ref and ref not in seen:
            seen.add(ref)
            refs.append(ref)
        if len(refs) >= TOP_N:
            break
    if len(refs) != TOP_N:
        raise RuntimeError(f"expected current Top-{TOP_N}, got {len(refs)}")
    return refs, p.stdout


def acquire_retry(ref: str, target: Path, attempts: int = 5):
    last = None
    for i in range(attempts):
        try:
            main_py, receipt = acquire_public_main(ref, target / f"a{i}")
            data = main_py.read_bytes()
            return main_py, sha256_bytes(data), receipt
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(1.5 * (i + 1))
    raise last


def acquire_expected_retry(ref: str, expected_sha: str, target: Path, attempts: int = 5):
    last = None
    for i in range(attempts):
        try:
            main_py, sha, receipt = acquire_retry(ref, target / f"outer{i}", attempts=1)
            if sha != expected_sha:
                raise RuntimeError(f"source SHA drift {sha} != {expected_sha}")
            return main_py, receipt
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(1.5 * (i + 1))
    raise last


def run_smoke(main_py: Path, seat: int):
    purge_package_modules(main_py.parent)
    agent = load_public_agent(main_py)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": SMOKE_SEED}, debug=False)
    t0 = time.perf_counter()
    if seat == 0:
        env.run([agent, "starter"])
    else:
        env.run(["starter", agent])
    secs = time.perf_counter() - t0
    p = env.toJSON()
    statuses = [str(x) for x in p.get("statuses", [])]
    rewards = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    ok = (
        statuses == ["DONE", "DONE"]
        and len(rewards) == 2
        and steps >= 720
        and all(math.isfinite(x) for x in rewards)
    )
    return {
        "seat": seat,
        "ok": ok,
        "statuses": statuses,
        "rewards": rewards,
        "steps": steps,
        "seconds": secs,
    }


class All3:
    def __init__(self, base_main: Path):
        self.agent = load_public_agent(base_main)
        self.state = OptionHostState()

    def __call__(self, obs, config=None):
        base = canonical_action(call_agent(self.agent, obs, config))
        return apply_option_host(
            obs,
            config,
            base,
            self.state,
            use_rw=True,
            use_tw=True,
            use_lq2=True,
        )


def run_all3(base_main: Path, opp_main: Path, seed: int, seat: int):
    purge_package_modules(base_main.parent)
    purge_package_modules(opp_main.parent)
    cand = All3(base_main)
    opp = load_public_agent(opp_main)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    t0 = time.perf_counter()
    if seat == 0:
        env.run([cand, opp])
    else:
        env.run([opp, cand])
    secs = time.perf_counter() - t0
    p = env.toJSON()
    statuses = [str(x) for x in p.get("statuses", [])]
    rewards = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    if statuses != ["DONE", "DONE"] or len(rewards) != 2 or steps < 720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine, other = (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])
    margin = mine - other
    return {
        "score": float(score(margin)),
        "margin": float(margin),
        "result": "W" if margin > 0 else ("L" if margin < 0 else "T"),
        "rewards": rewards,
        "steps": steps,
        "seconds": secs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True)
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(
            f"engine mismatch {getattr(kaggle_environments, '__version__', None)} != {EXPECTED_ENGINE}"
        )

    started = time.perf_counter()
    out_path = Path(args.out)
    raw_path = Path(args.raw)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    acquisition_failures = []
    smoke_failures = []
    episode_failures = []
    acquisitions = []
    unique_rows = []
    rows = []

    try:
        refs, raw = list_current_top30()
        raw_path.write_text(raw, encoding="utf-8")
    except Exception as exc:
        result = {
            "schema": "kculture-all3-v22a-fresh-current-frontier-v1",
            "mechanical_pass": False,
            "decision": "V22A_MECHANICS_INVALID",
            "error": f"{type(exc).__name__}: {exc}",
            "automatic_kaggle_submission": False,
        }
        out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("V22A_RESULT", json.dumps(result, sort_keys=True))
        raise SystemExit(2)

    with tempfile.TemporaryDirectory(prefix="v22a-frontier-") as td:
        tmp = Path(td)
        by_sha = {}

        for rank, ref in enumerate(refs, start=1):
            try:
                main_py, sha, receipt = acquire_retry(ref, tmp / f"rank{rank:02d}")
                rec = {
                    "rank": rank,
                    "ref": ref,
                    "status": "ACQUIRED",
                    "main_sha256": sha,
                    "main_bytes": main_py.stat().st_size,
                    "receipt": receipt,
                }
                acquisitions.append(rec)
                meta = by_sha.setdefault(
                    sha,
                    {"main": main_py, "ranks": [], "refs": []},
                )
                meta["ranks"].append(rank)
                meta["refs"].append(ref)
                print(
                    "V22A_ACQUIRE",
                    json.dumps({"rank": rank, "ref": ref, "main_sha256": sha}, sort_keys=True),
                    flush=True,
                )
            except Exception as exc:
                rec = {
                    "rank": rank,
                    "ref": ref,
                    "status": "ACQUIRE_FAIL",
                    "error": f"{type(exc).__name__}: {exc}",
                }
                acquisitions.append(rec)
                acquisition_failures.append(rec)
                print("V22A_ACQUIRE_FAIL", json.dumps(rec, sort_keys=True), flush=True)

        try:
            base_main, base_receipt = acquire_expected_retry(
                BASE["handle"],
                BASE["expected_main_sha256"],
                tmp / "all3-base",
            )
        except Exception as exc:
            base_main = None
            base_receipt = None
            episode_failures.append(
                {"phase": "base_acquire", "error": f"{type(exc).__name__}: {exc}"}
            )

        removed_credentials = []
        for key in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"):
            if key in os.environ:
                removed_credentials.append(key)
                os.environ.pop(key, None)

        for sha, meta in sorted(by_sha.items(), key=lambda kv: min(kv[1]["ranks"])):
            smokes = []
            err = None
            for seat in SEATS:
                try:
                    smokes.append(run_smoke(meta["main"], seat))
                except Exception as exc:
                    err = f"{type(exc).__name__}: {exc}"
                    smokes.append({"seat": seat, "ok": False, "error": err})
                finally:
                    purge_package_modules(meta["main"].parent)
            pass_both = len(smokes) == 2 and all(bool(x.get("ok")) for x in smokes)
            rep_rank = min(meta["ranks"])
            rep_ref = meta["refs"][meta["ranks"].index(rep_rank)]
            row = {
                "main_sha256": sha,
                "ranks": sorted(meta["ranks"]),
                "refs": list(meta["refs"]),
                "representative_rank": rep_rank,
                "representative_ref": rep_ref,
                "source_bytes": meta["main"].stat().st_size,
                "smoke": smokes,
                "smoke_pass_both_seats": pass_both,
                "is_v47_base_identity": sha == BASE["expected_main_sha256"],
            }
            unique_rows.append(row)
            if not pass_both:
                smoke_failures.append(
                    {"sha": sha, "representative_ref": rep_ref, "error": err or "smoke_not_done"}
                )
            print(
                "V22A_SMOKE",
                json.dumps(
                    {
                        "sha": sha,
                        "rank": rep_rank,
                        "ref": rep_ref,
                        "pass_both": pass_both,
                        "is_v47_base_identity": row["is_v47_base_identity"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

        eligible = [
            x for x in unique_rows
            if x["smoke_pass_both_seats"] and not x["is_v47_base_identity"]
        ]
        eligible.sort(key=lambda x: (int(x["representative_rank"]), x["main_sha256"]))
        selected = eligible[:MAX_REPS]

        selected_paths = {
            x["main_sha256"]: by_sha[x["main_sha256"]]["main"] for x in selected
        }

        if base_main is not None and len(selected) >= MIN_REPS:
            for rep in selected:
                opp_main = selected_paths[rep["main_sha256"]]
                for seed in DISCOVERY_SEEDS:
                    for seat in SEATS:
                        try:
                            rr = run_all3(base_main, opp_main, seed, seat)
                            row = {
                                "rank": int(rep["representative_rank"]),
                                "ref": rep["representative_ref"],
                                "main_sha256": rep["main_sha256"],
                                "seed": int(seed),
                                "seat": int(seat),
                                **rr,
                            }
                            rows.append(row)
                            print(
                                "V22A_EPISODE",
                                json.dumps(
                                    {k: row[k] for k in (
                                        "rank", "ref", "main_sha256",
                                        "seed", "seat", "result", "score", "margin"
                                    )},
                                    sort_keys=True,
                                ),
                                flush=True,
                            )
                        except Exception as exc:
                            failure = {
                                "phase": "episode",
                                "rank": int(rep["representative_rank"]),
                                "ref": rep["representative_ref"],
                                "sha": rep["main_sha256"],
                                "seed": int(seed),
                                "seat": int(seat),
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                            episode_failures.append(failure)
                            print("V22A_EPISODE_FAIL", json.dumps(failure, sort_keys=True), flush=True)
                        finally:
                            purge_package_modules(base_main.parent)
                            purge_package_modules(opp_main.parent)

    expected = len(selected) * len(DISCOVERY_SEEDS) * len(SEATS)
    unique_context_keys = {
        (r["main_sha256"], int(r["seed"]), int(r["seat"])) for r in rows
    }
    hard = [r for r in rows if float(r["score"]) < 1.0]
    hard_shas = sorted({r["main_sha256"] for r in hard})
    hard_seeds = sorted({int(r["seed"]) for r in hard})

    mechanical_pass = (
        len(refs) == TOP_N
        and base_main is not None
        and not acquisition_failures
        and not smoke_failures
        and len(selected) >= MIN_REPS
        and expected >= 96
        and len(rows) == expected
        and len(unique_context_keys) == expected
        and not episode_failures
    )

    if not mechanical_pass:
        decision = "V22A_MECHANICS_INVALID"
    elif len(hard) >= 12 and len(hard_shas) >= 4 and len(hard_seeds) >= 3:
        decision = "V22A_FRESH_FRONTIER_HARD_POPULATION_READY"
    else:
        decision = "V22A_FRESH_FRONTIER_TOO_EASY_REFRESH_LATER"

    by_source = []
    for rep in selected:
        rr = [x for x in rows if x["main_sha256"] == rep["main_sha256"]]
        if rr:
            by_source.append(
                {
                    "rank": int(rep["representative_rank"]),
                    "ref": rep["representative_ref"],
                    "sha": rep["main_sha256"],
                    "games": len(rr),
                    "wins": sum(x["result"] == "W" for x in rr),
                    "losses": sum(x["result"] == "L" for x in rr),
                    "ties": sum(x["result"] == "T" for x in rr),
                    "score_rate": sum(float(x["score"]) for x in rr) / len(rr),
                    "mean_margin": sum(float(x["margin"]) for x in rr) / len(rr),
                }
            )

    result = {
        "schema": "kculture-all3-v22a-fresh-current-frontier-v1",
        "engine": EXPECTED_ENGINE,
        "decision": decision,
        "mechanical_pass": mechanical_pass,
        "current_top30_refs": refs,
        "discovery_seeds": list(DISCOVERY_SEEDS),
        "seats": list(SEATS),
        "top30_refs_acquired": sum(x.get("status") == "ACQUIRED" for x in acquisitions),
        "top30_acquisition_failures": acquisition_failures,
        "unique_sources_acquired": len(unique_rows),
        "unique_sources_smoke_pass_both": sum(x["smoke_pass_both_seats"] for x in unique_rows),
        "unique_sources_excluding_v47": len(eligible),
        "selected_representatives": selected,
        "selected_representative_count": len(selected),
        "base": {
            "handle": BASE["handle"],
            "expected_main_sha256": BASE["expected_main_sha256"],
            "receipt": base_receipt,
        },
        "expected_games": expected,
        "completed_games": len(rows),
        "hard_contexts": len(hard),
        "hard_source_shas": hard_shas,
        "hard_seeds": hard_seeds,
        "by_source": by_source,
        "hard_rows": hard,
        "rows": rows,
        "smoke_failures": smoke_failures,
        "episode_failures": episode_failures,
        "credentials_removed_before_third_party_execution": removed_credentials,
        "third_party_code_persisted": False,
        "rank_used_only_for_offline_sampling": True,
        "opponent_identity_runtime_feature": False,
        "local_h2h_is_not_hosted_rating_estimator": True,
        "automatic_kaggle_submission": False,
        "seconds": time.perf_counter() - started,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        "V22A_RESULT",
        json.dumps(
            {
                "decision": decision,
                "mechanical_pass": mechanical_pass,
                "selected_representatives": len(selected),
                "expected_games": expected,
                "completed_games": len(rows),
                "hard_contexts": len(hard),
                "hard_sources": len(hard_shas),
                "hard_seeds": len(hard_seeds),
                "acquisition_failures": len(acquisition_failures),
                "smoke_failures": len(smoke_failures),
                "episode_failures": len(episode_failures),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
