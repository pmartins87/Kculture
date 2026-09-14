# FP001 ROADMAP — first-principles economy

Updated: 2026-09-14

Objective: produce a hosted-competitive zero-lineage Kaggriculture agent by deriving policy from game mechanics and runtime state rather than competitor replay imitation.

## Binding rules

- Official environment + our experiments define mechanics.
- Competitor replays may be used only as evaluation opponents, never as teachers or route templates.
- Every stage needs an explicit causal hypothesis and null/control.
- Local H2H filters mechanics/catastrophe; hosted probes measure population transfer.
- Preserve fresh seeds and both seats.
- No identity/rating/EpisodeId/hidden-seed/future/opponent-private runtime features.
- Do not retune failed hypotheses indefinitely.

## R0 — FP0 mechanics parity — PASS

Exact-engine workflow `34842825909` against `kaggle-environments==1.32.7`:

- 108/108 price-curve checks matched;
- 24/24 BUY/SELL transaction checks matched;
- 90/90 town-carry outcomes matched the microsimulator;
- unchanged-market/demand-zero round trip = exactly 0;
- `I0=10000`, q=90, demand 7 = +57 in both engine and microsim.

## R1 — H1 town-pulse WHEAT overlay — PASS

Workflow `34843184110` used PASS-only physical actions and fixed quantity 50.

32 treatment episodes = 16 fresh seeds × both seats:

- mean paired own-bank delta: **+916.875**;
- median: **+935**;
- min: **+688**;
- max: **+1120**;
- symmetric by seat;
- zero mechanical errors;
- matched BUY/SELL quantities.

Flat-price causal null: 8/8 exact **0.0** delta despite active carry trades.

Decision: H1 is a genuine runtime-accessible economic edge. Do not equate PASS-baseline delta with production-agent value because productive cash has opportunity cost.

## R1B — owned-inventory town-pulse sale deferral — MECHANICS PASS

Analytical workflow `34843505162`: PASS.
Exact-engine workflow `34843556192`: PASS, 104/104 positive cases and exact microsim parity.

Canonical q=25 / demand=4 timing gains:

- MILK +241;
- STRAWBERRY +224;
- WOOL +159;
- MELON +62;
- TOMATO +48;
- CARROT +22;
- EGG +21;
- WHEAT +18.

This mechanism avoids BUY capital but delays sale cash by one step and is exposed to intervening opponent market actions. Advance to risk/opportunity-cost evaluation, not blind deployment.

## R2A — first-principles economic ranking — ACTIVE

Before constructing a full physical route, rank the strongest mechanics-derived economic engines under common resource shadow prices.

### Candidate A — H1 WHEAT carry

Known causal value; costs one-turn cash commitment plus shed occupancy.

### Candidate B — H1B sale deferral

Known exact timing value; costs one-step liquidity delay and introduces opponent-intervention risk, but uses already-owned inventory.

### Candidate C — H8 fertilizer flywheel

New mechanics-derived hypothesis:

- free animal structures;
- one fertilizer becomes available each end-of-day for every surviving animal;
- feed is one WHEAT;
- escape requires two consecutive unfed days;
- GOOSE is cheapest animal at 300 and generates the same fertilizer unit as COW/SHEEP.

Required audit:

1. exact engine proof that alternating-day feed preserves the animal and allows daily fertilizer generation;
2. exact fertilizer sale-revenue curve under cumulative supply;
3. capital payback by purchase day and remaining horizon;
4. minimum labor/action budget for build, placement, feed, collect, pickup/drop and sale;
5. shed and WHEAT requirements;
6. egg side-output value without assuming perfect harvesting;
7. sensitivity to opponent fertilizer supply.

Only then may H8 influence the physical planner.

## R2B — opportunity-cost controller

After R2A ranking, implement a shared controller that prices:

- cash reserve / shadow price;
- shed reserve / overflow protection;
- own feed demand;
- action/labor shadow price;
- remaining horizon;
- current price/inventory state;
- known town-demand pulse;
- mechanics-derived uncertainty in opponent market intervention.

The controller chooses among carry, sell-now, defer-sale, hold inventory, or abstain.

## R3 — adversarial market extensions

Separate experiments:

- H3 WHEAT input squeeze against market-fed animal capacity;
- H4 premium-sale denial under relative-bank objective.

Each extension competes against the non-adversarial R2 controller. Close any extension that adds tail risk without repeatable relative-value gain.

## R4 — event-driven inventory MPC

Generalize market decisions into a short-horizon optimizer over hold/sell/buy/abstain with deterministic current-shop demand and resource shadow prices.

## R5 — shop-conditioned production economics

Build marginal value models per crop/animal/land/action under observed shops and remaining horizon. Incorporate H8 only if its exact economics survive R2A. Do not use replay-derived target counts.

## R6 — zero-lineage physical scheduler

Implement task generation and route scheduling from our own economic objectives for watering, feeding, harvest, care, fertilizer, planting, structures and shed logistics.

## R7 — hierarchical agent

Integrate macro planner + physical scheduler + market MPC.

## Hosted policy

A mechanically valid, causally distinct complete FP candidate may receive a hosted sensor before locally dominating replay-lineage agents because hosted transfer is the true objective and local ordering is known to miscalibrate. The current PASS-only H1 causal probe is not a complete candidate and receives no hosted slot.

## Stop criteria

- Close H1 if opportunity-cost-aware integration consumes more productive value than it earns.
- Close H1B if opponent intervention / cash-delay risk removes its timing edge on fresh scenarios.
- Close H8 if fertilizer price decay + labor + feed makes its risk-adjusted marginal return inferior to crop/animal alternatives.
- Stop sabotage extensions independently if they fail.
- Never rescue a failed first-principles hypothesis by importing competitor routes.
