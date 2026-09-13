"""Build frozen CR085: public-Pareto guard on the two late adaptive switches.

Base is exact CR083. Route tapes, thresholds, step 226, market logic and all
repair logic remain unchanged. The only policy change is that the existing
prefix-compatible switches at steps 360 and 433 additionally require our public
farm state to weakly Pareto-dominate the opponent in money, live animals and
active plants.
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
GUARDED_STEPS = (360, 433)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        f = tf.extractfile(tf.getmember("main.py"))
        if f is None:
            raise RuntimeError("main.py missing")
        return f.read().decode("utf-8")


def patch_source(source: str) -> str:
    helper_anchor = (
        'def _feature(obs, name):\n'
        '    if name == "shop_YARN_STORE":\n'
        '        return (obs.get("town", {}).get("unlocked_shops") or []).count("YARN_STORE")\n'
        '    if name == "px_CARROT":\n'
        '        return obs["market"]["prices"].get("CARROT", 0)\n'
        '    if name == "inv_MILK":\n'
        '        return obs["market"]["inventory"].get("MILK", 0)\n'
        '    return 0\n'
        '\n'
    )
    if source.count(helper_anchor) != 1:
        raise RuntimeError("CR083 _feature anchor mismatch")
    helper = helper_anchor + (
        '\n'
        'def _public_pareto_dominant(obs, me):\n'
        '    """Legal current-state guard: money, live animals and active plants."""\n'
        '    farms = obs.get("farms") or []\n'
        '    if len(farms) != 2 or not (0 <= me < 2):\n'
        '        return False\n'
        '    opp = 1 - me\n'
        '    def shape(farm):\n'
        '        animals = plants = 0\n'
        '        for row in (farm.get("tiles", []) or []):\n'
        '            for tile in row or []:\n'
        '                if not isinstance(tile, dict):\n'
        '                    continue\n'
        '                if tile.get("animal") is not None:\n'
        '                    animals += 1\n'
        '                if tile.get("kind") == "PLANT":\n'
        '                    plants += 1\n'
        '        return (float(farm.get("money", 0) or 0), animals, plants)\n'
        '    mine = shape(farms[me])\n'
        '    other = shape(farms[opp])\n'
        '    return all(a >= b for a, b in zip(mine, other))\n'
        '\n'
    )
    source = source.replace(helper_anchor, helper, 1)

    switch_anchor = (
        '        for (turn, feat, thr, target) in DECISIONS:\n'
        '            if turn == step and target != self.cur and self._switch_ok(target, turn):\n'
        '                if _feature(obs, feat) >= thr:\n'
        '                    self.cur = target\n'
    )
    if source.count(switch_anchor) != 1:
        raise RuntimeError("CR083 switch anchor mismatch")
    switch = (
        '        for (turn, feat, thr, target) in DECISIONS:\n'
        '            if turn == step and target != self.cur and self._switch_ok(target, turn):\n'
        '                if _feature(obs, feat) >= thr:\n'
        '                    # CR085: the two late adaptive tails sacrifice later productive\n'
        '                    # capacity, so enter them only from a non-inferior public state.\n'
        '                    # Step 226 is intentionally unchanged.\n'
        '                    if turn in (360, 433) and not _public_pareto_dominant(obs, me):\n'
        '                        continue\n'
        '                    self.cur = target\n'
    )
    source = source.replace(switch_anchor, switch, 1)
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

    patched = patch_source(extract_main(a.base))
    write_deterministic_tar_gz(a.output, patched)
    out_sha = sha256_bytes(a.output.read_bytes())
    manifest = {
        "schema_version": "cr085-pareto-guarded-switch-v1",
        "candidate": "CR085",
        "base": "CR083",
        "base_sha256": base_sha,
        "candidate_sha256": out_sha,
        "guarded_steps": list(GUARDED_STEPS),
        "guard_dimensions": ["public_farm_money", "public_live_animals", "public_active_plants"],
        "guard_relation": "candidate >= opponent in every dimension",
        "fitted_thresholds": False,
        "step_226_modified": False,
        "original_market_thresholds_modified": False,
        "route_tapes_modified": False,
        "market_logic_modified": False,
        "cr083_seed_clamp_modified": False,
        "route_stitching": False,
        "identity_episode_rating_seed_future_opponent_private_features": False,
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
