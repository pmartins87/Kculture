"""Build one conservative CR078 late-mirror breaker from frozen CR071M.

Discovery hypothesis: exact/near-exact Tetsu-family mirrors converge to a very
specific PUBLIC late-game farm shape.  If both farms match that shape at three
widely separated late checkpoints, replace the step-696 fertilizer buy with a
WHEAT sale that the route already intends to execute at step 697.  This uses no
opponent identity, submission id, seed, private opponent state, or future market
information.  Outside the detector, policy bytes/behavior are unchanged.

This builder is a discovery candidate only.  It does not authorize Kaggle
submission; promotion requires fresh exact-reference validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def safe_extract(archive: Path, dst: Path) -> None:
    base = dst.resolve()
    with tarfile.open(archive, "r:*") as tf:
        for m in tf.getmembers():
            target = (dst / m.name).resolve()
            if target != base and base not in target.parents:
                raise RuntimeError(f"unsafe member {m.name}")
            if m.issym() or m.islnk():
                raise RuntimeError("links forbidden")
        tf.extractall(dst)


HELPERS = r'''
    def _cr078_public_shape(self, farm):
        crops = {}
        animals = 0
        weeds = 0
        for row in (farm.get("tiles", []) or []):
            for tile in row or []:
                if not isinstance(tile, dict):
                    continue
                if tile.get("kind") == "PLANT":
                    crop = str(tile.get("crop"))
                    crops[crop] = crops.get(crop, 0) + 1
                if tile.get("kind") == "WEED":
                    weeds += 1
                if tile.get("animal") is not None:
                    animals += 1
        return {
            "hands": len(farm.get("hands", []) or []),
            "quadrants": len(farm.get("unlocked_quadrants", []) or []),
            "crops": crops,
            "animals": animals,
            "weeds": weeds,
        }

    def _cr078_update_mirror_detector(self, obs, step, me):
        expected = {
            650: {"hands": 11, "quadrants": 3, "crops": {"WHEAT": 27, "CARROT": 17, "STRAWBERRY": 13}, "animals": 17, "weeds": 0},
            680: {"hands": 11, "quadrants": 3, "crops": {"WHEAT": 14, "CARROT": 30}, "animals": 17, "weeds": 0},
            696: {"hands": 0, "quadrants": 3, "crops": {"CARROT": 24}, "animals": 17, "weeds": 0},
        }
        if step not in expected:
            return
        farms = list(obs.get("farms", []) or [])
        if len(farms) < 2:
            self._cr078_mirror_stage = -1
            return
        ours = self._cr078_public_shape(farms[me])
        opp = self._cr078_public_shape(farms[1 - me])
        good = ours == expected[step] and opp == expected[step]
        if step == 650:
            self._cr078_mirror_stage = 1 if good else -1
        elif step == 680:
            self._cr078_mirror_stage = 2 if self._cr078_mirror_stage == 1 and good else -1
        elif step == 696:
            self._cr078_mirror_stage = 3 if self._cr078_mirror_stage == 2 and good else -1

    def _cr078_break_late_mirror(self, step, market, proj):
        if step != 696 or self._cr078_mirror_stage != 3:
            return market
        slot = next((i for i, o in enumerate(market)
                     if o and len(o) >= 3 and o[0] == "BUY_PRODUCT" and o[1] == "FERTILIZER"), -1)
        if slot < 0:
            return market
        have = max(0, int(proj.get("WHEAT", 0)))
        planned_next = self._route_window_sells("WHEAT", step + 1, step + 2)
        qty = min(have, max(0, int(planned_next)))
        if qty <= 0:
            return market
        out = [list(o) for o in market]
        out[slot] = ["SELL", "WHEAT", qty]
        return out
'''


def patch_source(src: str) -> str:
    init = "        self._cr053_like = False\n"
    if src.count(init) != 1:
        raise RuntimeError("CR071M init marker mismatch")
    src = src.replace(init, init + "        self._cr078_mirror_stage = 0\n", 1)

    act = "    def act(self, obs):\n"
    if src.count(act) != 1:
        raise RuntimeError("act marker mismatch")
    src = src.replace(act, HELPERS + "\n" + act, 1)

    detector = "        self._cr053_update_detector(obs, step, me)\n"
    if src.count(detector) != 1:
        raise RuntimeError("detector marker mismatch")
    src = src.replace(detector, detector + "        self._cr078_update_mirror_detector(obs, step, me)\n", 1)

    ret = '        return {"farmer": acts[0], "hands": acts[1:],\n                "market": (market + extra)[:MAX_ORDERS]}\n'
    if src.count(ret) != 1:
        raise RuntimeError("final return marker mismatch")
    repl = '        final_market = (market + extra)[:MAX_ORDERS]\n        final_market = self._cr078_break_late_mirror(step, final_market, proj)\n        return {"farmer": acts[0], "hands": acts[1:], "market": final_market}\n'
    src = src.replace(ret, repl, 1)
    compile(src, "<cr078-late-mirror>", "exec")
    return src


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    base = Path(args.base)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cr078-build-") as td:
        root = Path(td)
        safe_extract(base, root)
        main = root / "main.py"
        original = main.read_text(encoding="utf-8")
        patched = patch_source(original)
        main.write_text(patched, encoding="utf-8")
        for c in root.rglob("__pycache__"):
            shutil.rmtree(c, ignore_errors=True)
        for p in root.rglob("*.pyc"):
            p.unlink(missing_ok=True)
        dst = out / "CR078_LATE_MIRROR_BREAKER_V1.tar.gz"
        with tarfile.open(dst, "w:gz") as tf:
            for p in sorted(root.rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                    tf.add(p, arcname=p.relative_to(root).as_posix())
    receipt = {
        "schema_version": "kculture-cr078-late-mirror-breaker-v1",
        "base": str(base),
        "base_sha256": sha256_file(base),
        "archive": dst.name,
        "archive_sha256": sha256_file(dst),
        "public_only_detector": True,
        "checkpoints": [650, 680, 696],
        "intervention_step": 696,
        "intervention": "replace BUY_PRODUCT FERTILIZER slot with route-planned next-step WHEAT sale",
        "automatic_kaggle_submission": False,
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
