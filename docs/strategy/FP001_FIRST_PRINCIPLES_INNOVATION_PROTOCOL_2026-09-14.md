# FP001 — First-Principles Innovation Protocol

Date: 2026-09-14  
Branch: `research/first-principles-economy-v1`

## 2026-09-14 integration amendment — binding

This document began as an intentionally isolated **zero-lineage experimental protocol**. That isolation remains useful when a causal experiment needs clean attribution, but it is **no longer a global restriction on the final competition policy**.

The competition-level objective is to win / maximize prize probability. Therefore:

- knowledge already acquired from opponent testing, public replays, top-player analysis, copied/derived baselines, hosted probes, failures and successful heuristics is cumulative and must not be discarded;
- legal competitor evidence may be used as policy-construction input, architecture prior, comparator or adaptation signal;
- FP001's purpose is to contribute new causally proven mechanics/economic primitives to that accumulated stack;
- a mechanism is not promoted because it is novel, and an older mechanism is not rejected because it is derivative;
- the final criterion is expected population/hosted strength under competition legality.

Where this historical protocol below says “zero-lineage”, “forbidden as policy-construction input”, “never as teachers” or “no replay-derived route backbone”, read those restrictions as applying to **experiments explicitly designated as isolated FP causal tests**, not to the integrated winning-policy track. Current binding integration gates live in `FP001_ROADMAP.md` and the competition-level `STATUS.md` / `ROADMAP.md` on `fix/kaggle-parity-v1`.

## Purpose

Open a research front whose original objective was to discover prize-class Kaggriculture mechanisms from the game mechanics and economics themselves, rather than merely reproducing competitor replay lineages.

The experimental distinction from CR088 remains useful: CR088 mines current population structure and tests operators over coherent top-lineage bases; FP001 isolates mechanics/economics so we can tell **why** something works. The two tracks are now explicitly complementary and are expected to be integrated.

## Experimental isolation boundary

When a gate is labeled **isolated FP**, allowed design inputs are:

- official `kaggle-environments==1.32.7` rules/source;
- our own Kculture experiments and diagnostics;
- current observation available legally to the agent;
- mechanics-derived simulation, optimization, control and game-theory reasoning;
- opponent public farm state and shared market/town state at runtime.

For those isolated attribution tests only, do not:

- copy/replay another team's action tape as the treatment itself;
- select physical actions by nearest-neighbour replay matching;
- use team/opponent identity, rating, submission ID, EpisodeId or hidden seed;
- use future state or opponent-private runtime state;
- rescue a failed causal hypothesis by silently switching to a replay-derived route.

Outside an explicitly isolated gate, legal public/top-player evidence is available to the integrated competition program according to the live project roadmap.

## Why this track exists

The authoritative project state shows that action-level imitation alone has poor transfer, local H2H ordering is not a reliable proxy for hosted population strength, and the current top-10 is materially state-adaptive. Therefore another replay reconstruction ladder by itself is not a sufficient path to ~3000+ hosted strength.

FP001 attacks the underlying game as a stochastic two-player economy and provides primitives that can strengthen coherent competitive backbones.

## Core economic observation

The market is not merely a liquidation endpoint.

`WHEAT` and `FERTILIZER` are purchasable assets. Produce prices are deterministic functions of shared market inventory. Town demand removes inventory at known periodic times, while shop composition is observable after unlock. The engine processes player market orders first and town demand afterward. Therefore the player can hold market inventory across a known demand pulse and potentially monetize the deterministic inventory reduction.

The official quote convention also guarantees that an otherwise unchanged BUY_PRODUCT -> SELL round trip is exactly zero, which gives a clean null baseline for testing exogenous-demand carry.

## FP001 hypothesis portfolio

### H1 — Town-pulse WHEAT carry

Buy WHEAT immediately before a known town consumption pulse, hold it through the pulse, then sell on the next market opportunity when the market inventory is lower.

Economic intuition:

- own BUY decreases market inventory and transfers cash into a resellable asset;
- town demand then decreases inventory further at no cost to us;
- the next SELL realizes the price appreciation caused by exogenous demand;
- if no town/opponent inventory change occurs, the engine's quote convention should make the round trip exactly zero.

This was selected first because it has a mechanics-guaranteed zero-demand control and does not require predicting a competitor.

### H2 — Regime-aware WHEAT carry

Generalize H1 by optimizing quantity from:

- current WHEAT market inventory/price;
- exact currently unlocked shop demand per pulse;
- cash shadow price for production/land/hiring;
- shed-capacity shadow price;
- own near-term feed requirement;
- estimated opponent net WHEAT market pressure from observable/legal state.

The carry is permitted only when its conservative expected relative value beats the shadow cost of cash and storage.

### H3 — Input squeeze / animal-tax strategy

When the opponent has visible animal capacity and evidence indicates likely market-fed WHEAT dependence, strategically hold/buy WHEAT to increase the shared WHEAT scarcity price.

The objective is **relative bank gap**, not merely own gross profit. Inventory can later be used as feed or liquidated.

Gate: must beat a pure profit-only WHEAT carry under fresh adversarial seeds; otherwise close the sabotage extension and retain H1/H2 only.

