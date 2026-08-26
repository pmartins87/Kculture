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
5. `experiments/KEXP-20260826-018-live-meta-radar/README.md`
6. `experiments/KEXP-20260826-019-live-meta-longitudinal/README.md`
7. `research/LATE_ANIMAL_TERMINAL_VALUE_20260826.md`
8. `experiments/KEXP-20260826-017-r4d-macro-oracle/README.md`
9. `experiments/KEXP-20260826-016-r4d-default-context-diagnostic/README.md`
10. `experiments/KEXP-20260826-015-r4d-default-route-counterfactual/README.md`
11. `experiments/KEXP-20260826-014-r4-late-lifecycle-full-panel/README.md`
12. `research/FIRST_HOSTED_SCORE_DIAGNOSTIC_20260826.md`
13. `research/V27_FRONTIER_REPLAY_DIAGNOSTIC_20260826.md`
14. `official/UPSTREAM_LOCK.md`

Then inspect latest commits and GitHub Actions before changing code.

## Working rules

- Official engine facts outrank assumptions.
- **Ideas are hypotheses, not directives.** Do not pivot because the user or assistant casually mentions a technique.
- Optimize expected top-10 probability, not elegance, novelty, or similarity to poker/other projects.
- Cheap falsification before expensive implementation; kill low-ceiling avenues quickly.
- Local public benchmarks are useful models, but hosted behavior is real calibration evidence.
- Official live-ladder Episode datasets are now a first-class meta source because they contain actual current high-rating play, including private agents.
- Preserve public-agent source/version/path/hash/license provenance.
- Fresh-load file agents per episode.
- Compare deterministic seeds in both seats.
- Development is for iteration; changed code gets fresh validation only after exact freeze; held-out is reserved for later promotion/final selection.
- Never transfer an old validation claim onto changed code.
- Never promote from replay correlation alone; use replay mining to generate hypotheses and controlled matches to test them.
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

These remain controlled regressions/benchmarks, not a calibrated model of the current hosted field.

## Route/solver branch — closed for now

KEXP-015 fixed route overrides did not improve aggregate W/L. KEXP-016 corrected the physical-state/internal-route conflation. KEXP-017 then measured the maximum possible value of perfect ex-post selection among the three existing macro branches:

- Kaito 25-7 → 25-7;
- Rayk 30-2 → 32-0;
- Andrew 26-6 → 26-6;
- combined **81-15 → 83-13**.

Only two Rayk losses are fixable by perfect branch selection. A route solver is therefore **deprioritized**. Solver/search methods remain optional tools only when tied to a higher-ceiling subproblem.

## KEXP-018 — official live-meta radar: COMPLETE

This is the most important recent change in research direction.

Official public datasets:

- `kaggle/kaggriculture-episodes-index`;
- `kaggle/kaggriculture-episodes-YYYY-MM-DD`.

They can be downloaded through `kagglehub` without credentials and contain actual current ladder replays, including private agents. Large raw episodes are temporary; compact reports are preserved.

Expanded top-20 screen on official date **2026-08-25**:

- Actions run `32977177944` — SUCCESS;
- artifact `9609951191`;
- ZIP SHA-256 `ec15ee2b2d5827e517af85e7018a7dcfe79a0b94f78ec574c17f30893b5b6964`;
- 688 daily episodes;
- median `avg_score` 2761.313513;
- top `avg_score` 3069.552857;
- selected top20 range 3069.552857→3056.613226;
- top band consisted of `Crop Dusta` and `Ryo Hasegawa`, 20 player-games each;
- wins in selected episodes: Crop Dusta 14, Ryo Hasegawa 6.

Top-20 winners averaged:

- herd reduction step 672→719: **5.8 animals**;
- losers: **1.25 animals**;
- 672-695: only **3.85 FEED + 0.05 CARE** per winner on average;
- 696-718: **0 FEED + 0 CARE**;
- terminal farm structures were heterogeneous, arguing against one fixed cow/sheep template.

The herd-exit effect is concentrated in the high-winning Crop Dusta family, so it is **not yet a universal causal rule**.

## Exact late-animal mechanics — frozen theorem

See `research/LATE_ANIMAL_TERMINAL_VALUE_20260826.md`.

From official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`:

- step 695 is the final end-of-day refresh;
- steps 696-718 have no later production refresh;
- animals escape after two successive unfed end-of-day refreshes;
- base animal production does not require FEED if the animal survives;
- FEED gates an existing `pending_care_bonus` and can prevent escape;
- CARE made during steps 672-695 banks a bonus only **after** the final scheduled production check, so it has zero direct terminal-production value;
- COK/R4B still issues roughly 8-10 CARE and 9-10 FEED actions in 672-695 depending on route, then zero of both during 696-718.

Implication: the most defensible new candidate region is a **state-aware penultimate-day stop-investment/throughput overlay**, not blanket animal starvation. CARE actions need profitable reallocation; FEED may be suppressed only when survival and existing-bonus value are provably unnecessary.

## KEXP-019 — longitudinal live-meta falsification: RUNNING/QUEUED

Actions run `33019193497`.

Predeclared top-10 official Episode screens for:

- 2026-08-23;
- 2026-08-24;
- 2026-08-25.

Target: 30 official episodes / 60 player-games. Purpose: test whether late herd exit / stop-investment repeats across dates/families before policy mutation.

Do not change the pass criteria after results. A late-exit counterfactual becomes eligible only if the pattern generalizes by the predeclared rules in the experiment README.

## Static COK vs live-meta gap audit

Run `33019034050` — SUCCESS; artifact `9625740899`, ZIP digest `4dde4e4a178bf5f7e22ba38ca42498a4f249751c9d0a6d642c31301c8ee159bf`.

Exact COK SHA was verified. Route tapes confirm the gap observed in actual R4B replays: COK continues ~8-9 CARE and ~9-10 FEED in 672-695, but none in 696-718.

## Exact continuation logic — prize-first

1. **Finish KEXP-019** and apply its predeclared longitudinal falsification rules.
2. If late stop-investment fails temporal/family generalization, deprioritize it despite the attractive KEXP-018 correlation.
3. If it survives, create a narrow development-only KEXP-020 candidate based on exact mechanics, not team identity:
   - preserve R4B before the late window;
   - reallocate terminally useless CARE to immediately realizable extraction when safe;
   - suppress FEED only when observed state proves no remaining survival/pending-bonus production value;
   - do not blindly starve all animals.
4. Test any KEXP-020 change with W/L primary across the full diverse development panel, both seats; broaden exploratory distribution where useful.
5. In parallel, continue mining official top-ladder Episodes for general state/action patterns. Episode/team IDs are research labels only, never deployable features.
6. A larger dynamic final-2/3-day task scheduler becomes eligible only if the narrow overlay shows meaningful headroom or live-replay evidence clearly supports the opportunity cost.
7. Freeze only a materially better cross-family candidate before fresh validation.
8. Keep R4B hosted package immutable until replacement promotion.
9. Keep all **32 held-out seeds sealed**.
