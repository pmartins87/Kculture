# HANDOFF — Kculture

Use this file as the first read in any new Kculture chat.

## Mission

Compete seriously for a **top-10 Kaggriculture prize**. Final submission deadline: 2026-09-30 23:59 UTC. `pmartins87/Kculture` is the source of truth and intentionally public.

## Mandatory first reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `experiments/KEXP-20260825-007-r4b-market-only-validation/README.md`
4. `experiments/KEXP-20260825-010-r4-development-failure-atlas/README.md`
5. `experiments/KEXP-20260825-011-r4-kaito-v27-strong-screen/README.md`
6. `research/CURRENT_META_ACQUISITION_20260826.md`
7. `research/R4B_MARKET_ONLY_PACKAGE_20260825.md`
8. `docs/SUBMISSION_LEDGER.md`
9. `official/UPSTREAM_LOCK.md`

Then inspect latest commits and GitHub Actions before changing code.

## Working rules

- Official engine facts outrank assumptions.
- Preserve public-agent source/version/path/hash/license provenance.
- Fresh-load file agents per episode.
- Compare deterministic seeds in both seats.
- Development is for iteration; validation only for an exact frozen candidate; held-out is reserved for later promotion/final selection.
- Never transfer an old validation claim onto changed code.
- Never promote from a few ladder games alone.
- Record every hosted submission and exact source/hash/package.
- Never commit credentials/private competitor code.
- Change one auditable strategic mechanism at a time.
- Advance autonomously; surface only material blockers/results.

## Current state

- **R0 COMPLETE for working purposes** — competition enrollment user-confirmed.
- **R1 PASS** — official starter parity.
- **R2 PASS** — deterministic 16 dev / 16 validation / 32 held-out laboratory.
- **R3 USER UPLOAD IN PROGRESS** — user reports manual Kaggle upload of the exact validated package has started. Do not mark PASS until hosted validation/submission ID/ladder entry are observed.
- **R4 ACTIVE.**
- **R4A frozen:** COK V8 (`779caae...`, SHA-256 `faf57412...`, Apache-2.0).
- **Full R4B rejected:** extra terminal physical DROP optimizer regressed directly vs R4A.
- **R4B market-only VALIDATION PASS:** frozen Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.
- Validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors.
- Package parity run `32919305800`: 4/4 full trajectories identical.
- Hosted archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`, 101557 bytes; packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`.
- **R4C ninth-cow:** NO PROMOTION.
- **KEXP-010 COMPLETE:** R4B 32-0 vs Seyamalam V21 and 32-0 vs Kaito V18 on all 16 development seeds × both seats; older panel is saturated.
- **KEXP-011 COMPLETE:** exact Kaito V27 V4 (public best 3090.1, `main.py` SHA `f48c2116...`) is a frontier opponent. R4A and R4B both 25-7; R4B mean +4396.84375 vs +4382.03125 for R4A. Do not migrate base.
- V27 loss seeds: `150614441` seat1 only; `1743398262`, `163219477`, `598340816` both seats.
- **Current-meta acquisition complete:** exact Rayk V11 `main.py` SHA `adc61ab1...` (best 2990.4 V11) and Andrew V12 SHA `df4e899a...` (best 2915.2 V12, Apache-2.0) acquired through public KaggleHub with no credentials.
- Strong screen run `32926727240`: R4A/R4B vs Rayk V11 and Andrew V12, all 16 dev seeds × both seats — running at last update.
- V27 frontier replay run `32926648674`: four frontier seeds × both seats — running/capturing at last update.
- **Held-out remains sealed 32/32.**

## Hosted submission checkpoint

The exact package the user is uploading must correspond to:

- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- `R4B-market-only-validated-v1`;
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`.

When Kaggle finishes processing:

1. record accepted/error state;
2. record submission ID and message;
3. preserve hosted validation/log evidence;
4. if accepted, record initial rating and later episodes;
5. reconcile hosted behavior with local assumptions;
6. update `docs/SUBMISSION_LEDGER.md`, `STATUS.md`, `ROADMAP.md`.

## Development continuation

Do not modify the frozen R4B candidate while the first hosted submission is being established.

Next engineering decision must use **multi-family frontier evidence**:

1. finish exact Rayk V11 / Andrew V12 strong screen (`32926727240`);
2. analyze complete V27 frontier replays (`32926648674`);
3. determine whether a common midgame/continuation/labor/market mechanism explains losses across more than one modern family;
4. only then create a separately named R4D development candidate;
5. R4D gets development evidence first and its own future validation if frozen.

Rayk V11 is benchmark-only until its license is independently verified; do not derive/redistribute its source. Andrew V12 is Apache-2.0 per public Kaggle page.
