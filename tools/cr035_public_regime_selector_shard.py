"""CR035 shard: evaluate one frozen public-regime selector on the 12 open elite scenarios.

candidate-rank 0 is the exact CR029 control. Ranks 1..12 use CR029 for clocks
0..23, latch the frozen CR034 public classifier at clock 24, and switch to that
rank's complete elite tape only when self_money > 35.5 (keiz regime).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import statistics
import tempfile
from pathlib import Path

import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr031_elite_round_robin.json"
OUT = ROOT / "artifacts/cr035_public_regime_selector/shards"
HANDLE = "kaggle/kaggriculture-episodes-2026-09-05"
SWITCH_CLOCK = 24
SELF_MONEY_THRESHOLD = 35.5


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except Exception:
        try:
            return obj[key]
        except Exception:
            return default


def _clock(obs) -> int:
    try:
        raw = _get(obs, "step", None)
        if raw is not None:
            return max(0, int(raw))
    except Exception:
        pass
    try:
        return max(0, int(_get(obs, "day", 0) or 0)) * 24 + max(0, int(_get(obs, "hour", 0) or 0))
    except Exception:
        return 0


def _self_money(obs) -> float:
    try:
        farms = _get(obs, "farms", []) or []
        player = int(_get(obs, "player", 0) or 0)
        v = float(_get(farms[player], "money", 0) or 0)
        return v if math.isfinite(v) else 0.0
    except Exception:
        return 0.0


def _canon(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def _tape_sha(tape: list[dict]) -> str:
    return hashlib.sha256(_canon(tape).encode("utf-8")).hexdigest()


def _actions(rep: dict, seat: int) -> list[dict]:
    steps = rep.get("steps") or []
    return [copy.deepcopy((steps[t][seat] or {}).get("action") or {}) for t in range(1, len(steps))]


def _download_episode(eid: int, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(HANDLE, path=f"{eid}.json", output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))


def _final_ok(rep: dict) -> bool:
    steps = rep.get("steps") or []
    return len(steps) == 720 and [steps[-1][i].get("status") for i in (0, 1)] == ["DONE", "DONE"]


def _rewards(rep: dict) -> list[float]:
    steps = rep.get("steps") or []
    return [float(steps[-1][i].get("reward")) for i in (0, 1)]


def _wl(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def _tape_agent(tape: list[dict]):
    def agent(obs, config=None):
        s = max(0, min(len(tape) - 1, _clock(obs)))
        return copy.deepcopy(tape[s])
    return agent


def _selector_agent(base: list[dict], alternate: list[dict] | None):
    state = {"predicted_team": None, "self_money_at_24": None, "switched": False}

    def agent(obs, config=None):
        s = max(0, min(len(base) - 1, _clock(obs)))
        if alternate is None:
            return copy.deepcopy(base[s])
        if state["predicted_team"] is None and s >= SWITCH_CLOCK:
            money = _self_money(obs)
            state["self_money_at_24"] = money
            state["predicted_team"] = "keiz" if money > SELF_MONEY_THRESHOLD else "Jesse Bullard"
            state["switched"] = state["predicted_team"] == "keiz"
        tape = alternate if state["switched"] else base
        return copy.deepcopy(tape[s])

    return agent, state


def _summary(rows: list[dict]) -> dict:
    scores = [float(r["score"]) for r in rows]
    deltas = [float(r["delta"]) for r in rows]
    return {
        "games": len(rows),
        "wins": sum(x == 1.0 for x in scores),
        "losses": sum(x == 0.0 for x in scores),
        "ties": sum(x == 0.5 for x in scores),
        "score_total": sum(scores),
        "score_rate": sum(scores) / len(scores) if scores else None,
        "mean_delta": statistics.mean(deltas) if deltas else None,
        "median_delta": statistics.median(deltas) if deltas else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-rank", type=int, required=True)
    args = ap.parse_args()
    candidate_rank = int(args.candidate_rank)
    if candidate_rank < 0 or candidate_rank > 12:
        raise SystemExit("candidate-rank must be 0..12")

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[dict] = []
    rows: list[dict] = []

    with tempfile.TemporaryDirectory(prefix=f"cr035-r{candidate_rank:02d}-") as td_raw:
        td = Path(td_raw)
        api = KaggleApi()
        api.authenticate()

        recent = cfg["recent_top"]
        recent_dir = td / "recent"
        recent_dir.mkdir(parents=True, exist_ok=True)
        api.competition_episode_replay(int(recent["episode_id"]), path=str(recent_dir), quiet=True)
        rp = recent_dir / f"episode-{int(recent['episode_id'])}-replay.json"
        recent_rep = json.loads(rp.read_text(encoding="utf-8"))
        base = _actions(recent_rep, int(recent["source_seat"]))
        if len(base) != 719 or _tape_sha(base) != recent["tape_sha256"]:
            raise RuntimeError("CR029 tape provenance mismatch")

        scenarios: dict[int, dict] = {}
        for s in cfg["scenarios"]:
            rank = int(s["rank"])
            eid = int(s["episode_id"])
            rep = _download_episode(eid, td / "episodes" / str(eid))
            tape = _actions(rep, int(s["winner_seat"]))
            observed = _tape_sha(tape)
            if len(tape) != 719 or observed != s["tape_sha256"]:
                raise RuntimeError(f"rank {rank} tape provenance mismatch: {observed}")
            info = rep.get("info") or {}
            if int(info.get("seed")) != int(s["seed"]):
                raise RuntimeError(f"rank {rank} seed provenance mismatch")
            scenarios[rank] = {
                "rank": rank,
                "episode_id": eid,
                "seed": int(s["seed"]),
                "team": s["team"],
                "configuration": rep.get("configuration") if isinstance(rep.get("configuration"), dict) else {},
                "tape": tape,
            }

        alternate = None if candidate_rank == 0 else scenarios[candidate_rank]["tape"]
        candidate_team = "CR029_CONTROL" if candidate_rank == 0 else scenarios[candidate_rank]["team"]

        for rank, sc in sorted(scenarios.items()):
            for seat in (0, 1):
                try:
                    own_agent, state = _selector_agent(base, alternate)
                    opp_agent = _tape_agent(sc["tape"])
                    conf = copy.deepcopy(sc["configuration"])
                    conf["episodeSteps"] = 720
                    conf["seed"] = int(sc["seed"])
                    env = make("kaggriculture", configuration=conf, debug=True)
                    env.run([own_agent, opp_agent] if seat == 0 else [opp_agent, own_agent])
                    rep = env.toJSON()
                    if not _final_ok(rep):
                        raise RuntimeError(f"non-DONE steps={len(rep.get('steps') or [])}")
                    rewards = _rewards(rep)
                    own_reward = rewards[seat]
                    opp_reward = rewards[1 - seat]
                    delta = own_reward - opp_reward
                    predicted = state["predicted_team"] if candidate_rank != 0 else None
                    rows.append({
                        "candidate_rank": candidate_rank,
                        "candidate_team": candidate_team,
                        "opponent_rank": rank,
                        "opponent_team": sc["team"],
                        "episode_id": sc["episode_id"],
                        "seed": sc["seed"],
                        "seat": seat,
                        "self_reward": own_reward,
                        "opp_reward": opp_reward,
                        "delta": delta,
                        "score": _wl(delta),
                        "predicted_team": predicted,
                        "classifier_correct": None if candidate_rank == 0 else predicted == sc["team"],
                        "self_money_at_24": state["self_money_at_24"],
                        "switched": bool(state["switched"]),
                    })
                except Exception as exc:
                    errors.append({"opponent_rank": rank, "seat": seat, "error": repr(exc)})

    keiz_rows = [r for r in rows if r["opponent_team"] == "keiz"]
    jesse_rows = [r for r in rows if r["opponent_team"] == "Jesse Bullard"]
    out = {
        "experiment": "CR035_PUBLIC_REGIME_SELECTOR_V1",
        "candidate_rank": candidate_rank,
        "candidate_team": candidate_team,
        "switch_clock": SWITCH_CLOCK,
        "classifier_feature": "self_money",
        "classifier_threshold": SELF_MONEY_THRESHOLD,
        "mechanical_complete": not errors and len(rows) == 24,
        "errors": errors,
        "all": _summary(rows),
        "keiz": _summary(keiz_rows),
        "jesse": _summary(jesse_rows),
        "classifier_correct": None if candidate_rank == 0 else sum(bool(r["classifier_correct"]) for r in rows),
        "classifier_total": None if candidate_rank == 0 else len(rows),
        "switched_games": sum(bool(r["switched"]) for r in rows),
        "rows": rows,
        "source_scenarios_already_open": True,
        "fresh_validation_touched": False,
        "held_out_touched": False,
        "runtime_identity_features": False,
    }
    path = OUT / f"shard_rank{candidate_rank:02d}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2, sort_keys=True))
    if errors or len(rows) != 24:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
