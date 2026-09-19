#!/usr/bin/env python3
"""One-opponent shard for the frozen O-RW1/O-TW1 composition gate."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.option_library_combo_runtime_v0 import (
    EXPECTED_ENGINE,
    BASE,
    SEEDS,
    VARIANTS,
    V2_OPPONENTS,
    acquire,
    run_variant,
    pretrigger_parity,
    summarize,
    purge,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(f"engine mismatch: {getattr(kaggle_environments,'__version__',None)}")

    specs = {x["key"]: x for x in V2_OPPONENTS}
    if args.opponent not in specs:
        raise SystemExit(f"unknown opponent {args.opponent}")
    spec = specs[args.opponent]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows, failures, provenance = [], [], {}
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix=f"combo-shard-{args.opponent}-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")
            probe = __import__("tools.programme_adaptive_expert_gate", fromlist=["load_public_agent"]).load_public_agent(base_main)
            if getattr(probe, "__name__", None) != "_y_agent_shopherd":
                raise RuntimeError(f"unexpected V47 entrypoint: {getattr(probe,'__name__',None)}")
            __import__("tools.programme_adaptive_expert_gate", fromlist=["purge_package_modules"]).purge_package_modules(base_main.parent)

            if spec["expected_main_sha256"] == BASE["expected_main_sha256"]:
                opp_main = base_main
                provenance["opponent"] = {
                    **provenance["base"],
                    "key": spec["key"],
                    "family": spec.get("family"),
                    "reused_exact_base_bytes": True,
                }
            else:
                opp_main, rec = acquire(spec, tmp / f"opp_{spec['key']}")
                provenance["opponent"] = {**rec, "family": spec.get("family")}

            all_paths = [base_main, opp_main]
            for seed in SEEDS:
                for seat in (0, 1):
                    key = {"opponent": spec["key"], "seed": seed, "seat": seat}
                    try:
                        results = {}
                        for variant in VARIANTS:
                            purge(all_paths)
                            results[variant] = run_variant(
                                base_main, opp_main, seed=seed, seat=seat, variant=variant
                            )
                        parities = {
                            v: pretrigger_parity(results["base"], results[v])
                            for v in ("rw1", "tw1", "both")
                        }
                        if not all(x["ok"] for x in parities.values()):
                            raise RuntimeError(f"pretrigger parity failure: {parities}")
                        rows.append({**key, **results, "parity": parities})
                    except Exception as exc:
                        failures.append({**key, "error": f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(all_paths)
    except Exception as exc:
        failures.append({"phase": "setup", "error": f"{type(exc).__name__}: {exc}"})

    summary = summarize(rows)
    expected = len(SEEDS) * 2
    mechanical_pass = (
        not failures
        and len(rows) == expected
        and all(all(x["ok"] for x in r["parity"].values()) for r in rows)
    )
    result = {
        "schema": "kculture-option-library-combo-runtime-v0-shard",
        "engine": EXPECTED_ENGINE,
        "opponent": spec,
        "seeds": SEEDS,
        "variants": VARIANTS,
        "contexts": len(rows),
        "mechanical_pass": mechanical_pass,
        "summary": summary,
        "rows": rows,
        "provenance": provenance,
        "failures": failures,
        "seconds": time.perf_counter() - started,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OPTION_LIBRARY_COMBO_SHARD_RESULT", json.dumps({
        "opponent": spec["key"],
        "mechanical_pass": mechanical_pass,
        "summary": summary,
        "failures": len(failures),
        "seconds": result["seconds"],
    }, sort_keys=True), flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
