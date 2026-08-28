"""Parity and activation gate for hosted R4B / CR-008 / CR-011 packages.

The audit replays official Aug-26 observation streams. Every packaged agent must
match its frozen source exactly. It additionally requires adaptive activity vs
R4B and a non-vacuous CR-008/CR-011 sequence-only A/B difference.
"""
from __future__ import annotations

import collections
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
OUT = ROOT / "artifacts" / "submissions" / "hosted_calibration_trio"
PAIRS = [
    (
        "r4b",
        "candidates/r4b_ablation_market_only.py",
        "artifacts/submissions/hosted_calibration_trio/Kculture_R4B_fresh_control_v1/main.py",
    ),
    (
        "cr008",
        "candidates/cr008_adaptive_frontrun.py",
        "artifacts/submissions/hosted_calibration_trio/Kculture_CR008_adaptive_append_calibration_v1/main.py",
    ),
    (
        "cr011",
        "candidates/cr011_adaptive_early_order.py",
        "artifacts/submissions/hosted_calibration_trio/Kculture_CR011_adaptive_early_calibration_v1/main.py",
    ),
]


def load(path: str):
    p = ROOT / path
    spec = importlib.util.spec_from_file_location(
        f"trio_{p.stem}_{time.time_ns()}", p
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def market_counter(action):
    return collections.Counter(canon(x) for x in (action.get("market") or []))


def main() -> None:
    reports = {
        key: {"states": 0, "mismatches": 0, "examples": []}
        for key, _, _ in PAIRS
    }
    seq_changes = 0
    seq_multiset_bad = 0
    cr008_vs_r4b_changes = 0
    cr011_vs_r4b_changes = 0
    episodes = 0

    with tempfile.TemporaryDirectory(prefix="kculture-hosted-trio-parity-") as tmp:
        root = Path(tmp)
        handle = f"kaggle/kaggriculture-episodes-{DATE}"
        manifest = sorted(
            read_csv(download(handle, "manifest.csv", root / "manifest")),
            key=lambda r: -float(r.get("avg_score") or 0),
        )[:TOP]

        for row in manifest:
            eid = str(row["episode_id"])
            rep = json.loads(
                download(handle, f"{eid}.json", root / "episodes" / eid).read_text()
            )
            steps = rep.get("steps") or []
            if len(steps) < 720:
                continue
            episodes += 1

            for player in (0, 1):
                parity = {
                    key: (load(src), load(pkg)) for key, src, pkg in PAIRS
                }
                packaged = {key: load(pkg) for key, _, pkg in PAIRS}

                for t in range(min(719, len(steps))):
                    state = steps[t][player]
                    obs = state.get("observation") if isinstance(state, dict) else None
                    if not isinstance(obs, dict):
                        continue

                    for key, (source, package) in parity.items():
                        sa = source.agent(obs, None)
                        pa = package.agent(obs, None)
                        reports[key]["states"] += 1
                        if sa != pa:
                            reports[key]["mismatches"] += 1
                            if len(reports[key]["examples"]) < 10:
                                reports[key]["examples"].append(
                                    {
                                        "episode": eid,
                                        "state": t,
                                        "player": player,
                                        "source": sa,
                                        "package": pa,
                                    }
                                )

                    r4b = packaged["r4b"].agent(obs, None)
                    c8 = packaged["cr008"].agent(obs, None)
                    c11 = packaged["cr011"].agent(obs, None)
                    if c8 != r4b:
                        cr008_vs_r4b_changes += 1
                    if c11 != r4b:
                        cr011_vs_r4b_changes += 1
                    if (c8.get("market") or []) != (c11.get("market") or []):
                        if market_counter(c8) == market_counter(c11):
                            seq_changes += 1
                        else:
                            seq_multiset_bad += 1

    payload = {
        "schema_version": "hosted-calibration-trio-parity-v1",
        "source_date": DATE,
        "episodes": episodes,
        "reports": reports,
        "cr008_vs_r4b_action_changes": cr008_vs_r4b_changes,
        "cr011_vs_r4b_action_changes": cr011_vs_r4b_changes,
        "cr008_vs_cr011_sequence_changes": seq_changes,
        "cr008_vs_cr011_multiset_mismatches": seq_multiset_bad,
    }
    payload["passed"] = (
        episodes >= 10
        and all(
            v["states"] >= 10000 and v["mismatches"] == 0
            for v in reports.values()
        )
        and cr008_vs_r4b_changes > 0
        and cr011_vs_r4b_changes > 0
        and seq_changes > 0
        and seq_multiset_bad == 0
    )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "parity.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    compact = dict(payload)
    compact["reports"] = {
        k: {x: y for x, y in v.items() if x != "examples"}
        for k, v in reports.items()
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
