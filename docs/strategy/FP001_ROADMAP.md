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

## R0 — FP0 mechanics parity — ACTIVE

Deliverables:

- reproduce official price curves;
- reproduce BUY_PRODUCT post-buy quote semantics;
- reproduce SELL pre-sell quote semantics;
- prove unchanged-market WHEAT BUY->SELL PnL = 0;
- compare microsim outputs against exact `kaggle-environments==1.32.7` deterministic cases.

PASS -> R1. FAIL -> repair simulator only; do not infer strategy.

## R1 — H1 town-pulse WHEAT overlay

Build a minimal runtime operator around a fixed physical baseline.

Intervention:

- buy WHEAT only immediately before mechanically known town-consumption pulses;
- sell the carried quantity at the next eligible market turn;
- include strict cash/shed safety bounds;
- log attributed cost, town demand, sale revenue and delta.

Required controls:

- same seed/base without carry;
- demand-zero regime;
- both seats.

PASS requires positive causal bank effect in demand regimes, zero mechanical errors and abstention when conditions are unfavorable.

## R2 — H2 opportunity-cost controller

Add:

- cash reserve / shadow price;
- shed reserve / overflow protection;
- own feed demand;
- remaining horizon;
- current price/inventory state.

Goal: retain carry edge without starving productive investment.

## R3 — adversarial market extensions

Separate experiments, not one combined patch:

- H3 WHEAT input squeeze against market-fed animal capacity;
- H4 premium-sale denial under relative-bank objective.

Each extension competes against the non-adversarial H2 controller. Close any extension that adds tail risk without repeatable relative-value gain.

## R4 — H5 inventory MPC

Generalize market actions to a short-horizon event-driven optimizer over hold/sell/buy/abstain decisions and deterministic current-shop demand.

## R5 — H6 shop-conditioned production economics

Build marginal value models per crop/animal/land/action under the observed shop multiset and remaining horizon. Do not use replay-derived target counts.

## R6 — zero-lineage physical scheduler

Only after the economic model demonstrates signal. Implement task generation and movement/action scheduling for watering, feeding, harvest, care, fertilizer, planting and structures.

## R7 — H7 hierarchical agent

Integrate macro planner + physical scheduler + market MPC.

## Hosted policy

A mechanically valid, causally distinct FP candidate may receive a hosted sensor earlier than a locally dominant replay-lineage candidate because hosted transfer is the true objective and local ordering is known to miscalibrate.

## Stop criteria

Stop the market-only track if R1-R4 cannot produce repeatable causal value after opportunity costs. Stop sabotage extensions independently if they fail. Do not contaminate the track with copied routes as a rescue mechanism.
