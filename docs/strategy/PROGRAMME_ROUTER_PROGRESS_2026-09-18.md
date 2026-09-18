# Programme router progress — 2026-09-18

## Outcome and next decision

The standalone exact-prefix router is now CLOSED as a competitive candidate.

Binding adaptive-expert gate: workflow `35307879368`, 64 paired matchups / 128 complete
episodes, official engine 1.32.7. Against the exact current public V47 and V39 adaptive
agents, W/L stayed `5/64 -> 5/64` (delta zero). The router did improve paired terminal
margin by `+2770.47` on average, including about +2.8k in both expert blocks, but V47
remained `0/32` for both treatments.

Binding verdict:
`CLOSE_STANDALONE_ROUTER_OPEN_BOUNDED_TRANSACTION_MARKET_SEARCH`.

Do not tune tree depth, checkpoints, seeds or programme membership to rescue this
candidate. The result says route continuation choice carries economic information but the
missing competitive control surface is the adaptive wrapper itself: transaction guards,
market timing/order, funding/storage repair and bounded visible-state transforms.

Next bounded work is an **oracle-headroom gate** on a complete strong adaptive backbone.
At matched public states, permit only one small transaction/market intervention, evaluate
the candidate set counterfactually in the exact engine, and ask whether the oracle can
actually convert losses to wins rather than merely increase terminal money. Only then
train an observation-only selector/value model.

Result:
`docs/strategy/PROGRAMME_ADAPTIVE_EXPERT_GATE_RESULT_2026-09-18.md`.
Summary:
`data/programme_teacher/2026-09-18/ADAPTIVE_EXPERT_GATE_SUMMARY.json`.

## Completed parity
16 complete games, eight representative programmes, both seats, eight checkpoints:
128 feature vectors / 14,592 scalar values exactly matched between native kagprog and
an independent feature extractor from pinned kagsim observations. Final margins matched
raw-action execution. This does NOT independently repeat official hosted parity.
New runtime modules use only observation and own private inventory, not simulator state.

## Family holdout
Leave one route-bank block out of training, with disjoint train/test seeds; no tree-depth
sweep. Additional smaller lineages are conservatively pooled into one block.
The same 51 decision groups are averaged; these are correlated groups, not independent
trials. The corpus does not prove unrelated ancestry across all route banks.

| Held-out block | Opponents | Static W/L | Tree W/L |
|---|---:|---:|---:|
| Modern | 38 | 0.38269694 | 0.39035088 |
| Legacy | 13 | 0.79386626 | 0.81561086 |
| Additional | 10 | 0.86797386 | 0.87500000 |

All three average deltas are positive. This supports implementing the router, not claiming
statistical significance, robustness against all opponents, or Kaggle rating.

## First complete router
Selected group 0, checkpoint 144, static programme 15 by highest TRAIN-only best-static
utility, breaking ties toward earlier checkpoints. No holdout result selected the group.
Only one decision is made per episode; all candidate prefixes are checked for equality.
Frozen depth-4 tree from the original training run.
64 full games: eight representative static opponents × two fresh seeds 53001/53002 ×
both seats × router/control. Decision executed once per enabled episode.
Both treatments scored 0.9375 W/L. This small, static-opponent panel is neutral and is
not sufficient for promotion. No parameter tuning or training scale-up performed.

## Published checkpoint
Authorized local commit eeb49883f0feadf3b0b1e7df0e980d1c80d90203 was published through
the authenticated connector as 947b5a92d94dc15d9d9615ef3f3d8a61958b9c28.
Both have exact tree edefa724acf6abb5eb36f631b2b7ebf0220b620c. Terminal Git lacked
credentials; commit metadata differ, file content does not.

## Evidence
`data/programme_teacher/2026-09-18/OBSERVATION_PARITY.json`
`data/programme_teacher/2026-09-18/FAMILY_HOLDOUT.json`
`data/programme_teacher/2026-09-18/ROUTER_EPISODE_GATE.json`
Implementation: solver/programme_features.py, programme_actions.py, programme_router.py.
Reproducible drivers: tools/programme_observation_parity.py,
programme_family_holdout.py, programme_router_episode_gate.py.
