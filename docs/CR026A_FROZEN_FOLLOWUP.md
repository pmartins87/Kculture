# CR026 screen result and CR026A freeze — 2026-09-05

## Result

Run [33973134213](https://github.com/pmartins87/Kculture/actions/runs/33973134213) finished successfully. All ten route shards completed: 160 direct games plus 80 candidate panel games, with 12 reusable CR024 panel controls and ten source reproductions.

| Route rank | Direct wins-equivalent / 16 | Mean direct margin | Paired score gain | Regressions | Shortlist |
|---|---:|---:|---:|---:|---|
| 5 | 16 | +28865.5625 | +2 | 0 | yes; selected |
| 10 | 16 | +28216.5625 | +2 | 0 | yes; backup |
| 2 | 12 | +1629.0 | +2 | 2 | yes; lower priority |

The original selection order picks rank 5; no thresholds changed after inspection. Results against static tapes are exploratory and do not estimate hosted rating.

## Actual CR024 execution

Official API snapshot at 2026-09-05 14:58 UTC returned 79 completed public episodes: 43 wins and 36 losses. This is the returned API window, not necessarily lifetime history. The deliberately selected 20-game audit contained 12 losses and 8 wins.

- All 20 hosted action streams match frozen CR024 exactly: zero mismatches over 14,380 actions.
- All 20 final reward pairs reproduce exactly in kaggle-environments 1.32.7.
- Zero audit errors.
- These episodes support a strategy weakness rather than an entrypoint/clock/package failure.
- Midgame PASS gap is larger in wins than losses; generic PASS minimization is not supported by this contrast.
- Terminal resource flags are descriptive and include resources of unequal realizable value; do not infer an easy terminal-money fix from counts alone.

Machine-readable results parsed from the final JSON blocks of the official job logs: `experiments/cr026_20260905_result.json`. Raw replays/action tapes are not committed.

## CR026A follow-up, frozen before results

Identity and all scenarios: `configs/cr026a_frozen_gate.json`.

- Candidate is exactly source episode 105565284 seat 1, tape SHA256 `7e90e317f88016a76b73b833c9f5c8aac30f950776b4da12aedb7aa5b3378b5b`.
- No market overlay, dynamic fallback or retuning. Pure recent production route; sparse adaptation remains a later hypothesis.
- Official file-based entrypoint checked in both seats; exhaustive numeric/fallback clock checks; deterministic archive whose main.py is the tested file.
- Reactive opponents: exact frozen packaged Rayk V23, Boatlee V2, Tetsu V2. Four fresh seeds, both seats, paired vs CR024: 24 comparisons / 48 games. This is a regression panel, not a live-field proxy.
- Actual hosted counterfactuals: all 20 fixed audit episodes, original seat/configuration/seed. Reproduce CR024 before replacing it with CR026A. The recorded opponents do not react to the replacement; interpret accordingly.
- Fresh direct replication: four further fresh seeds, both seats, versus CR024.
- Release for hosted calibration only if reactive aggregate score does not decline with <=2 regressions; hosted score improves >=6 points with <=2 regressions and positive mean relative margin; fresh direct score >=6/8 with positive margin; package mechanics pass.
- No automatic Kaggle submission. No held-out accessed. Rank 10 cannot inherit rank 5 validation if rank 5 fails.

## Upstream check

Current GitHub source and spec blobs checked on 2026-09-05 remain identical to `official/UPSTREAM_LOCK.md`:

- engine: `3c202c7ee921da239356789e266b694635103fc4`;
- spec: `b354d06b742fe48402513792253f1a5c29366b20`.

Current competition rules page returned no readable body through public web access, and the current PyPI version query failed. Those checks are not claimed complete; engine/spec parity plus exact hosted reproduction is the verified evidence available for this run.
