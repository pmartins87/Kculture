# ALL3 V9 Residual Structural Decomposition — Conditional Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V8C RESULT.**

Activate only if binding V8C closes without reusable W/L headroom.
If V8C advances to a frozen conditional O-LQ3 rule and fresh V8D validation, V9 remains dormant.

## Motivation

Current evidence already excludes several broad explanations:

- V5: one-turn physical proposals were margin-only;
- V6: H2/H3 one-locus physical continuations were margin-only;
- V7: static option suppression did not rescue residual hard losses;
- V8B: SELL order has narrow local causal headroom;
- global O-LQ3 failed badly, so simple always-on product priority is closed;
- earlier V4E showed that V48's useful market delta was structural, with REPLACE/QTY_UP/STRUCTURAL carrying the causal signal while sanitation alone was insufficient.

ALL3 already captures the dominant LQ2 canonicalization mechanism. The remaining question, if V8C does not yield a reusable condition, is therefore:

**what structural V48 market behavior remains absent from ALL3 specifically on residual hard trajectories?**

## Frozen population

Use exactly the four V6A hard contexts already frozen:

1. V47 mirror — seed 75113, seat 1;
2. V48 — seed 75103, seat 1;
3. V48 — seed 75110, seat 0;
4. V48 — seed 75113, seat 1.

Do not replace these with easier close wins.

## V9A — residual divergence census

Replay exact ALL3 on each hard context.

Maintain an exact V48 shadow agent on every candidate observation solely as an offline proposal/oracle source. The V48 shadow action is **never applied** in V9A.

At each turn record:

- exact ALL3 farmer/hands/market;
- exact V48-shadow farmer/hands/market on the same candidate observation;
- physical parity flag;
- normalized market multiset parity;
- first divergent turn;
- divergence category/counters;
- legal own/shared public-state features needed to describe the state.

Classify residual market divergence into mutually auditable categories:

1. `REORDER_ONLY`: identical market-order multiset, different slot order;
2. `QTY_UP`: same operation/product structure with at least one larger V48 quantity;
3. `QTY_DOWN`: same structure with only smaller V48 quantity;
4. `REPLACE`: occupied slot changes operation/product semantics;
5. `INSERT_DROP`: nonempty/empty structural change;
6. `MIXED_STRUCTURAL`: more than one structural category;
7. `OTHER`: uncategorized, requiring manual inspection before any causal gate.

Also summarize by turn/day/hour/product and by repeated public-state signature. Opponent identity is offline metadata only.

### V9A gate

- mechanics failure / shadow replay inconsistency -> no strategic verdict;
- zero residual market divergences -> `V9A_NO_RESIDUAL_MARKET_DIFFERENCE`;
- residual divergences exist but only REORDER_ONLY -> `V9A_ORDER_ONLY_RESIDUAL`;
- structural residuals (QTY_UP/REPLACE/INSERT_DROP/MIXED) in >=2 hard contexts -> `V9A_STRUCTURAL_RESIDUAL_READY`;
- otherwise -> `V9A_STRUCTURAL_RESIDUAL_NARROW`.

V9A is descriptive only. No Kaggle submission.

## V9B — causal category isolation (conditional)

Only if V9A finds structural residuals.

For each hard context, select a small frozen set of representative residual states **before** any causal outcome is observed, prioritizing:

- earliest residual structural divergence;
- repeated category/state signatures;
- broad context coverage;
- temporal separation to reduce duplicate nearby states.

At each selected state, branch exactly one turn and apply only one frozen semantic category from V48 while preserving:
- ALL3 farmer/hands;
- all non-target market slots;
- exact ALL3 before and after the one-turn branch.

Primary target: W/L flip.
Margin is diagnostic only.

Do not infer a first-party rule until the category itself shows causal W/L headroom.

## Stop rule

If V9B has no loss->win headroom and no repeatable positive W/L category, close residual one-turn V48 structural imitation and move away from local market surgery rather than extending horizons or tuning thresholds post hoc.

## Legality

No runtime opponent identity, rating, EpisodeId, hidden seed, future information or opponent-private state is allowed in any promoted rule. V48 is an offline oracle/proposal source only.
