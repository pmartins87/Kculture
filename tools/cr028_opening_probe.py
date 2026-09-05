"""CR028 Phase 1: verify the dominant >=3000 opening and compare it with CR024.

No strategic outcome is used here.  This only verifies public replay provenance,
canonical stream hashes, and structural action differences through turn 200.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

from cr026_live_meta_cr024_benchmark import build_cr024

REP = {
    "episode_id": 90919357,
    "seat": 0,
    "rating": 3138.928256637338,
    "stream_h24": "2c1d8379d022b6eb",
    "stream_h100": "b6092398b75bdf7b",
    "stream_h200": "37f58efc325bb97c",
    "stream_h400": "f135bcc40be3a574",
    "stream_h719": "0de6f3873c575d1b",
}


def actions_for(rep: dict, seat: int) -> list[dict]:
    steps = rep.get("steps") or []
    return [copy.deepcopy((steps[t + 1][seat] or {}).get("action") or {}) for t in range(min(719, len(steps)-1))]


def canonical_action(action: dict) -> bytes:
    return json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")


def h(actions: list[dict], n: int, trailing_nul: bool = False) -> str:
    body = b"\0".join(canonical_action(a) for a in actions[:n])
    if trailing_nul and n:
        body += b"\0"
    return hashlib.sha256(body).hexdigest()[:16]


def component_diffs(a: list[dict], b: list[dict], n: int) -> dict:
    out = {"any": 0, "farmer": 0, "hands": 0, "market": 0}
    first = []
    for i,(x,y) in enumerate(zip(a[:n], b[:n])):
        changed = False
        for k in ("farmer","hands","market"):
            if json.dumps(x.get(k), sort_keys=True) != json.dumps(y.get(k), sort_keys=True):
                out[k] += 1; changed = True
        if changed:
            out["any"] += 1
            if len(first) < 20:
                first.append(i)
    out["first_changed_turns"] = first
    return out


def main() -> None:
    api = KaggleApi(); api.authenticate()
    out = Path("artifacts/cr028_opening")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cr028-opening-") as td:
        td = Path(td)
        api.competition_episode_replay(REP["episode_id"], path=str(td), quiet=True)
        rp = td / f"episode-{REP['episode_id']}-replay.json"
        replay = json.loads(rp.read_text(encoding="utf-8"))
        tape = actions_for(replay, REP["seat"])
        cr024, provenance = build_cr024(td / "cr024")

    if len(tape) != 719 or len(cr024) != 719:
        raise RuntimeError((len(tape), len(cr024)))

    boundaries = (24,100,200,400,719)
    expected = {n: REP[f"stream_h{n}"] for n in boundaries}
    standard = {n: h(tape,n,False) for n in boundaries}
    trailing = {n: h(tape,n,True) for n in boundaries}
    standard_matches = {n: standard[n] == expected[n] for n in boundaries}
    trailing_matches = {n: trailing[n] == expected[n] for n in boundaries}
    if all(standard_matches.values()):
        convention = "canonical-json-nul-between-no-trailing"
        hash_fn = lambda acts,n: h(acts,n,False)
    elif all(trailing_matches.values()):
        convention = "canonical-json-nul-after-each"
        hash_fn = lambda acts,n: h(acts,n,True)
    else:
        convention = "UNRESOLVED"
        hash_fn = lambda acts,n: h(acts,n,False)

    cr024_hashes = {n: hash_fn(cr024,n) for n in boundaries}
    result = {
        "experiment": "CR028_DOMINANT_OPENING_PROBE",
        "representative": REP,
        "hash_verification": {
            "convention": convention,
            "expected": expected,
            "standard": standard,
            "standard_matches": standard_matches,
            "trailing": trailing,
            "trailing_matches": trailing_matches,
        },
        "cr024": {
            "provenance": provenance,
            "hashes": cr024_hashes,
            "matches_dominant": {n: cr024_hashes[n] == expected[n] for n in boundaries},
        },
        "prefix_differences": {
            "through_24": component_diffs(tape, cr024, 24),
            "through_100": component_diffs(tape, cr024, 100),
            "through_200": component_diffs(tape, cr024, 200),
        },
        "held_out_touched": False,
        "strategic_outcome_used": False,
    }
    (out / "report.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if convention == "UNRESOLVED":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
