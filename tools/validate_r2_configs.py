"""Validate the checked-in R2 seed/pool/provenance configuration."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    seeds = read_json("configs/seed_partitions.json")
    expected_lengths = {"development": 16, "validation": 16, "held_out": 32}
    all_seeds = []
    for name, expected in expected_lengths.items():
        values = seeds[name]
        assert len(values) == expected, (name, len(values), expected)
        assert len(values) == len(set(values)), f"duplicate seeds inside {name}"
        assert all(isinstance(v, int) and 1 <= v <= 2_147_483_646 for v in values)
        all_seeds.extend(values)
    assert len(all_seeds) == len(set(all_seeds)), "seed partitions overlap"

    pool = read_json("configs/opponent_pool.json")
    ids = [item["id"] for item in pool["opponents"]]
    specs = [item["spec"] for item in pool["opponents"]]
    assert len(ids) == len(set(ids)), "duplicate opponent ids"
    assert len(specs) == len(set(specs)), "duplicate opponent specs"
    assert "random" not in specs, "non-deterministic random opponent entered promotion pool"

    public = read_json("configs/public_opponents.json")
    public_ids = [item["id"] for item in public["artifacts"]]
    assert len(public_ids) == len(set(public_ids)), "duplicate public artifact ids"
    for item in public["artifacts"]:
        assert len(item["sha256"]) == 64
        int(item["sha256"], 16)
        assert len(item["commit"]) == 40
        int(item["commit"], 16)
        assert item["license"]

    report = {
        "result": "PASS",
        "seed_counts": expected_lengths,
        "total_seeds": len(all_seeds),
        "reference_opponents": len(pool["opponents"]),
        "public_artifacts": len(public["artifacts"]),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
