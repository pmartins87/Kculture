"""CR022C paired quantity shard runner.

One invocation evaluates one exact frozen opponent, every seed in the requested
stage, both seats, and all four preregistered quantity arms. q100 is the exact
frozen CR008 file; fractional arms use the frozen CR022C factory.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONFIG = ROOT / "configs/cr022c_quantity_preregistered_seeds_v1.json"
CR008 = ROOT / "candidates/cr008_adaptive_frontrun.py"
FACTORY_PATH = ROOT / "candidates/cr022c_fractional_adaptive.py"

ARMS = {
    "q25": (1, 4),
    "q50": (1, 2),
    "q75": (3, 4),
    "q100": (1, 1),
}


def load_module(path: Path, prefix: str):
    spec = importlib.util.spec_from_file_location(f"{prefix}_{time.time_ns()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_opponent(path: Path):
    return load_module(path, "cr022c_opp").agent


def make_own(arm: str):
    if arm == "q100":
        return load_module(CR008, "cr022c_control").agent
    num, den = ARMS[arm]
    factory = load_module(FACTORY_PATH, "cr022c_factory")
    return factory.make_agent(num, den)


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def play(arm: str, opponent_path: Path, seed: int, seat: int):
    own = make_own(arm)
    opp = load_opponent(opponent_path)
    agents = [own, opp] if seat == 0 else [opp, own]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=True,
    )
    env.run(agents)
    frame = env.toJSON()["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    rewards = [frame[i].get("reward") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses: {statuses}")
    self_reward = float(rewards[seat])
    opp_reward = float(rewards[1 - seat])
    delta = self_reward - opp_reward
    return {
        "self": self_reward,
        "opp": opp_reward,
        "delta": delta,
        "score": score(delta),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--stage", choices=("a", "b"), required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    seeds = cfg["stage_a_seeds" if args.stage == "a" else "stage_b_seeds"]
    opponent = Path(args.opponent)
    if not opponent.is_absolute():
        opponent = ROOT / opponent

    rows = []
    errors = []
    for seed in seeds:
        for seat in (0, 1):
            row = {"seed": int(seed), "opponent": args.opponent_id, "seat": seat}
            for arm in ("q100", "q25", "q50", "q75"):
                try:
                    row[arm] = play(arm, opponent, int(seed), seat)
                except Exception as exc:
                    errors.append({
                        "seed": int(seed),
                        "opponent": args.opponent_id,
                        "seat": seat,
                        "arm": arm,
                        "error": repr(exc),
                    })
                    row[arm] = None
                    break
            if all(row.get(arm) is not None for arm in ARMS):
                rows.append(row)

    payload = {
        "experiment": "CR022C",
        "stage": args.stage.upper(),
        "opponent": args.opponent_id,
        "seeds": seeds,
        "arms": ARMS,
        "expected_pairs": len(seeds) * 2,
        "completed_pairs": len(rows),
        "errors": errors,
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "experiment": payload["experiment"],
        "stage": payload["stage"],
        "opponent": payload["opponent"],
        "expected_pairs": payload["expected_pairs"],
        "completed_pairs": payload["completed_pairs"],
        "error_count": len(errors),
    }, indent=2, sort_keys=True))
    if errors or len(rows) != len(seeds) * 2:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
