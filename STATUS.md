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
- Local public benchmarks are models of the competition; hosted/live-ladder evidence is calibration truth when they conflict.
- Never pivot architecture merely because a technique was mentioned.

See `docs/PRIZE_FIRST_DECISION_POLICY.md`.

## Gate summary

- **R0 COMPLETE** — competition entry confirmed.
- **R1 PASS** — exact official starter/environment reproduction.
- **R2 PASS** — deterministic laboratory; 16 development / 16 validation / 32 held-out seeds.
- **R3 DELIVERY PASS / HOSTED CALIBRATION FAILING** — first exact R4B package is `Complete` with green Kaggle check, but visible rating fell **161.6 → 135.7**.
- **R4 ACTIVE** — hosted champion remains frozen R4B while R4D searches for a materially better replacement.
- **R4B VALIDATION PASS** — `R4B-market-only-validated-v1`.
- **R4C NO PROMOTION** — guarded ninth cow neutral.
- **KEXP-015 NO PROMOTION** — fixed route overrides fail to improve W/L.
- **KEXP-017 COMPLETE / SOLVER ROUTE BRANCH DEPRIORITIZED** — perfect ex-post choice among current three macro branches improves only 81-15 → **83-13**.
- **KEXP-018 COMPLETE** — official live-meta radar established; fixed public notebooks are no longer the only meta source.
- **KEXP-021 COMPLETE** — same-day live-meta demand response found strong late CARROT signal but a two-team confound.
- **KEXP-022 COMPLETE** — four-day longitudinal replication confirms strong agents systematically react to full late CARROT demand; unconditional CARROT rule rejected.
- **R4D late demand-response candidate is the current highest-priority controlled implementation.**
- **Held-out sealed 32/32.**

## Current hosted champion

`R4B-market-only-validated-v1`

- candidate `candidates/r4b_ablation_market_only.py`;
- frozen Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors;
- package parity run `32919305800`: 4/4 full trajectories identical;
- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- Kaggle filename `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- Kaggle status `Complete`, green check;
- observed live score **161.6 → 135.7**.

The declining hosted rating is a serious local/online contradiction, not evidence of packaging failure. Do not assume automatic recovery and do not spend submission #2 on a weak reaction.

## Frozen environment / evaluation facts

- `kaggle-environments==1.32.7`.
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- 720 recorded states; step 718 is the final executable action.
- terminal reward is exactly `farm.money`.
- positive-price SELL executes after unit actions; leftover inventory has no terminal reward.
- ladder rating depends on W/L/T, not coin margin.
- latest two submissions remain tracked for final evaluation.
- final submission deadline: 2026-09-30 23:59 UTC; games continue approximately to 2026-10-15 before final Bradley-Terry evaluation.

Current rebalance is already included in the frozen engine:

- shop draws with replacement, up to eight instances;
- CARROT/TOMATO/EGG use scarcity-sensitive `hinge` price curves;
- CARROT first yield in 2 days / max yield in 3;
- PET_CAFE consumes CARROT at double per-tick rate because it is a single-product shop;
- FARMERS_MARKET also consumes CARROT.

## Data discipline

Frozen partitions:

- development: 16 seeds — open for iteration;
- validation: 16 seeds — R4B gate already opened; changed code needs a fresh exact validation gate;
- held-out: 32 seeds — **never opened**.

New exploratory pool:

- `configs/exploratory_live_meta_seeds_20260825.json`;
- 20 environmental seeds reproduced from the official Aug-25 top-20 high-Elo episode set;
- development/diagnostic only;
- seed, episode and team identities are forbidden strategy features;
- never merge into validation/held-out.

## Frozen R4A base

COK V8:

- upstream commit `779caaec88a441345871e2d62eb5de93606b7b52`;
- source SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`;
- Apache-2.0;
- frozen as `R4A-public-base-v1`.

## Controlled modern public benchmark panel

Frozen R4B on all 16 development seeds × both seats:

| Opponent | W-L-T | Score | Mean delta |
|---|---:|---:|---:|
| Kaito V27 | 25-7-0 | 0.78125 | +4,396.84375 |
| Rayk V11 | 30-2-0 | 0.93750 | +7,477.21875 |
| Andrew V12 | 26-6-0 | 0.81250 | +5,287.43750 |
| **Combined** | **81-15-0** | **0.84375** | **+5,720.5** |

These remain regression controls, **not a calibrated proxy for the hosted field**.

## Closed/deprioritized route branch

### KEXP-015 — fixed route replacements

- baseline 81-15;
- default→10C/4S 81-15, money higher only;
- default→6C/8S 78-18.

No promotion.

### KEXP-016 — legal public context

Corrected run `32968422225`, all jobs PASS. It fixed the earlier physical-state/internal-route conflation. Context evidence was too opponent-correlated for a deployable selector.

### KEXP-017 — three-branch macro oracle

Run `32972566807`, 288 development games.

Perfect ex-post branch choice:

- Kaito 25-7 → 25-7;
- Rayk 30-2 → 32-0;
- Andrew 26-6 → 26-6;
- aggregate **81-15 → 83-13**.

A solver over the existing route library has low prize-value headroom and is **deprioritized**. Search/optimization remains available only for higher-ceiling bounded subproblems.

