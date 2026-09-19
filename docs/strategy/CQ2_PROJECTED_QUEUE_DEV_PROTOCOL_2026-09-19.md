# O-CQ2 Projected Queue Sanitation — Development Protocol — 2026-09-19

## Purpose

Explain enough of the exact V47→V48 market rewrite with a compact first-party mechanism before
spending compute on causal W/L search.

This is **development/parity only**. No candidate may be promoted from these seeds.

## Evidence entering the protocol

Fresh V47×V48 census:
- 8/8 V47 losses;
- mean margin -454;
- 458 market-only divergences;
- 0 physical farmer/hands divergences.

O-CQ1 closed:
- precision 0.2124;
- recall 0.6316;
- 900 false-positive rewrites.

The CQ1 failure showed that pre-action shed is not the market-time availability state.

## Legal projected state

For each exact V47 action, CQ2 first projects only mechanics that can change own shed before or
within the current market queue.

Physical phase, in official execution order:
1. main farmer;
2. hands in list order.

Supported shed mutations:
- shed-adjacent `DROP`;
- shed-adjacent `PLACE`;
- shed-adjacent `PICKUP`;
- animal PLACE on a matching structure is not treated as a shed deposit;
- shed capacity is respected.

Market projection:
- earlier `BUY_PRODUCT` / `BUY_ANIMAL` slots may add inventory before a later SELL;
- SELL availability is consumed in ordered market-slot sequence.

No opponent identity/private state, hidden seed, rating, EpisodeId or future state is a candidate
runtime input.

## Development population

Frozen development seeds:
`73301, 73302, 73303, 73304`, both seats.

Expected agent decisions:
`4 × 2 × 719 = 5,752`.

## Candidate rewrite languages

1. `slot_projected`
   - cap each SELL in place to projected remaining inventory;
   - zero becomes `[]`.

2. `compact_projected`
   - slotwise projected clamp;
   - within each consecutive SELL run, shift surviving SELLs left and pad vacated positions with
     `[]`.

3. `shortage_merge_compact`
   - if same-product queued SELL demand exceeds projected available quantity, allocate available
     quantity to its first SELL occurrence and clear later same-product occurrences;
   - compact surviving SELLs left within the SELL run.

4. `shortage_merge_keep_slots`
   - same shortage merge, but preserve original SELL slot positions.

## Frozen activation grid

`min_step ∈ {0,216,240,252,264,288,312,336,360,384,408,432}`.

These values are frozen before the development result. No extra threshold may be introduced after
seeing this matrix without opening a new named experiment.

## Selection metric

Rank lexicographically by:
1. exact-divergence F1;
2. precision;
3. recall;
4. whole-action accuracy;
5. earlier activation only as final tie-break.

Development labels:
- STRONG if best precision >=0.80 and recall >=0.80;
- PROMISING if both >=0.60;
- otherwise WEAK -> use V4A rather than endless rule fitting.

## Mandatory fresh validation

Development never promotes the option.

The selected configuration must be frozen in
`configs/cq2_frozen_candidate.json` together with SHA-256 of the implementation source.

Validation seeds are frozen independently:
`73401..73404`, both seats.

Validation PASS requires:
- precision >=0.75;
- recall >=0.70;
- F1 >=0.72.

Only a validation PASS may open a causal W/L gate.

## Stop rule

If the frozen rule fails validation:
- do not tune it on validation seeds;
- activate the already-prepared V4A bounded 1–3 turn V48 market oracle.

No Kaggle submission is authorized by CQ2 parity work.
