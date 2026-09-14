# ROADMAP — Kculture live plan

Updated: 2026-09-14

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

## Track C — CR088 automatic population search

### Phase 0 — COMPLETE

Run `34806600636`: 30/30 top-derived seeds mechanically valid across 720 fresh games. Seven diverse bases retained: Majkel, Orbital, feel the agi, redblackbst, ymg_aq, Otter and SpaTaro.

### Phase 1 — COMPLETE

Initial run `34807533884` suffered an entrypoint packaging failure for modified overlays and is not economic evidence.

Corrected frozen rerun **`34808258927`**:

- 42/42 policies mechanically valid;
- zero engine failures/non-DONE;
- 26 overlays passed the frozen non-regression filter;
- original holdout sealed.

Selected hosted sensors:

- CR088A Orbital base — SHA `24e78d657d6c16371fcc7393fbea4d23ce695fd456e722e37f5398f7866ab16e`;
- CR088B feel `risk8_p125` — SHA `055fbbcd09dc3112bef3ef7a78965ed09f28ec999283dab87641e60d5cf9d053`.

First submit attempt `34809554553` failed before Kaggle submission because the workflow incorrectly required `main.py` to be the only tar member. Infrastructure-only fix commit `761a83b063b11385570ba923e28840d93286e54f` preserves exact candidate bytes and changes only that preflight. Let the authenticated quota/duplicate gate decide whether submission is legal when the corrected workflow executes.

Stop rules: no manual CR088A/B patch ladder, no raw local-champion promotion, no revival of CR080/081/082 representations.

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

## Track E — integrated elite-informed hybrid — ACTIVE NEXT GATE

This is the new central workstream. The hypothesis is not “FP001 beats all prior knowledge”; it is:

> elite-informed macro production + causally proven FP001 execution/economic primitives + legal adaptive market logic can outperform either component alone.

### E1 — physical/economic hybrid gate

Compare on identical fresh seeds/seats:

1. `COW4_DAILY` animal-only control;
2. `COW5_SURVIVAL` animal-only control;
3. `COW5_DAILY` mean-best animal-only control;
4. COW4_DAILY + small STRAWBERRY block with H11-optimal fertilizer timing;
5. COW5_SURVIVAL + small STRAWBERRY block;
6. COW5_DAILY + STRAWBERRY as explicit action-starvation treatment;
7. treatments 4/5 with bounded dedicated HIRE only if the crop workload creates positive marginal labor value;
8. elite-informed COW/SHEEP mixed-capacity comparator, using CR087 macro priors without blindly replaying one tape.

Measure final bank, survival, crop/animal output, fertilizer allocation, labor cost, unused turns, movement, missed care/feed/water and terminal inventory.

PASS: a hybrid must beat its matched animal-only control causally without hidden catastrophe. If crop work simply displaces more valuable CARE, close that architecture rather than tune indefinitely.

### E2 — population compatibility gate

Only E1 survivors enter heterogeneous evaluation against exact historical anchors and multiple CR088/top-family representatives. Use both seats and fresh seeds. Do not promote by one local aggregate score alone; inspect matchup coverage and catastrophic weaknesses.

### E3 — market integration

For physical survivors, factorially test the legal CR088/CR086-style economic operators and FP001 H1/H1B timing primitives. Market overlays must be compared against each candidate's own physical base.

### E4 — public-shop adaptation

Use H9 public town composition to choose marginal capacity/product mix. This is legal current public state and should be evaluated as an adaptive expansion controller rather than a fixed species rule.

### E5 — hosted sensors

Spend hosted slots only on mechanically valid, meaningfully distinct candidates that answer a transfer question. Hosted evidence updates the population objective; it is not reserved only for the locally highest mean.

## Closed hypotheses

CR078, CR079, CR080 replay stitching, CR081 market-prefix transplant, CR082 1-NN teacher imitation, CR084 FEED rescue, CR085 Pareto gating: closed / do not retune.

Direct adoption of the three previously screened public notebook packages is closed; their mechanisms remain research inputs.

## Current frontier and stop condition

Fresh frozen top-10 snapshot from 2026-09-14 starts at Majkel1337 `3191.4`; rank 10 redblackbst `2958.4`. Our task is to construct a policy in that class, not optimize a ~1600 lineage indefinitely.

Do not stop at a merely profitable or novel farm. Stop only when evidence says either:

- we have a hosted/top-population candidate plausibly in prize contention; or
- a defined branch has exhausted its predeclared causal gates and should be closed in favor of the next highest-information branch.
