"""Prepare frozen CR028 recent-top full and prefix-splice action tapes.

The source replay and CR024 control are downloaded through the authenticated
competition API. Public stream hashes are verified before any candidate file is
written. This tool performs no strategic outcome evaluation.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

from cr026_live_meta_cr024_benchmark import build_cr024

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr028_recent_top_splice_screen.json"
OUT = ROOT / "artifacts/cr028_stagea/prepared"


def canonical(action: dict) -> bytes:
    return json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")


def stream_hash(actions: list[dict], n: int) -> str:
    # georgymamarin/kaggriculture-episodes stream_hashes convention, verified
    # against public replay data: canonical JSON followed by NUL per action.
    body = b"".join(canonical(a) + b"\0" for a in actions[:n])
    return hashlib.sha256(body).hexdigest()[:16]


def tape_sha(actions: list[dict]) -> str:
    body = json.dumps(actions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def actions_for(replay: dict, seat: int) -> list[dict]:
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay: {len(steps)}")
    return [copy.deepcopy((steps[t + 1][seat] or {}).get("action") or {}) for t in range(719)]


def seed_values(obj) -> set[int]:
    out: set[int] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "seed" in str(k).lower():
                vals = v if isinstance(v, list) else [v]
                for x in vals:
                    try: out.add(int(x))
                    except Exception: pass
            out |= seed_values(v)
    elif isinstance(obj, list):
        for v in obj: out |= seed_values(v)
    return out


def main() -> None:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    fresh = set(int(x) for x in cfg["fresh_seeds"])
    forbidden = set()
    for p in (ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json", ROOT / "configs/cr027_frontier_screen.json"):
        forbidden |= seed_values(json.loads(p.read_text(encoding="utf-8")))
    overlap = sorted(fresh & forbidden)
    if overlap:
        raise RuntimeError(f"fresh seed firewall overlap: {overlap}")

    api = KaggleApi(); api.authenticate()
    OUT.mkdir(parents=True, exist_ok=True)
    source = cfg["source"]
    with tempfile.TemporaryDirectory(prefix="cr028-prepare-") as td:
        tmp = Path(td)
        api.competition_episode_replay(int(source["episode_id"]), path=str(tmp), quiet=True)
        replay_path = tmp / f"episode-{int(source['episode_id'])}-replay.json"
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        recent = actions_for(replay, int(source["source_seat"]))
        cr024, cr024_provenance = build_cr024(tmp / "cr024")

    if len(recent) != 719 or len(cr024) != 719:
        raise RuntimeError((len(recent), len(cr024)))

    verified = {}
    for raw_n, expected in source["expected_stream_hashes"].items():
        n = int(raw_n)
        observed = stream_hash(recent, n)
        verified[str(n)] = {"expected": expected, "observed": observed, "exact": observed == expected}
    if not all(v["exact"] for v in verified.values()):
        raise RuntimeError(f"source stream hash mismatch: {verified}")

    manifest = {
        "experiment": cfg["experiment"],
        "source": source,
        "source_stream_verification": verified,
        "source_tape_sha256": tape_sha(recent),
        "cr024_provenance": cr024_provenance,
        "cr024_tape_sha256": tape_sha(cr024),
        "fresh_seeds": sorted(fresh),
        "seed_firewall_forbidden_count": len(forbidden),
        "variants": [],
        "held_out_touched": False,
        "strategic_outcomes_used": False
    }
    (OUT / "cr024_actions.json").write_text(json.dumps(cr024, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    for vm in cfg["variants"]:
        n = int(vm["recent_prefix_turns"])
        if not 0 <= n <= 719:
            raise RuntimeError(vm)
        tape = copy.deepcopy(recent[:n]) + copy.deepcopy(cr024[n:])
        if len(tape) != 719:
            raise RuntimeError((vm, len(tape)))
        path = OUT / f"{vm['id']}.json"
        path.write_text(json.dumps(tape, separators=(",", ":"), sort_keys=True), encoding="utf-8")
        manifest["variants"].append({**vm, "file": path.name, "tape_sha256": tape_sha(tape)})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
