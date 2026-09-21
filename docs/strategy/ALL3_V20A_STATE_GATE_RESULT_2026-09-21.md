# ALL3 V20A State Gate Result — 2026-09-21

## Binding

Workflow: **35557692905**  
Launch commit: `4613d77ea10d16110edf943948a18ea2d3b63573`  
Binding aggregate artifact: `all3-v20a-state-gate`  
Artifact id: **10620764741**  
Artifact digest: `sha256:422c1683cf20a5d82474a139242a2f96427ee578fc7c70b80ba8eedd310db811`

Decision:

**V20A_GATE_NOT_TRAINABLE**

## Mechanical result

- 5/5 discovery shards completed successfully.
- 120/120 paired BASE vs unconditional O-TM1 contexts were produced.
- zero shard failures.
- exact frozen V19A schedule SHA was used.
- O-TM1 changed market in 120/120 contexts.
- no Kaggle submission.

The workflow conclusion is `failure` only because the frozen aggregator intentionally exits nonzero when the strategic decision is not `V20A_STATE_GATE_READY`.

## Frozen W/L training label result

Training seeds: 78711..78714 = 80 contexts.

- train positive labels (`score_delta > 0`): **0**
- train non-positive labels: **80**
- positive seed support: **0**
- non-positive seed support: **4**

Therefore the pre-registered trainability gate failed before classifier fitting.

No tree was selected.
No threshold was tuned.
V20B is not activated.

## Full 120-context descriptive result

Across discovery seeds 78711..78716:

- positive score contexts: **0**
- negative score contexts: **0**
- neutral score-delta contexts: **120**
- mean score delta: **0.0**
- mean margin delta: **-742.75**

Per-seed margin effect:

| Seed | Contexts | Margin + | Margin - | Mean margin delta |
|---|---:|---:|---:|---:|
| 78711 | 20 | 8 | 12 | +230.2 |
| 78712 | 20 | 20 | 0 | +409.4 |
| 78713 | 20 | 2 | 18 | -1202.0 |
| 78714 | 20 | 9 | 11 | +13.3 |
| 78715 | 20 | 0 | 20 | -4346.7 |
| 78716 | 20 | 20 | 0 | +439.3 |

These margin statistics are diagnostic only. They do not promote O-TM1 and do not replace the frozen W/L gate.

## Interpretation

The V19C regime dependence was real, but the V20A architecture asked the wrong learnability question for this discovery population.

The unconditional O-TM1 schedule produced no W/L changes in any of the 120 new contexts, so a W/L-benefit classifier at turn 464 has no positive class to learn.

At the same time, the sign and magnitude of the margin effect are strongly regime-dependent. That justifies decomposing the fixed schedule causally, but does not justify relabeling margin as W/L or relaxing the V20A gate after seeing the result.

## Closure

O-TM2 / V20 state gate is **closed at V20A**.

- V20B protocol remains archival/dormant.
- dormant V20B implementation must not be executed.
- do not tune the V20A tree, threshold, label or train/holdout split post hoc.
- do not submit O-TM1/O-TM2 to Kaggle.

Next gate: **V21A Semantic Schedule Decomposition**.
