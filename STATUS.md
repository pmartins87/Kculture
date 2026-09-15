# STATUS — Kculture live source of truth

Updated: 2026-09-15

## Mission / objective

Maximize the probability of winning or reaching the prize frontier in Kaggriculture. The project is not optimizing novelty. Every legal piece of accumulated competitive, replay, mechanics and economic knowledge remains admissible unless stronger evidence supersedes it.

Authoritative branches:

- competitive source of truth: `fix/kaggle-parity-v1`
- experimental mechanics/integration: `research/first-principles-economy-v1`

## Engine / legality lock

- official evaluation path: `kaggle-environments==1.32.7`
- frozen upstream reference commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`
- public `town.unlocked_shops` is shared/legal runtime state and may contain repeated shop names
- no runtime identity, rating, EpisodeId, hidden seed, future state or direct opponent-private features
- original final holdout remains sealed

## Competitive target and calibration

Frozen external snapshot 2026-09-14:

- leader ~`3191`
- rank 10 ~`2958`
- target class remains roughly `3000+`

Strongest exact project-hosted anchor:

- **CR053_REAL** — submission `56073870`, checkpoint ~`2064.8`
- exact package SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`
- source artifact run `34105008373`, artifact ID `10012004237`

Other exact hosted anchors used for causal/population work:

- CR052_REAL ~`1749.2`, SHA `b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d`
- CR083 ~`1619.9`, SHA `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`
- CR086 ~`1612.6`, SHA `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`

Critical calibration warning: exact-byte league run `34802917553` locally ranked CR083/CR086 above CR053 even though hosted Kaggle ranks CR053 materially higher. Local H2H remains valid for mechanics, causal changes, catastrophe and diversity; its numeric ordering is **not** a hosted-rating oracle.

## Competitive evidence retained

### CR086 — legal latent-supply market representation

Independent estimator holdout: 100,660 commodity-step observations, MAE ~`1.25005`, p95 absolute error `9`, interval coverage ~`0.96946`, stock>=10 accuracy ~`0.95634`.

Its order-only candidate preserved route, physical actions, market-order products/quantities and changed only SELL priority by mechanics-derived cash-at-risk. Gate A vs exact CR083 was 26W–6L, but hosted checkpoint ~`1612.6` did not beat CR083. Therefore the estimator/operator remains reusable; CR086 is not a preferred backbone.

### CR087 / CR088 — elite macro/replay knowledge

Current-top action tapes are highly state-variable: 30/30 exact tapes unique, median Hamming distance 719/719. Modal/stitch/1-NN imitation is not a faithful substitute for a decision policy.

Repeated elite macro families still provide useful priors: early MELON/STRAWBERRY, substantial later WHEAT/CARROT/TOMATO, mixed animals, usually ~3 lands in the first half and state-sensitive market queues.

CR088 direct hosted tape sensors were weak:

- CR088A Orbital base submission `56233701`, checkpoint ~`1252.8`
- CR088B feel+risk8 submission `56233703`, checkpoint ~`1182.3`

Preserve corpus and market knowledge, close direct tape backbones.

## FP001 retained mechanics/economics knowledge

FP001 is an additive discovery track, not a replacement for competitive knowledge.

Validated primitives:

- H1 town-pulse WHEAT carry: +`916.875` paired mean, flat-price null 0 (`34843184110`)
- H1B owned-sale deferral: `104/104` positive mechanics cases (`34843556192`)
- H8/B3 animals: COW physically stronger than SHEEP/GOOSE in tested baseline; DAILY CARE is first-order (`34844919444`, `34847600991`)
- H9: public shop state changes expected MILK/WOOL/EGG demand (`34847099631`), but CR090 shows this is a representation, not a complete action rule
- H10: compact routing + threshold-6 batching (`34848106237`)
- H11: fertilizer conversion strongly useful for STRAWBERRY, positive regions for TOMATO, no tested extra MELON fertilizer value (`34848464648`)
- B4: COW5_DAILY marginally > COW4_DAILY; COW6_DAILY clearly worse due action/opportunity-cost frontier (`34848633407`)
- M6S1 = 6 MELON + 1 STRAWBERRY is a real economic module: E3/E4/E5 repeatedly produced roughly +9.5k to +10.5k value with exact mechanics preservation

Do not confuse module validity with competitive-backbone validity.

## CR089 — static physical population gate COMPLETE / FAIL

Authoritative run `34923802262`.

Against 11 heterogeneous exact/macro edges, 12 games/edge:

