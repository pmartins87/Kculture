# O-LQ2 Late Canonical SELL Queue — Fresh Causal Protocol — 2026-09-19

## Hypothesis

V4E showed that the W/L headroom is carried by the structural interaction between:
- same-product SELL quantity increases; and
- slotwise SELL replacements caused by moving later effective orders forward.

The recurring mechanism is consistent with canonicalizing each consecutive SELL run:
- merge duplicate products;
- cap merged demand to projected available inventory;
- remove zero-effective products;
- compact survivors left.

## First-party runtime rule

Use exact hosted-faithful V47 as the base policy.

Before step 336:
- return exact V47 unchanged.

From step 336 onward:
1. preserve exact V47 farmer and hands;
2. project own shed through current V47 farmer/hands shed mutations;
3. scan the exact V47 market in order;
4. for each consecutive SELL run:
   - preserve first-occurrence product order;
   - sum all requested quantities for each product;
   - cap the aggregate to projected remaining own inventory;
   - emit at most one SELL per product;
   - drop products with zero available quantity;
   - compact surviving SELLs left;
   - pad the remaining run positions with empty slots;
5. preserve every non-SELL market order exactly;
6. project earlier BUY_PRODUCT / BUY_ANIMAL inventory effects before later SELL runs.

The operator uses only current legal own observation, current config and exact current V47 action.

Forbidden runtime inputs:
- opponent identity;
- opponent private state;
- hidden seed;
- rating;
- EpisodeId;
- future state;
- V48 code/action.

## Separation from closed hypotheses

- O-CQ1 is closed.
- CQ2 parity fitting is closed.
- O-LQ1 projected slotwise clamp/clear is closed.

O-LQ2 is a distinct structural mechanism opened by V4E because CQ2 only merged duplicates under
shortage, while V48's effective behavior merges duplicates even when total demand is feasible.

## Fresh causal population

Primary opponent: exact public V48.

Seeds:
`74401..74408`, both seats = **16 paired contexts**.

For every context:
1. run exact V47 BASE;
2. run exact V47 + O-LQ2;
3. verify pre-trigger trace parity;
4. require physical action identity;
5. record score/margin and structural fire statistics.

## Frozen causal gate

Mechanical PASS:
- 16/16 paired contexts complete;
- all statuses DONE;
- pre-trigger parity PASS;
- treatment never changes farmer/hands.

**O_LQ2_V48_CAUSAL_PASS** requires:
- mean paired score delta >= **+0.125**;
- >= **4** positive-score contexts;
- **0** negative-score contexts;
- positive mean margin delta.

**WEAK**:
- positive mean score delta but strong gate not met.

**MARGIN_ONLY**:
- zero mean score delta with positive mean margin delta.

Otherwise FAIL.

## After PASS

Do not submit.

Next:
1. broad fresh regression vs V47 mirror, Ready Stock, V48 and unrelated families;
2. package/runtime parity;
3. option-library admission;
4. composition with O-RW1 + O-TW1;
5. selector/router integration only after broad safety.

No Kaggle submission is authorized by this protocol.
