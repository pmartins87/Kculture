"""CR025 fresh paired shard on the previously sealed adaptive Stage-B seeds."""
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
CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
CANDIDATE = ROOT / "candidates/cr025_consensus_adaptive.py"


def load_module(path: Path, prefix: str):
    spec = importlib.util.spec_from_file_location(f"{prefix}_{time.time_ns()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clock(obs):
    try:
        raw = obs.get("step")
        if raw is not None:
            return max(0, int(raw))
    except Exception:
        pass
    try:
        return max(0, int(obs.get("day") or 0)) * 24 + max(0, int(obs.get("hour") or 0))
    except Exception:
        return 0


def finite(value):
    x = float(value)
    if not math.isfinite(x):
        raise RuntimeError(value)
    return x


def score(delta):
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def download_tape(api: KaggleApi, meta: dict, folder: Path):
    episode_id = int(meta["episode_id"])
    source_seat = int(meta["source_seat"])
    api.competition_episode_replay(episode_id, path=str(folder), quiet=True)
    p = folder / f"episode-{episode_id}-replay.json"
    replay = json.loads(p.read_text(encoding="utf-8"))
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {episode_id}: {len(steps)}")
    return [copy.deepcopy((steps[t + 1][source_seat] or {}).get("action") or {}) for t in range(719)]


def build_consensus(t11, t19):
    if len(t11) != 719 or len(t19) != 719:
        raise RuntimeError("tape length mismatch")
    out = []
    for i, (a, b) in enumerate(zip(t11, t19)):
        if json.dumps(a.get("farmer"), sort_keys=True) != json.dumps(b.get("farmer"), sort_keys=True):
            raise RuntimeError(f"farmer mismatch at {i}")
        z = copy.deepcopy(b)
        z["hands"] = copy.deepcopy(a.get("hands"))
        z["market"] = copy.deepcopy(b.get("market"))
        out.append(z)
    return out


def make_tape_agent(tape):
    def agent(obs, config=None):
        return copy.deepcopy(tape[max(0, min(718, clock(obs)))])
    return agent


def play(agent, opponent_path: Path, seed: int, seat: int):
    opp = load_module(opponent_path, "cr025_opp").agent
    agents = [agent, opp] if seat == 0 else [opp, agent]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    frame = env.toJSON()["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses {statuses}")
    own = finite(frame[seat].get("reward"))
    other = finite(frame[1 - seat].get("reward"))
    delta = own - other
    result = {"self": own, "opp": other, "delta": delta, "score": score(delta)}
    stats = getattr(agent, "_cr025_stats", None)
    if stats is not None:
        result["overlay"] = copy.deepcopy(stats)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    seeds = [int(x) for x in cfg["adaptive_overlay_stage_b_seeds_reserved"]]
    forbidden = set(int(x) for x in cfg["raw_backbone_stage_a_seeds"])
    forbidden |= set(int(x) for x in cfg["raw_backbone_stage_b_seeds"])
    forbidden |= set(int(x) for x in cfg["adaptive_overlay_stage_a_seeds_reserved"])
    if set(seeds) & forbidden:
        raise SystemExit("seed firewall overlap")

    opponent_path = Path(args.opponent)
    if not opponent_path.is_absolute():
        opponent_path = ROOT / opponent_path

    candidate_mod = load_module(CANDIDATE, "cr025_candidate")
    api = KaggleApi(); api.authenticate()
    rows, errors = [], []
    with tempfile.TemporaryDirectory(prefix="cr025-stageb-") as td:
        folder = Path(td)
        t11 = download_tape(api, cfg["routes"]["top11_openloop"], folder)
        t19 = download_tape(api, cfg["routes"]["top19_openloop"], folder)
        consensus = build_consensus(t11, t19)
        for seed in seeds:
            for seat in (0, 1):
                row = {"seed": seed, "seat": seat, "opponent": args.opponent_id}
                try:
                    row["cr024"] = play(make_tape_agent(consensus), opponent_path, seed, seat)
                    row["cr025"] = play(candidate_mod.make_agent(consensus), opponent_path, seed, seat)
                    rows.append(row)
                except Exception as exc:
                    errors.append({"seed": seed, "seat": seat, "opponent": args.opponent_id, "error": repr(exc)})

    payload = {
        "experiment": "CR025_CONSENSUS_ADAPTIVE",
        "stage": "ADAPTIVE_OVERLAY_STAGE_B_RESERVED",
        "opponent": args.opponent_id,
        "expected_rows": len(seeds) * 2,
        "completed_rows": len(rows),
        "errors": errors,
        "held_out_touched": False,
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"opponent": args.opponent_id, "completed_rows": len(rows), "errors": len(errors)}, indent=2))
    if errors or len(rows) != len(seeds) * 2:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
