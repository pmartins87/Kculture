# ALL3 V10A Residual Cumulative Market Upper Bound Protocol — 2026-09-20

## Motivation

The evidence chain now separates local from cumulative effects:

- V4A: exact V48 market for only 1-3 turns under V47 was W/L-neutral;
- V4B/V4D: long-horizon market substitution produced genuine loss->tie score improvement;
- V4E: structural market categories carried that cumulative historical effect;
- O-LQ2 captured the dominant canonical SELL mechanism and became part of ALL3;
- V8/V9B: new local one-turn order/INSERT_DROP/QTY_UP interventions under ALL3 do not show fresh reusable W/L value.

Therefore the unresolved question is:

**does the residual V48 market behavior still have cumulative W/L headroom when layered over ALL3, even though its individual edits do not?**

V10A is an offline upper-bound diagnostic, not a deployable option.

## Frozen population

Use exactly the four frozen V6A hard contexts:
1. V47 mirror 75113 / seat 1;
2. V48 75103 / seat 1;
3. V48 75110 / seat 0;
4. V48 75113 / seat 1.

Base is exact ALL3.

## Frozen treatments

Run each context with exact clean replay for:

1. **BASE** — ALL3 unchanged.
2. **FULL_ALL** — whenever exact V48 shadow physical action matches ALL3 physical action, use exact V48 shadow market for the current turn across the full episode.
3. **FULL_W2PLUS** — same exact market substitution only from turn 336 onward.
4. **STRUCT_W2PLUS** — from turn 336 onward, apply only live INSERT_DROP or QTY_UP semantic transformations.
5. **INSERT_W2PLUS** — from turn 336 onward, apply only live INSERT_DROP.
6. **QTY_W2PLUS** — from turn 336 onward, apply only live QTY_UP.
7. **REORDER_W2PLUS** — from turn 336 onward, apply only live REORDER_ONLY.

All treatments:
- preserve exact ALL3 farmer/hands;
- evaluate V48 only as an offline shadow proposal source on the candidate's actual observation;
- if V48 physical action differs, retain ALL3 market for that turn and count a physical fallback;
- after any intervention, continue on the treatment's own resulting trajectory.

No opponent identity is used by any candidate rule; context identity is only experimental metadata.

## Why two full upper bounds

`FULL_ALL` answers the maximal question: can residual V48 market behavior rescue ALL3 at all?

`FULL_W2PLUS` tests the historically established late-market interval aligned with LQ2's step-336 activation.

If FULL_ALL works but FULL_W2PLUS does not, early residual state shaping matters.
If FULL_W2PLUS works, category decompositions determine whether the remaining cumulative signal is structural or reorder-driven.

## Mechanical gate

PASS requires:
- all four contexts complete for all seven modes;
- BASE reproduces the frozen ALL3 score/margin exactly;
- zero failures;
- ALL3 farmer/hands always remain the executed physical action.

Physical fallback counts are diagnostic, not an automatic mechanics failure.

## Strategic decision

A **score improvement** means treatment score > BASE score. Since all frozen bases are losses, loss->tie and loss->win both count as W/L headroom.

Decision hierarchy:

1. FULL_ALL has zero positive-score contexts:
   **`V10A_RESIDUAL_MARKET_UPPER_BOUND_CLOSED`**
   — close cumulative V48 residual market imitation under ALL3.

2. FULL_ALL has positive score, but FULL_W2PLUS has none:
   **`V10A_EARLY_RESIDUAL_REQUIRED`**
   — cumulative headroom exists but depends on pre-336 shaping.

3. FULL_W2PLUS has positive score and STRUCT_W2PLUS has positive score:
   **`V10A_W2PLUS_STRUCTURAL_HEADROOM`**
   — cumulative residual structural interaction survives under ALL3.

4. FULL_W2PLUS has positive score but STRUCT_W2PLUS has none:
   **`V10A_W2PLUS_NONSTRUCTURAL_HEADROOM`**
   — inspect REORDER and cross-category interaction before any first-party rule.

For any headroom label, record exact positive contexts and whether INSERT, QTY or REORDER alone reproduces them.

V10A cannot promote a hosted candidate. Any surviving mechanism must be distilled to a first-party legal-state rule and validated on untouched seeds.

No automatic Kaggle submission.
