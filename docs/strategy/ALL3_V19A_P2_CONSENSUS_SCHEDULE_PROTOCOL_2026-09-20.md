# ALL3 V19A P2 Cross-Source Consensus Market Schedule Protocol — 2026-09-20

## Status

Frozen after V18B tree closure and before any V19 causal result.

## Motivation

V18A proved that P2 (turns 464..591) alone contains strong W/L headroom.

V18B showed that independent shallow residual classifiers over current state have high recall but insufficient precision.

Inspection of the same outcome-free P2 dataset shows strong exact market-action agreement by turn across independent source SHAs.

V19A therefore distills a **fixed turn-indexed consensus market schedule**.

Turn is a legal runtime feature. No opponent/source identity is used.

## Input

Use exactly the four mechanically passed V18B dataset artifacts from workflow:
`35552335995`.

No new games are run in V19A.

Rows:
- 24 hard contexts;
- 10 unique source SHAs;
- turns 464..591.

## Source balancing

For each turn:

1. Within each source SHA, collect the teacher-market action from all contexts belonging to that source.
2. Choose that source's modal exact teacher-market JSON.
3. Ties are broken by lexical canonical JSON.
4. Across the 10 source-level votes, choose the modal exact teacher market.
5. Ties are broken by lexical canonical JSON.

Thus every source SHA contributes exactly one vote per turn regardless of how many hard contexts it owns.

## Frozen consensus gate per turn

A turn enters the schedule iff:

- modal teacher market has support from **>=8 of 10 unique source SHAs**;
- the same exact market is observed in **>=16 of 24 hard contexts**.

No outcome, margin, score, or V18A per-context winner is used.

The scheduled market is the exact modal market for that turn.

Turns failing the consensus gate return exact ALL3 unchanged.

## Schedule readiness

`V19A_CONSENSUS_SCHEDULE_READY` requires:

- >=20 scheduled turns inside 464..591;
- every scheduled turn satisfies the 8-source / 16-context gate;
- no source identity appears in the exported runtime schedule;
- schedule JSON is deterministic and canonical.

Otherwise:
`V19A_CONSENSUS_SCHEDULE_NOT_READY`.

## Runtime candidate

If READY, V19B candidate is:

**O-TM1 — P2 Cross-Source Consensus Market Schedule**.

For turn t in 464..591:

- if t is not scheduled: return exact ALL3;
- if scheduled: replace only ALL3.market with the frozen consensus market for t;
- preserve exact ALL3 farmer/hands;
- canonicalize the action.

Conservative SELL projection:
- aggregate each scheduled SELL product;
- cap scheduled aggregate SELL quantity to current legally available own product quantity (shed + carried inventory);
- if cap is zero, drop that SELL order;
- preserve relative order of surviving scheduled orders.

BUY_SEED / BUY_PRODUCT / HIRE orders remain exactly as in the frozen consensus market.
If the environment rejects/invalidates them in causal testing, V19B fails mechanics; no post-hoc clipping rule is added.

No source/opponent identity, seed, seat, context id, replay metadata, future state, score, or margin.

## V19B causal gate

Population:
same 24 binding V13C hard contexts.

Paired:
- BASE exact ALL3;
- TREATMENT exact ALL3 + frozen O-TM1.

Mechanical PASS:
- 24/24 pairs;
- BASE exact frozen score/margin reproduction;
- no source drift/failure;
- schedule hash equals binding V19A artifact;
- treatment changes market only on scheduled turns in 464..591;
- never changes farmer/hands;
- valid completed episode for every pair.

Coverage PASS:
- market changes in >=8 contexts;
- changed contexts span >=4 unique source SHAs.

Strategic PASS:
**`V19B_CONSENSUS_WL_HEADROOM`** iff:
- mechanical PASS;
- coverage PASS;
- positive-score contexts >=4;
- positive-score contexts span >=2 source SHAs;
- negative-score contexts = 0;
- mean score delta >0;
- mean margin delta >0.

If only margin improves without score regressions:
`V19B_CONSENSUS_MARGIN_ONLY_CLOSE`.

Otherwise:
`V19B_CONSENSUS_NO_HEADROOM_CLOSE`.

## Fresh validation if PASS

Only V19B_CONSENSUS_WL_HEADROOM may activate V19C.

Pre-frozen fresh population:
- same 10 exact hard-source SHAs;
- seeds `78601..78604`;
- both seats;
- 80 pairs.

Fresh PASS:
- all 80 pairs mechanical PASS;
- market changes in >=20 contexts;
- positive-score contexts >=2 across >=2 sources;
- negative-score contexts = 0;
- BASE-win -> treatment-nonwin regressions = 0;
- mean score delta >0;
- mean margin delta >=0.

No Kaggle submission is authorized by V19A/V19B alone.
