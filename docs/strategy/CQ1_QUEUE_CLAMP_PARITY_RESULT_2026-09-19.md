# O-CQ1 Queue Clamp Parity Audit — Result — 2026-09-19

## Binding run

Workflow: **`35439945148`**  
Head: `4a1b1f6fb4edc4ddf5c0628dd96d80b4fc611d1c`  
Artifact: `10583158262`  
Artifact digest: `sha256:37a7e62fad561181a649094b1d96ee6f89973c698df6a45e14af4e31aaec03d7`.

Mechanical PASS, strategic/mechanistic FAIL.

Decision: **`CQ1_PARITY_FAIL`**.

## Metrics

- exact V48 market-divergence rows: **456**;
- O-CQ1 changed rows: **1,356**;
- exact V48 matches: **288**;
- false-positive changes: **900**;
- V48 changes completely missed by CQ1: **0**;
- both changed but different result: **168**;
- precision: **0.2123894**;
- recall: **0.6315789**;
- failures: **0**.

## Closed hypothesis

O-CQ1 used only the **pre-action current shed**:
- preserve exact V47 farmer/hands;
- for every V47 SELL, cap quantity to current shed;
- replace zero-available SELL with `[]`.

This hypothesis is closed. Do not run its prepared causal W/L gate.

## Why it failed

Kaggriculture resolves each player's farmer/hand actions before processing the ordered market
queue. Therefore pre-action shed is not the inventory state available to later market slots.

Observed false positives include:
- current shed WHEAT=0, but an earlier `BUY_PRODUCT WHEAT 7` feeds a later `SELL WHEAT 2`;
- current shed FERTILIZER=0, but current `PLACE FERTILIZER` / shed-adjacent `DROP`
  deposits inventory before market;
- current shed WOOL=0, but a current unit can place/drop WOOL before the SELL slot;
- current `PICKUP` may also reduce shed before market.

Observed changed-but-not-exact states additionally show V48 can:
- clear infeasible SELL slots;
- cap oversized quantities;
- compact later feasible SELLs into earlier vacated SELL positions;
- in some same-product shortages, reallocate the available quantity to an earlier slot.

So V48's behavior is a **projected same-turn queue sanitation**, not a universal pre-state clamp.

## Next experiment

O-CQ2 development parity matrix:
- simulate the legal own shed effects of exact V47 farmer/hands actions first;
- project earlier inventory-changing market slots;
- compare compact sanitation languages;
- compare a small predeclared activation-threshold grid;
- select on development seeds only;
- freeze and validate on separate untouched seeds before any causal W/L test.

No Kaggle submission is authorized by this result.
