# HANDOFF — Kculture

Use this file as the first read in a dedicated Kculture chat.

## Mission

Compete seriously for a **top-10 prize** in Kaggle's Kaggriculture simulation competition. Final submission deadline: 2026-09-30 23:59 UTC.

## Source of truth

This repository is authoritative for project state, decisions, laboratory tooling, competitive candidate code, experiments, submissions, tournament results, and frozen artifacts.

The repository intentionally remains **public** during active development. This is a deliberate project decision recorded in `docs/DECISION_PUBLIC_DEVELOPMENT.md`: the discovery/copying risk is accepted in exchange for unrestricted GitHub Actions capacity.

## Required first reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/COMPETITION.md`
4. `docs/EXPERIMENT_PROTOCOL.md`
5. `docs/SUBMISSION_LEDGER.md`
6. `official/UPSTREAM_LOCK.md`
7. `docs/OFFICIAL_MECHANICS_SNAPSHOT.md`
8. `research/PUBLIC_BENCHMARKS.md`
9. `docs/DECISION_PUBLIC_DEVELOPMENT.md`

Then inspect the repository tree, latest commits, and latest GitHub Actions runs before changing anything.

## Working rules

- Treat official mechanics as facts and strategic ideas as hypotheses until measured.
- Freeze environment/package/hash provenance for every promoted experiment.
- Preserve seeds, opponent versions, configs, both-seat outcomes, and full episode metrics.
- Never tune against held-out seeds; use them only for promotion/final selection.
- Fresh-load file-based agents per episode so global state cannot leak between games.
- Do not promote from a single ladder rating or a few favorable matches.
- Keep champion/archive/public benchmark opponents so every new agent must beat past strong versions.
- Record every Kaggle submission and the exact source/config/hash that produced it.
- Use the final two tracked submission slots as a strategic portfolio rather than redundant copies.
- Public third-party competition code may be used only with preserved license, source, commit, path, and SHA-256 provenance.
- Never commit credentials, private/unpublished competitor code, or redistribution-restricted private replay payloads.
- Advance as far as possible without unnecessary user micromanagement; surface only meaningful blockers, decisions, or results.

## Current phase

- **R1 PASS** — official starter reproduced exactly.
- **R2 PASS** — deterministic tournament laboratory closed on 2026-08-25.
- **R3 pending** — first hosted ladder submission still requires account-side Kaggle entry confirmation.
- **R4 ACTIVE** — strong public licensed architectures are being screened on frozen engine 1.32.7 to select the first economic base before Kculture-specific improvements.

## R2 closure evidence

Experiment: `experiments/KEXP-20260825-003-r2-closure/`.

GitHub Actions run `32859938870` established:

- 64 disjoint seeds: 16 dev / 16 validation / 32 held-out;
- 7 deterministic reference opponents;
- fresh-module isolation;
- zero closure-smoke runtime errors;
- hash-pinned strong public benchmark acquisition;
- frozen carrot reference vs COK V8 at dev seed `150614441`: 4389–148019 from seat 0 and 3665–151384 from seat 1.

The ~145.7k mean cash gap proves that R4 needs a scaled multi-worker, multi-resource architecture rather than starter micro-tuning.

## Immediate continuation

1. Finish `KEXP-20260825-004-r4-public-base-screen` and freeze the winning public architecture as `R4A-public-base`.
2. Make one auditable Kculture change at a time against that frozen base, using development seeds only during iteration.
3. Expand the opponent panel with independent strong public policies and archived promoted Kculture agents.
4. Use validation only after an experiment design is frozen; reserve held-out for promotion gates.
5. Confirm Kaggle competition entry, package the first strong hosted candidate, and reconcile hosted behavior for R3.
