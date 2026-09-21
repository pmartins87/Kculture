# ALL3 V22B Fresh-Frontier Domain Upper-Bound Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED BEFORE V22A OUTCOMES.

Activate only if binding V22A returns:
`V22A_FRESH_FRONTIER_HARD_POPULATION_READY`.

Otherwise V22B remains dormant.

## Purpose

V22A refreshes the current executable public frontier and freezes fresh ALL3 non-win contexts.

V22B asks one architecture-level causal question before any new option is invented:

> On the refreshed hard population, is recoverable W/L headroom carried by MARKET decisions,
> PHYSICAL decisions, or only by their cross-domain interaction?

The public opponent for each frozen context is used only as an offline shadow teacher.
Opponent identity/code is never a deployable runtime feature.

## Frozen population

Use all and only V22A rows with `score < 1.0`.

For each context freeze:
- context_id;
- current representative rank;
- exact ref used by V22A;
- exact `main_sha256`;
- seed;
- seat;
- V22A BASE score;
- V22A BASE margin.

No context may be added/dropped based on V22B treatment outcomes.

The hard-context config must be materialized mechanically by `tools/materialize_v22b_hard_config.py`, which accepts all and only binding V22A rows with `score < 1.0` and rejects any binding/acquisition/smoke/episode inconsistency.

## Candidate baseline

Exact ALL3:
- exact V47 base host;
- O-RW1;
- O-TW1;
- O-LQ2.

Fresh candidate and teacher state for every context/mode.

## Frozen modes

Exactly four modes:

1. **BASE**
   - exact ALL3.

2. **MARKET_ONLY**
   - exact ALL3 farmer;
   - exact ALL3 hands;
   - shadow-teacher market list;
   - every turn.

3. **PHYSICAL_ONLY**
   - shadow-teacher farmer;
   - shadow-teacher hands;
   - exact ALL3 market;
   - every turn.

4. **FULL_SHADOW**
   - exact shadow-teacher complete action every turn;
   - offline ceiling/control only;
   - never deployable.

No W2/W3 time slicing, thresholds, product subsets, action subsets or post-result modes.

At each turn record:
- market difference;
- farmer difference;
- hand-action difference count;
- whether hybrid action differs from exact ALL3.

## Mechanical gate

PASS requires:
- all frozen V22A hard contexts complete in all four modes;
- BASE exactly reproduces V22A frozen score and margin;
- exact source SHA matches V22A;
- zero source drift;
- zero unhandled episode/runtime failures;
- candidate/opponent/shadow teacher states are independent;
- Kaggle credentials removed before third-party code execution.

Any failure -> `V22B_MECHANICS_INVALID`.

## W/L headroom metric

For a non-BASE mode, a context is improved iff:
`treatment_score > BASE_score`.

A domain mode passes when all are true:
- improved-score contexts >=4;
- improved contexts span >=2 unique source SHAs;
- improved contexts span >=2 V22A discovery seeds;
- mean score delta >0;
- regressed-score contexts <= improved-score contexts / 2.

Margin-only evidence cannot pass.

## Decision hierarchy

- MARKET_ONLY passes, PHYSICAL_ONLY does not:
  `V22B_MARKET_DOMAIN_HEADROOM`.

- PHYSICAL_ONLY passes, MARKET_ONLY does not:
  `V22B_PHYSICAL_DOMAIN_HEADROOM`.

- both pass:
  `V22B_BOTH_DOMAINS_HEADROOM`.

- neither domain passes, but FULL_SHADOW has:
  - >=4 improved-score contexts;
  - >=2 source SHAs;
  - >=2 seeds;
  - mean score delta >0:
  `V22B_CROSS_DOMAIN_INTERACTION_HEADROOM`.

- otherwise:
  `V22B_NO_DOMAIN_WL_HEADROOM_RESET`.

## Next-stage rule

If MARKET or PHYSICAL passes:
- open at most one new mechanism-discovery family in that passing domain;
- derive it from legal state/action structure across multiple refreshed sources;
- no opponent identity;
- no direct teacher copying;
- causal validation required before option admission.

If CROSS_DOMAIN_INTERACTION passes:
- localize recurrent interaction structure first;
- do not deploy FULL_SHADOW.

If `V22B_NO_DOMAIN_WL_HEADROOM_RESET`:
- stop ALL3 local-option mining;
- do not create V23 micro-patches around the same architecture;
- trigger an architectural reset / competition-strategy reassessment.

No Kaggle submission is authorized by V22B.
