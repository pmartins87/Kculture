"""CR045B: inspect non-step metadata of latest official ~3000 episodes.

The Georgy archive can lag the official daily dataset. This probe reads the
same eight frozen 2026-09-06 episodes directly from Kaggle and records only
compact metadata outside the 720-step payload. Goal: discover stable numeric
submission/team identifiers, if the official JSON exposes them, so later work
can follow the same live agents across episodes.
"""
from __future__ import annotations

import json
from pathlib import Path

import kagglehub

HANDLE = "kaggle/kaggriculture-episodes-2026-09-06"
EPISODES = [106275171,106277936,106272405,106269624,106262306,106255661,106257899,106254763]


def compact(x, depth=0):
    if depth > 5:
        return "<depth>"
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if str(k).lower() == "steps":
                continue
            out[str(k)] = compact(v, depth + 1)
        return out
    if isinstance(x, list):
        if len(x) > 50:
            return {"_type": "list", "length": len(x), "head": [compact(v, depth + 1) for v in x[:3]]}
        return [compact(v, depth + 1) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return repr(x)[:500]


def main():
    root = Path("artifacts/cr045b/data")
    rows = []
    for eid in EPISODES:
        out = root / str(eid)
        out.mkdir(parents=True, exist_ok=True)
        p = Path(kagglehub.dataset_download(HANDLE, path=f"{eid}.json", output_dir=str(out), force_download=True))
        if not p.is_file():
            raise FileNotFoundError(p)
        rep = json.loads(p.read_text(encoding="utf-8"))
        row = {"episode_id": eid, "top_level_keys": sorted(map(str, rep.keys())), "metadata": compact({k:v for k,v in rep.items() if k != "steps"})}
        rows.append(row)
    payload = {"experiment":"CR045B_OFFICIAL_EPISODE_METADATA_PROBE_V1","source":HANDLE,"rows":rows,"observational_only":True,"held_out_touched":False}
    op = Path("artifacts/cr045b/report.json")
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
