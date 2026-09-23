# V30B — Independent Public Persistent Policy Validation / Package-Parity Protocol — 2026-09-23

## Status

DORMANT / PRE-REGISTERED while V30A workflow `35877442921` is still running and before any V30A candidate outcome is known.

Activate **only** if V30A returns:
`V30A_PUBLIC_PERSISTENT_POLICY_CANDIDATE_READY`.

V30B cannot change the candidate selected by V30A and cannot mutate Kaggle slots.

## Binding candidate

The candidate is exactly the single V30A frozen-selector winner:
- exact public Kaggle competition notebook ref;
- exact main.py SHA;
- exact package tree frozen in the V30A immutable snapshot.

No code modification, action patch, option composition, source-conditioned switch, or alternate public candidate is permitted.

Attribution/provenance must be retained.

## Package preparation

Create one deterministic submission-shaped package by copying the selected immutable public source package tree without policy edits.

Requirements:
- root entrypoint `main.py`;
- candidate main.py SHA exactly equals V30A selected SHA;
- all source-side auxiliary files required by the public package are preserved;
- no teacher/private code added;
- no network/Kaggle credential dependency at episode runtime.

Record:
- source public ref;
- source SHA;
- package archive SHA;
- packaged main.py SHA;
- file manifest.

## Package parity gate

Before competitive validation, compare:
1. direct immutable V30A selected source loader;
2. packaged selected source loader.

Frozen parity contexts:
- seeds `80509,80510`;
- both seats;
- first 2 executable opponents (ordered by representative rank then SHA) from the V30A frozen snapshot.

Require:
- 8/8 terminal reward pairs exactly equal;
- 8/8 score and margin equal;
- DONE/DONE and >=720 steps.

Any mismatch => `V30B_PACKAGE_PARITY_FAIL`.

## Independent fresh validation frontier

Acquire a **new** current public frontier at V30B runtime using the same audited discovery implementation:
`tools/v28b_current_frontier_snapshot.py`.

Rules remain:
- current Top-30 Kaggriculture public kernels by Kaggle kernel score;
- public-source acquisition only;
- SHA deduplication;
- smoke both seats;
- exclude exact V47 identity;
- select up to 12, minimum 8, ordered by representative public-kernel rank then SHA;
- freeze immutable snapshot before benchmark.

This second snapshot must not reuse the V30A opponent results.

## Frozen validation contexts

Seeds:
`80511,80512,80513,80514,80515,80516`.

Seats:
both 0 and 1.

Every validation opponent/context is run with:
- selected V30A public policy package;
- exact protected ALL3 baseline.

Identical contexts for both candidates.

With 12 opponents:
144 contexts per candidate.

## Metrics

For selected candidate and ALL3:
- W/L/T;
- score rate;
- mean/median margin;
- score rate by opponent source;
- score rate by seed.

Paired selected-minus-ALL3:
- positive/negative/neutral score contexts;
- mean paired score delta;
- mean/median margin delta;
- positive opponent-source breadth;
- positive seed breadth;
- positive support in both seats.

## Frozen validation gate

Decision
`V30B_PUBLIC_PERSISTENT_POLICY_VALIDATED_READY_FOR_USER_DECISION`
only if all:

1. mechanics PASS;
2. package parity PASS 8/8;
3. selected score rate >= ALL3 score rate + **0.05**;
4. mean paired score delta >= **+0.05**;
5. positive aggregate opponent-source breadth >= **4**;
6. positive seed breadth >= **4 of 6**;
7. positive paired score contexts > negative paired score contexts;
8. positive paired support exists in both seats.

Otherwise:
`V30B_PUBLIC_PERSISTENT_POLICY_VALIDATION_FAIL`.

Mechanical failure:
`V30B_MECHANICS_INVALID`.

No threshold may be weakened after V30A outcome.

## Routing

VALIDATED:
- preserve exact package/provenance;
- run a read-only slot/quota/latest-two preflight;
- present evidence to the user and request explicit authorization for any hosted submission;
- do **not** submit automatically.

FAIL:
- do not fall through to the second-best V30A candidate;
- close this V30A/V30B candidate path;
- a different public policy may only be reconsidered through a newly preregistered independent family.

No V30B result authorizes a Kaggle submission by itself.
