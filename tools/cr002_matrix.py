"""Generate the complete unordered pair matrix for CR-002.

The matrix is deterministic and comes only from the frozen league config, so no
pair can be added/removed after outcomes are observed.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/competitive_reset_league_v1.json")
    ap.add_argument("--github", action="store_true")
    args = ap.parse_args()

    cfg = json.loads((ROOT / args.config).read_text(encoding="utf-8"))
    ids = [x["id"] for x in cfg["public_agents"]] + [x["id"] for x in cfg["local_agents"]]
    include = [
        {"a": a, "b": b, "pair": f"{a}__vs__{b}"}
        for a, b in itertools.combinations(ids, 2)
    ]
    payload = {"include": include}
    if args.github:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        print(json.dumps({"league_id": cfg["league_id"], "agents": ids, "pair_count": len(include), "matrix": payload}, indent=2))


if __name__ == "__main__":
    main()
