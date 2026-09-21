#!/usr/bin/env python3
"""Mechanically merge valid V22B rows across attempts.

Only exact frozen (context_id, mode) keys are accepted. Partial failed shards may
contribute rows because each emitted row already passed exact BASE replay and an
individual episode validation. Duplicate keys must agree exactly on strategic
outcomes. No treatment outcome is used to select or drop a context.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MODES = ("BASE", "MARKET_ONLY", "PHYSICAL_ONLY", "FULL_SHADOW")
CORE_FIELDS = (
    "context_id",
    "source_rank",
    "ref",
    "main_sha256",
    "seed",
    "seat",
    "mode",
    "base_score",
    "treatment_score",
    "score_delta",
    "base_margin",
    "treatment_margin",
    "margin_delta",
)


def canonical_core(row):
    return {k: row.get(k) for k in CORE_FIELDS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--hard-config", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--status-out", required=True)
    args = ap.parse_args()

    cfg = json.loads(Path(args.hard_config).read_text())
    contexts = list(cfg.get("hard_contexts") or [])
    ctx_by_id = {str(c["context_id"]): c for c in contexts}
    ctx_index = {str(c["context_id"]): i for i, c in enumerate(contexts)}

    expected_keys = {
        (str(c["context_id"]), mode)
        for c in contexts
        for mode in MODES
    }

    docs = []
    for p in sorted(Path(args.input_dir).rglob("*.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if d.get("schema") == "kculture-all3-v22b-domain-upper-bound-shard-v1":
            docs.append((p, d))

    accepted = {}
    origins = {}
    conflicts = []
    rejected = []

    for p, d in docs:
        for r in d.get("rows", []):
            cid = str(r.get("context_id"))
            mode = str(r.get("mode"))
            key = (cid, mode)
            ctx = ctx_by_id.get(cid)
            if ctx is None or mode not in MODES or key not in expected_keys:
                rejected.append({"file": str(p), "key": key, "reason": "unexpected_key"})
                continue

            checks = {
                "ref": str(r.get("ref")) == str(ctx["ref"]),
                "sha": str(r.get("main_sha256")) == str(ctx["main_sha256"]),
                "seed": int(r.get("seed")) == int(ctx["seed"]),
                "seat": int(r.get("seat")) == int(ctx["seat"]),
                "base_score": float(r.get("base_score")) == float(ctx["base_score"]),
                "base_margin": float(r.get("base_margin")) == float(ctx["base_margin"]),
            }
            if not all(checks.values()):
                rejected.append({
                    "file": str(p),
                    "key": key,
                    "reason": "context_binding_mismatch",
                    "checks": checks,
                })
                continue

            core = canonical_core(r)
            if key in accepted:
                if canonical_core(accepted[key]) != core:
                    conflicts.append({
                        "key": key,
                        "first": canonical_core(accepted[key]),
                        "other": core,
                        "other_file": str(p),
                    })
                else:
                    origins[key].append(str(p))
            else:
                accepted[key] = r
                origins[key] = [str(p)]

    missing = sorted(expected_keys - set(accepted))
    complete = (
        len(docs) > 0
        and not conflicts
        and not rejected
        and not missing
        and len(accepted) == len(expected_keys)
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    status = {
        "schema": "kculture-all3-v22b-mechanical-merge-status-v1",
        "input_shard_documents": len(docs),
        "expected_keys": len(expected_keys),
        "accepted_keys": len(accepted),
        "missing_keys": [list(x) for x in missing],
        "missing_count": len(missing),
        "conflicts": conflicts,
        "rejected": rejected,
        "complete": complete,
        "source_v22a_workflow": cfg.get("source_v22a_workflow"),
        "automatic_kaggle_submission": False,
    }

    Path(args.status_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.status_out).write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")

    if complete:
        mode_order = {m: i for i, m in enumerate(MODES)}
        for shard in range(4):
            shard_rows = [
                accepted[(str(c["context_id"]), mode)]
                for i, c in enumerate(contexts)
                if i % 4 == shard
                for mode in MODES
            ]
            shard_rows.sort(
                key=lambda r: (
                    ctx_index[str(r["context_id"])],
                    mode_order[str(r["mode"])],
                )
            )
            d = {
                "schema": "kculture-all3-v22b-domain-upper-bound-shard-v1",
                "mechanical_pass": True,
                "shard_index": shard,
                "num_shards": 4,
                "contexts_assigned": sum(1 for i in range(len(contexts)) if i % 4 == shard),
                "expected_rows": len(shard_rows),
                "rows": shard_rows,
                "failures": [],
                "provenance": {
                    "mechanical_merge": True,
                    "input_documents": sorted({
                        f
                        for r in shard_rows
                        for f in origins[(str(r["context_id"]), str(r["mode"]))]
                    }),
                },
                "credentials_removed_before_third_party_execution": True,
                "third_party_code_persisted": False,
                "automatic_kaggle_submission": False,
            }
            (out_dir / f"V22B_SHARD_{shard}.json").write_text(
                json.dumps(d, indent=2, sort_keys=True) + "\n"
            )

    print(
        "V22B_MERGE_RESULT",
        json.dumps(
            {
                "complete": complete,
                "documents": len(docs),
                "accepted_keys": len(accepted),
                "expected_keys": len(expected_keys),
                "missing_count": len(missing),
                "conflicts": len(conflicts),
                "rejected": len(rejected),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    if not complete:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
