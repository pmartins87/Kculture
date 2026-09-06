"""CR031: screen CR029's 12 exact elite benchmark winner tapes as candidate backbones.

Uses only already-open CR029 source scenarios and already-open CR029 direct seeds.
Each elite candidate is evaluated against the other eleven elite tapes in both seats,
then directly against full_recent_top on the six CR029 pairwise seeds.  No identity
feature is available to the runtime agents; candidates are complete deterministic tapes.
"""
from __future__ import annotations

import copy
import hashlib
import json
import statistics
import tempfile
from pathlib import Path

import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr031_elite_round_robin.json"
OUT = ROOT / "artifacts/cr031_elite_round_robin"
HANDLE = "kaggle/kaggriculture-episodes-2026-09-05"


def tape_sha(actions: list[dict]) -> str:
    body = json.dumps(actions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def actions_for(rep: dict, player: int) -> list[dict]:
    steps = rep.get("steps") or []
    return [copy.deepcopy((steps[t][player] or {}).get("action") or {}) for t in range(1, len(steps))]


def runtime_source(actions: list[dict], label: str) -> str:
    payload = json.dumps(actions, separators=(",", ":"), sort_keys=True)
    return f'''"""{label}: deterministic complete action tape."""\nimport copy as _copy\nimport json as _json\n_T=_json.loads({payload!r})\ndef _clock(obs):\n    try:\n        raw=obs.get("step")\n        if raw is not None:return max(0,int(raw))\n    except Exception:pass\n    try:return max(0,int(obs.get("day") or 0))*24+max(0,int(obs.get("hour") or 0))\n    except Exception:return 0\ndef agent(obs,config=None):\n    return _copy.deepcopy(_T[max(0,min(len(_T)-1,_clock(obs)))]) if _T else {{}}\n'''


def dl_episode(eid: int, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(HANDLE, path=f"{eid}.json", output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))


def final_statuses(rep: dict) -> list[str | None]:
    steps = rep.get("steps") or []
    if not steps:
        return [None, None]
    return [steps[-1][i].get("status") for i in (0, 1)]


def final_rewards(rep: dict) -> list[float]:
    steps = rep.get("steps") or []
    if not steps:
        raise RuntimeError("empty replay")
    return [float(steps[-1][i].get("reward")) for i in (0, 1)]


def wl(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def play(own: Path, opp: Path, seed: int, seat: int, configuration: dict | None = None) -> dict:
    cfg = copy.deepcopy(configuration) if isinstance(configuration, dict) else {}
    cfg["episodeSteps"] = 720
    cfg["seed"] = int(seed)
    agents = [str(own), str(opp)] if seat == 0 else [str(opp), str(own)]
    env = make("kaggriculture", configuration=cfg, debug=True)
    env.run(agents)
    rep = env.toJSON()
    statuses = final_statuses(rep)
    if len(rep.get("steps") or []) != 720 or statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"short/non-DONE steps={len(rep.get('steps') or [])} statuses={statuses}")
    rewards = final_rewards(rep)
    own_reward = rewards[seat]
    opp_reward = rewards[1-seat]
    delta = own_reward - opp_reward
    return {"self_reward": own_reward, "opp_reward": opp_reward, "delta": delta, "score": wl(delta)}


def summarize(rows: list[dict]) -> dict:
    scores = [float(r["score"]) for r in rows]
    deltas = [float(r["delta"]) for r in rows]
    return {
        "games": len(rows),
        "wins": sum(x == 1.0 for x in scores),
        "losses": sum(x == 0.0 for x in scores),
        "ties": sum(x == 0.5 for x in scores),
        "score_total": sum(scores),
        "score_rate": sum(scores)/len(scores) if scores else None,
        "mean_delta": statistics.mean(deltas) if deltas else None,
        "median_delta": statistics.median(deltas) if deltas else None,
    }


def main() -> None:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[dict] = []
    report_rows: list[dict] = []
    direct_rows: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="cr031-") as td_raw:
        td = Path(td_raw)
        scenario_data: dict[int, dict] = {}
        agent_paths: dict[str, Path] = {}

        # Recover and verify the exact CR029 backbone.
        recent = cfg["recent_top"]
        api = KaggleApi(); api.authenticate()
        recent_dir = td / "recent"
        recent_dir.mkdir(parents=True, exist_ok=True)
        api.competition_episode_replay(int(recent["episode_id"]), path=str(recent_dir), quiet=True)
        rp = recent_dir / f"episode-{int(recent['episode_id'])}-replay.json"
        recent_rep = json.loads(rp.read_text(encoding="utf-8"))
        recent_tape = actions_for(recent_rep, int(recent["source_seat"]))
        if len(recent_tape) != 719 or tape_sha(recent_tape) != recent["tape_sha256"]:
            raise RuntimeError("CR029 recent_top tape provenance mismatch")
        recent_path = td / "full_recent_top.py"
        recent_path.write_text(runtime_source(recent_tape, "CR031_CR029_CONTROL"), encoding="utf-8")
        agent_paths["full_recent_top"] = recent_path

        # Recover the 12 exact elite source tapes already opened by CR029.
        for s in cfg["scenarios"]:
            rank = int(s["rank"])
            eid = int(s["episode_id"])
            rep = dl_episode(eid, td / "episodes" / str(eid))
            tape = actions_for(rep, int(s["winner_seat"]))
            observed = tape_sha(tape)
            if len(tape) != 719 or observed != s["tape_sha256"]:
                raise RuntimeError(f"elite r{rank} tape mismatch: {observed}")
            info = rep.get("info") or {}
            observed_seed = int(info.get("seed"))
            if observed_seed != int(s["seed"]):
                raise RuntimeError(f"elite r{rank} seed mismatch {observed_seed}")
            cid = f"elite_r{rank:02d}"
            p = td / f"{cid}.py"
            p.write_text(runtime_source(tape, f"CR031_{cid}"), encoding="utf-8")
            agent_paths[cid] = p
            scenario_data[rank] = {
                "rank": rank,
                "episode_id": eid,
                "seed": observed_seed,
                "team": s["team"],
                "configuration": rep.get("configuration") if isinstance(rep.get("configuration"), dict) else {},
                "opponent_path": p,
            }

        # Baseline CR029 on every already-open elite scenario.
        baseline_by_key: dict[tuple[int,int], dict] = {}
        for rank, sc in sorted(scenario_data.items()):
            for seat in (0, 1):
                try:
                    z = play(recent_path, sc["opponent_path"], sc["seed"], seat, sc["configuration"])
                    row = {"candidate_id":"full_recent_top","candidate_source_rank":None,"opponent_rank":rank,"opponent_team":sc["team"],"seat":seat,**z}
                    report_rows.append(row)
                    baseline_by_key[(rank, seat)] = row
                except Exception as exc:
                    errors.append({"phase":"baseline","opponent_rank":rank,"seat":seat,"error":repr(exc)})

        candidate_reports = []
        gate_cfg = cfg["screen_gate"]
        for s in cfg["scenarios"]:
            rank = int(s["rank"])
            cid = f"elite_r{rank:02d}"
            own = agent_paths[cid]
            elite_rows = []
            # Leave the candidate's own source scenario out of the cross-generalization score.
            for opp_rank, sc in sorted(scenario_data.items()):
                if opp_rank == rank:
                    continue
                for seat in (0, 1):
                    try:
                        z = play(own, sc["opponent_path"], sc["seed"], seat, sc["configuration"])
                        row = {"candidate_id":cid,"candidate_source_rank":rank,"candidate_team":s["team"],"opponent_rank":opp_rank,"opponent_team":sc["team"],"seat":seat,**z}
                        report_rows.append(row); elite_rows.append(row)
                    except Exception as exc:
                        errors.append({"phase":"elite","candidate_id":cid,"opponent_rank":opp_rank,"seat":seat,"error":repr(exc)})

            base_subset = [baseline_by_key[(opp_rank, seat)] for opp_rank in scenario_data if opp_rank != rank for seat in (0,1) if (opp_rank,seat) in baseline_by_key]
            elite_m = summarize(elite_rows)
            base_m = summarize(base_subset)
            paired_score_gain = elite_m["score_total"] - base_m["score_total"]
            paired_mean_delta_gain = elite_m["mean_delta"] - base_m["mean_delta"] if elite_m["mean_delta"] is not None and base_m["mean_delta"] is not None else None

            # Direct complete-policy challenge on the CR029 seeds that are already open.
            dr = []
            for seed in cfg["direct_seeds_already_open"]:
                for seat in (0, 1):
                    try:
                        z = play(own, recent_path, int(seed), seat, None)
                        row = {"candidate_id":cid,"candidate_source_rank":rank,"candidate_team":s["team"],"seed":int(seed),"seat":seat,**z}
                        direct_rows.append(row); dr.append(row)
                    except Exception as exc:
                        errors.append({"phase":"direct","candidate_id":cid,"seed":int(seed),"seat":seat,"error":repr(exc)})
            direct_m = summarize(dr)
            passed = (
                len(elite_rows) == 22 and len(dr) == 12
                and paired_score_gain >= float(gate_cfg["paired_score_gain_vs_recent_top_excluding_self_min"])
                and paired_mean_delta_gain is not None and paired_mean_delta_gain > float(gate_cfg["paired_mean_delta_gain_vs_recent_top_excluding_self_min"])
                and direct_m["wins"] >= int(gate_cfg["direct_wins_vs_recent_top_min"])
                and direct_m["mean_delta"] is not None and direct_m["mean_delta"] > float(gate_cfg["direct_mean_delta_vs_recent_top_min"])
            )
            candidate_reports.append({
                "candidate_id":cid,"source_rank":rank,"team":s["team"],"episode_id":int(s["episode_id"]),"tape_sha256":s["tape_sha256"],
                "elite_cross_generalization":elite_m,"matched_recent_top_baseline":base_m,
                "paired_score_gain_vs_recent_top_excluding_self":paired_score_gain,
                "paired_mean_delta_gain_vs_recent_top_excluding_self":paired_mean_delta_gain,
                "direct_vs_recent_top":direct_m,"screen_pass":passed,
            })

        candidate_reports.sort(key=lambda x:(bool(x["screen_pass"]),x["paired_score_gain_vs_recent_top_excluding_self"],x["direct_vs_recent_top"]["score_total"],x["paired_mean_delta_gain_vs_recent_top_excluding_self"] or -1e30),reverse=True)
        shortlist = [x["candidate_id"] for x in candidate_reports if x["screen_pass"]]
        baseline_all = summarize([r for r in report_rows if r["candidate_id"] == "full_recent_top"])
        out = {
            "experiment":"CR031_ELITE_COMPLETE_TAPE_ROUND_ROBIN_V1",
            "mechanical_complete":not errors and len(baseline_by_key)==24,
            "errors":errors,
            "baseline_recent_top_all_12":baseline_all,
            "candidate_reports":candidate_reports,
            "shortlist":shortlist,
            "decision":"CR031_SHORTLIST_READY" if shortlist else "CR031_NO_ELITE_TAPE_BEATS_CR029_GATE",
            "source_scenarios_already_open":True,
            "direct_seeds_already_open":True,
            "fresh_validation_touched":False,
            "held_out_touched":False,
            "runtime_identity_features":False,
            "report_rows":report_rows,
            "direct_rows":direct_rows,
        }
        (OUT/"report.json").write_text(json.dumps(out,indent=2,sort_keys=True),encoding="utf-8")
        compact = {
            "decision":out["decision"],"mechanical_complete":out["mechanical_complete"],"error_count":len(errors),
            "baseline":baseline_all,"shortlist":shortlist,
            "ranking":[{
                "candidate_id":x["candidate_id"],"team":x["team"],"source_rank":x["source_rank"],
                "elite_score":x["elite_cross_generalization"]["score_total"],
                "elite_wins":x["elite_cross_generalization"]["wins"],
                "paired_gain":x["paired_score_gain_vs_recent_top_excluding_self"],
                "paired_mean_delta_gain":x["paired_mean_delta_gain_vs_recent_top_excluding_self"],
                "direct_wins":x["direct_vs_recent_top"]["wins"],
                "direct_score":x["direct_vs_recent_top"]["score_total"],
                "direct_mean_delta":x["direct_vs_recent_top"]["mean_delta"],
                "pass":x["screen_pass"],
            } for x in candidate_reports]
        }
        (OUT/"summary.json").write_text(json.dumps(compact,indent=2,sort_keys=True),encoding="utf-8")
        print(json.dumps(compact,indent=2,sort_keys=True))
        if errors:
            raise SystemExit(3)


if __name__ == "__main__":
    main()
