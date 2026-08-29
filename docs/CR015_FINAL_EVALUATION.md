# CR-015 final preregistered evaluation

Date closed: 2026-08-29

Candidate: `candidates/cr015_liquidation_phase_early_order.py`
Frozen candidate blob: `fabd4bc398e7eadcfd1d44add4d0e593315140e8`
Controls: frozen R4B and CR-011
Held-out: 32/32 remains sealed.

## Frozen protocol

Stage A and Stage B each used 12 preregistered fresh seeds, the same 9 exact frozen current-meta opponents and both seats. The candidate was unchanged between stages. The preregistration rejects money/margin gains that introduce net unfavorable W/L conversions; it does not require Stage B in isolation to create a new favorable conversion after Stage A has already supported the direction.

## Stage A

Run: `33143092984`
Aggregate job: `98760935541`
Artifact: `cr015-stage-a-final` / `9675060531`
Pairs: 216/216; errors: 0.

CR-015 vs R4B, broad:
- mean relative gain: +133.1064814814815
- mean self gain: +23.046296296296298
- mean score gain: +0.009259259259259259
- favorable outcome changes: 2
- unfavorable outcome changes: 0
- unchanged outcomes: 214

CR-015 vs R4B, closest 40 selected only by absolute frozen R4B delta:
- mean relative gain: +72.5
- mean self gain: +3.05
- mean score gain: +0.05
- favorable outcome changes: 2
- unfavorable outcome changes: 0

Frozen Stage-A gate: `supported=true`.

CR-015 vs CR-011, broad:
- mean relative gain: -0.7314814814814815
- outcome changes: 0 favorable / 0 unfavorable.

## Stage B

Run: `33168567052`
Aggregate job: `98843000396`
Artifact: `cr015-stage-b-final` / `9685019585`
Pairs: 216/216; errors: 0.

CR-015 vs R4B, broad:
- mean relative gain: +166.12962962962962
- mean self gain: +37.379629629629626
- mean score gain: 0.0
- favorable outcome changes: 0
- unfavorable outcome changes: 0
- unchanged outcomes: 216

CR-015 vs R4B, closest 40:
- mean relative gain: +18.75
- mean self gain: -10.325
- outcome changes: 0 favorable / 0 unfavorable.

CR-015 vs CR-011, broad:
- mean relative gain: -1.3148148148148149
- outcome changes: 0 favorable / 0 unfavorable.

## Combined A+B interpretation

Because each stage has 216 pairs, the broad combined CR-015 vs R4B mean relative gain is:

`(+133.1064814814815 + +166.12962962962962) / 2 = +149.61805555555554`

Across all 432 fresh pairs:
- favorable outcome changes vs R4B: 2
- unfavorable outcome changes vs R4B: 0
- unchanged: 430
- approximate combined mean self gain: +30.212962962962962
- combined mean score gain: +0.004629629629629629
- errors: 0

Against CR-011, CR-015 is essentially outcome-equivalent on these fresh stages but gives up about 1.02315 relative-money units per game on average. The reason to retain CR-015 is therefore not superior margin versus CR-011; it is the identity-free queue-placement safeguard motivated by the earlier causal diagnostics, while retaining positive fresh evidence versus R4B and no observed W/L harm.

## Verdict

**VALIDATED RESEARCH CANDIDATE / HOSTED CALIBRATION ELIGIBLE.**

Under the preregistered policy, CR-015 is not rejected: it improved broad relative money versus R4B in both fresh stages and produced no unfavorable W/L conversions, while Stage A supplied two favorable conversions. Stage B's zero new conversions do not retroactively invalidate Stage A because no such requirement was frozen.

This verdict does **not** establish that CR-015 dominates CR-011. Hosted calibration and future lineage-diverse evaluation remain useful. Do not alter this historical verdict by adding post-hoc gates.
