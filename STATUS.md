# STATUS — Kculture

Last updated: 2026-08-26

## Mission

**Goal: top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for strategy, code, experiments, Actions evidence, hashes, roadmap and handoff state.

## Gate summary

- **R0 COMPLETE for working purposes** — competition entry user-confirmed.
- **R1 PASS** — exact official starter parity / 720-turn reproduction.
- **R2 PASS** — deterministic laboratory; 16 development / 16 validation / 32 held-out seeds.
- **R3 PASS for delivery/hosted validation** — first exact R4B package is `Complete` with a green Kaggle validation check and joined live evaluation. First observed live score: **161.6**. This is a serious online-calibration signal, not evidence of package failure.
- **R4 ACTIVE** — frozen hosted champion remains R4B market-only while R4D is development-only.
- **R4B market-only VALIDATION PASS** — `R4B-market-only-validated-v1`.
- **R4C ninth-cow NO PROMOTION** — neutral.
- **KEXP-014 COMPLETE** — full 96-game current-meta lifecycle panel; generic weed/lifecycle patch rejected; default 8C/6S route isolated as the strongest structural weakness.
- **KEXP-015 RUNNING** — fixed route counterfactuals default 8C/6S→10C/4S and default 8C/6S→6C/8S on all development seeds against Kaito V27, Rayk V11 and Andrew V12. Actions run `32966913616`.
- **Held-out sealed 32/32.**

## Frozen environment / evaluation facts

- `kaggle-environments==1.32.7`.
- official engine intake commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- 720 recorded turns; step 718 is the final executable action.
- terminal reward is exactly `farm.money`.
- positive-price SELL orders execute after unit actions; leftover inventory itself has no terminal reward.
- ladder rating depends on win/loss/tie, not coin margin.
- valid simulation submissions initialize at rating mean 600 before ongoing matched episodes.
- latest two submissions remain tracked for final evaluation.
- final submission deadline: 2026-09-30 23:59 UTC; games continue approximately to 2026-10-15 before final Bradley-Terry evaluation.

## Seed discipline

- development: 16 seeds — open for iteration.
- validation: 16 seeds — previously opened for exact frozen R4B validation; any changed candidate needs a fresh exact validation gate.
- held-out: 32 seeds — **never opened so far**; reserve for later formal promotion/final selection.

## Current hosted champion

`R4B-market-only-validated-v1`

- path: `candidates/r4b_ablation_market_only.py`
- frozen Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- behavior: preserves every physical COK V8 action; completes terminal market liquidation at step 718.
- validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors.
- package parity run `32919305800`: 4/4 full trajectories identical.
- hosted archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`.
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`.
- Kaggle filename `Kculture_R4B_market_only_validated_v1_submission.tar.gz`.
- Kaggle status **Complete**, green check; first displayed score **161.6**.

The ~2900–3100 figures used in research are mature public benchmark ratings, not the starting rating of a new submission. The 161.6 display therefore means substantial negative hosted rating movement and must remain part of calibration. Do not burn a new submission merely to react to the number.

## R4A base

COK V8:

- upstream commit `779caaec88a441345871e2d62eb5de93606b7b52`;
- local SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`;
- Apache-2.0;
- frozen as `R4A-public-base-v1`.

Full R4B physical-DROP optimizer was rejected because it regressed directly vs R4A.

## Modern public benchmark panel

Frozen exact public outputs used for development screening:

- Kaito V27 V4 — public/best snapshot 3090.1, source SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`, Apache-2.0.
- Rayk V11 — public/best snapshot 2990.4, source SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`, benchmark-only until license independently verified.
- Andrew V12 — public/best snapshot 2915.2, source SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`, Apache-2.0.

Frozen R4B scores on all 16 development seeds × both seats:

| Opponent | W-L-T | Score | Mean delta |
|---|---:|---:|---:|
| Kaito V27 | 25-7-0 | 0.78125 | +4,396.84375 |
| Rayk V11 | 30-2-0 | 0.93750 | +7,477.21875 |
| Andrew V12 | 26-6-0 | 0.81250 | +5,287.43750 |
| **Combined** | **81-15-0** | **0.84375** | **+5,720.5** |

## KEXP-014 — lifecycle full panel: COMPLETE

Actions run `32931921583` — SUCCESS, 96 games, zero errors, development only.

Artifacts:

- Kaito `9593617801`, ZIP SHA-256 `0c74411cc73a4e5c42e60a4d1104ee7206e7eaaf96b95d0635c497f55ef0e61c`;
- Rayk `9593617367`, ZIP SHA-256 `e77fb0b89064b8c25b4e87c219773a68ffedc20e97933b647a91ab454b2202ba`;
- Andrew `9593614809`, ZIP SHA-256 `cc8a00bdcfa999a5c6bf1b142614e687c14b0391260c8c679e1fb82ffd5db814`.

The late-collapse effect exists, but generic crop-expiry/weed cleanup failed its causal-generalization test: losses did not consistently exhibit more weeds and less productive acreage than wins.

A much stronger separator emerged from step-672 production regimes:

| Regime | Games | W-L | Score | Mean terminal delta | Mean 672→terminal swing |
|---|---:|---:|---:|---:|---:|
| 6C/12S | 24 | 22-2 | 0.91667 | +8,174.333 | -2,120.875 |
| 10C/4S | 51 | 45-6 | 0.88235 | +6,301.647 | -1,718.686 |
| **8C/6S** | **19** | **12-7** | **0.63158** | **+1,143.000** | **-3,820.421** |

8C/6S is weak across every modern opponent family:

- Kaito: 5-3, mean +630.625, late swing -4,367.625;
- Rayk: 4-2, mean +2,635.167, late swing -4,250.0;
- Andrew: 3-2, mean +172.2, late swing -2,429.4.

Frozen COK V8 source inspection shows that final 8C/6S is the **default no-Yarn/no-early-milk-support route** after the first three public shop unlocks. COK already has bounded weed replay and passive-weed repair, so generic weed repair is not the next intervention.

See `experiments/KEXP-20260826-014-r4-late-lifecycle-full-panel/README.md`.

## KEXP-015 — R4D default-route counterfactual: RUNNING

Predeclared experiment: `experiments/KEXP-20260826-015-r4d-default-route-counterfactual/README.md`.

Candidates:

- R4D-A: `candidates/r4d_default_to_10c4s.py`, blob `a125e878ef262141cd2fd452a9f4edab42dfbae5`;
- R4D-B: `candidates/r4d_default_to_6c8s.py`, blob `34b66bc18471ffbb7d35f24f2ac39451bc8cb851`.

Both preserve the base opening until at least three shops are visible, change only the fully observed final-default 8C/6S selector, and retain the validated R4B terminal market-only controller.

Actions run: **32966913616**. Six modern-panel jobs (2 candidates × 3 opponents), development only. No validation or held-out access.

Primary baseline to beat: 81-15-0 / score 0.84375 / mean +5,720.5 overall, plus the baseline-defined 8C/6S exposure result 12-7.

## Immediate continuation

1. Finish KEXP-015 and compare both fixed overrides against the exact KEXP-014 baseline, with W/L primary.
2. If one fixed override passes the predeclared gate, freeze it before any fresh validation use.
3. If both fail, build a contextual default-route selector from legal public state instead of universal rerouting.
4. Continue hosted episode diagnosis when Kaggle exposes the submission episode details; reconcile them against the exact packaged agent.
5. Keep the hosted R4B package immutable until a replacement earns promotion.
6. Keep held-out sealed until later formal promotion/final selection.
