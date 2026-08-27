"""Mechanical equivalence gate for CR-011 versus frozen CR-008.

Use strict Aug-26 official replay observations, where the frozen CR-007 signal is
known to be active. For each observation, compute the frozen R4B base action once
and apply the CR-008 and CR-011 market transforms to independent copies.
Require the same non-market action and the same market-order multiset, while also
requiring at least one real sequence change. This proves that CR-011's intended
mechanical difference is order placement only before causal games are allowed.
"""
from __future__ import annotations

import collections
import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr004_adaptation_signal import download, read_csv
from candidates import cr008_adaptive_frontrun as A
from candidates import cr011_adaptive_early_order as B

TEST_DATE = "2026-08-26"
TOP = 20


def canon_order(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def market_counter(a):
    return collections.Counter(canon_order(x) for x in (a.get("market") or []))


def nonmarket(a):
    return {k: v for k, v in a.items() if k != "market"}


def reset_histories():
    for p in (0, 1):
        A._HISTORY[p].clear()
        A._LAST_STEP[p] = -1
        B._HISTORY[p].clear()
        B._LAST_STEP[p] = -1


def main():
    mismatches = []
    sequence_changes = []
    states = 0
    episodes = 0

    with tempfile.TemporaryDirectory(prefix="kculture-cr011-order-gate-") as tmp:
        root = Path(tmp)
        handle = f"kaggle/kaggriculture-episodes-{TEST_DATE}"
        manifest = sorted(
            read_csv(download(handle, "manifest.csv", root / "manifest")),
            key=lambda r: -float(r.get("avg_score") or 0),
        )[:TOP]

        for row in manifest:
            eid = str(row["episode_id"])
            path = download(handle, f"{eid}.json", root / "episodes" / eid)
            rep = json.loads(path.read_text(encoding="utf-8"))
            steps = rep.get("steps") or []
            if len(steps) < 720:
                continue
            episodes += 1
            reset_histories()

            for t in range(min(719, len(steps))):
                for player in (0, 1):
                    frame = steps[t][player]
                    obs = frame.get("observation") if isinstance(frame, dict) else None
                    if not isinstance(obs, dict):
                        continue
                    step = A._clock_step(obs)
                    A._reset_if_needed(player, step)
                    B._reset_if_needed(player, step)

                    # One base action only: both transforms receive the exact same
                    # physical/market baseline, eliminating double-call state effects.
                    base = A._BASE.agent(obs, None)
                    aa = A._append_adaptive_sales(obs, copy.deepcopy(base), player, step)
                    bb = B._prefix_adaptive_sales(obs, copy.deepcopy(base), player, step)
                    states += 1

                    problems = []
                    if nonmarket(aa) != nonmarket(bb):
                        problems.append("nonmarket")
                    if market_counter(aa) != market_counter(bb):
                        problems.append("market_multiset")
                    if problems:
                        mismatches.append({
                            "episode_id": eid,
                            "state": t,
                            "player": player,
                            "problems": problems,
                            "base": base,
                            "cr008": aa,
                            "cr011": bb,
                        })

                    if (aa.get("market") or []) != (bb.get("market") or []):
                        sequence_changes.append({
                            "episode_id": eid,
                            "state": t,
                            "player": player,
                            "base_market": base.get("market") or [],
                            "cr008_market": aa.get("market") or [],
                            "cr011_market": bb.get("market") or [],
                        })

                    A._remember(player, step, obs)
                    B._remember(player, step, obs)

                    if len(mismatches) >= 20:
                        break
                if len(mismatches) >= 20:
                    break
            if len(mismatches) >= 20:
                break

    payload = {
        "schema_version": "cr011-order-only-v2",
        "source_date": TEST_DATE,
        "top_episodes_requested": TOP,
        "episodes_used": episodes,
        "states_compared": states,
        "mismatch_count": len(mismatches),
        "sequence_change_count": len(sequence_changes),
        "passed": len(mismatches) == 0 and len(sequence_changes) > 0,
        "mismatches": mismatches,
        "sequence_changes": sequence_changes[:100],
    }
    out = ROOT / "artifacts/cr011/order-only.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k not in ("mismatches", "sequence_changes")}, indent=2))
    if not payload["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
