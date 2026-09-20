# ALL3 V11B Hosted Loss Signature Atlas — Result — 2026-09-20

Workflow: **`35519476400`**  
Launch commit: `de7804181b279d44954f0ee6bdf4d63ff0693a1d`

Decision: **`V11B_PUBLIC_CROP_SHIFT_REGIME_SIGNAL`**

Mechanical/data:
- 128/128 hosted replays parsed;
- 57 wins / 71 losses;
- failures: 0.

## Main public-state signal

At exact hosted checkpoints, define:

`opp_carrot_adv` =
opponent public CARROT plant count > ALL3 public CARROT plant count.

Qualifying checkpoints:

- step 456: 9/9 losses, mean margin -5303;
- step 480: 8/8 losses, mean margin -5413.875;
- step 504: 13/13 losses, mean margin -3801.46;
- step 552: 17/17 losses, mean margin -4095.71;
- step 600: **22/22 losses**, mean margin **-3504.27**.

A stricter step-600 signature:

`opponent CARROT - own CARROT >= 4`
AND
`own WHEAT - opponent WHEAT >= 4`

occurred in **15/15 losses**, mean margin **-4157.07**.

The first observed CARROT-advantage cutoff also remains highly concentrated in losses:
- by 408: 7/7 losses;
- by 456: 9/9;
- by 504: 15/15;
- by 552: 17/17;
- by 600: 22/22;
- by 648: 30 losses / 1 win.

## Other separation

At step 600:
- public money gap standardized loss-vs-win effect: about **-0.898**;
- CARROT crop-gap effect: about **-0.633**;
- WHEAT crop-gap effect: about **+0.605**.

ALL3 remains relatively macro-rigid; the modal step-600 public macro crop/animal profile begins
`WHEAT 37, CARROT 4, TOMATO 0, STRAWBERRY 17, MELON 0`.

## Critical interpretation

This is **observational** evidence only.

It does not prove that copying CARROT, reducing WHEAT, or reacting to the opponent will improve W/L.
A stronger opponent family may simply create both the CARROT signature and the loss.

Therefore:
- do not reopen O-PC1;
- do not install a CARROT response directly;
- first test whether the same public-state regime transfers to an exact-engine population of executable public agents on untouched seeds.

No automatic Kaggle submission.
