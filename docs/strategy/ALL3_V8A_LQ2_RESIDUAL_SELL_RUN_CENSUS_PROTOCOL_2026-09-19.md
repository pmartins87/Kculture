# ALL3 V8A LQ2 Residual SELL-Run Census — Protocol — 2026-09-19

## Purpose

V7 showed that LQ2 is the dominant value-producing component in the residual hard losses, while
static inclusion/suppression of RW1/TW1/LQ2 produced zero W/L rescues.

V8A asks a narrower structural question:

**After exact LQ2 canonicalization, do residual hard contexts still contain same-turn SELL runs with
two or more distinct non-empty products, so that cross-product execution order could matter?**

This is observation-only. No intervention is performed.

## Frozen contexts

Use exactly:
`configs/all3_v6_hard_contexts.json`.

No close wins may be added.

## Exact candidate

Exact ALL3:
- hosted-faithful V47;
- RW1;
- TW1;
- LQ2.

For each turn record:
1. exact V47 action;
2. exact post-RW/TW, pre-LQ2 action;
3. exact post-LQ2 ALL3 action;
4. whether LQ2 changed the market;
5. projected shed after physical action;
6. every post-LQ2 consecutive SELL run.

## Eligible order-search state

A turn is V8B-eligible iff post-LQ2 contains a consecutive SELL run with:
- at least 2 non-empty SELL orders;
- at least 2 distinct products.

The candidate state record must include:
- hard-context index;
- opponent/family/seed/seat;
- step;
- pre-LQ2 market;
- post-LQ2 market;
- eligible SELL run start/end;
- ordered product/quantity list;
- projected shed.

## Census metrics

Per context:
- total LQ2-changed turns;
- total post-LQ2 multi-product SELL-run turns;
- maximum distinct products in one eligible run;
- top eligible states by:
  1. more distinct products;
  2. more non-empty SELL orders;
  3. larger total SELL quantity;
  4. earlier step.

Aggregate:
- eligible-state count;
- hard contexts with >=1 eligible state.

## Gate

### V8A_ORDER_SEARCH_READY
- at least one eligible state exists.

Next:
freeze a bounded set of eligible states and run an exact cross-product SELL-order permutation oracle.

### V8A_NO_ORDER_HEADROOM
- zero eligible states.

Then cross-product SELL order is structurally unavailable after LQ2 and must be closed without
running permutation branches.

## Constraints

- observation-only;
- no opponent identity in deployable logic;
- no Kaggle submission;
- no threshold tuning in V8A.
