# ALL3 V17A2 Selected STRAWBERRY Bundle Translation Audit — 2026-09-20

## Status

Frozen after V17A selected the bundle and before any causal treatment.

## Binding selected bundle

From V17A workflow `35538621223`:

- `PRESENCE|SELL|STRAWBERRY|ADD`
- `QTY|SELL|STRAWBERRY|2|INC`

Support:
- 24/24 hard contexts;
- 10/10 hard-source SHAs;
- 42 occurrences;
- turns observed: 493, 503;
- median turn: 493.

## Purpose

Resolve only the action-shape details required to translate this selected bundle into one first-party rule:

1. exact teacher-added STRAWBERRY SELL quantity;
2. target market slot/index;
3. what occupies that slot in ALL3 before the teacher addition;
4. relative placement to existing nonempty orders;
5. per-context occurrence multiplicity.

No game outcomes are used.

## Audit population

All and only V14B W2 events whose normalized eligible bundle equals exactly the selected V17A bundle.

## Required output

For every selected event record:
- context id / source SHA / turn;
- base market;
- teacher market;
- indices containing SELL STRAWBERRY in teacher but not base;
- teacher quantity at each added index;
- base order occupying each added index;
- whether the added index was EMPTY in ALL3;
- whether it was the first EMPTY market slot;
- number of nonempty orders before/after the insertion.

Aggregate:
- occurrence count per context;
- distribution of turns;
- distribution of insertion indices;
- distribution of quantities;
- fraction added into an ALL3 EMPTY slot;
- fraction added into ALL3 first EMPTY slot.

## Candidate translation gate

A compact first-party translation is READY only if all 42 selected events satisfy one single legal structural insertion rule with >=95% agreement.

Preferred deterministic rule classes, in order:

1. first existing EMPTY slot;
2. last existing EMPTY slot;
3. fixed market index;
4. immediately after/before a uniquely identified existing order type.

If more than one rule has >=95% agreement, choose the earliest class in the list above.

Quantity must be exact and constant across >=95% of selected events; otherwise use the already-frozen bucket-minimum value +2.

Decision:
- `V17A2_STRAWBERRY_INSERTION_READY`
- `V17A2_STRAWBERRY_INSERTION_NOT_COMPRESSIBLE`

No causal game is run by V17A2.
No Kaggle submission.


### Mechanical representation amendment

The first V17A2 run failed before decision because selected events use two semantically equivalent empty-market encodings:
- `[[]]` — an explicit empty slot;
- `[]` — no materialized slot yet.

For translation only, define **first free slot** as:
- the first explicit empty slot when one exists;
- otherwise the virtual append position `len(market)`.

This does not alter the selected bundle, event population, recurrence evidence, quantity rule, or any strategic gate. It only normalizes equivalent market-list representations.
