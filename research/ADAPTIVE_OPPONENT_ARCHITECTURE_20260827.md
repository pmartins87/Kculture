# Adaptive opponent architecture — 2026-08-27

## Thesis

Kculture should move toward a **hybrid adaptive agent** rather than another universal static trace.

The static route remains useful as a mechanically strong prior. Adaptation is added only where the opponent or shared state materially changes action value.

CR-002 is the central empirical warning: R4B/KEXP-050 can dominate a broad set of historically high-scoring public agents locally while remaining ~142/145 hosted. A single fixed policy can therefore be a strong counter to several known families and still have poor field coverage.

## What the agent can observe legally

At every state, both players see both farms' public state:

- money;
- main farmer and hand positions;
- worker count;
- unlocked quadrants;
- all public farm tiles, crops, animals, weeds and public yield fields;
- shared market inventory/prices;
- town/shop state.

The opponent's private shed, carried inventories and seeds are not visible.

No team name, submission id, episode id or seed may be used by the deployable policy.

## Poker analogy

Treat the opponent strategy like a range, not a label.

- **Prior:** before enough observations, use a robust base policy.
- **Evidence:** observe public farm/state transitions and shared-market changes.
- **Posterior/forecast:** estimate likely near-future macro actions.
- **Best response:** choose a bounded response only when expected value exceeds the base action by a confidence margin.
- **Regularization:** when confidence is weak, stay close to the robust base.

This avoids two bad extremes: a rigid universal trace and an overreactive opponent chaser.

## Proposed controller stack

### Layer 0 — mechanical safety

Hard legality, inventory, seed, terminal and action-efficiency checks. These never depend on opponent identity.

### Layer 1 — strong base policy

A reproducible 2000–3000-class public/current baseline or our reconstructed equivalent. This supplies the opening and fallback behavior.

### Layer 2 — opponent tracker

Persistent within-episode state, reset at step 0. Every call records public snapshots and derived deltas:

- money trajectory;
- worker/land expansion;
- crop/animal composition;
- public yield accumulation;
- likely harvest cadence;
- market inventory/price changes;
- opponent exposure to each product.

No exact opponent action is required at inference. State transitions are sufficient for many macro inferences.

### Layer 3 — behavior forecast

Estimate probabilities over a small economically meaningful next-action set:

- sell product X soon;
- buy seed X soon;
- buy animal X soon;
- hire soon;
- buy land soon;
- expand/shift production toward product X.

CR-004 tests whether public opponent information improves these predictions on a strict later-day test.

### Layer 4 — bounded response modules

Responses are independent and value-tested. Initial priority order:

1. **market ordering/front-running** — promote sales likely to lose value if the opponent dumps the same product first in a later market-order slot;
2. **capital/expansion response** — adjust land/hire timing when opponent expansion changes the expected race for production and market pressure;
3. **production mix response** — shift marginal planting/animal allocation toward products with better projected value given opponent public exposure and town demand;
4. **labor dispatcher** — reclaim static PASS waste and prioritize time-sensitive jobs using state value rather than trace index;
5. **terminal collector/liquidator** — maximize banked money under the exact final-horizon mechanics.

### Layer 5 — mixture-of-experts / policy portfolio

Instead of one giant policy, maintain several macro experts around a common mechanical base. A lightweight gating model chooses weights from public state and opponent forecast.

Examples:

- robust/base;
- high-labor expansion;
- market-front-run;
- scarcity crop shift;
- defensive liquidity;
- late liquidation.

The gate chooses by expected value, not opponent identity.

## Why market adaptation is first

The official market is processed by **order position**. At each queue index, both players' current orders are processed in per-unit lockstep using the same pre-commit inventory; market prices refresh between units and between order positions.

Therefore order ordering creates a real strategic interaction. If our sell is in an earlier market slot while the opponent's relevant sell occurs later, we can realize a better price before the rival increases market inventory. Conversely, blindly replaying a fixed sell order can donate value when the opponent's product mix changes.

This is one of the cleanest places to turn opponent prediction into an exact counterfactual value calculation.

## Development sequence

### CR-004 — predictive feasibility

Prove opponent-public state contains temporal predictive signal. No candidate promotion.

### CR-005 — market best-response value

For the most predictable sell targets, replay exact official states and compare base market ordering with forecast-conditioned ordering under the real market engine. Gate on realized money delta, not classification accuracy.

### CR-006 — adaptive wrapper

Wrap a strong base policy with only CR-005 responses that pass counterfactual value tests. Test against current-meta league and fresh exploratory seeds.

### CR-007 — online mixture

Add production/labor experts one at a time. Require broad BT/coverage improvement rather than isolated head-to-head wins.

## Hosted-loss forensics

Exact R4B/KEXP-050 hosted replays are especially valuable because they tell us which opponent behaviors our static policy actually encounters near rating ~145.

Once submission IDs are known:

1. list every episode for each submission;
2. download replay JSON and agent logs;
3. run `tools/hosted_replay_loss_analyzer.py`;
4. compare losses vs wins phase by phase;
5. identify repeated failure clusters;
6. reproduce those opponents/behaviors locally where possible;
7. value-test adaptive responses on the same seeds/trajectories.

The loss analyzer's flags are diagnostic only. Causal claims require a same-seed counterfactual or a controlled local tournament.

## Prize criterion

Adaptation is successful only if it raises **broad matchup strength**. The final competition result is one Bradley–Terry tournament, so a policy that brilliantly counters two families but collapses against a third is not prize-grade.
