# KEXP-20260827-050 — same-slot WHEAT→CARROT seed reallocation

Status: **RUNNING / CROSS-DISTRIBUTION CANDIDATE**

## Why this differs from KEXP-041

KEXP-041 bought an extra CARROT for 20 and later converted one already-owned WHEAT plant. It passed development 20-12 but failed exploratory replication at 14-14-12.

KEXP-050 instead uses KEXP-038's stronger purchase-time economics. At state 614, when frozen R4B itself buys exactly one WHEAT seed and

`3 * (CARROT_price - WHEAT_price) - 10 > 0`,

replace that one WHEAT purchase with one CARROT **in the same market-order slot**. Incremental seed cost is only 10. At state 615 convert exactly one actual R4B WHEAT plant only if the CARROT seed is observed to have arrived above the frozen-base expectation.

The same-slot replacement preserves market-order count and minimizes behavioral surface area.

Candidate: `candidates/r4d_reallocate_614_carrot.py`  
Candidate blob: `61b77be136836328917441cb03f89bc6665c4c27`  
Frozen R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Predeclared gate

Because KEXP-041 overfit development, KEXP-050 must satisfy **both** distributions before any validation discussion.

Mechanical audit on 16 development + 20 exploratory live-meta environmental seeds must show:

- zero status errors;
- every observed +1 CARROT / -1 WHEAT market reallocation that fires produces the exact corresponding +1 CARROT / -1 WHEAT plant conversion;
- at least 4 converted development episodes and at least 5 converted exploratory episodes.

Competitive screen:

- development modern public panel no worse than R4B's 81-15;
- no public family loses more than one win versus R4B reference;
- development direct vs R4B score >= **0.55** and positive mean delta;
- exploratory live-meta environmental direct vs R4B score >= **0.55** and positive mean delta;
- zero runtime/status errors.

A development-only win is insufficient. Passing all gates authorizes fresh validation consideration; it does not itself authorize held-out access or hosted submission.

No threshold fitting, identity features, validation or held-out access.
