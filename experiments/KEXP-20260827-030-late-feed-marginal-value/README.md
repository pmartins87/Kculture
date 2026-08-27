# KEXP-20260827-030 — late FEED marginal terminal-value audit

Status: **RUNNING / DIAGNOSTIC ONLY**

## Prize-first question

KEXP-027 showed that the ultra-narrow step-695 FEED suppression has zero ceiling because frozen R4B issues no FEED at step 695. That does not answer whether some FEED actions earlier in the final day (steps 672..695) spend scarce WHEAT without changing terminal animal output.

This experiment measures the exact marginal terminal-production value of every frozen-R4B FEED intent in that window.

## Mechanics basis

Under the frozen official engine:

- the end-of-day refresh after step 695 is the final animal-production refresh;
- an animal escapes at refresh when `consecutive_unfed` reaches 2;
- a surviving animal can produce its base unit on a scheduled production day even when unfed;
- FEED is required to consume an already-existing `pending_care_bonus` on a production day;
- CARE issued during the final day creates new pending bonus only after that day's production check and therefore cannot pay before terminal scoring;
- animal product capacity (`max_held`) can cap the incremental benefit.

Replay alignment is exact: observation/state frame `t` is paired with submitted action frame `t+1`.

## Frozen protocol

Run unchanged `R4B-market-only-validated-v1` against deterministic `starter` on:

- all 16 development seeds;
- all 20 exploratory live-meta environmental seeds.

For every FEED intent during steps 672..695, inspect the acting animal and actor inventory before the action. Compute whether FEED can add any terminal product units through the final refresh by:

1. preventing an escape that would otherwise occur before a due production;
2. unlocking an already-existing pending care bonus on a due production;
3. respecting current `yield_units` and `max_held` capacity.

A FEED with zero incremental terminal product is separately counted when the acting unit actually holds WHEAT, because only then would suppressing the FEED save a real scarce unit.

No action is changed by this experiment.

## Predeclared gate

A narrow state-aware late-FEED suppression candidate becomes eligible only if all are true:

- at least **4/16 development episodes** contain a zero-terminal-value FEED whose actor holds WHEAT;
- at least **5/20 exploratory-live-meta episodes** contain one;
- at least **20% of all valid FEED intents** in the combined pools have zero terminal-production value.

Passing only authorizes a controlled development candidate. It does not authorize validation or Kaggle submission.

If the gate fails, close FEED suppression as a small-ceiling branch and move late-game work toward broader harvest/drop/sale/labor planning.

No validation or held-out seeds are accessed.

Tool: `tools/audit_late_feed_marginal_value.py`
Frozen tool blob: `9aa2951b7aa315334d5201a5c10eaaa38c6c3292`
