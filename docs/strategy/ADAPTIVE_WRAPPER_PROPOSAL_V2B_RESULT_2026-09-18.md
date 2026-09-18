# Adaptive Wrapper Proposal Oracle V2b Result — 2026-09-18

## Binding result

Workflow `35310754131`, artifact `10533820019`, exact engine `1.32.7`.

Mechanical PASS:
- 16 valid branch states;
- 16 exact counterfactual proposal rollouts;
- fresh replay parity exact;
- zero failures;
- third-party code used transiently only.

Strategic result:
- BASE score rate: `0.500`;
- oracle score rate: `0.625`;
- **W/L delta: `+0.125`**;
- non-win to win flips: **4**;
- mean oracle terminal-margin delta: **+4.0**;
- 8/16 states had positive margin headroom;
- every promoted non-base proposal came from **Ready Stock**.

Binding verdict: **`WRAPPER_PROPOSAL_WL_HEADROOM_PASS`**.

This is the first exact-engine evidence in the Prize Solver line that bounded search over
a strong adaptive organism has measurable **W/L headroom**, not merely terminal-money
headroom.

## Causal pattern

Two proposal families appeared in the selected states.

### Opening wheat reduction — rejected

At step 1:
- V47: `BUY_PRODUCT WHEAT 30`;
- Market-Smart / Shop-Aware: `BUY_PRODUCT WHEAT 8`;
- farmer/hands otherwise identical.

The reduced-wheat proposal was catastrophic in both fresh seeds. The oracle always kept
V47. This is useful negative evidence: not every public-frontier local disagreement is a
useful transform.

### Ready-stock sale — promoted

At the later disagreement state:
- V47 market: empty;
- Ready Stock market: `SELL WOOL 2`;
- farmer/hands exactly identical.

Seed 63001, both seats and both opponent blocks:
- BASE: tie;
- Ready Stock proposal: win by +15 margin.

Seed 63002:
- W/L unchanged;
- paired margin improved by +1.

This one local sale decision produced the entire positive V2b signal.

## Interpretation

Do **not** jump directly to a neural selector. The discovered intervention is simple
enough to isolate causally as a first-party own-state option.

Next gate: reconstruct a conservative **ready-stock early-sale** rule from legal current
state and the exact V47 base action, without executing Ready Stock code at runtime.
Evaluate BASE vs option on fresh seeds/opponents and both seats. The option may only add
an immediately feasible SELL for product already in own inventory and may not alter
farmer/hands or existing V47 market orders.

If that first-party rule transfers, freeze it as a solver proposal/operator and then
generate a broader state/value dataset. If it fails, retain V2b as proof of search
headroom but learn the proposal trigger from observation-labelled shadow data rather than
hardcoding the observed step.

No Kaggle submission is authorized by V2b alone.
