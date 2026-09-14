"""CR087 discovery: mine the current Kaggriculture top-lineage from public replays.

Offline/discovery only. It uses public submission IDs/replays to extract action tapes,
then measures pairwise Hamming distance, a medoid tape, and per-step modal consensus.
No team/submission identity is intended as a runtime feature.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, statistics, time
from pathlib import Path
import requests

LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
REPLAY_URL = "https://www.kaggleusercontent.com/episodes/{id}.json"
PASS = {"farmer":["PASS"],"hands":[],"market":[]}


def fetch_json(url, *, post=None, tries=5, timeout=120):
    last=None
    for i in range(tries):
        try:
            r=requests.post(url,json=post,timeout=timeout) if post is not None else requests.get(url,timeout=timeout)
            r.raise_for_status(); return r.json()
        except Exception as exc:
            last=exc
            if i+1<tries: time.sleep(2*(i+1))
    raise last


def canon(a):
    return json.dumps(a if isinstance(a,dict) else PASS,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def locate_seat(meta, sid):
    for a in meta.get("agents") or []:
        if int(a.get("submissionId") or -1)==int(sid):
            return int(a.get("index") or 0)
    raise RuntimeError(f"submission {sid} absent from episode {meta.get('id')}")


def load_episode(meta, sid):
    eid=int(meta["id"]); seat=locate_seat(meta,sid)
    rep=fetch_json(REPLAY_URL.format(id=eid)); steps=rep.get("steps") or []
    if len(steps)<720: raise RuntimeError(f"short replay {eid}: {len(steps)}")
    tape=[]
    for t in range(719):
        action=(steps[t+1][seat] or {}).get("action") or PASS
        tape.append(copy.deepcopy(action))
    return {"episode_id":eid,"submission_id":int(sid),"seat":seat,"end_time":meta.get("endTime"),"tape":tape}


def hamming(a,b):
    return sum(canon(x)!=canon(y) for x,y in zip(a,b))


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--targets",required=True); ap.add_argument("--output-dir",required=True); ap.add_argument("--episodes-per-submission",type=int,default=3); args=ap.parse_args()
    targets=json.loads(Path(args.targets).read_text())
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    loaded=[]; errors=[]
    for target in targets:
        sid=int(target["submission_id"])
        data=fetch_json(LIST_URL,post={"submissionId":sid})
        eps=[e for e in (data.get("episodes") or []) if str(e.get("state") or "").upper()=="COMPLETED" and e.get("endTime")]
        eps.sort(key=lambda e:e.get("endTime") or "",reverse=True)
        take=eps[:args.episodes_per_submission]
        for e in take:
            try:
                row=load_episode(e,sid); row.update({"team_id":target.get("team_id"),"team_name":target.get("team_name"),"leaderboard_rank":target.get("rank"),"leaderboard_score":target.get("score")}); loaded.append(row)
            except Exception as exc:
                errors.append({"submission_id":sid,"episode_id":e.get("id"),"error":repr(exc)[:1000]})
        print(json.dumps({"sid":sid,"available":len(eps),"loaded_total":len(loaded),"errors":len(errors)}),flush=True)
    if not loaded: raise RuntimeError("no top episodes loaded")
    tapes=[r["tape"] for r in loaded]; n=len(tapes)
    dist=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            d=hamming(tapes[i],tapes[j]); dist[i][j]=dist[j][i]=d
    mean_d=[sum(row)/(n-1) if n>1 else 0 for row in dist]
    medoid=min(range(n),key=lambda i:(mean_d[i],i))
    modal=[]; agreement=[]; unique_counts=[]
    for t in range(719):
        vals=[canon(x[t]) for x in tapes]
        counts={v:vals.count(v) for v in set(vals)}
        best=max(sorted(counts),key=lambda v:counts[v])
        modal.append(json.loads(best)); agreement.append(counts[best]/n); unique_counts.append(len(counts))
    exact_hashes=[]
    for r in loaded:
        blob=json.dumps(r["tape"],sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
        exact_hashes.append(hashlib.sha256(blob).hexdigest())
    pair_ds=[dist[i][j] for i in range(n) for j in range(i+1,n)]
    summary={
        "schema":"cr087-current-top-lineage-v1","targets":targets,"episodes_loaded":n,"errors":errors,
        "unique_exact_tapes":len(set(exact_hashes)),
        "pairwise_hamming":{"mean":statistics.mean(pair_ds) if pair_ds else 0,"median":statistics.median(pair_ds) if pair_ds else 0,"min":min(pair_ds) if pair_ds else 0,"max":max(pair_ds) if pair_ds else 0},
        "medoid":{"index":medoid,"episode_id":loaded[medoid]["episode_id"],"submission_id":loaded[medoid]["submission_id"],"team_name":loaded[medoid].get("team_name"),"leaderboard_rank":loaded[medoid].get("leaderboard_rank"),"mean_hamming_to_pool":mean_d[medoid]},
        "consensus":{"mean_step_agreement":statistics.mean(agreement),"median_step_agreement":statistics.median(agreement),"steps_unanimous":sum(x==1 for x in agreement),"steps_ge_0_8":sum(x>=0.8 for x in agreement),"steps_ge_0_5":sum(x>=0.5 for x in agreement),"mean_unique_actions_per_step":statistics.mean(unique_counts)},
    }
    Path(out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True))
    Path(out/'modal_tape.json').write_text(json.dumps(modal,separators=(",",":"),sort_keys=True))
    Path(out/'medoid_tape.json').write_text(json.dumps(loaded[medoid]["tape"],separators=(",",":"),sort_keys=True))
    meta=[]
    for i,r in enumerate(loaded):
        meta.append({k:r.get(k) for k in ("episode_id","submission_id","seat","end_time","team_id","team_name","leaderboard_rank","leaderboard_score")} | {"tape_sha256":exact_hashes[i],"mean_hamming_to_pool":mean_d[i]})
    Path(out/'episodes.json').write_text(json.dumps(meta,indent=2,sort_keys=True))
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__': main()
