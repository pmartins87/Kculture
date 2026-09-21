# ALL3 V23 — Immutable Snapshot Frontier Refresh + Domain Upper Bound Protocol — 2026-09-21

## Status

PRE-REGISTERED before any V23 execution.

V22B closed as `V22B_EXACT_ROUTING_INCONCLUSIVE_SOURCE_UNAVAILABLE` because one third-party public notebook changed between population discovery and upper-bound replay. V23 exists to remove that reproducibility failure mode, not to relax strategic thresholds.

## Goal

Run a fresh current-frontier hard-population refresh and the same domain upper-bound test while preserving the exact third-party bytes used for discovery in an immutable workflow artifact.

No V23B source may be reacquired from a mutable live Kaggle ref.

## V23A — immutable current-frontier snapshot

At workflow start:

1. query current public Kaggriculture Top-30 by score exactly once;
2. attempt to acquire refs serially with bounded retry/backoff;
3. compute SHA256 of acquired `main.py`;
4. deduplicate exact SHAs;
5. smoke each unique source in both seats against starter on smoke seed `79300`;
6. exclude exact V47 base identity;
7. select up to 12 unique executable representatives by current representative rank only;
8. snapshot the exact selected `main.py` bytes plus V47 base bytes into a workflow artifact before causal evaluation;
9. remove Kaggle credentials before executing third-party code;
10. run exact ALL3 against every selected source on fresh seeds
   `79301..79306`, both seats.

### Acquisition rule

Unlike V22A, V23A does not require every Top-30 ref to be downloadable.
A missing/removed/private live ref is an availability fact, not a strategic outcome.

Mechanical validity requires:
- current Top-30 listing succeeds;
- >=8 unique executable selected SHAs;
- every selected source passes both-seat smoke;
- every selected source is snapshot-persisted with SHA reverified;
- exact V47 base is snapshot-persisted with expected SHA;
- expected discovery contexts >=96;
- all expected discovery contexts complete;
- zero episode failures;
- no selected-source SHA mismatch between acquisition, snapshot, and execution.

Unavailable non-selected refs are recorded but do not invalidate the run.

### Fresh hard-population gate

Hard row = exact ALL3 discovery row with `score < 1.0`.

`V23A_IMMUTABLE_HARD_POPULATION_READY` iff:
- mechanical validity passes;
- hard contexts >=12;
- hard contexts span >=4 unique selected SHAs;
- hard contexts span >=3 of the six fresh seeds.

Otherwise:
- mechanically valid but insufficient hard population =>
  `V23A_FRONTIER_TOO_EASY_REFRESH_LATER`;
- mechanical failure =>
  `V23A_MECHANICS_INVALID`.

No threshold may be tuned after seeing V23A.

## V23B — immutable-snapshot domain upper bound

Activate only if V23A returns `V23A_IMMUTABLE_HARD_POPULATION_READY`.

Population:
- all and only V23A hard rows;
- exact ref, SHA, seed, seat, BASE score, and BASE margin frozen.

Source loading:
- teacher/opponent code comes only from the V23A immutable snapshot artifact;
- exact SHA must be verified before every source is accepted;
- no Kaggle source reacquisition is allowed in V23B.

Modes remain exactly:
- BASE;
- MARKET_ONLY;
- PHYSICAL_ONLY;
- FULL_SHADOW.

Semantics remain exactly V22B:
- MARKET_ONLY = ALL3 physical behavior + snapshot-teacher market;
- PHYSICAL_ONLY = snapshot-teacher farmer/hands + ALL3 market;
- FULL_SHADOW = complete snapshot teacher;
- BASE = exact ALL3.

### Domain pass criteria — unchanged from V22B

MARKET or PHYSICAL passes iff:
- improved-score contexts >=4;
- improved contexts span >=2 source SHAs;
- improved contexts span >=2 seeds;
- mean score delta >0;
- regressed-score contexts <= improved-score contexts / 2.

FULL_SHADOW interaction ceiling passes iff:
- improved-score contexts >=4;
- improved contexts span >=2 source SHAs;
- improved contexts span >=2 seeds;
- mean score delta >0.

Decision labels:
- `V23B_MARKET_DOMAIN_HEADROOM`;
- `V23B_PHYSICAL_DOMAIN_HEADROOM`;
- `V23B_BOTH_DOMAINS_HEADROOM`;
- `V23B_CROSS_DOMAIN_INTERACTION_HEADROOM`;
- `V23B_NO_DOMAIN_WL_HEADROOM_RESET`;
- `V23B_MECHANICS_INVALID`.

## Functional-diversity interpretation

After V23A, cluster selected sources only from exact V23A BASE outcome vectors on the 12 fresh seed/seat contexts.

This clustering is descriptive only and cannot change V23B's frozen domain pass criteria.

If BOTH passes, select the first mechanism family using the already frozen ordering:
1. more improved functional clusters;
2. more improved-score contexts;
3. more improved seeds;
4. more improved source SHAs;
5. larger mean score delta;
6. larger mean margin delta;
7. MARKET lexical tie-break.

## Routing

- MARKET pass => open one new market-mechanism family.
- PHYSICAL pass => open one new physical-mechanism family.
- BOTH => open exactly one family via deterministic selector above.
- CROSS_DOMAIN only => interaction-architecture reset.
- NO_DOMAIN => baseline-architecture / competition-strategy reset.
- MECHANICS_INVALID => mechanics only; no strategic mutation.

## Reproducibility invariant

Once V23A snapshots a selected SHA, all V23B evidence for that source must come from those snapshotted bytes.

A later public ref mutation, deletion, privacy change, or ranking change is irrelevant to V23B.

## Kaggle

No V23A or V23B result automatically authorizes a Kaggle submission.
