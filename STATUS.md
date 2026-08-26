# STATUS — Kculture

Last updated: 2026-08-26

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for strategy, code, experiments, Actions evidence, hashes, roadmap and handoff state.

## Prize-first decision rule

- User suggestions, assistant suggestions and public strategies are **hypotheses, not directives**.
- Prefer expected prize value over elegance, novelty or architectural purity.
- Cheap falsification before expensive implementation.
- W/L/T generalization and hosted relevance outrank money-margin improvements.
- Kill/deprioritize avenues whose measured ceiling is small.
- Local public benchmarks are models of the competition; the hosted ladder is real evidence and contradictions must be investigated.
- Do not pivot architecture because an idea was merely mentioned in conversation.

See `docs/PRIZE_FIRST_DECISION_POLICY.md`.

## Gate summary

- **R0 COMPLETE** — competition entry user-confirmed.
- **R1 PASS** — exact official starter parity / 720-turn reproduction.
- **R2 PASS** — deterministic laboratory; 16 development / 16 validation / 32 held-out seeds.
- **R3 PASS for delivery/hosted validation** — exact R4B package is `Complete` with green Kaggle check and live evaluation.
- **R4 ACTIVE** — hosted champion remains frozen R4B market-only while development searches for a materially better replacement.
- **R4B market-only VALIDATION PASS** — `R4B-market-only-validated-v1`.
- **R4C ninth-cow NO PROMOTION** — neutral.
- **KEXP-014 COMPLETE** — late-collapse mechanism exists; generic weed/lifecycle patch rejected. The weak 8C/6S label there is an *observed step-672 physical state*, not automatically COK's internal route label.
- **KEXP-015 COMPLETE / NO PROMOTION** — fixed default→10C/4S kept 81-15 but only improved money; fixed default→6C/8S regressed to 78-18.
- **KEXP-016 COMPLETE** — corrected public-context diagnostic, run `32968422225`, all three jobs PASS.
- **KEXP-017 COMPLETE / SOLVER BRANCH DEPRIORITIZED** — perfect ex-post selection among three existing macro branches improves only 81-15 → **83-13**; cannot fix any Kaito or Andrew losses.
- **Held-out sealed 32/32.**

## Hosted reality checkpoint

Current submission: `R4B-market-only-validated-v1`.

Observed Kaggle score sequence:

- **161.6** first snapshot;
- **135.7** later 2026-08-26 snapshot;
- status remains **Complete** / green check.

This continuing decline is a **high-priority hosted/local calibration contradiction**, not evidence of package failure. Local modern public panel is 81-15, so the current local opponent/state distribution is clearly not sufficient to predict hosted performance.

Do not assume automatic recovery. Do not spend submission #2 on a weak reaction. Highest-value missing evidence remains hosted Episodes/replays: submission ID, episode count, opponent distribution, W/L/T and execution anomalies.

## Frozen environment / evaluation facts

- `kaggle-environments==1.32.7`.
- official engine intake commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- 720 recorded turns; step 718 is final executable action.
- terminal reward is exactly `farm.money`.
- positive-price SELL orders execute after unit actions; leftover inventory itself has no terminal reward.
- ladder rating depends on win/loss/tie, not coin margin.
- valid simulation submissions initialize around rating mean 600 before ongoing matched episodes.
- latest two submissions remain tracked for final evaluation.
- final submission deadline: 2026-09-30 23:59 UTC; games continue approximately to 2026-10-15 before final Bradley-Terry evaluation.

## Seed discipline

- development: 16 frozen seeds — open for iteration.
- validation: 16 frozen seeds — R4B validation already opened; changed code needs a fresh exact validation gate.
- held-out: 32 frozen seeds — **never opened**; reserve for later promotion/final selection.
- New exploratory development seeds may be generated as a separate, documented pool; they must never be confused with frozen validation/held-out.

## Current hosted champion provenance

`R4B-market-only-validated-v1`

- candidate: `candidates/r4b_ablation_market_only.py`;
- frozen Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors;
- package parity run `32919305800`: 4/4 full trajectories identical;
- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- Kaggle filename `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- Kaggle status `Complete`; latest observed score **135.7**.

## R4A base

COK V8:

- upstream commit `779caaec88a441345871e2d62eb5de93606b7b52`;
- SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`;
- Apache-2.0;
- frozen as `R4A-public-base-v1`.

Full R4B physical-DROP optimizer was rejected because it regressed directly vs R4A.

## Modern public benchmark panel

Exact frozen public outputs:

