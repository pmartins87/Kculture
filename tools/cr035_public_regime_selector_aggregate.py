"""Aggregate the 13 CR035 selector shards and apply the frozen promotion gate."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/cr035_public_regime_selector"


def _load_shards(root: Path) -> dict[int, dict]:
    found: dict[int, dict] = {}
    for p in sorted(root.rglob("shard_rank*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        rank = int(obj["candidate_rank"])
        if rank in found:
            raise RuntimeError(f"duplicate shard rank {rank}")
        found[rank] = obj
    return found


def _row_key(r: dict) -> tuple[int, int]:
    return int(r["opponent_rank"]), int(r["seat"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default="artifacts/cr035_downloaded")
    args = ap.parse_args()
    inp = ROOT / args.input_dir
    shards = _load_shards(inp)
    OUT.mkdir(parents=True, exist_ok=True)

    missing = [r for r in range(13) if r not in shards]
    if missing:
        raise RuntimeError(f"missing CR035 shards: {missing}")

    control = shards[0]
    if not control.get("mechanical_complete") or len(control.get("rows") or []) != 24:
        raise RuntimeError("CR029 control shard incomplete")
    base = {_row_key(r): r for r in control["rows"]}
    if len(base) != 24:
        raise RuntimeError("CR029 control row key mismatch")

    reports = []
    for rank in range(1, 13):
        s = shards[rank]
        rows = s.get("rows") or []
        paired = []
        for r in rows:
            k = _row_key(r)
            if k not in base:
                raise RuntimeError(f"rank {rank} row has unknown key {k}")
            b = base[k]
            paired.append((r, b))

        favorable = sum(float(r["score"]) > float(b["score"]) for r, b in paired)
        unfavorable = sum(float(r["score"]) < float(b["score"]) for r, b in paired)
        same = len(paired) - favorable - unfavorable
        score_gain = sum(float(r["score"]) - float(b["score"]) for r, b in paired)
        delta_gains = [float(r["delta"]) - float(b["delta"]) for r, b in paired]
        mean_delta_gain = statistics.mean(delta_gains) if delta_gains else None
        jesse_pairs = [(r, b) for r, b in paired if r["opponent_team"] == "Jesse Bullard"]
        keiz_pairs = [(r, b) for r, b in paired if r["opponent_team"] == "keiz"]
        jesse_conversions = sum(float(r["score"]) != float(b["score"]) for r, b in jesse_pairs)
        keiz_favorable = sum(float(r["score"]) > float(b["score"]) for r, b in keiz_pairs)
        keiz_unfavorable = sum(float(r["score"]) < float(b["score"]) for r, b in keiz_pairs)
        keiz_score_gain = sum(float(r["score"]) - float(b["score"]) for r, b in keiz_pairs)
        classifier_correct = int(s.get("classifier_correct") or 0)
        classifier_total = int(s.get("classifier_total") or 0)
        mechanical = bool(s.get("mechanical_complete")) and len(rows) == 24 and not s.get("errors")
        passed = (
            mechanical
            and classifier_correct == 24 and classifier_total == 24
            and score_gain >= 2.0
            and favorable >= 2
            and unfavorable <= 2
            and mean_delta_gain is not None and mean_delta_gain > 0.0
            and jesse_conversions == 0
        )
        reports.append({
            "candidate_rank": rank,
            "candidate_team": s.get("candidate_team"),
            "mechanical_complete": mechanical,
            "classifier_correct": classifier_correct,
            "classifier_total": classifier_total,
            "switched_games": s.get("switched_games"),
            "score_total": s["all"]["score_total"],
            "control_score_total": control["all"]["score_total"],
            "score_gain_vs_cr029": score_gain,
            "favorable_conversions": favorable,
            "unfavorable_conversions": unfavorable,
            "same_outcomes": same,
            "net_conversions": favorable - unfavorable,
            "mean_paired_delta_gain": mean_delta_gain,
            "keiz_score_gain": keiz_score_gain,
            "keiz_favorable": keiz_favorable,
            "keiz_unfavorable": keiz_unfavorable,
            "jesse_conversions": jesse_conversions,
            "selector_summary": s["all"],
            "keiz_summary": s["keiz"],
            "jesse_summary": s["jesse"],
            "screen_pass": passed,
        })

    reports.sort(
        key=lambda x: (
            bool(x["screen_pass"]),
            float(x["score_gain_vs_cr029"]),
            int(x["net_conversions"]),
            float(x["mean_paired_delta_gain"] or -1e30),
        ),
        reverse=True,
    )
    shortlist = [r["candidate_rank"] for r in reports if r["screen_pass"]]
    decision = "CR035_SHORTLIST_READY" if shortlist else "CR035_NO_SELECTOR_PROMOTION"
    out = {
        "experiment": "CR035_PUBLIC_REGIME_SELECTOR_V1",
        "decision": decision,
        "control": control["all"],
        "shortlist": shortlist,
        "ranking": reports,
        "gate": {
            "classifier_correct": "24/24",
            "score_gain_vs_cr029_min": 2.0,
            "favorable_conversions_min": 2,
            "unfavorable_conversions_max": 2,
            "mean_paired_delta_gain_min_exclusive": 0.0,
            "jesse_conversions_required": 0,
        },
        "source_scenarios_already_open": True,
        "fresh_validation_touched": False,
        "held_out_touched": False,
        "runtime_identity_features": False,
    }
    (OUT / "report.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    compact = {
        "experiment": out["experiment"],
        "decision": decision,
        "control": out["control"],
        "shortlist": shortlist,
        "ranking": [
            {
                "candidate_rank": r["candidate_rank"],
                "candidate_team": r["candidate_team"],
                "score_gain_vs_cr029": r["score_gain_vs_cr029"],
                "favorable": r["favorable_conversions"],
                "unfavorable": r["unfavorable_conversions"],
                "net": r["net_conversions"],
                "mean_paired_delta_gain": r["mean_paired_delta_gain"],
                "keiz_score_gain": r["keiz_score_gain"],
                "jesse_conversions": r["jesse_conversions"],
                "classifier_correct": r["classifier_correct"],
                "pass": r["screen_pass"],
            }
            for r in reports
        ],
        "fresh_validation_touched": False,
        "held_out_touched": False,
    }
    (OUT / "summary.json").write_text(json.dumps(compact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
