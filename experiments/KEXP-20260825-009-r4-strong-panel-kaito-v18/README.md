# KEXP-20260825-009 — Kaito V18 strong-panel preservation

## Purpose

Check whether the frozen validated `R4B-market-only-validated-v1` improvement generalizes beyond the COK/Seyamalam development pair, without opening validation or held-out seeds.

## Opponent provenance

- family: Kaito Fukami public V18 / C20 exact-replication control
- mirrored public source: `Seyamalam/Kaggriculture`
- source commit: `8b8c421eb10634c756583ce10c75189f50c83a72`
- source path: `agents/candidate_v7_public_v18.py`
- SHA-256: `603175d39f2857cbd618dc8f5ac9411e9fd234e3142777ec203342172f05a50e`
- license: Apache-2.0
- local artifact: `artifacts/public_opponents/kaito_v18_public_8b8c421.py`

The mirror's `THIRD_PARTY_NOTICES.md` states that this is an exact copy of the public C20 artifact and attributes the underlying V18 policy to Kaito Fukami's public Kaggle notebook.

## Protocol

GitHub Actions run `32919635267`.

Use the first 8 frozen development seeds, both seats, `kaggle-environments==1.32.7`.

A. R4A / COK V8 control vs Kaito V18.
B. Frozen validated market-only candidate vs Kaito V18.

No validation or held-out seed is opened.

## Results

### R4A control vs Kaito V18

- 16 episodes
- 14 wins / 2 losses / 0 ties
- score rate: 0.875
- mean money delta: +20,732.750
- min delta: -1,357
- max delta: +39,362
- errors: 0

### R4B market-only vs Kaito V18

- 16 episodes
- **16 wins / 0 losses / 0 ties**
- score rate: **1.000**
- mean money delta: **+22,210.375**
- min delta: +5,575
- max delta: +39,362
- errors: 0

The two R4A losses occurred on development seed `583180324`, both seats (`-1,357` and `-1,327`). The market-only candidate flipped both to wins (`+5,575` and `+5,605`) while preserving the other wins.

## Interpretation

**GENERALIZATION SUPPORT.** The minimal final-market liquidation change improved both win count and mean delta against a third, independently attributed public policy family. This does not create a new validation claim, because the run is development-only, but it materially reduces the risk that the R4B gain was specific to Seyamalam.

The frozen hosted-submission candidate remains unchanged. Held-out remains sealed.
