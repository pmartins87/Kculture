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

## Current state

- Parallel branch created from `fix/kaggle-parity-v1`; CR088 remains untouched on its authoritative branch.
- FP001 purity boundary is frozen: zero competitor replay lineage in policy construction.
- **FP0 mechanics parity: PASS.** Exact-engine workflow `34842825909` matched 108 price cases, 24 transaction cases and 90 town-carry cases against `kaggle-environments==1.32.7`.
- **FP1 H1 town-pulse WHEAT runtime proof: PASS.** Workflow `34843184110` completed with zero mechanical errors.
- H1 used a PASS-only physical policy and fixed `TARGET_QTY=50`; the only treatment was WHEAT BUY_PRODUCT on known town pulses and SELL on the next turn.
- Across 16 fresh seeds × both seats = 32 treatment episodes, paired own-bank delta vs PASS was mean **+916.875**, median **+935**, min **+688**, max **+1120**, exactly symmetric by seat.
- Flat-WHEAT-price causal null: 8/8 episodes exactly **0.0** delta despite active carry trades. H1 is causally attributable to town-induced price movement.
- H1 is economically real but the PASS experiment has no productive cash opportunity cost. It is **not yet a production-ready +917 claim**.

## H1B — delay owned sales across town demand — mechanics PASS

Analytical workflow `34843505162`: **PASS**.
Exact-engine workflow `34843556192`: **PASS**, 104/104 tested cases positive and exactly equal to the microsimulator.

Canonical exact-engine gains for quantity 25 and demand 4:

- MILK: **+241**;
- STRAWBERRY: **+224**;
- WOOL: **+159**;
- MELON: **+62**;
- TOMATO: **+48**;
- CARROT: **+22**;
- EGG: **+21**;
- WHEAT: **+18**.

Large exact cases include MILK q50/D7 **+792**, STRAWBERRY q50/D7 **+731**, WOOL q50/D6 **+827**. Real deployment must price one-step cash delay and opponent same/next-step sale risk.

## H8 — animal/fertilizer capital engine — exact economics PASS

Workflow **`34844070131`**: **SUCCESS** against exact `kaggle-environments==1.32.7`.

The audit used exact engine helpers, minimum-survival feeding, daily fertilizer collection, base animal product only, no CARE bonus, no town-demand credit for animal products, exact WHEAT BUY cost, exact product/FERTILIZER SELL curves, and explicit lower-bound action counts. No competitor data or route was used.

### Exact mechanics proven

For every species, a 30-day minimum-survival schedule fed **15 WHEAT**, generated **30 fertilizer**, and survived. Base products over the same slice were:

- GOOSE: 27 EGG, 72 recurring actions;
- COW: 12 MILK, 57 recurring actions;
- SHEEP: 9 WOOL, 54 recurring actions.

This confirms that alternating-day survival feed can coexist with daily fertilizer generation. It also disproves the early assumption that GOOSE is automatically the best fertilizer machine: species ranking changes with horizon, scale and action shadow price because animal products and action cadence differ.

### Three-animal portfolios, raw exact economics

These values include animal purchase cost, exact market WHEAT feed cost, exact fertilizer/product price decay and base product revenue, but exclude routing/movement, actual hires, cashflow timing, land opportunity cost, shed congestion and opponent market pressure.

At 5 days:

- GOOSE **+708**;
- COW **+119**;
- SHEEP **-181**.

At 10 days:

- GOOSE **+2570**;
- COW **+2228**;
- SHEEP **+2195**.

At 15 days:

- SHEEP **+4582**;
- GOOSE **+4447**;
- COW **+4294**.

At 20 days:

- COW **+6506**;
- SHEEP **+6227**;
- GOOSE **+6173**.

At 25 days:

- SHEEP **+8432**;
- COW **+8284**;
- GOOSE **+7931**.

At 30 days:

- SHEEP **+10411**;
- COW **+10111**;
- GOOSE **+9544**.

For n=3/day30, raw PnL can tolerate a lower-bound action shadow price of roughly **61.6/SHEEP action**, **56.8/COW**, **42.8/GOOSE** before going to zero. This makes the long-horizon COW/SHEEP line materially more action-efficient than GOOSE despite higher capital cost.

### Scale effect

The largest raw tested portfolio was GOOSE n=8/day30 at **+21150**, but this is not proof that eight geese are deployable or optimal. With starting cash 3000, setup liquidity, routing, shed capacity, hires and opponent supply become binding. The scale result only establishes large mechanics-level headroom.

## Additional official-mechanics conclusions

- BUILD_COOP / BUILD_PASTURE is free; the animal itself consumes the setup capital.
- Daily HIRE costs follow Fibonacci `1,1,2,3,5,8,13,...` and reset every day, so early additional labor is cheap in cash but still consumes movement/action capacity.
- Market SELL/BUY_PRODUCT is per-unit lockstep: both players are quoted from the same pre-commit inventory at a given queue slot. There is **no intrinsic seat-0 price advantage** for equivalent same-slot orders. Queue position across different market-order slots remains economically causal.
- CARE requires FEED to bank a bonus, and a pending CARE bonus is consumed only on a **fed production day**. If the production day is unfed, the bonus is not paid and is then cleared. Therefore the optimal animal policy must synchronize FEED/CARE with production ticks rather than blindly feed every day or alternate days.

## Priority now

1. **H8 CARE/feed optimization:** derive the Pareto-optimal daily control schedule for each animal using exact mechanics, not hand-tuned heuristics.
2. **H8 logistics proof:** construct a small zero-lineage runtime farm capable of buying, placing, feeding, collecting, harvesting, dropping and selling animals/products/fertilizer; measure real movement/hire/cashflow losses.
3. **H1/H1B integration:** preserve both proven market alphas for a later common opportunity-cost controller; do not spend productive cash on H1 when its shadow value exceeds carry profit.
4. Build production architecture from mechanics-derived marginal return per cash/tile/action, not competitor route counts.

## Current gate

**R2A2 — animal-control frontier + logistics feasibility.**

H8 has survived the pure economics audit and now has more raw upside than H1/H1B, but it cannot be promoted from spreadsheet-like economics to strategy until actual control and logistics are proven. The next gate therefore allows a deliberately narrow physical scheduler earlier than originally planned.

## Hosted policy

No hosted submission is authorized yet. The H1 PASS-only agent is intentionally noncompetitive, H1B is a timing primitive rather than a farm, and H8 has not yet paid its real movement/logistics costs.
