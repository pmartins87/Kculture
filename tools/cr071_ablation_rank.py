from __future__ import annotations

"""Aggregate the CR071 one-component removal screen using W/L only."""

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-md", required=True)
    args = ap.parse_args()

    rows = []
    by_candidate: dict[str, dict] = {}
    for path in sorted(Path(args.input_dir).rglob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("schema_version") != "kculture-kaggle-reference-h2h-v2":
            continue
        cand = d["a"]
        opp = d["b"]
        m = d["metrics_a_vs_b"]
        item = {
            "candidate": cand,
            "opponent": opp,
            "games": int(m["games"]),
            "wins": int(m["wins"]),
            "losses": int(m["losses"]),
            "ties": int(m["ties"]),
            "score_rate": float(m["score_rate"]),
            "errors": len(d.get("errors") or []),
            "paired_ci95": (d.get("paired_seed_uncertainty") or {}).get("ci95"),
        }
        rows.append(item)
        agg = by_candidate.setdefault(cand, {"games": 0, "wins": 0, "losses": 0, "ties": 0, "errors": 0, "opponents": {}})
        for k in ("games", "wins", "losses", "ties", "errors"):
            agg[k] += item[k]
        agg["opponents"][opp] = item

    expected_opponents = {"CR070A", "CR065", "CR053", "CR061"}
    standings = []
    for cand, agg in by_candidate.items():
        if set(agg["opponents"]) != expected_opponents:
            agg["complete_panel"] = False
        else:
            agg["complete_panel"] = True
        agg["candidate"] = cand
        agg["score_rate"] = (agg["wins"] + 0.5 * agg["ties"]) / agg["games"] if agg["games"] else None
        parent = agg["opponents"].get("CR070A")
        agg["vs_parent_score_rate"] = None if parent is None else parent["score_rate"]
        standings.append(agg)

    standings.sort(key=lambda x: (x["errors"] == 0, x["complete_panel"], x["score_rate"] or -1, x["wins"]), reverse=True)
    parent_row = next((x for x in standings if x["candidate"] == "PARENT"), None)
    parent_score = parent_row["score_rate"] if parent_row else None
    for x in standings:
        x["aggregate_gain_vs_parent"] = None if parent_score is None else x["score_rate"] - parent_score
        x["screen_shortlist"] = bool(
            x["candidate"] != "PARENT"
            and x["errors"] == 0
            and x["complete_panel"]
            and parent_score is not None
            and x["score_rate"] > parent_score
            and (x["vs_parent_score_rate"] is not None and x["vs_parent_score_rate"] >= 0.5)
        )

    payload = {
        "schema_version": "kculture-cr071-ablation-screen-v1",
        "primary_metric": "seat_balanced_win_loss_score_rate",
        "money_margin_role": "ignored_for_screen_ranking",
        "paired_seeds_per_matchup": 8,
        "games_per_matchup": 16,
        "opponents": sorted(expected_opponents),
        "parent_aggregate_score_rate": parent_score,
        "standings": standings,
        "pairwise": rows,
        "decision_policy": "Shortlist only one-component removals that beat PARENT aggregate and are >=50% head-to-head versus CR070A parent. Shortlist is not promotion; expand with more official-reference seeds before any hosted submission.",
    }
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md = ["# CR071 Tetsu component ablation screen", "", "W/L is primary. Money margin is not used for ranking.", "", "| Rank | Candidate | W-L-T | Score | Gain vs parent | vs CR070A | Shortlist |", "|---:|---|---:|---:|---:|---:|---|"]
    for i, x in enumerate(standings, 1):
        gain = x["aggregate_gain_vs_parent"]
        gain_s = "n/a" if gain is None else f"{gain:+.4f}"
        vp = x["vs_parent_score_rate"]
        vp_s = "n/a" if vp is None else f"{vp:.4f}"
        md.append(f"| {i} | {x['candidate']} | {x['wins']}-{x['losses']}-{x['ties']} | {x['score_rate']:.4f} | {gain_s} | {vp_s} | {'YES' if x['screen_shortlist'] else 'no'} |")
    md += ["", "Shortlisted variants require a larger exact-reference confirmation before they can influence Kaggle promotion."]
    Path(args.output_md).write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
