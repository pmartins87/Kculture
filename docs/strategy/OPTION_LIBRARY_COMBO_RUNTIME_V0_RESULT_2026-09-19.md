# Option Library Composition Runtime V0 — Result — 2026-09-19

## Binding result

The original serial run `35424958961` was cancelled before completion and is non-binding.

The parallel-equivalent run `35426256016` completed all seven opponent shards mechanically
clean. The aggregate job itself failed only because that lightweight job did not install
`kaggle-environments` before importing the shared summarizer. This is an aggregation-harness
dependency error, not a shard or strategy failure.

Binding result is reconstructed exactly from the seven successful shard summaries because every
block has the same eight contexts (4 fresh seeds × 2 seats).

Decision: **`OPTION_LIBRARY_COMBO_ADVANCE`**.

## Population result

Total: **56 matched contexts**.

Score rates:
- BASE: **0.7857143**;
- O-RW1: **0.8392857**;
- O-TW1: **0.8392857**;
- BOTH: **0.8392857**.

Therefore:
- BOTH vs BASE score delta: **+0.0535714**;
- BOTH vs best single score delta: **0.0**;
- score-regressing opponent blocks: **0/7**;
- nonnegative opponent blocks: **7/7**.

The W/L gain is concentrated in the V47 mirror block:
- BASE: 0.500;
- RW1: 0.875;
- TW1: 0.875;
- BOTH: 0.875;
- delta BOTH vs BASE: **+0.375**.

All other six blocks are W/L-neutral under the composition gate.

## Margin diagnostics

Composition is W/L-safe in this gate but not uniformly margin-positive.

Examples:
- router_2715: BASE +7,515.75 -> BOTH +7,564.50;
- Ready Stock: +1,183.875 -> +1,245.375;
- V48: -611.0 -> -558.25;
- Conditional Memory: +47,865.25 -> +47,882.50;
- Best Market: +38,135.375 -> +37,647.75;
- Tactical Memory: +54,739.625 -> +52,071.375.

This is why **ADVANCE means “safe current option-library host”**, not “BOTH is proven superior to
O-TW1 everywhere”. No hosted submission is authorized from this gate alone.

## Interpretation

O-RW1 and O-TW1 may coexist in the offline option-library host:
- both fire at least once in every tested context;
- no W/L regression appeared in any opponent block;
- the combination preserves the mirror W/L gain.

However, the composition adds no W/L value over the best single option in this sample. The project
still needs new option families, especially for hard opponents such as V48.

## Next step

Keep BOTH available as the current offline host while option discovery continues. Do not spend
compute merely proving the same composition on more seeds unless a new interaction hypothesis
appears.

No Kaggle submission is authorized by this result.
