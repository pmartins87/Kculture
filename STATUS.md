# STATUS — Kculture

Last updated: 2026-08-27

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for strategy, code, experiments, Actions evidence, hashes, roadmap and handoff state.

## Prize-first decision rule

- User suggestions, assistant suggestions and public strategies are **hypotheses, not directives**.
- Prefer expected prize value over elegance, novelty or architectural purity.
- Cheap falsification before expensive implementation.
- W/L/T generalization and hosted relevance outrank money-margin improvements.
- Kill/deprioritize avenues whose measured ceiling is small.
- Local public benchmarks are models; official hosted/live-ladder evidence is calibration truth when they conflict.
- Never pivot architecture merely because a technique was mentioned.

See `docs/PRIZE_FIRST_DECISION_POLICY.md`.

## Gate summary

- **R0 COMPLETE** — competition entry confirmed.
- **R1 PASS** — exact official starter/environment reproduction.
- **R2 PASS** — deterministic laboratory; 16 development / 16 validation / 32 held-out seeds.
- **R3 DELIVERY PASS / HOSTED CALIBRATION FAILING** — first exact R4B package is `Complete` with green Kaggle check, but visible rating fell **161.6 → 135.7**.
- **R4 ACTIVE** — hosted champion remains frozen R4B while R4D searches for a materially better replacement.
- **R4B VALIDATION PASS** — `R4B-market-only-validated-v1`.
- **KEXP-015 NO PROMOTION** — fixed route overrides do not improve W/L.
- **KEXP-017 COMPLETE / route-solver branch DEPRIORITIZED** — perfect ex-post choice among current three macro branches improves only 81-15 → 83-13.
- **KEXP-018 COMPLETE / OPERATING INFRASTRUCTURE** — official live-meta radar now tracks actual top-ladder episodes and is scheduled twice daily.
- **KEXP-019 COMPLETE / SUPPORTS late stop-investment** — across Aug-23/24/25 top episodes, winners almost eliminate CARE in 672-695 and reduce herd more than losers.
- **KEXP-021 COMPLETE** — same-day CARROT demand-response signal found.
- **KEXP-022 COMPLETE** — four-day longitudinal replication confirms strong agents adapt late crop allocation to full shop demand; unconditional CARROT rule rejected.
- **KEXP-023 RUNNING (rerun after import-only fix)** — audit whether existing late WHEAT physical cycles can safely host CARROT substitution.
- **KEXP-024 RUNNING** — mechanics-based terminal CARE→HARVEST/COLLECT/PASS ablation on development only.
- **Held-out sealed 32/32.**

## Current hosted champion

`R4B-market-only-validated-v1`

- candidate `candidates/r4b_ablation_market_only.py`;
- frozen Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors;
- package parity run `32919305800`: 4/4 full trajectories identical;
- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- Kaggle status `Complete`, green check;
- observed live score **161.6 → 135.7**.

The declining hosted rating is a serious local/online contradiction, not evidence of packaging failure. Do not spend submission #2 without a materially stronger, freshly validated candidate.

## Frozen environment / evaluation facts

- `kaggle-environments==1.32.7`.
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- 720 recorded states; step 718 is the final executable action.
- terminal reward is exactly `farm.money`.
- positive-price SELL executes after unit actions; leftover inventory has no terminal reward.
- ladder rating depends on W/L/T, not coin margin.
- latest two submissions remain tracked for final evaluation.
- final submission deadline: 2026-09-30 23:59 UTC; games continue approximately to 2026-10-15 before final Bradley-Terry evaluation.
- current CARROT/TOMATO/EGG scarcity rebalance is already included in the frozen engine; it does **not** explain the hosted mismatch.

## Data discipline

- development: 16 frozen seeds — open for iteration;
- validation: 16 seeds — opened only for exact frozen R4B; changed code needs a fresh exact validation gate;
- held-out: **32/32 never opened**;
- exploratory live-meta pool: 20 environmental seeds reconstructed from official Aug-25 top episodes, development/diagnostic only. Seed/team/episode identity is forbidden as strategy input.

