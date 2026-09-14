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

Exact-engine workflow run **34842825909** against `kaggle-environments==1.32.7`:

- 108/108 price-curve checks matched;
- 24/24 BUY/SELL transaction checks matched;
- 90/90 town-carry outcomes matched the microsimulator;
- unchanged-market/demand-zero round trip = exactly 0;
- 56/90 carry cases positive;
- `I0=10000`, `q=90`, demand `7` = **+57** in both engine and microsim.

Decision: mechanics model is sufficiently exact for H1 causal testing. Advance to R1.

## R1 — H1 town-pulse WHEAT overlay — ACTIVE

Build a minimal runtime operator around a PASS-only physical baseline.

Intervention:

- infer step robustly from `step` or `day/hour`;
- buy WHEAT on a currently known town-consumption pulse;
- sell carried WHEAT on the next eligible market turn;
- use only current legal observation/configuration;
- fixed predeclared quantity for the causal proof; no threshold search;
- maintain shed-capacity and affordability safety.

Required controls:

- same environment with PASS-only agent;
- both seats;
- fresh deterministic seeds;
- flat-WHEAT-price null where carry actions still occur but town depletion cannot create appreciation.

PASS requires:

- zero mechanical errors / all episodes DONE;
- intervention actually triggers BUY and SELL;
- positive paired bank delta under default market mechanics in both seats;
- exact zero paired delta in the flat-price null;
- no use of competitor replay data or identity.

R1 does **not** establish prize-class strength. It establishes causal value of the mechanism.

## R2 — H2 opportunity-cost controller

Only after R1 PASS, add:

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
