# STATUS — Kculture live source of truth

Updated: 2026-09-15

## Mission / objective

Maximize the probability of winning or reaching the prize frontier in Kaggriculture. Novelty is not the objective. Every legal piece of accumulated competitive, replay, mechanics and economic knowledge remains admissible unless stronger evidence supersedes it.

Authoritative branches:

- competitive source of truth: `fix/kaggle-parity-v1`
- experimental mechanics/integration: `research/first-principles-economy-v1`

## Engine / legality lock

- official evaluation path: `kaggle-environments==1.32.7`
- frozen upstream reference commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`
- public `town.unlocked_shops` is shared/legal runtime state and may contain repeated shop names
- no runtime identity, rating, EpisodeId, hidden seed, future state or direct opponent-private features
- original final holdout remains sealed

## Competitive target / calibration

Frozen external snapshot 2026-09-14: leader ~`3191`, rank 10 ~`2958`; target remains roughly `3000+`.

Strongest exact project-hosted anchor:

- **CR053_REAL** — submission `56073870`, checkpoint ~`2064.8`
- exact SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`
- source run `34105008373`, artifact `10012004237`

Other exact anchors:

- CR052_REAL ~`1749.2`, SHA `b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d`
- CR083 ~`1619.9`, SHA `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`
- CR086 ~`1612.6`, SHA `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`

Critical calibration warning: exact-byte league `34802917553` locally ranked CR083/CR086 above CR053 although Kaggle hosted ranks CR053 materially higher. Local H2H is useful for mechanics, causal interventions, catastrophe and diversity, **not** as a hosted-rating oracle.

## Retained competitive knowledge

### CR086

Legal latent-opponent-supply estimator remains validated: 100,660 commodity-step observations, MAE ~`1.25005`, p95 error `9`, interval coverage ~`0.96946`, stock>=10 accuracy ~`0.95634`.

Its candidate preserved route/actions/order multiset and changed SELL priority only. Local Gate A vs exact CR083 was 26W–6L, but hosted checkpoint ~`1612.6` did not improve on CR083. Preserve the estimator/operator; do not use CR086 as preferred backbone.

### CR087 / CR088

Current-top tapes are highly state-variable: 30/30 exact tapes unique, median Hamming 719/719. Modal/stitch/1-NN imitation is not a faithful decision policy.

Useful macro priors remain: early MELON/STRAWBERRY, later WHEAT/CARROT/TOMATO, mixed animals, ~3 early-half lands and adaptive market queues.

Direct hosted tape sensors were weak: CR088A `56233701` ~`1252.8`; CR088B `56233703` ~`1182.3`. Preserve corpus/market knowledge; close direct tape backbones.

## FP001 retained mechanics/economics

Validated reusable knowledge:

- H1 WHEAT town-pulse carry: +`916.875` paired mean (`34843184110`)
- H1B owned-sale deferral: `104/104` positive exact cases (`34843556192`)
- H8/B3 + DAILY CARE: COW physically strongest in tested baseline; CARE first-order (`34844919444`, `34847600991`)
- H9 public-shop demand representation (`34847099631`), but not the failed simple species decision rule
- H10 compact routing + threshold-6 batching (`34848106237`)
- H11 fertilizer conversion: STRAWBERRY strong, TOMATO positive regions (`34848464648`)
- B4: fifth COW marginal, sixth COW beyond action/opportunity-cost frontier (`34848633407`)
- M6S1 = 6 MELON + 1 STRAWBERRY is a genuine economic module, repeatedly ~+9.5k to +10.5k when scheduler/liquidity preconditions hold

Module validity is not competitive-backbone validity.

## CR089 — COMPLETE / FAIL

Run `34923802262`: C5_BASE and C5_M6S1 each **0W–132L**, 11/11 zero-score edges, zero mechanical failures. M6S1 improved monetary margins but zero W/L coverage.

