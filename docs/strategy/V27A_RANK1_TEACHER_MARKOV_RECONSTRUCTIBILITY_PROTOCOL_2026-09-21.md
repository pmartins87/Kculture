# V27A — Rank-1 Teacher Markov Reconstructibility Audit — 2026-09-21

## Status

PRE-REGISTERED after V26B closed source-agnostic multi-teacher consensus and before any V27A outcome.

This is the first viability gate for a genuinely new learning architecture: first-party behavioral distillation of one strong public teacher.

It does not copy teacher source into a submission and does not authorize submission.

## Frozen teacher

Use exactly the rank-1 representative from the immutable V26A frontier snapshot:

- ref: `ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`;
- SHA: `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`.

Teacher selection is frozen by current public rank from V26A and was not chosen from V27 outcomes.

The teacher source is used only offline as a behavior oracle.

## Opponent population

Use all 12 exact V26A snapshot sources as opponents.

No source is dropped.

No live Kaggle reacquisition.

## Fresh seeds

`79701, 79702, 79703`.

Both seats.

Expected episodes:
`12 opponents × 3 seeds × 2 seats = 72`.

## Frozen checkpoints

Compare teacher history-state behavior at:

`[0,1,2,3,4,8,16,32,64,128,256,384,512,640,718]`.

At each checkpoint candidate call:

1. compute the action from the normal **ongoing teacher instance**, which has seen the whole episode history;
2. instantiate a **fresh teacher instance** from the same immutable source bytes;
3. give that fresh instance exactly the same current legal observation/configuration;
4. compare canonical complete actions.

The ongoing action remains the action executed in the episode.

Expected comparisons:
`72 × 15 = 1080`.

## Metrics

Report exact parity for:
- complete action;
- market component;
- farmer component;
- complete hands component.

Also report:
- parity by opponent source;
- parity by checkpoint;
- parity by seed;
- action-key disagreement counts.

## Mechanical validity

Require:
- 72/72 episodes DONE/DONE, 720 steps, finite rewards;
- 1080/1080 checkpoint comparisons;
- exact teacher/opponent snapshot SHAs;
- no live Kaggle source reacquisition;
- no source or checkpoint missing.

Any failure:
`V27A_MECHANICS_INVALID`.

## Frozen decisions

### V27A_MARKOV_DISTILLATION_VIABLE

All must hold:
- complete-action parity >= **0.95** overall;
- market parity >= **0.98**;
- farmer parity >= **0.98**;
- hands parity >= **0.98**;
- every opponent source complete-action parity >= **0.90**;
- every checkpoint complete-action parity >= **0.85**.

Route:
- V27B trains state-only behavioral cloning from legal player state;
- teacher source is offline labels only;
- train/validation/test split is by fresh seed and opponent source;
- no opponent identity runtime feature.

### V27A_HISTORY_AWARE_DISTILLATION_REQUIRED

Mechanical PASS, complete-action parity >= **0.70**, but Markov gate fails.

Route:
- state-only imitation is closed;
- V27B may use one fixed explicit history representation consisting only of legal past observations/actions;
- no teacher hidden state or source identity;
- no post-hoc history-window sweep.

### V27A_TEACHER_TOO_STATEFUL_FOR_FAST_DISTILLATION

Mechanical PASS, complete-action parity < **0.70**.

Route:
- do not spend remaining competition time on behavioral cloning of this teacher;
- close fast teacher distillation;
- move to final competition-slot strategy + publication/research preservation.

## Anti-overfit restrictions

- no changing teacher after outcome;
- no dropping difficult opponents;
- no changing checkpoints;
- no source-conditioned parity gate;
- no runtime source/rank/SHA identity;
- no embedding the teacher source in a derived candidate under V27.

## Competition timing

The final Kaggriculture submission deadline is September 30, 2026 at 23:59 UTC.

V27 is therefore a fast viability branch: only a strong reconstructibility result justifies spending the remaining time on learned policy distillation.

No V27A result directly authorizes Kaggle submission.
