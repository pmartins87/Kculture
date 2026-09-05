"""CR027: paired fresh-seed screen of pinned public frontier packages.

Each public candidate is run from the exact extracted packaged main.py via a file
path, matching hosted last-callable loading semantics as closely as the local
engine permits. CR024 and each candidate are paired against the same frozen
reactive opponents on the same seeds/seats. Candidate-vs-CR024 head-to-head is
also measured. No ladder submission is made here.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import statistics
import tempfile
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr027_frontier_screen.json"
OLD_CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def seed_values(obj, parent=""):
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k).lower()
            if "seed" in key:
                if isinstance(v, list):
                    for x in v:
                        try:
                            out.add(int(x))
                        except Exception:
                            pass
                else:
                    try:
                        out.add(int(v))
                    except Exception:
                        pass
            out |= seed_values(v, key)
    elif isinstance(obj, list):
        for v in obj:
            out |= seed_values(v, parent)
    return out


def play(own: Path, opp: Path, seed: int, seat: int):
    agents = [str(own), str(opp)] if seat == 0 else [str(opp), str(own)]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    rep = env.toJSON()
    steps = rep.get("steps") or []
    if len(steps) != 720:
        raise RuntimeError(f"short game: {len(steps)}")
    final = steps[-1]
    statuses = [final[p].get("status") for p in (0, 1)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses: {statuses}")
    rewards = []
    for p in (0, 1):
        x = float(final[p].get("reward"))
        if not math.isfinite(x):
            raise RuntimeError("non-finite reward")
        rewards.append(x)
    delta = rewards[seat] - rewards[1 - seat]
    return {"rewards": rewards, "delta": delta, "score": score(delta)}


def paired_metrics(rows):
    diffs = [r["candidate"]["delta"] - r["control"]["delta"] for r in rows]
    return {
        "score_gain": sum(r["candidate"]["score"] - r["control"]["score"] for r in rows),
        "regressions": sum(r["candidate"]["score"] < r["control"]["score"] for r in rows),
        "improvements": sum(r["candidate"]["score"] > r["control"]["score"] for r in rows),
        "mean_delta_gain": statistics.mean(diffs) if diffs else None,
        "positive_margin_rows": sum(x > 0 for x in diffs),
        "negative_margin_rows": sum(x < 0 for x in diffs),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-id", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--candidate-receipt", required=True)
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    candidate_meta = next((x for x in cfg["candidates"] if x["id"] == args.candidate_id), None)
    if candidate_meta is None:
        raise SystemExit("unknown candidate")
    receipt = json.loads(Path(args.candidate_receipt).read_text(encoding="utf-8"))
    if receipt.get("handle") != candidate_meta["handle"]:
        raise SystemExit("candidate provenance mismatch")

    seeds = [int(x) for x in cfg["fresh_seeds"]]
    old = json.loads(OLD_CFG.read_text(encoding="utf-8"))
    overlap = sorted(set(seeds) & seed_values(old))
    if overlap:
        raise SystemExit(f"fresh seed firewall overlap: {overlap}")

    candidate_path = Path(args.candidate).resolve()
    opp_dir = Path(args.opponent_dir).resolve()
    if not candidate_path.is_file():
        raise FileNotFoundError(candidate_path)

    errors = []
    direct = []
    reactive = []
    per_opponent = {}

    with tempfile.TemporaryDirectory(prefix="cr027-screen-") as td:
        tmp = Path(td)
        bench = load_module(ROOT / "tools/cr026_live_meta_cr024_benchmark.py", "cr027_bench")
        builder = load_module(ROOT / "tools/build_cr024_consensus_submission.py", "cr027_builder")
        consensus, provenance = bench.build_cr024(tmp / "cr024_source")
        cr024_path = tmp / "cr024_main.py"
        cr024_path.write_text(builder.runtime_source(consensus), encoding="utf-8")

        for seed in seeds:
            for seat in (0, 1):
                try:
                    direct.append({"seed": seed, "seat": seat, "candidate": play(candidate_path, cr024_path, seed, seat)})
                except Exception as exc:
                    errors.append({"phase": "direct", "seed": seed, "seat": seat, "error": repr(exc)[:500]})

        for om in cfg["opponents"]:
            opp_path = opp_dir / f"{om['id']}.py"
            rows = []
            for seed in seeds:
                for seat in (0, 1):
                    try:
                        control = play(cr024_path, opp_path, seed, seat)
                        cand = play(candidate_path, opp_path, seed, seat)
                        row = {"opponent": om["id"], "seed": seed, "seat": seat, "control": control, "candidate": cand}
                        rows.append(row)
                        reactive.append(row)
                    except Exception as exc:
                        errors.append({"phase": "reactive", "opponent": om["id"], "seed": seed, "seat": seat, "error": repr(exc)[:500]})
            if rows:
                per_opponent[om["id"]] = paired_metrics(rows)

    expected_direct = len(seeds) * 2
    expected_reactive = len(seeds) * 2 * len(cfg["opponents"])
    mechanical = len(direct) == expected_direct and len(reactive) == expected_reactive and not errors
    direct_score = sum(r["candidate"]["score"] for r in direct)
    direct_mean = statistics.mean(r["candidate"]["delta"] for r in direct) if direct else None
    paired = paired_metrics(reactive) if reactive else {
        "score_gain": None, "regressions": None, "improvements": None,
        "mean_delta_gain": None, "positive_margin_rows": 0, "negative_margin_rows": 0,
    }
    g = cfg["gate"]
    checks = {
        "mechanical": mechanical,
        "direct": mechanical and direct_score >= float(g["direct_vs_cr024_min_score"]),
        "reactive_score": mechanical and paired["score_gain"] >= float(g["reactive_paired_min_score_gain"]),
        "reactive_regressions": mechanical and paired["regressions"] <= int(g["reactive_max_regressions"]),
    }
    decision = "SHORTLIST_FOR_HOSTED_CALIBRATION" if all(checks.values()) else "REJECT_FRONTIER_PACKAGE"
    payload = {
        "experiment": cfg["experiment"],
        "candidate": candidate_meta,
        "candidate_receipt": receipt,
        "cr024_provenance": provenance,
        "fresh_seeds": seeds,
        "expected_direct": expected_direct,
        "completed_direct": len(direct),
        "expected_reactive": expected_reactive,
        "completed_reactive": len(reactive),
        "errors": errors,
        "direct_score": direct_score,
        "direct_mean_delta": direct_mean,
        "reactive": paired,
        "per_opponent": per_opponent,
        "checks": checks,
        "decision": decision,
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
        "direct_rows": direct,
        "reactive_rows": reactive,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k not in ("direct_rows", "reactive_rows")}, indent=2, sort_keys=True))
    if not mechanical:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
