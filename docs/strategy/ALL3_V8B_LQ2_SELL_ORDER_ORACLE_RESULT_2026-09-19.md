# ALL3 V8B LQ2 SELL-Order Pairwise Transposition Oracle — Result — 2026-09-19

## Binding execution

Workflow:
**`35479783995`**.

Mechanical:
- PASS;
- 4 frozen hard contexts;
- 8 frozen target states;
- zero failures.

## Verdict

**`V8B_ORDER_HEADROOM_NARROW`**

Aggregate:
- hard-context loss->win flips: **1 / 4**;
- mean best-branch margin delta: **+96**.

Per context:

1. V47 mirror 75113/seat1:
   - -263 -> -251;
   - +12;
   - best: step 577, swap WOOL 1 with FERTILIZER 9;
   - still LOSS.

2. V48 75103/seat1:
   - **-86 -> +10**;
   - +96;
   - step 600;
   - swap FERTILIZER 11 with WOOL 7;
   - **LOSS -> WIN**.

3. V48 75110/seat0:
   - -484 -> -220;
   - +264;
   - step 600;
   - swap WOOL 7 with MILK 16;
   - still LOSS.

4. V48 75113/seat1:
   - -794 -> -782;
   - +12;
   - best: step 577, swap WOOL 1 with FERTILIZER 9;
   - still LOSS.

## Mechanistic pattern

The two strongest V48 results at step 600 are consistent with the local ordering:

**MILK before WOOL before FERTILIZER**.

- context 1 already had MILK first; moving WOOL before FERTILIZER caused the win;
- context 2 already had FERTILIZER after WOOL; moving MILK before WOOL produced +264.

This suggests a conservative first-party rule:

within each post-LQ2 consecutive SELL run, consider only positions occupied by
MILK / WOOL / FERTILIZER; stable-sort those selected orders by:

`MILK -> WOOL -> FERTILIZER`

while:
- keeping all non-target SELL products in their original slots;
- preserving all quantities;
- preserving all non-SELL market slots;
- preserving farmer/hands.

This candidate is named **O-LQ3**.

## Required next step

Because V8B headroom is narrow, do not promote O-LQ3 directly.

Stage A:
- replay O-LQ3 vs ALL3 on the exact four frozen hard contexts.

Only if Stage A preserves the observed direction without W/L regression:
Stage B:
- fresh targeted paired confirmation on untouched seeds against V48 plus unrelated controls.

No opponent identity is permitted in O-LQ3.
No Kaggle submission is authorized by V8B.
