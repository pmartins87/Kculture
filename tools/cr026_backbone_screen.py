"""Exploratory current-route screen. No hosted promotion or rating estimate.

Public replay actions remain in CI artifacts, never in the public repository.
Names select research comparison groups only, never runtime decisions.
"""
from __future__ import annotations
import argparse
import copy
import json
import statistics
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECT_SEEDS = [926050101, 926050103, 926050107, 926050109,
                926050113, 926050117, 926050119, 926050123]
PANEL_SEEDS = [926050201, 926050203]


def write(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True))


def checked_play(candidate, opponent, seed, seat):
    from cr026_live_meta_cr024_benchmark import run_pair, tape_agent
    agents = [tape_agent(candidate), tape_agent(opponent)]
    if seat: agents.reverse()
    result = run_pair(seed, agents, None)
    if result['steps'] != 720 or result['statuses'] != ['DONE', 'DONE'] or None in result['rewards']:
        raise RuntimeError(f'invalid game {result}')
    delta = result['rewards'][seat] - result['rewards'][1-seat]
    return dict(seed=seed, seat=seat, delta=delta,
                score=1.0 if delta > 0 else 0.0 if delta < 0 else 0.5,
                rewards=result['rewards'])


def prepare(out):
    from cr026_live_meta_cr024_benchmark import (build_cr024, download, read_csv,
        actions_for, final_rewards, winner_index, run_pair, tape_agent, exact_rewards, tape_sha)
    handle = 'kaggle/kaggriculture-episodes-2026-09-04'
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        control, provenance = build_cr024(tmp/'control')
        manifest = sorted(read_csv(download(handle, 'manifest.csv', tmp/'day')),
                          key=lambda r: -float(r['avg_score']))[:10]
        if len(manifest) != 10: raise RuntimeError('need exactly ten source episodes')
        sources = []
        for rank, row in enumerate(manifest, 1):
            eid = str(row['episode_id'])
            rep = json.loads(download(handle, eid+'.json', tmp/eid).read_text())
            seed = int(rep['info']['seed'])
            tapes = [actions_for(rep, p) for p in (0,1)]
            original = final_rewards(rep); wi = winner_index(original)
            replay = run_pair(seed, [tape_agent(t) for t in tapes], rep.get('configuration'))
            if (wi is None or replay['steps'] != 720 or replay['statuses'] != ['DONE','DONE']
                    or not exact_rewards(original, replay['rewards'])):
                raise RuntimeError(f'cannot reproduce source rank {rank}')
            sources.append(dict(rank=rank, episode_id=eid, source_seat=wi,
                source_seed=seed, team=rep['info']['TeamNames'][wi],
                tape=tapes[wi], tape_sha256=tape_sha(tapes[wi]), original_rewards=original))
        panel = []
        for source in sources:
            if source['team'] not in [s['team'] for s in panel]: panel.append(source)
        if len(panel) < 3: raise RuntimeError('need three source families')
        baseline = []
        for opponent in panel:
            for seed in PANEL_SEEDS:
                for seat in (0,1):
                    baseline.append(dict(opponent_rank=opponent['rank'], **checked_play(control, opponent['tape'], seed, seat)))
        write(out, dict(control=control, control_provenance=provenance, sources=sources,
            panel_ranks=[s['rank'] for s in panel], baseline=baseline,
            direct_seeds=DIRECT_SEEDS, panel_seeds=PANEL_SEEDS, held_out_touched=False))
        print(json.dumps(dict(source_count=len(sources), panel_teams=[s['team'] for s in panel],
                              baseline_games=len(baseline))), flush=True)


def shard(bundle, rank, out):
    data = json.loads(Path(bundle).read_text())
    candidate = next(s for s in data['sources'] if s['rank'] == rank)
    direct = []; paired = []
    for seed in DIRECT_SEEDS:
        for seat in (0,1):
            direct.append(checked_play(candidate['tape'], data['control'], seed, seat))
    # Exclude the candidate's entire source family to avoid counting self-match evidence.
    opponents = [s for s in data['sources'] if s['rank'] in data['panel_ranks'] and s['team'] != candidate['team']]
    for opponent in opponents:
        for seed in PANEL_SEEDS:
            for seat in (0,1):
                result = checked_play(candidate['tape'], opponent['tape'], seed, seat)
                control = next(r for r in data['baseline'] if (r['opponent_rank'],r['seed'],r['seat']) == (opponent['rank'],seed,seat))
                paired.append(dict(opponent_rank=opponent['rank'], opponent_family=opponent['team'],
                                   candidate=result, control=control))
    gain = sum(r['candidate']['score'] - r['control']['score'] for r in paired)
    regressions = sum(r['candidate']['score'] < r['control']['score'] for r in paired)
    direct_score = sum(r['score'] for r in direct)
    mean = statistics.mean(r['delta'] for r in direct)
    # Shortlisting only: small development sample, static opposition, multiple comparisons.
    shortlist = direct_score >= 10 and mean > 0 and gain >= 1 and regressions <= 2
    report = dict(rank=rank, source={k:v for k,v in candidate.items() if k != 'tape'},
                  direct=direct, paired=paired, direct_score=direct_score, direct_mean_delta=mean,
                  paired_gain=gain, paired_regressions=regressions, shortlist=shortlist,
                  held_out_touched=False, hosted_authorized=False)
    write(out, report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('direct','paired')}, indent=2), flush=True)


def aggregate(folder, out):
    rows = [json.loads(p.read_text()) for p in Path(folder).glob('rank_*.json')]
    if sorted(r['rank'] for r in rows) != list(range(1,11)):
        raise RuntimeError('incomplete/duplicate rank results; cannot select')
    for r in rows:
        if len(r['direct']) != 16 or len(r['paired']) < 8:
            raise RuntimeError('incomplete candidate')
    ranked = sorted(rows, key=lambda r: (r['shortlist'], r['paired_gain'], r['direct_score'], r['direct_mean_delta']), reverse=True)
    result = dict(decision='SHORTLIST_FOR_FRESH_REACTIVE_TESTS' if any(r['shortlist'] for r in ranked) else 'NO_BACKBONE_SHORTLIST__USE_HOSTED_FAILURE_MECHANISMS',
                  ranking=[{k:v for k,v in r.items() if k not in ('direct','paired')} for r in ranked],
                  held_out_touched=False, hosted_authorized=False,
                  limitation='Exploratory fixed tapes; no estimate of live rating; source families are research metadata only.')
    write(out, result); print(json.dumps(result, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['prepare','shard','aggregate'])
    ap.add_argument('--bundle'); ap.add_argument('--rank', type=int); ap.add_argument('--folder'); ap.add_argument('--output', required=True)
    a = ap.parse_args()
    if a.mode == 'prepare': prepare(a.output)
    elif a.mode == 'shard': shard(a.bundle, a.rank, a.output)
    else: aggregate(a.folder, a.output)
