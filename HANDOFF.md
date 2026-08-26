# HANDOFF — Kculture

Use this file as the first read in any new Kculture chat.

## Mission

Compete seriously for a **top-10 Kaggriculture prize**. Final submission deadline: 2026-09-30 23:59 UTC. `pmartins87/Kculture` is the source of truth and intentionally public.

## Mandatory first reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/SUBMISSION_LEDGER.md`
4. `research/FIRST_HOSTED_SCORE_DIAGNOSTIC_20260826.md`
5. `experiments/KEXP-20260826-014-r4-late-lifecycle-full-panel/README.md`
6. `experiments/KEXP-20260826-015-r4d-default-route-counterfactual/README.md`
7. `experiments/KEXP-20260826-012-r4-current-meta-strong-screen/README.md`
8. `experiments/KEXP-20260826-013-r4-current-meta-hard-replays/README.md`
9. `research/V27_FRONTIER_REPLAY_DIAGNOSTIC_20260826.md`
10. `research/CURRENT_META_ACQUISITION_20260826.md`
11. `research/R4B_MARKET_ONLY_PACKAGE_20260825.md`
12. `official/UPSTREAM_LOCK.md`

Then inspect latest commits and GitHub Actions before changing code.

## Working rules

- Official engine facts outrank assumptions.
- Preserve public-agent source/version/path/hash/license provenance.
- Fresh-load file agents per episode.
- Compare deterministic seeds in both seats.
- Development is for iteration; changed code gets fresh validation only after exact freeze; held-out is reserved for later promotion/final selection.
- Never transfer an old validation claim onto changed code.
- Never promote from a few ladder games alone.
- Record every hosted submission and exact source/hash/package.
- Never commit credentials/private competitor code.
- Change one auditable strategic mechanism at a time.
- W/L/T is the primary competition-aligned objective; money margin is secondary diagnostic evidence.
- Advance autonomously; surface only material blockers/results.

## Current hosted champion

`R4B-market-only-validated-v1`

- candidate: `candidates/r4b_ablation_market_only.py`;
- Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125;
- package parity run `32919305800`: 4/4 complete trajectories identical;
- hosted archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- Kaggle filename `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- status **Complete** / green check;
- first observed live score **161.6**.

Interpretation: mature public-agent ratings around 2900–3100 are benchmark-strength snapshots, not a new submission's initial rating. A valid simulation submission initializes around 600, so 161.6 is a real negative hosted calibration signal. Keep diagnosing hosted episodes when Kaggle exposes them, but do not spend a new submission merely to react to the score.

## Exact modern development panel

Frozen R4B on all 16 development seeds × both seats:

- Kaito V27 V4 (`f48c2116...`): 25-7, mean +4,396.84375;
- Rayk V11 (`adc61ab1...`): 30-2, mean +7,477.21875;
- Andrew V12 (`df4e899a...`): 26-6, mean +5,287.43750;
- combined: **81-15-0 / 96**, score **0.84375**, mean +5,720.5, zero errors.

Rayk source is benchmark-only until license is independently verified. Kaito and Andrew are Apache-2.0 per their public pages.

## KEXP-014 result — important correction

Actions run `32931921583` completed successfully, 96 development games, zero errors.

The loss-focused KEXP-013 clue that expiring strawberries → weeds → productive-acreage collapse was **not** supported as a generic causal rule on the full win/loss panel. Do not implement generic weed cleanup from that hypothesis.

The strongest structural split was production route at step 672:

- 6C/12S: 22-2 / 24, score 0.91667, mean +8,174.333;
- 10C/4S: 45-6 / 51, score 0.88235, mean +6,301.647;
- **8C/6S: 12-7 / 19, score 0.63158, mean +1,143.0, mean 672→terminal swing -3,820.421**.

The 8C/6S weakness reproduces against Kaito, Rayk and Andrew.

Frozen COK V8 source confirms that final 8C/6S is the default route once three shops are visible and the first-three prefix contains neither Yarn nor early milk-support. COK V8 already has weed replay/passive repair. This selector is the current causal target.

## KEXP-015 — currently running

Predeclared fixed counterfactual screen:

- **R4D-A:** `candidates/r4d_default_to_10c4s.py`, blob `a125e878ef262141cd2fd452a9f4edab42dfbae5`;
- **R4D-B:** `candidates/r4d_default_to_6c8s.py`, blob `34b66bc18471ffbb7d35f24f2ac39451bc8cb851`.

Both leave the provisional opening untouched until at least three shops are visible. Only then, if frozen COK V8's original selector still resolves to the default 8C/6S route, they substitute the target route. All other route cases, physical recovery controllers, front-running, and the validated R4B terminal market-only controller stay unchanged.

Actions run: **32966913616**.

Matrix: 2 candidates × Kaito V27/Rayk V11/Andrew V12 × all 16 development seeds × both seats = 192 candidate episodes total. Validation and held-out are not touched.

Predeclared baseline to beat:

- overall score 0.84375 and mean +5,720.5;
- baseline 8C/6S exposure set 12-7;
- zero errors mandatory;
- no severe new family regression.

## Exact continuation logic

1. Finish run `32966913616`; download all six artifacts and pair by opponent/seed/seat against KEXP-014.
2. Separate baseline-defined 8C/6S exposure rows from unaffected rows; verify that any gain is actually caused by the intended trigger.
3. If one universal override passes the predeclared gate, freeze that exact candidate and only then open a fresh validation gate against the modern panel.
4. If neither passes, do **not** broaden changes. Build a contextual default-route selector from legal public observables at the third-shop boundary, using paired counterfactual evidence to choose features/thresholds.
5. Keep R4B hosted package immutable until replacement promotion.
6. Keep all 32 held-out seeds sealed.
