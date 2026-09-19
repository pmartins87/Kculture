#!/usr/bin/env python3
"""Ryzen V2 option-value generator over a diverse seven-agent public league.

Uses the exact V1 state/option feature contract and counterfactual mechanics, but expands
the opponent population. One atomic shard per seed; safe to resume; never submits to
Kaggle.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.option_value_dataset_v0_pilot import (
    BASE,
    EXPECTED_ENGINE,
    MODEL_FEATURE_NAMES,
    acquire,
)
from tools.option_value_dataset_ryzen_v1 import (
    _aggregate,
    _git_head,
    _make_seeds,
    _run_seed,
    _stable_json_hash,
    _write_json_atomic,
)

V2_OPPONENTS = [
    {
        "key":"v47_mirror",
        "handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
        "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
        "family":"modern41_v47",
    },
    {
        "key":"ready_stock",
        "handle":"alperen5252525/kaggriculture-ready-stock-earlier-sales",
        "expected_main_sha256":"45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017",
        "family":"modern41_ready_stock",
    },
    {
        "key":"v48",
        "handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
        "expected_main_sha256":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
        "family":"modern41_queue",
    },
    {
        "key":"router_2715",
        "handle":"nusrati/2715-6",
        "expected_main_sha256":"66585d1a5dbfe11c946a3c400278592f860342bc4a8f5e5f87f2a9293348984b",
        "family":"multi_program_router",
    },
    {
        "key":"conditional_memory",
        "handle":"ravi123a321at/177-180-fresh-top-30-v21-1-conditional-memory",
        "expected_main_sha256":"d9dc24ce5429ec628ead0621a160bee90725350683d7dfcc4686fcaf511f3aab",
        "family":"literal_conditional_memory",
    },
    {
        "key":"tactical_memory",
        "handle":"web3cainiao/kaggriculture-v21-tactical-memory",
        "expected_main_sha256":"630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054",
        "family":"literal_tactical_memory",
    },
    {
        "key":"best_market",
        "handle":"reyhanksatria/best-market-agent-high-strategy",
        "expected_main_sha256":"d39dba50793d9777c990347443bf0c481c78adaea86055f6f6b0600dcfcd9f2e",
        "family":"literal_market_strategy",
    },
]
DEFAULT_OPPONENTS = tuple(x["key"] for x in V2_OPPONENTS)


def source_manifest(run_dir: Path, selected_opponents: tuple[str, ...]) -> dict:
    sources = run_dir / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    provenance = {}

    base_main, rec = acquire(BASE, sources / "base")
    provenance["base"] = rec
    paths = {"base": str(base_main.resolve())}

    specs = {x["key"]: x for x in V2_OPPONENTS}
    for key in selected_opponents:
        spec = specs[key]
        if spec["expected_main_sha256"] == BASE["expected_main_sha256"]:
            paths[key] = str(base_main.resolve())
            provenance[key] = {
                **rec,
                "key": key,
                "family": spec["family"],
                "role": "opponent",
                "reused_exact_base_bytes": True,
            }
        else:
            p, orec = acquire(spec, sources / f"opp_{key}")
            paths[key] = str(p.resolve())
            provenance[key] = {
                **orec,
                "family": spec["family"],
            }

    return {"paths": paths, "provenance": provenance}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/option_value_v2_150")
    ap.add_argument("--seed-count", type=int, default=150)
    ap.add_argument("--master-seed", type=int, default=26091902)
    ap.add_argument("--opponents", default=",".join(DEFAULT_OPPONENTS))
    ap.add_argument("--seats", default="0,1")
    ap.add_argument("--workers", type=int, default=max(1,(os.cpu_count() or 8)-2))
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__","")) != EXPECTED_ENGINE:
        raise SystemExit(
            f"engine mismatch: {getattr(kaggle_environments,'__version__',None)}"
        )

    selected = tuple(x.strip() for x in args.opponents.split(",") if x.strip())
    unknown = sorted(set(selected)-set(DEFAULT_OPPONENTS))
    if unknown:
        raise SystemExit(f"unknown V2 opponents: {unknown}")
    seats = tuple(int(x.strip()) for x in args.seats.split(",") if x.strip())
    if not seats or any(x not in (0,1) for x in seats):
        raise SystemExit(f"invalid seats: {seats}")

    out_dir=(ROOT/args.out).resolve()
    out_dir.mkdir(parents=True,exist_ok=True)
    shards=out_dir/"shards"
    shards.mkdir(parents=True,exist_ok=True)

    sources=source_manifest(out_dir,selected)
    seeds=_make_seeds(args.seed_count,args.master_seed)
    manifest={
        "schema":"kculture-option-value-dataset-ryzen-v2-manifest",
        "source_commit":_git_head(),
        "engine":EXPECTED_ENGINE,
        "seed_count":int(args.seed_count),
        "master_seed":int(args.master_seed),
        "opponents":list(selected),
        "opponent_families":{x["key"]:x["family"] for x in V2_OPPONENTS if x["key"] in selected},
        "seats":list(seats),
        "options":["O-RW1","O-TW1"],
        "model_feature_names":list(MODEL_FEATURE_NAMES),
        "hosted_entrypoint":"_y_agent_shopherd",
        "provenance":sources["provenance"],
    }
    manifest["config_sha256"]=_stable_json_hash(manifest)

    mp=out_dir/"MANIFEST.json"
    if mp.exists():
        old=json.loads(mp.read_text(encoding="utf-8"))
        if old.get("config_sha256") != manifest["config_sha256"]:
            raise SystemExit(f"refusing incompatible resume in {out_dir}")
    else:
        _write_json_atomic(mp,manifest)

    pending=[s for s in seeds if not (shards/f"seed_{s}.json").exists()]
    done_before=len(seeds)-len(pending)
    print("OPTION_VALUE_RYZEN_V2_START",json.dumps({
        "seed_count":len(seeds),
        "resume_done":done_before,
        "pending":len(pending),
        "workers":int(args.workers),
        "opponents":selected,
        "seats":seats,
        "max_rows":len(seeds)*len(selected)*len(seats)*2,
        "out":str(out_dir),
    },sort_keys=True),flush=True)

    start=time.time()
    if pending:
        common={"paths":sources["paths"],"opponents":selected,"seats":seats}
        with ProcessPoolExecutor(max_workers=max(1,int(args.workers))) as ex:
            futs={ex.submit(_run_seed,{"seed":s,**common}):s for s in pending}
            completed=done_before
            for fut in as_completed(futs):
                seed=futs[fut]
                try:
                    result=fut.result()
                except Exception as exc:
                    result={
                        "seed":seed,
                        "rows":[],
                        "matchups":[],
                        "failures":[{"seed":seed,"exception":repr(exc)}],
                    }
                _write_json_atomic(shards/f"seed_{seed}.json",result)
                completed += 1
                if completed % 5 == 0 or completed == len(seeds):
                    elapsed=max(1.0,time.time()-start)
                    rate=max(0.0,(completed-done_before)/elapsed)
                    rows_so_far=sum(
                        len(json.loads(p.read_text(encoding="utf-8")).get("rows",[]))
                        for p in shards.glob("seed_*.json")
                    )
                    print("OPTION_VALUE_RYZEN_V2_PROGRESS",json.dumps({
                        "seeds":f"{completed}/{len(seeds)}",
                        "new_seed_rate_per_s":rate,
                        "rows_so_far":rows_so_far,
                    },sort_keys=True),flush=True)

    summary=_aggregate(out_dir,manifest)
    summary["schema"]="kculture-option-value-dataset-ryzen-v2-summary"
    _write_json_atomic(out_dir/"SUMMARY.json",summary)
    print("OPTION_VALUE_RYZEN_V2_DONE",json.dumps({
        "completed_seeds":summary["completed_seeds"],
        "rows":summary["rows"],
        "unique_state_hashes":summary["unique_state_hashes"],
        "failures":len(summary["failures"]),
        "rows_by_option":summary["rows_by_option"],
        "rows_by_opponent":summary["rows_by_opponent"],
        "out":str(out_dir),
    },sort_keys=True),flush=True)
    if summary["failures"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
