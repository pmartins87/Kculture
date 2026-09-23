#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
ORDER=("EARLY","PRE_MID","LATE")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();docs=[]
 for p in Path(a.input_dir).rglob("*.json"):
  try:d=json.loads(p.read_text())
  except:continue
  if d.get("schema")=="kculture-v28l-physical-temporal-localization-shard-v1":docs.append(d)
 rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])];mech=len(docs)==4 and all(d.get("mechanical_pass") for d in docs) and not fails and len(rows)==264
 by={}
 for mode in ("BASE",)+ORDER:
  x=[r for r in rows if r["mode"]==mode];wins=[r for r in x if r["base_score"]==0 and r["treatment_score"]==1];ties=[r for r in x if r["base_score"]==0 and r["treatment_score"]==0.5];ds=[r["score_delta"] for r in x];dm=[r["margin_delta"] for r in x]
  by[mode]={"contexts":len(x),"loss_to_win_flips":len(wins),"loss_to_tie_flips":len(ties),"flip_sources":len({r["main_sha256"] for r in wins}),"flip_seeds":len({r["seed"] for r in wins}),"flip_seats":sorted({r["seat"] for r in wins}),"mean_score_delta":statistics.fmean(ds) if ds else 0,"mean_margin_delta":statistics.fmean(dm) if dm else 0,"median_margin_delta":statistics.median(dm) if dm else 0}
  by[mode]["pass"]=mode!="BASE" and by[mode]["loss_to_win_flips"]>=4 and by[mode]["flip_sources"]>=2 and by[mode]["flip_seeds"]>=2 and by[mode]["mean_score_delta"]>0
 passing=[m for m in ORDER if by[m]["pass"]];selected=None
 if passing:selected=sorted(passing,key=lambda m:(-by[m]["loss_to_win_flips"],-by[m]["mean_score_delta"],-by[m]["mean_margin_delta"],ORDER.index(m)))[0]
 decision="V28L_PHYSICAL_TEMPORAL_HEADROOM_LOCALIZED" if mech and selected else ("V28L_NO_ROBUST_PHYSICAL_TEMPORAL_HEADROOM" if mech else "V28L_MECHANICS_INVALID")
 out={"schema":"kculture-v28l-physical-temporal-localization-v1","mechanical_pass":mech,"decision":decision,"selected_window":selected,"by_mode":by,"failures":fails,"automatic_kaggle_submission":False};p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("V28L_RESULT",json.dumps({"mechanical_pass":mech,"decision":decision,"selected_window":selected,"by_mode":by,"failures":len(fails)},sort_keys=True));
 if not mech:raise SystemExit(2)
if __name__=="__main__":main()
