# O-LQ2 + O-RW1 + O-TW1 Triple Composition Protocol — 2026-09-19

## Purpose

Determine whether the newly validated O-LQ2 can be added safely to the existing offline host
(O-RW1 + O-TW1) without a learned router.

## Frozen variants

For each fresh context:
- BASE = exact V47;
- OLD = O-RW1 + O-TW1;
- LQ2 = O-LQ2 only;
- ALL3 = O-RW1 + O-TW1 + O-LQ2.

Operator order in ALL3:
1. compute exact V47 action;
2. apply O-TW1 if eligible and unused;
3. else apply O-RW1 if eligible and unused;
4. apply O-LQ2 canonicalization to the resulting action from step 336 onward.

The one-shot predicates remain evaluated on exact V47 current action, preserving their frozen semantics.

## Fresh league

Seven-family V2 league.

Seeds:
`74601..74604`, both seats.

Total:
56 contexts × 4 variants.

## Mechanical gate

- all 56 contexts complete;
- all variants DONE;
- pre-trigger exact-V47 trace parity;
- no physical action mutation;
- pinned public-agent identities.

## Strategic classification

**TRIPLE_COMBO_SAFE_ADVANCE** if:
- ALL3 overall score rate >= max(OLD, LQ2);
- ALL3 vs BASE mean score delta > 0;
- every opponent block ALL3-vs-BASE delta >= 0;
- zero ALL3-vs-BASE negative-score contexts.

**TRIPLE_COMBO_SAFE_NO_INCREMENT** if:
- ALL3 is W/L-safe vs BASE on every block;
- but ALL3 is below the best constituent on aggregate.

**TRIPLE_COMBO_ROUTER_REQUIRED** if:
- LQ2 remains positive overall;
- ALL3 introduces any W/L regression.

Otherwise FAIL.

No Kaggle submission is authorized by this gate.
