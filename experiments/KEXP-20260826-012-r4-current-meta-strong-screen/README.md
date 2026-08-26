# KEXP-20260826-012 — exact current-meta strong screen

## Purpose

Test whether the frozen Kculture R4B champion remains competitive against two independent, more current public Kaggriculture families after the older Seyamalam/Kaito V18 panel became saturated.

This is a **development-only frontier screen**, not a validation/promotion gate.

## Exact opponents

### Rayk V11

- notebook: `raykkretzschmar/kaggriculture-rank-your-agent/versions/11`
- public Best Score snapshot associated with V11: **2990.4**
- exact `main.py`: 36,233 bytes
- SHA-256: `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`
- license not independently captured; benchmark-only, no derivative use.

### Andrew V12

- notebook: `andrewsokolovsky/kaggriculture-breaking-the-tie/versions/12`
- public Best Score snapshot associated with V12: **2915.2**
- exact `main.py`: 26,585 bytes
- SHA-256: `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`
- Apache-2.0 displayed on public Kaggle page.

Independent acquisition evidence is frozen in `research/CURRENT_META_ACQUISITION_20260826.md`.

## Protocol

Actions run: `32926727240`.

For every job:

1. exact notebook version downloaded by KaggleHub with Kaggle credential environment variables blank;
2. downloaded `main.py` rejected unless the exact SHA-256 above matches;
3. `kaggle-environments==1.32.7`;
4. all **16 frozen development seeds**;
5. both candidate seats;
6. compare both R4A/COK V8 control and frozen `R4B-market-only-validated-v1` against each opponent;
7. validation and held-out remain untouched.

Total: **128 development games**, zero execution errors.

## Results

| Candidate | Opponent | W-L-T | Score | Mean money delta | Min delta | Errors |
|---|---|---:|---:|---:|---:|---:|
| R4A | Rayk V11 | **30-2-0** | 0.9375 | +7,462.00000 | -1,188 | 0 |
| R4B | Rayk V11 | **30-2-0** | 0.9375 | +7,477.21875 | -1,188 | 0 |
| R4A | Andrew V12 | **26-6-0** | 0.8125 | +5,287.43750 | -2,590 | 0 |
| R4B | Andrew V12 | **26-6-0** | 0.8125 | +5,287.43750 | -2,590 | 0 |

Combined frozen R4B current-meta evidence including exact Kaito V27 from KEXP-011:

- Kaito V27: 25-7;
- Rayk V11: 30-2;
- Andrew V12: 26-6;
- combined: **81 wins / 15 losses / 0 ties over 96 development games**, zero errors.

The combined count is descriptive, not an independent statistical sample: all opponents use the same frozen development seed panel.

## Exact hard regimes

### Rayk V11

Only one seed loses, symmetrically in both seats:

- `163219477`: -1,188 / -1,188.

This seed is especially important because R4B also loses it **in both seats against Kaito V27** (-3,516 / -3,516). It is therefore the first exact multi-family recurrent hard regime.

### Andrew V12

Six losses:

- `150614441`: seat 0 only, -224; opposite seat wins +7,569;
- `393297156`: both seats, -2,533 / -2,533;
- `598340816`: seat 1 only, -2,590; opposite seat wins +5,341;
- `1422177419`: both seats, -1,678 / -2,328.

Cross-family comparison matters:

- `163219477`: hard for Kaito V27 + Rayk V11, but R4B narrowly beats Andrew (+392 / +204);
- `598340816`: loses both seats to V27, one seat to Andrew, but beats Rayk both seats;
- `1743398262`: loses both seats to V27 but beats Rayk and Andrew;
- `393297156` and `1422177419`: Andrew-specific symmetric losses while R4B beats V27 and Rayk.

## Interpretation

1. R4B/COK remains locally competitive with all three current public benchmark families; there is no evidence to migrate wholesale to Kaito, Rayk, or Andrew.
2. R4B terminal liquidation remains safe but does not change the W/L pattern against these frontier opponents.
3. `163219477` is the strongest multi-family diagnostic seed, but it must not become a target-specific patch.
4. Different public families expose different route/economic regimes. A next R4D mutation must address a **repeated mechanism**, not memorize seeds or opponent identities.
5. Complete replay analysis is required before defining R4D.

## Decision

**SCREEN COMPLETE — NO BASE MIGRATION, NO NEW CANDIDATE YET.**

Next: capture full Rayk/Andrew hard-regime replays in both orientations, compare checkpoint money/animals/hands/land/crop/inventory/market trajectories with the already captured V27 loss replays, and define one auditable late-game/continuation hypothesis only if the mechanism repeats across families.
