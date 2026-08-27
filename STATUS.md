# STATUS — Kculture

Last updated: 2026-08-27

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for code, experiments, public-package provenance, Actions evidence, hosted submissions and continuation state.

## Hosted reality — reset trigger

Current calibration snapshot:

- `Kculture_KEXP050_reallocate614_validated_v1_submission.tar.gz`: **145.1**, Complete / green check;
- `Kculture_R4B_market_only_validated_v1_submission.tar.gz`: **142.0**, Complete / green check.

KEXP-050 had passed development, exploratory live-meta, a fresh 192-game stress, fresh validation and exact package parity. A +3.1 hosted separation is far below prize-scale progress. Therefore the R4B → micro-overlay promotion program remains **frozen as calibration history**.

Earlier R4B snapshots: **161.6 → 135.7 → 110.5 → 142.0**. Rating is dynamic; exact values are evidence snapshots, not permanent scores.

**Held-out remains 32/32 sealed.**

## Frozen hosted references

### R4B

- candidate: `candidates/r4b_ablation_market_only.py`;
- blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- package parity proven;
- current role: weak hosted calibration reference / exploit detector, not likely final candidate.

### KEXP-050

- candidate: `candidates/r4d_reallocate_614_carrot.py`;
- blob: `61b77be136836328917441cb03f89bc6665c4c27`;
- KEXP-054 validation run `33073517302`: direct **14-8-10**, score 0.59375, mean +31.06, zero errors;
- formal package run `33074434495`, exact package parity;
- archive SHA-256 `59a45adf283f2f4dd1f9272150786c014585aa08c9b31b3348cf992ebe3bb64c`;
- hosted snapshot **145.1**;
- current role: evidence that a carefully validated local micro-improvement did not close the hosted gap.

## Competitive Reset — ACTIVE

Research record: `research/COMPETITIVE_RESET_20260827.md`.

### CR-001 — exact scored-package identity: CLOSED

The hypothesis that Kculture had benchmarked the wrong public files was falsified for the principal strong references.

- **Kaito V27 V4, historical 3090.1**: package `main.py` == old benchmark file;
- **Rayk V11, historical 2990.4**: package `main.py` == old benchmark file;
- **Andrew V12, historical 2883.0**: package `submission.py` byte-identical to old benchmark `main.py`.

Therefore R4B really did beat exact historically high-scoring code locally. The old three-agent 81-15 panel is permanently retired as a promotion metric.

### CR-002 — historical-public Bradley–Terry proxy: CLOSED / CALIBRATION_FAIL

Canonical run: **`33084489238`**  
Result artifact: **`9652034347`**  
Artifact ZIP digest: **sha256:52698fd46d11968893a96baac908cac86afccd0ce9dbe93c726ab4246fd97787**  
Protocol/result: `experiments/CR-002-broad-proxy-league/README.md`.

Frozen design completed:

- 10 identity-proven historical public references + R4B + KEXP-050;
- all **66/66** unordered pairs;
- 6 common fresh seeds per pair;
- both seats;
- **792 games**;
- zero runtime/status errors.

Predeclared gate result:

- complete matrix: PASS;
- zero errors: PASS;
- public BT order accuracy: **0.6888889** vs >=0.65 — PASS;
- public Spearman: **0.5757576** vs >=0.60 — **FAIL**;
- formal status: **CALIBRATION_FAIL**.

Local BT ranking started with **KEXP-050 #1, R4B #2**, followed by Flex, Andrew, Kaito and Rayk. This is incompatible with their ~145/~142 hosted snapshots.

The stronger falsification is direct coverage: R4B beat every one of the ten historical public references, totaling **112-8 / 120** on fresh seeds:

- Kaito 8-4;
- Rayk 12-0;
- Andrew 10-2;
- Prvsiyan Frontier 12-0;
- Flex 10-2;
- Bruce 12-0;
- Roman 12-0;
- Anas 12-0;
- Prvsiyan Baseline 12-0;
- Renji 12-0.

