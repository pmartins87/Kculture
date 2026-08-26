# KEXP-20260826-019 — longitudinal official live-meta falsification

Status: **PREDECLARED / OBSERVATIONAL / DEVELOPMENT INTELLIGENCE ONLY**

## Question

Does the late stop-investment / herd-exit signal observed in the 2026-08-25 top ladder band persist across recent days, or is it merely a one-day/two-team artifact?

KEXP-018 found that top-20 winners on 2026-08-25 reduced herd by 5.8 animals on average from step 672→719 versus 1.25 for losers, with the effect concentrated in the winning `Crop Dusta` family. Before any Kculture policy mutation, this experiment tests temporal generalization.

## Source

Official public Kaggriculture Episodes datasets only:

- `kaggle/kaggriculture-episodes-index`;
- `kaggle/kaggriculture-episodes-2026-08-23`;
- `kaggle/kaggriculture-episodes-2026-08-24`;
- `kaggle/kaggriculture-episodes-2026-08-25`.

Data are fetched via `kagglehub` without credentials. Raw ~30MB episode JSONs are temporary and are not committed; only compact reports are preserved as Actions artifacts.

## Frozen screen

For each date independently:

- select the 10 episodes with highest official `avg_score` in that day's manifest;
- profile both players and matched winner/loser outcomes;
- record team labels for research grouping only;
- record herd changes, terminal farm composition, seeds/sales, action mix and late windows;
- do not use opponent/team identity as a deployable policy feature.

Total target: **30 official episodes / 60 player-games** across three dates.

## Predeclared interpretation

A late-exit mechanism is considered worth a development counterfactual only if at least one of these holds:

1. winner herd reduction exceeds loser herd reduction on at least two of the three dates; or
2. within a repeated high-performing family, winners show materially stronger late herd reduction than that same family's losses on multiple dates; or
3. a closely related stop-investment signature (sharp FEED/CARE decline plus increased harvest/drop/sales throughput) repeats across different top families even when physical herd exit differs.

Failure to generalize means the herd-exit idea is deprioritized. No threshold is retrofitted after looking at results.

## Guardrails

- observational only;
- no frozen validation seeds;
- no held-out seeds;
- no code promotion from replay correlation;
- no team-name/opponent-ID/episode-ID policy rules;
- hosted R4B remains immutable.

## Follow-up if signal survives

Create a narrow Kculture counterfactual based on **official state mechanics**, not imitation by identity. Candidate examples may include state-aware suppression of terminally worthless CARE or selective FEED cessation when remaining production value is below wheat/action opportunity cost. Each candidate must be development-screened with W/L primary before any fresh validation access.