## Official live-meta intelligence — current frontier

### KEXP-018 — radar

Official public sources:

- `kaggle/kaggriculture-episodes-index`;
- `kaggle/kaggriculture-episodes-YYYY-MM-DD`.

Expanded Aug-25 top-20 run `32977177944`:

- 688 daily episodes;
- median episode avg Elo ~2761.31;
- selected top band ~3056.61–3069.55;
- artifact `9609951191`, ZIP SHA-256 `ec15ee2b2d5827e517af85e7018a7dcfe79a0b94f78ec574c17f30893b5b6964`.

The live top band is strategically heterogeneous. Winners rotate crops and herds instead of converging to one fixed final farm.

### Hosted episode forensics

Run `33018633680` confirmed official episode JSON contains `info.seed`, `Agents`, and `TeamNames`; daily manifest itself has no identity fields.

Once the Aug-26 daily dataset or Kculture Episode IDs are available, locate our hosted games and reproduce their environmental seeds exactly.

### Static COK live-meta gap

Latest exact audit run `33019622974` — SUCCESS.
Artifact `9625980030`, ZIP SHA-256 `09ceabc082093af71ceb46a8fa9f50fd567dac3a5b2c6683a154166f22b65afe`.

Rejected hypothesis: COK does **not** waste final-day actions on CARE/FEED; it also has zero CARE/FEED during 696-718.

More important gap: COK remains extremely WHEAT-heavy late and largely commits strategy from the first three shops. Representative routes during 600-671 plant roughly **28-32 WHEAT versus 0-3 CARROT**, even though the complete eight-shop multiset is already public.

## KEXP-021 — same-day full-demand response

Canonical record:
`experiments/KEXP-20260826-021-live-meta-demand-response/README.md`

Run `33019276166` — SUCCESS; artifact `9625868747`; ZIP SHA-256 `0a0c9028ce33b177b61a41fe4da691f6de6b7740c4729a0108ad4991e33dd821`.

Top-20 Aug-25, 40 player-games:

- CARROT-demand weight → CARROT seed buy 600-671 Pearson **+0.46156**;
- winners mean late CARROT seeds **14.20**, losers **2.95**;
- winners final-day CARROT sales **50.95**, losers **4.85**.

Because all selected games were Crop Dusta vs Ryo Hasegawa, no policy was promoted.

## KEXP-022 — longitudinal demand response

Canonical record:
`experiments/KEXP-20260826-022-live-meta-demand-longitudinal/README.md`

Run `33019559986` — SUCCESS; artifact `9625961691`; ZIP SHA-256 `76ddbf8e2d453cdb357143002646e14c59fdbed054240089ef19968ce26a3963`.

Demand→late CARROT seed-buy Pearson by day:

- Aug-22 **+0.49505**;
- Aug-23 **+0.52212**;
- Aug-24 **+0.53413**;
- Aug-25 **+0.50326**.

This establishes a robust multi-day mechanism: strong live agents systematically use the complete public late demand state to alter crop allocation.

Important negative result: “more CARROT always wins” is false. Winner/loser CARROT quantities reverse on some days and demand levels. Therefore any Kculture candidate must be **state-aware and conservative**, not a fixed CARROT quota copied from one leader.

Distinct top families (`Subramanya + Aakarsh`, `Crop Dusta`, `Ryo Hasegawa`) demonstrate different responses, reducing the risk that this is a one-team artifact.

## Current R4D hypothesis

Highest-value bounded intervention:

> after all eight shop instances are visible, use legal public demand/economic state to redirect a bounded subset of existing late WHEAT seed/plant slots to short-horizon CARROT when scarcity opportunity is strong.

Design invariants:

1. preserve frozen R4B/COK behavior outside this crop mechanism;
2. preserve movement, labor, animals, recovery controllers and step-718 terminal liquidation;
3. use only legal public shops/prices plus own state;
4. no seed/team/opponent identity features;
5. W/L primary;
6. first test on canonical modern development panel and separately on 20 live-meta environmental seeds;
7. candidate must show cross-panel improvement with no severe family regression;
8. exact freeze before fresh validation;
9. no second Kaggle submission until validation earns it;
10. held-out remains sealed 32/32.

See `research/LIVE_META_DEMAND_DIAGNOSTIC_20260826.md`.

## Experiment numbering note

A temporary ID collision occurred because an earlier animal-lifecycle study already occupied `KEXP-019`. The new demand studies were canonicalized as **KEXP-021** and **KEXP-022**. Their original `019/020` demand paths are historical aliases only and must not be counted as separate experiments.

## Immediate continuation — prize-first

1. Implement one or two **conservative late demand-response candidates**, changing only existing late WHEAT seed/plant slots.
2. Predeclare triggers before seeing candidate results; prefer demand + market/economic evidence over raw demand threshold.
3. Establish paired R4B baselines on the 20 exploratory live-meta seeds.
4. Screen candidates on both canonical 16×3 modern development panel and live-meta environmental pool, both seats.
5. Kill variants that improve money without W/L or collapse against any family.
6. Continue hosted-episode forensics when Aug-26 data appears.
7. Freeze only a materially better candidate; then open a fresh validation gate.
8. Keep the hosted R4B immutable and all 32 held-out seeds sealed until justified.
