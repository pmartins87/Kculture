"""CR035 mechanical infrastructure fix: download and verify frozen sources once.

This does not alter CR035 strategy, classifier, threshold, switch clock, candidates,
or promotion gate. It only avoids concurrent Kaggle downloads that triggered HTTP 429.
"""
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi

import cr035_public_regime_selector_shard as core

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr031_elite_round_robin.json"
OUT = ROOT / "artifacts/cr035_source_bundle"


def _retry_dataset_episode(eid: int, out: Path) -> dict:
    waits = (0, 5, 10, 20, 40, 80, 120)
    last: Exception | None = None
    for attempt, wait in enumerate(waits, start=1):
        if wait:
            print(f"retry wait {wait}s for elite episode {eid}", flush=True)
            time.sleep(wait)
        try:
            out.mkdir(parents=True, exist_ok=True)
            p = Path(
                kagglehub.dataset_download(
                    core.HANDLE,
                    path=f"{eid}.json",
                    output_dir=str(out),
                    force_download=True,
                )
            )
            if not p.is_file():
                raise FileNotFoundError(p)
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # network/rate-limit retry only; provenance is checked later
            last = exc
            print(f"elite episode {eid} attempt {attempt} failed: {exc!r}", flush=True)
    raise RuntimeError(f"unable to download elite episode {eid} after retries") from last


def _retry_recent_replay(api: KaggleApi, eid: int, out: Path) -> dict:
    waits = (0, 5, 10, 20, 40, 80, 120)
    last: Exception | None = None
    for attempt, wait in enumerate(waits, start=1):
        if wait:
            print(f"retry wait {wait}s for CR029 replay {eid}", flush=True)
            time.sleep(wait)
        try:
            out.mkdir(parents=True, exist_ok=True)
            api.competition_episode_replay(eid, path=str(out), quiet=True)
            p = out / f"episode-{eid}-replay.json"
            if not p.is_file():
                raise FileNotFoundError(p)
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            last = exc
            print(f"CR029 replay {eid} attempt {attempt} failed: {exc!r}", flush=True)
    raise RuntimeError(f"unable to download CR029 replay {eid} after retries") from last


def main() -> None:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    api = KaggleApi()
    api.authenticate()
    OUT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cr035-bundle-") as td_raw:
        td = Path(td_raw)

        recent = cfg["recent_top"]
        recent_eid = int(recent["episode_id"])
        recent_rep = _retry_recent_replay(api, recent_eid, td / "recent")
        base_tape = core._actions(recent_rep, int(recent["source_seat"]))
        observed_base = core._tape_sha(base_tape)
        if len(base_tape) != 719 or observed_base != recent["tape_sha256"]:
            raise RuntimeError(
                f"CR029 provenance mismatch len={len(base_tape)} sha={observed_base}"
            )

        scenarios: dict[str, dict] = {}
        for s in cfg["scenarios"]:
            rank = int(s["rank"])
            eid = int(s["episode_id"])
            rep = _retry_dataset_episode(eid, td / "episodes" / str(eid))
            tape = core._actions(rep, int(s["winner_seat"]))
            observed_sha = core._tape_sha(tape)
            if len(tape) != 719 or observed_sha != s["tape_sha256"]:
                raise RuntimeError(
                    f"elite r{rank} provenance mismatch len={len(tape)} sha={observed_sha}"
                )
            info = rep.get("info") or {}
            observed_seed = int(info.get("seed"))
            if observed_seed != int(s["seed"]):
                raise RuntimeError(
                    f"elite r{rank} seed mismatch {observed_seed} != {int(s['seed'])}"
                )
            scenarios[str(rank)] = {
                "rank": rank,
                "episode_id": eid,
                "seed": observed_seed,
                "team": s["team"],
                "winner_seat": int(s["winner_seat"]),
                "tape_sha256": observed_sha,
                "configuration": rep.get("configuration") if isinstance(rep.get("configuration"), dict) else {},
                "tape": tape,
            }
            print(f"verified elite r{rank:02d} episode={eid} sha={observed_sha}", flush=True)

        bundle = {
            "schema_version": "cr035-source-bundle-v1",
            "purpose": "mechanical_retry_of_frozen_CR035_only",
            "recent_top": {
                "episode_id": recent_eid,
                "source_seat": int(recent["source_seat"]),
                "tape_sha256": observed_base,
                "tape": base_tape,
            },
            "scenarios": scenarios,
            "classifier": {
                "feature": "self_money",
                "threshold": core.SELF_MONEY_THRESHOLD,
                "switch_clock": core.SWITCH_CLOCK,
            },
            "source_scenarios_already_open": True,
            "fresh_validation_touched": False,
            "held_out_touched": False,
            "runtime_identity_features": False,
        }
        path = OUT / "source_bundle.json"
        path.write_text(json.dumps(bundle, separators=(",", ":"), sort_keys=True), encoding="utf-8")
        summary = {
            "schema_version": bundle["schema_version"],
            "recent_top_sha256": observed_base,
            "scenario_count": len(scenarios),
            "scenario_ranks": sorted(int(x) for x in scenarios),
            "classifier": bundle["classifier"],
            "fresh_validation_touched": False,
            "held_out_touched": False,
        }
        (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
