# CR-014 — Identity-free opponent-conditioned response gate

Status: **RUNNING / DIAGNOSTIC ONLY**

CR-011 proved that high-confidence opponent-aware STRAWBERRY response can improve terminal money/relative margin when placed early in the shared market sequence. CR-013 then showed that enabling the same response globally is harmful in some close-match families. CR-014 asks whether public state can distinguish those contexts without using opponent identity.

## Frozen design

- Base: frozen R4B.
- Alternative response: frozen CR-011.
- 12 fresh exploratory seeds from `configs/cr014_response_gate_seeds_v1.json`.
- Nine current public opponent packages.
- Both seats.
- No validation or held-out access.
- First actual CR-011 adaptive sale defines the decision context.
- Features are public game state/history plus trigger mechanics only. Opponent name/path/ID is never a model feature.
- Model: `DecisionTreeClassifier(max_depth=3, min_samples_leaf=8, class_weight='balanced', random_state=2026082714)`.
- Response enabled only when predicted probability of positive terminal relative effect is >= 0.70.
- Evaluation: leave-one-opponent-family-out (train on eight, test on the ninth), so the held-out family is never seen by the gate that decides its episodes.

## Frozen gate

`IDENTITY_FREE_RESPONSE_GATE_SUPPORTED` requires all:

- zero simulation errors;
- at least 6 evaluable held-out opponent families;
- at least 15 enabled episodes;
- mean own-money gain vs R4B > 0;
- mean relative-delta gain vs R4B > 0;
- mean W/L score gain vs R4B >= 0;
- suppress at least 60% of CR-011 episodes whose terminal relative effect is negative;
- retain at least 30% of CR-011 episodes whose terminal relative effect is positive;
- no opponent family W/L score-rate regression worse than 0.08;
- favorable outcome changes >= unfavorable outcome changes.

PASS authorizes one bounded deployable episode-latched response-gate candidate on **new exploratory seeds**. It does not authorize held-out use or automatic promotion. Under the revised hosted-information policy, a mechanically valid materially distinct candidate may later receive a hosted calibration submission if the ladder result would resolve a specific uncertainty.