Conclusion: the historical-public generation is structurally unrepresentative of the current hosted field relevant to Kculture. CR-002 is **diagnostic only** and must never be used for promotion.

### Temporal diagnosis — confirmed

Public notebook score snapshots have moved substantially with the evolving ladder. Examples observed on 2026-08-27 include current-version/public scores materially below old best scores for Rayk, Flex and Andrew. Temporal freshness is now a first-class calibration variable.

### CR-002B — current-meta proxy: ACTIVE / PREFLIGHT

Frozen config: `configs/competitive_reset_current_meta_v1.json`  
Current preflight workflow: `.github/workflows/cr002b-current-meta-preflight.yml`  
Preflight run 2: **`33086405765`**.

Current snapshot set uses recent exact public notebook versions and contemporaneous observed public scores, including:

- Kaito Sparse V13 — 2882.0;
- Prvsiyan Frontier V10 — 2610.2;
- Salem Harvest V4 — 2590.2;
- Rayk Rank V23 — 2563.4;
- Kaito Future/Unseen V1 — 2530.5;
- Tactical Memory V1 — 2491.7;
- BoatLee Route V2 — 2467.9;
- Andrew Kaggriculture V11 — 2441.2;
- Tetsu Town V2 — 1896.6 lower current-score anchor.

Flex V84 was initially selected as the lower anchor because its public page exposed 1961.6, but KaggleHub returned 404 for that exact version identifier during package preflight. It was replaced **before any CR-002B league episode** by reproducible Tetsu V2; the replacement and reason are frozen in the config.

CR-002B has a stricter calibration gate:

- complete pair matrix;
- zero runtime errors;
- public Spearman >= **0.65**;
- public pair-order accuracy >= **0.70**;
- **hosted sanity clause:** R4B/KEXP-050 must not rank above the majority of contemporaneous 2400+ references. If they do, the proxy fails even if public-public correlation passes.

No CR-002B league begins until every exact public snapshot has a reproducible runnable package entry point and frozen content hash.

## CR-003 — architecture research active in parallel

Research map: `research/CR003_PUBLIC_STRONG_ARCHITECTURE_MAP.md`.

Static study of public high-scoring agents shows a recurring progression:

1. mechanically competent routed/base policy;
2. repair/robustness overlays;
3. dynamic cash-flow and sell timing;
4. market-state adaptation using demand/price/inventory;
5. meta/opponent adaptation and race/front-running logic.

The strongest public 2700–3100 historical agents do not require a full-game solver or end-to-end RL. R4B is mechanically strong but strategically much less expressive at the economic/meta layer.

The next legitimate Kculture architecture should therefore combine a strong mechanical base with a **stateful economic controller**, multi-product allocation, cash reserves/sale timing, terminal liquidation, and only then controlled meta adaptation.

Do not resume isolated CARROT/TOMATO micro-overlay optimization as the main line. Do not start end-to-end PPO as the first reset move.

## Exact continuation

1. Complete CR-002B preflight run `33086405765` and inspect all nine manifests.
2. Freeze exact runnable entry points and hashes; do not normalize away package dependencies.
3. Launch the current-meta round-robin only after preflight PASS.
4. Apply all CR-002B gates, including the hosted sanity clause, without reinterpretation.
5. If calibrated, identify the true current-meta coverage hole and build CR-003 against that distribution.
6. If still uncalibrated, expand with even fresher public snapshots and official recent-episode behavior before promoting any strategy.
7. Keep all **32/32 held-out sealed**.

## Paused branches

CARROT/TOMATO micro-overlay work is paused. KEXP-053/055 remain mechanics research only; KEXP-056 must not delay the reset. KEXP-037 is also held.

## Frozen environment facts

- `kaggle-environments==1.32.7`;
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`;
- 720 recorded states; state 718 final executable action;
- terminal reward is farm money;
- replay alignment: `state t -> action frame t+1`;
- final competition relevance is Bradley–Terry / matchup strength, so broad **current-field** coverage matters more than isolated head-to-head exploits.
