"""Build the single frozen CR081 current-3056 lineage bridge.

Architecture is fixed by CR081_GATE_A_RESULT_2026-09-11.md:
- base = exact CR071M package source;
- delay the CR071M route backbone by one turn (step 0 is PASS);
- for steps 0..287 replace only the base market queue with the UMG development-only
  per-step modal market queue;
- keep CR071M public route decisions and safety/repair logic;
- extend sell clamping inside the stable prefix so an earlier same-turn BUY_PRODUCT
  can legally fund a later SELL, required by the observed UMG buy->sell market cycle;
- no replay selection, target identity feature, seed, future state or opponent private state.

Holdout episodes are never used to construct the runtime policy.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import statistics
import tarfile
import tempfile
from collections import Counter
from pathlib import Path

UMG = "Unknown Mother-Goose"
PREFIX = 288


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replay_files(root: Path):
    return sorted(root.rglob("episode-*-replay.json"), key=lambda p: int(p.name.split("-")[1]))


def read_record(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    teams = list(d.get("info", {}).get("TeamNames") or [])
    seats = [i for i, t in enumerate(teams) if t == UMG]
    if len(seats) != 1 or len(d.get("steps") or []) < PREFIX:
        return None
    seat = seats[0]
    return {
        "episode": int(d.get("info", {}).get("EpisodeId") or path.name.split("-")[1]),
        "market": [d["steps"][s][seat]["action"].get("market") or [] for s in range(PREFIX)],
    }


def modal_market(umg_root: Path):
    rows = [r for p in replay_files(umg_root) if (r := read_record(p)) is not None]
    rows.sort(key=lambda r: r["episode"])
    cut = int(len(rows) * 0.75)
    dev, hold = rows[:cut], rows[cut:]
    if len(dev) < 10 or not hold:
        raise RuntimeError("insufficient usable episodes")
    policy, support = [], []
    for s in range(PREFIX):
        c = Counter(json.dumps(r["market"][s], sort_keys=True, separators=(",", ":")) for r in dev)
        k, n = c.most_common(1)[0]
        policy.append(json.loads(k))
        support.append(n / len(dev))
    blocks = []
    for a in (0, 96, 192):
        blocks.append({"start": a, "end": a + 95, "mean_market_support": statistics.mean(support[a:a+96])})
    # Frozen development-only rationale for PREFIX=288.
    if min(b["mean_market_support"] for b in blocks) < 0.80:
        raise RuntimeError(f"frozen 0..287 development support no longer satisfies evidence: {blocks}")
    return rows, dev, hold, policy, support, blocks


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        member = tf.getmember("main.py")
        f = tf.extractfile(member)
        if f is None:
            raise RuntimeError("CR071M package missing main.py")
        return f.read().decode("utf-8")


def patch_source(source: str, policy: list[list]) -> str:
    const_anchor = "_CR053_COUNTER_LEAD = 1\n\n_BLOB = ("
    if source.count(const_anchor) != 1:
        raise RuntimeError("CR071M constant anchor mismatch")
    constants = (
        "_CR053_COUNTER_LEAD = 1\n\n"
        "# CR081 frozen current-3056 bridge: development-only UMG market prefix.\n"
        f"CR081_PREFIX = {PREFIX}\n"
        "CR081_MARKET = " + repr(policy) + "\n\n"
        "_BLOB = ("
    )
    source = source.replace(const_anchor, constants, 1)

    base_old = "        base = route[step] if step < len(route) else PASS\n"
    base_new = (
        "        # CR081: UMG/bridge lineage begins the conserved route one turn later.\n"
        "        base = PASS if step == 0 else (route[step - 1] if (step - 1) < len(route) else PASS)\n"
    )
    if source.count(base_old) != 1:
        raise RuntimeError("CR071M base-action anchor mismatch")
    source = source.replace(base_old, base_new, 1)

    market_old = "        market = [list(o) for o in (base.get(\"market\") or [])]\n"
    market_new = (
        "        market = [list(o) for o in (base.get(\"market\") or [])]\n"
        "        # CR081: only the frozen stable prefix receives the UMG market queue.\n"
        "        if 0 <= step < CR081_PREFIX:\n"
        "            market = [list(o) for o in CR081_MARKET[step]]\n"
    )
    if source.count(market_old) != 1:
        raise RuntimeError("CR071M market anchor mismatch")
    source = source.replace(market_old, market_new, 1)

    clamp_old = (
        "        for o in market:\n"
        "            if o and o[0] == \"SELL\":\n"
        "                have = avail.get(o[1], 0)\n"
        "                if have <= 0:\n"
        "                    continue\n"
        "                n = min(int(o[2]), have)\n"
        "                if n <= 0:\n"
        "                    continue\n"
        "                avail[o[1]] = have - n\n"
        "                kept.append([\"SELL\", o[1], n])\n"
        "            else:\n"
        "                kept.append(o)\n"
    )
    clamp_new = (
        "        for o in market:\n"
        "            # In the CR081 prefix, market orders are sequential: an earlier\n"
        "            # BUY_PRODUCT can supply a later SELL in the same queue. This is\n"
        "            # required by the observed UMG WHEAT buy->sell cycle at step 1.\n"
        "            if (step < CR081_PREFIX and o and len(o) >= 3\n"
        "                    and o[0] == \"BUY_PRODUCT\"):\n"
        "                avail[o[1]] = avail.get(o[1], 0) + max(0, int(o[2]))\n"
        "                kept.append(o)\n"
        "            elif o and o[0] == \"SELL\":\n"
        "                have = avail.get(o[1], 0)\n"
        "                if have <= 0:\n"
        "                    continue\n"
        "                n = min(int(o[2]), have)\n"
        "                if n <= 0:\n"
        "                    continue\n"
        "                avail[o[1]] = have - n\n"
        "                kept.append([\"SELL\", o[1], n])\n"
        "            else:\n"
        "                kept.append(o)\n"
    )
    if source.count(clamp_old) != 1:
        raise RuntimeError("CR071M clamp-sells anchor mismatch")
    source = source.replace(clamp_old, clamp_new, 1)

    header = (
        '"""CR081 current-3056 lineage bridge.\n\n'
        'Single frozen candidate: delayed conserved CR071M backbone plus development-only\n'
        'UMG market prefix (steps 0..287), with legal same-turn buy->sell accounting.\n'
        'No replay route stitching and no hidden/identity features.\n'
        '"""\n'
    )
    # Replace only the leading module docstring to make runtime provenance obvious.
    if source.startswith('"""'):
        end = source.find('"""', 3)
        if end != -1:
            source = header + source[end + 3:].lstrip("\n")
    return source


