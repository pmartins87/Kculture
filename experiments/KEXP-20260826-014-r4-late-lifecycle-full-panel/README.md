# KEXP-20260826-014 — R4 late-lifecycle full-panel diagnostic

## Purpose

Test whether the crop-lifecycle signal discovered in loss-focused KEXP-013 generalizes across **wins and losses** before any R4D policy mutation.

This experiment is diagnostic-only. It changes no agent behavior and opens **development seeds only**.

## Frozen candidate

`R4B-market-only-validated-v1`

- path: `candidates/r4b_ablation_market_only.py`
- Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- hosted package remains immutable.

## Exact opponent panel

Run all 16 frozen development seeds in both orientations against each independent current-meta family:

1. **Kaito V27 V4**
   - `kaitofukami/25-27-strict-future-v27-midgame-meta-reset/versions/4`
   - `main.py` SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`
   - public/best score snapshot 3090.1
   - Apache-2.0.
2. **Rayk V11**
   - `raykkretzschmar/kaggriculture-rank-your-agent/versions/11`
   - `main.py` SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`
   - best-score snapshot 2990.4
   - benchmark-only until license independently verified.
3. **Andrew V12**
   - `andrewsokolovsky/kaggriculture-breaking-the-tie/versions/12`
   - `main.py` SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`
   - best-score snapshot 2915.2
   - Apache-2.0.

Each job must reacquire the exact public notebook output and fail closed if the expected SHA-256 does not match.

## Protocol

- environment: `kaggle-environments==1.32.7`;
- partition: exact `development` list from `configs/seed_partitions.json`;
- 16 seeds × 2 candidate seats × 3 opponents = **96 games**;
- fresh-load both file agents for every episode;
- no validation seed;
- no held-out seed;
- checkpoints: 600, 648, 672, 696, 708, 717, 718, 719;
- action windows: 672–695 and 696–718.

The diagnostic records, for candidate and opponent:

- money trajectory;
- strawberries expiring at step 672 and by step 696;
- weeds and productive crop tiles at step 696;
- hands at step 708;
- carried/shed inventory;
- final-day PASS, HARVEST, DROP and requested SELL quantities;
- terminal result and 672→terminal relative swing.

Tool: `tools/run_late_lifecycle_panel.py`.

## Predeclared hypotheses

The loss-focused KEXP-013 observation is **not** accepted as causal evidence unless it separates wins from losses on the full panel.

### H1 — lifecycle load

In at least **two independent opponent families**, loss games should show a worse late crop-lifecycle state than win games in the same directional sense:

- greater candidate/relative strawberry-expiry load at step 672 or by 696; and/or
- greater relative weeds at 696; and
- lower relative productive crop acreage at 696.

### H2 — economic consequence

Across the combined panel, worse lifecycle state should move in the mechanically expected direction with 672→terminal relative swing:

- more weeds / more candidate expiry: negative relationship with late swing;
- more productive acreage: positive relationship with late swing.

Pearson correlation is descriptive because features are discrete and opponent-family mixtures are heterogeneous; signs and win/loss group separation matter more than one arbitrary magnitude cutoff.

### H3 — residual throughput

After examining lifecycle separation, final-day labor/throughput variables are treated as a **separate residual mechanism**:

- hands;
- HARVEST;
- DROP;
- requested SELL quantity;
- PASS.

They must not be bundled automatically into the first lifecycle intervention.

## Decision rule

**Allow R4D crop-lifecycle prototype** only if H1 is directionally reproduced across at least two families and the combined H2 evidence is compatible with the same mechanism.

If lifecycle separation is weak/inconsistent, reject crop-lifecycle targeting and move the next causal experiment to labor/harvest/drop/market conversion instead.

If lifecycle is confirmed, R4D must still obey:

- legal-state-observable logic only;
- no seed ID;
- no opponent ID;
- preserve successful opening/midgame unless the tested state trigger fires;
- preserve frozen terminal market completeness;
- one narrow mechanism first;
- all 16 development seeds/current-meta panel before any new validation gate.

## Hosted-score context

The first exact R4B submission is now `Complete` on Kaggle but its first observed live score is **161.6**, far below the 600 initialization documented for valid simulation submissions and far below mature public benchmarks around 2900–3100. KEXP-014 therefore serves both R4D engineering and local-vs-hosted calibration: it tests a mechanism already seen across three public families rather than reacting to the ladder score with an ungrounded patch.

## Status

**PREDECLARED — NOT YET RUN.**
