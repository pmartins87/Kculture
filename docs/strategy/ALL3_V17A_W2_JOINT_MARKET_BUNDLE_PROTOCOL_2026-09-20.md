# ALL3 V17A W2 Joint Market-Edit Bundle Protocol — 2026-09-20

## Status

Frozen after V16B margin-only closure and before V17A descriptive extraction.

## Motivation

Binding evidence:

- V14A MARKET_W2PLUS: 18/24 loss-to-win flips, 7 source families, zero W/L regressions;
- V15A EARLY reorder: exact zero causal effect;
- V16B one-shot W2 FERTILIZER +2: positive margin in all 24 contexts but zero W/L flips.

This suggests the W2 headroom may be carried by a **coordinated bundle** of market edits that appear together on the same turn.

## Source

Use only the binding V14B artifact from workflow `35526759114`.

No new games are run in V17A.

## Event population

Consider only V14B market-divergence events satisfying:
- phase = `W2`;
- at least one elementary edit;
- event belongs to one of the 24 binding hard contexts.

## Eligible elementary edit classes

Use all and only:
- QTY on real SELL products;
- PRESENCE on real SELL products;
- DUPLICATE on real SELL products;
- ORDER_COUNT;
- REORDER.

Exclude:
- EMPTY/_ pseudo-orders;
- BUY/HIRE-only edits;
- exact source identity;
- outcome-derived filters.

Each elementary edit is normalized to:
- kind;
- side/product when applicable;
- dominant direction;
- magnitude bucket when applicable.

## Bundle construction

For each W2 event:
1. form the set of normalized eligible edits present on that event;
2. retain only edit signatures that were recurrent under the binding V14B recurrence gate;
3. discard singleton sets — V17A is specifically about coordination;
4. canonicalize each bundle lexically.

Aggregate exact bundle signatures across events.

## Recurrence gate

A bundle is recurrent only if:
- context support >=4;
- source support >=2;
- exact same normalized bundle appears in all counted occurrences;
- no opponent identity is needed.

## Deterministic selection

Choose exactly one recurrent bundle by:
1. highest unique source support;
2. highest context support;
3. highest occurrence count;
4. earliest median turn;
5. lexical bundle key.

No game outcomes may be used for ranking.

## Decision

If a recurrent multi-edit bundle exists:
**`V17A_W2_JOINT_MARKET_BUNDLE_READY`**.

Otherwise:
**`V17A_W2_JOINT_MARKET_BUNDLE_NOT_COMPRESSIBLE`**.

## Candidate translation

If READY, V17B may translate exactly the selected bundle into one first-party intervention.

Translation rules:
- same W2 phase only;
- no exact-turn whitelist;
- only edits explicitly present in the selected bundle;
- for quantity buckets use the already frozen minimum-in-bucket mapping:
  1 -> 1, 2 -> 2, 3-4 -> 3, 5+ -> 5;
- preserve physical action;
- no source/opponent identity;
- no future information.

Before V17B outcomes, the exact bundle-to-action transformation and fire multiplicity (one-shot vs recurrent) must be frozen from the selected bundle's event-level occurrence structure.

No Kaggle submission.
