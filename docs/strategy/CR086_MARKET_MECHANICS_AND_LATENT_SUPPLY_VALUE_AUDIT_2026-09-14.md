# CR086 market mechanics and latent-supply value audit — 2026-09-14

## Scope

Mechanics-only audit before any CR086 policy build or score evaluation. Source is the official Kaggle `kaggle-environments==1.32.7` Kaggriculture engine plus the exact frozen CR083 `main.py`.

No replay outcome is used to fit a policy threshold here.

## Official mechanics established

### Price

For every product, price is a deterministic function of current market inventory and is floored at `$1`. Above the target inventory `I0`, increasing inventory cannot increase price. A SELL is quoted at the current pre-commit market inventory.

### Per-unit lockstep market execution

The market processes queue index 0, then 1, etc. For each queue index, SELL / BUY_* orders are executed unit-by-unit.

When both players have a SELL in the **same queue index**, both units are quoted from the same pre-commit market inventory before either commit. Thus neither seat receives an intra-slot quote advantage.

When one player's SELL for an item is in an **earlier queue index** than the opponent's later SELL for the same item, the earlier sale can receive prices before the later sale increases supply.

### Floor behavior

A successful SELL at price `$1` pays `$1` but does **not** increase market inventory. This is why post-floor private stock is only interval-identifiable by the CR086 estimator.

### Town demand / price recovery

After player market orders, the town consumes public market inventory:

- unlocked shops consume their listed products every configured shop interval (default 4 steps);
- town center consumes one unit of every non-fertilizer product every configured center interval (default 24 steps).

Prices are refreshed after this consumption. Therefore premium-product prices can recover over time; `SELL immediately always` is not a general dominance rule.

### Premium product purchase restriction

`BUY_PRODUCT` is legal only for `WHEAT` and `FERTILIZER`. The CR086 premium set is:

`CARROT, TOMATO, STRAWBERRY, MELON, EGG, MILK, WOOL`.

Reordering an already-existing premium SELL earlier cannot change the price of a later BUY_PRODUCT, because those bought products are different market dimensions. Product price curves are item-separable.

### Liquidity and shed capacity

Moving an already-existing premium SELL earlier in the same turn weakly improves same-turn liquidity and frees shed capacity earlier. It does not add an order or increase quantity.

## Exact CR083 SELL behavior

CR083 currently combines:

- route/tape SELL orders;
- CR053-specific predicted-sell reordering / pull-forward;
- end-of-day room guard;
- invalid SELL clamp;
- dead-stock liquidation for route-surplus product when current price > 1.

It does **not** maintain a general opponent-private-stock estimate and does not rank existing premium SELLs by latent-supply cash-at-risk.

## Mechanics-derived revenue functions

For product `i`, let `p_i(M)` be the official market price at inventory `M`.

Define `advance_i(M, s)` as the market inventory after `s` successful opponent SELL units, applying the exact floor rule: a unit increments inventory only when its quoted price is >1.

Define `revenue_i(M, q)` as the exact revenue from selling `q` units beginning at inventory `M`, again applying per-unit quotes and the floor rule.

For an existing CR083 SELL order of `q` units and CR086 opponent-stock upper bound `S_i`, define:

`latent_supply_cash_risk_i = revenue_i(M, q) - revenue_i(advance_i(M, S_i), q)`.

Properties:

- the quantity is money, not a fitted score;
- it is >=0 under the official non-increasing price-vs-inventory mechanics;
- it is exactly 0 when the modeled latent supply cannot reduce our quoted revenue;
- it naturally becomes 0 at a persistent price floor;
- using the estimator **upper bound** is a conservative worst-case ordering signal, not a prediction that the opponent will certainly dump all stock.

## Candidate action principle

Only existing CR083 premium SELL orders with strictly positive `latent_supply_cash_risk` are urgent.

Within the same turn:

1. urgent premium SELL orders move to the front;
2. urgent orders are sorted by decreasing `latent_supply_cash_risk`;
3. ties preserve original CR083 order;
4. every non-urgent order keeps its original relative order;
5. no order is added/deleted and no quantity/product is changed.

This is a queue-priority intervention, not a route or inventory-liquidation intervention.

## Why this is distinct from closed families

- not replay/action imitation;
- not route stitching;
- not time-indexed transplant;
- not late FEED rescue;
- not Pareto switch gating;
- not public-backbone reuse;
- does not fit a stock threshold from replay outcomes.

It is a clean-room market-order scheduling layer built from official mechanics plus the independently validated legal CR086 inventory representation.
