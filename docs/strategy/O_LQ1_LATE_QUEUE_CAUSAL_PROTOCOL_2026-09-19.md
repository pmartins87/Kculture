# O-LQ1 Late Queue Sanitation — Fresh Causal Protocol — 2026-09-19

## Hypothesis

V4B established that cumulative V48 market behavior can move exact V47 from loss to tie in 12/12
contexts without changing farmer/hands. V4D localized the smallest global predeclared suffix to
steps **336–718** and showed that winning transformations are dominated by SELL clearing and SELL
quantity reduction.

O-LQ1 is a new first-party causal hypothesis:

- use exact hosted-faithful V47 as the base policy;
- preserve exact V47 farmer/hands always;
- preserve exact V47 market before step 336;
- from step 336 onward, project own current shed through exact current physical actions;
- project earlier market inventory-changing slots in order;
- for each SELL slot, cap quantity to projected remaining own inventory;
- replace zero-available SELL with `[]`;
- preserve slot order and all non-SELL market orders.

Inputs are limited to current legal own observation, current config and exact V47 current action.
No opponent identity, rating, EpisodeId, hidden seed, future state or opponent-private state is used
by the operator.

## Important separation from CQ2

CQ2 remains **closed** as an exact-V48 parity model. Its best development rule had insufficient
precision.

O-LQ1 is opened by independent V4D **outcome localization**, not by lowering the CQ2 parity gate.
The question is now causal: does late first-party queue sanitation improve W/L on fresh games?

## Fresh population

Primary opponent: exact V48 Clear the Queue.

Seeds:
`74301..74308`, both seats = **16 paired contexts**.

For each context:
1. run exact V47 BASE;
2. run exact V47 + O-LQ1 treatment;
3. verify pre-trigger V47 trace parity;
4. record score/margin, first fire, fire count and changed slots.

## Frozen causal gate

Mechanical PASS requires:
- 16/16 paired contexts complete;
- all statuses DONE;
- pre-trigger parity PASS everywhere;
- treatment never changes farmer/hands.

**O_LQ1_V48_CAUSAL_PASS** requires:
- paired mean score delta >= **+0.125**;
- at least **4** contexts with positive score delta;
- **0** contexts with negative score delta;
- positive mean margin delta.

**O_LQ1_V48_CAUSAL_WEAK**:
- positive mean score delta, but strong gate not met.

**MARGIN_ONLY**:
- zero score delta with positive mean margin delta.

Otherwise FAIL.

## After PASS

Do not submit immediately.

Next:
1. broad fresh regression gate across V47 mirror, Ready Stock, V48 and unrelated families;
2. autonomous/runtime parity;
3. option-library admission only if broad gate is safe;
4. then test composition with O-RW1 + O-TW1 and value/router integration.

No Kaggle submission is authorized by this protocol alone.
