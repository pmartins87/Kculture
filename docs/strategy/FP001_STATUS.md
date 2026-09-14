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

## Current state

- Parallel branch created from `fix/kaggle-parity-v1`.
- CR088 remains untouched on its authoritative branch.
- FP001 purity boundary is frozen: zero competitor replay lineage in policy construction.
- First mechanism selected: **town-pulse WHEAT carry**.
- Standalone market microsimulator created.
- Exact-engine parity workflow run **34842825909** completed **SUCCESS** against `kaggle-environments==1.32.7`.
- FP0 result: **PASS**.
- Exact checks: 108 market-price cases, 24 BUY/SELL transaction cases, 90 town-carry cases.
- 56/90 town-carry cases were positive; demand-zero cases remained exactly zero.
- Canonical check `I0=10000`, `q=90`, town WHEAT demand `7`: exact-engine PnL **+57**, identical to microsim.
- Therefore H1 is a real engine mechanic, not a microsimulation artifact.

## Priority hypotheses

1. H1 town-pulse WHEAT carry.
2. H2 cash/shed-aware WHEAT carry.
3. H3 input squeeze / animal-tax extension.
4. H4 premium-sale denial under relative-bank objective.
5. H5 event-driven inventory MPC.
6. H6 shop-conditioned production portfolio.
7. H7 hierarchical zero-lineage agent.

## Current gate

**FP1 — causal runtime proof.**

Build and test a legal runtime agent that changes only WHEAT market actions around known town-demand pulses. Physical actions remain PASS so every reward delta is attributable to H1.

Required evidence:

- both seats;
- fresh deterministic seeds;
- zero mechanical errors;
- actual BUY and SELL triggers;
- positive reward delta under default town demand;
- zero-delta null under a flat WHEAT price curve despite identical carry actions.

## Next action

Implement `fp001_h1_town_wheat_carry.py` and its exact-environment FP1 causal harness. Do not introduce cash-shadow-price tuning or production logic until FP1 closes.
