# V31A — V30B Second-Slot Complementarity Protocol — 2026-09-24

## Status

PRE-REGISTERED after explicit user authorization and successful hosted registration of V30B submission `56509591`, before any V31A complementarity outcome is observed.

No V31A result authorizes Kaggle mutation.

## Purpose

Select the best offline second-slot companion for the already-hosted V30B primary by measuring **best-of-two outcome complementarity**, not standalone rating or public-kernel rank.

Current hosted pair:
1. V30B `56509591`;
2. exact V47 `56466970`.

The question is whether V47 should remain the second active submission during the final week.

## Frozen primary

Exact V30B candidate:
- ref `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`;
- main.py SHA `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`;
- exact packaged archive SHA `70d93426baa309e3a13a6c837504e4d73b177cd05d7d2865c024844e1d2abe7b`;
- package artifact from binding V30B-R2 workflow `35906418993`.

## Frozen hedge pool

A. exact V47 historical public package:
- archive SHA `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- main.py SHA `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

B. Every other executable unique public policy frozen in the immutable V30A snapshot from workflow `35877442921`, excluding the exact V30B primary SHA.

No hedge may be selected or removed based on V31A outcomes.

## Frozen opponent/context panel

Reuse the exact immutable binding V30B-R2 fresh frontier and exact binding primary rows from workflow `35906418993`.

Full primary panel:
- all frozen frontier opponents;
- seeds exactly `80511..80516`;
- both seats.

### Pre-run compute clarification

Because the decision target is **best-of-two W/L complementarity**, every context where V30B already wins is algebraically fixed as a pair win regardless of the hedge. Therefore, before observing any V31A hedge result, hedge execution is frozen to the exact V30B-R2 **primary non-win residual contexts only**.

The full 144-context V30B binding rows remain the denominator for pair score-rate calculations. For V30B-win contexts, pair score is fixed to the binding V30B score and no hedge episode is executed.

This is a deterministic compute reduction, not context selection based on hedge outcomes.

No live opponent reacquisition.

## Mechanical requirements

- exact primary package SHA and main SHA;
- exact V47 archive/main SHA;
- all V30A public-policy source SHAs preserved;
- every candidate completes every expected context DONE/DONE with finite rewards and >=720 steps;
- V30B primary rerun terminal score/margin must reproduce binding V30B-R2 rows exactly when available, otherwise the run is mechanically invalid;
- no runtime opponent identity/rank/ref/SHA routing.

## Metrics

For each hedge H:
- hedge W/L/T on the frozen V30B non-win residual set;
- V30B residual-nonwin -> hedge-win conversions;
- V30B loss -> hedge-win conversions;
- V30B loss -> hedge-tie conversions;
- hedge regressions on contexts V30B already wins (reported but do not hurt best-of-two mathematically);
- best-of-two pair score rate;
- pair score delta versus V30B alone;
- residual rescue margin statistics on executed non-win contexts;
- rescue source breadth;
- rescue seed breadth;
- rescue support in both seats.

## Frozen material-replacement gate versus retained V47

A non-V47 hedge is **materially better than retained V47** only if all:

1. best-of-two pair score rate >= V30B+V47 pair score rate + **0.03**;
2. V30B loss->hedge-win conversions >= V47 conversions + **3**;
3. rescue source breadth >= V47 rescue source breadth;
4. rescue seed breadth >= V47 rescue seed breadth;
5. rescue support exists in both seats;
6. mechanics PASS.

## Frozen selector

Among candidates satisfying the material-replacement gate, select by:
1. highest best-of-two pair score rate;
2. highest V30B loss->hedge-win conversions;
3. highest rescue source breadth;
4. highest rescue seed breadth;
5. highest mean residual hedge margin;
6. lower frozen V30A representative rank when available;
7. lexical SHA.

If no non-V47 candidate passes:
`V31A_RETAIN_V47_SECOND_SLOT`.

If one passes:
`V31A_SECOND_SLOT_REPLACEMENT_CANDIDATE_READY`.

Mechanical invalidity:
`V31A_MECHANICS_INVALID`.

## Routing

REPLACEMENT READY:
- freeze exact public ref/SHA/package;
- run one fresh independent V31B validation on a newly acquired frontier and unseen seeds;
- no Kaggle submission before V31B and explicit user authorization.

RETAIN V47:
- keep hosted pair unchanged and focus remaining compute on V30B hosted monitoring/final-week risk management.

No V31A result authorizes a Kaggle submission, deletion, or reordering.
