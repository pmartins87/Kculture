# KEXP-20260827-037 — early terminal non-input liquidation

Status: **EXPLORATORY PASS / RETAIN AS SMALL COMPONENT / NOT HOSTED-ELIGIBLE ALONE**

## Prize-first mechanism

At the default town intervals, step **716** is the final town-consumption tick before terminal scoring. Neither executable step 717 nor 718 has another town tick.

For `CARROT`, `TOMATO`, `STRAWBERRY`, `MELON`, `EGG`, `MILK`, and `WOOL`, market inventory cannot decrease between 717 and 718 through town demand or BUY_PRODUCT. Their price can therefore only remain unchanged or fall from player sales. Selling already-available projected shed stock one step earlier weakly front-runs a later terminal dump.

WHEAT and FERTILIZER are intentionally excluded because they remain usable/buyable inputs.

## Candidate

`candidates/r4d_early_terminal_noninput_sell.py`, blob `222e9c1de9bab043780af4a1f10bf8cd2f0c210f`.

Frozen R4B is unchanged except at executable state 717, where eligible projected shed stock is sold using otherwise-free market slots. Step 718 remains normal R4B.

Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Development result

GitHub Actions run **33043310488 — SUCCESS**.  
Artifact **9635102382**, ZIP digest **SHA-256 `133e347dc355844b3611cc17f611e4e33139623262e67db919c39a36411639b5`**.

Modern public panel:

- Kaito 25-7;
- Rayk 30-2;
- Andrew 26-6;
- combined **81-15**, exactly preserving R4B;
- zero errors.

Direct candidate vs R4B:

- **13-11-8**;
- score rate **0.53125**;
- mean terminal delta **+33.5**;
- zero errors.

## Exploratory replication

A fresh direct screen used the 20 exploratory live-meta environmental seeds × both seats (40 games), with fresh agent loads per game.

GitHub Actions run **33045020546 — SUCCESS**.  
Artifact **9635467165**, ZIP digest **SHA-256 `b8322cd6f966e80291d65a52782e570c0eabf8585e3cf5d38cd0b0d341dce3a4`**.

Result vs frozen R4B:

- **12-8-20**;
- score rate **0.55000**;
- mean terminal delta **+32.2**;
- zero errors.

Seat split remains asymmetric:

- candidate seat0: 8-2-10;
- candidate seat1: 4-6-10.

The edge therefore replicated in direction and magnitude across an independent environmental pool, but remains small and seat-sensitive.

## Decision

**Retain as a small independent component.** KEXP-037 has now passed both development and exploratory direct replication, while preserving the strong public panel. Its effect is too small to justify validation or a hosted Kaggle submission alone.

The intended use is combination with a materially stronger state-adaptive policy after that policy independently passes. Combination must then be re-screened because market interaction is not guaranteed additive.

KEXP-039 independently found that 717 liquidation is common in recent top trajectories, but is not itself a winner signature.

No validation or held-out seeds were accessed.
