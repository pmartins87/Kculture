"""KEXP-028: exact public live-meta action-tape benchmark.

Phase A replays both public action streams from each selected official episode
under the frozen official engine/seed and requires exact terminal reward
reproduction. Phase B, only for episodes that reproduce exactly, replaces the
original loser with frozen R4B and keeps the original winner action tape in its
original seat. This is benchmark-only; no tape, team or episode identity is a
deployable policy feature.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import statistics
import sys
import tempfile
from pathlib import Path

import kagglehub
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return default


def actions_for(rep: dict, player: int) -> list[dict]:
    out = []
    for frame in rep.get("steps", []):
        action = frame[player].get("action") if player < len(frame) else None
        out.append(copy.deepcopy(action) if isinstance(action, dict) else {})
    return out


def tape_agent(actions: list[dict]):
    def agent(obs, config=None):
        try:
            step = int(get(obs, "step", 0) or 0)
        except (TypeError, ValueError):
            step = 0
        if 0 <= step < len(actions):
            return copy.deepcopy(actions[step])
        return {}
    return agent


def final_rewards(rep: dict) -> list[float | None]:
    if not rep.get("steps"):
        return [None, None]
    final = rep["steps"][-1]
    out = []
    for p in (0, 1):
        r = final[p].get("reward") if p < len(final) else None
        out.append(float(r) if isinstance(r, (int, float)) else None)
    return out


def final_statuses(rep: dict) -> list[str | None]:
    if not rep.get("steps"):
        return [None, None]
    final = rep["steps"][-1]
    return [final[p].get("status") if p < len(final) else None for p in (0, 1)]


def run_pair(seed: int, agents: list) -> dict:
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    rep = env.toJSON()
    return {
        "rewards": final_rewards(rep),
        "statuses": final_statuses(rep),
        "steps": len(rep.get("steps", [])),
    }


def winner_index(rewards: list[float | None]) -> int | None:
    if len(rewards) != 2 or any(r is None for r in rewards):
        return None
    if rewards[0] == rewards[1]:
        return None
    return 0 if rewards[0] > rewards[1] else 1


def exact_rewards(a: list[float | None], b: list[float | None]) -> bool:
    return len(a) == len(b) == 2 and all(x is not None and y is not None and float(x) == float(y) for x, y in zip(a, b))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if not 1 <= args.top <= 20:
        raise SystemExit("--top must be 1..20")

    r4b = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
    rows = []

    with tempfile.TemporaryDirectory(prefix="kculture-action-tape-") as tmp:
        root = Path(tmp)
        index = sorted(read_csv(download(INDEX_HANDLE, "manifest.csv", root / "index")), key=lambda r: r["date"])
        idx_row = next((r for r in index if r["date"] == args.date), None)
        if idx_row is None:
            raise RuntimeError(f"date {args.date} absent from official index")
        handle = f"kaggle/kaggriculture-episodes-{args.date}"
        manifest = sorted(read_csv(download(handle, "manifest.csv", root / "day")), key=lambda r: -float(r["avg_score"]))[:args.top]

        for mr in manifest:
            eid = str(mr["episode_id"])
            rep = json.loads(download(handle, f"{eid}.json", root / "episodes" / eid).read_text(encoding="utf-8"))
            seed = (rep.get("info") or {}).get("seed")
            if not isinstance(seed, int):
                try:
                    seed = int(seed)
                except (TypeError, ValueError):
                    raise RuntimeError(f"episode {eid} missing reproducible integer seed: {seed!r}")
            names = (rep.get("info") or {}).get("TeamNames") or ["p0", "p1"]
            original = final_rewards(rep)
            tapes = [actions_for(rep, 0), actions_for(rep, 1)]

            replay = run_pair(seed, [tape_agent(tapes[0]), tape_agent(tapes[1])])
            reproducible = replay["steps"] == 720 and exact_rewards(original, replay["rewards"]) and all(s == "DONE" for s in replay["statuses"])

            row = {
                "episode_id": eid,
                "avg_score": float(mr["avg_score"]),
                "seed": int(seed),
                "team_names": names,
                "original_rewards": original,
                "tape_replay_rewards": replay["rewards"],
                "tape_replay_statuses": replay["statuses"],
                "tape_replay_steps": replay["steps"],
                "exact_terminal_reproduction": reproducible,
                "benchmark": None,
            }

            if reproducible:
                wi = winner_index(original)
                if wi is not None:
                    li = 1 - wi
                    agents = [None, None]
                    agents[wi] = tape_agent(tapes[wi])
                    agents[li] = r4b
                    bench = run_pair(seed, agents)
                    r4b_reward = bench["rewards"][li]
                    tape_reward = bench["rewards"][wi]
                    if r4b_reward is None or tape_reward is None:
                        outcome = "ERROR"
                        delta = None
                    else:
                        delta = float(r4b_reward) - float(tape_reward)
                        outcome = "WIN" if delta > 0 else "LOSS" if delta < 0 else "TIE"
                    row["benchmark"] = {
                        "winner_tape_player": wi,
                        "winner_tape_team": names[wi] if wi < len(names) else f"p{wi}",
                        "r4b_player": li,
                        "rewards": bench["rewards"],
                        "statuses": bench["statuses"],
                        "steps": bench["steps"],
                        "r4b_terminal_delta": delta,
                        "r4b_outcome": outcome,
                        "tape_reward_change_vs_original": None if tape_reward is None else float(tape_reward) - float(original[wi]),
                    }
            rows.append(row)

    exact = [r for r in rows if r["exact_terminal_reproduction"]]
    benches = [r["benchmark"] for r in exact if isinstance(r.get("benchmark"), dict)]
    valid = [b for b in benches if b["r4b_outcome"] in {"WIN", "LOSS", "TIE"} and b["steps"] == 720 and all(s == "DONE" for s in b["statuses"])]
    wins = sum(b["r4b_outcome"] == "WIN" for b in valid)
    losses = sum(b["r4b_outcome"] == "LOSS" for b in valid)
    ties = sum(b["r4b_outcome"] == "TIE" for b in valid)
    deltas = [float(b["r4b_terminal_delta"]) for b in valid if isinstance(b.get("r4b_terminal_delta"), (int, float))]
    tape_changes = [abs(float(b["tape_reward_change_vs_original"])) for b in valid if isinstance(b.get("tape_reward_change_vs_original"), (int, float))]

    report = {
        "schema_version": "live-meta-action-tape-benchmark-v1",
        "source": {"date": args.date, "top_n": args.top},
        "replayability": {
            "episodes": len(rows),
            "exact_terminal_reproductions": len(exact),
            "fraction": len(exact) / len(rows) if rows else None,
        },
        "r4b_vs_original_winner_tapes": {
            "valid_games": len(valid),
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "score_rate_tie_half": (wins + 0.5 * ties) / len(valid) if valid else None,
            "mean_terminal_delta": statistics.mean(deltas) if deltas else None,
            "median_terminal_delta": statistics.median(deltas) if deltas else None,
            "mean_abs_winner_tape_reward_change_vs_original": statistics.mean(tape_changes) if tape_changes else None,
        },
        "episodes": rows,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"replayability": report["replayability"], "benchmark": report["r4b_vs_original_winner_tapes"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
