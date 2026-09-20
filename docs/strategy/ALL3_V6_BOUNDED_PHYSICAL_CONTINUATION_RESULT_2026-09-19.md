# ALL3 V6 Bounded Physical Continuation — Result — 2026-09-19

## Binding execution

Lifecycle-corrected binding workflow:
**`35473780009`**.

The earlier run `35473389439` is NON-BINDING. It treated H2/H3 continuations on a hired hand
crossing an end-of-day boundary as global mechanical failures. Kaggriculture removes hired hands
at end of day, so those continuations are structurally ineligible rather than failed rollouts.

Mechanical amendment:
- farmer continuations may cross a day boundary;
- `hand:i` continuations are skipped before rollout if H2/H3 crosses the end-of-day boundary;
- no outcome information is used by this eligibility rule.

## Binding verdict

**`V6_CONTINUATION_MARGIN_ONLY`**

Mechanical:
- PASS;
- failures: 0;
- active hard contexts: 4.

Strategic:
- nonwin->win flips: **0**;
- flip families: none;
- mean oracle margin delta: **+68.5**.

Hard-context oracle outcomes:

1. V47 mirror, seed 75113, seat 1:
   - ALL3 base: -263;
   - best bounded continuation: -96;
   - delta: +167;
   - H2, hand:9, Conditional Memory shadow;
   - step 489: CARE -> NORTH;
   - step 490: COLLECT_FERTILIZER -> WATER;
   - still LOSS.

2. V48, seed 75103, seat 1:
   - ALL3 base: -86;
   - best: -76;
   - delta: +10;
   - H2, hand:3, router_2715 shadow;
   - still LOSS.

3. V48, seed 75110, seat 0:
   - ALL3 base: -484;
   - best: -484;
   - delta: 0;
   - still LOSS.

4. V48, seed 75113, seat 1:
   - ALL3 base: -794;
   - best: -697;
   - delta: +97;
   - H2, hand:9, Conditional Memory shadow;
   - still LOSS.

## Interpretation

One-locus H2/H3 physical continuations can improve terminal money but show **zero W/L headroom**
on the frozen residual-loss set.

Therefore:
- close bounded one-locus 2–3-turn physical continuation as a W/L source;
- do not simply extend horizon;
- do not deploy any third-party continuation or opponent-identity logic;
- do not promote margin-only physical patches.

The next diagnostic should remain first-party and directly attribute the four residual losses across
the existing O-RW1 / O-TW1 / O-LQ2 option composition.

## Next gate

Run a frozen option-composition attribution over the four hard contexts:

- V47 only;
- RW1 only;
- TW1 only;
- LQ2 only;
- RW1+TW1;
- RW1+LQ2;
- TW1+LQ2;
- ALL3.

Purpose:
determine whether one of the existing first-party options is responsible for residual losses and
whether selective suppression has causal W/L headroom.

No Kaggle submission is authorized by V6.
