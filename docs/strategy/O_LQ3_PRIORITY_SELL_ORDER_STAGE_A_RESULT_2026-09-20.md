# O-LQ3 Priority SELL Ordering — Stage A Result — 2026-09-20

Workflow: **35480144515**

Binding decision: **O_LQ3_STAGE_A_FAIL**.

Mechanical status: PASS, failures 0.

Four frozen hard-context replays:
- V47 mirror 75113/seat1: -263 -> -374, delta -111;
- V48 75103/seat1: -86 -> -2366, delta -2280;
- V48 75110/seat0: -484 -> -3187, delta -2703;
- V48 75113/seat1: -794 -> -917, delta -123.

Aggregate:
- loss->win flips: 0;
- mean margin delta: **-1304.25**.

Interpretation:

The V8B local direction `MILK -> WOOL -> FERTILIZER` is not a globally safe priority. Applying it at every eligible post-LQ2 SELL run compounds into large losses. O-LQ3 is therefore closed as an always-on rule; it will not be rescued by threshold or frequency retuning after seeing this result.

The remaining admissible question is causal/state conditionality, handled by V8C one-shot branch attribution.
