# HANDOFF — Kculture

Use this file as the first read in a dedicated Kculture chat.

## Mission

Compete seriously for a **top-10 prize** in Kaggle's Kaggriculture simulation. Final submission deadline: 2026-09-30 23:59 UTC. The repository `pmartins87/Kculture` is the source of truth and intentionally remains public during development.

## First reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/COMPETITION.md`
4. `docs/EXPERIMENT_PROTOCOL.md`
5. `docs/SUBMISSION_LEDGER.md`
6. `official/UPSTREAM_LOCK.md`
7. `research/PUBLIC_BENCHMARK_SNAPSHOT_20260825.md`

Then inspect latest commits and GitHub Actions before changing anything.

## Working rules

- Facts from the official engine outrank assumptions.
- Preserve source/commit/path/hash/license for third-party public agents.
- Fresh-load file agents per episode.
- Compare both seats and deterministic seeds.
- Development is for iteration; validation is only for frozen candidates; held-out is reserved for later promotion/final selection.
- Never tune a changed candidate on results from a validation run belonging to an earlier frozen candidate.
- Do not promote from a few ladder games alone.
- Record every hosted submission and exact source/config/hash.
- Never commit credentials or private/unpublished competitor code.
- Advance autonomously and surface only meaningful blockers/results.

## Current state

- **R1 PASS** — official starter parity.
- **R2 PASS** — deterministic lab with 16 dev / 16 validation / 32 held-out seeds.
- **R3 pending** — first hosted ladder submission/account-side Kaggle confirmation.
- **R4 ACTIVE**.
- **R4A frozen:** COK V8 (`779caae...`, SHA-256 `faf57412...`, Apache-2.0), selected 14-2 over Seyamalam V21 on first 8 dev seeds × both seats.
- **Full terminal R4B rejected:** 16-0 vs Seyamalam but only 5-11 vs R4A, mean -1.625; failed predeclared direct gate.
- **Market-only terminal candidate frozen for validation:** 16-0 vs Seyamalam and 5-3-8 vs R4A, mean +12 on development. Frozen Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.
- **KEXP-007 validation running:** Actions run `32918640409`, all 16 validation seeds, both seats, 3 matchup blocks.
- **Held-out remains sealed.**

## Exact active validation gate

`experiments/KEXP-20260825-007-r4b-market-only-validation/README.md`

PASS requires:

1. zero runtime errors;
2. market-only direct score vs R4A >= 0.50;
3. direct mean money delta vs R4A >= 0;
4. market-only wins vs Seyamalam >= R4A-control wins;
5. market-only mean delta vs Seyamalam >= R4A-control mean.

Do not alter the candidate after seeing validation results and then claim the old validation applies to the new code.

## Packaging

`tools/build_r4b_market_only_submission.py` prepares a self-contained archive from the hash-pinned COK V8 source plus the Kculture market-only overlay. If KEXP-007 passes, require full-trajectory action parity between the laboratory wrapper and packaged root `main.py` before hosted submission.

## Next independent development hypothesis

`KEXP-20260825-008-r4c-guarded-ninth-cow` is prepared but not executed. It is development-only and toggles one already-implemented guarded ninth-cow branch. It must not use validation or held-out seeds.

## External benchmark targets

High-priority dated public targets: Kaito V27 V4 (~3090.1 snapshot), Rayk V11 (~2990.4 best snapshot), Andrew V12 (~2915.2), Flexona V59 (~2767.3). Exact Kaggle notebook pull requires `KAGGLE_API_TOKEN` and is prepared as a manual, secret-only workflow.
