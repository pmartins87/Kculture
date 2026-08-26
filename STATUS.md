# STATUS — Kculture

Last updated: 2026-08-26

## Mission

**Goal: top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for strategy, code, experiments, Actions evidence, hashes, roadmap and handoff state.

## Gate summary

- **R0 COMPLETE for working purposes** — competition entry user-confirmed.
- **R1 PASS** — exact official starter parity / 720-turn reproduction.
- **R2 PASS** — deterministic laboratory; 16 development / 16 validation / 32 held-out seeds.
- **R3 PASS for delivery/hosted validation** — first exact R4B package is `Complete` with a green Kaggle validation check and has joined live evaluation. First observed score: **161.6** at ~2026-08-26 04:37 UTC. This is a material online-calibration contradiction because valid simulation submissions initialize at rating 600.
- **R4 ACTIVE** — COK V8 lineage + Kculture terminal improvement remains current frozen hosted champion while R4D is development-only.
- **R4B market-only VALIDATION PASS** — frozen as `R4B-market-only-validated-v1`.
- **Package parity PASS** — self-contained hosted archive reproduced frozen wrapper action-for-action.
- **R4C ninth-cow NO PROMOTION** — neutral.
- **KEXP-010 COMPLETE** — older Seyamalam/Kaito V18 panel saturated; R4B 32-0 against each.
- **KEXP-011 COMPLETE** — exact Kaito V27 V4 / public best 3090.1; R4B 25-7.
- **KEXP-012 COMPLETE** — exact Rayk V11 / Andrew V12 current-meta screen; R4B 30-2 and 26-6 respectively.
- **V27 frontier replay diagnostic COMPLETE** — symmetric V27 losses are primarily late-phase collapses after step ~672.
- **KEXP-013 COMPLETE** — exact Rayk/Andrew hard-regime replays confirm the same late collapse in 8/8 captured losses.
- **R4D crop-lifecycle lead ACTIVE** — expiring strawberries → weeds → final-day productive-acreage/throughput collapse is now a mechanistic lead requiring full-panel win/loss testing before code mutation.
- **Held-out sealed 32/32.**

## Frozen environment / evaluation facts

- `kaggle-environments==1.32.7`.
- official engine intake commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- 720 recorded turns; step 718 is the final executable action.
- terminal reward is exactly `farm.money`.
- positive-price SELL orders execute after unit actions; leftover inventory itself has no terminal reward.
- ladder rating depends on win/loss/tie, not coin margin.
- valid simulation submissions initialize at rating mean **600** before ongoing matched episodes.
- latest two submissions remain tracked for final evaluation.
- final submission deadline: 2026-09-30 23:59 UTC; games continue approximately to 2026-10-15 before the final Bradley-Terry evaluation.

## Seed discipline

- development: 16 seeds — open for iteration.
- validation: 16 seeds — opened once for exact frozen R4B validation; do not reuse that claim for changed code.
- held-out: 32 seeds — **never opened so far**; reserve for later formal promotion/final selection.

## Current champion / first hosted submission

`R4B-market-only-validated-v1`

- candidate path: `candidates/r4b_ablation_market_only.py`
- frozen Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- behavior: preserves every physical COK V8 action; on final step makes terminal market liquidation complete.
- validation run: `32918640409`.
- validation vs Seyamalam: **32-0**, mean `+18,885.875`.
- validation direct vs R4A: **8-6-18**, score `0.53125`, mean `+165.03125`, zero errors.

Hosted package parity run `32919305800`:

- package-build Git SHA `29a883aba3df6347d72e321c9970c9694e0b6fa0`;
- archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`
- archive size: `101557` bytes
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`
- 4/4 full trajectories exactly identical to frozen wrapper.

Hosted evidence from Kaggle UI:

