# HANDOFF — Kculture

Use this file as the first read in a dedicated Kculture chat.

## Mission

Compete seriously for a **top-10 prize** in Kaggle's Kaggriculture simulation competition. Final submission deadline: 2026-09-30 23:59 UTC.

## Source of truth

This repository is authoritative for public-safe project state, decisions, laboratory tooling, experiments, submissions, tournament results, and frozen artifacts. Competitive candidate source must remain private during active development unless deliberate publication is chosen and Kaggle code-sharing requirements are satisfied.

## Required first reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/COMPETITION.md`
4. `docs/EXPERIMENT_PROTOCOL.md`
5. `docs/SUBMISSION_LEDGER.md`
6. `official/UPSTREAM_LOCK.md`
7. `docs/OFFICIAL_MECHANICS_SNAPSHOT.md`
8. `research/PUBLIC_BENCHMARKS.md`

Then inspect the current repository tree, latest commits, and latest GitHub Actions runs before changing anything.

## Working rules

- Treat official mechanics as facts and strategic ideas as hypotheses until measured.
- Freeze upstream environment/package/hash provenance for every promoted experiment.
- Preserve seeds, opponent versions, configs, both-seat outcomes, and full episode metrics.
- Never tune against held-out seeds; use them only for promotion/final selection.
- Fresh-load file-based agents per episode so global state cannot leak between games.
- Do not promote from a single ladder rating or a few favorable matches.
- Keep champion/archive/public benchmark opponents so every new agent must beat past strong versions.
- Record every Kaggle submission and the exact source/config/hash that produced it.
- Use the final two tracked submission slots as a strategic portfolio rather than redundant copies.
- Do not commit private competitive policy source to this public repository while the competition is active.
- Advance as far as possible without unnecessary user micromanagement; surface only meaningful blockers, decisions, or results.

## Current phase

- **R1 PASS** — official starter reproduced exactly.
- **R2 PASS** — deterministic tournament laboratory closed on 2026-08-25.
- **R3 pending** — first hosted ladder submission requires Kaggle account-side entry confirmation.
- **R4 preparation** — serious economic candidate development is gated on private source storage because `pmartins87/Kculture` is public.

## R2 closure evidence

Experiment: `experiments/KEXP-20260825-003-r2-closure/`.

Key evidence from GitHub Actions run `32859938870` on `kaggle-environments==1.32.7`:

- 64 disjoint seeds: 16 dev / 16 validation / 32 held-out;
- 7 deterministic reference opponents;
- fresh-module isolation;
- zero closure-smoke runtime errors;
- strong public COK V8 artifact hash verified;
- frozen carrot reference vs COK V8 at dev seed `150614441`: 4389–148019 from seat 0 and 3665–151384 from seat 1.

The ~145.7k mean cash gap is the current calibration target: R4 requires a different production architecture, not starter micro-tuning.

## Immediate continuation

1. Check `STATUS.md` for whether private candidate storage and Kaggle entry have been resolved.
2. If private storage is available, implement R4 candidate work there while keeping only safe metrics/provenance in this repository.
3. Build multi-worker/multi-resource economics with explicit land/hire payback, livestock/crop mix, shop-demand routing, market-aware sales, failure recovery, and terminal liquidation.
4. Iterate only on development seeds; freeze experiment before validation; reserve held-out for promotion.
5. Package/submit the first hosted candidate when account access is confirmed, then reconcile hosted episodes against local behavior for R3.