- C5_BASE: **0W–132L**
- C5_M6S1: **0W–132L**
- both: 11/11 zero-score edges
- zero execution failures
- M6S1 improved monetary edge margin on 10/11 edges and by ~`+16.6k` averaged over edge means, but produced zero W/L gain

Binding verdict: `M6S1_FAILS_POPULATION_COMPATIBILITY`.

Static C5 and C5+M6S1 are closed as competitive backbones. M6S1 remains a valid module.

Result: `docs/strategy/CR089_INTEGRATED_PHYSICAL_POPULATION_RESULT_2026-09-15.md`.

## CR090 — simple H9 species adaptation COMPLETE / FAIL

Authoritative run `34979280512`, artifact `10401171740`, ZIP SHA `407769891c9f8ab7c240c8bb08fd10bfa606a890436cc320d5de6508ba2971ec`.

Design: four-COW DAILY core until first public shop; then timing-matched fifth COW, fifth SHEEP or H9 selector choosing SHEEP iff expected remaining WOOL > MILK.

Mechanics were exact:

- zero failures
- prefix parity `128/128`
- first-shop parity `128/128`
- selector full-trajectory parity `128/128`
- final fifth animal exact `128/128`
- support YARN `24`, MILK `28`, NEUTRAL `76`

Causal result:

- YARN adaptive SHEEP minus delayed COW: mean **-174.46**, median **-451**, `7W/17L`, positive rate `29.17%`
- MILK adaptive COW minus delayed SHEEP: mean **+2119.39**, median **+2151**, `28/28` positive
- all adaptive minus delayed COW: mean **-32.71**, median `0`, `7W/104T/17L`

Binding verdict: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`.

Do not threshold-tune the simple rule. CR090 Phase 2 H9+M6S1 is cancelled because its prerequisite failed.

Result: `docs/strategy/CR090_H9_PUBLIC_SHOP_ADAPTIVE_RESULT_2026-09-15.md`.

## Current binding gate — CR091 hierarchical controller / market option

Protocol: `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_PROTOCOL_2026-09-15.md`.

Key architecture decision: preserve CR053 as the hosted-proven physical/macro host rather than replace it with another isolated backbone. Begin hierarchy in a separable subsystem.

Phase-1 treatments:

1. `CR053_BASE`: exact CR053;
2. `CR053_LATENT_PRIORITY`: exact CR053 farmer + hands + full market-order multiset, with only existing order sequence changed by the exact CR086 latent-supply cash-risk priority operator.

Exact Phase-1 population:

- CR052_REAL
- CR053_REAL
- CR083
- CR086
- seeds `91301..91308`
- both seats
- 16 games/edge
- 64 games/treatment; 128 total

Mandatory parity: every farmer/hand action and every normalized market-order multiset must equal CR053. Treatment must actually reorder at least one market call. W/L edge score is primary; terminal money is diagnostic only.

Implementation on `research/first-principles-economy-v1`:

- candidate wrapper `candidates/cr091_cr053_market_option.py`
- test `tools/cr091_hierarchical_market_option_gate.py`
- workflow `.github/workflows/cr091-hierarchical-market-option.yml`
- head commit `93e3926581706b10c11f93fbec9ae5559670dc55`
- active workflow run **`34987640694`**

Frozen decisions:

- broad positive transfer -> `CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`
- strong positive + negative edges -> `CR091_HETEROGENEOUS_OPTION_VALUE_ADVANCE_ROUTER_DISCOVERY`
- neither -> `CR091_LATENT_OPTION_FAIL_CLOSE_OPTION`, no post-result threshold rescue
- mechanics failure/dormancy -> repair semantics only or close dormant option

If CR091 provides option value, Phase 2 learns a **legal public-state option-value router**. Runtime opponent identity is prohibited. Candidate state features can include latent-risk summaries, prices/inventory, town shops, clock, own resources, public production and action-capacity proxies. The target is counterfactual competitive W/L value, not money.

## Closed hypotheses / do-not-retune list

Without genuinely new evidence changing the documented failure mechanism, keep closed:

- CR078 / CR079
- CR080 replay stitching
- CR081 static market-prefix transplant
- CR082 1-NN teacher imitation
- CR084 FEED rescue
- CR085 Pareto gating
- direct CR088 tape backbones
- fixed C5/C5+M6S1 backbone
- fixed C3S2/C2S3 opening grid
- simple CR090 first-shop species rule

## Hosted policy

No CR091 Phase-1 hosted submission is authorized. Hosted slots are information-expensive population sensors. Submit only a mechanically exact, strategically distinct candidate that has answered a real population-transfer question.
