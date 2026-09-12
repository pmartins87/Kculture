# CR083 Phase 1 — causal market-family ablation result

Status: **complete / architecture evidence only**.

Canonical workflow: `34715158344`.

Exploratory master seed: `9130830`; 8 fresh seeds × both seats = 16 games/variant. This master is permanently architecture-forming only and may not be reused for CR083 promotion.

All six jobs completed with zero execution errors and zero non-DONE games. Each variant was exact CR071M with exactly one final market-order family deleted after inherited queue construction and safety logic.

## Result

| Ablation | W-L-T vs CR071M | Score rate | Mean money margin | Median margin | Best margin |
|---|---:|---:|---:|---:|---:|
| NO_BUY_ANIMAL | 0-16-0 | 0.0000 | -153,976.4 | -158,923 | -112,192 |
| NO_BUY_LAND | 0-16-0 | 0.0000 | -70,241.5 | -68,357 | -42,515 |
| NO_BUY_PRODUCT | 0-16-0 | 0.0000 | -139,142.0 | -139,122.5 | -124,368 |
| NO_BUY_SEED | 0-16-0 | 0.0000 | -152,182.4 | -150,497 | -103,396 |
| NO_HIRE | 0-16-0 | 0.0000 | -155,494.1 | -152,936 | -107,352 |
| NO_SELL | 0-16-0 | 0.0000 | -138,184.8 | -146,022.5 | -97,253 |

## Interpretation

There is **no removable market family** in CR071M. Every broad deletion is catastrophically harmful on the same physical backbone.

The largest causal dependence is on HIRE / animals / seeds, but all six families are deeply coupled to the route. Even BUY_LAND, the least destructive ablation, still loses every game and roughly 70k money on average.

Therefore CR083 must not search for a whole-family switch such as “disable seeds” or “disable hires”. The intervention surface must be **within-family and mechanically dominated**, preserving the backbone's productive plan.

## Mechanically dominated opportunity identified after the frozen ablation

Seed purchases admit a strong value invariant:

- seeds have no terminal liquidation value;
- seeds cannot be sold;
- a seed can create value only if some future route unit action actually executes `PLANT` for that crop;
- therefore, once the current route is known, purchasing seed quantity above `future PLANT demand - current seed stock` is weakly dominated: the excess cannot be consumed by the policy and can only reduce final money.

Static route audit found that the MAIN route contains 188 WHEAT seed purchases but only 164 WHEAT PLANT commands, while one alternate tail uses 189/189. Because all route-switch checkpoints occur before the late-game seed purchases, a runtime clamp can condition on the **already selected own route**, not on opponent-private or future random information.

This motivates CR083 Phase 2: a route-aware future-seed-demand clamp, not a broad BUY_SEED deletion.

## Closure / next step

- Do not tune or compare whole-family deletion variants further on `9130830`.
- Do not use these 96 games as promotion evidence.
- Freeze the Phase-2 seed-demand-clamp representation and a fresh exact Gate A before building/evaluating it.
- Preserve CR071M farmer/hands and every non-dominated economic action unchanged.
