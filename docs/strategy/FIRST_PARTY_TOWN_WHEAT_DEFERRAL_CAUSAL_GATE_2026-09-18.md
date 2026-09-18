# First-Party O-TW1 Town-WHEAT Pulse Hold Causal Gate — 2026-09-18

## Purpose

Open the next **orthogonal** bounded first-party economic option while the valid O-RW1
hosted R2 pair matures.

O-TW1 is not a retune of O-RW1 and does not use intermediate O-RW1 hosted outcomes.

## Historical causal prior

Preserve the frozen first-principles evidence already accepted by CR092:

### H1 runtime causal proof

Commit:
`ab951727a195dce2992a07bf3e8b08992187fdf6`

The H1 probe bought WHEAT on a legally known town-consumption pulse and sold after the
pulse. Against passive control, the default-price treatment was positive on every tested
seat/seed, while a flat-WHEAT-price causal null produced exactly zero value.

### H1B exact-engine timing proof

Commit:
`a00d2ffce9656b83df263f407ed9b92a718502db`

H1B proved in the exact engine that, for already-owned inventory, selling **after** known
town consumption is never worse than selling immediately in the tested market-state
family and can be strictly better. CR092 explicitly froze H1/H1B as the next timing-option
family after O1.

These are priors only. They do **not** prove that a V47 wrapper improves competitive W/L.

## Frozen first-party operator O-TW1

Host:
exact public V47,
`ahmedberatozer/kaggriculture-v47-reactive-market-coordination`

Pinned `main.py` SHA-256:
`f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`

Hosted loader contract:
`kaggle_environments.agent.get_last_callable`

Expected hosted entrypoint:
`_y_agent_shopherd`.

### Runtime-legal eligibility

At the current turn only:

1. `step <= 671`;
2. public town state/config imply positive WHEAT consumption on this turn, using the
   historical H1 mechanism:
   - unlocked WHEAT-consuming shops on `townShopSellInterval`, and/or
   - town-center WHEAT demand on `townCenterSellInterval`;
3. exact V47 base market action contains one or more `SELL WHEAT q` orders;
4. current own private shed contains at least the total WHEAT quantity V47 intends to
   sell.

No opponent-private state, hidden seed, future state, identity, rating or replay metadata
is a runtime feature.

### Treatment

For the target turn only:

- keep exact V47 `farmer`;
- keep exact V47 `hands`;
- keep every non-WHEAT-sale market order in its original order;
- remove all current-turn `SELL WHEAT` orders.

On the very next turn, the wrapper is gone and exact V47 resumes with no forced sale.

This is intentionally weaker and cleaner than an explicit two-turn forced deferral. It
tests the causal question:

> Does preventing V47 from selling owned WHEAT immediately before a known public
> town-consumption pulse create competitive value?

## Frozen panel

Exact engine:
`kaggle-environments==1.32.7`.

Fresh seeds:
`67001..67004`.

Both seats.

Opponents:

1. exact V47 mirror;
2. exact V48 Clear the Queue;
3. Tactical Memory.

For each matchup:

- run a discovery episode with exact V47;
- replay exact BASE and require identical final rewards;
- select at most the first two eligible pulse-sale events;
- selected events must be at least 72 turns apart;
- rerun one causal treatment per selected event.

Minimum mechanically interpretable branch states:
**12**.

No automatic Kaggle submission.

## Frozen outcomes

### `TOWN_WHEAT_DEFERRAL_CAUSAL_PASS_SAFE_OPTION`

Requires all:

- mechanics PASS;
- overall mean W/L score delta > 0;
- at least 2 non-win -> win flips;
- 0 win -> non-win regressions;
- at least 2 opponent blocks with nonnegative mean W/L delta.

Advance to an autonomous one-shot runtime gate. Do not submit automatically.

### `TOWN_WHEAT_DEFERRAL_CAUSAL_HETEROGENEOUS`

Mechanics pass and there is both positive and negative W/L evidence, or an opponent block
regresses. Freeze labels; do not threshold-tune from the same seeds.

### `TOWN_WHEAT_DEFERRAL_MARGIN_ONLY`

W/L is neutral but mean terminal-margin delta is positive. Retain as an economic proposal
feature, not a hosted candidate.

### `TOWN_WHEAT_DEFERRAL_NO_HEADROOM`

Mechanics pass but no positive competitive or margin signal. Close this minimal wrapper
without threshold rescue.

### `TOWN_WHEAT_DEFERRAL_MECHANICS_INVALID`

Insufficient valid branch states, replay mismatch, runtime failure, or source/loader
identity failure. Fix mechanics only; no strategic interpretation.

## Anti-tuning rule

Do not change product, pulse definition, seed panel, minimum WHEAT quantity, timing
window, event spacing, or pass thresholds after seeing this gate.

A later broader timing option must be justified by new causal evidence, not by rescuing a
failed O-TW1 result.
