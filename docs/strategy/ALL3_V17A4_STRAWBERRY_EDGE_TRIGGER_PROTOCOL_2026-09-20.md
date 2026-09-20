# ALL3 V17A4 STRAWBERRY Rising-Edge Trigger Audit — 2026-09-20

## Status

Frozen after V17A3 stateless-trigger closure and before V17A4 extraction.

## Binding V17A3 result

Workflow: `35539020930`.

Decision:
`V17A3_STRAWBERRY_TRIGGER_NOT_COMPRESSIBLE`.

Key result:
- T3_CARRIED20_OR_SHED2: recall 1.0, precision 0.4565;
- its false positives are dominated by consecutive persistence after the true event:
  turns 494 and 495 after the selected turn-493 event.

No STRAWBERRY treatment has been run.

## Purpose

Test whether the selected bundle corresponds to a **state transition** rather than a persistent state.

No new game is run.

Use only the exact per-turn stateless-trigger hit sequences already recorded in V17A3.

## Frozen edge transformation

For each V17A3 stateless trigger T0..T3:

A turn `t` is an edge fire iff:
- stateless trigger is true at `t`;
- stateless trigger was false at `t-1`.

At W2 start, the previous state is defined as false.

Create exactly:
- E0_AVAILABLE_RISING;
- E1_CARRIED20_RISING;
- E2_SHED2_RISING;
- E3_CARRIED20_OR_SHED2_RISING.

No thresholds, source filters, context filters, or turn thresholds may change.

## Target labels

Same 42 binding V17A selected event keys.

## Gate

For each edge trigger report:
- fires;
- TP/FP/FN;
- recall;
- precision;
- context support;
- source support.

Eligible:
- recall = 1.0;
- precision >=0.90;
- all 24 contexts;
- all 10 source SHAs.

Deterministic selection:
1. highest precision;
2. fewest fires;
3. lexical edge-trigger name.

Decision:
- `V17A4_STRAWBERRY_EDGE_TRIGGER_READY`
- `V17A4_STRAWBERRY_EDGE_TRIGGER_NOT_COMPRESSIBLE`.

If READY, the selected edge trigger replaces the stateless trigger variable in the already pre-registered V17B O-LQ6S family. The STRAWBERRY action transformation remains unchanged:
first-free SELL STRAWBERRY qty2.

No Kaggle submission.
