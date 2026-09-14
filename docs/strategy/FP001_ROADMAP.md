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

Exact-engine workflow `34842825909`: full tested price/transaction/town-carry parity against `kaggle-environments==1.32.7`.

## R1 — H1 town-pulse WHEAT overlay — PASS

Workflow `34843184110`: mean paired own-bank delta **+916.875** across 32 treatment episodes; flat-price null exactly zero.

Decision: preserve as real market alpha, but do not spend productive cash blindly.

## R1B — owned-inventory pulse sale deferral — MECHANICS PASS

Exact-engine workflow `34843556192`: 104/104 positive tested cases. Strong exact gains include MILK q50/D7 +792, STRAWBERRY q50/D7 +731, WOOL q50/D6 +827.

Decision: preserve as sale-timing primitive; account for delayed liquidity and intervening orders before deployment.

## R2A — H8 animal/fertilizer exact economics — PASS

Workflow `34844070131`.

Three-animal day-30 raw economics after animal purchase, exact WHEAT feed cost and exact nonlinear sale curves, before routing/hire costs:

- SHEEP +10411;
- COW +10111;
- GOOSE +9544.

Decision: H8 is large enough to justify an early narrow physical scheduler.

## R2A2-A — exact FEED/CARE Pareto frontier — PASS

Workflow `34844616747`, `H8_CONTROL_FRONTIER_PASS`.

At 3 animals, SHEEP was best at every tested action shadow price 0–80 and horizons 10/20/30 days. Day-30 examples:

- shadow 0: SHEEP raw/objective 13187, 187 actions;
- shadow 40: SHEEP objective 6019, raw 12899, 172 actions;
- shadow 60: SHEEP objective 2579, raw 12899, 172 actions.

Decision: abstract control favors SHEEP, but this is not yet a routing result.

## R2A2-B1 — one-animal full runtime logistics — PASS

Workflow `34844919444`, 4 fresh seeds × both seats per species.

Realized own-bank delta vs PASS baseline:

- COW mean **+4721**, min +4425;
- SHEEP mean **+3593**, min +3516;
- GOOSE mean **+3457**, min +3317.

All animals survived and every episode was profitable.

Critical decision: **physical runtime ranking differs from abstract Pareto ranking.** COW beat SHEEP materially in the one-animal implementation, so species selection must be decided at the realized scheduler level.

## R2A2-B2 — multi-animal realized logistics — ACTIVE

Current workflow: `34846686427`.

### Architectures

- COW2, no hands;
- COW2, 2 daily hands;
- COW3, no hands;
- COW3, 2 daily hands;
- COW2 + SHEEP1, 2 daily hands;
- COW1 + SHEEP2, 2 daily hands;
- SHEEP3, 2 daily hands.

### Physical constraints charged

- fixed first-principles tiles `(4,4)`, `(3,4)`, `(4,3)`;
- main-farmer setup only;
- actual BUY_ANIMAL, pickup, build, movement and placement;
- real shared WHEAT inventory and market cost;
- movement by main farmer and hands;
- actual daily HIRE orders/costs;
- FEED survival deadlines;
- daily fertilizer opportunity loss if collection is missed;
- HARVEST cadence and market liquidation;
- terminal return/drop behavior.

### Required evidence

- both seats, fresh seeds, all episodes DONE;
- all target animals alive at finish;
- positive realized margin in every tested architecture or explicit failure classification;
- movement and hire counts recorded;
- direct labor value from COW2 H2-H0 and COW3 H2-H0;
- ranking of pure COW, pure SHEEP and mixed 3-animal portfolios.

### B2 decision gate

- If 3-animal runtime remains strongly positive and H2 labor helps, advance the best architecture to B3.
- If H0 beats H2, stop assuming cheap hands are valuable and redesign around persistent main-farmer routing.
- If mixed species win, keep the physical production portfolio heterogeneous.
- If COW remains runtime-best, use COW as the first physical backbone despite SHEEP's abstract frontier lead.
- If congestion destroys scale, cap H8 at the largest stable small module rather than forcing expansion.

## R2A2-B3 — control-aware realized attribution — CONDITIONAL NEXT

Only if B2 passes materially.

Add the best exact FEED/CARE policy to the winning physical architecture and decompose realized PnL into:

- animal purchase capital;
- WHEAT spend;
- HIRE spend;
- fertilizer revenue;
- product revenue;
- movement count;
- FEED/CARE/collection/harvest actions;
- missed fertilizer/harvest opportunities;
- shed overflow/discard;
- H1B sale-timing contribution.

PASS requires material improvement over the B2 conservative survival scheduler on fresh seeds without new catastrophe modes.

## R2B — common opportunity-cost controller

After B3, combine the surviving production engine with H1/H1B under shadow prices for:

- cash;
- shed space;
- action/labor;
- remaining horizon;
- current market state;
- deterministic town pulse;
- opponent intervention risk from legal/public state only.

## R3 — adversarial market extensions

Separate experiments: H3 WHEAT input squeeze and H4 premium-sale denial / queue-position response. No seat-specific same-slot price advantage is assumed.

## R4 — event-driven inventory MPC

Generalize hold/sell/buy/abstain decisions over a short horizon.

## R5 — shop-conditioned production economics

Compare the surviving animal engine against crop alternatives from first principles under observed shops and remaining horizon. No replay-derived target counts.

## R6 — full zero-lineage physical scheduler

Expand only after H8/crop economics prove which modules deserve physical capacity.

## R7 — hierarchical agent

Integrate macro planner + physical scheduler + market MPC.

## Hosted policy

No current FP candidate receives a hosted slot yet. Eligibility begins after a complete mechanically valid zero-lineage farm policy clears catastrophe/logistics gates.

## Stop criteria

- Close H1 if cash/shed opportunity cost consumes its alpha.
- Close H1B if intervention/liquidity risk consumes timing value.
- Cap or close H8 scale if multi-animal logistics erase its economics.
- Do not rescue a failed first-principles hypothesis by importing competitor routes.
