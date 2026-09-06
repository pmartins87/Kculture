"""CR035 mechanical retry shard using the preverified source bundle.

All strategic semantics are imported from the original frozen CR035 shard.
No Kaggle network access occurs here.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from kaggle_environments import make

import cr035_public_regime_selector_shard as core

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr031_elite_round_robin.json"
OUT = core.OUT


def _resolve(path_text: str) -> Path:
    p = Path(path_text)
    return p if p.is_absolute() else ROOT / p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-rank", type=int, required=True)
    ap.add_argument("--source-bundle", required=True)
    args = ap.parse_args()
    candidate_rank = int(args.candidate_rank)
    if candidate_rank < 0 or candidate_rank > 12:
        raise SystemExit("candidate-rank must be 0..12")

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    bundle = json.loads(_resolve(args.source_bundle).read_text(encoding="utf-8"))
    if bundle.get("schema_version") != "cr035-source-bundle-v1":
        raise RuntimeError("unexpected CR035 source bundle schema")
    frozen = bundle.get("classifier") or {}
    if int(frozen.get("switch_clock")) != core.SWITCH_CLOCK:
        raise RuntimeError("bundle switch clock differs from frozen CR035")
    if float(frozen.get("threshold")) != core.SELF_MONEY_THRESHOLD:
        raise RuntimeError("bundle classifier threshold differs from frozen CR035")

    recent = cfg["recent_top"]
    b_recent = bundle["recent_top"]
    base = b_recent["tape"]
    if (
        int(b_recent["episode_id"]) != int(recent["episode_id"])
        or int(b_recent["source_seat"]) != int(recent["source_seat"])
        or len(base) != 719
        or core._tape_sha(base) != recent["tape_sha256"]
        or b_recent["tape_sha256"] != recent["tape_sha256"]
    ):
        raise RuntimeError("CR029 source bundle provenance mismatch")

    scenarios: dict[int, dict] = {}
    by_rank = bundle["scenarios"]
    for s in cfg["scenarios"]:
        rank = int(s["rank"])
        b = by_rank[str(rank)]
        tape = b["tape"]
        observed = core._tape_sha(tape)
        if (
            int(b["rank"]) != rank
            or int(b["episode_id"]) != int(s["episode_id"])
            or int(b["seed"]) != int(s["seed"])
            or b["team"] != s["team"]
            or int(b["winner_seat"]) != int(s["winner_seat"])
            or len(tape) != 719
            or observed != s["tape_sha256"]
            or b["tape_sha256"] != s["tape_sha256"]
        ):
            raise RuntimeError(f"elite r{rank} source bundle provenance mismatch")
        scenarios[rank] = {
            "rank": rank,
            "episode_id": int(s["episode_id"]),
            "seed": int(s["seed"]),
            "team": s["team"],
            "configuration": b["configuration"] if isinstance(b.get("configuration"), dict) else {},
            "tape": tape,
        }

    if sorted(scenarios) != list(range(1, 13)):
        raise RuntimeError("CR035 bundle missing elite ranks")

    alternate = None if candidate_rank == 0 else scenarios[candidate_rank]["tape"]
    candidate_team = "CR029_CONTROL" if candidate_rank == 0 else scenarios[candidate_rank]["team"]
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[dict] = []
    rows: list[dict] = []

    for rank, sc in sorted(scenarios.items()):
        for seat in (0, 1):
            try:
                own_agent, state = core._selector_agent(base, alternate)
                opp_agent = core._tape_agent(sc["tape"])
                conf = copy.deepcopy(sc["configuration"])
                conf["episodeSteps"] = 720
                conf["seed"] = int(sc["seed"])
                env = make("kaggriculture", configuration=conf, debug=True)
                env.run([own_agent, opp_agent] if seat == 0 else [opp_agent, own_agent])
                rep = env.toJSON()
                if not core._final_ok(rep):
                    raise RuntimeError(f"non-DONE steps={len(rep.get('steps') or [])}")
                rewards = core._rewards(rep)
                own_reward = rewards[seat]
                opp_reward = rewards[1 - seat]
                delta = own_reward - opp_reward
                predicted = state["predicted_team"] if candidate_rank != 0 else None
                rows.append({
                    "candidate_rank": candidate_rank,
                    "candidate_team": candidate_team,
                    "opponent_rank": rank,
                    "opponent_team": sc["team"],
                    "episode_id": sc["episode_id"],
                    "seed": sc["seed"],
                    "seat": seat,
                    "self_reward": own_reward,
                    "opp_reward": opp_reward,
                    "delta": delta,
                    "score": core._wl(delta),
                    "predicted_team": predicted,
                    "classifier_correct": None if candidate_rank == 0 else predicted == sc["team"],
                    "self_money_at_24": state["self_money_at_24"],
                    "switched": bool(state["switched"]),
                })
            except Exception as exc:
                errors.append({"opponent_rank": rank, "seat": seat, "error": repr(exc)})

    keiz_rows = [r for r in rows if r["opponent_team"] == "keiz"]
    jesse_rows = [r for r in rows if r["opponent_team"] == "Jesse Bullard"]
    out = {
        "experiment": "CR035_PUBLIC_REGIME_SELECTOR_V1",
        "candidate_rank": candidate_rank,
        "candidate_team": candidate_team,
        "switch_clock": core.SWITCH_CLOCK,
        "classifier_feature": "self_money",
        "classifier_threshold": core.SELF_MONEY_THRESHOLD,
        "mechanical_complete": not errors and len(rows) == 24,
        "errors": errors,
        "all": core._summary(rows),
        "keiz": core._summary(keiz_rows),
        "jesse": core._summary(jesse_rows),
        "classifier_correct": None if candidate_rank == 0 else sum(bool(r["classifier_correct"]) for r in rows),
        "classifier_total": None if candidate_rank == 0 else len(rows),
        "switched_games": sum(bool(r["switched"]) for r in rows),
        "rows": rows,
        "source_scenarios_already_open": True,
        "fresh_validation_touched": False,
        "held_out_touched": False,
        "runtime_identity_features": False,
        "mechanical_retry_from_verified_bundle": True,
    }
    path = OUT / f"shard_rank{candidate_rank:02d}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2, sort_keys=True))
    if errors or len(rows) != 24:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
