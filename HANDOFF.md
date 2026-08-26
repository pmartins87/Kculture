# HANDOFF — Kculture

Use this file as the first read in a dedicated Kculture chat.

## Mission

Compete seriously for a **top-10 prize** in Kaggle's Kaggriculture simulation. Final submission deadline: 2026-09-30 23:59 UTC. `pmartins87/Kculture` is the source of truth and intentionally remains public during development.

## First reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `experiments/KEXP-20260825-007-r4b-market-only-validation/README.md`
4. `research/R4B_MARKET_ONLY_PACKAGE_20260825.md`
5. `experiments/KEXP-20260825-010-r4-development-failure-atlas/README.md`
6. `docs/SUBMISSION_LEDGER.md`
7. `official/UPSTREAM_LOCK.md`

Then inspect latest commits and GitHub Actions before changing anything.

## Working rules

- Official engine facts outrank assumptions.
- Preserve source/commit/path/hash/license for public agents.
- Fresh-load file agents per episode.
- Compare both seats and deterministic seeds.
- Development is for iteration; validation only for frozen candidates; held-out is reserved for later promotion/final selection.
- Never tune changed code on an earlier candidate's validation and then reuse that validation claim.
- Do not promote from a few ladder games alone.
- Record every hosted submission and exact source/config/hash.
- Never commit credentials/private competitor code.
- Advance autonomously and surface only meaningful blockers/results.

## Current state

- **R0 working intake complete:** competition entry is user-confirmed; API reconciliation will occur on authenticated submission.
- **R1 PASS** — official starter parity.
- **R2 PASS** — deterministic lab with 16 dev / 16 validation / 32 held-out seeds.
- **R3 READY TO SUBMIT:** only the authenticated Kaggle upload/hosted reconciliation remains.
- **R4 ACTIVE.**
- **R4A frozen:** COK V8 (`779caae...`, SHA-256 `faf57412...`, Apache-2.0).
- **Full R4B rejected:** 16-0 vs Seyamalam but 5-11 vs R4A; extra physical terminal DROP replacement was harmful.
- **R4B market-only VALIDATION PASS:** exact Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.
- Validation run `32918640409`: R4A control vs Sey 30-2; market-only vs Sey 32-0; market-only vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors.
- **Package parity PASS:** run `32919305800`, 4/4 full trajectories identical.
- Submission archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`, 101557 bytes; packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`.
- `R4B-market-only-validated-v1` is **HOSTED_SUBMISSION_READY**.
- **KEXP-008 ninth cow:** NO PROMOTION. 14-2 vs Seyamalam exactly matched R4A; direct vs R4A 4-4-8, mean zero.
- **KEXP-009 Kaito V18:** generalization support. R4A 14-2 / +20,732.75; market-only 16-0 / +22,210.375 on the same first 8 dev seeds × both seats.
- **KEXP-010 failure atlas:** running all 16 development seeds across R4A/Seyamalam/Kaito, 160 games total.
- **Held-out remains sealed 32/32.**

## R3 next step

`.github/workflows/r3-first-hosted-submission.yml` is manual-only. It:

1. requires repository secret `KAGGLE_API_TOKEN`;
2. verifies Kaggriculture appears under entered competitions;
3. rebuilds the exact deterministic archive;
4. rejects any archive hash other than `19cc08d2...c53117`;
5. submits the agent;
6. preserves the hosted submission list for the ledger.

The user has confirmed competition enrollment. Do not expose credentials in source or chat. If API auth is not configured, the same exact tar.gz may be uploaded manually in the Kaggle UI.

## Development continuation

`KEXP-20260825-010-r4-development-failure-atlas` is the current development diagnostic. It must be interpreted before creating another physical/economic strategy mutation. Use only recurring patterns from development evidence, change one mechanism at a time, and give every changed candidate a new experiment identity.

## External benchmark targets

High-priority newer targets remain Kaito V27/V42+, Rayk V11, Andrew V12 and Flexona V59. Exact Kaggle notebook pull requires authenticated `KAGGLE_API_TOKEN`; the acquisition workflow is manual/secret-only.
