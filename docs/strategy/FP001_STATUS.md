# FP001 STATUS — first-principles innovation

Updated: 2026-09-14

Authoritative branch: `research/first-principles-economy-v1`.

## Mission

Discover a prize-class Kaggriculture policy from official mechanics, our own experiments and legal runtime state, without using competitor action tapes as policy-construction data.

## Source of truth

Read together:

1. `docs/strategy/FP001_FIRST_PRINCIPLES_INNOVATION_PROTOCOL_2026-09-14.md`
2. `docs/strategy/FP001_ROADMAP.md`
3. `tools/fp001_market_microsim.py`
4. `tools/fp001_engine_parity.py`
5. `candidates/fp001_h1_town_wheat_carry.py`
6. `tools/fp001_h1_causal_test.py`
7. `tools/fp001_h1b_pulse_hold_scan.py`
8. `tools/fp001_h1b_engine_parity.py`
9. `tools/fp001_h8_animal_fertilizer_economics.py`
10. `fp001_h8_control_frontier.py`
11. `candidates/fp001_h8_single_animal_module.py`
12. `tools/fp001_h8_single_animal_runtime_test.py`
13. `candidates/fp001_h8_multi_animal_module.py`
14. `tools/fp001_h8_multi_animal_runtime_test.py`

## Current state

- Parallel branch created from `fix/kaggle-parity-v1`; CR088 remains untouched on its authoritative branch.
- FP001 purity boundary is frozen: zero competitor replay lineage in policy construction.
- **FP0 mechanics parity: PASS.** Exact-engine workflow `34842825909` matched 108 price cases, 24 transaction cases and 90 town-carry cases against `kaggle-environments==1.32.7`.
- **FP1 H1 town-pulse WHEAT runtime proof: PASS.** Workflow `34843184110`; 32 treatment episodes produced mean paired own-bank delta **+916.875**, median **+935**, min **+688**, max **+1120**, exactly symmetric by seat. Flat-price null: 8/8 exactly zero.
- **H1B owned-sale deferral: mechanics PASS.** Exact-engine workflow `34843556192`; 104/104 positive tested cases with exact microsim parity. Strong cases include MILK q50/D7 **+792**, STRAWBERRY q50/D7 **+731**, WOOL q50/D6 **+827**.

## H8 — animal/fertilizer capital engine

### Gate R2A — exact economics PASS

Workflow `34844070131`: SUCCESS.

A 30-day minimum-survival schedule uses 15 WHEAT per animal while every surviving animal exposes one fertilizer per day. Base no-CARE output was GOOSE 27 EGG, COW 12 MILK, SHEEP 9 WOOL. Three-animal raw economics at day 30, after animal purchase, exact WHEAT BUY cost and exact product/FERTILIZER price decay but before pathing/hire logistics, were:

- SHEEP **+10411**;
- COW **+10111**;
- GOOSE **+9544**.

This killed the initial “GOOSE must be best” assumption: horizon, product cadence and action cost matter.

### Gate R2A2-A — exact FEED/CARE control frontier PASS

Workflow `34844616747`: SUCCESS, `H8_CONTROL_FRONTIER_PASS`.

Exact Pareto-frontier sizes at day 30:

- GOOSE: 1147 nondominated states;
- COW: 930;
- SHEEP: 992.

For a 3-animal portfolio, **SHEEP was the best species at every tested action shadow price 0,10,20,30,40,50,60,80 and at horizons 10,20,30 days**. At day 30:

- shadow 0: SHEEP raw/objective **13187**, 187 actions;
- shadow 20: SHEEP objective **9494**, raw 13114, 181 actions;
- shadow 40: SHEEP objective **6019**, raw 12899, 172 actions;
- shadow 60: SHEEP objective **2579**, raw 12899, 172 actions.

Species comparison at day 30 / shadow 40:

- SHEEP objective **6019**;
- COW **4549**;
- GOOSE **3030**.

Important interpretation: this is an exact control/economics result, not a routing result. It says that once FEED/CARE/collection decisions are optimized abstractly, SHEEP dominates the other species across the tested action-price range. It does **not** prove that a physical sheep farm is the best runtime architecture.

### Gate R2A2-B1 — one-animal full runtime logistics PASS

Workflow `34844919444`: SUCCESS, `H8_SINGLE_ANIMAL_RUNTIME_PASS`.

Each species was run through the complete legal chain against PASS, 4 fresh seeds × both seats = 8 episodes/species, including BUY_ANIMAL, structure, pickup/place, real WHEAT BUY/PICKUP/FEED, COLLECT_FERTILIZER, HARVEST, shed/drop timing and market sale. All tested animals survived and every episode was profitable.

Realized own-bank delta vs starting money:

- **COW:** mean **+4721**, median 4765, min 4425, max 4929;
- **SHEEP:** mean **+3593**, median 3543.5, min 3516, max 3769;
- **GOOSE:** mean **+3457**, median 3496.5, min 3317, max 3518.

This is a critical correction: **the exact abstract frontier ranks SHEEP first, but the one-animal runtime module ranks COW first by a wide margin.** Therefore routing, harvest cadence, town-demand timing and realized logistics are decision variables, not implementation details. We must not freeze the production species from the abstract model alone.

The one-animal runs also fully liquidated tested output and had no stranded positive shed inventory at finish.

## Additional official-mechanics conclusions

- BUILD_COOP / BUILD_PASTURE is free; animal purchase is the setup capital.
- Daily HIRE costs follow Fibonacci `1,1,2,3,5,8,13,...` and reset daily.
- SELL/BUY_PRODUCT uses per-unit lockstep quotes from the same pre-commit inventory for both players at each queue slot; there is no inherent seat-0 same-slot price advantage.
- CARE requires FEED to bank a bonus, and pending CARE is paid only on a fed production day.
- A worker may operate from shed-access positions even where the standing tile began locked; this makes cheap daily hands mechanically useful candidates, but their value must be measured rather than assumed.

## Active gate — R2A2-B2 multi-animal realized logistics

Workflow `34846686427` is the current experiment on the first-principles branch.

It tests:

- COW2 with 0 vs 2 daily hands;
- COW3 with 0 vs 2 daily hands;
- COW2+SHEEP1 with 2 hands;
- COW1+SHEEP2 with 2 hands;
- SHEEP3 with 2 hands.

The fixed zero-lineage target tiles are `(4,4)`, `(3,4)`, `(4,3)`. Setup is done by the main farmer before hired labor is allowed, so the test charges actual movement rather than granting free initial placement. The 0-vs-2-hand ablations directly measure labor value.

## Decision rule after B2

1. If 3-animal runtime remains strongly profitable and 2 hands add positive realized value, promote the best B2 architecture to B3 with CARE-aware control and detailed realized-vs-model attribution.
2. If COW remains runtime-best despite SHEEP's abstract frontier advantage, prioritize COW as the physical backbone and treat SHEEP as a later marginal-capacity candidate.
3. If mixed portfolios dominate pure species, keep species selection dynamic instead of freezing a monoculture.
4. If multiple animals collapse under movement/task congestion, stop scale-up and retain the proven one-animal module as the physical primitive.

## H1/H1B integration

Both market alphas remain preserved. They are not being naively merged yet because H1 consumes productive cash and H1B changes sale timing. After the H8 physical architecture stabilizes, a common controller will price cash, shed space, action/labor and town-pulse timing jointly.

## Hosted policy

No hosted submission is authorized yet. The first-principles track now has real runtime economics, but it still lacks a complete competitive farm policy and population-transfer evidence.
