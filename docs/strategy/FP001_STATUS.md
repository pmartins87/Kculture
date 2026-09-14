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

## Current state

- Parallel branch created from `fix/kaggle-parity-v1`.
- CR088 remains untouched on its authoritative branch.
- FP001 purity boundary is frozen: zero competitor replay lineage in policy construction.
- First mechanism selected: **town-pulse WHEAT carry**.
- Standalone market microsimulator created and locally self-checked before commit.
- Required null behavior: unchanged-market WHEAT BUY->SELL round trip is exactly zero.
- Mechanics-only town-pulse examples are positive; these are analytical evidence only, not candidate-performance evidence.
- GitHub Actions self-test workflow added.

## Priority hypotheses

1. H1 town-pulse WHEAT carry.
2. H2 cash/shed-aware WHEAT carry.
3. H3 input squeeze / animal-tax extension.
4. H4 premium-sale denial under relative-bank objective.
5. H5 event-driven inventory MPC.
6. H6 shop-conditioned production portfolio.
7. H7 hierarchical zero-lineage agent.

## Current gate

**FP0 — mechanics parity.**

No runtime candidate may be promoted until the microsimulator is checked against exact `kaggle-environments==1.32.7` deterministic environment cases.

## Next action

Implement exact-environment parity tests and then a minimal H1 overlay that changes only WHEAT market actions around known town-demand pulses while keeping physical actions fixed.
