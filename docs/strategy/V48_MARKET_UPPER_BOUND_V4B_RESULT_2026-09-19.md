# V4B Long-Horizon V48 Market Upper Bound — Result — 2026-09-19

## Binding run

Workflow: **`35448761774`**  
Head: `3f6ea5aa2af734493a2b2abc9643694333a70987`  
Artifact: `10585808415`  
Artifact digest: `sha256:518aaa487d53926212f8cb924e89e3d41fdd17a8ade0b10ffab3bc1206fbf4ff`.

Mechanical PASS:
- 12 fresh contexts;
- zero failures;
- exact V47 farmer/hands retained;
- **zero physical fallback turns**.

## Strategic result

Every BASE context lost:
- BASE score rate: **0.0**.

Every long-horizon market-substitution context tied:
- upper-bound score rate: **0.5**;
- paired score delta: **+0.5**;
- mean margin delta: **+585.67**;
- mean V48-market substitutions: **50.17 turns**;
- mean physical fallback turns: **0**.

Per seed, both seats agreed:
- 74101: loss -> tie, +324 margin;
- 74102: loss -> tie, +303;
- 74103: loss -> tie, +1,930;
- 74104: loss -> tie, +172;
- 74105: loss -> tie, +286;
- 74106: loss -> tie, +499.

First substituted market step was 253 in five seeds and 196 in seed 74103.

## Decision-label correction

The runner emitted **`V48_V4B_LONG_HORIZON_MARGIN_ONLY`** because its first branch required
`nonwin_to_win_flips >= 2`, and its flip counter intentionally counted only transitions all the
way to score 1.0.

That label is too narrow for the post-V4B protocol: **loss -> tie is a genuine W/L score
improvement**. The measured score rate increased from 0.0 to 0.5 in all 12 contexts.

Binding interpretation:
**`V48_V4B_LOSS_TO_TIE_WL_HEADROOM`**.

This is not a retroactive threshold change. The pre-frozen post-V4B branch protocol says to enter
temporal localization whenever V4B shows W/L headroom, and the paired score delta is unambiguously
positive.

## Interpretation

The V47→V48 advantage can be recovered partially by cumulative market behavior while keeping the
entire V47 physical policy unchanged.

Because physical fallback count is exactly zero:
- do **not** activate V4C;
- do **not** open physical/macro search;
- the next task is temporal localization of the cumulative market effect.

The result does **not** authorize copying V48 wholesale or using V48 at runtime.

## Next gate

Apply the already frozen post-V4B localization protocol on the same discovery seeds:
- W0 0–215
- W1 216–335
- W2 336–431
- W3 432–527
- W4 528–623
- W5 624–718
- cumulative suffixes W5, W4+, W3+, W2+, W1+

Find the smallest predeclared interval/suffix that reproduces the loss->tie improvement, then inspect
recurring market transformations inside that interval and rewrite them first-party.

No Kaggle submission is authorized by V4B.
