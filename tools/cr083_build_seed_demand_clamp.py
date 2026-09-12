"""Build the single frozen CR083 Phase-2 route-aware seed-demand clamp.

The exact CR071M policy is preserved. After the last possible route switch (step 433),
BUY_SEED quantities in the final market queue are clamped to the selected route's
maximum remaining PLANT demand after projecting same-turn physical seed consumption.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

BASE_SHA = "dbc6fc2b2c3673b1d9fc36e103b8369a53c7f2cc33381e11a3cb5f769bebe652"
CLAMP_START = 434


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        f = tf.extractfile(tf.getmember("main.py"))
        if f is None:
            raise RuntimeError("main.py missing")
        return f.read().decode("utf-8")


def patch_source(source: str) -> str:
    # Add a route-local maximum future PLANT-demand counter next to future_sells.
    anchor = (
        "    def _switch_ok(self, target, turn):\n"
        "        \"\"\"A switch is legal only onto a tail identical to the current one so far.\"\"\"\n"
    )
    if source.count(anchor) != 1:
        raise RuntimeError("CR071M switch anchor mismatch")
    helper = (
        "    def future_plants(self, crop, step):\n"
        "        \"\"\"Maximum remaining PLANT commands for crop on the selected own route.\"\"\"\n"
        "        r = self.R[self.cur]\n"
        "        total = 0\n"
        "        for t in range(max(0, step), len(r)):\n"
        "            a = r[t]\n"
        "            acts = [a.get(\"farmer\") or [\"PASS\"], *(a.get(\"hands\") or [])]\n"
        "            for x in acts:\n"
        "                if x and len(x) >= 2 and x[0] == \"PLANT\" and x[1] == crop:\n"
        "                    total += 1\n"
        "        return total\n\n"
        + anchor
    )
    source = source.replace(anchor, helper, 1)

    ret = (
        '        return {"farmer": acts[0], "hands": acts[1:],\n'
        '                "market": (market + extra)[:MAX_ORDERS]}\n'
    )
    if source.count(ret) != 1:
        raise RuntimeError("CR071M final return anchor mismatch")
    repl = (
        "        final_market = (market + extra)[:MAX_ORDERS]\n"
        "\n"
        "        # CR083 Phase 2: after all route-switch checkpoints are resolved,\n"
        "        # seeds above the selected route's maximum remaining PLANT demand\n"
        "        # have no liquidation/productive value and are weakly dominated.\n"
        f"        if step >= {CLAMP_START}:\n"
        "            plant_now = {}\n"
        "            for a in acts:\n"
        "                if a and len(a) >= 2 and a[0] == \"PLANT\":\n"
        "                    plant_now[a[1]] = plant_now.get(a[1], 0) + 1\n"
        "            projected_seeds = dict(seeds)\n"
        "            for crop, demand in plant_now.items():\n"
        "                have = max(0, int(projected_seeds.get(crop, 0)))\n"
        "                # Kaggriculture atomic validation blocks ALL same-crop PLANTs\n"
        "                # when demand exceeds stock; otherwise all consume one seed.\n"
        "                if demand <= have:\n"
        "                    projected_seeds[crop] = have - demand\n"
        "            clamped = []\n"
        "            for o in final_market:\n"
        "                if o and len(o) >= 3 and o[0] == \"BUY_SEED\":\n"
        "                    crop = o[1]\n"
        "                    qty = max(0, int(o[2]))\n"
        "                    future = self.future_plants(crop, step + 1)\n"
        "                    have = max(0, int(projected_seeds.get(crop, 0)))\n"
        "                    needed = max(0, future - have)\n"
        "                    keep = min(qty, needed)\n"
        "                    if keep > 0:\n"
        "                        clamped.append([\"BUY_SEED\", crop, keep])\n"
        "                        projected_seeds[crop] = have + keep\n"
        "                else:\n"
        "                    clamped.append(o)\n"
        "            final_market = clamped\n"
        "\n"
        '        return {"farmer": acts[0], "hands": acts[1:],\n'
        '                "market": final_market}\n'
    )
    source = source.replace(ret, repl, 1)
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


def static_route_audit(source: str) -> dict:
    ns = {"__name__": "cr083_static_audit"}
    exec(compile(source, "main.py", "exec"), ns)
    R = ns["routes"]()
    rows = []
    for h, r in sorted(R.items()):
        buy = plant = 0
        by_crop = {}
        for t in range(CLAMP_START, len(r)):
            a = r[t]
            for o in (a.get("market") or []):
                if o and len(o) >= 3 and o[0] == "BUY_SEED":
                    q = max(0, int(o[2])); buy += q
                    by_crop.setdefault(o[1], {"buy": 0, "plant": 0})["buy"] += q
            acts = [a.get("farmer") or ["PASS"], *(a.get("hands") or [])]
            for x in acts:
                if x and len(x) >= 2 and x[0] == "PLANT":
                    plant += 1
                    by_crop.setdefault(x[1], {"buy": 0, "plant": 0})["plant"] += 1
        rows.append({"route": h, "post434_seed_buys": buy, "post434_plant_commands": plant, "by_crop": by_crop})
    return {"routes": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()

    base_bytes = a.base.read_bytes()
    base_sha = sha256_bytes(base_bytes)
    if base_sha != BASE_SHA:
        raise RuntimeError(f"frozen CR071M SHA mismatch: {base_sha}")
    source = extract_main(a.base)
    patched = patch_source(source)
    write_deterministic_tar_gz(a.output, patched)
    out_sha = sha256_bytes(a.output.read_bytes())

    audit = static_route_audit(source)
    manifest = {
        "schema_version": "cr083-phase2-seed-demand-clamp-v1",
        "candidate": "CR083",
        "base": "CR071M",
        "base_sha256": base_sha,
        "candidate_sha256": out_sha,
        "clamp_start_step": CLAMP_START,
        "last_route_switch_step": 433,
        "rule": "BUY_SEED <= max future selected-route PLANT demand minus projected post-current-turn seed stock",
        "same_turn_atomic_plant_accounting": True,
        "farmer_hands_modified": False,
        "route_switch_modified": False,
        "non_seed_market_logic_modified": False,
        "seed_quantity_can_increase": False,
        "teacher_imitation": False,
        "identity_episode_seed_future_opponent_private_features": False,
        "static_route_audit": audit,
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
