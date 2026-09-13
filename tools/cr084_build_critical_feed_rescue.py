"""Build the single frozen CR084 critical late-livestock feed rescue.

Base is the exact hosted/local-promoted CR083 package.  CR084 changes only a physical
command that CR083 would send as an engine-certain noop: during steps 576..695, if
that unit is standing on a live animal at immediate escape risk and carries WHEAT,
replace the noop with FEED.  Market logic, route selection and the CR083 seed clamp
are untouched.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

BASE_SHA = "648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8"
START_STEP = 576
END_STEP_EXCLUSIVE = 696


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        member = tf.getmember("main.py")
        f = tf.extractfile(member)
        if f is None:
            raise RuntimeError("main.py missing")
        return f.read().decode("utf-8")


def patch_source(source: str) -> str:
    anchor = (
        '        positions = [tuple(farm["farmer"])] + [tuple(p) for p in farm["hands"]]\n'
        '\n'
        '        # ---- weed_dig: a wasted turn spent standing on a weed becomes a DIG ----\n'
    )
    if source.count(anchor) != 1:
        raise RuntimeError("CR083 physical-action anchor mismatch")
    block = (
        '        positions = [tuple(farm["farmer"])] + [tuple(p) for p in farm["hands"]]\n'
        '\n'
        '        # ---- CR084 critical_feed_rescue ----\n'
        '        # Only replace an engine-certain noop.  The animal must already have\n'
        '        # missed one feed, be unfed today, and this unit must carry WHEAT.\n'
        f'        if {START_STEP} <= step < {END_STEP_EXCLUSIVE}:\n'
        '            for i in range(min(len(acts), len(positions))):\n'
        '                x, y = positions[i]\n'
        '                if not (0 <= x < board and 0 <= y < board):\n'
        '                    continue\n'
        '                tile = tiles[y][x]\n'
        '                if not (isinstance(tile, dict) and tile.get("animal") is not None):\n'
        '                    continue\n'
        '                inv = invs[i] if i < len(invs) else {}\n'
        '                if (not bool(tile.get("fed_today"))\n'
        '                        and int(tile.get("consecutive_unfed", 0)) >= 1\n'
        '                        and int(inv.get("WHEAT", 0)) > 0\n'
        '                        and _noop(acts[i], tile, inv, seeds, x, y, board)):\n'
        '                    acts[i] = ["FEED"]\n'
        '\n'
        '        # ---- weed_dig: a wasted turn spent standing on a weed becomes a DIG ----\n'
    )
    source = source.replace(anchor, block, 1)
    compile(source, "main.py", "exec")
    return source


def write_deterministic_tar_gz(path: Path, main_text: str) -> None:
    data = main_text.encode("utf-8")
    ti = tarfile.TarInfo("main.py")
    ti.size = len(data)
    ti.mode = 0o644
    ti.mtime = 0
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        tf.addfile(ti, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()

    base_bytes = a.base.read_bytes()
    base_sha = sha256_bytes(base_bytes)
    if base_sha != BASE_SHA:
        raise RuntimeError(f"frozen CR083 SHA mismatch: {base_sha}")

    source = extract_main(a.base)
    patched = patch_source(source)
    write_deterministic_tar_gz(a.output, patched)
    out_sha = sha256_bytes(a.output.read_bytes())

    manifest = {
        "schema_version": "cr084-critical-feed-rescue-v1",
        "candidate": "CR084",
        "base": "CR083",
        "base_sha256": base_sha,
        "candidate_sha256": out_sha,
        "activation_start_step": START_STEP,
        "activation_end_step_exclusive": END_STEP_EXCLUSIVE,
        "replacement": "engine-certain noop -> FEED",
        "requires_live_animal": True,
        "requires_fed_today_false": True,
        "requires_consecutive_unfed_at_least": 1,
        "requires_carried_wheat_at_least": 1,
        "route_tapes_modified": False,
        "route_switch_modified": False,
        "market_logic_modified": False,
        "cr083_seed_clamp_modified": False,
        "non_noop_action_can_be_replaced": False,
        "care_repair_enabled": False,
        "identity_episode_seed_future_opponent_private_features": False,
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
