"""Source-package parity and activation audit for CR-015.

Mechanical audit.  Hosted submission remains unauthorized unless the separate
preregistered strategic gates pass.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr004_adaptation_signal import download, read_csv

DATE = "2026-08-26"
TOP = 20
SOURCE = ROOT / "candidates/cr015_liquidation_phase_early_order.py"
PACKAGE = ROOT / "artifacts/submissions/cr015_liquidation_phase_v1/Kculture_CR015_liquidation_phase_early_v1/main.py"
R4B = ROOT / "candidates/r4b_ablation_market_only.py"
CR008 = ROOT / "candidates/cr008_adaptive_frontrun.py"
CR011 = ROOT / "candidates/cr011_adaptive_early_order.py"
OUT = ROOT / "artifacts/submissions/cr015_liquidation_phase_v1/parity.json"


def load(path: Path):
    spec = importlib.util.spec_from_file_location(f"cr015audit_{path.stem}_{time.time_ns()}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    states = 0
    mismatches = 0
    examples = []
    changes_vs_r4b = 0
    equals_cr008_on_changes = 0
    equals_cr011_on_changes = 0
    other_on_changes = 0
    episodes = 0

    with tempfile.TemporaryDirectory(prefix="kculture-cr015-package-audit-") as tmp:
        root = Path(tmp)
        handle = f"kaggle/kaggriculture-episodes-{DATE}"
        manifest = sorted(
            read_csv(download(handle, "manifest.csv", root / "manifest")),
            key=lambda r: -float(r.get("avg_score") or 0),
        )[:TOP]
        for row in manifest:
            eid = str(row["episode_id"])
            rep = json.loads(download(handle, f"{eid}.json", root / "episodes" / eid).read_text())
            steps = rep.get("steps") or []
            if len(steps) < 720:
                continue
            episodes += 1
            for player in (0, 1):
                src = load(SOURCE)
                pkg = load(PACKAGE)
                r4b = load(R4B)
                c8 = load(CR008)
                c11 = load(CR011)
                for t in range(min(719, len(steps))):
                    state = steps[t][player]
                    obs = state.get("observation") if isinstance(state, dict) else None
                    if not isinstance(obs, dict):
                        continue
                    sa = src.agent(obs, None)
                    pa = pkg.agent(obs, None)
                    ba = r4b.agent(obs, None)
                    a8 = c8.agent(obs, None)
                    a11 = c11.agent(obs, None)
                    states += 1
                    if sa != pa:
                        mismatches += 1
                        if len(examples) < 10:
                            examples.append({"episode": eid, "state": t, "player": player, "source": sa, "package": pa})
                    if sa != ba:
                        changes_vs_r4b += 1
                        if sa == a8:
                            equals_cr008_on_changes += 1
                        elif sa == a11:
                            equals_cr011_on_changes += 1
                        else:
                            other_on_changes += 1

    payload = {
        "schema_version": "cr015-package-parity-v1",
        "source_date": DATE,
        "episodes": episodes,
        "states": states,
        "mismatches": mismatches,
        "examples": examples,
        "changes_vs_r4b": changes_vs_r4b,
        "equals_cr008_on_changes": equals_cr008_on_changes,
        "equals_cr011_on_changes": equals_cr011_on_changes,
        "other_on_changes": other_on_changes,
    }
    payload["passed"] = (
        episodes >= 10
        and states >= 10000
        and mismatches == 0
        and changes_vs_r4b > 0
        and equals_cr008_on_changes > 0
        and equals_cr011_on_changes > 0
        and other_on_changes == 0
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = dict(payload); compact.pop("examples", None)
    print(json.dumps(compact, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
