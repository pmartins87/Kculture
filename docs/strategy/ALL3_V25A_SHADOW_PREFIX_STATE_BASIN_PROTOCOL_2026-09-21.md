# ALL3 V25A — Shadow Prefix State-Basin Horizon Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED before the outcome of V24B identifiability audit workflow `35645479016`.

Activate only if V24B returns `V24B_NOT_DISTILLABLE_COMPACTLY`.

This is an architecture-level state-basin diagnostic. It is not threshold tuning and it does not reopen compact <=2-turn controller search.

## Motivation

Binding V23B established:
- MARKET_ONLY fails the multi-seed gate;
- PHYSICAL_ONLY has 0 score improvements;
- FULL_SHADOW improves 81/93 hard contexts across all hard seeds.

V24A found an early recurrent `M_TO_P|hands|2` sequence, but V24B may show that its teacher actions are not identity-free distillable.

V25A therefore asks a different question:

**How many consecutive FULL_SHADOW turns are required before returning to exact ALL3 can preserve W/L headroom?**

If a finite prefix works, the teacher may be moving the episode into a better state basin. If only persistent FULL_SHADOW works, the gap is policy-wide rather than an opening macro.

## Binding inputs

Use only immutable artifacts:
- V23A snapshot workflow `35627972979`;
- snapshot artifact ID `10655240502`;
- V23 hard config / cluster map from the same workflow;
- V23B binding aggregate workflow `35632311093`, artifact ID `10656170070`.

No live Kaggle source reacquisition.

Population:
- all **93** V23 hard contexts.

Opponent:
- exact frozen source from the immutable snapshot, same as V23B.

## Candidate semantics

At every candidate turn:
1. compute exact V47 action;
2. compute exact ALL3 action, advancing the ALL3 host state exactly once;
3. compute exact frozen shadow-teacher action.

For prefix horizon `H`:
- turns `t < H`: return complete shadow action;
- turns `t >= H`: return exact ALL3 action.

This preserves ALL3 internal host-state evolution throughout the prefix while changing the externally executed trajectory.

## Frozen horizons

Exactly:

`H = [0, 4, 8, 16, 32, 64, 128, 256, 720]`

Interpretation:
- H=0 = exact ALL3 BASE;
- H=720 = FULL_SHADOW ceiling.

No additional horizon may be inserted after outcomes are seen.

## Mechanical invariants

For every context:
- H=0 score and margin must exactly reproduce binding V23B BASE;
- H=720 score and margin must exactly reproduce binding V23B FULL_SHADOW;
- exact source SHA must match snapshot manifest;
- episode status DONE/DONE, 720 steps, finite rewards;
- all 93 contexts × 9 horizons must complete.

Any violation => `V25A_MECHANICS_INVALID`.

## Headroom gate for finite horizons

For each finite H in [4,8,16,32,64,128,256], compare against H=0.

H passes iff:
- improved-score contexts >=4;
- improved source SHAs >=2;
- improved functional clusters >=2;
- improved seeds >=2;
- mean score delta >0;
- regressed-score contexts <= improved-score contexts / 2.

This gate is frozen before execution.

## Frozen selector

If one or more finite horizons pass:
- select the **smallest H** that passes.

No ranking by margin or score after minimum passing horizon is found.

## Decisions

### `V25A_EARLY_STATE_BASIN_HEADROOM`
- selected minimum H is 4, 8, 16, or 32.

Interpretation:
- an early trajectory prefix is sufficient to enter a better basin;
- V25B may attempt one identity-free opening/basin policy distilled over that horizon.

### `V25A_LONG_STATE_BASIN_HEADROOM`
- selected minimum H is 64, 128, or 256.

Interpretation:
- benefit requires sustained trajectory control;
- V25B must distill a longer-horizon first-party policy, not a compact option.

### `V25A_PERSISTENT_POLICY_REQUIRED`
- no finite H <=256 passes;
- H=720 binding ceiling passes/reproduces V23B.

Interpretation:
- the advantage is policy-wide;
- stop additive option mining around ALL3;
- move to materially different first-party base architecture.

### `V25A_NO_REPRODUCIBLE_SHADOW_HEADROOM`
- H=720 fails to reproduce binding V23B headroom despite mechanical validity.

This would indicate a semantic implementation mismatch and blocks strategy work.

### `V25A_MECHANICS_INVALID`
- any mechanical invariant fails.

## Restrictions

- source identity may be used only offline to choose the exact frozen teacher/opponent bytes;
- source identity is forbidden in any later runtime candidate;
- no per-source horizon selection;
- no per-seed horizon selection;
- no additional horizons;
- no Kaggle submission.

## Next-stage rule

If V25A selects a finite horizon:
- freeze exactly that H;
- V25B distills at most one identity-free state-basin policy using legal runtime state;
- untouched fresh causal validation is mandatory.

If V25A returns persistent-policy-required:
- close the ALL3 additive-option architecture;
- benchmark a materially different first-party base architecture.
