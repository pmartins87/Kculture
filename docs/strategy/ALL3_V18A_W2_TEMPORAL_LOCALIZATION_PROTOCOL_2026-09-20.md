# ALL3 V18A W2 Market-Headroom Temporal Localization Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V17B RESULT.**

Activate only if V17B does **not** return `V17B_LQ6S_WL_HEADROOM`.

## Motivation

Binding evidence already establishes:

- V14A MARKET_W2PLUS: 18/24 hard-context loss-to-win flips, zero W/L regressions;
- isolated EARLY reorder (V15A): exact zero causal effect;
- isolated W2 FERTILIZER +2 (V16B): margin-only;
- V17B tests the strongest recurrent STRAWBERRY insertion bundle with an identity-free edge trigger.

If V17B fails W/L, do **not** select a second-ranked V14B phenotype post-hoc.
Instead localize where inside W2 the full teacher-market upper-bound is carried.

## Population

All and only the same 24 binding V13C hard contexts.

Exact source SHAs, seeds and seats are unchanged.

## Candidate baseline

Exact ALL3.

## Frozen W2 windows

Partition W2 `336..503` into exactly three contiguous windows of 56 turns:

- **W2A**: turns `336..391`
- **W2B**: turns `392..447`
- **W2C**: turns `448..503`

No window boundary may change after V17B.

## Modes

For each context run:

1. **BASE** — exact ALL3.
2. **MARKET_W2A_ONLY** — shadow-teacher market only during W2A; ALL3 market elsewhere.
3. **MARKET_W2B_ONLY** — shadow-teacher market only during W2B.
4. **MARKET_W2C_ONLY** — shadow-teacher market only during W2C.
5. **MARKET_W2AB** — shadow-teacher market during W2A+W2B only.
6. **MARKET_W2BC** — shadow-teacher market during W2B+W2C only.
7. **MARKET_W2ABC** — exact V14A MARKET_W2PLUS replication during all W2.

Physical action always exact ALL3.

The public hard-source policy is an offline shadow teacher only and is never a runtime feature.

## Mechanical gate

PASS requires:

- all 24 contexts × 7 modes complete;
- BASE exactly reproduces frozen V13C score/margin;
- MARKET_W2ABC reproduces the corresponding V14A MARKET_W2PLUS paired score/margin;
- zero source drift;
- candidate/teacher state reset independently between modes;
- no physical action substitution.

## Strategic localization

For each non-BASE mode record:

- loss-to-win flips;
- positive/negative score contexts;
- unique source SHAs with score improvement;
- mean score delta;
- mean margin delta.

A window mode has **W/L headroom** iff:

- loss-to-win flips >=4;
- flips span >=2 unique source SHAs;
- mean score delta >0;
- mean margin delta >0.

## Decision

Use deterministic specificity order:

1. If one or more **single-window** modes pass, select the passing single window with:
   - most loss-to-win flips;
   - then most unique improved source SHAs;
   - then highest mean score delta;
   - then earliest window lexical order W2A < W2B < W2C.

   Decision: **`V18A_SINGLE_W2_WINDOW_HEADROOM`**.

2. Else if W2AB or W2BC passes, choose by the same metrics, then lexical order.
   Decision: **`V18A_ADJACENT_W2_WINDOWS_HEADROOM`**.

3. Else if only W2ABC passes:
   **`V18A_DISTRIBUTED_W2_HEADROOM`**.

4. If even W2ABC fails to reproduce V14A W/L headroom:
   **`V18A_V14A_REPLICATION_FAILURE`**.

5. Mechanics failure:
   **`V18A_MECHANICS_INVALID`**.

## Next stage

V18A is localization only.

A passing window narrows a fresh phenotype/action-difference atlas to that fixed temporal region.
No exact-turn rule, source identity, or teacher policy may be promoted directly.

No Kaggle submission.
