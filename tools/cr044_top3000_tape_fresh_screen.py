"""CR044: fresh-seed screen of exact 2026-09-06 ~3000 winner tapes.

Purpose: determine whether any current top winner trajectory is robust outside
its source episode. Stage A is direct head-to-head against frozen CR029 on fresh
seeds. Only direct qualifiers enter a small paired reactive panel. No Kaggle
submission is made.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import statistics
import tempfile
import time
from pathlib import Path

import kagglehub
from kaggle_environments import make

import cr035_public_regime_selector_shard as core
import cr043_latest_top3000_probe as p43

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr044_top3000_tape_fresh_screen.json"


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def seed_values(obj) -> set[int]:
    out: set[int] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "seed" in str(k).lower():
                vals = v if isinstance(v, list) else [v]
                for x in vals:
                    try:
                        out.add(int(x))
                    except Exception:
                        pass
            out |= seed_values(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= seed_values(v)
    return out


def seed_firewall(cfg: dict) -> list[int]:
    own = set(map(int, cfg["fresh_direct_seeds"] + cfg["reactive_seeds"]))
    old: set[int] = set()
    for p in (ROOT / "configs").glob("*.json"):
        if p.resolve() == CFG.resolve():
            continue
        try:
            old |= seed_values(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return sorted(own & old)


def tape_agent(tape: list[dict]):
    def agent(obs, config=None):
        s = max(0, min(718, core._clock(obs)))
        return copy.deepcopy(tape[s])
    return agent


def load_agent(path: Path):
    name = f"cr044_opp_{path.stem}_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def run_game(own, opp, seed: int, seat: int) -> dict:
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run([own, opp] if seat == 0 else [opp, own])
    rep = env.toJSON()
    steps = rep.get("steps") or []
    if len(steps) != 720:
        raise RuntimeError(f"short game {len(steps)}")
    final = steps[-1]
    statuses = [final[i].get("status") for i in (0, 1)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"statuses {statuses}")
    rewards = [float(final[i].get("reward")) for i in (0, 1)]
    if not all(math.isfinite(x) for x in rewards):
        raise RuntimeError("nonfinite reward")
    delta = rewards[seat] - rewards[1-seat]
    return {"score": score(delta), "delta": delta, "rewards": rewards}


def download_episode(handle: str, eid: int, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=f"{eid}.json", output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))


def paired(rows: list[dict]) -> dict:
    diffs = [r["candidate"]["delta"] - r["control"]["delta"] for r in rows]
    return {
        "games": len(rows),
        "score_gain": sum(r["candidate"]["score"] - r["control"]["score"] for r in rows),
        "improvements": sum(r["candidate"]["score"] > r["control"]["score"] for r in rows),
        "regressions": sum(r["candidate"]["score"] < r["control"]["score"] for r in rows),
        "mean_delta_gain": statistics.mean(diffs) if diffs else None,
        "positive_margin_rows": sum(x > 0 for x in diffs),
        "negative_margin_rows": sum(x < 0 for x in diffs),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    overlap = seed_firewall(cfg)
    if overlap:
        raise SystemExit(f"seed firewall overlap: {overlap}")

    bundle = json.loads(Path(args.source_bundle).read_text(encoding="utf-8"))
    base = bundle["recent_top"]["tape"]
    if len(base) != 719 or core._tape_sha(base) != bundle["recent_top"]["tape_sha256"]:
        raise RuntimeError("CR029 source bundle mismatch")

    errors: list[dict] = []
    candidates: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="cr044-") as td0:
        td = Path(td0)
        for meta in cfg["episodes"]:
            eid = int(meta["episode_id"])
            try:
                rep = download_episode(cfg["day_handle"], eid, td / str(eid))
                steps = rep.get("steps") or []
                if len(steps) != 720:
                    raise RuntimeError(f"steps {len(steps)}")
                names = (rep.get("info") or {}).get("TeamNames") or ["p0", "p1"]
                rewards = [float(steps[-1][i].get("reward")) for i in (0, 1)]
                win = 0 if rewards[0] >= rewards[1] else 1
                if win != int(meta["expected_winner_seat"]):
                    raise RuntimeError(f"winner seat {win}")
                if str(names[win]) != str(meta["expected_winner_team"]):
                    raise RuntimeError(f"winner team {names[win]}")
                tape = p43._actions(rep, win)
                if len(tape) != 719:
                    raise RuntimeError("bad tape")
                cid = f"ep{eid}_s{win}"
                candidates[cid] = {
                    "id": cid,
                    "episode_id": eid,
                    "winner_seat": win,
                    "winner_team": str(names[win]),
                    "tape": tape,
                    "tape_sha256": core._tape_sha(tape),
                    "source_rewards": rewards,
                }
            except Exception as exc:
                errors.append({"phase": "load", "episode_id": eid, "error": repr(exc)[:1000]})

        direct = {}
        for cid, c in candidates.items():
            rows = []
            for seed in map(int, cfg["fresh_direct_seeds"]):
                for seat in (0, 1):
                    try:
                        r = run_game(tape_agent(c["tape"]), tape_agent(base), seed, seat)
                        rows.append({"seed": seed, "seat": seat, **r})
                    except Exception as exc:
                        errors.append({"phase": "direct", "candidate": cid, "seed": seed, "seat": seat, "error": repr(exc)[:1000]})
            ss = [r["score"] for r in rows]
            dd = [r["delta"] for r in rows]
            direct[cid] = {
                "games": len(rows),
                "score_total": sum(ss),
                "wins": sum(x == 1 for x in ss),
                "losses": sum(x == 0 for x in ss),
                "ties": sum(x == 0.5 for x in ss),
                "mean_delta": statistics.mean(dd) if dd else None,
                "median_delta": statistics.median(dd) if dd else None,
            }

        expected_direct = 2 * len(cfg["fresh_direct_seeds"])
        dg = cfg["direct_gate"]
        eligible = [
            cid for cid, m in direct.items()
            if m["games"] == expected_direct
            and m["score_total"] >= float(dg["min_score_vs_cr029"])
            and m["mean_delta"] is not None and m["mean_delta"] >= float(dg["min_mean_delta"])
        ]
        eligible.sort(key=lambda x: (direct[x]["score_total"], direct[x]["mean_delta"]), reverse=True)
        shortlist = eligible[: int(dg["max_shortlist"])]

        reactive = {}
        opp_dir = Path(args.opponent_dir)
        for cid in shortlist:
            rows = []
            for om in cfg["opponents"]:
                opath = opp_dir / f"{om['id']}.py"
                for seed in map(int, cfg["reactive_seeds"]):
                    for seat in (0, 1):
                        try:
                            control = run_game(tape_agent(base), load_agent(opath), seed, seat)
                            cand = run_game(tape_agent(candidates[cid]["tape"]), load_agent(opath), seed, seat)
                            rows.append({"opponent": om["id"], "seed": seed, "seat": seat, "control": control, "candidate": cand})
                        except Exception as exc:
                            errors.append({"phase": "reactive", "candidate": cid, "opponent": om["id"], "seed": seed, "seat": seat, "error": repr(exc)[:1000]})
            reactive[cid] = paired(rows)

    rg = cfg["reactive_gate"]
    expected_reactive = 2 * len(cfg["reactive_seeds"]) * len(cfg["opponents"])
    passing = [
        cid for cid in shortlist
        if reactive.get(cid, {}).get("games") == expected_reactive
        and reactive[cid]["score_gain"] >= float(rg["min_paired_score_gain_vs_cr029"])
        and reactive[cid]["regressions"] <= int(rg["max_regressions"])
    ]
    passing.sort(key=lambda x: (reactive[x]["score_gain"], -reactive[x]["regressions"], direct[x]["score_total"], direct[x]["mean_delta"]), reverse=True)

    mechanical = not errors and len(candidates) == len(cfg["episodes"]) and all(m["games"] == expected_direct for m in direct.values())
    selected = passing[0] if passing else None
    decision = f"SHORTLIST_{selected}_FOR_PACKAGE_PREFLIGHT" if selected else "CR044_NO_TOP3000_TAPE_PROMOTION"
    compact_candidates = {cid: {k: v for k, v in c.items() if k != "tape"} for cid, c in candidates.items()}
    out = {
        "experiment": cfg["experiment"],
        "source_date": cfg["source_date"],
        "seed_firewall_overlap": overlap,
        "mechanical_complete": mechanical,
        "errors": errors,
        "candidates": compact_candidates,
        "direct": direct,
        "direct_shortlist": shortlist,
        "reactive": reactive,
        "passing": passing,
        "selected_for_next_stage": selected,
        "decision": decision,
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
    }
    op = Path(args.output)
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False))
    if not mechanical:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
