"""Aggregate exact Kaggle-reference historical league H2Hs.

Primary signal is seat-balanced W/L score rate. Money margins remain secondary
and are deliberately excluded from Bradley-Terry fitting.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def load_results(root: Path) -> list[dict]:
    out = []
    for p in sorted(root.rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict) or "metrics_a_vs_b" not in d or "a" not in d or "b" not in d:
            continue
        m = d.get("metrics_a_vs_b") or {}
        if not all(k in m for k in ("games", "wins", "losses", "ties", "score_rate")):
            continue
        d["_path"] = str(p)
        out.append(d)
    return out


def fit_bradley_terry(results: list[dict]) -> dict[str, float]:
    names = sorted({str(d["a"]) for d in results} | {str(d["b"]) for d in results})
    if not names:
        return {}
    ability = {n: 1.0 for n in names}
    wins = defaultdict(float)
    games = defaultdict(float)
    for d in results:
        a, b = str(d["a"]), str(d["b"])
        m = d["metrics_a_vs_b"]
        w, l, t = float(m["wins"]), float(m["losses"]), float(m["ties"])
        wins[a] += w + 0.5 * t
        wins[b] += l + 0.5 * t
        games[(a, b)] += w + l + t
        games[(b, a)] += w + l + t
    for _ in range(10000):
        new = {}
        for i in names:
            denom = 0.0
            for j in names:
                if i == j:
                    continue
                n = games.get((i, j), 0.0)
                if n:
                    denom += n / max(ability[i] + ability[j], 1e-15)
            new[i] = max(wins[i] / denom, 1e-12) if denom else ability[i]
        gm = math.exp(sum(math.log(max(new[n], 1e-15)) for n in names) / len(names))
        new = {n: new[n] / gm for n in names}
        delta = max(abs(math.log(new[n]) - math.log(ability[n])) for n in names)
        ability = new
        if delta < 1e-12:
            break
    ratings = {n: 400.0 * math.log10(max(ability[n], 1e-15)) for n in names}
    mean = sum(ratings.values()) / len(ratings)
    return {n: ratings[n] - mean for n in names}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-md", required=True)
    args = ap.parse_args()

    results = load_results(Path(args.root))
    if not results:
        raise SystemExit("no reference H2H result JSONs found")

    agents = sorted({str(d["a"]) for d in results} | {str(d["b"]) for d in results})
    total = {a: {"games": 0, "wins": 0, "losses": 0, "ties": 0, "score": 0.0} for a in agents}
    pairs = []
    for d in results:
        a, b = str(d["a"]), str(d["b"])
        m = d["metrics_a_vs_b"]
        g, w, l, t = int(m["games"]), int(m["wins"]), int(m["losses"]), int(m["ties"])
        total[a]["games"] += g; total[a]["wins"] += w; total[a]["losses"] += l; total[a]["ties"] += t; total[a]["score"] += w + 0.5*t
        total[b]["games"] += g; total[b]["wins"] += l; total[b]["losses"] += w; total[b]["ties"] += t; total[b]["score"] += l + 0.5*t
        u = d.get("paired_seed_uncertainty") or {}
        pairs.append({
            "a": a, "b": b, "games": g, "a_wins": w, "a_losses": l, "ties": t,
            "a_score_rate": float(m["score_rate"]),
            "a_paired_ci95": u.get("ci95"),
            "decisive_vs_0_5": bool(u.get("decisive_vs_0_5", False)),
            "mean_margin_secondary": m.get("mean_margin_secondary"),
            "median_margin_secondary": m.get("median_margin_secondary"),
            "reference_backend": d.get("reference_backend"),
            "source": d["_path"],
        })

    bt = fit_bradley_terry(results)
    standings = []
    for a in agents:
        x = total[a]
        rate = x["score"] / x["games"] if x["games"] else None
        standings.append({
            "agent": a, "games": x["games"], "wins": x["wins"], "losses": x["losses"], "ties": x["ties"],
            "league_score_rate": rate, "bradley_terry_rating": bt.get(a),
        })
    standings.sort(key=lambda x: (x["bradley_terry_rating"], x["league_score_rate"]), reverse=True)

    ambiguous = [p for p in pairs if not p["decisive_vs_0_5"]]
    payload = {
        "schema_version": "kculture-historical-reference-league-v1",
        "primary_metric": "seat_balanced_win_loss_score_rate",
        "money_margin_role": "diagnostic_only",
        "pair_count": len(pairs),
        "expected_complete_pair_count": len(agents) * (len(agents)-1) // 2,
        "complete_round_robin": len(pairs) == len(agents) * (len(agents)-1) // 2,
        "standings": standings,
        "pairs": sorted(pairs, key=lambda p: (p["a"], p["b"])),
        "ambiguous_pairs": ambiguous,
        "promotion_policy": "Do not promote from mean money margin. Use official-reference W/L; expand seed count where paired CI crosses 0.5, prioritizing matchups that can change the top ranking.",
    }
    outj = Path(args.output_json); outj.parent.mkdir(parents=True, exist_ok=True)
    outj.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = ["# Historical exact-reference league v1", "", "Primary metric: seat-balanced W/L score rate. Money margins are diagnostic only.", "", "| Rank | Agent | BT rating | League score | W-L-T | Games |", "|---:|---|---:|---:|---:|---:|"]
    for i, s in enumerate(standings, 1):
        lines.append(f"| {i} | {s['agent']} | {s['bradley_terry_rating']:.1f} | {s['league_score_rate']:.3f} | {s['wins']}-{s['losses']}-{s['ties']} | {s['games']} |")
    lines += ["", f"Complete round robin: **{payload['complete_round_robin']}** ({len(pairs)}/{payload['expected_complete_pair_count']} pairs)", f"Ambiguous pairwise CIs crossing 50%: **{len(ambiguous)}**", "", "## Pairwise results", "", "| A | B | A W-L-T | A score | Paired 95% CI | Decisive |", "|---|---|---:|---:|---|---|"]
    for p in sorted(pairs, key=lambda p: (p["a"], p["b"])):
        ci = p["a_paired_ci95"]
        cis = "n/a" if not ci else f"[{ci[0]:.3f}, {ci[1]:.3f}]"
        lines.append(f"| {p['a']} | {p['b']} | {p['a_wins']}-{p['a_losses']}-{p['ties']} | {p['a_score_rate']:.3f} | {cis} | {p['decisive_vs_0_5']} |")
    Path(args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"standings": standings, "pair_count": len(pairs), "ambiguous_pairs": len(ambiguous)}, indent=2))


if __name__ == "__main__":
    main()
