# STATUS — Kculture

Last updated: 2026-08-26

## Mission

**Goal: top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for strategy, code, experiments, Actions evidence, hashes, roadmap and handoff state.

## Gate summary

- **R0 COMPLETE for working purposes** — competition entry user-confirmed.
- **R1 PASS** — exact official starter parity / 720-turn reproduction.
- **R2 PASS** — deterministic laboratory; 16 development / 16 validation / 32 held-out seeds.
- **R3 UPLOAD IN PROGRESS (user-reported)** — exact validated R4B archive is being uploaded manually to Kaggle. Do not mark R3 PASS until hosted validation/submission ID/ladder entry are observed.
- **R4 ACTIVE** — COK V8 lineage + Kculture terminal improvement remains current engineering champion.
- **R4B market-only VALIDATION PASS** — frozen as `R4B-market-only-validated-v1`.
- **Package parity PASS** — self-contained hosted archive reproduced frozen wrapper action-for-action.
- **R4C ninth-cow NO PROMOTION** — neutral.
- **KEXP-010 COMPLETE** — older Seyamalam/Kaito V18 panel saturated; R4B 32-0 against each.
- **KEXP-011 COMPLETE** — exact Kaito V27 V4 / public best 3090.1; R4B 25-7.
- **KEXP-012 COMPLETE** — exact Rayk V11 / Andrew V12 current-meta screen; R4B 30-2 and 26-6 respectively.
- **V27 frontier replay diagnostic COMPLETE** — symmetric V27 losses are primarily late-phase collapses after step ~672, not opening failures or only terminal-liquidation failures.
- **KEXP-013 RUNNING** — exact Rayk/Andrew hard-regime replay capture, development only.
- **Held-out sealed 32/32.**

## Frozen environment / evaluation facts

- `kaggle-environments==1.32.7`.
- official engine intake commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- 720 recorded turns; step 718 is the final executable action.
- terminal reward is exactly `farm.money`.
- positive-price SELL orders execute after unit actions; leftover inventory itself has no terminal reward.
- ladder rating depends on win/loss/tie, not coin margin.
- latest two submissions remain tracked for final evaluation.
- final submission deadline: 2026-09-30 23:59 UTC; games continue approximately to 2026-10-15.

## Seed discipline

- development: 16 seeds — open for iteration.
- validation: 16 seeds — opened once for exact frozen R4B validation; do not reuse that claim for changed code.
- held-out: 32 seeds — **never opened so far**; reserve for later formal promotion/final selection.

## Current champion / hosted package

`R4B-market-only-validated-v1`

- candidate path: `candidates/r4b_ablation_market_only.py`
- frozen Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- behavior: preserves every physical COK V8 action; on final step makes terminal market liquidation complete.
- validation run: `32918640409`.
- validation vs Seyamalam: **32-0**, mean `+18,885.875`.
- validation direct vs R4A: **8-6-18**, score `0.53125`, mean `+165.03125`, zero errors.

Hosted package parity run `32919305800`:

- archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`
- archive size: `101557` bytes
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`
- 4/4 full trajectories exactly identical to frozen wrapper.

**R3 state:** user reports this exact package upload has begun in Kaggle UI. Await hosted validation/result before recording submission ID/rating.

## R4A base

COK V8:

- upstream commit `779caaec88a441345871e2d62eb5de93606b7b52`
- local SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`
- Apache-2.0
- frozen as `R4A-public-base-v1`.

Full R4B physical-DROP optimizer was **REJECTED** because direct development result vs R4A was 5-11 despite improving Seyamalam.

## KEXP-010 — full development failure atlas: COMPLETE

Run `32920250892`, 160 development games, zero errors:

| Matchup | W-L-T | Score | Mean delta |
|---|---:|---:|---:|
| R4B vs R4A | 15-9-8 | 0.59375 | +20.000 |
| R4B vs Seyamalam V21 | **32-0** | 1.000 | +20,004.0625 |
| R4B vs Kaito V18 | **32-0** | 1.000 | +19,739.000 |
| R4A vs Seyamalam | 30-2 | 0.9375 | +18,704.875 |
| R4A vs Kaito V18 | 30-2 | 0.9375 | +18,439.96875 |

Paired-seat comparison R4B vs R4A is non-negative on all 16 development seeds; 11 exactly zero, five positive, total +640. Older external panel is saturated.

## KEXP-011 — exact Kaito V27 frontier screen: COMPLETE

Exact public notebook:

- `kaitofukami/25-27-strict-future-v27-midgame-meta-reset/versions/4`
- public/best score snapshot: **3090.1 V4**
- Apache-2.0
- exact `main.py`: 20,813 bytes
- SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`
- acquisition run `32920859121`.

