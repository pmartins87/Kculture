# ROADMAP — Kculture live plan

Updated: 2026-09-15

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. The target class is ~3000+ hosted rating.

## Binding principles

1. Hosted leaderboard strength is the primary outcome.
2. Local H2H is for mechanics, catastrophe filtering, causal comparison and hosted-calibrated league evidence — never a single-incumbent surrogate for population skill.
3. A local anchor may represent a hosted agent only if its exact submitted bytes/hash are proven.
4. Authenticated Kaggle API is the default current-meta source.
5. Use both seats and `kaggle-environments==1.32.7` for exact local H2H.
6. No identity, team, rating, EpisodeId, hidden seed, future state or opponent-private runtime features.
7. Original final holdout remains sealed.
8. Do not retune closed hypotheses on spent validation evidence.
9. Do not enter polling loops.
10. Distinct mechanically valid candidates may be probed hosted earlier; submission slots are experimental sensors as well as final promotion slots.
11. **Competitive knowledge is cumulative.** New research tracks do not erase prior opponent/replay/top-player knowledge. Proven architectures, mechanisms, baselines and failure lessons remain available until superseded by better evidence.
12. **Innovation has no intrinsic promotion value.** A new idea advances only if it increases expected population/hosted performance or information value toward winning.

## Critical reset — exact hosted incumbent

Best known historical project agent is **CR053 submission `56073870`**, score checkpoint **2064.8**, exact SHA:
`095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`.

The later `CR053_CONTROL` anchor SHA `a9fea449...bd4c` is a different file and is quarantined as a proxy for hosted CR053.

The exact CR053/CR052 candidate artifact is preserved in run `34105008373`, artifact `10012004237`.

## Track A — hosted-calibrated league

Workflow: `.github/workflows/hosted-calibrated-league-v1.yml`, commit `a42b4589e568e3203ede7dad653e1c000f22b710`.

Initial exact cohort:
- CR053_REAL — 2064.8 hosted
- CR052_REAL — ~1700–1750 hosted
- CR083 — ~1619.9 latest authenticated
- CR086 — hosted probe later around ~1612.6

Run `34802917553` completed with zero errors, but the local order is not hosted-calibrated: CR083 and CR086 each beat CR053_REAL 20–4 locally although CR053 remains substantially stronger on Kaggle. CR053_REAL beat CR052_REAL 14–10.

Decision: keep exact packages for mechanics, catastrophe and diversity screens. Hosted probes remain the calibration instrument for population strength.

## Track B — preserved competitive mechanisms from CR086/CR087

CR086 proved that legal latent-opponent-supply estimation is technically strong, but its locally strong SELL-priority overlay did not translate into a hosted gain over CR083. Preserve the estimator/market mechanism as a module; do not treat its original candidate as a promoted backbone.

CR087 current-top mining is binding architectural evidence:

- exact action tapes are highly variable and should not be reconstructed by modal/stitch/1-NN imitation;
- elite macro production programs nevertheless converge in useful families;
- recurring structure includes early MELON/STRAWBERRY, later WHEAT/CARROT/TOMATO, durable mixed animals, usually 3 lands in the first half, and state-adaptive market queues;
- five macro families from `docs/strategy/CR087_TOP_MACRO_PROFILE_RESULT_2026-09-14.md` must remain represented in population research.

This is not a closed knowledge source. It is the competitive prior against which new FP001 primitives are integrated.

## Track C — CR088 automatic population search — HOSTED SENSOR COMPLETE

Phase 0 run `34806600636`: 30/30 top-derived tapes mechanically valid. Corrected Phase 1 run `34808258927`: 42/42 valid, 26 overlays passed the frozen local non-regression filter.

Corrected submission workflow `34858890714` sent the exact selected sensors:

- CR088A `56233701`, Orbital base, SHA `24e78d65...16e`;
- CR088B `56233703`, feel `risk8_p125`, SHA `055fbbcd...053`.

Authenticated run `34910849970` closed both as direct candidates:

- CR088A: 1252.8, 59 episodes; newest 32 = 11W–21L;
- CR088B: 1182.3, 54 episodes; newest 32 = 16W–16L;
- zero mechanical failures.

Full result: `docs/strategy/CR088_HOSTED_SENSOR_RESULT_2026-09-15.md`.

Decision: no tape/cap/floor retuning and no resubmission. Preserve the legal market operator, seven macro-family representatives and replay corpus for integrated population work.

## Track D — FP001 additive production/economics discovery

FP001 is no longer treated as a purity-separated alternative agent. It is a module-discovery laboratory whose passing mechanisms may be inserted into elite-informed competitive architectures.

Passed primitives to preserve:

- H1 WHEAT town-pulse carry;
- H1B owned-inventory sale deferral;
- H9 public-shop-conditioned animal demand;
- B3 FEED/CARE production bonus;
- H10 compact routing + batched animal harvest;
- H11 fertilizer conversion into premium crops, especially STRAWBERRY;
- B4 action-capacity frontier.

### B4 action-capacity decision

Run `34848633407`:

- COW4_DAILY mean +37,949.75;
- COW5_SURVIVAL +36,685.25;
- **COW5_DAILY +39,447.50** — mean-best animal-only policy;
- COW6_SURVIVAL +33,054.25;
- COW6_DAILY +35,272.75.

But COW5_DAILY is not a universal optimum:

- vs COW4_DAILY it is only +1,497.75 mean and 4–4 paired;
- vs COW5_SURVIVAL +2,762.25 mean and 6–2;
- sixth cow under SURVIVAL loses −3,631 mean, 0–8 vs COW5;
- sixth cow under DAILY loses −4,174.75 mean, 0–8 vs COW5.

