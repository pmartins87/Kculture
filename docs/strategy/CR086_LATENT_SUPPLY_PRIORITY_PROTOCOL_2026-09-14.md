# CR086 latent-supply priority protocol — frozen before build

Date: 2026-09-14

## Status

**FROZEN BEFORE CANDIDATE BUILD OR PERFORMANCE SCORE.**

This protocol may not be retuned from Gate A outcomes.

## Candidate

Name: **CR086 latent-supply priority queue**.

Base package must be byte-exact CR083:

`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`

CR083 physical actions, route tapes, route switches, market order membership/quantity, room guard, CR053 counterplay, sell clamp, dead-stock logic and CR083 seed clamp must remain unchanged except for the final same-turn market queue ordering defined below.

## Legal state representation

Embed the already-confirmed CR086 opponent-private-stock estimator semantics for:

`CARROT, TOMATO, STRAWBERRY, MELON, EGG, MILK, WOOL`.

Runtime estimator inputs are limited to:

- current/prior public farms;
- current/prior public market/town state;
- our current/prior private state;
- frozen official mechanics/constants.

Forbidden: opponent private state/action, identity/team/rating, EpisodeId, hidden seed and future state.

At/after first observed `$1` for a commodity, use point `0` plus the mechanics-derived upper interval exactly as in the confirmed estimator. Queue risk uses the **upper bound**.

## Exact value function

Use official `kaggle-environments==1.32.7` market-price parameters and floor semantics.

For current market inventory `M`, existing SELL quantity `q` and current CR086 opponent upper stock `S`:

1. `R_now = revenue(item, M, q)`;
2. `M_after_opp = advance(item, M, S)`;
3. `R_after = revenue(item, M_after_opp, q)`;
4. `cash_risk = R_now - R_after`.

`advance` and `revenue` simulate official per-unit SELL mechanics exactly, including no market-inventory increment for a unit quoted at `$1`.

No probability, learned weight, replay-fitted threshold or opponent-action prediction is permitted.

## Exact queue intervention

After CR083 has completed all existing market logic and the CR083 seed clamp:

- inspect only final existing `SELL` orders for premium products;
- an order is **urgent** iff `cash_risk > 0`;
- move urgent premium SELLs to the front;
- sort urgent SELLs by descending `cash_risk`;
- preserve original queue index as the stable tie-break;
- append every non-urgent order in its original relative order.

Binding invariants:

- final queue length unchanged;
- exact multiset of market orders unchanged;
- all quantities unchanged;
- no physical action changes;
- no route/current-route changes;
- no order additions/deletions;
- no change to the CR083 seed clamp;
- risk can change ordering only.

## Score-blind semantic audit

Before Gate A, prove on deterministic synthetic observations and/or shadow episodes:

1. exact CR083 base hash;
2. estimator runtime uses no forbidden source;
3. candidate market queue multiset exactly equals CR083 on every compared step;
4. physical actions exactly equal CR083;
5. only queue ordering differs;
6. urgent orders satisfy `cash_risk > 0` under the frozen formula;
7. risk-zero premium orders are not promoted by the new layer;
8. stable tie behavior;
9. at least one queue reorder is exercised;
10. deterministic rebuild yields identical candidate hash.

If any semantic audit fails, quarantine candidate before score interpretation.

## Seed firewall

Predeclare:

- semantic/shadow master: `91708609`;
- Gate A master: **`9170861`**;
- promotion master: `9170862`.

All generated seeds must be disjoint from all prior masters and from each other. Firewall failure invalidates evaluation before scores.

## Gate A

Exact CR086 vs exact CR083.

- 16 fresh seeds;
- both seats;
- 32 games total;
- `kaggle-environments==1.32.7`;
- fresh isolated package process per agent/episode;
- zero hidden RNG manipulation.

Frozen PASS requirements:

- exactly 32 completed games / 16 seeds;
- zero errors / zero non-DONE;
- score rate **>= 0.5625**;
- mean terminal-money margin **> 0**.

FAIL decision: `CLOSE_CR086_LATENT_SUPPLY_PRIORITY_NO_RETUNING`.

PASS decision: `ELIGIBLE_FOR_CR086_FROZEN_PROMOTION_PANEL`.

No adjustment of premium set, estimator bounds, `cash_risk > 0`, sorting rule, tie-break, masters or thresholds after Gate A.

## Promotion if Gate A passes

Use the exact Gate-A package unchanged on master `9170862`, 32 fresh seeds × both seats.

Minimum panel:

- CR086 vs CR083 direct;
- CR086 and CR083 versus CR071M;
- CR086 and CR083 versus CR053;
- CR086 and CR083 versus CR061;
- CR086 and CR083 versus CR065.

A later independent high-strength population stress layer remains mandatory before any hosted submission, even if this local promotion panel passes.

## Hosted rule

**This protocol does not authorize a Kaggle submission.**
