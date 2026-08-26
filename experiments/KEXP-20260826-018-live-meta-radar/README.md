# KEXP-20260826-018 — official live-meta radar

Status: **ACTIVE / OBSERVATIONAL / PRIZE-FIRST CALIBRATION**

## Motivation

The hosted R4B submission is valid (`Complete`) but its visible rating moved **161.6 → 135.7**, while the same frozen policy scores 81-15 against our three exact public benchmark snapshots. This is a large local/hosted contradiction.

The official Kaggriculture ecosystem publishes a daily Episodes index and per-day top episode replay datasets. Those replays sample agents that are **actually playing at the top of the current ladder**, including strategies whose source code may be private. This is a more direct calibration source than repeatedly tuning only against Kaito V27, Rayk V11 and Andrew V12.

## Question

What does the current high-Elo live field actually do, and where does frozen R4B structurally differ?

## Data

Official public datasets only:

- `kaggle/kaggriculture-episodes-index`;
- latest `kaggle/kaggriculture-episodes-YYYY-MM-DD` referenced by the index.

Acquisition uses unauthenticated `kagglehub.dataset_download(path=...)` and downloads only:

1. index `manifest.csv`;
2. latest day `manifest.csv`;
3. a small number of highest-`avg_score` episode JSONs.

The large raw episode JSONs are temporary and are **not** uploaded as GitHub artifacts. Only the compact derived report is retained.

## First screen

Top **5** episodes from the latest official index date.

For each player-game extract:

- team name from replay metadata for analysis only;
- reward/status;
- first-three shop sequence;
- farm composition and unlocked land;
- worker counts;
- action histogram;
- movement/PASS/productive-action percentages;
- seed purchases;
- market sale quantities;
- money/farm checkpoints at 600/648/672/696/708/717/719.

Aggregate winner profiles separately.

## Policy-use boundary

Opponent/team identity is **never** a deployable feature. Episode IDs are never policy features. The dataset is for discovering general strategic patterns and calibrating our lab to the actual live meta.

## Decision use

This experiment does not directly promote code. It may:

- reveal strategy families absent from our local opponent panel;
- identify production/labor/market patterns associated with current top play;
- identify why R4B is locally flattering itself;
- motivate new broad development tests;
- guide acquisition of additional public agents that resemble the actual top meta.

Any policy change still requires development W/L evidence, exact freeze and fresh validation before submission.

## Data separation

- does not consume frozen validation seeds;
- does not consume held-out seeds;
- all 32 held-out remain sealed.
