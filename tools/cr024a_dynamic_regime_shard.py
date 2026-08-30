"""CR024A dynamic public-state diagnostic on already-open CR023 Stage A.

For one exact frozen opponent, rerun CR008 and the frozen top19 public action tape
on the 12 already-open raw Stage-A seeds/both seats.  The top19 run records only
legal public-state features at fixed checkpoints.  Outcome labels are attached
offline after the episode.  No seed, opponent identity, submission identity, or
held-out information is exposed as a candidate runtime feature.
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
CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
CR008_PATH = ROOT / "candidates/cr008_adaptive_frontrun.py"
CHECKPOINT_EVERY = 12


def load_module(path: Path, prefix: str):
    spec = importlib.util.spec_from_file_location(f"{prefix}_{time.time_ns()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clock(obs):
    raw = obs.get("step")
    try:
        if raw is not None:
            return max(0, int(raw))
    except Exception:
        pass
    return max(0, int(obs.get("day") or 0)) * 24 + max(0, int(obs.get("hour") or 0))


def download_tape(api: KaggleApi, meta: dict, folder: Path):
    eid = int(meta["episode_id"])
    api.competition_episode_replay(eid, path=str(folder), quiet=True)
    p = folder / f"episode-{eid}-replay.json"
    replay = json.loads(p.read_text(encoding="utf-8"))
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {len(steps)}")
    seat = int(meta["source_seat"])
    return [copy.deepcopy((steps[t + 1][seat] or {}).get("action") or {}) for t in range(719)]


def finite(x):
    y = float(x)
    if not math.isfinite(y):
        raise RuntimeError(x)
    return y


def score(delta):
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def play(agent, opp_path: Path, seed: int, seat: int):
    opp = load_module(opp_path, "cr024a_opp").agent
    agents = [agent, opp] if seat == 0 else [opp, agent]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run(agents)
    frame = env.toJSON()["steps"][-1]
    if [frame[i].get("status") for i in range(2)] != ["DONE", "DONE"]:
        raise RuntimeError("non-DONE")
    own = finite(frame[seat].get("reward")); other = finite(frame[1-seat].get("reward"))
    delta = own - other
    return {"self": own, "opp": other, "delta": delta, "score": score(delta)}


def make_recording_tape_agent(tape, seat: int):
    cr008 = load_module(CR008_PATH, "cr024a_feature_encoder")
    history = {}
    checkpoints = []

    def agent(obs, config=None):
        t = clock(obs)
        if t == 0:
            history.clear(); checkpoints.clear()
        # Use the already-frozen CR008 legal public feature encoder, comparing
        # current public state with the public state 24 turns earlier.
        if t >= 24 and t % CHECKPOINT_EVERY == 0 and (t - 24) in history:
            feat = cr008._public_features(obs, history[t - 24], seat)
            if feat:
                # _feature_step intentionally reproduces a historical encoder
                # quirk. Add a reliable public clock only for this diagnostic.
                feat = {k: float(v) for k, v in feat.items() if isinstance(v, (int, float)) and math.isfinite(float(v))}
                feat["clock"] = float(t)
                checkpoints.append({"clock": t, "features": feat})
        history[t] = cr008._snapshot(obs)
        for old in list(history):
            if old < t - 30:
                del history[old]
        return copy.deepcopy(tape[max(0, min(718, t))])

    return agent, checkpoints


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    seeds = [int(x) for x in cfg["raw_backbone_stage_a_seeds"]]
    assert not set(seeds) & set(cfg["raw_backbone_stage_b_seeds"])
    opp_path = Path(args.opponent)
    if not opp_path.is_absolute(): opp_path = ROOT / opp_path
    api = KaggleApi(); api.authenticate()
    rows, errors = [], []
    with tempfile.TemporaryDirectory(prefix="cr024a-dyn-") as td:
        tape = download_tape(api, cfg["routes"]["top19_openloop"], Path(td))
        for seed in seeds:
            for seat in (0, 1):
                try:
                    control = play(load_module(CR008_PATH, "cr024a_cr008").agent, opp_path, seed, seat)
                    tape_agent, checkpoints = make_recording_tape_agent(tape, seat)
                    route = play(tape_agent, opp_path, seed, seat)
                    unfavorable = route["score"] < control["score"]
                    favorable = route["score"] > control["score"]
                    rows.append({
                        "seed": seed,
                        "seat": seat,
                        "opponent": args.opponent_id,
                        "control": control,
                        "top19": route,
                        "unfavorable_conversion": unfavorable,
                        "favorable_conversion": favorable,
                        "checkpoints": checkpoints,
                    })
                except Exception as exc:
                    errors.append({"seed": seed, "seat": seat, "opponent": args.opponent_id, "error": repr(exc)})
    payload = {
        "experiment": "CR024A",
        "stage": "DYNAMIC_REGIME_DIAGNOSTIC_STAGE_A_ONLY",
        "opponent": args.opponent_id,
        "expected_rows": len(seeds) * 2,
        "completed_rows": len(rows),
        "errors": errors,
        "runtime_identity_features_used": False,
        "runtime_seed_feature_allowed": False,
        "stage_b_touched": False,
        "held_out_touched": False,
        "checkpoint_every": CHECKPOINT_EVERY,
        "rows": rows,
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "opponent": args.opponent_id,
        "completed_rows": len(rows),
        "error_count": len(errors),
        "unfavorable": sum(bool(r["unfavorable_conversion"]) for r in rows),
        "favorable": sum(bool(r["favorable_conversion"]) for r in rows),
    }, indent=2, sort_keys=True))
    if errors or len(rows) != len(seeds) * 2:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
