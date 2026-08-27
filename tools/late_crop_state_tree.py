"""KEXP-031: shallow public-state tree for late CARROT-vs-WHEAT seed choice.

Learns from exact official high-Elo public replays. Features are limited to
information legally observable by the acting agent at state t; label is the
seed purchase stored in replay frame t+1.

Model selection uses leave-one-day-out validation across Aug-22..25. Aug-26 is
a strict temporal test and is not used for hyperparameter selection.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import math
import statistics
import tempfile
from pathlib import Path

import kagglehub
from sklearn.tree import DecisionTreeClassifier, export_text

INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"
TRAIN_DATES = ("2026-08-22", "2026-08-23", "2026-08-24", "2026-08-25")
TEST_DATE = "2026-08-26"
START, END = 600, 647
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("GOOSE", "COW", "SHEEP")
SHOPS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file(): raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh: return list(csv.DictReader(fh))


def demand_weights(shops: list[str]) -> dict[str, int]:
    out = collections.Counter({p: 0 for p in PRODUCTS})
    for shop in shops:
        ps = SHOPS.get(shop, ())
        mult = 2 if len(ps) == 1 else 1
        for p in ps: out[p] += mult
    return dict(out)


def market_buys(action) -> tuple[int, int]:
    wb = cb = 0
    if not isinstance(action, dict): return 0, 0
    for order in action.get("market", []) or []:
        if not (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_SEED"): continue
        try: q = max(0, int(order[2] or 0))
        except (TypeError, ValueError): continue
        if order[1] == "WHEAT": wb += q
        elif order[1] == "CARROT": cb += q
    return wb, cb


def tile_counts(farm: dict) -> dict[str, int]:
    out = collections.Counter()
    for row in farm.get("tiles", []) or []:
        for tile in row if isinstance(row, list) else []:
            if not isinstance(tile, dict): continue
            if tile.get("kind") == "PLANT": out[f"plant_{tile.get('crop')}"] += 1
            if tile.get("animal") in ANIMALS: out[f"animal_{tile.get('animal')}"] += 1
            if tile.get("kind") == "WEED": out["weeds"] += 1
    return dict(out)


def num(d, key) -> float:
    try:
        v = float((d or {}).get(key, 0) or 0)
        return v if math.isfinite(v) else 0.0
    except (TypeError, ValueError, AttributeError): return 0.0


def features(obs: dict, player: int) -> dict[str, float]:
    farms = obs.get("farms") or []
    if player >= len(farms): return {}
    own = farms[player]
    opp = farms[1-player] if len(farms) > 1 else {}
    priv = obs.get("private") or {}
    seeds = priv.get("seeds") or {}
    shed = priv.get("shed") or {}
    market = obs.get("market") or {}
    prices = market.get("prices") or {}
    inv = market.get("inventory") or {}
    shops = list(((obs.get("town") or {}).get("unlocked_shops") or []))
    dem = demand_weights(shops)
    oc, pc = tile_counts(own), tile_counts(opp)
    pw = max(1.0, num(prices, "WHEAT")); pcarr = max(1.0, num(prices, "CARROT"))
    f = {
        "step": float(obs.get("step", 0) or 0),
        "money_own": num(own, "money"),
        "money_opp": num(opp, "money"),
        "money_relative": num(own, "money") - num(opp, "money"),
        "hands_own": float(len(own.get("hands", []) or [])),
        "hands_opp": float(len(opp.get("hands", []) or [])),
        "quadrants_own": float(len(own.get("unlocked_quadrants", []) or [])),
        "quadrants_opp": float(len(opp.get("unlocked_quadrants", []) or [])),
        "seed_wheat": num(seeds, "WHEAT"),
        "seed_carrot": num(seeds, "CARROT"),
        "shed_wheat": num(shed, "WHEAT"),
        "shed_carrot": num(shed, "CARROT"),
        "price_wheat": pw,
        "price_carrot": pcarr,
        "price_ratio_carrot_wheat": pcarr / pw,
        "market_inv_wheat": num(inv, "WHEAT"),
        "market_inv_carrot": num(inv, "CARROT"),
        "demand_wheat": float(dem.get("WHEAT", 0)),
        "demand_carrot": float(dem.get("CARROT", 0)),
        "demand_ratio_carrot_wheat": (float(dem.get("CARROT", 0)) + .5) / (float(dem.get("WHEAT", 0)) + .5),
        "opportunity_index": ((float(dem.get("CARROT", 0)) + .5) / (float(dem.get("WHEAT", 0)) + .5)) * (pcarr / pw),
        "own_weeds": float(oc.get("weeds", 0)),
        "opp_weeds": float(pc.get("weeds", 0)),
    }
    for crop in CROPS:
        f[f"own_plant_{crop.lower()}"] = float(oc.get(f"plant_{crop}", 0))
        f[f"opp_plant_{crop.lower()}"] = float(pc.get(f"plant_{crop}", 0))
    for animal in ANIMALS:
        f[f"own_{animal.lower()}"] = float(oc.get(f"animal_{animal}", 0))
        f[f"opp_{animal.lower()}"] = float(pc.get(f"animal_{animal}", 0))
    return f


def final_rewards(rep):
    try:
        final = rep["steps"][-1]
        return [float(final[p].get("reward")) for p in (0,1)]
    except Exception: return [None, None]


def collect_date(date: str, top: int, root: Path) -> list[dict]:
    handle = f"kaggle/kaggriculture-episodes-{date}"
    manifest = sorted(read_csv(download(handle, "manifest.csv", root/date/"manifest")), key=lambda r:-float(r["avg_score"]))[:top]
    out=[]
    for mr in manifest:
        eid=str(mr["episode_id"])
        rep=json.loads(download(handle,f"{eid}.json",root/date/"episodes"/eid).read_text(encoding="utf-8"))
        steps=rep.get("steps") or []; rewards=final_rewards(rep)
        if len(steps)<END+2 or any(r is None for r in rewards): continue
        best=max(rewards)
        names=(rep.get("info") or {}).get("TeamNames") or ["p0","p1"]
        for p in (0,1):
            winner = rewards[p] == best
            for t in range(START,END+1):
                obs=steps[t][p].get("observation") or {}
                action=steps[t+1][p].get("action")
                wb,cb=market_buys(action)
                if wb+cb<=0: continue
                fv=features(obs,p)
                if not fv: continue
                out.append({"date":date,"episode_id":eid,"player":p,"team":names[p] if p<len(names) else f"p{p}","winner":winner,"buy_wheat":wb,"buy_carrot":cb,"carrot_positive":cb>0,"features":fv})
    return out


def metric(y, pred):
    tp=sum(a and b for a,b in zip(y,pred)); fp=sum((not a) and b for a,b in zip(y,pred))
    fn=sum(a and (not b) for a,b in zip(y,pred)); tn=sum((not a) and (not b) for a,b in zip(y,pred))
    return {"n":len(y),"tp":tp,"fp":fp,"tn":tn,"fn":fn,"precision":tp/(tp+fp) if tp+fp else None,"recall":tp/(tp+fn) if tp+fn else None,"predicted_positive":tp+fp,"positive":tp+fn}


def matrix(rows, names):
    return [[float(r["features"].get(n,0.0)) for n in names] for r in rows]


def fit_eval(train, test, names, params):
    clf=DecisionTreeClassifier(random_state=20260827, **params)
    clf.fit(matrix(train,names), [int(r["carrot_positive"]) for r in train])
    pred=[bool(v) for v in clf.predict(matrix(test,names))]
    return clf, metric([bool(r["carrot_positive"]) for r in test],pred)


def select_model(train_rows, names):
    configs=[]
    for depth in (2,3,4):
        for leaf in (10,20,30,40):
            for criterion in ("gini","entropy"):
                params={"max_depth":depth,"min_samples_leaf":leaf,"criterion":criterion}
                folds=[]
                for hold in TRAIN_DATES:
                    tr=[r for r in train_rows if r["date"]!=hold]
                    te=[r for r in train_rows if r["date"]==hold]
                    _,m=fit_eval(tr,te,names,params); m["date"]=hold; folds.append(m)
                precisions=[m["precision"] for m in folds if m["precision"] is not None]
                recalls=[m["recall"] for m in folds if m["recall"] is not None]
                supports=[m["predicted_positive"] for m in folds]
                rec={"params":params,"folds":folds,"worst_precision":min(precisions) if len(precisions)==4 else None,"mean_precision":statistics.mean(precisions) if precisions else None,"mean_recall":statistics.mean(recalls) if recalls else None,"min_predicted_positive":min(supports) if supports else 0}
                rec["cv_eligible"]=(rec["worst_precision"] is not None and rec["worst_precision"]>=0.60 and rec["mean_precision"]>=0.70 and rec["mean_recall"]>=0.10 and rec["min_predicted_positive"]>=3)
                configs.append(rec)
    eligible=[r for r in configs if r["cv_eligible"]]
    pool=eligible or configs
    pool.sort(key=lambda r:((r["worst_precision"] if r["worst_precision"] is not None else -1),(r["mean_precision"] if r["mean_precision"] is not None else -1),(r["mean_recall"] if r["mean_recall"] is not None else -1),-r["params"]["max_depth"],-r["params"]["min_samples_leaf"]),reverse=True)
    return pool[0], configs


def tree_json(clf, names):
    t=clf.tree_
    def node(i):
        vals=t.value[i][0].tolist(); total=sum(vals); p1=(vals[1]/total) if len(vals)>1 and total else 0.0
        if t.children_left[i] == t.children_right[i]: return {"leaf":True,"n":int(t.n_node_samples[i]),"p_carrot":p1,"prediction":int(clf.classes_[vals.index(max(vals))])}
        return {"leaf":False,"feature":names[t.feature[i]],"threshold":float(t.threshold[i]),"n":int(t.n_node_samples[i]),"p_carrot":p1,"left":node(t.children_left[i]),"right":node(t.children_right[i])}
    return node(0)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--top",type=int,default=20); ap.add_argument("--output",required=True); args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="kculture-kexp031-") as tmp:
        root=Path(tmp); idx=read_csv(download(INDEX_HANDLE,"manifest.csv",root/"index")); dates={r["date"] for r in idx}
        missing=[d for d in (*TRAIN_DATES,TEST_DATE) if d not in dates]
        if missing: raise RuntimeError(f"dates absent from official index: {missing}")
        rows=[]
        for d in (*TRAIN_DATES,TEST_DATE): rows.extend(collect_date(d,args.top,root))
    winners=[r for r in rows if r["winner"]]
    train=[r for r in winners if r["date"] in TRAIN_DATES]; test=[r for r in winners if r["date"]==TEST_DATE]
    names=sorted(train[0]["features"].keys()) if train else []
    selected, configs=select_model(train,names)
    clf,testm=fit_eval(train,test,names,selected["params"])
    gate=(selected["cv_eligible"] and testm["predicted_positive"]>=10 and testm["precision"] is not None and testm["precision"]>=0.75 and testm["recall"] is not None and testm["recall"]>=0.15)
    importances=sorted(((names[i],float(v)) for i,v in enumerate(clf.feature_importances_) if v>0),key=lambda x:-x[1])
    payload={"schema_version":"late-crop-state-tree-v1","alignment":"observation frame t paired with action frame t+1","window":[START,END],"train_dates":list(TRAIN_DATES),"test_date":TEST_DATE,"top_n_per_date":args.top,"feature_names":names,"selected_cv":selected,"temporal_test":testm,"gate":{"eligible_for_policy_prototype":gate,"criteria":"LODO CV eligible; Aug-26 support>=10, precision>=0.75, recall>=0.15"},"feature_importances":importances,"tree_text":export_text(clf,feature_names=names,decimals=3),"tree":tree_json(clf,names),"row_counts":{"winner_train":len(train),"winner_test":len(test),"all":len(rows)},"all_configs":configs}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ("selected_cv","temporal_test","gate","feature_importances","tree_text","row_counts")},indent=2,sort_keys=True))

if __name__=="__main__": main()