def write_tar(path: Path, main_text: str):
    data = main_text.encode("utf-8")
    info = tarfile.TarInfo("main.py")
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as tf:
        tf.addfile(info, io.BytesIO(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--umg-root", type=Path, required=True)
    ap.add_argument("--cr071m", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()

    rows, dev, hold, policy, support, blocks = modal_market(a.umg_root)
    source = extract_main(a.cr071m)
    base_hash = sha256_bytes(a.cr071m.read_bytes())
    patched = patch_source(source, policy)
    compile(patched, "main.py", "exec")
    write_tar(a.output, patched)
    out_hash = sha256_bytes(a.output.read_bytes())

    manifest = {
        "schema_version": "cr081-current3056-bridge-v1",
        "candidate": "CR081",
        "architecture": "delayed CR071M backbone + UMG dev-only modal market prefix",
        "prefix_steps": PREFIX,
        "usable_umg_episodes": len(rows),
        "development_episodes": len(dev),
        "sealed_holdout_episodes_not_used_in_build": len(hold),
        "development_episode_range": [dev[0]["episode"], dev[-1]["episode"]],
        "development_market_support_blocks": blocks,
        "market_nonempty_steps_in_prefix": sum(bool(x) for x in policy),
        "base_cr071m_sha256": base_hash,
        "candidate_sha256": out_hash,
        "same_turn_buy_product_funds_later_sell_in_prefix": True,
        "replay_stitching": False,
        "identity_features": False,
        "holdout_used_for_policy_construction": False,
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
