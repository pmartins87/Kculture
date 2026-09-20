# ALL3 V8C Local Priority Value Atlas — Protocol — 2026-09-20

## Trigger

V8B showed narrow local SELL-order headroom, but the always-on O-LQ3 Stage A replay failed mechanically clean:

- workflow `35480144515`;
- decision `O_LQ3_STAGE_A_FAIL`;
- 0 loss->win flips;
- mean margin delta **-1304.25**;
- all four hard contexts worsened in margin.

Therefore O-LQ3 as a global/static priority rule is closed. No threshold rescue or post-hoc frequency tuning is allowed.

## Question

Was the V8B signal genuinely state-conditional?

V8C isolates every turn where frozen O-LQ3 would fire in the four frozen hard contexts. Each branch:

1. replays exact ALL3;
2. applies the unchanged `MILK -> WOOL -> FERTILIZER` priority transform on exactly one firing turn;
3. returns immediately to exact ALL3 for every later turn.

This removes the cumulative-confounding present in Stage A.

## Frozen discovery population

The same four V6A hard contexts remain frozen:

1. V47 mirror 75113 / seat 1;
2. V48 75103 / seat 1;
3. V48 75110 / seat 0;
4. V48 75113 / seat 1.

Stage A established exactly 12 O-LQ3 fires per context, so the binding aggregate expects **48 one-shot branch states**.

## Recorded legal features

Discovery records only own/private and shared public state available to the agent, including:

- day/hour and internal deterministic turn counter;
- current target SELL quantities and order;
- own shed and projected post-physical shed;
- public market prices/inventory;
- public town shop counts;
- market composition counts.

Opponent identity remains offline stratification metadata only and is forbidden as a future runtime feature.

## Frozen decision rule

- mechanics invalid or !=48 valid branch states -> `V8C_MECHANICS_INVALID`;
- loss->win flips in >=2 distinct hard contexts -> `V8C_CONDITIONAL_ORDER_HEADROOM_REPEATABLE`;
- >=1 loss->win plus positive-margin states in >=2 contexts -> `V8C_CONDITIONAL_ORDER_HEADROOM_NARROW`;
- positive-margin states in >=2 contexts without a win flip -> `V8C_CONDITIONAL_ORDER_MARGIN_HETEROGENEOUS`;
- otherwise -> `V8C_CONDITIONAL_ORDER_NO_REUSABLE_HEADROOM`.

## Binding next branch

Only a repeatable/narrow W/L result may justify deriving **one** compact public-state condition. That condition must be frozen before a fresh-seed V8D paired validation.

Margin-only evidence does not authorize another hosted candidate.

No Kaggle submission is authorized by V8C.
