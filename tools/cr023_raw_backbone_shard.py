"""CR023 raw-backbone paired shard runner.

Evaluates the three preregistered public action tapes against exact frozen CR008
on one exact opponent across all raw Stage-A seeds and both seats. Replay bytes
are downloaded transiently from Kaggle and never written to the result artifact.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import tempfile
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
CR008 = ROOT / "candidates/cr008_adaptive_frontrun.py"
CONTROL = "cr008"


def load_agent(path: Path, prefix: str):
    spec = importlib.util.spec_from_file_location(f"{prefix}_{time.time_ns()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.agent


def clock(obs):
    try:
        raw = obs.get("step")
        if raw is not None:
            return int(raw)
    except Exception:
        pass
    try:
        return int(obs.get("day") or 0) * 24 + int(obs.get("hour") or 0)
    except Exception:
        return 0


def download_replay(api: KaggleApi, episode_id: int, folder: Path) -> Path:
    api.competition_episode_replay(int(episode_id), path=str(folder), quiet=True)
    path = folder / f"episode-{int(episode_id)}-replay.json"
    if not path.exists():
        raise RuntimeError(f"missing replay {episode_id}")
    return path


def extract_tape(path: Path, source_seat: int):
    replay = json.loads(path.read_text(encoding="utf-8"))
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {len(steps)}")
    tape = []
    for t in range(719):
        frame = steps[t + 1][int(source_seat)]
        action = frame.get("action") if isinstance(frame, dict) else None
        tape.append(copy.deepcopy(action or {}))
    return tape


def make_tape_agent(tape):
    def agent(obs, config=None):
        t = max(0, min(718, clock(obs)))
        return copy.deepcopy(tape[t])
    return agent


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def finite_reward(value):
    try:
        x = float(value)
        if math.isfinite(x):
            return x
    except Exception:
        pass
    raise RuntimeError(f"invalid reward {value!r}")


def play(own_agent, opponent_path: Path, seed: int, seat: int):
    opponent = load_agent(opponent_path, "cr023_opp")
    agents = [own_agent, opponent] if seat == 0 else [opponent, own_agent]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=True,
    )
    env.run(agents)
    frame = env.toJSON()["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses {statuses}")
    own = finite_reward(frame[seat].get("reward"))
    opp = finite_reward(frame[1 - seat].get("reward"))
    delta = own - opp
    return {"self": own, "opp": opp, "delta": delta, "score": score(delta)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    seeds = [int(x) for x in cfg["raw_backbone_stage_a_seeds"]]
    routes = cfg["routes"]
    opponent_path = Path(args.opponent)
    if not opponent_path.is_absolute():
        opponent_path = ROOT / opponent_path

    api = KaggleApi()
    api.authenticate()
    rows = []
    errors = []

    with tempfile.TemporaryDirectory(prefix="kculture-cr023-raw-") as td:
        tmp = Path(td)
        tapes = {}
        for route_id, meta in routes.items():
            replay_path = download_replay(api, int(meta["episode_id"]), tmp)
            tapes[route_id] = extract_tape(replay_path, int(meta["source_seat"]))

        for seed in seeds:
            for seat in (0, 1):
                row = {"seed": seed, "opponent": args.opponent_id, "seat": seat}
                try:
                    row[CONTROL] = play(load_agent(CR008, "cr023_cr008"), opponent_path, seed, seat)
                except Exception as exc:
                    errors.append({"seed": seed, "seat": seat, "opponent": args.opponent_id, "arm": CONTROL, "error": repr(exc)})
                    continue

                failed = False
                for route_id in routes:
                    try:
                        row[route_id] = play(make_tape_agent(tapes[route_id]), opponent_path, seed, seat)
                    except Exception as exc:
                        errors.append({"seed": seed, "seat": seat, "opponent": args.opponent_id, "arm": route_id, "error": repr(exc)})
                        failed = True
                        break
                if not failed:
                    rows.append(row)

    payload = {
        "experiment": "CR023",
        "stage": "RAW_A",
        "opponent": args.opponent_id,
        "control": CONTROL,
        "route_provenance": routes,
        "expected_pairs": len(seeds) * 2,
        "completed_pairs": len(rows),
        "errors": errors,
        "rows": rows,
        "raw_replays_persisted": False,
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