Binding verdict: `M6S1_FAILS_POPULATION_COMPATIBILITY`. Static C5/C5+M6S1 are closed as competitive backbones; M6S1 survives as a module.

## CR090 — COMPLETE / FAIL

Run `34979280512`, artifact `10401171740`.

Mechanics exact. YARN adaptive SHEEP minus delayed COW: mean `-174.46`, median `-451`, 7W/17L. MILK adaptive COW minus delayed SHEEP: mean `+2119.39`, median `+2151`, 28/28 positive. Overall adaptive minus delayed COW mean `-32.71`.

Binding verdict: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`. No threshold rescue; H9 survives only as a state feature/prior.

## Current binding gate — CR091 hierarchical market option

Protocol: `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_PROTOCOL_2026-09-15.md`.

Architecture: keep exact hosted CR053 as physical/macro host and test CR086 latent-supply priority as a separable market option.

Frozen Phase-1 design:

- `CR053_BASE`: exact CR053
- `CR053_LATENT_PRIORITY`: exact CR053 farmer/hands and exact market-order multiset; only order sequence may change by the exact CR086 latent-supply cash-risk operator
- opponents: CR052_REAL, CR053_REAL, CR083, CR086
- seeds `91301..91308`, both seats
- 16 games/edge, 64 games/treatment, 128 total
- W/L edge score primary; terminal money diagnostic only
- zero mechanics failures/parity violations required
- no automatic Kaggle submission

### CR091 run 1 — INVALID, no strategic verdict

Workflow `34987640694` is **not evidence for PASS or FAIL**. Its harness executed historical `main.py` files directly with `exec()` rather than the hosted-faithful package runner. CR052 therefore failed all 32 of its treatment episodes and had zero valid games.

The remaining three edges were mechanically clean and produced a non-binding diagnostic only:

- vs CR053_REAL: base `0.5000` -> latent `0.6875` (`+0.1875`)
- vs CR083: `0.5000` -> `0.5000`
- vs CR086: `0.5000` -> `0.5000`
- physical/multiset/base parity exact on all executable calls; zero violations

These partial numbers **must not be promoted** because the frozen panel was incomplete.

Record: `docs/strategy/CR091_RUN1_INVALID_2026-09-15.md`.

### CR091 authoritative rerun — ACTIVE

Repair commit on research branch: `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.

Binding workflow run: **`34990757344`**.

The frozen experimental design and thresholds are unchanged. Only execution semantics were repaired to the already validated reference path:

- `kaggle_exact_runtime.AgentProcess`
- fresh spawned process per package per episode
- official `kaggle_environments.agent.Agent`
- `Environment.__get_shared_state(seat).observation`
- official reference stepping/overage accounting
- no falsy-action PASS substitution
- the exact CR053 package itself now generates the candidate base action; the CR086 option is applied on top of that exact action
- detailed phase/step/traceback is recorded if any package still fails

Only run `34990757344` may produce the CR091 verdict.

Frozen outcomes after a mechanically valid rerun:

- broad positive transfer -> `CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`
- strong positive + negative edges -> `CR091_HETEROGENEOUS_OPTION_VALUE_ADVANCE_ROUTER_DISCOVERY`
- neither -> `CR091_LATENT_OPTION_FAIL_CLOSE_OPTION`, no threshold rescue
- mechanics failure -> diagnose/repair semantics only; no strategic inference

If option value survives, Phase 2 learns a **legal public-state option-value router**; runtime opponent identity remains prohibited.

## Closed / do-not-retune absent new evidence

CR078/079, CR080 replay stitching, CR081 static market-prefix transplant, CR082 1-NN imitation, CR084 FEED rescue, CR085 Pareto gating, direct CR088 tapes, static C5/C5+M6S1, fixed C3S2/C2S3, simple CR090 first-shop species rule.

## Hosted policy

No CR091 Phase-1 hosted submission is authorized. Hosted slots remain high-information population sensors, used only after a mechanically exact candidate answers a real population-transfer question.