- filename `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- description `Kculture R4B market-only validated v1`;
- status **Complete** / green check;
- first displayed score **161.6**;
- screenshot observation ~2026-08-26 04:37 UTC;
- submission ID and hosted episode count not yet observed.

**Interpretation:** the ~2900–3100 values used in local current-meta research are mature public-agent rating snapshots, not a new submission's starting score. Kaggle initializes valid simulation submissions at 600. Therefore 161.6 is an actual downward live-rating movement and is treated as a serious calibration signal. Do not assume automatic recovery to ~3000. See `research/FIRST_HOSTED_SCORE_DIAGNOSTIC_20260826.md` and `docs/SUBMISSION_LEDGER.md`.

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

Working region: **late-phase continuation control** — coupled production mix, labor, crop lifecycle, harvest/drop throughput and sale timing — before the step-718 terminal market controller can recover the value.

## KEXP-013 — current-meta hard replays: COMPLETE

Actions run `32927303182` — SUCCESS; exact Rayk/Andrew hard-regime capture, development only, zero runtime errors.

Captured:

- Rayk V11: `163219477`, both orientations;
- Andrew V12: `150614441`, `393297156`, `598340816`, `1422177419`, both orientations;
- total 10 replays: 8 R4B losses, 2 wins.

Across all **8 captured losses**:

- R4B is ahead at step 672 in every game;
- mean step-672 lead: **+2007.5**;
- mean terminal result: **-1782.75**;
- mean 672→terminal swing: **-3790.25**.

Day-29 (steps 696–718) descriptive averages in those losses:

| Metric | R4B | Opponent |
|---|---:|---:|
| hands around mid-final-day | 8.0 | 9.75 |
| HARVEST actions | 18.5 | 29.75 |
| DROP actions | 8.0 | 13.75 |
| requested SELL units | 139.5 | 222.75 |
| PASS actions (farmer+hands) | 70.25 | 14.0 |

Artifacts:

- Rayk `9591994623`, ZIP SHA-256 `f78a3f400b698749ce60d1664bce3315c702e10bedd3f91690400474834d343a`;
- Andrew `9592011224`, ZIP SHA-256 `343e2dce16452dc0cb2e57b2da933253b5402a44e1a656624b0ed03127feb103`.

## R4D mechanistic lead — crop lifecycle / final acreage

A deeper inspection of the KEXP-013 replay states found a more specific candidate mechanism in the eight losses:

At step 672, R4B averages:

- **13.0 STRAWBERRY tiles with `max_lifespan_step=672`**;
- **6.5 additional STRAWBERRY tiles expiring at 696**;
- opponent averages only 5.0 strawberries expiring at 672 and none in the same 696 bucket.

At step 696:

- R4B averages **13.5 WEED tiles** vs opponent **4.625**;
- R4B productive crop tiles average about **16.25** (6.5 strawberry + 9.75 wheat) vs opponent **25.25 wheat**.

The numerical correspondence between ~13 expiring strawberries at 672 and ~13.5 weeds at 696 is a strong engine-plausible clue for the late collapse: old high-value crop acreage ages out, becomes unproductive, and the fixed route does not recover it fast enough before the horizon ends. This can directly reduce harvest/drop/sale throughput.

**This remains a lead, not a causal proof.** It was discovered in a loss-focused replay set. Before changing strategy, test the lifecycle signature across all 16 development seeds, both seats, independent current-meta opponents, including wins. No seed- or opponent-ID logic is permitted.

## Immediate continuation

1. **Hosted diagnosis:** capture submission ID and hosted episode list when available; reconstruct W/L/T and rating trajectory behind the 161.6 score and compare hosted replays with exact package behavior.
2. **KEXP-014:** run a full-development late-lifecycle checkpoint panel to test whether step-672 expiring-crop load and step-696 weed/productive-acreage state predict late relative collapse across wins and losses.
3. If KEXP-014 confirms the signal, implement the narrowest state-observable **R4D crop-lifecycle recovery** candidate first; preserve opening/midgame and frozen terminal market completeness.
4. Ablate labor/harvest/DROP throughput separately after the crop-lifecycle experiment; do not bundle mechanisms prematurely.
5. Keep R4B hosted candidate immutable while R4D remains development-only.
6. Do **not** open held-out until a later formal promotion/final-selection gate.
