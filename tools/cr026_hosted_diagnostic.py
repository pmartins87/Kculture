"""Bounded official-API CR024 forensics, with trace and engine reproduction.

Download public completed episodes only. Never print authentication values.
Keep raw competition replays transient, output aggregate facts and provenance.
"""
from __future__ import annotations
import collections
import copy
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi
from collect_top_ladder_snapshot import public_episodes, download, as_dict
from fetch_authenticated_hosted_forensics import outcome
from cr026_live_meta_cr024_benchmark import (build_cr024, actions_for, final_rewards,
    run_pair, tape_agent, exact_rewards)
from hosted_replay_loss_analyzer import analyze_replay, aggregate

SID = 56025052


def main():
    api = KaggleApi(); api.authenticate()
    episodes = public_episodes(api, SID, 200)
    outcomes = collections.Counter(outcome(e, SID)[0] for e in episodes)
    # Balanced, bounded descriptive sample; all available metadata is retained.
    losses = [e for e in episodes if outcome(e, SID)[0] == 'LOSS'][:12]
    wins = [e for e in episodes if outcome(e, SID)[0] == 'WIN'][:8]
    other = [e for e in episodes if outcome(e, SID)[0] not in ('WIN','LOSS')][:4]
    selected = losses + wins + other
    rows=[]; checks=[]; errors=[]; metadata=[]
    for e in episodes:
        result, seat = outcome(e, SID)
        metadata.append(dict(episode_id=e['id'], result=result, seat=seat, agents=e.get('agents'),
                             end_time=e.get('endTime')))
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td); control, provenance=build_cr024(tmp/'control')
        for e in selected:
            eid=int(e['id']); _,seat=outcome(e,SID)
            try:
                if seat not in (0,1): raise ValueError('submission seat unavailable')
                path=download(api,eid,tmp/'replays')
                rep=json.loads(path.read_text())
                tapes=[actions_for(rep,p) for p in (0,1)]
                mismatch=[t for t,(a,b) in enumerate(zip(tapes[seat],control)) if a!=b]
                seed=int(rep['info']['seed'])
                replay=run_pair(seed,[tape_agent(t) for t in tapes],rep.get('configuration'))
                exact=(replay['steps']==720 and replay['statuses']==['DONE','DONE'] and exact_rewards(final_rewards(rep),replay['rewards']))
                checks.append(dict(episode_id=eid,seat=seat,trace_steps=len(tapes[seat]),
                    action_mismatches=len(mismatch),first_mismatches=mismatch[:10],
                    exact_terminal_reproduction=exact,original_rewards=final_rewards(rep),local_rewards=replay['rewards']))
                # Kaggle shared public observation fields may be omitted from seat 1.
                # Carry only public keys across seats; private inventories stay seat-specific.
                for frame in rep['steps']:
                    shared=frame[0].get('observation') or {}
                    for p in (0,1):
                        obs=frame[p].setdefault('observation',{})
                        for key in ('farms','market','day','hour','step','town'):
                            if key not in obs and key in shared: obs[key]=copy.deepcopy(shared[key])
                rows.append(analyze_replay(rep,seat,str(eid)))
                path.unlink()
            except Exception as exc:
                errors.append(dict(episode_id=eid,error=type(exc).__name__,detail=str(exc)[:300]))
    result=dict(submission_id=SID,captured_at=datetime.now(timezone.utc).isoformat(),
        available_public_episodes=len(episodes),metadata_outcomes=dict(outcomes),metadata=metadata,
        sample_policy='latest up to 12 losses, 8 wins, 4 ties/unknown; not an unbiased win-rate sample',
        selected=len(selected),analyzed=len(rows),errors=errors,control_provenance=provenance,
        execution_checks=checks,aggregate=aggregate(rows),games=rows,held_out_touched=False)
    out=Path('artifacts/cr026_hosted/report.json');out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in result.items() if k not in ('metadata','games')},indent=2))
    if not rows or errors: raise SystemExit(3)


if __name__=='__main__':main()
