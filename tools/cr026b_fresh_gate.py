"""CR026B rank-10 independent fresh gate.

Rank 10 was frozen as the predeclared backup before CR026A results. This gate
uses new seeds and a deterministic fresh hosted sample that excludes every
episode consumed by CR026A. No opponent/team identity is a runtime feature.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import statistics
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr026b_rank10_frozen_gate.json"
WORK = ROOT / "artifacts/cr026b"
SID = 56025052


def sha(b): return hashlib.sha256(b).hexdigest()
def tape_hash(t): return sha(json.dumps(t, sort_keys=True, separators=(",", ":")).encode())
def write(p, d):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, sort_keys=True), encoding="utf-8")


def load_agent(path):
    spec = importlib.util.spec_from_file_location("cr026b_" + str(time.time_ns()), path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.agent


def runtime_source(tape):
    encoded = json.dumps(tape, sort_keys=True, separators=(",", ":"))
    return '''"""Kculture CR026B frozen recent production route."""
import copy as _copy
import json as _json
_TAPE = _json.loads(%r)
def _clock(obs):
    raw = obs.get("step")
    if raw is not None:
        return int(raw)
    return int(obs.get("day") or 0) * 24 + int(obs.get("hour") or 0)
def agent(obs, config=None):
    return _copy.deepcopy(_TAPE[max(0, min(718, _clock(obs)))])
_cr026b_hosted_entrypoint = agent
''' % encoded


def play(own, opponent, seed, seat, configuration=None):
    from kaggle_environments import make
    cfg = copy.deepcopy(configuration or {})
    cfg.update(seed=int(seed), episodeSteps=720)
    agents = [own, opponent] if seat == 0 else [opponent, own]
    env = make("kaggriculture", configuration=cfg, debug=True)
    env.run(agents)
    steps = env.toJSON()["steps"]; last = steps[-1]
    if len(steps) != 720 or [s["status"] for s in last] != ["DONE", "DONE"]:
        raise RuntimeError("short game or agent execution failure")
    rewards = [float(s["reward"]) for s in last]
    if not all(math.isfinite(r) for r in rewards):
        raise RuntimeError("invalid rewards")
    delta = rewards[seat] - rewards[1-seat]
    trace = [(frame[seat].get("action") or {}) for frame in steps[1:]]
    return dict(seed=seed, seat=seat, rewards=rewards, delta=delta,
                score=1.0 if delta > 0 else 0.0 if delta < 0 else 0.5,
                trace_hash=tape_hash(trace))


def prepare(bundle):
    from build_cr024_consensus_submission import deterministic_tar_gz
    from cr026_live_meta_cr024_benchmark import tape_agent
    cfg = json.loads(CFG.read_text())
    data = json.loads(Path(bundle).read_text())
    src = next(s for s in data["sources"] if s["rank"] == cfg["source"]["rank"])
    tape = src["tape"]; control = data["control"]
    if len(tape) != 719 or tape_hash(tape) != cfg["source"]["tape_sha256"]:
        raise RuntimeError("candidate identity mismatch")
    if tape_hash(control) != cfg["control_tape_sha256"]:
        raise RuntimeError("control identity mismatch")
    pack = WORK / "package"; pack.mkdir(parents=True, exist_ok=True)
    main = pack / "main.py"; main.write_text(runtime_source(tape), encoding="utf-8")
    agent = load_agent(main)
    for t in range(719):
        for obs in ({"step": t}, {"step": None, "day": t // 24, "hour": t % 24}):
            action = agent(obs)
            if action != tape[t]: raise RuntimeError("runtime clock parity")
            action.clear()
            if agent(obs) != tape[t]: raise RuntimeError("runtime mutates its tape")
    checks = []
    for seat in (0, 1):
        seed = cfg["direct_seeds"][0]
        expected = play(tape_agent(tape), tape_agent(control), seed, seat)
        packaged = play(str(main), tape_agent(control), seed, seat)
        if expected != packaged:
            raise RuntimeError("official file entrypoint parity failed")
        checks.append(dict(seat=seat, seed=seed, exact=True))
    notices = pack / "PROVENANCE.txt"
    notices.write_text(
        "Kculture CR026B: public official episode action route.\n"
        f"Episode {cfg['source']['episode_id']} seat {cfg['source']['source_seat']}\n"
        f"Tape SHA256 {cfg['source']['tape_sha256']}\n"
        "No opponent identity or seed-based runtime selection. No runtime network access.\n",
        encoding="utf-8",
    )
    archive = WORK / "CR026B_RECENT_BACKBONE_RANK10_V1.tar.gz"
    deterministic_tar_gz(archive, [(main, "main.py"), (notices, "PROVENANCE.txt")])
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        if len(members) != 2 or {m.name for m in members} != {"main.py", "PROVENANCE.txt"} or not all(m.isfile() for m in members):
            raise RuntimeError("package member mismatch")
        if tf.extractfile("main.py").read() != main.read_bytes():
            raise RuntimeError("archive main mismatch")
    manifest = dict(
        candidate=cfg["candidate"], source=cfg["source"], archive=archive.name,
        archive_sha256=sha(archive.read_bytes()), main_sha256=sha(main.read_bytes()),
        config_sha256=sha(CFG.read_bytes()), archive_bytes=archive.stat().st_size,
        clock_checks=1438, file_entrypoint_parity=checks, mechanical_pass=True,
        runtime_network_required=False, held_out_touched=False,
    )
    write(WORK / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2), flush=True)


def paired_metrics(rows):
    return dict(
        score_gain=sum(r["candidate"]["score"] - r["control"]["score"] for r in rows),
        regressions=sum(r["candidate"]["score"] < r["control"]["score"] for r in rows),
        improvements=sum(r["candidate"]["score"] > r["control"]["score"] for r in rows),
        mean_delta_gain=statistics.mean(r["candidate"]["delta"] - r["control"]["delta"] for r in rows),
    )


def reactive(bundle, opponent, opponent_id):
    from cr026_live_meta_cr024_benchmark import tape_agent
    cfg = json.loads(CFG.read_text()); data = json.loads(Path(bundle).read_text())
    if opponent_id not in cfg["reactive_opponents"]:
        raise RuntimeError("unknown opponent")
    rows = []
    for seed in cfg["seeds"]:
        for seat in (0, 1):
            a = play(tape_agent(data["control"]), load_agent(opponent), seed, seat)
            b = play(str(WORK / "package/main.py"), load_agent(opponent), seed, seat)
            rows.append(dict(control=a, candidate=b))
    result = dict(opponent=opponent_id, rows=rows, completed=len(rows), held_out_touched=False)
    write(WORK / f"reactive_{opponent_id}.json", result)
    print(json.dumps(dict(opponent=opponent_id, completed=len(rows), **paired_metrics(rows)), indent=2), flush=True)


def _fresh_hosted_sample(api, cfg):
    from collect_top_ladder_snapshot import public_episodes
    from fetch_authenticated_hosted_forensics import outcome
    excluded = {int(x) for x in cfg["exclude_hosted_episode_ids"]}
    eligible = []
    for e in public_episodes(api, SID, 200):
        result, seat = outcome(e, SID)
        eid = int(e["id"])
        if eid in excluded or seat not in (0, 1) or result not in ("WIN", "LOSS"):
            continue
        key = sha(f"{cfg['hosted_sampling_salt']}:{eid}".encode())
        eligible.append((key, eid, seat, result, e))
    eligible.sort(key=lambda x: x[0])
    n = int(cfg["hosted_sample_size"])
    if len(eligible) < n:
        raise RuntimeError(f"only {len(eligible)} fresh hosted episodes available; need {n}")
    return eligible[:n], len(eligible)


def hosted(bundle):
    from kaggle.api.kaggle_api_extended import KaggleApi
    from collect_top_ladder_snapshot import download
    from cr026_live_meta_cr024_benchmark import tape_agent, actions_for, final_rewards
    cfg = json.loads(CFG.read_text()); data = json.loads(Path(bundle).read_text())
    api = KaggleApi(); api.authenticate()
    selected, available = _fresh_hosted_sample(api, cfg)
    rows = []; sample = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for key, eid, seat, result, _meta in selected:
            p = download(api, eid, root)
            rep = json.loads(p.read_text())
            tapes = [actions_for(rep, 0), actions_for(rep, 1)]
            if tape_hash(tapes[seat]) != cfg["control_tape_sha256"]:
                raise RuntimeError(f"hosted trace mismatch episode {eid}")
            seed = int(rep["info"]["seed"]); config = rep.get("configuration")
            opp = tapes[1-seat]
            a = play(tape_agent(data["control"]), tape_agent(opp), seed, seat, config)
            original = final_rewards(rep)
            if a["rewards"] != original:
                raise RuntimeError(f"hosted reproduction mismatch episode {eid}")
            b = play(str(WORK / "package/main.py"), tape_agent(opp), seed, seat, config)
            rows.append(dict(episode_id=eid, control=a, candidate=b))
            sample.append(dict(episode_id=eid, seat=seat, original_result=result, sample_key=key))
            p.unlink()
    direct = []
    for seed in cfg["direct_seeds"]:
        for seat in (0, 1):
            direct.append(play(str(WORK / "package/main.py"), tape_agent(data["control"]), seed, seat))
    result = dict(
        rows=rows, direct=direct, sample=sample, fresh_eligible_count=available,
        sampling_salt=cfg["hosted_sampling_salt"], held_out_touched=False,
        limitation="Observed opponent tapes cannot react to the changed candidate.",
    )
    write(WORK / "hosted.json", result)
    print(json.dumps(dict(completed=len(rows), direct_score=sum(r["score"] for r in direct), **paired_metrics(rows)), indent=2), flush=True)


def aggregate():
    cfg = json.loads(CFG.read_text()); g = cfg["gate"]; rows = []; reports = {}
    for opponent in cfg["reactive_opponents"]:
        r = json.loads((WORK / f"reactive_{opponent}.json").read_text())
        if r["opponent"] != opponent or len(r["rows"]) != len(cfg["seeds"]) * 2:
            raise RuntimeError("incomplete reactive shard")
        keys = {(x["candidate"]["seed"], x["candidate"]["seat"]) for x in r["rows"]}
        if keys != {(s, p) for s in cfg["seeds"] for p in (0, 1)}:
            raise RuntimeError("wrong reactive scenarios")
        rows.extend(r["rows"]); reports[opponent] = paired_metrics(r["rows"])
    host = json.loads((WORK / "hosted.json").read_text())
    manifest = json.loads((WORK / "manifest.json").read_text())
    if len(host["rows"]) != cfg["hosted_sample_size"] or len(host["sample"]) != cfg["hosted_sample_size"]:
        raise RuntimeError("incomplete hosted sample")
    if {x["episode_id"] for x in host["sample"]} & set(cfg["exclude_hosted_episode_ids"]):
        raise RuntimeError("hosted sample reused CR026A episodes")
    if len(host["direct"]) != len(cfg["direct_seeds"]) * 2:
        raise RuntimeError("incomplete direct replication")
    a = paired_metrics(rows); b = paired_metrics(host["rows"]); ds = sum(r["score"] for r in host["direct"])
    checks = dict(
        reactive=a["score_gain"] >= g["reactive_min_score_gain"] and a["regressions"] <= g["reactive_max_regressions"],
        hosted=b["score_gain"] >= g["hosted_min_score_gain"] and b["regressions"] <= g["hosted_max_regressions"] and b["mean_delta_gain"] > 0,
        direct=ds >= g["direct_min_score"] and statistics.mean(r["delta"] for r in host["direct"]) > 0,
        package=manifest["mechanical_pass"] and manifest["config_sha256"] == sha(CFG.read_bytes()),
    )
    result = dict(
        candidate=cfg["candidate"], checks=checks, reactive=a, per_opponent=reports,
        hosted=b, hosted_sample=host["sample"], direct_score=ds, manifest=manifest,
        decision="READY_FOR_HOSTED_CALIBRATION" if all(checks.values()) else "REJECT__NO_THRESHOLD_RESCUE",
        held_out_touched=False, automatic_kaggle_submission=False,
    )
    write(WORK / "final.json", result); print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["prepare", "reactive", "hosted", "aggregate"])
    ap.add_argument("--bundle", default=str(WORK / "bundle.json"))
    ap.add_argument("--opponent"); ap.add_argument("--opponent-id")
    a = ap.parse_args()
    if a.mode == "prepare": prepare(a.bundle)
    elif a.mode == "reactive": reactive(a.bundle, a.opponent, a.opponent_id)
    elif a.mode == "hosted": hosted(a.bundle)
    else: aggregate()
