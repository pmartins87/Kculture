# ALL3 V18C P2 Cumulative Market Controller — Causal Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V18B MODEL RESULT.**

Activate only if V18B returns:
`V18B_CONTROLLER_READY_FOR_CAUSAL`.

## Candidate

The candidate is exactly the frozen V18B exported JSON controller artifact:

- selected temporal scope: turns 464..591;
- retained family set fixed by V18B leave-one-source-out gates;
- final tree JSONs fixed before V18C outcomes;
- pure-Python tree inference only;
- frozen SELL compiler semantics from the V18B protocol;
- exact ALL3 outside turns 464..591.

No tree, threshold, family set, compiler priority, or temporal scope may change after V18B.

## Discovery population

All and only the 24 binding V13C hard contexts from:
`configs/all3_v14a_hard_contexts.json`.

Paired episodes:
- BASE exact ALL3;
- TREATMENT exact ALL3 + frozen V18B controller.

Same pinned source SHA, seed and seat.

Expected:
- 24 pairs;
- 48 episodes.

## Mechanical gate

PASS requires:
- 24/24 paired contexts complete;
- zero source drift/failures;
- BASE exactly reproduces every frozen V13C score and margin;
- treatment uses no source identity, seed, seat, context id, outcome, or future information;
- treatment changes market only during turns 464..591;
- treatment never alters farmer/hands;
- every emitted market action passes structural legality checks;
- exported JSON model hash equals the V18B binding artifact hash.

## Coverage

Controller coverage PASS requires:
- treatment changes the ALL3 market in >=8 contexts;
- changed contexts span >=4 unique source SHAs.

## Strategic PASS

**`V18C_CONTROLLER_WL_HEADROOM`** iff:
- mechanical PASS;
- coverage PASS;
- positive-score contexts >=4;
- positive-score contexts span >=2 unique source SHAs;
- negative-score contexts = 0;
- mean score delta >0;
- mean margin delta >0.

If score PASS fails but mean margin delta >0 and negative-score contexts =0:
**`V18C_CONTROLLER_MARGIN_ONLY_CLOSE`**.

Otherwise:
**`V18C_CONTROLLER_NO_HEADROOM_CLOSE`**.

Mechanics failure:
**`V18C_MECHANICS_INVALID`**.

## Fresh validation if PASS

Only `V18C_CONTROLLER_WL_HEADROOM` may activate V18D.

V18D frozen population:
- same 10 exact source SHAs represented in the hard-context set;
- fresh seeds `78501,78502,78503,78504`;
- both seats;
- BASE exact ALL3 vs unchanged V18B controller;
- 80 paired contexts.

Fresh validation PASS requires:
- all 80 pairs mechanically clean;
- controller changes market in >=20 contexts;
- positive-score contexts >=2;
- positive-score contexts span >=2 source SHAs;
- negative-score contexts = 0;
- BASE-win -> treatment-nonwin regressions = 0;
- mean score delta >0;
- mean margin delta >=0.

No Kaggle submission is authorized by V18C.
