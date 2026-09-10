"""Authenticated Kaggle API/CLI competition meta scout for Kaggriculture.

Uses only official Kaggle CLI endpoints.  It freezes raw command outputs first,
then opportunistically walks leaderboard -> team-submissions -> episodes -> a
small replay sample.  Parsing is deliberately tolerant because CLI CSV column
names can change.  No submission or mutation command is ever issued.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import time
from pathlib import Path


def run_capture(root: Path, label: str, cmd: list[str]) -> dict:
    p = subprocess.run(cmd, text=True, capture_output=True, check=False)
    rec = {"label": label, "command": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    (root / f"{label}.json").write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    return rec


def csv_rows(text: str) -> list[dict]:
    lines = [x for x in text.splitlines() if x.strip()]
    best: list[dict] = []
    for start in range(len(lines)):
        try:
            rows = list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))
        except Exception:
            continue
        if rows and len(rows[0]) >= 2:
            best = rows
            break
    return best


def normkey(k: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(k).lower())


def first_int(row: dict, preferred: tuple[str, ...], contains: tuple[str, ...] = ()) -> int | None:
    keys = [(normkey(k), k) for k in row if k]
    for target in preferred:
        for nk, raw in keys:
            if nk == target:
                v = str(row.get(raw, "")).strip()
                if re.fullmatch(r"\d+", v): return int(v)
    for nk, raw in keys:
        if all(tok in nk for tok in contains):
            v = str(row.get(raw, "")).strip()
            if re.fullmatch(r"\d+", v): return int(v)
    return None


def unique_keep(xs):
    out=[]; seen=set()
    for x in xs:
        if x not in seen:
            seen.add(x); out.append(x)
    return out


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--competition", default="kaggriculture")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--top-teams", type=int, default=15)
    ap.add_argument("--submissions-per-team", type=int, default=2)
    ap.add_argument("--replays-per-submission", type=int, default=2)
    ap.add_argument("--delay", type=float, default=0.75)
    args=ap.parse_args()
    root=Path(args.output_dir); root.mkdir(parents=True, exist_ok=True)

    report={
        "schema_version":"kculture-kaggle-meta-scout-v1",
        "competition":args.competition,
        "read_only":True,
        "commands":{},
        "leaderboard":{},
        "teams":[],
    }

    version=run_capture(root,"00_version",["kaggle","--version"]); report["commands"]["version"]=version["returncode"]
    own=run_capture(root,"01_own_submissions",["kaggle","competitions","submissions",args.competition,"-v","-q"]); report["commands"]["own_submissions"]=own["returncode"]
    lb=run_capture(root,"02_leaderboard_show",["kaggle","competitions","leaderboard",args.competition,"--show","-v","-q"]); report["commands"]["leaderboard_show"]=lb["returncode"]
    # Freeze the downloadable leaderboard too; failure is non-fatal.
    dl_dir=root/"leaderboard_download"; dl_dir.mkdir(exist_ok=True)
    dl=run_capture(root,"03_leaderboard_download",["kaggle","competitions","leaderboard",args.competition,"--download","-p",str(dl_dir)]); report["commands"]["leaderboard_download"]=dl["returncode"]

    rows=csv_rows(lb["stdout"]) if lb["returncode"]==0 else []
    report["leaderboard"]["parsed_rows"]=len(rows)
    report["leaderboard"]["columns"]=list(rows[0].keys()) if rows else []
    team_ids=[]
    for row in rows:
        tid=first_int(row,("teamid","id"),contains=("team","id"))
        if tid is not None: team_ids.append(tid)
    team_ids=unique_keep(team_ids)[:max(0,args.top_teams)]
    report["leaderboard"]["top_team_ids"]=team_ids

    replay_root=root/"replays"; replay_root.mkdir(exist_ok=True)
    for rank,tid in enumerate(team_ids,1):
        time.sleep(max(0,args.delay))
        trec=run_capture(root,f"team_{rank:02d}_{tid}_submissions",["kaggle","competitions","team-submissions",str(tid),"-v","-q"])
        trows=csv_rows(trec["stdout"]) if trec["returncode"]==0 else []
        sids=[]
        for row in trows:
            sid=first_int(row,("submissionid","id"),contains=("submission","id"))
            if sid is not None: sids.append(sid)
        sids=unique_keep(sids)[:max(0,args.submissions_per_team)]
        tinfo={"rank_order":rank,"team_id":tid,"team_submissions_returncode":trec["returncode"],"parsed_submission_rows":len(trows),"submission_ids":sids,"submissions":[]}
        for si,sid in enumerate(sids,1):
            time.sleep(max(0,args.delay))
            erec=run_capture(root,f"team_{rank:02d}_{tid}_sub_{sid}_episodes",["kaggle","competitions","episodes",str(sid),"-v","-q"])
            erows=csv_rows(erec["stdout"]) if erec["returncode"]==0 else []
            eids=[]
            for row in erows:
                eid=first_int(row,("episodeid","id","episode"),contains=("episode","id"))
                if eid is not None: eids.append(eid)
            eids=unique_keep(eids)
            sinfo={"submission_id":sid,"episodes_returncode":erec["returncode"],"listed_episodes":len(eids),"sample_episode_ids":eids[:max(0,args.replays_per_submission)],"replays":[]}
            for eid in sinfo["sample_episode_ids"]:
                time.sleep(max(0,args.delay))
                folder=replay_root/f"team_{tid}"/f"submission_{sid}"; folder.mkdir(parents=True,exist_ok=True)
                rrec=run_capture(root,f"replay_cmd_{eid}",["kaggle","competitions","replay",str(eid),"-p",str(folder),"-q"])
                sinfo["replays"].append({"episode_id":eid,"returncode":rrec["returncode"]})
            tinfo["submissions"].append(sinfo)
        report["teams"].append(tinfo)

    (root/"meta_scout_report.json").write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8")
    compact={"competition":args.competition,"own_submissions_rc":report["commands"].get("own_submissions"),"leaderboard_rc":report["commands"].get("leaderboard_show"),"leaderboard_rows":report["leaderboard"].get("parsed_rows"),"team_ids":team_ids,"teams_walked":len(report["teams"]),"sample_replays_attempted":sum(len(s["replays"]) for t in report["teams"] for s in t["submissions"])}
    print(json.dumps(compact,indent=2,sort_keys=True))


if __name__=="__main__": main()
