# ALL3 V22B Functional-Diversity Interpretation Rule — 2026-09-21

## Status

PRE-REGISTERED while binding V22B workflow `35566168354` is running and before any V22B treatment outcome has been read.

This document does **not** change the frozen V22B decision gate. It constrains only how a passing result may be interpreted for the next mechanism-discovery stage.

## Motivation from V22A BASE evidence

Binding V22A evaluated 12 selected current-frontier source SHAs on the exact same 12 seed/seat contexts.

The exact ordered BASE outcome vector
`(seed, seat, score, margin)`
revealed that three distinct source SHAs are outcome-identical on all 12 contexts:

- rank 1 — `nathanjacob/kaggriculture-pipe16-idle-workers`;
- rank 2 — `haodou092/notebookdb6965aa8e`;
- rank 11 — `romantamrazov/kaggriculture-yummers`.

Their source SHAs differ, so they remain distinct under the frozen V22B gate, but the available evidence does not justify treating them as three independent behavioral regimes.

Among the 8 hard V22A source SHAs, this collapses the BASE outcome-vector diversity from 8 SHA identities to **6 observed functional outcome clusters**.

This is an interpretive warning, not a retroactive population change.

## Frozen rule

V22B continues to use its original gate exactly:

- improved-score contexts >=4;
- improved contexts across >=2 source SHAs;
- improved contexts across >=2 seeds;
- mean score delta >0;
- regressions <= improvements / 2.

No V22B threshold is changed.

However, after V22B:

1. If a passing MARKET_ONLY or PHYSICAL_ONLY result spans >=2 source SHAs **and** those positive SHAs span >=2 distinct V22A BASE outcome-vector clusters, cross-source robustness may be described directly.

2. If a passing result satisfies the SHA gate but all positive SHAs belong to only one observed BASE outcome-vector cluster, the V22B decision label still stands, but the evidence is classified as **source-SHA pass / functional-diversity unconfirmed**.

3. In that second case, the next mechanism family may still be opened because the frozen V22B gate passed, but it must obtain fresh validation across at least two functionally distinct sources before option-library admission or hosted promotion.

4. No source may be removed from V22B because it appears clone-like.

5. No treatment outcome may be used to redefine the clusters.

## Cluster construction

Clusters are frozen from V22A BASE only, before V22B outcomes:

- sort each source's 12 binding V22A rows by seed then seat;
- fingerprint the exact vector of `score, margin`;
- identical vectors are one observed functional outcome cluster.

This is deliberately conservative. It does not claim code/action-trace identity; it only prevents overstating independence where observed outcomes are exactly identical.

No Kaggle submission is authorized by this rule.
