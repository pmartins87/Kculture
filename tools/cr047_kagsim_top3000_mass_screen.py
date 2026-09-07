"""CR047: massive fresh-seed screen of current ~3000 winner tapes with kagsim.

Fixed-vs-fixed only. The bit-exact 1.32.7 C++ engine lets us replace tiny seed
panels with thousands of fresh seasons. Each candidate is tested against the
frozen CR029 full_recent_top stream in both seat orders on every seed.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import tempfile
from pathlib import Path

import kagglehub
import kagsim

import cr035_public_regime_selector_shard as core
import cr043_latest_top3000_probe as p43

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr047_kagsim_top3000_mass_screen.json"


def download_episode(handle: str, eid: int, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=f"{eid}.json", output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))


def make_seeds(spec: dict) -> list[int]:
    r = random.Random(int(spec["master_seed"]))
    lo, hi = int(spec["range_min"]), int(spec["range_max"])
    n = int(spec["count"])
    out = set()
    while len(out) < n:
        out.add(r.randint(lo, hi))
    return sorted(out)


def metrics(results: list[tuple[float, float]]) -> dict:
    margins = [float(a) - float(b) for a, b in results]
    wins = sum(x > 0 for x in margins)
    losses = sum(x < 0 for x in margins)
    ties = len(margins) - wins - losses
    return {
        "games": len(margins),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "score_total": wins + 0.5 * ties,
        "score_rate": (wins + 0.5 * ties) / len(margins) if margins else None,
        "mean_margin": statistics.mean(margins) if margins else None,
        "median_margin": statistics.median(margins) if margins else None,
        "p05_margin": sorted(margins)[max(0, int(0.05 * (len(margins)-1)))] if margins else None,
        "p95_margin": sorted(margins)[min(len(margins)-1, int(0.95 * (len(margins)-1)))] if margins else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    if str(getattr(kagsim, "ENGINE_VERSION", "")) != str(cfg["engine"]):
        raise RuntimeError(f"kagsim engine {getattr(kagsim, 'ENGINE_VERSION', None)} != {cfg['engine']}")
    idle = kagsim.Stream([])
    if tuple(kagsim.run_episode(idle, idle, seed=11)) != (3000.0, 3000.0):
        raise RuntimeError("kagsim idle self-check failed")

    bundle = json.loads(Path(args.source_bundle).read_text(encoding="utf-8"))
    base_actions = bundle["recent_top"]["tape"]
    if len(base_actions) != 719 or core._tape_sha(base_actions) != bundle["recent_top"]["tape_sha256"]:
        raise RuntimeError("CR029 source bundle mismatch")
    base = kagsim.Stream(base_actions)
    seeds = make_seeds(cfg["seed_generator"])

    candidates = {}
    errors = []
    with tempfile.TemporaryDirectory(prefix="cr047-") as td0:
        td = Path(td0)
        for meta in cfg["episodes"]:
            eid = int(meta["episode_id"])
            try:
                rep = download_episode(cfg["day_handle"], eid, td / str(eid))
                steps = rep.get("steps") or []
                if len(steps) != 720:
                    raise RuntimeError(f"episode {eid} has {len(steps)} steps")
                rewards = [float(steps[-1][i].get("reward")) for i in (0,1)]
                win = 0 if rewards[0] >= rewards[1] else 1
                if win != int(meta["winner_seat"]):
                    raise RuntimeError(f"episode {eid} winner seat {win} != frozen {meta['winner_seat']}")
                actions = p43._actions(rep, win)
                if len(actions) != 719:
                    raise RuntimeError(f"episode {eid} tape length {len(actions)}")
                candidates[f"ep{eid}_s{win}"] = {
                    "episode_id": eid,
                    "winner_seat": win,
                    "source_rewards": rewards,
                    "tape_sha256": core._tape_sha(actions),
                    "stream": kagsim.Stream(actions),
                }
            except Exception as exc:
                errors.append({"episode_id": eid, "error": repr(exc)[:1000]})

    reports = {}
    for cid, c in candidates.items():
        stream = c["stream"]
        # Seat 0: candidate vs CR029. Seat 1: CR029 vs candidate, then flip banks.
        jobs0 = [(stream, base, int(s)) for s in seeds]
        jobs1 = [(base, stream, int(s)) for s in seeds]
        r0 = list(kagsim.run_many(jobs0))
        r1raw = list(kagsim.run_many(jobs1))
        r1 = [(b, a) for a, b in r1raw]
        m0, m1 = metrics(r0), metrics(r1)
        both = r0 + r1
        mb = metrics(both)
        reports[cid] = {
            "episode_id": c["episode_id"],
            "winner_seat": c["winner_seat"],
            "source_rewards": c["source_rewards"],
            "tape_sha256": c["tape_sha256"],
            "seat0": m0,
            "seat1": m1,
            "combined": mb,
        }

    gate = cfg["promotion_gate"]
    passing = [
        cid for cid, r in reports.items()
        if r["combined"]["score_rate"] >= float(gate["min_score_rate_vs_cr029"])
        and r["combined"]["mean_margin"] >= float(gate["min_mean_margin"])
    ]
    passing.sort(key=lambda cid: (reports[cid]["combined"]["score_rate"], reports[cid]["combined"]["mean_margin"]), reverse=True)
    ranking = sorted(reports, key=lambda cid: (reports[cid]["combined"]["score_rate"], reports[cid]["combined"]["mean_margin"]), reverse=True)
    selected = passing[0] if passing else None
    payload = {
        "experiment": cfg["experiment"],
        "engine": cfg["engine"],
        "kagsim_self_check": True,
        "seed_generator": cfg["seed_generator"],
        "seed_count": len(seeds),
        "games_per_candidate": len(seeds) * 2,
        "errors": errors,
        "reports": reports,
        "ranking": ranking,
        "passing": passing,
        "selected_for_next_stage": selected,
        "decision": f"SHORTLIST_{selected}_FOR_PACKAGE_PREFLIGHT" if selected else "CR047_NO_STATIC_TOP3000_TAPE_PROMOTION",
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
