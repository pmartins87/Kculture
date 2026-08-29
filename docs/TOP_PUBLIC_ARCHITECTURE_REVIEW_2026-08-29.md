# Exact public-agent architecture review — 2026-08-29

Purpose: identify reusable ideas and remaining headroom in current strong public Kaggriculture agents before designing Adaptive V2. This review uses exact hash-pinned public packages already fetched in Kculture experiments. It is not based only on notebook titles or descriptions.

Identity is used here only for attribution/research. Kculture agent logic must remain identity-free.

## Common meta pattern

The strongest inspected public agents are not end-to-end learned policies. They are generally:

**strong deterministic/replay backbone + sparse public-state corrections.**

The corrections often use shops, market state, coarse opponent farm similarity, or a fixed schedule of expected future sells. This validates Kculture's decision to retain a strong backbone and invest in a much better adaptive overlay rather than replacing everything with full RL.

## Rayk — exact public package

Frozen package: `raykkretzschmar/kaggriculture-rank-your-agent/versions/23`.

Key mechanisms:

- Computes a public farm signature: hands, unlocked quadrants, crops, animals and related board counts.
- `_clone_distance(obs)` measures how similar the two public farms are.
- `_future_sells(obs, step)` reads the agent's own scheduled next-step route sales.
- If clone distance is small, the policy assumes the opponent is likely following a related route and shifts premium sales forward by one turn.
- Frozen preemption constants include full fraction (`1.0`), max batch `12`, minimum future quantity `4`, active window roughly 120–679 and clone-distance cap `6`.
- Premium preemption covers high-value products such as STRAWBERRY/MELON/MILK/WOOL.
- Shifted sale quantity is repaid by reducing the corresponding scheduled later sale.

Market ordering is substantially more sophisticated than raw replay:

- `_impact_score` computes the price damage of a sale using exact market mechanics.
- `_demand_per_day` computes town demand from unlocked shops and center consumption.
- `_order_score` combines market impact with urgency from excess inventory relative to demand.
- `_rank_sell_slots` reorders only existing SELL slots, preserving non-SELL positions.
- Additional route-family counters use observable opponent farm composition.

### Headroom relative to Adaptive V2

Rayk's front-run premise is still a hard similarity heuristic: **if farms look like clones, assume the opponent will approximately follow our own future route tape**. It does not estimate a calibrated state-conditioned probability distribution over the opponent's actual next market action. Quantity is capped by fixed constants rather than chosen by counterfactual expected relative value.

## Tetsu — exact public package

Frozen package: `tetsutani/read-the-town-build-the-farm-kaggriculture/versions/2`.

Architecture is closely related to the Rayk family:

- same public farm similarity / clone-distance concept;
- same scheduled-future-sale preemption family;
- exact market impact + town-demand ordering;
- route/farm-family counters.

Additional visible refinements include:

- `_PREEMPT_EXTRA_UNITS = 1`;
- a separate early-premium WOOL preemption path;
- max batch `12` and clone-distance cap `6`.

### Headroom

Again the central uncertainty model is heuristic route similarity, not a calibrated posterior over strategy archetypes or future sale quantity/position. The extra unit is a fixed policy constant, not a state-specific optimum.

## Tactical — exact public package

Frozen package: `web3cainiao/kaggriculture-v21-tactical-memory/versions/1`.

This agent makes the contrast with CR008 especially clear.

It contains a compressed `_HAZARD` table indexed by absolute future step. Preemption uses:

- lead = `1` turn;
- probability threshold = `0.55`;
- sale fraction = `0.5` of median forecast quantity;
- max batch = `30`;
- cooldown = `8` turns;
- active window 24–679;
- clone-distance cap = `2`.

If the public farms look sufficiently similar and the static hazard table says a product is likely to be sold next turn, it prepends a partial sale.

The terminal sale controller does use public opponent exposure. It estimates how much the opponent appears exposed to each crop/animal product and prioritizes liquidation using a multiplicative score involving opponent exposure, glut weight, current price and `log1p(own_quantity)`.

### Headroom

