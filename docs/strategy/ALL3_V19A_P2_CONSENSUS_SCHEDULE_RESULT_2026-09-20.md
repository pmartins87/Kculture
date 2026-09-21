# ALL3 V19A P2 Cross-Source Consensus Market Schedule — Binding Result — 2026-09-20

Workflow: **`35552885627`**.

Decision: **`V19A_CONSENSUS_SCHEDULE_READY`**.

## Input

Frozen V18B dataset artifacts:
- workflow `35552335995`;
- 3072 P2 rows;
- 24 hard contexts;
- 10 unique source SHAs;
- turns 464..591.

## Source-balanced extraction

Every source SHA contributed exactly one modal market vote per turn.

Turn schedule gate:
- modal exact market supported by >=8/10 source SHAs;
- same market observed in >=16/24 hard contexts.

## Result

- scheduled turns: **102/128**;
- minimum scheduled source support: **8/10**;
- minimum scheduled context support: **16/24**;
- no source identity appears in runtime schedule.

The schedule contains both no-order turns and exact market programs including SELL, BUY_SEED, BUY_PRODUCT and HIRE sequences.

Examples with 10/10 source support:
- 468 -> BUY_SEED WHEAT 1;
- 480 -> SELL MILK 1 + nine HIRE;
- 493 -> SELL STRAWBERRY 2;
- 517 -> SELL STRAWBERRY 8 + BUY_SEED WHEAT 2;
- 518 -> SELL STRAWBERRY 2;
- 523 -> SELL STRAWBERRY 16 + BUY_SEED WHEAT 1;
- 570 -> SELL MILK 6;
- 576 -> SELL STRAWBERRY 10 + nine HIRE;
- 590/591 -> BUY_SEED CARROT 1.

The schedule is an outcome-free cross-source consensus artifact and is now frozen for V19B.

No Kaggle submission.