## Controlled modern public panel

Frozen R4B, all 16 development seeds × both seats:

| Opponent | W-L-T | Score | Mean delta |
|---|---:|---:|---:|
| Kaito V27 | 25-7-0 | 0.78125 | +4,396.84375 |
| Rayk V11 | 30-2-0 | 0.93750 | +7,477.21875 |
| Andrew V12 | 26-6-0 | 0.81250 | +5,287.43750 |
| **Combined** | **81-15-0** | **0.84375** | **+5,720.5** |

These are regression controls, **not a calibrated proxy for the hosted field**.

## Closed/deprioritized route branch

### KEXP-015

- baseline 81-15;
- default→10C/4S 81-15, money higher only;
- default→6C/8S 78-18.

No promotion.

### KEXP-017

Run `32972566807`, 288 development games. Perfect ex-post branch choice among baseline/10C4S/6C8S yields only:

- Kaito 25-7 → 25-7;
- Rayk 30-2 → 32-0;
- Andrew 26-6 → 26-6;
- aggregate **81-15 → 83-13**.

A solver over the existing route library has low prize-value headroom and is **deprioritized**. Search/optimization remains available for bounded high-ceiling subproblems only.

## Official live-meta intelligence — primary frontier source

### KEXP-018 live radar

Public sources:

- `kaggle/kaggriculture-episodes-index`;
- `kaggle/kaggriculture-episodes-YYYY-MM-DD`.

`tools/live_meta_radar.py` now records checkpoints 600/648/672/696/708/717/719, late-window physical/market actions, crops, herd, hands, shop prefixes and winner/loser aggregates. Workflow `live-meta-radar` is scheduled at 00:17 and 12:17 UTC daily; scheduled runs use top-10 episodes, manual runs default top-20.

Latest top-20 run `33036951875` (official date **2026-08-26**) — SUCCESS:

- daily episodes: 687;
- median avg score: **2752.948115**;
- top avg score: **3075.180535**;
- selected top20 range: **3075.180535 → 3057.712986**;
- 40 player-games / 20 winners;
- top band dominated by Crop Dusta and Ryo Hasegawa;
- artifact `9632352609`, ZIP SHA-256 `a0dc50e382ede83378b3c3c73c8b1479ec31d2101b484f339b5818d7d2a5dafd`.

Aug-26 winner means:

- reward 112,307.2;
- productive actions 43.03%, movement 52.91%, PASS 4.06%;
- step-672 herd 16.25 → final herd 12.05: **4.2-animal reduction**;
- losers reduce only **1.95** animals;
- 672-695: CARE 0.6, FEED 5.4, HARVEST 21.25, DROP 3.9, SELL qty 86.2;
- 696-718: CARE 0.5, FEED 0, HARVEST 21.35, DROP 14.1, SELL qty 158.25.

### Live policy fingerprint — architecture warning

Run `33019862336` — SUCCESS.

The two dominant high-Elo families are **not fixed tapes**:

- ~20 sampled trajectories per family, all complete trajectories unique;
- mean exact action agreement during steps 216-599:
  - Crop Dusta ~**1.36%**;
  - Ryo Hasegawa ~**0.88%**;
- modal exact action per step appears only around 7% of samples.

This is strong evidence that the hosted frontier is state-adaptive. It helps explain why COK/R4B can dominate fixed public notebooks locally yet rate poorly against the live field. Do not interpret it as proof that one specific adaptive architecture is optimal.

## Late animal stop-investment evidence

### Exact engine theorem

See `research/LATE_ANIMAL_TERMINAL_VALUE_20260826.md`.

- end-of-day after step 695 is the final plant/animal production refresh;
- CARE issued during 672-695 creates a pending care bonus only **after** that final production check, so it has zero direct terminal-production value;
- FEED in 672-695 can still prevent escape and/or gate an already-existing pending bonus, so it is not blanket-removable;
- HARVEST on an animal tile moves all held `yield_units` into the acting unit's inventory and resets tile yield to zero, potentially freeing `max_held` capacity before the step-695 refresh;
- COK routes still schedule roughly 8–10 CARE during 672-695.

