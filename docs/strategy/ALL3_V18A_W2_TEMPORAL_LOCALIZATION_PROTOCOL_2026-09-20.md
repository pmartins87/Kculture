# ALL3 V18A MARKET_W2PLUS Temporal Localization Protocol — 2026-09-20

## Status

ACTIVE after V17B closed without W/L headroom.

The first dormant draft used only turns 336..503. Before any V18A game was run, inspection of the binding V14A implementation confirmed that `MARKET_W2PLUS` means **all turns t >= 336 through episode end**, not only the earlier W2 subphase.

This corrected binding protocol therefore partitions the entire V14A treatment interval. No V18A outcome existed when this correction was made.

## Motivation

Binding evidence:

- V14A MARKET_W2PLUS: 18/24 hard-context score improvements, 7 source families, mean score delta +0.75, mean margin delta +1858.5, zero score regressions;
- V15A EARLY reorder: zero causal effect;
- V16B one-shot W2 FERTILIZER +2: margin-only;
- V17B STRAWBERRY edge bundle: no W/L headroom and negative mean margin.

Rather than selecting additional atlas phenotypes post-hoc, localize where in the full `t >= 336` market-treatment horizon the W/L headroom resides.

## Population

All and only the same 24 binding V13C hard contexts.

Exact source SHAs, seeds and seats are unchanged.

## Candidate baseline

Exact ALL3.

## Frozen equal chronological partitions

The V14A MARKET_W2PLUS interval is turns `336..718` inclusive = 383 turns.

Partition deterministically into three contiguous chronological segments:

- **P1**: turns `336..463` inclusive — 128 turns;
- **P2**: turns `464..591` inclusive — 128 turns;
- **P3**: turns `592..718` inclusive — 127 turns.

No boundary may change after this protocol.

## Modes

For each context run:

1. **BASE** — exact ALL3.
2. **MARKET_P1_ONLY** — shadow-teacher market only in P1.
3. **MARKET_P2_ONLY** — shadow-teacher market only in P2.
4. **MARKET_P3_ONLY** — shadow-teacher market only in P3.
5. **MARKET_P12** — shadow-teacher market in P1+P2 only.
6. **MARKET_P23** — shadow-teacher market in P2+P3 only.
7. **MARKET_P123** — shadow-teacher market for every turn t>=336.

Physical action always remains exact ALL3.

The public hard-source policy is an offline shadow teacher only and is never a runtime feature.

## Mechanical gate

PASS requires:

- all 24 contexts × 7 modes complete;
- BASE exactly reproduces frozen V13C score/margin for every context;
- **MARKET_P123 exactly reproduces the binding V14A MARKET_W2PLUS treatment score and treatment margin for every context**;
- binding V14A source: workflow `35526276641`, artifact `all3-v14a-mechanical-completion`;
- zero source drift;
- candidate and teacher state reset independently between modes;
- no physical-action substitution.

Any P123/V14A mismatch is:
**`V18A_V14A_REPLICATION_FAILURE`** and invalidates temporal interpretation.

## Strategic localization

For each non-BASE mode record:

- loss-to-win flips;
- positive/negative score contexts;
- unique source SHAs with score improvement;
- mean score delta;
- mean margin delta.

A mode has W/L headroom iff:

- score-improved contexts >=4;
- improvements span >=2 unique source SHAs;
- mean score delta >0;
- mean margin delta >0.

## Decision

Use deterministic specificity order:

1. If one or more single partitions pass, select the passing single partition with:
   - most score-improved contexts;
   - then most unique improved source SHAs;
   - then highest mean score delta;
   - then chronological order P1 < P2 < P3.

   Decision: **`V18A_SINGLE_PARTITION_HEADROOM`**.

2. Else if P12 or P23 passes, choose by the same metrics and chronological order.
   Decision: **`V18A_ADJACENT_PARTITIONS_HEADROOM`**.

3. Else if only P123 passes:
   **`V18A_DISTRIBUTED_HEADROOM`**.

4. If P123 fails exact binding replication:
   **`V18A_V14A_REPLICATION_FAILURE`**.

5. Mechanics failure:
   **`V18A_MECHANICS_INVALID`**.

## Next stage

V18A is localization only.

A passing partition narrows the next fresh phenotype/action-difference atlas to that pre-frozen temporal region.
No exact-turn rule, source identity, or teacher policy may be promoted directly.

No Kaggle submission.