### H4 — Premium-sale denial

Premium resources have extremely steep glut-side price curves. If our visible/estimated state implies that a later opponent premium sale is likely, an earlier partial sale can depress the price faced by that later sale.

The correct objective is not `maximize own sale revenue`; it is approximately:

`own realized value - inventory shadow value + expected opponent revenue denied`.

This is potentially rational even when the chosen sale is earlier/larger than an absolute-profit maximizer would choose.

Gate: require causal improvement in paired money-gap / W-L against multiple mechanically different opponents. A microsim immediate-gap gain alone is insufficient.

### H5 — Event-driven inventory MPC

Build a small exact/approximate model-predictive controller over:

- own shed inventory;
- current market inventory and price curve;
- deterministic town pulses from already-unlocked shops;
- future shop unlock uncertainty;
- cash deadlines for land/seeds/animals/hires;
- shed-capacity/overflow risk;
- final liquidation deadline.

Actions: hold, sell quantity, buy WHEAT/FERTILIZER, or abstain.

This controller should output market decisions from state rather than blindly replaying step-indexed market commands.

### H6 — Shop-conditioned production portfolio

At day boundaries, recompute production targets from marginal expected value per tile/action/cash unit under the observed shop multiset and remaining horizon.

The planner should explicitly price:

- scarcity value created by shop demand;
- premium-product glut risk;
- land cost;
- watering/feed/care labor;
- hire cost;
- shed capacity;
- fertilizer conversion value;
- time to first yield and remaining harvest cycles.

### H7 — Hierarchical integrated agent

Integrate successful primitives under layers such as:

1. macro production/economic planner, informed by mechanics **and legal competitive priors**;
2. deterministic/state-adaptive task scheduler for movement, watering, feeding, harvest, care, fertilizer and land;
3. market controller for inventory, timing, adversarial price impact and final liquidation;
4. population/hosted calibration loop using diverse coherent competitive representatives.

For isolated attribution experiments, keep replay-derived physical backbones out of the treatment. For final competition architecture, the live roadmap governs and prior competitive knowledge is allowed.

## Initial analytical result

`tools/fp001_market_microsim.py` was created from the official price curves and BUY/SELL quote semantics.

Self-test requirement:

- unchanged-market WHEAT BUY->SELL round trip = exactly 0 for representative inventories/quantities.

Illustrative mechanics-only checks from `I0=10000`:

- q=25 before a town pulse: demand 1/2/4/7 gives +4/+8/+14/+24 coins;
- q=50: +6/+12/+22/+37;
- q=90: +9/+18/+34/+57.

These were never candidate-performance claims; they establish that official mechanics admit positive temporal carry when exogenous town demand occurs between buy and sell.

## Experimental gates — historical foundation

### Gate FP0 — mechanics parity

PASS only if the microsim reproduces official price and quote behavior on deterministic cases, including zero-demand round-trip = 0.

### Gate FP1 — H1 causal environment proof

Build a minimal legal runtime overlay that changes only WHEAT BUY/SELL around deterministic town pulses.

Compare base vs overlay under identical seeds and both seats with physical actions held fixed.

PASS requires zero mechanical errors, actual interventions, positive own-bank causal delta in demand regimes, and safe abstention when demand is insufficient.

### Gate FP2 — cash/storage opportunity-cost proof

Add cash and shed shadow prices. Compare against H1 naive carry. PASS only if the constrained controller improves/preserves outcomes while reducing production starvation/overflow cases.

### Gate FP3 — adversarial opponent panel

For an isolated mechanism test, evaluate against a heterogeneous exact-agent set without changing the treatment based on their action tapes mid-gate.

Metrics include paired W/L, relative bank, tail risk, intervention attribution, starvation, overflow and price impact.

### Gate FP4 — hosted sensor

Only after mechanical validity and causal evidence. Hosted transfer is the population calibration instrument; a distinct valid candidate may deserve a high-information hosted probe without needing to beat every local anchor.

### Gate FP5 — architecture expansion

Historical gate now superseded by the integrated `FP001_ROADMAP.md`: architecture expansion is active because multiple mechanisms have already passed, including CARE, batched harvest, fertilizer conversion and scale/capacity tests.

## Current stop rules

- Do not mutate thresholds endlessly on the same seeds.
- In isolated FP gates, do not rescue a failed hypothesis by importing replay actions after seeing the result.
- In integrated gates, **do** use accumulated competitive knowledge deliberately and transparently when it creates a better architecture or prior.
- Close H1 if exact tests show no positive causal value after cash/storage costs across meaningful demand regimes.
- Close H3/H4 if relative-value sabotage adds tail risk without repeatable paired benefit.
- Keep mechanisms modular enough for attribution.
- Preserve fresh held-out seed blocks for promoted stages.
- Do not continue a branch merely to preserve novelty; redirect effort to the highest-information path toward a winning hosted policy.

## Current implementation pointer

The historical “first deliverable” sequence is complete and several later mechanisms have passed. Current work is defined by `FP001_ROADMAP.md`: integrated premium-crop/animal hybrids, labor revaluation, elite-macro compatibility, heterogeneous population testing and hosted calibration.
