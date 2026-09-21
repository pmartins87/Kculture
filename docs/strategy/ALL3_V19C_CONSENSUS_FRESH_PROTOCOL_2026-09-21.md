# ALL3 V19C O-TM1 Fresh Validation — Binding Protocol — 2026-09-21

## Candidate and frozen population

Activate only after `V19B_CONSENSUS_WL_HEADROOM`.

Candidate:
**O-TM1 — P2 Cross-Source Consensus Market Schedule** using the exact binding V19A artifact and schedule SHA256
`c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22`.

Frozen population:
- 10 exact source SHAs from `configs/all3_v19c_consensus_fresh_validation.json`;
- seeds 78601..78604;
- both seats;
- 80 paired BASE/TREATMENT contexts.

Fresh PASS:
- all 80 pairs mechanically clean;
- changed-market coverage >=20 contexts;
- positive-score contexts >=2;
- positive-score contexts span >=2 source SHAs;
- negative-score contexts =0;
- BASE-win -> treatment-nonwin regressions =0;
- mean score delta >0;
- mean margin delta >=0.

Decision:
- `V19C_CONSENSUS_FRESH_PASS`;
- `V19C_CONSENSUS_FRESH_FAIL_CLOSE`;
- `V19C_CONSENSUS_UNDERPOWERED`;
- `V19C_MECHANICS_INVALID`.

No Kaggle submission.

## Mechanical sharding amendment before outcomes

To shorten wall-clock runtime only, the exact 80 frozen pairs may be partitioned across 4 independent jobs by source-list index modulo 4.

Requirements:
- every frozen source appears in exactly one shard;
- every source still runs all 4 frozen seeds × both seats;
- rows are aggregated before any strategic decision;
- aggregator requires exactly 80 unique `(source_sha,seed,seat)` rows;
- all shards must report the exact same binding schedule SHA256;
- final gate is exactly the frozen gate above.

This amendment changes execution mechanics only, not the experiment.
