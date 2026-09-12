# CR083 Phase 0 — exact mechanics / counterfactual branching result

Status: **mechanics audit complete**, performed before interpretation of canonical CR082 H2H results.

Canonical probe: GitHub Actions run `34709053070`, artifact `cr083-mechanics-probe-v1`, using exactly `kaggle-environments==1.32.7`.

No CR082 validation replay, H2H score or seed was used by this probe.

## Branching result

The official Kaggriculture `Environment` is deep-copyable in the pinned runtime:

- `deepcopy_supported = true`;
- copied state digest initially equals source state digest;
- source and clone given the same actions evolve to identical state digests;
- applying a different action to the clone does not mutate the source;
- the divergent action changes the clone state.

Therefore exact environment-state branching is technically available for **offline mechanics/counterfactual research**.

This does **not** authorize use of hidden simulator state as a runtime feature or target shortcut.

## Exact reward objective

The official terminal reward is simply the player's final `farm["money"]`.

Consequences:

- unsold shed/hand inventory has zero terminal value unless converted to money before the end;
- productive assets matter only through future cash they can ultimately create;
- an explicit-value model can be aligned directly to final money / score differential rather than action imitation.

## Interpreter order per turn

The official interpreter executes, in order:

1. farmer and farm-hand actions;
2. market queue processing;
3. town consumption from market inventory;
4. plant decay;
5. end-of-day refresh when applicable;
6. advance day/hour; terminal reward at final step.

A market macro's value therefore depends on the **post-physical current state** and can affect prices/inventory before that turn's town consumption.

## Market mechanics that matter for value modeling

- At most `maxMarketOrdersPerTurn` orders per player are processed; default is 10. Extras are silently dropped.
- Queues are positional. At each queue index, atomic `HIRE` / `BUY_LAND` execute once; unit-count orders then execute one unit at a time.
- Unit-count market operations are lockstep between both players: both are quoted from the same pre-commit market state for that unit, then commits occur in player order.
- `SELL` can sell products from the shed. At price floor `$1`, the player receives the coin but the sold unit does not increase market supply.
- `BUY_PRODUCT` is legal only for `WHEAT` and `FERTILIZER`, deposits directly into shed, respects shed capacity, deducts money and reduces market inventory.
- `BUY_SEED` has fixed crop-specific seed cost and adds to private seed inventory.
- `BUY_ANIMAL` has fixed animal cost, deposits the animal into the shed and respects shed capacity.
- `HIRE` cost follows the per-day Fibonacci sequence times `farmHandCostMult`; hires reset at end of day.
- `BUY_LAND` unlocks NE, SW, SE in that fixed order for 1000, 2000, 4000 coins.
- Buy-product price is quoted at post-buy inventory; sell price is quoted at pre-sell inventory. Therefore an immediate buy→sell round trip against an otherwise unchanged market is intentionally zero-net, not a profitable arbitrage.

## Productive mechanics relevant to long-horizon value

Default crop seed costs / timing:

- WHEAT: seed 10, first yield day 2, max-yield day 4, one-shot, max yield 6;
- CARROT: seed 20, first day 2, max day 3, one-shot, max yield 4;
- TOMATO: seed 50, first day 8, ongoing every 1 day, max yield 4;
- STRAWBERRY: seed 100, first day 10, ongoing every 2 days, max yield 4;
- MELON: seed 80, first day 10, max day 12, one-shot, max yield 6.

Default animals:

- GOOSE: cost 300, coop, first yield day 4, interval 1, max held yield 4, produces EGG;
- COW: cost 400, pasture, first yield day 8, interval 2, max held 6, produces MILK;
- SHEEP: cost 500, pasture, first yield day 6, interval 3, max held 6, produces WOOL.

Plants require daily watering; two consecutive missed days turn them into weeds. Animals require daily feeding with wheat; two missed feed days make them escape. End-of-day hand inventory is dropped into shed up to shed capacity, with overflow discarded.

## Dynamic market / town

Market sell prices are deterministic functions of shared public market inventory, with resource-specific curves and a floor of 1.

Town demand removes products from market inventory and therefore can raise scarcity prices:

- town center consumes every non-fertilizer product at its configured interval (default once/day);
- unlocked shops consume their demand products every configured shop interval (default every 4 turns);
- single-product shops consume 2x;
- shops unlock with replacement and can duplicate.

Current town state is public. **Future shop unlock draws are random and keyed to the episode seed**, which is intentionally hidden from agent observations.

## Critical leakage rule for CR083

Although `deepcopy(env)` preserves the exact hidden RNG/seed state, a future CR083 runtime policy may not receive or infer hidden seed/future shop draws as features.

Therefore exact branching may be used in either of these safe ways:

1. **one-step / known-public-state counterfactuals** whose target does not depend on future hidden randomness; or
2. **multi-step expected-value labels averaged across independently generated simulator seeds / opponent scenarios**, so the learned target is a function of legal observable state and frozen mechanics rather than the hidden seed of a particular episode.

Using the exact hidden seed from a replay/state to choose the best action and then training a runtime predictor to mimic that clairvoyant label is prohibited.

## Opponent-action issue

Market orders are processed concurrently/lockstep, so an own-action counterfactual is not uniquely valued without an opponent action assumption.

CR083 must therefore pre-register how opponent action uncertainty is handled before candidate evaluation, for example a frozen mixture of structural anchor policies or a robust objective across several opponent macro responses. It may not inspect the opponent's private state or current unobserved action.

## Phase-0 conclusion

Exact model-based counterfactual research is feasible and is a materially different architecture from route/teacher imitation. If CR082 fails, the next candidate should be built around **mechanics-derived expected economic value under legal current observation**, with hidden randomness and opponent-action uncertainty explicitly marginalized or made robust.
