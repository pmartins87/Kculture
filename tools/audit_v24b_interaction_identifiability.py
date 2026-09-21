#!/usr/bin/env python3
"""V24B compact interaction distillation identifiability audit."""
from __future__ import annotations
import argparse,collections,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from solver.programme_features import features as programme_features
from tools.kaggle_exact_runtime import assert_reference_version,make_reference_env,agent_visible_observation

SELECTED_FAMILY="M_TO_P|hands|2"
TRAIN={"F01","F03","F05"}
HOLD={"F02","F04","F08"}

def hfeat(vals):
    payload=json.dumps([float(x) for x in vals],separators=(",",":"))
    return hashlib.sha256(payload.encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v24a",required=True)
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    assert_reference_version()

    d=json.loads(Path(args.v24a).read_text())
    cfg=json.loads(Path(args.hard_config).read_text())
    if d.get("decision")!="V24A_COMPACT_COUPLED_EVENT_FAMILY_FOUND":
        raise SystemExit("binding V24A decision mismatch")
    if str(d.get("selected_family",{}).get("family"))!=SELECTED_FAMILY:
        raise SystemExit("selected family mismatch")

    occ=list(d.get("selected_occurrences") or [])
    if len(occ)!=63:
        raise SystemExit(f"expected 63 selected interaction occurrences, got {len(occ)}")

    # R1: one exact market+hands label pair.
    def label_pair(x):
        return json.dumps({
          "start_shadow_market":x["start_shadow"]["market"],
          "end_shadow_hands":x["end_shadow"]["hands"],
        },sort_keys=True,separators=(",",":"))

    train=[x for x in occ if x["cluster"] in TRAIN]
    hold=[x for x in occ if x["cluster"] in HOLD]
    train_counts=collections.Counter(label_pair(x) for x in train)
    dominant_label,dominant_n=train_counts.most_common(1)[0]
    train_cov=dominant_n/len(train)
    hold_dom=sum(label_pair(x)==dominant_label for x in hold)
    hold_cov=hold_dom/len(hold)

    # Event presence across all hard contexts. OTHER_HARD cannot be relabeled
    # as negative if it actually contains the selected event.
    family_present=set()
    annotation_by_context={}
    for r in d.get("rows",[]):
        cid=str(r["context_id"])
        annotation_by_context[cid]=str(r["annotation"])
        if any(str(e.get("family"))==SELECTED_FAMILY for e in r.get("events",[])):
            family_present.add(cid)
    hard_ids={str(c["context_id"]) for c in cfg["hard_contexts"]}
    if hard_ids != {str(r["context_id"]) for r in d.get("rows",[])}:
        raise SystemExit("V24A/hard-config context mismatch")

    other_ids={cid for cid,a in annotation_by_context.items() if a=="OTHER_HARD"}
    valid_other_negative=sorted(other_ids-family_present)
    interaction_non_event=sorted(
      {cid for cid,a in annotation_by_context.items() if a=="INTERACTION_EXCLUSIVE"}-family_present
    )

    # Reconstruct exact legal turn-0 feature vector for every selected occurrence.
    state_cache={}
    for seed,seat in sorted({(int(x["seed"]),int(x["seat"])) for x in occ}):
        env=make_reference_env(seed)
        obs=agent_visible_observation(env,seat)
        feat=programme_features(obs)
        state_cache[(seed,seat)]={
          "feature_hash":hfeat(feat.tolist()),
          "features":[float(v) for v in feat.tolist()],
          "step":int(obs.get("step",0)),
        }

    state_labels=collections.defaultdict(lambda:collections.Counter())
    state_rows=collections.defaultdict(list)
    for x in occ:
        st=state_cache[(int(x["seed"]),int(x["seat"]))]
        label=json.dumps(x["start_shadow"]["market"],sort_keys=True,separators=(",",":"))
        key=(st["feature_hash"],x["start_base"]["action_key"])
        state_labels[key][label]+=1
        state_rows[key].append({
          "context_id":x["context_id"],"cluster":x["cluster"],"source_rank":x["source_rank"],
          "main_sha256":x["main_sha256"],"seed":x["seed"],"seat":x["seat"],"label":label,
        })

    conflicting=[]
    for key,cnt in state_labels.items():
        if len(cnt)>1:
            conflicting.append({
              "feature_hash":key[0],"base_action_key":key[1],
              "label_counts":dict(cnt),
              "clusters":sorted({r["cluster"] for r in state_rows[key]}),
              "source_shas":sorted({r["main_sha256"] for r in state_rows[key]}),
              "rows":state_rows[key],
            })

    r1_pass=(
      train_cov>=0.70
      and len({x["cluster"] for x in train if label_pair(x)==dominant_label})==3
      and len({x["main_sha256"] for x in train if label_pair(x)==dominant_label})>=3
      and len({int(x["seed"]) for x in train if label_pair(x)==dominant_label})>=2
      and hold_cov>=0.50
      and len({x["cluster"] for x in hold if label_pair(x)==dominant_label})==3
    )

    # R2 needs valid negatives for "family start event" and an identifiable label.
    r2_valid_negative_count=len(valid_other_negative)+len(interaction_non_event)
    r2_identifiable=(len(conflicting)==0)
    r2_possible=r2_valid_negative_count>0 and r2_identifiable

    if r1_pass:
        decision="V24B_R1_DISTILLABLE"
    elif r2_possible:
        decision="V24B_R2_REQUIRES_TREE_FIT"
    else:
        decision="V24B_NOT_DISTILLABLE_COMPACTLY"

    result={
      "schema":"kculture-all3-v24b-identifiability-audit-v1",
      "mechanical_pass":True,
      "selected_family":SELECTED_FAMILY,
      "train_clusters":sorted(TRAIN),"holdout_clusters":sorted(HOLD),
      "train_occurrences":len(train),"holdout_occurrences":len(hold),
      "r1":{
        "label_pair_counts":dict(train_counts),
        "dominant_label_pair":dominant_label,
        "dominant_train_count":dominant_n,
        "dominant_train_coverage":train_cov,
        "dominant_holdout_count":hold_dom,
        "dominant_holdout_coverage":hold_cov,
        "pass":r1_pass,
      },
      "event_presence":{
        "hard_contexts":len(hard_ids),
        "family_present_contexts":len(family_present),
        "other_hard_contexts":len(other_ids),
        "other_hard_without_family":len(valid_other_negative),
        "interaction_exclusive_without_family":len(interaction_non_event),
        "valid_negative_start_states":r2_valid_negative_count,
      },
      "legal_state_identifiability":{
        "unique_seed_seat_states":len(state_cache),
        "unique_feature_plus_base_action_keys":len(state_labels),
        "conflicting_state_keys":len(conflicting),
        "conflicts":conflicting,
        "identifiable":r2_identifiable,
      },
      "r2_possible":r2_possible,
      "decision":decision,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V24B_AUDIT_RESULT",json.dumps({
      "decision":decision,
      "train_occurrences":len(train),"holdout_occurrences":len(hold),
      "r1_train_coverage":train_cov,"r1_holdout_coverage":hold_cov,"r1_pass":r1_pass,
      "family_present_contexts":len(family_present),"hard_contexts":len(hard_ids),
      "valid_negative_start_states":r2_valid_negative_count,
      "unique_legal_states":len(state_labels),"conflicting_legal_states":len(conflicting),
      "r2_identifiable":r2_identifiable,"r2_possible":r2_possible,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
