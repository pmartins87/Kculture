# ALL3 V9B Causal Structural Isolation — Result — 2026-09-20

Workflow: **`35517836947`**  
Launch commit: `fefc69744fb0b12bdd1c71141c53d0ff1083bd17`

Decision: **`V9B_NO_WL_HEADROOM_CLOSE_ONE_TURN_STRUCTURAL`**

Mechanical:
- 16/16 frozen branches PASS;
- failures 0;
- exact base replay PASS;
- exact pre-target parity PASS.

## INSERT_DROP

8 branches:
- loss->win flips: **0**;
- mean margin delta: **-7.875**;
- positive-margin states: 1;
- positive-margin contexts: only context 1.

Best:
- context 1 earliest, turn 153: -86 -> -65, +21 margin, still loss.

Other earliest states:
- context 0 turn 80: -27 margin;
- context 2 turn 80: -30;
- context 3 turn 80: -27.

The repeated turn-337 split-insertion was W/L-neutral in all four contexts.

## QTY_UP

8 branches:
- loss->win flips: **0**;
- mean margin delta: **0**;
- positive-margin states: 0.

Both repeated archetypes:
- turn 427;
- turn 698;
were exactly W/L- and margin-neutral across all four contexts.

## Binding interpretation

V9A proved that residual V48 structural behavior exists in abundance.
V9B proves that representative **one-turn** INSERT_DROP and QTY_UP substitutions do not expose reusable W/L headroom.

Therefore close:
- one-turn residual V48 structural imitation;
- state-threshold retuning of these branches;
- searching more individual turns in the same family.

This does not contradict V4B/V4D/V4E: those experiments showed the historical V48 market advantage was cumulative and long-horizon. The next architecture must therefore test cumulative residual interaction under ALL3 rather than more local surgery.

No Kaggle submission is authorized.
