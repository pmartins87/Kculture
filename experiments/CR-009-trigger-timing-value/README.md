# CR-009 — antecipatory sale timing/value audit

Status: **FROZEN / RUNNING — DIAGNOSTIC ONLY**

## Question

CR-007 predicts high-confidence opponent sales somewhere in the next 24 turns. CR-008 showed that responding with an immediate full-stock sale reduces own terminal reward on a paired contemporary Kaggriculture field. Is the failure explained by acting too early?

## Frozen inputs

- final forecast training dates: 2026-08-23..25;
- strict out-of-time diagnostic date: 2026-08-26;
- top 20 official complete Kaggriculture episodes;
- frozen thresholds: CARROT 0.90, STRAWBERRY 0.85;
- no player-name/team/submission features;
- tool: `tools/cr009_trigger_timing_value_audit.py`, blob `af6a6195be14a0d19d524f3e9c161f7148da79d5`.

No CR-007 threshold is selected or modified in this experiment.

## Measurement

For every stock-eligible high-confidence trigger, locate the first actual opponent sale of that product within the frozen 24-turn horizon, measure the delay, and hold the current own shed quantity fixed while calculating official Kaggriculture sale revenue at every observed market state from the trigger through the last pre-sale state.

The audit compares immediate simulated revenue with the best observed pre-sale revenue and the last pre-sale revenue, retaining separate CARROT and STRAWBERRY summaries.

This is a timing diagnostic, not a full counterfactual: an actual own sale would itself change the simulated market inventory.

## Predeclared classification

`TIMING_MISMATCH_SUPPORTED` requires all:

- at least 40 high-confidence true-positive stock-eligible events;
- median first-opponent-sale delay at least 4 turns;
- positive mean best pre-sale wait gain versus immediate sale;
- at least 30% of true positives have at least 10 in-game dollars more revenue available at some pre-sale state than at the trigger state.

If this passes, the next adaptive architecture must predict **when** to sell rather than selling immediately on a 24-turn event forecast. If it fails, prioritize simulated market-impact and stock opportunity-cost attribution instead.

This experiment does not authorize a hosted submission or a new candidate by itself.