Strong screen run `32921007864`, 16 development seeds × both seats:

| Candidate | W-L-T | Score | Mean delta | Errors |
|---|---:|---:|---:|---:|
| R4A / COK V8 | **25-7** | 0.78125 | +4,382.03125 | 0 |
| R4B market-only | **25-7** | 0.78125 | +4,396.84375 | 0 |

R4B losses: `150614441` one seat; `1743398262`, `163219477`, `598340816` both seats. Decision: no migration to V27.

## KEXP-012 — exact Rayk/Andrew current-meta screen: COMPLETE

Discovery run `32926623429` acquired exact public outputs with Kaggle credentials blank.

### Rayk V11

- `raykkretzschmar/kaggriculture-rank-your-agent/versions/11`
- public best score associated with V11: **2990.4**
- `main.py`: 36,233 bytes
- SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`
- benchmark-only until license independently verified.

### Andrew V12

- `andrewsokolovsky/kaggriculture-breaking-the-tie/versions/12`
- public best score associated with V12: **2915.2**
- `main.py`: 26,585 bytes
- SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`
- Apache-2.0.

Strong screen run `32926727240`, all 16 development seeds × both seats, zero errors:

| Candidate | Opponent | W-L-T | Score | Mean delta |
|---|---|---:|---:|---:|
| R4A | Rayk V11 | **30-2** | 0.9375 | +7,462.00000 |
| R4B | Rayk V11 | **30-2** | 0.9375 | +7,477.21875 |
| R4A | Andrew V12 | **26-6** | 0.8125 | +5,287.43750 |
| R4B | Andrew V12 | **26-6** | 0.8125 | +5,287.43750 |

Combined R4B across exact V27 + Rayk V11 + Andrew V12: **81-15-0 across 96 development games**, zero errors. This combined count is descriptive because all use the same seed panel.

Hard regimes:

- Rayk: only `163219477`, both seats (-1188/-1188); same seed also loses both seats to V27.
- Andrew: `150614441` one seat; `393297156` both; `598340816` one seat; `1422177419` both.

Different current families expose different regimes. `163219477` is the strongest multi-family recurrence, but no seed-specific patch is allowed.

## V27 frontier replay diagnostic: COMPLETE

Replay run `32926648674`; full both-seat replays captured for V27 hard seeds.

Key result for symmetric loss seeds `1743398262`, `163219477`, `598340816`: R4B is still ahead at step 672 by +249, +990 and +3679 respectively, then loses. From step 672 to terminal, V27 gains roughly **2.7k–4.5k more** per orientation.

Across seven V27 loss games, mean R4B-minus-V27 money trajectory:

- step 360: +4692.4
- step 480: +6550.6
- step 600: +2807.1
- step 672: +1245.3
- step 718: -2475.7
- terminal: -2728.1

Working hypothesis: repeated weakness is in **late-phase continuation control** — coupled production mix, labor, harvest/drop throughput and sale timing — before the step-718 terminal market controller can recover the value. See `research/V27_FRONTIER_REPLAY_DIAGNOSTIC_20260826.md`.

## KEXP-013 — current-meta hard replays: RUNNING

Actions run `32927303182`.

Predeclared 10 complete development replays:

- Rayk V11: `163219477`, both orientations;
- Andrew V12: `150614441`, `393297156`, `598340816`, `1422177419`, both orientations.

Purpose: test whether the late-collapse mechanism repeats across current families before defining R4D. Exact notebook version and SHA are fail-closed in every job.

## Immediate continuation

1. Observe the user's first hosted upload result. If validation succeeds, record submission ID, hosted status/rating/episodes in `docs/SUBMISSION_LEDGER.md` and mark R3 appropriately.
2. Finish/analyze KEXP-013 (`32927303182`) against the predeclared replay questions.
3. Define R4D only if multi-family replay evidence supports one observable, auditable late-phase/continuation mechanism; never key to seed or opponent identity.
4. Keep R4B hosted candidate frozen while R4D exploration remains development-only.
5. Do **not** open held-out until a later formal promotion/final-selection gate.
