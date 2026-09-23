# V30B — Independent Public Persistent Policy Validation / Package-Parity Protocol

Preregistered: 2026-09-23, after binding V30A selection and before any V30B outcomes.

## Purpose

Independently test whether the exact V30A-selected complete public policy retains a persistent closed-loop advantage over ALL3 on unseen seeds and a separately reacquired fresh/current immutable public frontier. This is an offline validation gate only. It cannot submit, delete, or reorder Kaggle slots.

## Frozen candidate

- ref: `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`
- exact V30A `main.py` SHA-256: `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`
- attribution/provenance must be retained.

Package parity is mandatory: the exact V30A candidate package is taken from immutable V30A workflow `35877442921`; its `main.py` SHA must equal the frozen SHA above. No candidate reacquisition/substitution is permitted.

## Fresh frontier

Acquire a new current Top-30 public-kernel snapshot using the existing audited `tools/v28b_current_frontier_snapshot.py` implementation at V30B run time. SHA-deduplicate and two-seat smoke exactly as that implementation defines. Freeze 8–12 executable unique representatives. This frontier must be a newly acquired immutable snapshot, separate from V30A.

## Frozen benchmark

Candidates: exact V30A selected policy and ALL3 only.

Opponent panel: every representative in the fresh V30B immutable frontier.

Seeds: exactly `80601, 80602, 80603, 80604` (unseen in V30A).

Seats: both `0,1`.

Episode configuration: same pinned Kaggriculture execution semantics used by V30A; complete 720-step closed-loop episodes.

No policy mixing, opponent-identity routing, teacher call, source/rank/SHA runtime feature, or hosted feedback is allowed.

## Frozen mechanics gate

PASS requires: fresh frontier acquisition PASS; 8–12 unique executable representatives; exact frozen candidate SHA/package parity; complete expected context coverage for both candidates; DONE/DONE terminal status; finite rewards; 720-step episodes; zero episode failures.

Any failure here is mechanical only and may be repaired without changing scientific rules.

## Frozen independent promotion gate

The exact V30A candidate independently validates only if ALL conditions hold on the fresh common panel:

1. candidate score rate >= ALL3 score rate + `0.08`;
2. mean paired score delta >= `+0.08`;
3. positive aggregate opponent-source breadth >= `4`;
4. positive seed breadth >= `3/4`;
5. positive paired contexts > negative paired contexts;
6. positive support in both seats;
7. mechanics PASS.

These deliberately reuse the V30A promotion thresholds; no weakening after outcomes is allowed.

## Binding decisions

- `V30B_PUBLIC_PERSISTENT_POLICY_INDEPENDENTLY_VALIDATED`: all frozen conditions pass. Freeze exact package/ref/SHA plus V30B evidence and stop for strategic hosted-slot decision; do not mutate Kaggle without explicit user authorization.
- `V30B_PUBLIC_PERSISTENT_POLICY_VALIDATION_FAIL`: any scientific promotion condition fails with mechanics PASS. Close this candidate; do not cherry-pick another V30A candidate or alter thresholds based on V30B outcomes.
- `V30B_MECHANICS_INVALID`: mechanics fail. Repair mechanics only and rerun unchanged.

Protected hosted latest-two remains exact V47 `56466970` + ALL3 `56367770` throughout.