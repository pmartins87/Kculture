# Competitive Reset — 2026-08-27

## Trigger

Hosted snapshot after the validated KEXP-050 submission:

- KEXP-050: **145.1**;
- R4B at the same snapshot: **142.0**.

KEXP-050 had passed development, exploratory live-meta, a fresh 192-game stress, fresh validation and exact package parity. The tiny hosted separation invalidated the working assumption that the old three-agent local strong panel was a sufficiently calibrated promotion proxy.

## CR-001 — exact scored-package identity audit: CLOSED

The initial reset hypothesis was that Kculture may have benchmarked notebook-output helper files rather than the exact packages that earned high Kaggle scores. The audit largely **falsified that explanation**.

Exact results:

- **Kaito V27 V4 — historical 3090.1:** `submission.tar.gz/main.py` is byte-identical to the `main.py` Kculture benchmarked. SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`.
- **Rayk V11 — historical 2990.4:** packaged `main.py` is byte-identical to the benchmarked file. SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`.
- **Andrew V12 — historical 2883.0:** package member is named `submission.py`, but it is byte-identical to the benchmarked top-level `main.py`. SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`.

Therefore the old R4B results such as 25-7 versus Kaito and ~30-2/32-0 versus Rayk were genuinely against the exact historically high-scoring code. They still failed to predict hosted strength.

### Dominant interpretation after CR-001

**Tiny-panel head-to-head strength is not field strength.** Kaggriculture is strongly matchup-dependent/non-transitive enough that an agent can exploit several elite public policies and still perform poorly across the wider population. The old 81-15 panel is retired as a promotion metric.

Package identity remains mandatory, but it is no longer the main explanation of the calibration failure.

## CR-001B — broaden public reference coverage

A second package audit acquired identity-proven public agents across a much wider historical score range. The reset league now has exact package identities for public references around:

- 3090.1 Kaito;
- 2990.4 Rayk;
- 2883.0 Andrew;
- 2798.6 Prvsiyan Frontier;
- 2767.3 Flex;
- 2754.9 Bruce;
- 2391.0 Roman;
- 2213.8 Anas;
- 2123.7 Prvsiyan Baseline;
- 1771.3 Renji.

Third-party code is kept in GitHub Actions artifacts, not committed into this public repository. License/provenance must remain attached to any future derivative use.

## CR-002 — broad Bradley-Terry proxy league: ACTIVE

Frozen config: `configs/competitive_reset_league_v1.json`.  
Protocol: `experiments/CR-002-broad-proxy-league/README.md`.  
Actions run: **`33083452488`**.

Entrants:

- the 10 public references above;
- frozen R4B, hosted snapshot 142.0;
- frozen KEXP-050, hosted snapshot 145.1.

Design:

- all **66** unordered pairs;
- 6 common fresh environmental seeds per pair;
- both seats;
- **792 complete games** if all jobs succeed;
- fit one local Bradley–Terry model;
- compare public local BT ranking with historical Kaggle score ranking.

Predeclared calibration gate:

- 66/66 pair reports;
- zero runtime errors;
- Spearman(public BT, historical score) >= **0.60**;
- public BT ordering accuracy >= **0.65**.

If CR-002 fails, it remains diagnostic only and the field/episode model must be expanded before any new candidate is promoted. If it passes, it becomes the first promotion-grade local strength proxy of the reset.

## CR-003 — true strong baseline

The next strategic milestone is **not** 145 → 170. It is to start from/reproduce a legitimate public high-strength baseline in the approximate 2000–3000 historical score class, preserving attribution/license/provenance, and then improve broad meta coverage rather than one or two hand-picked matchups.

Candidate directions after a calibrated benchmark exists:

- dynamic production/capital allocation;
- market-aware crop/animal portfolio control;
- high-level behavioral cloning from strong trajectories;
- bounded search/value models for high-leverage decisions;
- policy mixtures / meta diversification to reduce non-transitive weakness.

End-to-end PPO is not the first reset step.

## Frozen old line

R4B and KEXP-050 remain useful hosted calibration references. CARROT/TOMATO micro-overlays are paused. KEXP-056 is not allowed to delay CR-002.

## Prize-first decision rule

Continue aggressively if the reset can reproduce public field ordering and give us a believable route from an identity-proven 2000–3000-class baseline toward broad tournament strength. If even the public state of the art cannot be reproduced/calibrated after CR-002/CR-003, reassess expected financial return rather than spending the remaining competition time on low-impact local patches.