All animals survive, so the limit is action/opportunity cost. Preserve COW4_DAILY, COW5_SURVIVAL and COW5_DAILY as controls for integration.

## Track E — integrated elite-informed hybrid

The architecture hypothesis remains:

> elite-informed macro production + causally proven FP001 execution/economic primitives + legal adaptive market logic can outperform either component alone.

### E1–E4 — production module discovery COMPLETE

- E1 closed residual-idle main-farmer STRAWBERRY.
- E2D proved dedicated labor/crop value after correcting the crop-occupancy/shop-RNG confound: +907 to +919 over animal controls, all 8/8.
- E3 run `34868854114` selected M6S1 = 6 MELON + 1 STRAWBERRY, +9,533 in deterministic-town causal testing.
- E4 run `34869392514` gave **STRONG PASS** under default stochastic environment: +9,594.5 mean, CI95 [+6,057.83,+13,131.17], 33–7 signs, 80/80 complete mechanics/output.

Density tuning is closed. M6S1 is the frozen physical crop module.

### E5 — elite fixed mixed-animal transfer COMPLETE / FAIL

Corrected run `34922557868` passed 4/4 exact COW5/E4 trajectory parity. C5_M6S1 replicated +10,542.09 mean over C5_BASE with 64/64 full mechanics. Fixed C3S2/C2S3 hybrids produced only partial MELON blocks and lost −8,392.45/−14,370.72 mean versus C5_M6S1, failing the frozen retention rules.

Decision: close the static composition grid. C5_M6S1 was the sole E5 physical survivor; fixed mixed animals remain only as an H9 adaptive prior.

### E6 / CR089 — heterogeneous population compatibility COMPLETE / FAIL

Run `34923802262` tested exact C5_BASE and C5_M6S1 against four exact hosted anchors plus all seven CR088/current-top macro representatives, 12 seat-balanced games per edge.

Final result:

- C5_BASE: **0W–132L**, 11/11 zero-score edges;
- C5_M6S1: **0W–132L**, 11/11 zero-score edges;
- zero errors/non-DONE and both mechanically valid;
- mean/median edge-score delta from M6S1: `0.0`;
- M6S1 improved monetary mean margin on 10/11 edges, averaging about +16,566 across edge means, but converted zero additional wins.

Verdict: `M6S1_FAILS_POPULATION_COMPATIBILITY`. Full result: `docs/strategy/CR089_INTEGRATED_PHYSICAL_POPULATION_RESULT_2026-09-15.md`.

Binding stop: close static C5/C5+M6S1 as direct competitive backbones. Do not threshold-rescue, opponent-patch, run the market factorial on C5, or submit C5. Preserve M6S1/CARE/H10/H11 as reusable modules.

### E7 / CR090 — H9 public-shop adaptive marginal expansion CURRENT

Use the legal current public town-shop state to allocate the **marginal fifth animal slot** after a shop reveal instead of buying another fixed opening composition.

Why this slot:

- COW5_DAILY beat COW4_DAILY by only +1,497.75 mean with a 4–4 paired sign split;
- a sixth CARE animal is already decisively negative;
- H9 proves public shop composition can reverse MILK vs WOOL remaining demand;
- E5 proves a fixed opening sheep mix can damage liquidity and crop completion.

Frozen experimental hierarchy:

1. four-COW DAILY core;
2. defer the fifth animal until the first legal public-shop signal is available;
3. compare adaptive COW/SHEEP choice against **same-timing delayed-COW and delayed-SHEEP controls**;
4. first causal test uses controlled shop-demand regimes and must prove that the adaptive selector chooses the economically correct species without mechanical regression;
5. only then run fresh default-environment robustness;
6. only after robustness run a heterogeneous population W/L gate.

No rescue threshold may be selected after seeing the population result. If H9 cannot beat timing-matched controls causally, close species adaptation and move to the higher-level hierarchical controller.

### E8 — separable market integration CONDITIONAL

Only on an adaptive physical/controller survivor, factorially test CR086/CR088 legal latent-supply SELL logic plus H1/H1B timing. Keep physical and market layers attributable.

Do **not** run this factorial on the failed static C5 backbone.

### E9 — hierarchical competitive controller

Combine elite-derived macro priors, passing physical modules, H9 town conditioning, fertilizer/crop opportunity-cost allocation and adaptive market logic. This is the intended path toward a genuinely state-adaptive architecture rather than another fixed tape or fixed farm.

### E10 — hosted sensors

Spend a hosted slot only on a mechanically valid, strategically distinct candidate that survives its declared causal/robustness gate and answers a population-transfer question. CR089 authorizes no submission.

## Closed hypotheses

CR078, CR079, CR080 replay stitching, CR081 market-prefix transplant, CR082 1-NN teacher imitation, CR084 FEED rescue, CR085 Pareto gating: closed / do not retune.

Direct adoption of the three previously screened public notebook packages is closed; their mechanisms remain research inputs.

Static C5 and C5+M6S1 are closed as direct competitive backbones after CR089. Their passing submodules remain reusable.

## Current frontier and stop condition

Fresh frozen top-10 snapshot from 2026-09-14 starts at Majkel1337 `3191.4`; rank 10 redblackbst `2958.4`. Our task is to construct a policy in that class, not optimize a ~1600 or zero-coverage lineage indefinitely.

Do not stop at a merely profitable or novel farm. Stop only when evidence says either:

- we have a hosted/top-population candidate plausibly in prize contention; or
- a defined branch has exhausted its predeclared causal gates and should be closed in favor of the next highest-information branch.
