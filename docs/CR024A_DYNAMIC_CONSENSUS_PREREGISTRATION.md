# CR024A — preregistration: dynamic guard vs consensus backbone

Frozen before reading run `33323718867` final aggregate.

## Goal

Produce a **new, materially different** Kaggriculture strategy that preserves the large broad strength of CR023 top-lineage routes while repairing their unfavorable close-game flips. Re-submission of CR008/CR011/CR015 is not an experiment in this branch.

## Data firewall

Development may use only the already-open CR023 raw Stage-A seeds and exact frozen current-meta opponents. Raw Stage-B seeds remain untouched until one CR024A candidate is frozen. All 32 held-out seeds remain sealed.

Runtime identity, username, submission id, opponent id and seed are forbidden features.

## Branch A — dynamic public-state guard

Run `cr024a-dynamic-regime-stage-a` reapplies frozen CR008 and the frozen CR023 top19 tape to all 216 Stage-A conditions and records legal public-state features every 12 turns during the top19 trajectory.

A simple guard is freeze-eligible only if the aggregate finds a rule that:

- catches harmful conversions originating from at least 2 distinct Stage-A seeds;
- recall >= 0.60 on unfavorable W/L conversions;
- false-positive rate <= 0.10 on non-harmful conditions;
- precision >= 0.20;
- uses only legal public state and no identity/seed feature.

If eligible rules exist, choose the **earliest** checkpoint; ties are resolved by higher recall, lower FPR, then higher precision. Freeze that rule before Stage B.

The resulting CR024A_GUARD will follow the strong meta route outside the guard and retreat toward the frozen CR008 policy when the guard fires. The implementation must use only information available before the action it changes.

## Branch B — consensus/shrinkage backbone

If no simple dynamic guard satisfies the frozen criteria, do not invent a threshold and do not relax the gate post hoc.

Build CR024A_CONSENSUS from the three frozen public tapes top11/top16/top19:

1. at a turn where at least two tapes have exactly the same legal action, use that majority action;
2. at a turn with no exact majority, use frozen CR008 for that turn;
3. no identity/seed information;
4. no new opponent exploit overlay in CR024A.

This is a deterministic shrinkage rule: agreement among independent strong lineages earns deviation from CR008; disagreement shrinks back to the proven baseline.

## Stage-A candidate gate

Whichever branch is selected must first be evaluated on Stage A, both seats, against the exact current-meta panel. Report:

- W/L conversions vs CR008;
- mean relative economic delta;
- close-game subset;
- downside/CVaR;
- mechanical errors;
- intervention/fallback frequency.

A candidate is not frozen for Stage B if it has net unfavorable W/L conversions, material close-game degradation, or mechanical errors.

## Stage-B confirmation

Only one frozen CR024A candidate may open the raw Stage-B seeds. No threshold/action editing after looking at Stage-B outcomes. Stage B is confirmation, not tuning.

If CR024A passes, package it as a **new hosted strategy** and then construct CR024B by adding only the frozen CR008 high-confidence exploit overlay.

## Hosted policy

Kaggle slots are for new materially different strategies. This branch will not spend a slot on duplicate CR008/CR011/CR015 controls.
