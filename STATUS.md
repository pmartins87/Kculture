# STATUS — Kculture

Last updated: 2026-08-27

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for code, experiments, public-package provenance, Actions evidence, hosted submissions and continuation state.

## Hosted reality — reset trigger

Current user-visible Kaggle snapshot:

- `Kculture_KEXP050_reallocate614_validated_v1_submission.tar.gz`: **145.1**, Complete / green check;
- `Kculture_R4B_market_only_validated_v1_submission.tar.gz`: **142.0**, Complete / green check.

KEXP-050 had passed development, exploratory live-meta, a fresh 192-game stress, fresh validation and exact package parity. A +3.1 hosted separation is far below prize-scale progress. Therefore the R4B → micro-overlay promotion program is **frozen as calibration history**, not continued as the main development strategy.

Earlier R4B rating snapshots: **161.6 → 135.7 → 110.5 → 142.0**. Rating is dynamic; exact current values are evidence snapshots, not permanent scores.

**Held-out remains 32/32 sealed.**

## Frozen hosted references

### R4B

- candidate: `candidates/r4b_ablation_market_only.py`;
- blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- package parity proven;
- current role: weak hosted calibration reference, not likely final candidate.

### KEXP-050

- candidate: `candidates/r4d_reallocate_614_carrot.py`;
- blob: `61b77be136836328917441cb03f89bc6665c4c27`;
- KEXP-054 validation run `33073517302`: direct **14-8-10**, score 0.59375, mean +31.06, zero errors;
- validation public controls unchanged: Kaito 25-7, Rayk 32-0, Andrew 21-11;
- formal package run `33074434495`, exact package parity;
- archive SHA-256 `59a45adf283f2f4dd1f9272150786c014585aa08c9b31b3348cf992ebe3bb64c`;
- hosted first snapshot **145.1**;
- current role: evidence that a carefully validated local micro-improvement did not close the hosted gap.

## Competitive Reset — ACTIVE

Research record: `research/COMPETITIVE_RESET_20260827.md`.

### CR-001 — exact scored-package identity: CLOSED

The hypothesis that Kculture had benchmarked the wrong public files was largely falsified.

Exact package identity:

- **Kaito V27 V4, historical 3090.1**: package `main.py` == old benchmark file, SHA `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`;
- **Rayk V11, historical 2990.4**: package `main.py` == old benchmark file, SHA `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`;
- **Andrew V12, historical 2883.0**: package `submission.py` is byte-identical to old benchmark `main.py`, SHA `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`.

Therefore R4B really did beat exact historically high-scoring code locally. The old three-agent 81-15 panel is retired as a promotion metric because it has poor field calibration. **Non-transitivity / matchup coverage is now the dominant explanation.**

### CR-001B — broad public reference acquisition: COMPLETE ENOUGH FOR V1

Identity-proven exact packages now span approximately:

3090 Kaito; 2990 Rayk; 2883 Andrew; 2799 Prvsiyan Frontier; 2767 Flex; 2755 Bruce; 2391 Roman; 2214 Anas; 2124 Prvsiyan Baseline; 1771 Renji.

Third-party sources stay in Actions artifacts; they are not committed into this public repository. Attribution/license/provenance remain mandatory for any derivative use.

### CR-002 — broad Bradley–Terry proxy league: RUNNING

Workflow: `.github/workflows/cr002-broad-proxy-league.yml`  
Run: **`33083452488`**  
Protocol: `experiments/CR-002-broad-proxy-league/README.md`  
Config: `configs/competitive_reset_league_v1.json`.

Frozen design:

- 10 identity-proven public references + R4B + KEXP-050;
- all **66** unordered pairs;
- 6 common fresh seeds per pair;
- both seats;
- **792 games** total;
- fit one local Bradley–Terry model;
- test Spearman/local-order correlation against historical public Kaggle scores.

Predeclared calibration gate:

- complete 66/66 pair matrix;
- zero runtime errors;
- public Spearman >= **0.60**;
- public BT ordering accuracy >= **0.65**.

The prepare stage already passed: all 10 exact public packages were downloaded and hash-verified. Pair jobs are queued/running in GitHub Actions.

If CR-002 passes, it becomes the first promotion-grade local strength proxy of the reset. If it fails, do **not** optimize candidates against it; expand/reweight the field or episode model first.

## CR-003 — next strategic milestone

The target is no longer “145 → 170”. The target is to start from/reproduce a legitimate **2000–3000-class public baseline** and then improve broad tournament coverage.

Only after CR-002 calibration do we choose the derivative architecture. Current candidate directions:

- dynamic production/capital allocation;
- market-aware crop/animal portfolio control;
- high-level behavioral cloning from strong trajectories;
- bounded search/value models for high-leverage decisions;
- policy mixtures/meta diversification against non-transitivity.

Do not start end-to-end PPO as the first reset move.

## Paused branches

CARROT/TOMATO micro-overlay work is paused. KEXP-053/055 remain useful mechanics research, but KEXP-056 must not delay CR-002/CR-003. KEXP-037 is also held.

## Exact continuation

1. Poll CR-002 run `33083452488`.
2. If any pair job fails mechanically, repair execution without changing frozen entrants/seeds/gate.
3. When all pair artifacts exist, inspect `cr002-league-result` and apply the predeclared calibration gate exactly.
4. If calibrated, inspect where R4B/KEXP-050 rank in the broad local BT league and identify which public baseline gives the best legal/provenance-safe starting point for CR-003.
5. If uncalibrated, diagnose rank reversals/non-transitive cycles and broaden/reweight the reference population before developing another candidate.
6. Keep all **32/32 held-out sealed**.

## Frozen environment facts

- `kaggle-environments==1.32.7`;
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`;
- 720 recorded states; state 718 final executable action;
- terminal reward is farm money;
- replay alignment: `state t -> action frame t+1`;
- final competition relevance is Bradley–Terry / matchup strength, so broad coverage matters more than isolated head-to-head exploits.
