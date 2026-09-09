"""Causal lockstep telemetry for CR071M PRESALE1 vs its exact CR070A parent.

For a fixed seed/seat, two independent official Kaggle reference environments are
advanced in lockstep: PRESALE1-vs-CR053 and PARENT-vs-CR053.  Until our own first
action divergence the two worlds must have identical observations.  The first
self divergence is therefore attributable to the counterplay component rather
than a downstream trajectory difference.  This tool is explanatory only and
must not be used as a promotion metric.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import tempfile
import traceback
from pathlib import Path

from kaggle_exact_runtime import (
    AgentProcess,
    agent_visible_observation,
    assert_reference_version,
    done_status,
    extract,
    make_reference_env,
    make_seeds,
    norm,
    reference_config,
    reference_step,
)


def _sell_map(action) -> dict[str, int]:
    out: dict[str, int] = {}
    a = norm(action) if action is not None else None
    if not isinstance(a, dict):
        return out
    for o in (a.get("market") or []):
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
            try:
                q = max(0, int(o[2]))
            except Exception:
                continue
            if q:
                out[str(o[1])] = out.get(str(o[1]), 0) + q
    return out


def _reward_value(x):
    return None if x is None else float(x)


def _score(env, a_seat: int) -> dict:
    rewards = [_reward_value(env.state[p].reward) for p in (0, 1)]
    statuses = [str(env.state[p].status) for p in (0, 1)]
    a_status, b_status = statuses[a_seat], statuses[1 - a_seat]
    if a_status == "DONE" and b_status != "DONE":
        s = 1.0
    elif a_status != "DONE" and b_status == "DONE":
        s = 0.0
    elif a_status != "DONE" or b_status != "DONE":
        s = 0.5
    else:
        if rewards[0] is None or rewards[1] is None:
            raise RuntimeError(f"DONE episode has null reward: {rewards}")
        margin = (rewards[0] - rewards[1]) if a_seat == 0 else (rewards[1] - rewards[0])
        s = 1.0 if margin > 0 else (0.0 if margin < 0 else 0.5)
    return {"score": s, "rewards": rewards, "statuses": statuses}


def _market_snapshot(obs: dict) -> dict:
    m = obs.get("market") or {}
    return {
        "prices": dict(m.get("prices") or {}),
        "inventory": dict(m.get("inventory") or {}),
    }


def play_lockstep(candidate_dir: Path, parent_dir: Path, cr053_dir: Path, seed: int, a_seat: int) -> dict:
    env_c = make_reference_env(seed)
    env_p = make_reference_env(seed)
    config_c = reference_config(env_c)
    config_p = reference_config(env_p)
    ctx = mp.get_context("spawn")
    cand = AgentProcess(ctx, candidate_dir, f"tele_cand_{seed}_{a_seat}")
    par = AgentProcess(ctx, parent_dir, f"tele_parent_{seed}_{a_seat}")
    opp_c = AgentProcess(ctx, cr053_dir, f"tele_oppc_{seed}_{a_seat}")
    opp_p = AgentProcess(ctx, cr053_dir, f"tele_oppp_{seed}_{a_seat}")
    first = None
    pre_divergence_state_mismatch = None
    pre_divergence_opp_action_mismatch = None
    steps = 0
    try:
        while True:
            done_c = all(done_status(s.status) for s in env_c.state)
            done_p = all(done_status(s.status) for s in env_p.state)
            if done_c or done_p:
                if done_c != done_p:
                    raise RuntimeError(f"lockstep completion mismatch candidate={done_c} parent={done_p}")
                break
            obs_ca = agent_visible_observation(env_c, a_seat)
            obs_cb = agent_visible_observation(env_c, 1 - a_seat)
            obs_pa = agent_visible_observation(env_p, a_seat)
            obs_pb = agent_visible_observation(env_p, 1 - a_seat)
            step_c = int(obs_ca.get("step", steps) or steps)
            step_p = int(obs_pa.get("step", steps) or steps)
            if step_c != step_p:
                raise RuntimeError(f"step mismatch {step_c} vs {step_p}")

            states_equal = (norm(obs_ca) == norm(obs_pa)) and (norm(obs_cb) == norm(obs_pb))
            if first is None and not states_equal and pre_divergence_state_mismatch is None:
                pre_divergence_state_mismatch = step_c

            ac, dc = cand.call(obs_ca, config_c)
            ap, dp = par.call(obs_pa, config_p)
            oc, doc = opp_c.call(obs_cb, config_c)
            op, dop = opp_p.call(obs_pb, config_p)
            nac, nap, noc, nop = norm(ac), norm(ap), norm(oc), norm(op)

            if first is None and noc != nop and pre_divergence_opp_action_mismatch is None:
                pre_divergence_opp_action_mismatch = step_c

            if first is None and nac != nap:
                sc, sp = _sell_map(nac), _sell_map(nap)
                keys = sorted(set(sc) | set(sp))
                delta = {k: sc.get(k, 0) - sp.get(k, 0) for k in keys if sc.get(k, 0) != sp.get(k, 0)}
                first = {
                    "step": step_c,
                    "pre_action_worlds_equal": states_equal,
                    "candidate_action": nac,
                    "parent_action": nap,
                    "cr053_action_candidate_world": noc,
                    "cr053_action_parent_world": nop,
                    "sell_delta_candidate_minus_parent": delta,
                    "market_before": _market_snapshot(obs_ca),
                    "market_before_parent": _market_snapshot(obs_pa),
                }

            if a_seat == 0:
                reference_step(env_c, [ac, oc], [dc, doc])
                reference_step(env_p, [ap, op], [dp, dop])
            else:
                reference_step(env_c, [oc, ac], [doc, dc])
                reference_step(env_p, [op, ap], [dop, dp])
            steps += 1
            if first is not None and "market_after" not in first:
                done_c2 = all(done_status(s.status) for s in env_c.state)
                done_p2 = all(done_status(s.status) for s in env_p.state)
                if not done_c2 and not done_p2:
                    first["market_after"] = _market_snapshot(agent_visible_observation(env_c, a_seat))
                    first["market_after_parent"] = _market_snapshot(agent_visible_observation(env_p, a_seat))
            if steps > 725:
                raise RuntimeError("Kaggle environment exceeded expected episode length")

        rc = _score(env_c, a_seat)
        rp = _score(env_p, a_seat)
        return {
            "seed": int(seed),
            "a_seat": int(a_seat),
            "steps": steps,
            "candidate_score": rc["score"],
            "parent_score": rp["score"],
            "score_delta": rc["score"] - rp["score"],
            "candidate_rewards": rc["rewards"],
            "parent_rewards": rp["rewards"],
            "candidate_statuses": rc["statuses"],
            "parent_statuses": rp["statuses"],
            "first_self_divergence": first,
            "pre_divergence_state_mismatch_step": pre_divergence_state_mismatch,
            "pre_divergence_opponent_action_mismatch_step": pre_divergence_opp_action_mismatch,
        }
    finally:
        for p in (cand, par, opp_c, opp_p):
            p.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--parent", required=True)
    ap.add_argument("--cr053", required=True)
    ap.add_argument("--seed-count", type=int, required=True)
    ap.add_argument("--master-seed", type=int, required=True)
    ap.add_argument("--batch-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    assert_reference_version()
    rows, errors = [], []
    seeds = make_seeds(args.seed_count, args.master_seed)
    with tempfile.TemporaryDirectory(prefix="cr071-presale1-lockstep-") as td:
        root = Path(td)
        cdir = extract(Path(args.candidate), root, "candidate")
        pdir = extract(Path(args.parent), root, "parent")
        odir = extract(Path(args.cr053), root, "cr053")
        for seed in seeds:
            for seat in (0, 1):
                try:
                    rows.append(play_lockstep(cdir, pdir, odir, seed, seat))
                except Exception as exc:
                    errors.append({"seed": int(seed), "a_seat": seat, "error": repr(exc), "traceback": traceback.format_exc()[-10000:]})
            print(json.dumps({"batch": args.batch_id, "completed_games": len(rows), "errors": len(errors), "last_seed": int(seed)}), flush=True)
            if errors:
                break
    out = {
        "schema_version": "kculture-cr071-presale1-lockstep-telemetry-v1",
        "purpose": "causal_explanatory_only_no_promotion",
        "reference_backend": "kaggle-environments==1.32.7",
        "batch_id": args.batch_id,
        "master_seed": args.master_seed,
        "seed_count": args.seed_count,
        "rows": rows,
        "errors": errors,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
