"""CR036: decompose CR035 rank5 handoff into farmer/hands/market component grafts.

Uses the exact CR035 verified source bundle and the exact frozen turn-24 public
classifier.  On Jesse-classified games CR029 is unchanged. On keiz-classified
games only the requested rank5 action components replace CR029 components.
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
SPEC = ROOT / "configs/cr036_rank5_component_graft.json"
OUT = ROOT / "artifacts/cr036_rank5_component_graft/shards"


def _resolve(x: str) -> Path:
    p = Path(x)
    return p if p.is_absolute() else ROOT / p


def _variant_agent(base: list[dict], alt: list[dict], components: tuple[str, ...]):
    state = {"classified": False, "predicted_team": None, "self_money_at_24": None, "grafted": False}

    def agent(obs, config=None):
        s = max(0, min(718, core._step(obs)))
        if not state["classified"] and s >= core.SWITCH_CLOCK:
            money = core._self_money(obs)
            state["classified"] = True
            state["self_money_at_24"] = money
            state["predicted_team"] = "keiz" if money > core.SELF_MONEY_THRESHOLD else "Jesse Bullard"
        action = copy.deepcopy(base[s])
        if state["classified"] and state["predicted_team"] == "keiz" and components:
            src = alt[s]
            for comp in components:
                if comp == "farmer":
                    if "farmer" in src:
                        action["farmer"] = copy.deepcopy(src.get("farmer"))
                    else:
                        action.pop("farmer", None)
                else:
                    action[comp] = copy.deepcopy(src.get(comp) or [])
            state["grafted"] = True
        return action

    return agent, state


def _verify_bundle(bundle: dict, cfg: dict, spec: dict) -> tuple[list[dict], list[dict], dict[int, dict]]:
    frozen = bundle.get("classifier") or {}
    if int(frozen.get("switch_clock")) != int(spec["switch_clock"]):
        raise RuntimeError("bundle/spec switch clock mismatch")
    if float(frozen.get("threshold")) != float(spec["classifier"]["threshold"]):
        raise RuntimeError("bundle/spec threshold mismatch")
    recent = cfg["recent_top"]
    br = bundle["recent_top"]
    base = br["tape"]
    if len(base) != 719 or core._tape_sha(base) != recent["tape_sha256"]:
        raise RuntimeError("CR029 bundle provenance mismatch")
    scenarios: dict[int, dict] = {}
    for s in cfg["scenarios"]:
        rank = int(s["rank"]); b = bundle["scenarios"][str(rank)]; tape = b["tape"]
        if (
            int(b["episode_id"]) != int(s["episode_id"]) or
            int(b["seed"]) != int(s["seed"]) or
            b["team"] != s["team"] or
            len(tape) != 719 or core._tape_sha(tape) != s["tape_sha256"]
        ):
            raise RuntimeError(f"scenario r{rank} provenance mismatch")
        scenarios[rank] = {
            "rank": rank, "team": s["team"], "episode_id": int(s["episode_id"]),
            "seed": int(s["seed"]), "configuration": b.get("configuration") or {}, "tape": tape,
        }
    alt_rank = int(spec["alternate_rank"])
    return base, scenarios[alt_rank]["tape"], scenarios


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant-id", type=int, required=True)
    ap.add_argument("--source-bundle", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    variant = next((v for v in spec["variants"] if int(v["id"]) == int(args.variant_id)), None)
    if variant is None:
        raise SystemExit("unknown variant-id")
    components = tuple(str(x) for x in variant["components"])
    allowed = {"farmer", "hands", "market"}
    if len(set(components)) != len(components) or not set(components) <= allowed:
        raise RuntimeError("invalid component set")

    bundle = json.loads(_resolve(args.source_bundle).read_text(encoding="utf-8"))
    base, alt, scenarios = _verify_bundle(bundle, cfg, spec)
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    errors: list[dict] = []

    for rank, sc in sorted(scenarios.items()):
        for seat in (0, 1):
            try:
                own, state = _variant_agent(base, alt, components)
                opp = core._tape_agent(sc["tape"])
                conf = copy.deepcopy(sc["configuration"])
                conf["episodeSteps"] = 720; conf["seed"] = int(sc["seed"])
                env = make("kaggriculture", configuration=conf, debug=True)
                env.run([own, opp] if seat == 0 else [opp, own])
                rep = env.toJSON()
                if not core._final_ok(rep):
                    raise RuntimeError(f"non-DONE steps={len(rep.get('steps') or [])}")
                rew = core._rewards(rep); sr = rew[seat]; orun = rew[1-seat]; delta = sr-orun
                pred = state["predicted_team"]
                rows.append({
                    "variant_id": int(variant["id"]), "variant_name": variant["name"],
                    "components": list(components), "opponent_rank": rank, "opponent_team": sc["team"],
                    "episode_id": sc["episode_id"], "seed": sc["seed"], "seat": seat,
                    "self_reward": sr, "opp_reward": orun, "delta": delta, "score": core._wl(delta),
                    "predicted_team": pred, "classifier_correct": pred == sc["team"],
                    "self_money_at_24": state["self_money_at_24"], "grafted": bool(state["grafted"]),
                })
            except Exception as exc:
                errors.append({"opponent_rank": rank, "seat": seat, "error": repr(exc)})

    keiz = [r for r in rows if r["opponent_team"] == "keiz"]
    jesse = [r for r in rows if r["opponent_team"] == "Jesse Bullard"]
    out = {
        "experiment": "CR036_RANK5_COMPONENT_GRAFT_V1",
        "variant_id": int(variant["id"]), "variant_name": variant["name"], "components": list(components),
        "alternate_rank": int(spec["alternate_rank"]), "mechanical_complete": not errors and len(rows)==24,
        "errors": errors, "all": core._summary(rows), "keiz": core._summary(keiz), "jesse": core._summary(jesse),
        "classifier_correct": sum(bool(r["classifier_correct"]) for r in rows), "classifier_total": len(rows),
        "grafted_games": sum(bool(r["grafted"]) for r in rows), "rows": rows,
        "source_scenarios_already_open": True, "fresh_validation_touched": False,
        "held_out_touched": False, "runtime_identity_features": False,
    }
    p = OUT / f"variant_{int(variant['id']):02d}.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k != "rows"}, indent=2, sort_keys=True))
    if errors or len(rows) != 24:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
