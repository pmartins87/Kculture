# V29A — Recurrent Structural Teacher Distillation Protocol — 2026-09-23

## Status

PRE-REGISTERED after V28N final-week audit established that the protected pair is far outside prize contention and after V23–V28 closed compact-option, short imitation, tree-distillation, classifier-gating, and physical-imitation rescue routes.

No V29A outcome may authorize a Kaggle submission directly.

## Motivation

Binding evidence:

- V25A: only a persistent whole-episode stronger policy preserves W/L headroom; finite shadow prefixes <=256 lose the gain.
- V27B: legal observation history is sufficient to reconstruct the rank-1 teacher's hidden policy state.
- V27C/V27C2: fast tree-based behavioral distillation fails because the teacher has a large structured action space and late-episode generalization collapses.
- V28N: on 2026-09-23 the better protected active submission was about 1097 rating points below the current Top-10 threshold, so final-week prize strategy requires a genuinely higher-ceiling architecture rather than preserving the current pair alone.

## Frozen teacher and data

Teacher:
- ref `ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`;
- SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`.

Use only the already-collected immutable V27C2 structural datasets from workflow `35682535729`:
- all 12 `v27c2-data-*` artifacts;
- 192 teacher episodes;
- no new teacher/opponent source acquisition;
- no Kaggle credentials at training/evaluation runtime.

The V27C2 datasets already retain:
- sequential 136-d turn-global vectors, whose first 114 columns are exact legal `solver.programme_features`;
- actor-local legal features (104 dims);
- actor index / turn alignment;
- exact unit-action labels;
- exact 10-slot market labels;
- episode source/seed/seat boundaries.

V29A intentionally ignores the V27C2 hand-crafted 22-d compact memory tail and learns recurrent legal memory directly from the sequential 114-d observations.

## Frozen split

Exactly reuse V27C2:

Training:
- seeds `79901..79905`;
- opponent ranks `1,2,4,5,6,7,9,10`.

Validation:
- seed `79906`;
- all 12 opponents.

Untouched holdout:
- seeds `79907,79908`;
- all 12 opponents.

All other episodes are unused for fitting.

No holdout information may choose features, dimensions, epochs, learning rate, thresholds, or model family.

## Runtime-legal recurrent state

At each candidate turn t:
- input only the current 114 `solver.programme_features`;
- normalize using TRAIN-only mean/std;
- update one recurrent hidden state initialized to zero at episode start.

No:
- opponent ref/rank/SHA/name;
- source identity;
- seed;
- EpisodeId;
- future observation;
- hidden opponent-private state;
- teacher call;
- copied route ID/table.

## Frozen model

Framework for offline fitting:
PyTorch.

Global memory encoder:
- one GRU layer;
- input size 114;
- hidden size **64**;
- recurrent state persists across the full episode;
- no dropout.

UNIT decoder:
- input = GRU hidden 64 + exact V27C2 actor-local legal features 104;
- TRAIN-only actor-local normalization;
- Linear(168 -> 64);
- ReLU;
- Linear(64 -> number of TRAIN unit-action labels).

MARKET-SLOT decoder:
- input = GRU hidden 64 + one-hot market slot index 10;
- Linear(74 -> 64);
- ReLU;
- Linear(64 -> number of TRAIN market-slot labels).

Teacher actions are used only as offline labels.

## Frozen loss

Per episode:
- UNIT cross entropy averaged with actor-0/farmer sample weight **3.0**, all hand samples weight 1.0;
- MARKET-SLOT cross entropy averaged with non-`<NONE>` slot weight **2.0**, `<NONE>` weight 1.0;
- total loss = UNIT loss + MARKET loss.

No class-frequency weighting.

Optimizer:
- AdamW;
- learning rate `1e-3`;
- weight decay `1e-4`;
- gradient norm clip `1.0`;
- **8 epochs exactly**;
- no early stopping;
- no scheduler;
- random seed `20260923`;
- CPU deterministic execution where supported.

The epoch-8 model is binding. Validation does not select an epoch.

## Structural reconstruction

For each evaluation turn:
- predict one exact UNIT label for every currently observed actor;
- actor 0 is farmer, remaining ordered actors are hands;
- predict exactly 10 market slots;
- output market orders until first predicted `<NONE>`;
- reconstruct FARMER, HANDS, MARKET and complete action.

Any truth label absent from TRAIN vocabulary counts as incorrect; no post-hoc vocabulary expansion.

## Metrics

Report validation and untouched holdout:
- UNIT sample accuracy;
- MARKET-SLOT sample accuracy;
- FARMER exact parity;
- HANDS exact parity;
- MARKET exact parity;
- complete-action parity;
- minimum source complete-action parity;
- complete parity by 120-turn stage;
- minimum stage complete parity;
- unseen truth-label counts by UNIT / MARKET-SLOT;
- model parameter count;
- training wall time.

## Frozen gates

### STRONG offline pass

All untouched holdout metrics:
- complete-action parity >= 0.90;
- MARKET >= 0.94;
- FARMER >= 0.99;
- HANDS >= 0.98;
- minimum source complete parity >= 0.80;
- minimum stage complete parity >= 0.80.

Decision:
`V29A_RECURRENT_STRUCTURAL_OFFLINE_STRONG_PASS`.

### CAUSAL-ELIGIBLE pass

If STRONG does not pass, V29A still advances to one closed-loop causal benchmark only if all:
- complete-action parity >= **0.80**;
- MARKET >= **0.88**;
- FARMER >= **0.97**;
- HANDS >= **0.90**;
- minimum source complete parity >= **0.70**;
- minimum stage complete parity >= **0.70**;
- no forbidden runtime feature;
- no teacher call at inference.

Decision:
`V29A_RECURRENT_STRUCTURAL_CAUSAL_ELIGIBLE`.

### Fail

Otherwise:
`V29A_RECURRENT_STRUCTURAL_DISTILLATION_FAIL`.

Mechanical invalidity:
`V29A_MECHANICS_INVALID`.

## Routing

STRONG or CAUSAL-ELIGIBLE:
- freeze epoch-8 weights, vocabularies, normalization, and architecture;
- implement a first-party inference runtime without teacher bytes;
- open exactly one V29B fresh closed-loop causal benchmark on unseen seeds/current immutable frontier;
- V29B must compare against ALL3 and report multi-source/multi-seed W/L, not imitation parity alone.

FAIL:
- no hidden-size sweep;
- no epoch sweep;
- no loss-weight sweep;
- no holdout-guided architecture change;
- close this final-week teacher-distillation family and return to final slot preservation.

No V29A result authorizes Kaggle mutation.
