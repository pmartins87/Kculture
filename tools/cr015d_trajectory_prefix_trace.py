"""CR-015D: trace every adaptive append/prefix on the five frozen CR-014C flips.

Diagnostic-only and restricted to pre-CR020 frozen cases.  It instruments the
already-frozen CR-015 candidate without changing its actions.  No CR-015 Stage-A
row is read or used.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CFG = ROOT / "configs/cr014c_flip_pairs_v1.json"
CANDIDATE = ROOT / "candidates/cr015_liquidation_phase_early_order.py"


def load_module(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(f"cr015d_{tag}_{time.time_ns()}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def install_trace(module):
    events = []
    original = module._selective_adaptive_sales

    def wrapped(obs, action, player, step):
        before = copy.deepcopy(action)
        prev = module._HISTORY[player].get(step - 24)
        feat = module.C._public_features(obs, prev, player) if prev is not None else {}
        out = original(obs, action, player, step)
        bm = list(before.get("market") or [])
        am = list(out.get("market") or [])
        if bm != am:
            # Candidate only adds adaptive SELL orders; infer additions by
            # multiset subtraction while preserving final order.
            remaining = [copy.deepcopy(x) for x in bm]
            added = []
            for order in am:
                try:
                    idx = remaining.index(order)
                except ValueError:
                    added.append(copy.deepcopy(order))
                else:
                    remaining.pop(idx)
            if added:
                mode = "prefix" if am[:len(added)] == added else "append" if am[-len(added):] == added else "mixed"
                shed = module.C._get(module.C._get(obs, "private", {}) or {}, "shed", {}) or {}
                market = module.C._get(obs, "market", {}) or {}
                prices = module.C._get(market, "prices", {}) or {}
                inv = module.C._get(market, "inventory", {}) or {}
                farms = module.C._get(obs, "farms", []) or []
                own = farms[player] if len(farms) > player else {}
                other = farms[1-player] if len(farms) > 1-player else {}
                probs = {}
                if feat:
                    names = module.C._MODELS["feature_names"]
                    for target, item in module.C.TARGET_TO_ITEM.items():
                        probs[item] = module.C._tree_prob(module.C._MODELS["models"][target], feat, names)
                events.append({
                    "step": int(step),
                    "player": int(player),
                    "mode": mode,
                    "base_market": bm,
                    "final_market": am,
                    "adaptive_added": added,
                    "base_first_op": bm[0][0] if bm and isinstance(bm[0], list) and bm[0] else None,
                    "self_money": float(module.C._get(own, "money", 0) or 0),
                    "opp_money": float(module.C._get(other, "money", 0) or 0),
                    "gap_money": float(module.C._get(own, "money", 0) or 0) - float(module.C._get(other, "money", 0) or 0),
                    "shed_strawberry": int(module.C._get(shed, "STRAWBERRY", 0) or 0),
                    "strawberry_price": float(module.C._get(prices, "STRAWBERRY", 0) or 0),
                    "strawberry_inventory": float(module.C._get(inv, "STRAWBERRY", 0) or 0),
                    "prob_strawberry": probs.get("STRAWBERRY"),
                    "prob_carrot": probs.get("CARROT"),
                })
        return out

    module._selective_adaptive_sales = wrapped
    return events


def play(candidate_module, opponent_path: Path, seed: int, seat: int):
    opponent = load_module(opponent_path, f"opp_{seed}_{seat}")
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run([candidate_module.agent, opponent.agent] if seat == 0 else [opponent.agent, candidate_module.agent])
    rep = env.toJSON()
    frame = rep["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(statuses)
    own = float(frame[seat]["reward"])
    other = float(frame[1-seat]["reward"])
    return {"self": own, "opp": other, "delta": own-other, "score": 1.0 if own>other else 0.0 if own<other else 0.5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    od = Path(args.opponent_dir)
    if not od.is_absolute():
        od = ROOT / od
    cfg = json.loads(CFG.read_text(encoding="utf-8"))

    rows = []
    errors = []
    for entry in cfg["pairs"]:
        seed = int(entry["seed"])
        seat = int(entry["seat"])
        try:
            cand = load_module(CANDIDATE, f"cand_{seed}_{seat}")
            events = install_trace(cand)
            terminal = play(cand, od / f"{entry['opponent']}.py", seed, seat)
            own_events = [e for e in events if e["player"] == seat]
            rows.append({
                "label": entry["label"],
                "opponent": entry["opponent"],
                "seed": seed,
                "seat": seat,
                "terminal": terminal,
                "event_count": len(own_events),
                "prefix_count": sum(e["mode"] == "prefix" for e in own_events),
                "append_count": sum(e["mode"] == "append" for e in own_events),
                "first_prefix_step": next((e["step"] for e in own_events if e["mode"] == "prefix"), None),
                "events": own_events,
            })
        except Exception as exc:
            errors.append({"opponent": entry["opponent"], "seed": seed, "seat": seat, "error": repr(exc)})

    payload = {
        "experiment": "CR-015D-trajectory-prefix-trace",
        "validation_status": "DIAGNOSTIC_ONLY_PRE_CR020_DATA",
        "status": "PASS" if not errors and len(rows) == len(cfg["pairs"]) else "FAIL",
        "rows": rows,
        "errors": errors,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {
        "experiment": payload["experiment"],
        "status": payload["status"],
        "error_count": len(errors),
        "rows": [
            {k: r[k] for k in ("label", "opponent", "seed", "seat", "terminal", "event_count", "prefix_count", "append_count", "first_prefix_step")}
            for r in rows
        ],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    if payload["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
