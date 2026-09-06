"""CR032: structural forensics of the CR029 loss regime.

CR029's six official-meta losses are all against keiz source tapes.  This script
uses only those already-open CR029 source episodes and the already-open CR029
backbone.  It does not play games, tune on fresh seeds, or expose identity at
runtime.  Goal: identify high-support component/action differences that are
specific to the loss cohort and therefore worth causal intervention testing.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr031_elite_round_robin.json"
OUT = ROOT / "artifacts/cr032_keiz_regime_forensics"
HANDLE = "kaggle/kaggriculture-episodes-2026-09-05"
LOSS_RANKS = {1, 2, 3, 5, 6, 11}
WIN_RANKS = {4, 7, 8, 9, 10, 12}
KEIZ_WIN_RANKS = {4, 12}
COMPONENTS = ("farmer", "hands", "market")


def canon(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def sha_tape(tape: list[dict]) -> str:
    return hashlib.sha256(canon(tape).encode()).hexdigest()


def actions_for(rep: dict, seat: int) -> list[dict]:
    steps = rep.get("steps") or []
    return [copy.deepcopy((steps[t][seat] or {}).get("action") or {}) for t in range(1, len(steps))]


def component(action: dict, name: str):
    if not isinstance(action, dict):
        return None
    if name == "farmer":
        return copy.deepcopy(action.get("farmer"))
    return copy.deepcopy(action.get(name) or [])


def category(v) -> str:
    if v is None:
        return "NONE"
    if isinstance(v, list) and v:
        first = v[0]
        if isinstance(first, str):
            return first
        if isinstance(first, list) and first:
            return "+".join(str(row[0]) for row in v if isinstance(row, list) and row) or "LIST"
    if isinstance(v, list):
        return "EMPTY"
    return type(v).__name__.upper()


def hamming(a: list[dict], b: list[dict], comp: str, start: int, end: int) -> int:
    return sum(canon(component(a[t], comp)) != canon(component(b[t], comp)) for t in range(start, end))


def mode_info(values: list) -> dict:
    cs = Counter(canon(v) for v in values)
    key, n = cs.most_common(1)[0]
    # recover one exact object
    obj = next(v for v in values if canon(v) == key)
    return {"value": obj, "support": n, "support_rate": n / len(values), "hash": hashlib.sha256(key.encode()).hexdigest()[:16]}


def main() -> None:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    tapes: dict[int, list[dict]] = {}
    meta: dict[int, dict] = {}

    with tempfile.TemporaryDirectory(prefix="cr032-") as td_raw:
        td = Path(td_raw)
        recent = cfg["recent_top"]
        api = KaggleApi(); api.authenticate()
        api.competition_episode_replay(int(recent["episode_id"]), path=str(td), quiet=True)
        rp = td / f"episode-{int(recent['episode_id'])}-replay.json"
        rr = json.loads(rp.read_text(encoding="utf-8"))
        recent_tape = actions_for(rr, int(recent["source_seat"]))
        if len(recent_tape) != 719 or sha_tape(recent_tape) != recent["tape_sha256"]:
            raise RuntimeError("recent_top provenance mismatch")

        for s in cfg["scenarios"]:
            rank = int(s["rank"]); eid = int(s["episode_id"])
            p = Path(kagglehub.dataset_download(HANDLE, path=f"{eid}.json", output_dir=str(td / f"e{eid}"), force_download=True))
            rep = json.loads(p.read_text(encoding="utf-8"))
            tape = actions_for(rep, int(s["winner_seat"]))
            if len(tape) != 719 or sha_tape(tape) != s["tape_sha256"]:
                raise RuntimeError(f"rank {rank} provenance mismatch")
            tapes[rank] = tape
            meta[rank] = s

    pairwise = []
    horizons = [(0,24),(24,48),(48,100),(100,200),(200,400),(400,600),(600,719),(0,719)]
    for rank, tape in sorted(tapes.items()):
        row = {"rank":rank,"team":meta[rank]["team"],"cr029_outcome":"loss" if rank in LOSS_RANKS else "win"}
        for comp in COMPONENTS:
            for a,b in horizons:
                row[f"{comp}_{a}_{b}_diffs"] = hamming(recent_tape, tape, comp, a, b)
        pairwise.append(row)

    steps = []
    templates = {"support4": {c:{} for c in COMPONENTS}, "support5": {c:{} for c in COMPONENTS}, "support6": {c:{} for c in COMPONENTS}}
    for t in range(719):
        for comp in COMPONENTS:
            rv = component(recent_tape[t], comp)
            loss_vals = [component(tapes[r][t], comp) for r in sorted(LOSS_RANKS)]
            win_vals = [component(tapes[r][t], comp) for r in sorted(WIN_RANKS)]
            kwin_vals = [component(tapes[r][t], comp) for r in sorted(KEIZ_WIN_RANKS)]
            lm = mode_info(loss_vals); wm = mode_info(win_vals); km = mode_info(kwin_vals)
            rvk = canon(rv); lmk = canon(lm["value"])
            win_match_loss = sum(canon(v) == lmk for v in win_vals)
            kwin_match_loss = sum(canon(v) == lmk for v in kwin_vals)
            recent_diff = rvk != lmk
            score = (lm["support"] / 6.0) - (win_match_loss / 6.0)
            # High support among losses, different from CR029, and uncommon in wins.
            if recent_diff and lm["support"] >= 4 and win_match_loss <= 2:
                rec = {
                    "step":t,"component":comp,"loss_mode":lm["value"],"loss_support":lm["support"],
                    "loss_support_rate":lm["support_rate"],"win_match_loss_mode":win_match_loss,
                    "keiz_win_match_loss_mode":kwin_match_loss,"discriminative_score":score,
                    "recent_top":rv,"recent_category":category(rv),"loss_mode_category":category(lm["value"]),
                    "win_mode":wm["value"],"win_mode_support":wm["support"],
                    "keiz_win_mode":km["value"],"keiz_win_mode_support":km["support"],
                }
                steps.append(rec)
                for n in (4,5,6):
                    if lm["support"] >= n:
                        templates[f"support{n}"][comp][str(t)] = copy.deepcopy(lm["value"])

    steps.sort(key=lambda x:(x["discriminative_score"],x["loss_support"],-x["win_match_loss_mode"]), reverse=True)
    # Collapse adjacent discriminative steps into blocks for human inspection.
    blocks = []
    for comp in COMPONENTS:
        ts = sorted(x["step"] for x in steps if x["component"] == comp)
        if not ts: continue
        start = prev = ts[0]
        for x in ts[1:]:
            if x == prev + 1:
                prev = x; continue
            blocks.append({"component":comp,"start":start,"end":prev,"length":prev-start+1})
            start = prev = x
        blocks.append({"component":comp,"start":start,"end":prev,"length":prev-start+1})
    blocks.sort(key=lambda x:x["length"], reverse=True)

    template_counts = {k:{c:len(v[c]) for c in COMPONENTS} for k,v in templates.items()}
    out = {
        "experiment":"CR032_KEIZ_LOSS_REGIME_FORENSICS_V1",
        "loss_ranks":sorted(LOSS_RANKS),"win_ranks":sorted(WIN_RANKS),"keiz_win_ranks":sorted(KEIZ_WIN_RANKS),
        "recent_top_tape_sha256":cfg["recent_top"]["tape_sha256"],
        "pairwise_component_distances":pairwise,
        "discriminative_steps":steps,
        "top_discriminative_steps":steps[:80],
        "blocks":blocks,
        "template_counts":template_counts,
        "templates":templates,
        "source_only_already_open":True,"fresh_validation_touched":False,"held_out_touched":False,
        "runtime_identity_features":False,
    }
    (OUT/"report.json").write_text(json.dumps(out,indent=2,sort_keys=True),encoding="utf-8")
    summary = {
        "experiment":out["experiment"],"discriminative_step_count":len(steps),"template_counts":template_counts,
        "largest_blocks":blocks[:20],"top_steps":steps[:30],
        "loss_ranks":sorted(LOSS_RANKS),"win_ranks":sorted(WIN_RANKS),"keiz_win_ranks":sorted(KEIZ_WIN_RANKS),
        "held_out_touched":False,
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
