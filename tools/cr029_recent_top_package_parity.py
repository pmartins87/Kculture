"""Exact game-trace parity for CR029 full_recent_top research tape vs package.

Uses only already-open CR023 raw Stage-A seeds and the local simple_crop opponent.
No reserved or held-out CR029 data are touched.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import tarfile
import tempfile
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CFG = ROOT / "configs/cr029_fresh_official_meta_calibration.json"
OPEN_CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
EXPECTED_TAPE_SHA256 = "6c56840b9510e0688da2fbec47e8f89583c63a0124fa4c8801fa5d93c197226b"


def load_module(path: Path, prefix: str):
    spec = importlib.util.spec_from_file_location(f"{prefix}_{time.time_ns()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canonical_tape_sha(actions: list[dict]) -> str:
    import hashlib
    body = json.dumps(actions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def trace(env, seat: int) -> list[str]:
    out = []
    for frame in env.toJSON()["steps"][1:]:
        action = (frame[seat] or {}).get("action") if isinstance(frame[seat], dict) else None
        out.append(json.dumps(action or {}, sort_keys=True, separators=(",", ":")))
    return out


def run(agent, opponent_path: Path, seed: int, seat: int):
    opponent = load_module(opponent_path, "cr029_parity_opp").agent
    agents = [agent, opponent] if seat == 0 else [opponent, agent]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    final = env.toJSON()["steps"][-1]
    statuses = [final[i].get("status") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses: {statuses}")
    return {
        "trace": trace(env, seat),
        "self": float(final[seat].get("reward")),
        "opp": float(final[1 - seat].get("reward")),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src_cfg = json.loads(SOURCE_CFG.read_text(encoding="utf-8"))
    open_cfg = json.loads(OPEN_CFG.read_text(encoding="utf-8"))
    open_seeds = [int(x) for x in open_cfg["raw_backbone_stage_a_seeds"]]
    seeds = [open_seeds[0], open_seeds[len(open_seeds) // 2], open_seeds[-1]]

    reserved = set(int(x) for x in open_cfg.get("adaptive_overlay_stage_a_seeds_reserved", []))
    reserved |= set(int(x) for x in open_cfg.get("adaptive_overlay_stage_b_seeds_reserved", []))
    held = set(int(x) for x in open_cfg.get("held_out_seeds", [])) if isinstance(open_cfg.get("held_out_seeds"), list) else set()
    cr029_fresh = set(int(x) for x in src_cfg.get("fresh_pairwise_seeds", []))
    if set(seeds) & (reserved | held | cr029_fresh):
        raise SystemExit("seed firewall violation")

    source = src_cfg["recent_top_source"]
    api = KaggleApi(); api.authenticate()
    rows = []
    errors = []

    with tempfile.TemporaryDirectory(prefix="cr029-parity-") as td_raw:
        td = Path(td_raw)
        episode_id = int(source["episode_id"])
        api.competition_episode_replay(episode_id, path=str(td), quiet=True)
        replay = json.loads((td / f"episode-{episode_id}-replay.json").read_text(encoding="utf-8"))
        steps = replay.get("steps") or []
        tape = [copy.deepcopy((steps[t + 1][int(source["source_seat"])] or {}).get("action") or {}) for t in range(719)]
        if canonical_tape_sha(tape) != EXPECTED_TAPE_SHA256:
            raise RuntimeError("source tape identity mismatch")

        def research_agent(obs, config=None):
            try:
                raw = obs.get("step")
                step = int(raw) if raw is not None else int(obs.get("day") or 0) * 24 + int(obs.get("hour") or 0)
            except Exception:
                step = 0
            return copy.deepcopy(tape[max(0, min(718, step))])

        with tarfile.open(args.archive, "r:gz") as tf:
            fh = tf.extractfile(tf.getmember("main.py"))
            package_main = td / "package_main.py"
            package_main.write_bytes(fh.read() if fh else b"")

        opp_path = ROOT / "opponents/simple_crop.py"
        for seed in seeds:
            for seat in (0, 1):
                try:
                    package_agent = load_module(package_main, "cr029_pkg").agent
                    a = run(research_agent, opp_path, seed, seat)
                    b = run(package_agent, opp_path, seed, seat)
                    same_trace = a["trace"] == b["trace"]
                    same_rewards = a["self"] == b["self"] and a["opp"] == b["opp"]
                    first_diff = None
                    if not same_trace:
                        n = min(len(a["trace"]), len(b["trace"]))
                        first_diff = next((i for i in range(n) if a["trace"][i] != b["trace"][i]), n if len(a["trace"]) != len(b["trace"]) else None)
                    row = {
                        "seed": seed,
                        "seat": seat,
                        "same_trace": same_trace,
                        "same_rewards": same_rewards,
                        "first_diff": first_diff,
                        "research_reward": a["self"],
                        "package_reward": b["self"],
                    }
                    rows.append(row)
                    if not same_trace or not same_rewards:
                        errors.append(row)
                except Exception as exc:
                    errors.append({"seed": seed, "seat": seat, "error": repr(exc)})

    report = {
        "experiment": "CR029_FULL_RECENT_TOP_V1_PACKAGE_PARITY",
        "seed_class": "CR023_RAW_STAGE_A_ALREADY_OPEN_ONLY",
        "seeds": seeds,
        "rows": rows,
        "row_count": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "decision": "PASS" if len(rows) == len(seeds) * 2 and not errors else "FAIL",
        "cr029_fresh_touched": False,
        "reserved_touched": False,
        "held_out_touched": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["decision"] != "PASS":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
