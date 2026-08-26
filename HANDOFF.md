# HANDOFF — Kculture

Use this file as the first read in a dedicated Kculture chat.

## Mission

Compete seriously for a **top-10 prize** in Kaggle's Kaggriculture simulation. Final submission deadline: 2026-09-30 23:59 UTC. `pmartins87/Kculture` is the source of truth and intentionally remains public during development.

## First reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `experiments/KEXP-20260825-007-r4b-market-only-validation/README.md`
4. `research/R4B_MARKET_ONLY_PACKAGE_20260825.md`
5. `docs/SUBMISSION_LEDGER.md`
6. `official/UPSTREAM_LOCK.md`
7. `research/PUBLIC_BENCHMARK_SNAPSHOT_20260825.md`

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

- **R1 PASS** — official starter parity.
- **R2 PASS** — deterministic lab with 16 dev / 16 validation / 32 held-out seeds.
- **R3 pending only on hosted submission/account authentication.**
- **R4 ACTIVE.**
- **R4A frozen:** COK V8 (`779caae...`, SHA-256 `faf57412...`, Apache-2.0), selected 14-2 over Seyamalam V21 on first 8 dev seeds × both seats.
- **Full R4B rejected:** 16-0 vs Seyamalam but 5-11 vs R4A; extra physical terminal DROP replacement was harmful.
- **R4B market-only VALIDATION PASS:** exact Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.
- Validation run `32918640409`: R4A control vs Sey 30-2; market-only vs Sey 32-0; market-only vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors.
- **Package parity PASS:** run `32919305800`, 4/4 full trajectories identical.
- Submission archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`, 101557 bytes; packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`.
- `R4B-market-only-validated-v1` is **HOSTED_SUBMISSION_READY**.
- **Held-out remains sealed 32/32.**

## R3 next step

`.github/workflows/r3-first-hosted-submission.yml` is manual-only. It:

1. requires repository secret `KAGGLE_API_TOKEN`;
2. checks `kaggle competitions list --group entered` contains Kaggriculture;
3. rebuilds the exact deterministic archive;
4. rejects any archive hash other than `19cc08d2...c53117`;
5. submits `kaggle competitions submit kaggriculture -f ...`;
6. preserves the hosted submission list for the ledger.

Do not expose credentials in source or chat. If API auth is not configured, the same exact tar.gz may be uploaded manually in the Kaggle UI after joining the competition.

## Development continues independently

- `KEXP-20260825-008-r4c-guarded-ninth-cow` is currently being executed on development seeds only (Actions run `32919545606`).
- Kaito public V18/C20 exact control was added as a third hash-pinned public family (`603175d3...a50e`, Apache-2.0) and a development preservation panel is running.
- Validation/held-out must not be used by these hypotheses unless a later candidate is independently frozen and predeclared.

## External benchmark targets

High-priority newer targets remain Kaito V27/V42+, Rayk V11, Andrew V12 and Flexona V59. Exact Kaggle notebook pull requires authenticated `KAGGLE_API_TOKEN`; the acquisition workflow is manual/secret-only.
