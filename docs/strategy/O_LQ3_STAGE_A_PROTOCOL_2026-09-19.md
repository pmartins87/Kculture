# O-LQ3 Priority SELL Ordering — Stage A Protocol — 2026-09-19

## Motivation

V8B found narrow causal W/L headroom by changing only SELL order:

- V48 75103/seat1: -86 -> +10 by moving WOOL before FERTILIZER at step 600;
- V48 75110/seat0: -484 -> -220 by moving MILK before WOOL at step 600.

The common local priority is:

**MILK -> WOOL -> FERTILIZER**.

## Candidate O-LQ3

Input:
exact ALL3 action after LQ2.

For every consecutive SELL run:
1. identify slots occupied by MILK, WOOL or FERTILIZER;
2. stable-sort only those selected orders by fixed priority:
   MILK, then WOOL, then FERTILIZER;
3. put the sorted orders back into the same selected slots.

Invariant:
- all non-target SELL products stay in their original slots;
- all quantities are identical;
- all non-SELL slots are identical;
- farmer/hands are identical;
- market order multiset is identical.

No opponent identity, no hidden state, no future information.

## Stage A hard-context replay

Use exactly the four frozen V6 hard contexts.

For each:
- BASE = exact ALL3;
- TREATMENT = exact ALL3 then O-LQ3 every turn.

Measure:
- W/T/L;
- terminal margin;
- first fire;
- fire count;
- margin delta.

## Stage A classification

### O_LQ3_STAGE_A_PASS
- mechanical PASS;
- at least one ALL3 loss becomes a win;
- mean treatment margin delta across the four contexts > 0.

Then open fresh targeted paired confirmation on untouched seeds.

### O_LQ3_STAGE_A_DIRECTIONAL_ONLY
- zero loss->win flips;
- mean margin delta > 0.

Then do not fresh-promote the global rule yet; inspect which fires contribute and derive a narrower
legal-state condition.

### O_LQ3_STAGE_A_FAIL
- mean margin delta <= 0 or mechanical invalid.

No Kaggle submission is authorized by Stage A.
