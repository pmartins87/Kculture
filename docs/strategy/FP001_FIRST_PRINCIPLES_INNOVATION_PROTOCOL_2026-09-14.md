# FP001 — First-Principles Innovation Protocol

Date: 2026-09-14  
Branch: `research/first-principles-economy-v1`

## Purpose

Open a parallel research front whose objective is to discover a prize-class Kaggriculture policy from the game mechanics and economics themselves, rather than from competitor replay lineages.

This track deliberately differs from CR088. CR088 is allowed to mine current population structure and test operators over coherent top-lineage bases. FP001 is a **zero-lineage design track**: the policy architecture, objectives and operators must be derivable from the official environment, our own experiments and general optimization/game-theory reasoning.

## Purity boundary

Allowed design inputs:

- official `kaggle-environments==1.32.7` rules/source;
- our own Kculture experiments and diagnostics;
- current observation available legally to the agent;
- mechanics-derived simulation, optimization, control and game-theory reasoning;
- opponent public farm state and shared market/town state at runtime.

Forbidden as policy-construction inputs:

- copying or replaying another team's 719/720-action tape;
- using competitor action sequences as a route template;
- selecting physical actions from nearest-neighbour replay matching;
- team/opponent identity, rating, submission ID, EpisodeId or hidden seed;
- future state or opponent-private runtime state;
- tuning a mechanic because a named top team happens to use it.

Public/top agents may later be used only as **adversarial evaluation opponents**, never as teachers.

## Why this track exists

The current authoritative project state shows that action-level imitation has poor transfer, local H2H ordering is not a reliable proxy for hosted population strength, and the current top-10 itself is materially state-adaptive. Therefore, another replay reconstruction ladder is not a sufficient path to ~3000+ hosted strength.

FP001 attacks the underlying game as a stochastic two-player economy.

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

This is the first hypothesis to test because it has a mechanics-guaranteed zero-demand control and does not require predicting a competitor.

### H2 — Regime-aware WHEAT carry

Generalize H1 by optimizing quantity from:

- current WHEAT market inventory/price;
- exact currently unlocked shop demand per pulse;
- cash shadow price for production/land/hiring;
- shed-capacity shadow price;
- own near-term feed requirement;
- estimated opponent net WHEAT market pressure from observable market deltas.

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

This controller should output market decisions from state, not from step-indexed replay commands.

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

This is a larger architecture and should not start until the market-only hypotheses have been isolated.

### H7 — Hierarchical first-principles agent

If H1-H6 establish useful operators, integrate them under three layers:

1. macro economic planner (daily target capacities and cash budget);
2. deterministic task/route scheduler (movement, watering, feeding, harvest, care, fertilizer, land use);
3. market MPC (inventory, timing, adversarial price impact, final liquidation).

No replay-derived route backbone is allowed.

## Initial analytical result

`tools/fp001_market_microsim.py` was created from the official price curves and BUY/SELL quote semantics.

Self-test requirement:

- unchanged-market WHEAT BUY->SELL round trip = exactly 0 for representative inventories/quantities.

Illustrative mechanics-only checks from `I0=10000`:

- q=25 before a town pulse: demand 1/2/4/7 gives +4/+8/+14/+24 coins;
- q=50: +6/+12/+22/+37;
- q=90: +9/+18/+34/+57.

These are **not candidate-performance claims**. They simply establish that the official market mechanics admit positive temporal carry when exogenous town demand occurs between the buy and sell.

The same tool contains a premium sequential-sale impact diagnostic, but that metric intentionally omits the shadow value of our inventory and cannot authorize H4 promotion.

## Experimental gates

### Gate FP0 — mechanics parity

PASS only if the microsim reproduces official price and quote behavior on deterministic cases, including zero-demand round-trip = 0.

### Gate FP1 — H1 causal environment proof

Build a minimal legal runtime overlay that changes only WHEAT BUY/SELL around deterministic town pulses.

Compare base vs overlay under identical seeds and both seats in an environment where physical actions are held fixed.

PASS requires:

- zero mechanical errors;
- intervention actually triggers;
- positive own-bank causal delta in town-demand regimes;
- no systematic loss when current shop demand is zero/too small because abstention must fire.

### Gate FP2 — cash/storage opportunity-cost proof

Add cash and shed shadow prices. Compare against H1 naive carry.

PASS only if the constrained controller improves or preserves W-L / money-gap while materially reducing cases where the trade starves production or causes shed overflow.

### Gate FP3 — adversarial opponent panel

Test against a heterogeneous set of exact mechanically valid agents, but do not tune from their action tapes.

Metrics:

- paired W/L;
- mean and median relative bank delta;
- 10th percentile / CVaR-style tail;
- intervention frequency and PnL attribution;
- cash-starvation events;
- overflow/discard events;
- price impact on both players.

### Gate FP4 — hosted sensor

Only after mechanical validity and causal local evidence. Because hosted transfer is weakly correlated with local ordering, a distinct mechanically valid FP candidate may deserve one high-information hosted probe without requiring it to beat every local anchor.

### Gate FP5 — architecture expansion

Do not start a full zero-lineage physical planner until at least one market operator survives FP1-FP4 or the market-only line is closed with clear evidence.

## Stop rules

- Do not mutate quantity thresholds endlessly on the same seeds.
- Do not use top-team replays to rescue an FP hypothesis.
- Close H1 if exact environment tests show no positive causal value after cash/storage costs across meaningful demand regimes.
- Close H3/H4 if relative-value sabotage adds tail risk without repeatable paired benefit.
- Keep market operators modular; failure of sabotage does not invalidate pure carry.
- Preserve a fresh held-out seed block for each promoted stage.

## Immediate next implementation

1. prove the standalone microsim against exact `kaggle-environments==1.32.7` calls;
2. implement the minimal H1 runtime overlay with no physical-action changes;
3. create deterministic scenarios spanning zero, low and high WHEAT town demand;
4. run both seats and attribute every coin of delta;
5. only then add cash/shed opportunity-cost controls.

The first deliverable is therefore **not** a 720-step farm strategy. It is a falsifiable economic mechanism with an exact null control.