The hazard is largely **step-conditioned rather than rich-state-conditioned**. The 50% fraction, cap and cooldown are fixed. Adaptive V2 can generalize this idea by predicting the full conditional sale distribution from legal public state/history and solving for the response quantity under exact market mechanics.

## Boatlee — exact public package

Frozen package: `boatlee/v21-r1-public-state-route-portfolio/versions/2`.

This is a multi-route portfolio rather than one tape plus small patches. It runs several internal route families and selects or overlays them using public signals.

Visible decisions include:

- an early opponent-hire/money signal that can select or defer a route;
- delayed route decisions around step 144 using the first two unlocked shops and opponent money;
- first-three-shop regime mapping;
- a step-217 opponent spending jump that can activate a market overlay;
- selection at the first action divergence between route policies;
- `_apply_market_delta`, which can keep one route's physical backbone while importing only the market delta from another.

The embedded route family also contains the same general demand-aware/preemption mechanisms found in other strong public agents.

### Headroom

Boatlee demonstrates an important higher-level idea: **adapt at the route-policy level, not only at the next sale**. However, its gates are coarse hand-built rules at specific stages. Kculture should first prove a superior market adaptive model, then use its inferred archetype/residual state to choose among production/capital subpolicies.

## Kaito V43 — exact public package

Frozen public reference: `kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid/versions/13`.

Prior exact-package inspection established:

- strong climb-safe/common deterministic opening;
- sparse routing changes from observable shop signals;
- first/second YARN_STORE branches around specific route phases;
- exact market mechanics and a state encoder containing own/opponent public assets, shops, demand, prices and inventories;
- a demand-adjusted impact-based sale-order planner;
- quantity-MPC/market-maker components present in the library but deliberately disabled or not deployed when grouped holdouts did not improve wins.

This is a useful methodological prior: sophisticated components should remain off if lineage-aware validation does not support them.

## Prvsiyan — exact public package

Frozen package: `prvsiyan/kaggriculture-frontier-the-soil-remembers-rain/versions/10`.

Dominated by a large replay/action trace plus scheduled market actions, with:

- bounded weed repair;
- shop-regime route/fallback selection;
- terminal inventory liquidation.

Compared with Rayk/Tetsu/Tactical/Boatlee, it contains relatively little opponent-conditioned online adaptation.

## What Kculture already did differently

CR008 does not ask whether the opponent is a named competitor or a clone of our route. It uses legal public opponent state/history to predict high-confidence imminent SELL events. This opponent-conditioned signal produced the largest hosted improvement seen so far in Kculture.

CR008 is nevertheless primitive in the **decision layer**:

- binary trigger;
- only CARROT/STRAWBERRY deployed;
- full available inventory sold when triggered;
- no predicted sale quantity distribution;
- no predicted order-position distribution;
- no explicit downside-risk model;
- no route-archetype posterior;
- no exact optimization over abstain/partial/full response.

## Adaptive V2 opportunity

The exact public code suggests a synthesis that is stronger than any one inspected design:

1. **Bayesian/public-behavior route fingerprint** instead of hard clone distance.
2. **Calibrated state-conditioned hazard** instead of static hazard-by-step.
3. **Quantity and order-position forecasts** rather than event-only prediction.
4. **Exact market counterfactual optimizer** instead of fixed 50%/100% fractions and fixed caps.
5. **CVaR/downside-aware abstention** to avoid CR011-type catastrophic trajectory cascades.
6. **Opponent exposure and forecast residuals throughout the game**, not only at terminal liquidation.
7. After the market layer proves itself, extend the same belief state to coarse route/production/capital choices inspired by Boatlee's policy portfolio.

Formal frozen plan: `docs/ADAPTIVE_V2_RESEARCH_PLAN.md`.

## Current live-replay gap

Kculture now has an automated current-ladder pipeline (`tools/collect_top_ladder_snapshot.py` + `tools/top_ladder_behavior_atlas.py`) requesting top-20 teams and up to three recent public episodes each. The first automatic run safely stopped because repository secret `KAGGLE_API_TOKEN` is not yet configured. No credential was exposed.

Once that one-time secret is configured, CR022A can measure how rigid/adaptive the actual current top submissions are instead of relying only on public source packages.
