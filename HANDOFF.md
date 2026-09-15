# HANDOFF — Kculture

> **Current update — 2026-09-15:** CR089 is complete and failed population compatibility. Static C5/C5+M6S1 are closed as direct competitive backbones. The current gate is CR090 / H9 public-shop adaptive marginal expansion.

Use this file as the **first read in any new Kculture chat**.

## Mission

Compete seriously for a **top-10 Kaggriculture prize**. Final submission deadline: 2026-09-30 23:59 UTC. Repository `pmartins87/Kculture` is the source of truth and intentionally public.

The objective is prize probability, not elegance or novelty. Hosted population strength outranks local single-opponent ordering.

## Mandatory first reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/PRIZE_FIRST_DECISION_POLICY.md`
4. `docs/SUBMISSION_LEDGER.md`
5. `docs/strategy/CR089_INTEGRATED_PHYSICAL_POPULATION_RESULT_2026-09-15.md`
6. `docs/strategy/CR088_HOSTED_SENSOR_RESULT_2026-09-15.md`
7. `docs/strategy/CR087_TOP_MACRO_PROFILE_RESULT_2026-09-14.md`
8. `docs/strategy/FP001_E5_ELITE_MIXED_ANIMAL_RESULT_2026-09-15.md`
9. `docs/strategy/FP001_E4_NORMAL_ENVIRONMENT_ROBUSTNESS_RESULT_2026-09-15.md`
10. `official/UPSTREAM_LOCK.md`

Also inspect the latest commits and GitHub Actions before changing code.

## Binding working rules

- Hosted leaderboard/prize performance is the primary outcome.
- Competitive knowledge is cumulative. Do not discard useful opponent/replay/top-player/failed-hypothesis knowledge merely because FP001 exists.
- Official engine facts outrank assumptions.
- Local H2H is a mechanics/catastrophe/causal tool; it is not a hosted-rating oracle.
- Exact hosted bytes are required when a local package is claimed to represent a hosted submission.
- Authenticated Kaggle API is the default current-meta source.
- Both seats and `kaggle-environments==1.32.7` for exact H2H.
- Replay/team/seed identity is research metadata only, never a runtime policy feature.
- No identity/rating/EpisodeId/hidden seed/future/opponent-private runtime information.
- Changed code never inherits old validation.
- Original final holdout remains sealed.
- No repeated polling loops.
- Close failed representations according to their predeclared stop rule; preserve their valid mechanisms as reusable knowledge.

## Current competitive calibration

Best known historical project agent:

- **CR053** submission `56073870`;
- historical checkpoint **2064.8**;
- exact archive SHA-256 `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`.

Important correction: the later local `CR053_CONTROL.tar.gz` is a different file and is quarantined as a hosted proxy.

Frozen external top-10 snapshot from 2026-09-14 is roughly **2958–3191**. The project target is therefore ~3000+, not incremental optimization around 1600.

## CR087/CR088 competitive knowledge to preserve

CR087 showed that exact elite action tapes are extremely state-variable; modal/stitch/1-NN reconstruction is not a faithful elite strategy. The useful recurring macro structure is higher-level:

- early MELON/STRAWBERRY;
- later WHEAT/CARROT/TOMATO;
- durable mixed animals;
- typically about three lands in the first half;
- state-adaptive market queues.

CR088 hosted sensors proved that direct top-tape backbones still transfer badly:

- CR088A `56233701`: ~1252.8;
- CR088B `56233703`: ~1182.3.

Do not retune/resubmit their tape/cap/floor families. Preserve their legal market operators, replay corpus and macro-family representatives.

## FP001 mechanisms currently preserved

- H1 WHEAT town-pulse carry;
- H1B owned-sale deferral;
- H9 public-shop-conditioned product demand;
- DAILY CARE production bonus;
- H10 compact routing and batched animal harvest;
- H11 fertilizer conversion into premium crops;
- M6S1 = 6 MELON + 1 STRAWBERRY with one dedicated hand.

M6S1 is a real economic module:

- E4 default-environment robustness: +9,594.5 mean, CI95 [+6,057.83,+13,131.17], 33–7 signs, 80/80 full mechanics;
- E5 on COW5: +10,542.09 mean, 29–3 signs, 64/64 full mechanics.

But economic gain is not enough to make the C5 architecture competitive.

## CR089 — decisive current diagnosis

Run `34923802262` compared exact C5_BASE and C5_M6S1 over 11 heterogeneous opponent edges, 12 seat-balanced games per edge.

Result:

- C5_BASE: **0W–132L**, 11/11 zero-score edges;
- C5_M6S1: **0W–132L**, 11/11 zero-score edges;
- zero execution failures;
- M6S1 improved mean monetary margin on 10/11 edges and about +16.6k on average across edge means, but converted **zero** W/L coverage.

Binding verdict: `M6S1_FAILS_POPULATION_COMPATIBILITY`.

Therefore:

- close static C5/C5+M6S1 as direct competitive backbones;
- do not threshold-rescue them;
- do not patch them per opponent;
- do not run the market factorial on C5;
- do not submit C5 to Kaggle;
- preserve M6S1/CARE/H10/H11 as modules for a different architecture.

Full result: `docs/strategy/CR089_INTEGRATED_PHYSICAL_POPULATION_RESULT_2026-09-15.md`.

## Current gate — CR090 / H9 adaptive marginal expansion

The next hypothesis is not another fixed composition. It is **state-conditioned marginal capacity**.

Why the fifth animal slot:

- COW5_DAILY exceeded COW4_DAILY by only +1,497.75 mean and 4–4 paired;
- the sixth CARE animal is already decisively negative;
- H9 proves public shop reveals can strongly reverse expected MILK versus WOOL demand;
- E5 proved buying a fixed sheep mix at the opening can damage liquidity and crop completion.

Planned causal structure:

1. four-COW DAILY core;
2. defer the fifth animal until the first legal public shop signal;
3. adaptive COW/SHEEP selection from public expected remaining demand;
4. same-timing delayed-COW control;
5. same-timing delayed-SHEEP control;
6. controlled demand regimes first;
7. fresh default-environment robustness only after causal pass;
8. heterogeneous population W/L gate only after robustness.

A timing-matched control is mandatory: otherwise any gain/loss could come merely from delaying the purchase rather than choosing the correct species.

If H9 fails the causal gate, close species adaptation and move to the higher-level hierarchical controller. If it passes, then and only then test market factors on the surviving adaptive physical controller.

## Hosted submission policy

No Kaggle submission is currently authorized.

A new hosted sensor requires a mechanically valid, strategically distinct candidate that answers a real transfer question after its declared causal/robustness gate. The current task is to build and test CR090, not spend another slot on a static lineage already falsified.

## User action

At this point the user should **not submit anything, rerun anything, or keep a browser/PC open**. Continue the project by sending **“continue”** in the working chat; ChatGPT should inspect the latest GitHub state and advance CR090 from the repository source of truth.
