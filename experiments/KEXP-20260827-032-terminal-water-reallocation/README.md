# KEXP-20260827-032 — terminal WATER reallocation

Status: **COMPLETE / REJECTED / MECHANICS PREMISE CORRECTED**

## Original hypothesis

The experiment assumed that because there is no daily refresh after step 695, WATER during states 696..718 could not add terminal crop value.

That assumption was **wrong for one-time crops**.

In the frozen official engine, WATER on a one-time crop applies its bonus **immediately when the WATER action executes** if the crop is inside its watering bonus window. It increments `yield_units` directly, capped by crop max yield. Therefore a final-day WATER can still create product that is later HARVESTed, DROPed and SOLD before terminal scoring.

This distinction does not depend on a day refresh.

## Candidate tested

`candidates/r4d_terminal_water_harvest.py`

Frozen R4B was unchanged except that its WATER actions during 696..718 were replaced by HARVEST when already standing on positive yield, DROP in a narrow shed case, or PASS otherwise.

Candidate blob: `a34f7d137b6a06b45714bc7f79bb8c3995c835d0`.  
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Canonical result

Actions run **`33041733810` — SUCCESS**.  
Artifact **`9634478348`**.  
Artifact ZIP digest **SHA-256 `fae17f93588f092df3b70784e5fd14a89f95bfe9b53736a2e3d493077de1dab8`**.

All runs had zero runtime/status errors.

Modern development panel:

- Kaito V27: **25-7-0**, mean terminal delta +3,988.34;
- Rayk V11: **30-2-0**, mean terminal delta +7,076.72;
- Andrew V12: **24-8-0**, mean terminal delta +4,891.00;
- combined: **79-17-0** versus frozen R4B reference **81-15-0**.

Direct candidate vs frozen R4B, 16 development seeds × both seats:

- **1-31-0**;
- score rate **0.03125**;
- mean terminal delta **-441.375**.

The candidate fails every meaningful promotion criterion. The almost systematic direct loss is strong empirical evidence that the supposedly wasteful WATER actions often carry real terminal value.

## Decision

**Reject KEXP-032 completely. Do not suppress final-day WATER by step alone.**

The correct next question is state-specific marginal value:

1. does this WATER immediately increase `yield_units` on the current crop?
2. if yes, is the extra unit actually harvested before terminal?
3. can it reach shed/market and be sold before scoring?
4. if no to all value paths, only then is the WATER reclaimable.

This failure also invalidates the blanket WATER premise used when KEXP-033 was launched. KEXP-033's result may still be diagnostically informative, but it cannot be promoted without re-auditing the WATER decisions against the corrected mechanic.

No validation or held-out seeds were accessed.
