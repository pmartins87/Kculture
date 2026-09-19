# Adaptive Wrapper Proposal Oracle V3 — Result — 2026-09-19

## Binding run

Workflow: **`35426189093`**  
Head: `2e2f5f6607f3007ef4cec6ad68b53c0ea1058ab5`  
Artifact: `10578809952`  
Artifact digest: `sha256:0637fe718de7012cea0868dbee136327cdbb39643a3e46ea89891def6d87d486`.

Two earlier attempts are non-binding mechanical failures:
- `35425004728`: repo-root import bootstrap failure;
- `35426094440`: inaccessible Shop-Aware acquisition (403) before branch evaluation.

## Mechanical result

PASS:
- **56 branch states**;
- **84 candidate counterfactual rollouts**;
- exact replay parity;
- **0 failures**;
- `kaggle-environments==1.32.7`.

## Strategic result

Decision: **`WRAPPER_PROPOSAL_OUTSIDE_MARGIN_ONLY`**.

Overall:
- BASE score rate: **0.7857143**;
- oracle score rate: **0.7857143**;
- W/L delta: **0.0**;
- nonwin→win flips: **0**;
- positive-margin headroom states: **8/56**;
- mean oracle margin delta: **+393.39**.

Outside the modern V47-family control stratum:
- BASE score rate: **1.0**;
- oracle score rate: **1.0**;
- W/L delta: **0.0**;
- nonwin→win flips: **0**;
- positive-margin states: **8/32**;
- mean oracle margin delta: **+688.44**.

All eight promoted non-base proposals came from **`router_2715`**.

## Recurrent proposal discovered

At step 0 V47 executes:

`BUY_PRODUCT WHEAT 7; SELL WHEAT 2`.

The promoted router proposal was:

`BUY_PRODUCT WHEAT 13; SELL WHEAT 13; BUY_PRODUCT WHEAT 13`.

It improved terminal margin repeatedly against:
- Conditional Memory;
- Tactical Memory;
- Best Market.

But it **did not change W/L** because V47 already won those tested contexts.

Critically, the same opening proposal was harmful against the hard blocks:
- V47 mirror: tie -> loss;
- Ready Stock: win -> loss;
- V48: remained a loss with much worse margin.

Therefore this opening transform must **not** be promoted as a generic first-party option.

## Interpretation

V3 proves that one-turn public proposal search can still identify economic headroom, but it does
not solve the competition-relevant W/L surface.

The prior V4 protocol required diverse non-V47 flips. V3 exposes a flaw in that formulation:
the selected non-V47 branch contexts were already BASE wins, so nonwin→win conversion there was
mathematically impossible.

The next search must target **hard BASE non-win strata**, especially V48, rather than requiring
arbitrary family diversity for its own sake.

Before launching expensive multi-turn counterfactual search, run a fresh V47×V48 divergence census
to determine whether the relevant gap is market/queue-only or includes farmer/hands programme
divergence.

No Kaggle submission is authorized by V3.
