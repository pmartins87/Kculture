# KEXP-20260827-037 — early terminal non-input liquidation

Status: **DEVELOPMENT PASS / EXPLORATORY DIRECT RUNNING / NOT HOSTED-ELIGIBLE YET**

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

This exactly meets the predeclared direct-score gate, but the edge is small. Seat behavior is asymmetric: candidate seat0 9-3-4 with mean delta -142.875; candidate seat1 4-8-4 with mean delta +209.875. That makes broader replication mandatory before treating the mechanism as a robust component.

## Current decision

**Development PASS only.** The candidate is not strong enough for validation or hosted submission on this evidence alone.

A fresh exploratory direct screen on the 20 live-meta environmental seeds × both seats has been launched via `kexp037-exploratory-direct`. If the direct edge does not replicate, close the branch. If it replicates cleanly, retain the mechanism only as a small independent component for later combination with a larger adaptive policy.

KEXP-039 provides observational context from recent top episodes; it does not determine promotion.

No validation or held-out seeds were accessed.