- Kaito V27 V4 — score snapshot 3090.1, SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`, Apache-2.0.
- Rayk V11 — score snapshot 2990.4, SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`, benchmark-only until license independently verified.
- Andrew V12 — score snapshot 2915.2, SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`, Apache-2.0.

Frozen R4B on all 16 development seeds × both seats:

| Opponent | W-L-T | Score | Mean delta |
|---|---:|---:|---:|
| Kaito V27 | 25-7-0 | 0.78125 | +4,396.84375 |
| Rayk V11 | 30-2-0 | 0.93750 | +7,477.21875 |
| Andrew V12 | 26-6-0 | 0.81250 | +5,287.43750 |
| **Combined** | **81-15-0** | **0.84375** | **+5,720.5** |

These are useful controlled benchmarks, but the hosted 135.7 proves they cannot be treated as a calibrated proxy for the live field.

## KEXP-014 — late lifecycle panel

Actions run `32931921583`, 96 games, zero errors, development only.

Repeated hard-loss mechanism: several games are still ahead around step 672 and reverse during the final ~47 turns. Generic weed/expiry cleanup did not generalize.

Observed step-672 physical-state split:

| Observed state | Games | W-L | Score | Mean terminal delta | Mean 672→terminal swing |
|---|---:|---:|---:|---:|---:|
| 6C/12S | 24 | 22-2 | 0.91667 | +8,174.333 | -2,120.875 |
| 10C/4S | 51 | 45-6 | 0.88235 | +6,301.647 | -1,718.686 |
| **8C/6S** | **19** | **12-7** | **0.63158** | **+1,143.000** | **-3,820.421** |

Important correction: this classification is **physical state at step 672**, not proof of the COK hidden route label that produced it.

## KEXP-015 — fixed route counterfactual: COMPLETE / NO PROMOTION

Actions run `32966913616`.

- R4B baseline: **81-15**, mean +5,720.5.
- default→10C/4S: **81-15**, mean +5,908.542.
- default→6C/8S: **78-18**, mean +5,700.260.

10C/4S raises money but not W/L overall; 6C/8S regresses. On seed `163219477`, 10C/4S fixes both Rayk losses but creates two Andrew losses. Universal reroute is rejected.

## KEXP-016 — public context: COMPLETE

Corrected run `32968422225`, all three jobs SUCCESS; development only.

Artifacts:

- Kaito `9606674181`, digest `928e1377e4b219e89ba498c22da46ad1cff75bd7a1d57017d6c2e2a86ea7f5f5`;
- Rayk `9606672044`, digest `436c092faeaab12d36391bed39e61f02e35f892b0a52bf541c3b8b17b07a277c`;
- Andrew `9606666107`, digest `d455a05223fc9c2a2adf50eb8086634f02da0deb15a14ea1e4ae5a1698b9f587`.

The diagnostic corrected the earlier route/state conflation. Public third-shop snapshots show opponent-family differences (including money divergence), but the corpus is too small and too opponent-correlated to justify a hardcoded selector. No policy promotion.

## KEXP-017 — three-branch macro oracle: COMPLETE / DEPRIORITIZED

Actions run `32972566807`, 288 complete development games.

| Opponent | Baseline | Perfect ex-post choice among baseline/10C4S/6C8S |
|---|---:|---:|
| Kaito V27 | 25-7 | **25-7** |
| Rayk V11 | 30-2 | **32-0** |
| Andrew V12 | 26-6 | **26-6** |
| **Combined** | **81-15** | **83-13** |

Perfect knowledge among the three existing macro routes gains only **2 wins out of 96**, all against Rayk. It cannot fix any Kaito or Andrew loss. Therefore a solver/selector over the current route set is **not a priority architecture**. New strategic actions and better hosted calibration have higher expected value.

See `experiments/KEXP-20260826-017-r4d-macro-oracle/README.md`.

## Immediate continuation — prize-first

1. **Hosted/local mismatch first:** obtain and analyze hosted Episodes/replays as soon as exposed by Kaggle; determine opponent distribution, W/L, execution anomalies and whether public benchmarks are unrepresentative.
2. **Broaden development distribution:** add new documented exploratory seeds and more current/diverse opponent families; stop repeatedly optimizing only the original 16×3 panel.
3. **Attack mechanisms no route selector can fix:** especially Kaito/Andrew late reversals; compare action throughput, labor, production, drop/shed flow, sales timing and stop-investment horizon.
4. **Search new action families:** cheap counterfactuals / parameter search / evolutionary or model-based search are allowed when bounded and empirically justified. Method name does not matter.
5. Freeze only candidates with cross-family W/L improvement; then run a fresh validation gate.
6. Do not submit a second agent until it materially earns promotion.
7. Keep all 32 held-out seeds sealed.
