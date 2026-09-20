# ALL3 V17A3 STRAWBERRY Runtime Trigger Audit — 2026-09-20

## Status

Frozen before V17A3 baseline replay.

## Inputs

Binding V17A/V17A2 results:

- selected W2 bundle:
  - `PRESENCE|SELL|STRAWBERRY|ADD`
  - `QTY|SELL|STRAWBERRY|2|INC`
- 42 selected events;
- 24/24 hard contexts;
- 10/10 source SHAs;
- insertion rule: first free market slot;
- quantity: exactly 2;
- observed event turns: 493 (24 contexts) and 503 (18 contexts).

No causal outcome from a STRAWBERRY treatment exists yet.

## Purpose

Find a legal runtime trigger that reproduces the selected bundle events without:
- exact turn whitelists;
- opponent/source identity;
- seed or replay metadata;
- future information.

## Audit population

Replay exact ALL3 BASE on all 24 binding V13C hard contexts.

For every turn in W2 (`336..503`), record whether:
- ALL3 market has **no nonempty order**;
- own private STRAWBERRY shed quantity;
- own carried STRAWBERRY quantity across own inventories;
- total own available STRAWBERRY = shed + carried.

BASE must reproduce the frozen V13C score and margin exactly.

## Frozen trigger grammar

Every candidate requires:
- W2;
- ALL3 market has no nonempty order;
- total available STRAWBERRY >= 2.

Evaluate exactly these four identity-free candidates:

- **T0_AVAILABLE**: common requirements only.
- **T1_CARRIED20**: common + carried STRAWBERRY >= 20.
- **T2_SHED2**: common + shed STRAWBERRY >= 2.
- **T3_CARRIED20_OR_SHED2**: common + (carried STRAWBERRY >= 20 OR shed STRAWBERRY >= 2).

Thresholds 20 and 2 are frozen from the two exact selected-event state clusters observed in the binding V14B artifact:
- turn-493 cluster: carried=20, shed=0;
- selected turn-503 cluster: carried=4, shed=2.

No threshold search is permitted.

## Target labels

The positive target set is all and only the 42 binding V17A selected event keys `(context_id, turn)`.

For each trigger report:
- total fires;
- true positives;
- false positives;
- false negatives;
- recall;
- precision;
- contexts covered;
- source SHAs covered.

## Deterministic selection

Eligible trigger:
- recall = 1.0;
- precision >= 0.90;
- covers all 24 contexts and 10 source SHAs.

Select by:
1. highest precision;
2. fewest total fires;
3. lexical trigger name.

Decision:
- `V17A3_STRAWBERRY_TRIGGER_READY`
- `V17A3_STRAWBERRY_TRIGGER_NOT_COMPRESSIBLE`
- `V17A3_MECHANICS_INVALID`.

If READY, V17B may use exactly the selected trigger to insert `SELL STRAWBERRY 2` at the first free market slot.

No Kaggle submission.
