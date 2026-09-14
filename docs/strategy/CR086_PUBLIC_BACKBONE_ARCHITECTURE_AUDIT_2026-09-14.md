# CR086 public-backbone architecture audit

Date: 2026-09-14

This is a score-blind/static architecture audit performed after source acquisition and before interpreting the frozen public-backbone H2H benchmark. It does not define or authorize a CR086 candidate.

## Frozen sources

Acquisition run `34790801576`, artifact `10327672303`.

### 1. Indarkarhana — Shape the Shop Work the Pasture (TOP 10)

The pulled notebook deterministically produces archive SHA-256 `fa9e7eb1a0174a1bf292fb4d47bd209defed929758214d3506e050a68ee5f98f` with 13 members and entrypoint `kaggriculture_e776_agent`.

Notebook provenance explicitly attributes the complete programme prior to an official CC0 Kenjo1209 replay and an inherited execution-network prior to an official CC0 NIklitaCheporev replay. The notebook describes its own contribution as guarded execution, demand-aligned pasture substitution, delivery repair, latent-pasture activation and causal/closed-loop validation. Public-notebook source licensing beyond those replay-prior statements still requires explicit compliance review before any hosted derivative use.

Architecture:

- complete deterministic farm programme / action-network prior;
- demand pressure from unlocked shops plus current MILK/WOOL prices;
- conserved COW<->SHEEP bundle substitution without changing route geometry;
- reallocation of animal-product sales by current revenue and demand;
- guarded purchase of one extra demand-aligned animal plus one extra hand at a single checkpoint;
- activation of an already serviced empty pasture;
- engine-exact delivery repair for the appended hand;
- fail-closed guards on geometry, inventory, market capacity and cash.

Key distinction from CR083: this changes productive structure, not merely market timing or late route selection.

### 2. Boatlee — V29-R1 Adaptive Market Hysteresis

The notebook deterministically produces standalone package SHA-256 `8dc512911c0173483211314f63cbf1d7e460cad33dfbc02f0f77d023f6d809fe` with `main.py` SHA-256 `c4a6964cec3c1c99207c32bb1fd91e53c3ec01e6890da5734331cbeab1cc1267`.

Architecture:

- deterministic high-output production schedule remains the physical backbone;
- stateful market controller for MILK/WOOL/STRAWBERRY/MELON;
- time-varying private-stock reserves;
- shed-pressure reserve cuts;
- price-gated bounded sale tranches;
- town-shop demand raises reserves and price gates;
- public-market-flow memory with exponential decay;
- inferred external supply from market-inventory delta, prior own sale and public town demand;
- public-capacity and near-mirror signals modify release thresholds;
- no direct reconstruction of opponent private commodity stock.

This is the closest architectural complement to the CR086 opponent-inventory estimator. Its public-flow signal estimates recent external supply pressure; our validated representation estimates hidden current opponent stock/range. These signals are related but non-identical.

### 3. Lynn Sakurai — Farming Score V3 Replay Revised

The notebook deterministically produces standalone package SHA-256 `5cde13b09e9506f24b2f5df05719b597fe07ebbb6dead7da12894beda203e419` with `main.py` SHA-256 `d36ae976ad4a6316e6c1a27a5d04e9cc8e30300f21bdd31e749127c67a9311c4`.

Architecture:

- two deterministic routes;
- one route selection at step 360;
- branch uses first unlocked shop, fertilizer market inventory and public rival planted-tile count;
- route differences are localized to turns 360..431;
- 72-turn affordability guard forecasts planned purchases;
- protects future feed/fertilizer/unplaced-animal requirements;
- sells only surplus products, prioritizing higher current prices, to fund the planned block.

This is structurally closest to CR071M/CR083 route-based planning and therefore is less likely to provide a genuinely new representation, though the explicit block-level budget guard is a useful mechanism to benchmark.

### 4. Tetsutani — Shape the Shop Work the Pasture | Kaggriculture

Pulled source is an analytical/visual notebook rather than a standalone agent builder. It is excluded from the frozen direct H2H but remains useful for mechanics/trajectory interpretation.

## Comparison with CR083

CR083 is primarily a deterministic route/tape system with three prefix-compatible route decisions plus market counterplay, room guard, dead-stock liquidation and the mechanically dominated future-seed-demand clamp. Static source inspection finds no explicit opponent/private-stock estimator and no hysteresis controller.

The strongest genuinely new mechanism discovered so far is therefore not another route threshold. It is the combination of:

1. a stronger physical/production backbone or stateful market backbone; and
2. the independently validated CR086 opponent-inventory representation.

## Candidate-design constraint

Do not define CR086 before the frozen H2H benchmark completes.

If a public backbone passes the frozen screen, study that exact backbone first and then test whether opponent-stock features add value under a separately frozen causal intervention. If none passes, use their mechanisms as design evidence but implement a fresh architecture rather than retuning them on the spent benchmark.

No public-code-derived hosted candidate is eligible before explicit provenance/license/attribution review.