### KEXP-019 longitudinal live evidence — COMPLETE

Run `33019193497` — SUCCESS, top-10 official episodes on Aug-23/24/25.

Winner herd reduction 672→719 versus losers:

- Aug-23: **2.2 vs 1.3**;
- Aug-24: **2.6 vs 0.4**;
- Aug-25: **6.7 vs 1.1**.

Winner CARE 672-695:

- Aug-23 **0.1**;
- Aug-24 **0.0**;
- Aug-25 **0.0**.

Thus the stop-investment mechanism survives temporal replication and is eligible for a controlled candidate. The deployable rule must still come from engine state, not team identity.

### KEXP-024 — terminal CARE reallocation: RUNNING

Candidate: `candidates/r4d_terminal_care_reallocate.py`, blob `daab48a896535cd514e725affef6e8568e6b0a21`.

Only steps 672-695 and only when base action is CARE:

1. HARVEST if current animal has product;
2. else COLLECT_FERTILIZER if available;
3. else PASS.

FEED, movement, routes, crops, market and step-718 R4B liquidation are unchanged.

Predeclared primary gate on modern development panel:

- zero errors;
- no family win-count regression;
- combined W/L must improve beyond **81-15**;
- direct candidate-vs-R4B score >=0.50 and mean delta >=0.

Run `33037860772` in progress. Validation/held-out closed.

## Live crop demand-response evidence

### KEXP-021

Aug-25 top20:

- CARROT demand-weight → late CARROT seed buy Pearson **+0.46156**;
- winners late CARROT seeds 14.20 vs losers 2.95;
- winner final-day CARROT sales 50.95 vs losers 4.85.

Same-day two-family confound prevented promotion.

### KEXP-022 — longitudinal replication

Run `33019559986` — SUCCESS.

CARROT demand→late CARROT seed-buy Pearson:

- Aug-22 **+0.49505**;
- Aug-23 **+0.52212**;
- Aug-24 **+0.53413**;
- Aug-25 **+0.50326**.

Strong live agents systematically use complete public late shop demand to alter crop allocation. “More CARROT always” is false; winner/loser quantities reverse on some dates/demand regimes. Any candidate must be contextual and conservative.

### Static COK gap

COK/R4B remains highly WHEAT-heavy after all eight shop instances are known. Representative route tapes during 600-671 plant ~28–32 WHEAT vs 0–3 CARROT. This is a concrete adaptation gap.

### KEXP-023 — late crop-cycle audit: RUNNING

Purpose: before changing WHEAT→CARROT, measure whether the existing physical tape harvests late WHEAT tiles on a horizon compatible with CARROT's shorter lifecycle.

- all 16 development seeds + 20 exploratory live-meta environmental seeds;
- unchanged R4B vs deterministic starter;
- inspect every `PLANT WHEAT` during 576-647 and next same-tile HARVEST;
- no strategy mutation and no validation/held-out.

First run `33037518259` failed before any game due only to direct-script Python import path. Import fixed without changing protocol. Rerun `33037701080` in progress.

## Immediate continuation — prize-first

1. Finish KEXP-023 and KEXP-024 without altering their gates after seeing outcomes.
2. If KEXP-024 improves W/L cross-family, broaden on exploratory live-meta environmental seeds before any validation.
3. If KEXP-024 is money-only or neutral in W/L, record NO PROMOTION despite clean mechanics.
4. If KEXP-023 shows most intended crop slots are mechanically CARROT-compatible, prototype one conservative shop-demand + current-price crop substitution; otherwise require a real crop lifecycle controller instead of blind substitution.
5. Keep the live-meta radar operating twice daily and use it to find mechanisms shared across dates/families rather than copy final farm templates.
6. Continue hosted-episode forensics once Kculture episode IDs/identities become available.
7. Freeze only a materially stronger candidate, then open a fresh candidate-specific validation gate.
8. Do not submit a second Kaggle agent before that gate.
9. Keep hosted R4B immutable and all **32 held-out seeds sealed**.
