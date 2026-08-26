# HANDOFF — Kculture

Use this file as the first read in any new Kculture chat.

## Mission

Compete seriously for a **top-10 Kaggriculture prize**. Final submission deadline: 2026-09-30 23:59 UTC. `pmartins87/Kculture` is the source of truth and intentionally public.

The objective is prize probability, not elegance. A user suggestion, assistant suggestion, public notebook, solver idea or attractive architecture is only a **hypothesis** until evidence supports it.

## Mandatory first reads

1. `STATUS.md`
2. `docs/PRIZE_FIRST_DECISION_POLICY.md`
3. `ROADMAP.md`
4. `docs/SUBMISSION_LEDGER.md`
5. `experiments/KEXP-20260826-017-r4d-macro-oracle/README.md`
6. `experiments/KEXP-20260826-016-r4d-default-context-diagnostic/README.md`
7. `experiments/KEXP-20260826-015-r4d-default-route-counterfactual/README.md`
8. `experiments/KEXP-20260826-014-r4-late-lifecycle-full-panel/README.md`
9. `research/FIRST_HOSTED_SCORE_DIAGNOSTIC_20260826.md`
10. `research/V27_FRONTIER_REPLAY_DIAGNOSTIC_20260826.md`
11. `research/CURRENT_META_ACQUISITION_20260826.md`
12. `research/R4B_MARKET_ONLY_PACKAGE_20260825.md`
13. `official/UPSTREAM_LOCK.md`

Then inspect latest commits and GitHub Actions before changing code.

## Working rules

- Official engine facts outrank assumptions.
- **Ideas are hypotheses, not directives.** Do not pivot because the user or assistant casually mentions a technique.
- Optimize expected top-10 probability, not elegance, novelty, or similarity to poker/other projects.
- Cheap falsification before expensive implementation; kill low-ceiling avenues quickly.
- Local public benchmarks are useful models, but hosted behavior is real calibration evidence.
- Preserve public-agent source/version/path/hash/license provenance.
- Fresh-load file agents per episode.
- Compare deterministic seeds in both seats.
- Development is for iteration; changed code gets fresh validation only after exact freeze; held-out is reserved for later promotion/final selection.
- Never transfer an old validation claim onto changed code.
- Never promote from a few ladder games alone.
- Record every hosted submission and exact source/hash/package.
- Never commit credentials/private competitor code.
- W/L/T is primary; money margin is secondary diagnostic evidence.
- Advance autonomously; surface only material blockers/results.

## Current hosted champion

`R4B-market-only-validated-v1`

- candidate `candidates/r4b_ablation_market_only.py`;
- Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- validation run `32918640409`: 32-0 vs Seyamalam; direct vs R4A 8-6-18, score 0.53125, mean +165.03125;
- package parity run `32919305800`: 4/4 complete trajectories identical;
- hosted archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- Kaggle filename `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- status **Complete** / green check;
- observed live score progression **161.6 → 135.7**.

This is a serious hosted/local contradiction: the same frozen agent is 81-15 on the controlled modern public development panel. Do not assume hosted recovery and do not spend submission #2 without material evidence.

## Exact modern development panel

Frozen R4B on all 16 development seeds × both seats:

- Kaito V27 V4 (`f48c2116...`): 25-7, mean +4,396.84375;
- Rayk V11 (`adc61ab1...`): 30-2, mean +7,477.21875;
- Andrew V12 (`df4e899a...`): 26-6, mean +5,287.43750;
- combined: **81-15-0 / 96**, score **0.84375**, mean +5,720.5, zero errors.

Rayk source is benchmark-only until license is independently verified. Kaito and Andrew are Apache-2.0 per their public pages.

## Critical methodological correction

KEXP-014's `8C/6S` category is a **physical farm state observed at step 672**. It must not be automatically equated to COK's hidden/static `8c6s_3q` route label.

COK's static selector is based on the first three public shops: Yarn placement and milk-support shops. KEXP-016 was rerun after catching this conflation and now records the static shop signal separately from observed physical state.

## KEXP-015 — COMPLETE / NO PROMOTION

Actions run `32966913616`.

- baseline: 81-15, mean +5,720.5;
- default→10C/4S: 81-15, mean +5,908.542;
- default→6C/8S: 78-18, mean +5,700.260.

10C/4S improves money, not aggregate W/L. On `163219477` it fixes Rayk while breaking Andrew. Universal reroute rejected.

## KEXP-016 — COMPLETE

Corrected Actions run `32968422225`, three jobs SUCCESS, development only.

Artifacts:

- Kaito `9606674181`, digest `928e1377e4b219e89ba498c22da46ad1cff75bd7a1d57017d6c2e2a86ea7f5f5`;
- Rayk `9606672044`, digest `436c092faeaab12d36391bed39e61f02e35f892b0a52bf541c3b8b17b07a277c`;
- Andrew `9606666107`, digest `d455a05223fc9c2a2adf50eb8086634f02da0deb15a14ea1e4ae5a1698b9f587`.

Public snapshots show opponent/state differences, but the small correlated corpus does not justify a production hardcoded selector. No promotion.

## KEXP-017 — COMPLETE / SOLVER BRANCH DEPRIORITIZED

The solver question was tested as a bounded value-of-information experiment, not adopted as project architecture.

Actions run `32972566807`: 96 contexts × 3 existing branches = 288 development games.

Perfect ex-post branch selection:

- Kaito: baseline 25-7 → oracle **25-7**;
- Rayk: 30-2 → **32-0**;
- Andrew: 26-6 → **26-6**;
- combined: **81-15 → 83-13**.

Thus even perfect knowledge among baseline/default→10C4S/default→6C8S fixes only **2 of 15 losses**, all Rayk. It cannot fix any Kaito/Andrew losses. This is too small a W/L ceiling to justify a solver pivot. Solver/search techniques remain optional bounded tools only when a specific experiment shows higher expected value.

## Exact continuation logic — prize-first

1. Prioritize the **hosted/local mismatch**. When Kaggle Episodes becomes accessible, capture submission ID, episode count, opponents, W/L/T, ratings and any execution errors/replays.
2. Broaden the exploratory development distribution with new documented seeds and additional current/diverse opponent families. Do not overfit the original 16×3 panel.
3. Focus on loss mechanisms that route selection cannot fix, especially the repeated late-horizon reversals against Kaito/Andrew.
4. Search new strategic action families: labor timing, production stop horizon, harvest/drop throughput, shed bottlenecks, market timing/product mix, dynamic response to public opponent state. Use cheap counterfactual tests first.
5. Method is secondary: heuristics, search, evolutionary methods, ML, planning or bounded optimization are all acceptable if evidence says they improve prize probability.
6. Freeze only a materially better cross-family W/L candidate before fresh validation.
7. Keep R4B hosted package immutable until replacement promotion.
8. Keep all 32 held-out seeds sealed.
