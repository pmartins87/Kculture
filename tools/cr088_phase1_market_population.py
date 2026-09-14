"""CR088 Phase 1: factorial legal-state market operators over diverse top tapes.

The physical/action-tape backbone remains coherent.  Operators may reorder
existing premium SELLs or add one bounded state-supported premium SELL.  The
validated CR086 opponent latent-supply estimator uses only legal observations.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import statistics
import tarfile
from pathlib import Path

import cr086_build_latent_supply_priority as c86
import cr088_top_tape_population as p0


SELECTED = {
    "r01_e108766633_s56156662": "A_MAJKEL_HOSTED_PRIOR",
    "r06_e108754069_s56205640": "A_ORBITAL_LOCAL_ROBUST",
    "r07_e108766657_s56132899": "B_FEEL_LOCAL_ROBUST",
    "r10_e108754200_s56210228": "B_REDBLACK_4LAND_DIVERSITY",
    "r03_e108766659_s56209748": "C_YMG_HOWARD_FAMILY",
    "r09_e108766659_s56097405": "D_OTTER_DISTINCT",
    "r02_e108761464_s56114097": "E_SPATARO_DISTINCT",
}

OPERATORS = [
    {"id": "base", "cap": 0, "price_floor": 0.0, "latent_order": False},
    {"id": "order", "cap": 0, "price_floor": 0.0, "latent_order": True},
    {"id": "risk8_p100", "cap": 8, "price_floor": 1.00, "latent_order": True},
    {"id": "risk8_p125", "cap": 8, "price_floor": 1.25, "latent_order": True},
    {"id": "risk16_p100", "cap": 16, "price_floor": 1.00, "latent_order": True},
    {"id": "risk16_p125", "cap": 16, "price_floor": 1.25, "latent_order": True},
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_tar(path: Path, members: list[tuple[str, bytes]]) -> None:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name, data in sorted(members):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tf.addfile(info, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def overlay_source(base_source: str, estimator_source: Path, operator: dict) -> str:
    if operator["id"] == "base":
        return base_source
    block = c86.runtime_block(estimator_source)
    cap = int(operator["cap"])
    floor = float(operator["price_floor"])
    use_order = bool(operator["latent_order"])
    source = base_source + "\n\n# ---- CR088 Phase-1 legal-state market operator ----\nimport copy\nimport math\n" + block + f'''

_CR088_CAP = {cap}
_CR088_PRICE_FLOOR = {floor!r}
_CR088_USE_LATENT_ORDER = {use_order!r}
_CR088_MAX_MARKET_ORDERS = 10
_cr088_base_agent = agent

def _cr088_risk_sale(agent_fn, obs, market):
    queue = [list(x) for x in (market or [])]
    if _CR088_CAP <= 0:
        return queue
    private = obs.get("private") or {{}}
    market_state = obs.get("market") or {{}}
    prices = market_state.get("prices") or {{}}
    candidates = []
    for item in _CR086_PRIMARY:
        price = max(0, int(prices.get(item, 0) or 0))
        base_price = int(_CR086_MARKET_PARAMS[item]["base"])
        if price < _CR088_PRICE_FLOOR * base_price:
            continue
        available = max(0, int(_cr086_private_total(private, item)))
        planned = sum(max(0, int(x[2])) for x in queue
                      if len(x) >= 3 and x[0] == "SELL" and x[1] == item)
        extra = min(_CR088_CAP, max(0, available - planned))
        if extra <= 0:
            continue
        risk = _cr086_cash_risk(agent_fn, obs, ["SELL", item, extra])
        if risk > 0:
            candidates.append((risk, price, extra, item))
    if not candidates:
        return queue
    risk, price, extra, item = max(candidates)
    positions = [i for i, x in enumerate(queue)
                 if len(x) >= 3 and x[0] == "SELL" and x[1] == item]
    if positions:
        queue[positions[0]][2] = max(0, int(queue[positions[0]][2])) + extra
    elif len(queue) < _CR088_MAX_MARKET_ORDERS:
        queue.insert(0, ["SELL", item, extra])
    return queue

def agent(obs, config=None):
    step = _clock(obs)
    if step == 0:
        for name in ("_cr086_prev", "_cr086_point_mass", "_cr086_upper_mass", "_cr086_ever_floor", "_cr086_upper"):
            if hasattr(agent, name):
                delattr(agent, name)
    _cr086_update(agent, obs, step)
    out = _cr088_base_agent(obs, config)
    queue = _cr088_risk_sale(agent, obs, out.get("market") or [])
    if _CR088_USE_LATENT_ORDER:
        queue = _cr086_prioritize(agent, obs, queue)
    out["market"] = queue[:_CR088_MAX_MARKET_ORDERS]
    return out
'''
    compile(source, "main.py", "exec")
    return source


def matrix_cmd(args) -> None:
    rows = p0.load_meta(Path(args.metadata))
    phase0 = json.loads(Path(args.phase0).read_text())
    best_by_team = {x["candidate_id"] for x in phase0["best_valid_seed_per_source_team_in_hosted_rank_order"]}
    missing = sorted(set(SELECTED) - {p0.candidate_id(r) for r in rows})
    if missing:
        raise RuntimeError(f"selected bases absent: {missing}")
    # Every selection is a frozen per-team best from Phase 0; the second member
    # of broad family A/B is retained deliberately for hosted-prior/diversity.
    if not set(SELECTED).issubset(best_by_team):
        raise RuntimeError("selection is not composed of frozen per-team Phase-0 winners")
    include = []
    for row in rows:
        base_id = p0.candidate_id(row)
        if base_id not in SELECTED:
            continue
        for op in OPERATORS:
            include.append({
                "variant_id": f"{base_id}__{op['id']}",
                "base_candidate_id": base_id,
                "family": SELECTED[base_id],
                "tape_file": p0.tape_filename(row),
                "episode_id": int(row["episode_id"]),
                "submission_id": int(row["submission_id"]),
                "team_name": str(row["team_name"]),
                "source_rank": int(row["leaderboard_rank"]),
                "operator": op["id"],
                "cap": op["cap"],
                "price_floor": op["price_floor"],
                "latent_order": op["latent_order"],
            })
    if len(include) != len(SELECTED) * len(OPERATORS):
        raise RuntimeError(f"expected 42 variants, found {len(include)}")
    Path(args.output).write_text(json.dumps({"include": include}, separators=(",", ":"), sort_keys=True))
    print(json.dumps({"bases": len(SELECTED), "operators": len(OPERATORS), "population": len(include)}, sort_keys=True))


def build_cmd(args) -> None:
    rows = p0.load_meta(Path(args.metadata))
    row = next((x for x in rows if int(x["episode_id"]) == args.episode_id and int(x["submission_id"]) == args.submission_id), None)
    if row is None:
        raise RuntimeError("frozen base absent")
    base_id = p0.candidate_id(row)
    if base_id not in SELECTED:
        raise RuntimeError("base not selected by frozen Phase 0")
    op = next((x for x in OPERATORS if x["id"] == args.operator), None)
    if op is None:
        raise RuntimeError("unknown frozen operator")
    tape = json.loads(Path(args.tape).read_text())
    tape_sha = sha256(p0.canonical_bytes(tape))
    if len(tape) != 719 or tape_sha != row.get("tape_sha256"):
        raise RuntimeError("base tape identity mismatch")
    source = overlay_source(p0.runtime_source(tape), Path(args.estimator_source), op).encode()
    provenance = (
        f"CR088 Phase 1 base={base_id} family={SELECTED[base_id]} operator={op['id']}\n"
        f"episode={args.episode_id} submission={args.submission_id} tape_sha256={tape_sha}\n"
        "Identifiers are offline provenance only; runtime uses no identity/rating/episode/seed.\n"
    ).encode()
    out = Path(args.output)
    write_tar(out, [("main.py", source), ("CR088_PHASE1_PROVENANCE.txt", provenance)])
    first = out.read_bytes()
    rebuild = out.with_suffix(out.suffix + ".rebuild")
    write_tar(rebuild, [("main.py", source), ("CR088_PHASE1_PROVENANCE.txt", provenance)])
    if first != rebuild.read_bytes():
        raise RuntimeError("non-deterministic build")
    rebuild.unlink()
    manifest = {
        "schema": "cr088-state-coherent-market-population-v1",
        "variant_id": f"{base_id}__{op['id']}",
        "base_candidate_id": base_id,
        "family": SELECTED[base_id],
        "team_name_provenance_only": row["team_name"],
        "source_rank_context_only": row["leaderboard_rank"],
        "tape_sha256": tape_sha,
        "operator": op,
        "archive_sha256": sha256(first),
        "physical_actions_modified": False,
        "base_market_orders_removed": False,
        "runtime_identity_features": False,
        "runtime_opponent_private_features": False,
        "runtime_hidden_seed_or_future": False,
        "automatic_submission": False,
        "held_out_touched": False,
    }
    mp = Path(args.manifest); mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps(manifest, indent=2, sort_keys=True))


def metric(data: dict) -> dict:
    m = data["metrics_a_vs_b"]
    return {
        "games": int(m["games"]), "wins": int(m["wins"]), "losses": int(m["losses"]), "ties": int(m["ties"]),
        "score_rate": 0.0 if m.get("score_rate") is None else float(m["score_rate"]),
        "mean_margin": m.get("mean_margin_secondary"),
        "non_done": int(m.get("non_done_games") or 0),
        "errors": len(data.get("errors") or []),
        "seat_floor": min(0.0 if x.get("score_rate") is None else float(x["score_rate"]) for x in data["metrics_by_a_seat"].values()),
    }


def collect_cmd(args) -> None:
    root = Path(args.result_dir)
    manifest = json.loads(Path(args.manifest).read_text())
    direct = metric(json.loads((root / "direct_vs_base.json").read_text()))
    anchors = {p.stem[3:]: metric(json.loads(p.read_text())) for p in sorted(root.glob("vs_*.json"))}
    expected = {"CR053_REAL", "CR052_REAL", "CR083", "CR086"}
    if set(anchors) != expected:
        raise RuntimeError(f"anchor mismatch {sorted(anchors)}")
    scores = [x["score_rate"] for x in anchors.values()]
    mean_score = statistics.mean(scores)
    worst = min(scores)
    seat_floor = min(x["seat_floor"] for x in anchors.values())
    errors = direct["errors"] + sum(x["errors"] for x in anchors.values())
    non_done = direct["non_done"] + sum(x["non_done"] for x in anchors.values())
    out = {
        **manifest,
        "direct_vs_base": direct,
        "anchors": anchors,
        "mean_anchor_score": mean_score,
        "worst_anchor_score": worst,
        "seat_floor_score": seat_floor,
        "robust_local_safety_score": 0.50 * mean_score + 0.35 * worst + 0.15 * seat_floor,
        "errors": errors,
        "non_done_games": non_done,
        "mechanically_valid": errors == 0 and non_done == 0 and direct["games"] == 6 and all(x["games"] == 6 for x in anchors.values()),
        "interpretation_limit": "operator safety/causal screen only; hosted transfer unknown",
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps(out, indent=2, sort_keys=True))


def slim(r: dict, base: dict) -> dict:
    return {
        "variant_id": r["variant_id"], "base_candidate_id": r["base_candidate_id"], "family": r["family"],
        "team": r["team_name_provenance_only"], "source_rank": r["source_rank_context_only"],
        "operator": r["operator"], "archive_sha256": r["archive_sha256"],
        "mean_anchor_score": r["mean_anchor_score"], "worst_anchor_score": r["worst_anchor_score"],
        "robust_local_safety_score": r["robust_local_safety_score"],
        "delta_mean_vs_same_base": r["mean_anchor_score"] - base["mean_anchor_score"],
        "delta_robust_vs_same_base": r["robust_local_safety_score"] - base["robust_local_safety_score"],
        "direct_vs_base": r["direct_vs_base"],
        "anchor_scores": {k: v["score_rate"] for k, v in sorted(r["anchors"].items())},
    }


def aggregate_cmd(args) -> None:
    rows = [json.loads(p.read_text()) for p in Path(args.input_dir).glob("**/candidate-summary.json")]
    if len(rows) != 42:
        raise RuntimeError(f"expected 42 summaries, found {len(rows)}")
    groups = {}
    for row in rows:
        groups.setdefault(row["base_candidate_id"], []).append(row)
    families = []
    eligible = []
    for base_id, members in sorted(groups.items()):
        base = next(x for x in members if x["operator"]["id"] == "base")
        ranked = sorted(members, key=lambda x: (x["robust_local_safety_score"], x["mean_anchor_score"]), reverse=True)
        slims = [slim(x, base) for x in ranked]
        family_eligible = []
        for x in members:
            if x["operator"]["id"] == "base":
                continue
            ok = (
                x["mechanically_valid"]
                and x["direct_vs_base"]["score_rate"] >= 0.5
                and x["mean_anchor_score"] >= base["mean_anchor_score"] - 0.0625
                and x["robust_local_safety_score"] >= base["robust_local_safety_score"] - 0.0625
            )
            if ok:
                q = slim(x, base); q["eligible_for_diverse_phase2_consideration"] = True
                family_eligible.append(q); eligible.append(q)
        family_eligible.sort(key=lambda x: (x["delta_robust_vs_same_base"], x["delta_mean_vs_same_base"]), reverse=True)
        families.append({"base": slim(base, base), "ranked_variants": slims, "eligible_overlays": family_eligible})
    eligible.sort(key=lambda x: (x["source_rank"], -x["delta_robust_vs_same_base"], -x["delta_mean_vs_same_base"]))
    out = {
        "schema": "cr088-state-coherent-market-population-phase1-aggregate-v1",
        "population": len(rows), "bases": len(groups), "operators_per_base": 6,
        "master_seed": 9230881, "seeds_per_edge": 3,
        "mechanically_valid": sum(x["mechanically_valid"] for x in rows),
        "families": families,
        "eligible_diverse_overlays_in_hosted_prior_order": eligible,
        "decision": "PHASE1_COMPLETE_SELECT_MATERIALLY_DIFFERENT_HOSTED_SENSORS",
        "automatic_submission": False, "held_out_touched": False,
        "warning": "Eligibility is a non-regression/safety filter, not evidence of hosted strength. Do not select solely by local rank.",
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "families"}, indent=2, sort_keys=True))


def main() -> None:
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("matrix"); m.add_argument("--metadata", required=True); m.add_argument("--phase0", required=True); m.add_argument("--output", required=True)
    b = sub.add_parser("build"); b.add_argument("--metadata", required=True); b.add_argument("--tape", required=True); b.add_argument("--episode-id", type=int, required=True); b.add_argument("--submission-id", type=int, required=True); b.add_argument("--operator", required=True); b.add_argument("--estimator-source", required=True); b.add_argument("--output", required=True); b.add_argument("--manifest", required=True)
    c = sub.add_parser("collect"); c.add_argument("--result-dir", required=True); c.add_argument("--manifest", required=True); c.add_argument("--output", required=True)
    a = sub.add_parser("aggregate"); a.add_argument("--input-dir", required=True); a.add_argument("--output", required=True)
    args = ap.parse_args(); {"matrix": matrix_cmd, "build": build_cmd, "collect": collect_cmd, "aggregate": aggregate_cmd}[args.cmd](args)


if __name__ == "__main__":
    main()
