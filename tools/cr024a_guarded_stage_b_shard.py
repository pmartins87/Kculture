"""Frozen CR024A guarded-top19 Stage-B paired shard.

Runs exact CR008, raw top19, and the preregistered CR024A hybrid on one exact
opponent over the untouched CR023 raw Stage-B seeds and both seats.
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
GUARD_CLOCK = 192
GUARD_FEATURE = "dmarket_price_wool"
GUARD_THRESHOLD = 11.5


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


def finite(x):
    y = float(x)
    if not math.isfinite(y):
        raise RuntimeError(x)
    return y


def wl(delta):
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def download_top19(api: KaggleApi, cfg: dict, folder: Path):
    meta = cfg["routes"]["top19_openloop"]
    eid = int(meta["episode_id"])
    api.competition_episode_replay(eid, path=str(folder), quiet=True)
    p = folder / f"episode-{eid}-replay.json"
    replay = json.loads(p.read_text(encoding="utf-8"))
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {len(steps)}")
    source_seat = int(meta["source_seat"])
    return [copy.deepcopy((steps[t + 1][source_seat] or {}).get("action") or {}) for t in range(719)]


def play(agent, opponent_path: Path, seed: int, seat: int):
    opponent = load_module(opponent_path, "cr024a_b_opp").agent
    agents = [agent, opponent] if seat == 0 else [opponent, agent]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    frame = env.toJSON()["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses {statuses}")
    own = finite(frame[seat].get("reward")); opp = finite(frame[1-seat].get("reward"))
    delta = own - opp
    return {"self": own, "opp": opp, "delta": delta, "score": wl(delta)}


def make_tape_agent(tape):
    def agent(obs, config=None):
        return copy.deepcopy(tape[max(0, min(718, clock(obs)))])
    return agent


def make_guarded_agent(tape):
    """Top19 until one frozen public-state check; then permanent CR008 fallback."""
    cr008 = load_module(CR008_PATH, "cr024a_b_hybrid")
    local_history = {}
    state = {"last": -1, "switched": False, "guard_value": None, "switch_clock": None}

    def reset(player, t):
        if t == 0 or t < state["last"]:
            local_history.clear()
            state.update({"last": -1, "switched": False, "guard_value": None, "switch_clock": None})
            cr008._HISTORY[player].clear()
            cr008._LAST_STEP[player] = -1
        state["last"] = t
        cr008._reset_if_needed(player, t)

    def remember(player, t, obs):
        local_history[t] = cr008._snapshot(obs)
        for old in list(local_history):
            if old < t - 30:
                del local_history[old]
        cr008._remember(player, t, obs)

    def agent(obs, config=None):
        player = int(cr008._get(obs, "player", 0) or 0)
        t = clock(obs)
        reset(player, t)

        if t == GUARD_CLOCK and not state["switched"]:
            prev = local_history.get(t - 24)
            if prev is not None:
                feat = cr008._public_features(obs, prev, player)
                value = float(feat.get(GUARD_FEATURE, 0.0)) if feat else 0.0
                state["guard_value"] = value
                if value >= GUARD_THRESHOLD:
                    state["switched"] = True
                    state["switch_clock"] = t

        if state["switched"]:
            # Execute frozen CR008 semantics without double-updating its history.
            action = cr008._BASE.agent(obs, config)
            action = cr008._append_adaptive_sales(obs, action, player, t)
        else:
            action = copy.deepcopy(tape[max(0, min(718, t))])

        remember(player, t, obs)
        return action

    return agent, state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    stage_a = set(int(x) for x in cfg["raw_backbone_stage_a_seeds"])
    seeds = [int(x) for x in cfg["raw_backbone_stage_b_seeds"]]
    if stage_a & set(seeds):
        raise SystemExit("Stage-A/Stage-B seed overlap")
    if set(seeds) & set(int(x) for x in cfg["adaptive_overlay_stage_a_seeds_reserved"]):
        raise SystemExit("adaptive seed firewall violation")
    if set(seeds) & set(int(x) for x in cfg["adaptive_overlay_stage_b_seeds_reserved"]):
        raise SystemExit("adaptive seed firewall violation")

    opponent_path = Path(args.opponent)
    if not opponent_path.is_absolute():
        opponent_path = ROOT / opponent_path

    api = KaggleApi(); api.authenticate()
    rows, errors = [], []
    with tempfile.TemporaryDirectory(prefix="cr024a-stage-b-") as td:
        tape = download_top19(api, cfg, Path(td))
        for seed in seeds:
            for seat in (0, 1):
                try:
                    control = play(load_module(CR008_PATH, "cr024a_b_cr008").agent, opponent_path, seed, seat)
                    raw = play(make_tape_agent(tape), opponent_path, seed, seat)
                    hybrid_agent, meta = make_guarded_agent(tape)
                    hybrid = play(hybrid_agent, opponent_path, seed, seat)
                    rows.append({
                        "seed": seed,
                        "seat": seat,
                        "opponent": args.opponent_id,
                        "cr008": control,
                        "top19": raw,
                        "cr024a": hybrid,
                        "guard_positive": bool(meta["switched"]),
                        "guard_value": meta["guard_value"],
                        "switch_clock": meta["switch_clock"],
                    })
                except Exception as exc:
                    errors.append({"seed": seed, "seat": seat, "opponent": args.opponent_id, "error": repr(exc)})

    payload = {
        "experiment": "CR024A",
        "stage": "GUARDED_TOP19_STAGE_B",
        "opponent": args.opponent_id,
        "guard": {"clock": GUARD_CLOCK, "feature": GUARD_FEATURE, "direction": "ge", "threshold": GUARD_THRESHOLD},
        "expected_rows": len(seeds) * 2,
        "completed_rows": len(rows),
        "errors": errors,
        "stage_a_touched_by_this_run": False,
        "adaptive_reserved_touched": False,
        "held_out_touched": False,
        "runtime_identity_features_used": False,
        "runtime_seed_feature_used": False,
        "rows": rows,
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "opponent": args.opponent_id,
        "completed_rows": len(rows),
        "error_count": len(errors),
        "guard_positive": sum(bool(r["guard_positive"]) for r in rows),
    }, indent=2, sort_keys=True))
    if errors or len(rows) != len(seeds) * 2:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
