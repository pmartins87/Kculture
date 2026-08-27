# KEXP-20260827-055 — TOMATO slot succession diagnostic

Status: **COMPLETE / SIMPLE-SUBSTITUTION ROUTE PLAUSIBLE**

Run `33073812783`, artifact `9647111604`, digest `sha256:48f061b2b283a20396272c180004c29a27c3cb655ac04a959bba570782c8b6aa`.

## Question

KEXP-053 found 32 R4B WHEAT plant events whose next same-tile HARVEST occurs at least 192 turns later, long enough for TOMATO's first production under the official engine.

TOMATO is ongoing: HARVEST resets its accumulated yield but does not remove the plant. Therefore a naive substitution can block a later `PLANT` that assumes the one-shot WHEAT tile became empty.

KEXP-055 measured this exact succession risk before any TOMATO candidate is written.

## Result

Across the 32 compatible slots:

- **26/32** have no future same-tile PLANT at all after the audited HARVEST;
- only **6/32** have a future replant within 96 turns;
- all six conflicts are the **same structural slot**: state `381`, position `(0,2)`;
- for that slot, R4B HARVEST occurs at state `594` and the next WHEAT PLANT occurs immediately at state `595`;
- no other compatible slot has a later same-tile PLANT in the observed trajectory.

Development: 14 compatible slots, 3 immediate conflicts, 11 no future PLANT.  
Exploratory live-meta: 18 compatible slots, 3 immediate conflicts, 15 no future PLANT.

The predeclared low-conflict routing criterion was <=25% replant conflict within 96 turns. Observed: **6/32 = 18.75% — PASS**.

## Recurring compatible slots

- state 262, `(0,4)`: 6 observations, no future replant conflict;
- state 310, `(9,7)`: 6, no future replant conflict;
- state 334, `(5,9)`: 6, no future replant conflict;
- state 381, `(0,2)`: 6, **immediate replant conflict — exclude from simple substitution**;
- state 451, `(7,3)`: 4, no future replant conflict;
- state 477, `(0,9)`: 4, no future replant conflict.

KEXP-053 measured the corresponding original WHEAT plant-to-harvest delays as 281, 398, 356, 213, 229 and 211 turns respectively. Thus five recurring slot families have enough physical lifetime for TOMATO and no observed downstream PLANT collision.

## Decision

A bounded TOMATO experiment is authorized in development using only the five non-conflicting structural slot families. Do **not** include the state-381 `(0,2)` slot without explicit tile-release logic.

This does not modify or delay the frozen KEXP-050 validation/submission path. TOMATO remains a next-generation R4D research branch.

No validation or held-out outcome was accessed. Held-out remains sealed.
