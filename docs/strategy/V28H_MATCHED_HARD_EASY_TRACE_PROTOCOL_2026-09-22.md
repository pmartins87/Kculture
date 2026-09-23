# V28H — Matched Hard-vs-Easy Trajectory Trace Protocol — 2026-09-22

## Status

PRE-REGISTERED after V28G returned `V28G_SOURCE_CLUSTERED_HARD_CORE`.

No Kaggle mutation is authorized.

## Strategic question

At what phase does ALL3 begin to separate economically from its zero-loss behavior when facing the six source-clustered hard frontier policies, and what observable/action signatures precede that separation?

## Frozen evidence

Use only:
- V28F immutable snapshot from workflow `35807910104`, artifact `v28f-immutable-snapshot`;
- V28F aggregate artifact from the same workflow;
- V28G census artifact from workflow `35812527508`.

No Kaggle source reacquisition is allowed.

## Hard targets

Use exactly the deterministic `trace_targets` emitted by V28G.

V28G provides at most 12 targets spanning:
- closest residual losses;
- most severe residual losses;
- source-diversity preference.

Every hard-target rerun must reproduce the exact V28F ALL3 terminal score and margin. Otherwise mechanics fail.

## Matched easy controls

V28G identifies six sources with zero ALL3 losses in the 12-context V28F panel.

Sort those zero-loss sources by representative rank then SHA.

For hard target index i, choose control source:
`zero_loss_sources[i mod N]`.

Run the control at the **same seed and same seat** as the hard target.

Every control rerun must reproduce the exact V28F ALL3 terminal score and margin for that source/seed/seat.

This produces one matched control for every hard target without outcome-adaptive reselection.

## Frozen checkpoints

`0, 96, 192, 288, 384, 480, 576, 648, 696, 719`.

At each checkpoint report for ALL3:
- own money;
- opponent public money;
- money gap;
- own/opponent public farm composition:
  - hands;
  - unlocked quadrants;
  - COW, SHEEP, GOOSE;
  - WHEAT, CARROT, TOMATO, STRAWBERRY, MELON;
  - WEED;
- ALL3 own legal private shed and seeds.

Opponent private state is not used.

## Frozen action windows

`0–95, 96–191, 192–287, 288–383, 384–479, 480–575, 576–647, 648–695, 696–718`.

For ALL3 and opponent separately count:
- physical operation verbs;
- market verb/item quantities.

## ALL3 option events

Instrument exact ALL3 without changing its action:
- O-RW1 one-shot firing;
- O-TW1 one-shot firing;
- O-LQ2 turns where post-LQ2 action differs from the same pre-LQ2 action.

For each event record:
- step;
- event kinds;
- exact V47 action;
- exact ALL3 action;
- legal own money/public money gap;
- own legal private shed/seeds.

## Earliest separation selector

For every checkpoint compute the paired hard-minus-control difference in ALL3 money gap.

Select:
1. the earliest checkpoint where median paired difference <= -1000;
2. if none exists, the checkpoint with the most negative median paired difference;
3. ties by earlier checkpoint.

Let S be the selected checkpoint.

The explanatory action window is the latest frozen window whose end is < S. If S=0, use the first window.

## Explanatory differences

At S report:
- paired money-gap hard-control distribution;
- public farm composition hard-control differences;
- own legal private inventory hard-control differences.

In the explanatory action window report the largest absolute hard-control mean differences for:
- opponent public action allocation;
- ALL3 action allocation.

These are observational discovery signals only. Opponent identity/source/rank/SHA is forbidden as a runtime feature.

## Decisions

- `V28H_EARLY_STRUCTURAL_SEPARATION` if S <= 288;
- `V28H_MIDGAME_STRUCTURAL_SEPARATION` if 288 < S <= 576;
- `V28H_LATE_STRUCTURAL_SEPARATION` if S > 576;
- `V28H_MECHANICS_INVALID` on any replay parity failure, missing target/control, runtime failure, or snapshot hash mismatch.

## Routing

A mechanically valid V28H routes to legal-observation mechanism discovery around the selected checkpoint and its preceding action window.

No V28H result directly authorizes a policy edit or Kaggle submission.
