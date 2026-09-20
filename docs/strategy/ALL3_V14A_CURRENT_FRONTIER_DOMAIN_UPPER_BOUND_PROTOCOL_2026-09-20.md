# ALL3 V14A Current-Frontier Domain Upper-Bound Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE BINDING V13C RESULT.**

Activate only if the binding V13C run returns:
`V13C_CURRENT_FRONTIER_HARD_CONTEXTS_READY`.

If V13C is NARROW, TOO_EASY, or mechanically invalid, this protocol remains dormant.

## Purpose

V13C identifies exact-engine current-frontier contexts where ALL3 is non-winning.

V14A asks a broad causal architecture question before inventing another narrow option:

> In those hard contexts, is recoverable W/L headroom carried primarily by market decisions,
> physical/farm decisions, or only by their cross-domain interaction?

Public opponent agents are used only as offline **shadow teachers**. Their identity or code is never
a runtime feature of a future ALL3 option.

## Frozen population

Use **all and only** loss/tie rows from the binding V13C result.

Before V14A execution:
- freeze source SHA;
- freeze source ref/version handle used by V13C;
- freeze seed;
- freeze seat;
- freeze V13C base score/margin.

No hard context may be selected or dropped by treatment outcome.

## Candidate and shadow

Candidate baseline:
exact ALL3 (O-RW1 + O-TW1 + O-LQ2 over the exact V47 host).

For every candidate observation, independently evaluate the exact hash-pinned public source that
generated that V13C hard context. This is the **shadow teacher**.

Reload candidate and teacher state fresh for every episode/mode.

## Frozen modes

1. **BASE**
   - exact ALL3 unchanged.

2. **MARKET_ALL**
   - exact ALL3 farmer + hands;
   - shadow-teacher market list;
   - every turn.

3. **MARKET_W2PLUS**
   - exact ALL3 unchanged through turn 335;
   - from turn 336 onward: ALL3 farmer + hands, shadow-teacher market.

4. **PHYSICAL_ALL**
   - shadow-teacher farmer + hands;
   - exact ALL3 market;
   - every turn.

5. **PHYSICAL_W2PLUS**
   - exact ALL3 unchanged through turn 335;
   - from turn 336 onward: shadow-teacher farmer + hands, ALL3 market.

6. **FULL_ALL**
   - exact shadow-teacher complete action every turn.
   - This is an offline ceiling/control only and can never become a deployable option.

At each turn record:
- whether market differs;
- whether farmer differs;
- number of hand-action differences;
- whether returned hybrid action differs from exact ALL3.

No post-result mode additions.

## Mechanical gate

PASS requires:
- every frozen hard context completes in all six modes;
- BASE exactly reproduces V13C frozen score/margin;
- exact source SHA matches V13C;
- zero source drift;
- zero unhandled runtime failures;
- candidate/teacher modules reset independently between modes.

Hybrid actions are allowed to be processed by the official environment exactly as returned.
Any environment ERROR/invalid episode is a mechanics failure, not a strategic result.

## Strategic labels

A treatment has **W/L headroom** when treatment score > BASE score.

For each mode record:
- improved-score contexts;
- regressed-score contexts;
- improved unique source SHAs;
- mean score delta;
- mean paired margin delta.

Primary domain gate:

### MARKET_HEADROOM
Either MARKET_ALL or MARKET_W2PLUS has:
- >=4 improved-score contexts;
- improvements across >=2 unique source SHAs;
- mean score delta > 0;
- regressed-score contexts <= improved-score contexts / 2.

### PHYSICAL_HEADROOM
Same gate applied to PHYSICAL_ALL / PHYSICAL_W2PLUS.

Decision hierarchy:

- market passes, physical does not:
  **`V14A_MARKET_DOMAIN_HEADROOM`**
- physical passes, market does not:
  **`V14A_PHYSICAL_DOMAIN_HEADROOM`**
- both pass:
  **`V14A_BOTH_DOMAINS_HEADROOM`**
- neither passes, but FULL_ALL improves >=4 contexts across >=2 sources:
  **`V14A_CROSS_DOMAIN_INTERACTION_HEADROOM`**
- even FULL_ALL fails that threshold:
  **`V14A_SHADOW_UPPER_BOUND_NOT_REUSABLE`**

Margin-only evidence without score improvement cannot pass a domain gate.

## Next stage

V14A never promotes a hosted candidate.

For a passing domain:
- build a phenotype/difference atlas from legal state/action structure;
- derive at most one compact first-party mechanism family;
- test it causally without opponent identity;
- validate on untouched seeds before option-library admission.

For CROSS_DOMAIN_INTERACTION:
- do not blindly copy full opponent policies;
- localize the earliest/most recurrent cross-domain divergence shared across hard sources first.

No Kaggle submission.
