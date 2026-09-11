"""Fingerprint a public Kaggriculture hosted-replay policy corpus.

Descriptive research only. Given replay JSONs and a target team name, this tool
measures how replay-like vs state-adaptive the policy is, freezes modal actions,
opening clusters, turn-level consensus, public farm/economy checkpoints, and
basic W/L/T information. Replays where the target team occupies both seats are
skipped because the target submission seat is ambiguous from replay metadata.
It does not infer causality or promote a submission.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import statistics
from pathlib import Path

CHECKPOINTS = (0, 24, 48, 72, 96, 144, 192, 226, 240, 288, 336, 384, 480, 576, 648, 696, 718)


def canon(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def num(x, default=0.0):
    try:
        v = float(x)
        return v if math.isfinite(v) else default
    except Exception:
        return default


def team_names(rep: dict) -> list[str]:
    info = rep.get("info") or {}
    names = info.get("TeamNames") or info.get("teamNames") or []
    return [str(x) for x in names] if isinstance(names, list) else []


def target_seat(rep: dict, target: str) -> int:
    names = team_names(rep)
    exact = [i for i, name in enumerate(names) if name == target]
    if len(exact) == 1:
        return exact[0]
    folded = [i for i, name in enumerate(names) if name.casefold() == target.casefold()]
    if len(folded) == 1:
        return folded[0]
    raise ValueError(f"cannot uniquely identify target {target!r} in {names!r}")


def actions(rep: dict, p: int) -> list:
    steps = rep.get("steps") or []
    out = []
    for t in range(max(0, len(steps) - 1)):
        frame = steps[t + 1][p] if isinstance(steps[t + 1], list) else {}
        out.append(frame.get("action") if isinstance(frame, dict) else None)
    return out


def tile_stats(farm: dict) -> dict:
    crops = collections.Counter(); animals = collections.Counter(); weeds = 0; yield_units = 0.0
    for row in farm.get("tiles") or []:
        if not isinstance(row, list): continue
        for tile in row:
            if not isinstance(tile, dict): continue
            if tile.get("kind") == "PLANT": crops[str(tile.get("crop"))] += 1
            if tile.get("animal"): animals[str(tile.get("animal"))] += 1
            if tile.get("kind") == "WEED": weeds += 1
            yield_units += max(0.0, num(tile.get("yield_units")))
    return {"crops": dict(crops), "animals": dict(animals), "weeds": weeds, "yield_units": yield_units}


def checkpoint(rep: dict, p: int, t: int) -> dict | None:
    steps = rep.get("steps") or []
    if not steps: return None
    t = min(t, len(steps) - 1)
    frame = steps[t][p]
    obs = (frame or {}).get("observation") or {}
    farms = obs.get("farms") or []
    if p >= len(farms): return None
    farm = farms[p] or {}; ts = tile_stats(farm); town = obs.get("town") or {}; market = obs.get("market") or {}
    return {
        "step": int(obs.get("step", t) or t), "day": int(obs.get("day", 0) or 0), "hour": int(obs.get("hour", 0) or 0),
        "money": num(farm.get("money")), "unlocked_quadrants": len(farm.get("unlocked_quadrants") or []),
        "hands": len(farm.get("hands") or []), "unlocked_shops": list(town.get("unlocked_shops") or []),
        "market_prices": dict(market.get("prices") or {}), **ts,
    }


def mean_dict(rows: list[dict], key: str) -> dict:
    all_keys = sorted({k for row in rows for k in (row.get(key) or {})})
    return {k: statistics.mean(num((row.get(key) or {}).get(k)) for row in rows) for k in all_keys}


def summarize_checkpoints(cps: dict[int, list[dict]]) -> dict:
    out = {}
    for t, rows in sorted(cps.items()):
        rows = [r for r in rows if r]
        if not rows: continue
        shops = collections.Counter(tuple(r.get("unlocked_shops") or []) for r in rows)
        out[str(t)] = {
            "n": len(rows), "money_mean": statistics.mean(r["money"] for r in rows),
            "money_median": statistics.median(r["money"] for r in rows),
            "quadrants_mean": statistics.mean(r["unlocked_quadrants"] for r in rows),
            "hands_mean": statistics.mean(r["hands"] for r in rows),
            "yield_units_mean": statistics.mean(r["yield_units"] for r in rows),
            "weeds_mean": statistics.mean(r["weeds"] for r in rows),
            "crops_mean": mean_dict(rows, "crops"), "animals_mean": mean_dict(rows, "animals"),
            "top_shop_worlds": [{"shops": list(k), "count": v} for k, v in shops.most_common(8)],
        }
    return out


def entropy(counter: collections.Counter) -> float:
    total = sum(counter.values())
    if total <= 0: return 0.0
    return -sum((n / total) * math.log2(n / total) for n in counter.values() if n)


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("replay_root"); ap.add_argument("--team", required=True); ap.add_argument("--output", required=True); ap.add_argument("--max-turns", type=int, default=719); args=ap.parse_args()
    files=sorted(Path(args.replay_root).rglob("*replay.json"))
    if not files: raise SystemExit("no replay JSONs found")
    seqs=[]; cps={t:[] for t in CHECKPOINTS}; episodes=[]; errors=[]; outcomes=collections.Counter(); seats=collections.Counter()
    for path in files:
        try:
            rep=json.loads(path.read_text(encoding="utf-8")); p=target_seat(rep,args.team); seq=actions(rep,p)[:args.max_turns]; seqs.append(seq); seats[p]+=1
            for t in CHECKPOINTS: cps[t].append(checkpoint(rep,p,t))
            rewards=list(rep.get("rewards") or [])
            if len(rewards)<2:
                final=rep.get("steps",[[]])[-1]; rewards=[]
                for i in (0,1):
                    try: rewards.append(float(final[i].get("reward")))
                    except Exception: rewards.append(None)
            a=rewards[p] if p < len(rewards) else None; b=rewards[1-p] if 1-p < len(rewards) else None
            if a is not None and b is not None:
                outcomes['win' if a>b else 'loss' if a<b else 'tie'] += 1
            episodes.append({"file":str(path),"seat":p,"team_names":team_names(rep),"steps":len(rep.get("steps") or []),"rewards":rewards})
        except Exception as exc:
            errors.append({"file":str(path),"error":repr(exc)})
    if not seqs: raise SystemExit("no usable target-team replays")
    max_turns=min(args.max_turns,max(len(s) for s in seqs)); turn_rows=[]; modal_actions=[]
    for t in range(max_turns):
        vals=[canon(s[t]) for s in seqs if t<len(s)]; c=collections.Counter(vals); modal,count=c.most_common(1)[0]; modal_actions.append(json.loads(modal))
        turn_rows.append({"turn":t,"n":len(vals),"unique_actions":len(c),"modal_fraction":count/len(vals),"entropy_bits":entropy(c),"modal_action":json.loads(modal),"top_actions":[{"count":n,"fraction":n/len(vals),"action":json.loads(raw)} for raw,n in c.most_common(5)]})
    opening_clusters={}
    for width in (2,8,16,32,64,96,128,192,288):
        c=collections.Counter()
        for seq in seqs:
            raw="\n".join(canon(x) for x in seq[:width]); c[hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]]+=1
        opening_clusters[str(width)]=[{"hash":h,"count":n} for h,n in c.most_common()]
    consensus=[r['modal_fraction'] for r in turn_rows]
    payload={"schema_version":"kculture-hosted-policy-corpus-fingerprint-v2","team":args.team,"usable_replays":len(seqs),"errors":errors,"max_turns":max_turns,"outcomes":dict(outcomes),"seats":dict(seats),"score_rate":(outcomes['win']+0.5*outcomes['tie'])/sum(outcomes.values()) if outcomes else None,"policy_shape":{"unanimous_turns":sum(x==1.0 for x in consensus),"turns_modal_ge_0_90":sum(x>=0.90 for x in consensus),"turns_modal_ge_0_75":sum(x>=0.75 for x in consensus),"mean_modal_fraction":statistics.mean(consensus),"median_modal_fraction":statistics.median(consensus),"first_nonunanimous_turn":next((i for i,x in enumerate(consensus) if x<1.0),None)},"opening_clusters":opening_clusters,"checkpoints":summarize_checkpoints(cps),"turns":turn_rows,"modal_actions":modal_actions,"episodes":episodes,"note":"Descriptive public-replay evidence only; same-team ambiguous replays skipped; no causal or promotion claim."}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({"team":args.team,"usable_replays":len(seqs),"errors":len(errors),"outcomes":dict(outcomes),"seats":dict(seats),"score_rate":payload['score_rate'],"policy_shape":payload['policy_shape'],"opening_clusters_96_top5":opening_clusters['96'][:5],"opening_clusters_288_top5":opening_clusters['288'][:5]},indent=2,ensure_ascii=False))

if __name__=='__main__': main()
