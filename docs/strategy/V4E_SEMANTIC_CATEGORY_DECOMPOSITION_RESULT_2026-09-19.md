# V4E Exact Semantic-Category Decomposition — Result — 2026-09-19

## Binding run

Workflow: **`35450703737`**  
Head: `7c3e8f6c73945b9ca0450c427ce80af8a6eda06c`  
Aggregate artifact: `10586741127`  
Aggregate digest: `sha256:0b52b9cad9890b9f0a262311c073a58f49dae3163b9678b25f7f8934b6592977`.

Mechanical PASS:
- 6/6 seed shards PASS;
- 12/12 contexts complete;
- FULL positive control reproduced the V4B/V4D loss->tie effect;
- physical fallback turns: 0.

## Binding decision

**`V4E_STRUCTURAL_SUFFICIENT_SANITATION_NOT_NECESSARY`**

### FULL exact V48 market inside W2+

- reproduced contexts: **12/12**;
- score rate: **0.5**;
- mean score delta: **+0.5**;
- mean margin delta: **+585.67**.

### ONLY_SANITATION = CLEAR + QTY_DOWN

- reproduced contexts: **2/12**;
- score rate: **0.1667**;
- mean margin delta: **+18.67**.

This confirms O-LQ1: visible queue clearing/quantity reduction is not the causal driver.

### ONLY_STRUCTURAL = REPLACE + QTY_UP + OTHER

- reproduced contexts: **10/12**;
- score rate: **0.5**;
- mean margin delta: **+587.17**.

### FULL_MINUS_SANITATION

- reproduced contexts: **10/12**;
- score rate: **0.5**;
- mean margin delta: **+587.17**.

So sanitation is not necessary.

### Necessity ablations

- FULL_MINUS_REPLACE: **0/12** reproduced;
- FULL_MINUS_QTY_UP: **2/12** reproduced;
- FULL_MINUS_STRUCTURAL: **2/12** reproduced.

Binding necessary categories:
- **REPLACE**;
- **QTY_UP**;
- therefore their **STRUCTURAL interaction**.

## Mechanistic interpretation

The structural pattern is highly regular.

Examples:
- `SELL MILK 6; SELL MILK 1` -> `SELL MILK 7; []`;
- `SELL EGG 6; SELL EGG 4` -> `SELL EGG 10; ...`;
- when early SELLs are infeasible, later feasible products shift left, which appears slotwise as
  `REPLACE`;
- late liquidation queues keep only products with sellable inventory, compacted toward the front.

Therefore the apparent REPLACE category is mostly **queue compaction after canonicalizing effective
SELL demand**, while QTY_UP is mostly **same-product duplicate aggregation**.

This reveals a first-party mechanism not previously tested by CQ2:
- CQ2's shortage-merge mode merged duplicates only when total requested demand exceeded projected
  inventory;
- V48 structurally merges duplicate SELLs even when their total is fully feasible.

## New first-party hypothesis — O-LQ2

**O-LQ2 — Late Canonical SELL Queue**:

From step 336 onward, within each consecutive SELL run:
1. preserve first-occurrence product order;
2. aggregate **all** requested quantities for each product in the run;
3. cap the aggregated quantity to projected available own inventory;
4. emit at most one SELL per product;
5. drop zero-available products;
6. compact surviving SELLs left inside the original SELL run;
7. pad remaining SELL-run positions with `[]`;
8. preserve non-SELL market orders and exact V47 farmer/hands.

Projected availability uses only legal own current state plus exact current V47 action.

O-LQ2 must be tested causally on fresh seeds. It is not promoted by V4E alone.

No Kaggle submission is authorized by V4E.
