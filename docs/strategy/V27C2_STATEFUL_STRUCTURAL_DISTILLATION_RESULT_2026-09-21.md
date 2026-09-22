# V27C2 Stateful Structural Distillation — Result — 2026-09-21

## Binding result

Workflow: **`35682535729`**  
Train job: `106603317949`  
Final artifact: `10675616361`  
Digest: `sha256:4a40b1156a52b2bb26ae5473d7bf339e2dab8d1b84b448f53d268ca1b7de434c`

Mechanical:
- 12/12 collection shards PASS;
- 192/192 teacher episodes;
- UNIT training rows: 555,636;
- MARKET-SLOT training rows: 575,200;
- UNIT classes: 83;
- MARKET-SLOT classes: 236;
- UNIT tree depth/leaves: 32 / 5684;
- MARKET tree depth/leaves: 32 / 3458;
- no runtime identity feature;
- no teacher call at inference.

Decision:

**`V27C2_STRUCTURAL_POLICY_DISTILLATION_NOT_VIABLE`**

## Untouched holdout

48 episodes / 34,512 turns.

- complete-action parity: **0.5734817**;
- MARKET parity: **0.6978442**;
- FARMER parity: **0.9541029**;
- HANDS parity: **0.7493046**;
- minimum source complete-action parity: **0.5625869**;
- minimum 120-turn stage complete-action parity: **0.1454861**.

Frozen required gates were:
- complete >= 0.90;
- MARKET >= 0.94;
- FARMER >= 0.99;
- HANDS >= 0.98;
- minimum source >= 0.80;
- minimum stage >= 0.80.

Every principal parity gate fails materially.

Stage parity also deteriorates strongly as the episode progresses:
- stage 0: 0.9888889;
- stage 1: 0.8430556;
- stage 2: 0.7982639;
- stage 3: 0.4302083;
- stage 4: 0.1454861;
- stage 5: 0.2321429.

## Interpretation

The rank-1 teacher is reconstructible by direct replay of bounded legal history (V27B), but **not compressible by the frozen low-complexity structural decision-tree representation**.

The failure is not marginal and cannot be repaired legitimately by:
- depth sweep;
- class weighting;
- history-window changes;
- new post-hoc features;
- source-conditioned models;
- route-ID/table features;
- teacher fallback.

Per the frozen V27C2 protocol:
- close fast rank-1 behavioral distillation for this competition;
- do not activate V27D;
- preserve V27 artifacts as research evidence;
- move to final-slot / competition strategy.

No Kaggle submission is authorized.
