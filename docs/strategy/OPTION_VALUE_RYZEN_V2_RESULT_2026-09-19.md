# Option-Value Ryzen V2 — Result — 2026-09-19

## Status

Binding result: **MECHANICS PASS / CURRENT OPTION LIBRARY HAS INSUFFICIENT CROSS-FAMILY W/L COVERAGE FOR A PRODUCTION SELECTOR**.

This does **not** close the Prize Solver architecture. It closes the idea that simply fitting a larger
selector on O-RW1 + O-TW1, with the current label distribution, is enough to obtain broad
opponent-family adaptation.

## Frozen run

Source commit used by the user Ryzen run:
`2c402f54462bb31be4f1061c64efe11613b24253`.

Configuration:
- `kaggle-environments==1.32.7`;
- 150 fresh seeds;
- 7 opponents;
- both seats;
- O-RW1 and O-TW1;
- 31 workers;
- maximum / realized rows: **4,200 / 4,200**.

League:
1. V47 mirror;
2. Ready Stock;
3. V48;
4. `2715.6` multi-program router;
5. Conditional Memory;
6. Tactical Memory;
7. Best Market Agent.

## Mechanical result

- completed seeds: **150/150**;
- matchups: **2,100**;
- counterfactual rows: **4,200**;
- unique state hashes: **1,238**;
- failures: **0**;
- mechanical pass: **true**.

Manifest config SHA-256:
`bb689a1331bb51ed485fab6a50fd2896ed0608ff2d87e43d88124a630a2d2c64`.

## By option

### O-RW1

- rows: 2,100;
- mean W/L-score delta: **+0.0352381**;
- positive: **208**;
- negative: **60**;
- neutral: **1,832**;
- mean margin delta: **-88.5776**;
- unique state hashes: **703**.

### O-TW1

- rows: 2,100;
- mean W/L-score delta: **+0.0571429**;
- positive: **253**;
- negative: **16**;
- neutral: **1,831**;
- mean margin delta: **+85.7710**;
- unique state hashes: **535**.

O-TW1 remains the cleaner option in this sample.

## Population decomposition

Each opponent contributes 600 rows.

- V47 mirror: mean score delta **+0.3183333**; **458 positive / 76 negative**.
- Ready Stock: mean score delta **+0.0033333**; **2 positive / 0 negative**.
- `2715.6`: mean score delta **+0.0016667**; **1 positive / 0 negative**.
- V48: score delta **0**; no non-neutral W/L labels.
- Conditional Memory: score delta **0**; no non-neutral W/L labels.
- Tactical Memory: score delta **0**; no non-neutral W/L labels.
- Best Market Agent: score delta **0**; no non-neutral W/L labels.

Therefore **458 of 461 positive W/L labels (99.35%) are against the V47 mirror**.
Outside V47 there are only **3 positive labels in 3,600 rows** and **0 negative labels**.

## Interpretation

The V1 whole-seed audit proved that legal-state features can learn option value across unseen seeds
inside the sampled population. V2 now shows the limiting factor is not sample count or model
capacity: it is **option support**.

A larger ridge/tree/MLP trained now would mostly learn when the existing two options help against
the V47 family. It cannot learn broad cross-family improvements when those improvements are absent
from the labels.

The correct next move is:
1. retain O-RW1 and O-TW1;
2. test their composition for interaction/synergy;
3. discover additional first-party options with exact-engine W/L headroom against non-V47 families;
4. only then refit the multi-option selector/value model.

## Binding stop rule

Do **not** scale this exact O-RW1/O-TW1 dataset merely by adding more seeds.
Additional compute is justified only after:
- a new option adds nontrivial W/L support outside the V47-mirror stratum, or
- a new legal feature/opponent-model hypothesis is tied to a reproducible causal mechanism.

## Hosted policy

No Kaggle submission is authorized by this result.
Preserve the two currently active hosted slots while offline option discovery continues.
