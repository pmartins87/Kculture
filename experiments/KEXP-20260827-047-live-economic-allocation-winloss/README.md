# KEXP-20260827-047 — live economic allocation winner-vs-loser radar

Status: **RUNNING / OBSERVATIONAL PRIORITY DIAGNOSTIC**

## Question

KEXP-042 showed large structural differences between frozen R4B and recent official top winners, but that comparison is confounded by different opponents/markets. KEXP-047 instead compares winners and losers **within the same official episodes** to identify economic allocations that consistently associate with winning across multiple days.

## Frozen protocol

Use the top 20 complete official episodes from each of 2026-08-24, 2026-08-25 and 2026-08-26. Exclude ties.

For each winner/loser pair, with corrected replay alignment `state t -> action frame t+1`, aggregate:

- HIRE and BUY_LAND;
- animal purchases by type;
- seed purchases by crop;
- sales by product;
- farm composition at states 192, 384, 576, 648 and 696.

Phases: 0-191, 192-383, 384-575, 576-647 and 648-718.

Report overall winner-minus-loser differences, per-date differences and signals whose sign is identical on all three dates.

## Decision use

This experiment does not authorize a candidate by itself. It ranks the next mechanics-first intervention if the current bounded CARROT line fails to generalize. Prefer signals that:

- have the same sign on all three dates;
- are economically meaningful rather than tiny action-count noise;
- map to a controllable public-state decision;
- can be falsified cheaply in R4B.

No validation or held-out access. Team/episode identity is research metadata only.

Tool: `tools/live_economic_allocation_winloss.py`  
Frozen tool blob: `32951de780fb2502b8398f738ce5c74e5e11c4d8`.
