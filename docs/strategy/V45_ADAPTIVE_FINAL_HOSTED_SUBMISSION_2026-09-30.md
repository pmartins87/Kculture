# V45 — Adaptive Counterfactual Meta Controller — Final Hosted Submission — 2026-09-30

## Final adaptive hypothesis

V45 is the first late-stage adaptive candidate whose training features, arm outcomes, and packaged runtime all inhabit the same V30B counterfactual trajectory.

It preserves the exact V30B physical/strategic chassis. At step 216, after V30B has acted, it observes only public game state and chooses among ADV sale lookaheads 0/4/8/12 through a shallow decision tree. The selected ADV mechanism advances already-planned future SELL actions; it does not replace the physical policy.

## Why V43 was rejected

V43 had appeared to pass statistically, but its rich features for V47/V37C contexts were taken from the original hosted agent trajectory rather than the counterfactual V30B trajectory. Small state differences crossed decision-tree thresholds. Exact-package validation exposed this and V43 was never submitted.

## V45 counterfactual feature corpus

Workflow run: `36779746548`.

- 75 contexts total;
- 25 newest V30B final contexts;
- 25 newest V47 final contexts;
- 25 newest V37C contexts;
- 122 public-state features captured from the exact V30B counterfactual at step 216;
- V30B step-216 parity: **25/25**.

Decision: `V45_COUNTERFACTUAL_FEATURE_CORPUS_PASS`.

## Statistical gate

Workflow run: `36780002763`.

Training: 60 older contexts.
Temporal holdout: 15 newest contexts, 5 per source family.

Results:
- training baseline: 37.5 points;
- training V45: 45.0 points;
- training score-rate delta: **+12.5 percentage points**;
- holdout baseline: 10.0 / 15;
- holdout V45: 11.0 / 15;
- holdout score-rate delta: **+6.67 percentage points**;
- loss-to-win flips: 1;
- win-to-loss flips: 0;
- holdout mean-margin delta: **+112.33**;
- V30B replay parity: **25/25**.

Decision: `V45_CF_RICH_TREE_GATE_PASS`.

## Exact packaged-agent gate

Validation run: `36780286556`.

All five shards passed. The final package reproduced the expected outcomes on **15/15 untouched holdout games exactly**.

Binding package SHA-256:

`163c2db397f3e4a44bdad0b72b535d841c3771a44a2f2096bc844d741dc40b99`

Decision:
`V45_EXACT_15_OF_15_PASS`.

The aggregate job in that run failed only after printing the binding PASS because its small output-writing script omitted `import os`. This did not affect any validation shard or package bytes. The exact gate was rebound from the five successful shard artifacts in the submission workflow.

## Authorized hosted submission

Submission workflow: `36780686155` — SUCCESS.

Binding preflight immediately before submission:
- newest active ID: V30B `56693642`;
- second active ID: V47 `56693641`;
- quota available: 3;
- package SHA matched exactly;
- exact holdout gate rebound at 15/15.

Submitted:
- ID: **`56719341`**
- description: `PS_V45_ADAPTIVE_CF_META_FINAL`
- initial status: `PENDING`
- archive SHA: `163c2db397f3e4a44bdad0b72b535d841c3771a44a2f2096bc844d741dc40b99`

Post-registration latest-two:
1. V45 adaptive `56719341`
2. V30B exact `56693642`

V47 `56693641` was displaced as the unavoidable consequence of the user's authorization for at most one new submission.

Quota after submission: 2 remaining, intentionally unused.

## Binding state

The single adaptive-submission authorization has been consumed.

**KCULTURE_FINAL_PAIR_V45_ADAPTIVE_PLUS_V30B — NO FURTHER SUBMISSIONS WITHOUT NEW EXPLICIT AUTHORIZATION**

Only read-only monitoring is authorized from this point.
