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

Workflow `34843184110`, 32 treatment episodes, mean paired own-bank delta **+916.875**, min **+688**, max **+1120**, symmetric seats. Flat-price null 8/8 exactly zero.

Decision: real market alpha; defer production integration until cash/shed opportunity cost is priced.

## R1B — owned-inventory pulse sale deferral — MECHANICS PASS

Analytical workflow `34843505162` and exact-engine workflow `34843556192` PASS. Strong exact timing gains include MILK q50/D7 +792, STRAWBERRY q50/D7 +731 and WOOL q50/D6 +827.

Decision: real timing primitive; deployment must account for delayed liquidity and intervening opponent orders.

## R2A — H8 animal/fertilizer economics — PASS

Workflow **`34844070131`** exact-engine audit.

Minimum-survival feeding over 30 days:

- every species survives on 15 WHEAT;
- every species generates 30 fertilizer;
- GOOSE produces 27 EGG, COW 12 MILK, SHEEP 9 WOOL in the tested base/no-CARE schedule.

Three-animal raw PnL after animal purchase, exact WHEAT buy cost and exact fertilizer/product price decay:

- day 5: GOOSE +708, COW +119, SHEEP -181;
- day 10: GOOSE +2570, COW +2228, SHEEP +2195;
- day 15: SHEEP +4582, GOOSE +4447, COW +4294;
- day 20: COW +6506, SHEEP +6227, GOOSE +6173;
- day 25: SHEEP +8432, COW +8284, GOOSE +7931;
- day 30: SHEEP +10411, COW +10111, GOOSE +9544.

At n=3/day30, lower-bound action-shadow break-even is ~61.6 for SHEEP, 56.8 COW, 42.8 GOOSE. Therefore species choice is horizon/action-budget dependent; do not freeze a goose-only architecture.

## R2A2 — animal-control frontier + logistics feasibility — ACTIVE

The evidence changes the earlier roadmap: H8 is too economically large to leave physical scheduling until R6. We now permit a **narrow first-principles animal scheduler** solely to price the missing logistics costs. This does not authorize a full farm architecture yet.

### Gate A — exact FEED/CARE control frontier

Use exact engine transitions and dynamic programming / Pareto enumeration, not a hand-picked schedule.

State must include at least:

- `consecutive_unfed`;
- `pending_care_bonus`;
- production clock / day;
- alive/dead;
- accumulated product/fertilizer;
- feed units and action count.

Controls may include only mechanics-relevant choices: NONE, FEED, FEED+CARE; CARE without FEED is dominated for bonus generation.

Report optimal policies under multiple action shadow prices and horizons for GOOSE/COW/SHEEP. Account for exact nonlinear market revenue when portfolio output is sold.

### Gate B — narrow runtime logistics proof

Build a zero-lineage deterministic scheduler for a small animal module (start 1–3 animals) that can execute:

- free structure build;
- BUY_ANIMAL / pickup / place;
- WHEAT acquisition or own-feed consumption;
- movement;
- FEED and CARE when selected by the control policy;
- COLLECT_FERTILIZER;
- HARVEST;
- shed drop / overflow safety;
- market sale with H1B-aware timing when beneficial.

Use no crop route and no competitor route. Both seats, fresh seeds, zero errors.

### Gate C — realized-vs-model attribution

For each runtime episode decompose:

- animal purchase capital;
- WHEAT spend;
- hire spend;
- product/fertilizer realized revenue;
- movement/action count;
- missed collection/harvest;
- shed overflow/discard;
- idle time;
- H1B timing contribution.

PASS if a small animal module retains a material fraction of mechanics-level economics after actual logistics and is stable in both seats.

FAIL/STOP if movement/task congestion destroys the economics, animals escape materially, or realized margin cannot beat simpler production alternatives after fresh tests.

## R2B — common opportunity-cost controller

After R2A2, combine the surviving production engine with H1/H1B under shadow prices for:

- cash;
- shed space;
- action/labor;
- remaining horizon;
- current market state;
- deterministic town pulse;
- opponent-market intervention risk derived only from current legal/public state.

## R3 — adversarial market extensions

Separate experiments:

- H3 WHEAT input squeeze;
- H4 premium-sale denial / queue-position response.

No seat-specific same-slot price advantage is assumed: official market processing quotes both players from the same pre-commit inventory per unit. Queue position across distinct order slots remains causal.

## R4 — event-driven inventory MPC

Generalize market decisions into short-horizon hold/sell/buy/abstain optimization.

## R5 — shop-conditioned production economics

Compare animal module against crop alternatives from first principles under observed shops and remaining horizon. No replay-derived target counts.

## R6 — full zero-lineage physical scheduler

Expand only after R2A2/R5 prove which economic modules deserve physical capacity.

## R7 — hierarchical agent

Integrate macro planner + physical scheduler + market MPC.

## Hosted policy

No current FP primitive receives a hosted slot. A hosted sensor becomes eligible only after a complete mechanically valid zero-lineage farm policy exists and passes catastrophe/logistics gates.

## Stop criteria

- Close H1 if cash/shed opportunity cost consumes its alpha.
- Close H1B if intervention/liquidity risk consumes timing value.
- Close H8 if CARE/feed optimization plus real logistics cannot preserve material economics.
- Do not rescue a failed first-principles hypothesis by importing competitor routes.
