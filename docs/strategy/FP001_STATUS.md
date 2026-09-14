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

## Current state

- Parallel branch created from `fix/kaggle-parity-v1`; CR088 remains untouched on its authoritative branch.
- FP001 purity boundary is frozen: zero competitor replay lineage in policy construction.
- **FP0 mechanics parity: PASS.** Exact-engine workflow `34842825909` matched 108 price cases, 24 transaction cases and 90 town-carry cases against `kaggle-environments==1.32.7`.
- **FP1 H1 town-pulse WHEAT runtime proof: PASS.** Workflow `34843184110` completed with zero mechanical errors.
- H1 used a PASS-only physical policy and fixed `TARGET_QTY=50`; the only treatment was WHEAT BUY_PRODUCT on known town pulses and SELL on the next turn.
- Across 16 fresh seeds × both seats = 32 treatment episodes, paired own-bank delta vs PASS was:
  - mean **+916.875**;
  - median **+935**;
  - min **+688**;
  - max **+1120**;
  - seat 0 and seat 1 summaries were exactly identical.
- H1 intervention triggered 2,475 BUY and 2,475 SELL orders per seat block, with matched total bought/sold quantity.
- Flat-WHEAT-price causal null: 8/8 episodes exactly **0.0** delta despite 1,200 BUY and 1,200 SELL triggers. Therefore the observed H1 gain is causally attributable to town-induced price movement, not route or unrelated state changes.
- H1 is economically real but the PASS experiment has no productive cash opportunity cost. It is **not yet a production-ready +917 claim**.

## H1B — delay owned sales across town demand — PASS at mechanics layer

Hypothesis: when we already own a product, postponing its sale from the pulse step to the next step lets town demand lower shared inventory first. Around normal prices, the immediate-sale and delayed-sale paths end with the same market inventory, so the revenue difference is pure timing value when no opponent trade intervenes.

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

Large exact cases include MILK q50/D7 **+792**, STRAWBERRY q50/D7 **+731**, WOOL q50/D6 **+827**. These are isolated timing effects, not population-performance claims. Real deployment must price one-step cash delay and opponent same/next-step sale risk.

## New first-principles production hypothesis — H8 fertilizer flywheel

Official mechanics audit shows:

- animal structures are free to build;
- every surviving animal sets `fertilizer_available=True` at end of day;
- `COLLECT_FERTILIZER` yields one fertilizer and clears that flag;
- an animal escapes only after two consecutive unfed days;
- therefore feeding on alternating days appears sufficient for survival while fertilizer remains available every surviving day;
- all animal species generate the same fertilizer unit, while GOOSE has the lowest purchase cost (300 vs COW 400 vs SHEEP 500).

This creates a candidate economic mechanism: **GOOSE as fertilizer-producing capital equipment**, with eggs as secondary output rather than the primary thesis. It must be quantified including WHEAT feed, labor/movement, fertilizer price decay, shed capacity and setup capital before promotion.

## Priority now

1. Preserve H1 as proven market alpha but do not integrate naively; build an opportunity-cost-aware controller.
2. Promote H1B to a separate runtime-risk experiment because its per-event upside can dominate H1 without tying up buy capital.
3. Quantify H8 fertilizer flywheel before committing to a physical farm architecture.
4. Choose the next production architecture from mechanics-derived marginal return per cash/tile/action — not from competitor route counts.

## Current gate

**R2A — economic ranking of first-principles mechanisms.**

Before building the full zero-lineage scheduler, compare H1, H1B and H8 under common shadow prices for cash, shed space and actions. H1/H1B are already causally proven at the mechanics layer; H8 must first receive an exact mechanics/ROI audit.

## Next action

Build the H8 exact-engine economics audit, then update the R2 controller design around the highest-value mechanisms. No hosted submission is authorized yet; the H1 PASS-only probe is intentionally noncompetitive as a full farm policy.
