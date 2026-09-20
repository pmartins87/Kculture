# ALL3 V13C Current Frontier Hard-Context Census — Conditional Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V13B RESULT.**

Activate only if V13B returns:
`V13B_EXECUTABLE_FRONTIER_READY`.

## Purpose

The frozen seven-agent league became trivial for ALL3 (V12A: 112W–0L).

V13C asks whether the refreshed, mechanically executable **current Top-30 source frontier**
contains exact-engine contexts where ALL3 is not dominant and can therefore support causal
mechanism discovery.

This is NOT a hosted-strength estimator. CR073 already falsified that interpretation.

## Population

After V13B completes:

- take exactly one current representative per unique source SHA that passed both-seat smoke;
- freeze its current notebook ref, current rank aliases and exact `main.py` SHA in a config before any V13C episode runs;
- never select/drop a source using local W/L;
- sources that fail V13B smoke are excluded mechanically, not strategically.

## Frozen exact-engine census

Engine:
`kaggle-environments==1.32.7`.

Candidate:
exact ALL3 unchanged.

Fresh seeds:
- `78101`
- `78102`

Both seats.

For each source representative × seed × seat:
- run one complete episode;
- record W/L score and margin;
- record public own/opponent farm snapshots at steps
  `336, 408, 456, 504, 552, 600, 648, 696`;
- record own option fire counts for O-RW1/O-TW1/O-LQ2 if available from host state;
- no treatment is applied.

## Mechanical gate

PASS requires:
- every frozen representative attempted on both seeds and both seats;
- zero source-SHA drift;
- every successful source uses the official hosted-faithful callable;
- no ALL3 policy modification.

A source-level runtime failure after V13B smoke is recorded as mechanics failure for that source
and cannot be silently dropped from strategic accounting.

## Strategic diagnostic labels

A **hard context** is an ALL3 loss or tie.

Decision:

1. >=4 hard contexts across >=2 unique source SHAs:
   **`V13C_CURRENT_FRONTIER_HARD_CONTEXTS_READY`**
   — freeze all hard contexts and use them for bounded causal mechanism/oracle discovery.

2. 1–3 hard contexts, or hard contexts from only one unique source:
   **`V13C_CURRENT_FRONTIER_HARD_CONTEXTS_NARROW`**
   — retain the contexts but do not fit a broad router/selector; require hosted evidence to nominate
   the next mechanism.

3. zero hard contexts:
   **`V13C_LOCAL_FRONTIER_TOO_EASY`**
   — close current local H2H as a discovery population and return to hosted replay/state/action
   forensics. Do not add seeds just to manufacture losses.

## Restrictions

- no opponent identity as runtime feature;
- no ranking by local H2H;
- no post-hoc seed expansion to rescue a sparse result;
- no third-party code persisted in the repository;
- no Kaggle submission.

