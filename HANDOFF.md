# HANDOFF — Kculture

Use this file as the first read in any new Kculture chat.

## Mission

Compete seriously for a **top-10 Kaggriculture prize**. Final submission deadline: 2026-09-30 23:59 UTC. `pmartins87/Kculture` is the source of truth and intentionally public.

## Mandatory first reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/SUBMISSION_LEDGER.md`
4. `research/FIRST_HOSTED_SCORE_DIAGNOSTIC_20260826.md`
5. `experiments/KEXP-20260825-007-r4b-market-only-validation/README.md`
6. `experiments/KEXP-20260825-010-r4-development-failure-atlas/README.md`
7. `experiments/KEXP-20260825-011-r4-kaito-v27-strong-screen/README.md`
8. `experiments/KEXP-20260826-012-r4-current-meta-strong-screen/README.md`
9. `experiments/KEXP-20260826-013-r4-current-meta-hard-replays/README.md`
10. `research/V27_FRONTIER_REPLAY_DIAGNOSTIC_20260826.md`
11. `research/CURRENT_META_ACQUISITION_20260826.md`
12. `research/R4B_MARKET_ONLY_PACKAGE_20260825.md`
13. `official/UPSTREAM_LOCK.md`

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
- **R3 PASS for delivery/hosted validation:** Kaggle UI shows the exact first package as **Complete** with a green check. First observed live score is **161.6** at ~2026-08-26 04:37 UTC. This is a serious online calibration contradiction because valid simulation submissions initialize at rating 600; it is not the expected ~3000 benchmark regime and must be diagnosed at episode level.
- **R4 ACTIVE.**
- **R4A frozen:** COK V8 (`779caae...`, SHA-256 `faf57412...`, Apache-2.0).
- **Full R4B rejected:** extra terminal physical DROP optimizer regressed directly vs R4A.
- **R4B market-only VALIDATION PASS:** frozen Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.
- Validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125, zero errors.
- Package parity run `32919305800`: 4/4 full trajectories identical.
- Hosted archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`, 101557 bytes; packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`.
- Hosted filename: `Kculture_R4B_market_only_validated_v1_submission.tar.gz`; submission ID and hosted episode count have not yet been observed.
- **R4C ninth-cow:** NO PROMOTION.
- **KEXP-010 COMPLETE:** R4B 32-0 vs Seyamalam V21 and 32-0 vs Kaito V18 on all 16 development seeds × both seats; old panel saturated.
- **KEXP-011 COMPLETE:** exact Kaito V27 V4 (public best 3090.1, SHA `f48c2116...`) — R4B 25-7, mean +4396.84375. No base migration.
- **KEXP-012 COMPLETE:** exact Rayk V11 (best 2990.4, SHA `adc61ab1...`) — R4B 30-2; exact Andrew V12 (best 2915.2, SHA `df4e899a...`) — R4B 26-6. Combined exact-current panel with V27: **81-15-0 / 96 dev games**, zero errors.
- Rayk hard regime: only `163219477`, both seats. This same seed also loses both seats to V27, so it is the strongest multi-family recurrence.
- Andrew hard regimes: `150614441` one seat, `393297156` both, `598340816` one seat, `1422177419` both.
- **V27 frontier replay diagnostic COMPLETE:** on symmetric V27 losses (`1743398262`, `163219477`, `598340816`) R4B is still ahead at step 672 but loses 2.7k–4.5k of relative value in the final ~47 turns.
- **KEXP-013 COMPLETE:** Actions `32927303182`, 10 exact Rayk/Andrew hard replays, development only, zero runtime errors. In all **8 captured losing games**, R4B is ahead at step 672 (mean +2007.5) and finishes at mean -1782.75: mean late swing about -3790.25.
- New replay-level clue from KEXP-013: at step 672 the eight losing R4B states average **13 strawberries with `max_lifespan_step=672`** plus 6.5 expiring at 696; by step 696 R4B averages **13.5 weeds vs 4.625** for opponents and only 16.25 productive crops vs 25.25 opponent wheat. In steps 696–718 R4B averages 8 hands vs 9.75, 18.5 harvest actions vs 29.75, 8 DROP vs 13.75, and 139.5 requested SELL units vs 222.75. This is currently a strong mechanistic R4D lead, not yet a promoted causal claim.
- **Held-out remains sealed 32/32.**

## First hosted submission checkpoint

Exact identity:

- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- `R4B-market-only-validated-v1`;
- candidate Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- package-build Git SHA `29a883aba3df6347d72e321c9970c9694e0b6fa0`;
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- Kaggle UI status: **Complete**;
- first displayed score: **161.6**;
- screenshot observation time: ~2026-08-26 04:37 UTC;
- submission ID: unknown;
- episode count: unknown.

Interpretation: ~3000 was the strength/rating regime of mature public benchmarks used for local screening, not an immediate submission initialization. Kaggle initializes valid simulation submissions at `mu0=600`. A display of 161.6 means the hosted rating has already moved sharply downward. Treat this as evidence that local calibration is incomplete until hosted episodes are reconciled.

Next hosted actions when episode access/ID becomes available:

1. capture submission ID and episode list;
2. record W/L/T, opponent ratings and score trajectory if available;
3. download/inspect hosted replay/log evidence;
4. compare hosted action trajectory with the exact packaged local agent;
5. determine whether the failure is matchup/meta distribution, hosted behavior mismatch, or a known strategic frontier;
6. do not spend a second submission slot merely to react to one rating snapshot.

## Development continuation

Keep the frozen R4B candidate immutable. Development proceeds as separately named R4D candidates.

Priority now:

1. formalize the KEXP-013 late-game causal signature across the full 16-seed development panel, including wins, so the strawberry-expiry/weed/throughput signal is tested as a predictor rather than fitted to losses;
2. compare late checkpoints 672/696/708/717/718 for Kaito V27, Rayk V11 and Andrew V12;
3. test the narrowest legal-state-observable intervention first: prevent/recover the final-day productive-acreage collapse caused by expiring crops/weeds without changing successful opening/midgame behavior;
4. separately ablate labor/harvest/DROP throughput; do not bundle it into the first crop-lifecycle intervention;
5. R4D gets all-16-seed development evidence first and a fresh validation gate only if frozen;
6. never key R4D to seed ID or opponent identity.

Rayk V11 remains benchmark-only until license is independently verified; do not derive/redistribute its source. Andrew V12 and Kaito V27 are Apache-2.0 per public Kaggle pages.
