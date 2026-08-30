"""CR023 mechanical-only probe for exact public top-ladder action tapes.

The tool downloads three frozen public episode replays at runtime using Kaggle
authentication, extracts only the referenced submission seat's action tape in
memory/temp storage, and checks whether that tape completes fresh local games in
both seats. It intentionally does NOT print/store rewards or commit replay/tape
data. This is a mechanical feasibility probe, not strategic selection evidence.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
R4B = ROOT / "candidates/r4b_ablation_market_only.py"

ROUTES = {
    "top11_openloop": {"episode_id": 102908981, "source_seat": 1, "submission_id": 55858273},
    "top16_openloop": {"episode_id": 102915518, "source_seat": 1, "submission_id": 55847696},
    "top19_openloop": {"episode_id": 102895545, "source_seat": 1, "submission_id": 55872138},
}

# Old non-preregistered seeds used only to prove the tape can execute.
PROBE_SEEDS = (2026082901, 2026082903, 2026082905)


def load_agent(path: Path):
    spec = importlib.util.spec_from_file_location(f"cr023_r4b_{time.time_ns()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


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
    p = folder / f"episode-{int(episode_id)}-replay.json"
    if not p.exists():
        raise RuntimeError(f"missing replay {episode_id}")
    return p


def extract_tape(path: Path, source_seat: int):
    rep = json.loads(path.read_text(encoding="utf-8"))
    steps = rep.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay: {len(steps)}")
    tape = []
    for t in range(719):
        frame = steps[t + 1][source_seat]
        action = frame.get("action") if isinstance(frame, dict) else None
        tape.append(copy.deepcopy(action or {}))
    return tape


def tape_agent(tape):
    def agent(obs, config=None):
        t = max(0, min(718, clock(obs)))
        return copy.deepcopy(tape[t])
    return agent


def run_case(tape, seed: int, tape_seat: int):
    base = load_agent(R4B)
    ta = tape_agent(tape)
    agents = [ta, base] if tape_seat == 0 else [base, ta]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    final = env.toJSON()["steps"][-1]
    statuses = [final[i].get("status") for i in range(2)]
    # Do not inspect or report reward in this mechanical-only probe.
    return statuses == ["DONE", "DONE"], statuses


def main():
    api = KaggleApi(); api.authenticate()
    results = {}
    with tempfile.TemporaryDirectory(prefix="kculture-cr023-") as td:
        root = Path(td)
        for rid, meta in ROUTES.items():
            p = download_replay(api, meta["episode_id"], root)
            tape = extract_tape(p, meta["source_seat"])
            cases = []
            for seed in PROBE_SEEDS:
                for seat in (0, 1):
                    ok, statuses = run_case(tape, seed, seat)
                    cases.append({"seed": seed, "seat": seat, "done": ok, "statuses": statuses})
            results[rid] = {
                "submission_id": meta["submission_id"],
                "episode_id": meta["episode_id"],
                "tape_actions": len(tape),
                "cases": len(cases),
                "all_done": all(c["done"] for c in cases),
                "case_status": cases,
            }
    compact = {
        "experiment": "CR023 mechanical-only public-tape probe",
        "reward_observed_or_reported": False,
        "routes": results,
        "all_routes_mechanical_pass": all(v["all_done"] for v in results.values()),
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    if not compact["all_routes_mechanical_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
