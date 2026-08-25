"""R1 smoke test for the frozen Kaggriculture reference baseline.

Checks:
1. Kculture root `main.py` completes a full 720-turn episode.
2. On fixed seeds, Kculture's port produces the same final player-0 state as
   Kaggle's built-in `starter` when each is run independently versus `pass`.
3. Kculture self-play completes with both agents DONE.

The script writes a compact JSON artifact for experiment traceability.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import agent as kculture_agent  # noqa: E402


PARITY_SEEDS = (101, 202, 303)
SELF_PLAY_SEED = 404


def _run(agent0, agent1, seed: int):
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=True,
    )
    env.run([agent0, agent1])
    payload = env.toJSON()
    final = payload["steps"][-1]

    return {
        "seed": seed,
        "p0_status": final[0]["status"],
        "p1_status": final[1]["status"],
        "p0_reward": final[0]["reward"],
        "p1_reward": final[1]["reward"],
        "p0_observation": final[0]["observation"],
    }


def _parity_view(result):
    obs = result["p0_observation"]
    return {
        "p0_status": result["p0_status"],
        "p0_reward": result["p0_reward"],
        "farm0": obs["farms"][0],
        "private": obs.get("private", {}),
        "market": obs.get("market", {}),
        "town": obs.get("town", {}),
        "day": obs.get("day"),
        "hour": obs.get("hour"),
    }


def main():
    parity = []
    for seed in PARITY_SEEDS:
        local = _run(kculture_agent, "pass", seed)
        official = _run("starter", "pass", seed)

        assert local["p0_status"] == "DONE", local
        assert official["p0_status"] == "DONE", official
        assert _parity_view(local) == _parity_view(official), (
            f"starter parity failed for seed {seed}"
        )

        parity.append(
            {
                "seed": seed,
                "reward": local["p0_reward"],
                "status": local["p0_status"],
                "parity": "PASS",
            }
        )

    self_play = _run(kculture_agent, kculture_agent, SELF_PLAY_SEED)
    assert self_play["p0_status"] == "DONE", self_play
    assert self_play["p1_status"] == "DONE", self_play

    report = {
        "environment": "kaggriculture",
        "episode_steps": 720,
        "baseline": "official-starter-carrot-port",
        "parity": parity,
        "self_play": {
            "seed": SELF_PLAY_SEED,
            "p0_status": self_play["p0_status"],
            "p1_status": self_play["p1_status"],
            "p0_reward": self_play["p0_reward"],
            "p1_reward": self_play["p1_reward"],
        },
        "result": "PASS",
    }

    out_dir = ROOT / "artifacts"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "baseline_smoke.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
