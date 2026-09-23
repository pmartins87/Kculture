# V28G — ALL3 Residual Hard-Core Census Protocol — 2026-09-22

## Status

PRE-REGISTERED after V28F returned `V28F_NO_MATERIAL_HEDGE_REPLACEMENT`.

No Kaggle mutation is authorized.

## Motivation

V28F used 12 fresh current-frontier sources x 6 fresh seeds x 2 seats = 144 common contexts.

ALL3 won 78 and lost 66. Every tested hedge (V47, O-RW1, CR053, CR029) produced zero ALL3-nonwin -> hedge-win conversions.

The next question is therefore not which existing hedge to choose, but what structure exists inside the 66 residual losses.

## Frozen evidence

Use only the immutable V28F aggregate artifact from workflow `35807910104`:
- artifact name: `v28f-all3-hedge-complementarity`;
- artifact id: `10729759999`;
- digest: `sha256:489a910097a36dd16bc5b6574d94a6aa50c2f3b7686be1fccb25ea41420145ec`.

No rerun of candidate episodes is allowed in V28G.

## Residual loss definition

A residual loss is a V28F context where ALL3 score == 0.0.

Expected from V28F: 66 residual losses.

A universal-hard context is a residual loss where V47, O-RW1, CR053 and CR029 also score 0.0.

## Metrics

### Source structure

For each frontier source SHA:
- representative ref/rank;
- contexts;
- ALL3 wins/losses;
- loss rate;
- mean ALL3 margin;
- median ALL3 loss margin;
- losses by seat;
- distinct losing seeds;
- close / medium / severe loss counts.

Severity buckets:
- close: margin >= -2000;
- medium: -10000 < margin < -2000;
- severe: margin <= -10000.

Concentration:
- top-1 source share of all residual losses;
- top-2 share;
- top-4 share;
- number of sources with >=9 losses out of 12 contexts (>=75% loss rate);
- number with 6–8 losses;
- number with 1–5 losses;
- number with zero losses.

### Seat / seed structure

Report:
- residual losses by seat;
- residual losses by seed;
- loss rate by seat;
- loss rate by seed.

### Overlay effect inside ALL3 losses

On the exact same residual-loss contexts compare margins:
- ALL3 minus V47;
- ALL3 minus O-RW1.

For each comparison report:
- mean margin delta;
- median delta;
- contexts ALL3 margin is better;
- equal;
- worse.

This is diagnostic only; it cannot establish counterfactual causal value beyond the common-context benchmark.

### Deterministic trace targets

Produce at most 12 loss contexts for a later trajectory trace gate:
1. up to 6 closest losses (largest negative ALL3 margins);
2. up to 6 most severe losses (most negative ALL3 margins);
3. within each bucket, prefer source diversity before taking a second context from the same source;
4. ties by source rank, seed, seat.

The target list must record source SHA/ref/rank, seed, seat, ALL3 margin, and all candidate margins.

## Frozen decision

- `V28G_SOURCE_CLUSTERED_HARD_CORE` if top-4 sources account for >=60% of all residual losses.
- otherwise `V28G_BROAD_HARD_CORE`.

Additionally report whether all 66 expected residual losses are universal-hard.

## Routing

Regardless of clustered/broad classification, V28G routes to a trajectory-level trace gate over the deterministic target list.

If clustered:
- trace the dominant sources more deeply.

If broad:
- trace source-diverse close and severe losses.

The next trajectory gate may inspect public/own-observable state, candidate actions, phase-level money/resource deltas and option triggers. Opponent identity is offline forensic metadata only and cannot become a runtime policy feature.

No Kaggle submission is authorized.
