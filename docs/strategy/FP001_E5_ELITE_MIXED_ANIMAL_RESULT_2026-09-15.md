# FP001 E5 — elite-informed mixed-animal transfer result

Date: 2026-09-15  
Corrected run: `34922557868`  
Initial run `34922078827`: infrastructure-only; it lacked the pre-result COW5/E4 trajectory-parity requirement  
Conclusion: **FIXED MIX FAIL — KEEP C5_M6S1**

## Frozen gate

Six policies were evaluated on 32 fresh default-environment seeds `69701..69732`, both seats:

- COW5, 3-COW/2-SHEEP and 2-COW/3-SHEEP;
- each animal family with no crop and with exact requested M6S1;
- H10 compact five-pasture routing, threshold-6 harvest batching and DAILY CARE;
- passive opponent; 720 steps; starting money 3000;
- no H9 shop adaptation and no CR086/CR088 market overlay.

Before economic evidence was admissible, the generic species scheduler had to reproduce the original E4 COW5 and COW5+M6S1 trajectories exactly for crop/no-crop × both seats on separate seed `69700`.

## Infrastructure parity

**4/4 exact full-game trajectories passed**: C5_BASE and C5_M6S1, each in both seats, matched the original E4 implementation action-for-action with identical statuses and rewards. The generic five-pasture implementation is therefore an admissible extension rather than a changed COW5 control.

## Final-bank distributions

| Policy | Mean | Median | p10 | Min | Max |
|---|---:|---:|---:|---:|---:|
| C5_BASE | 39,061.34 | 40,220.0 | 31,717.2 | 15,231 | 48,892 |
| **C5_M6S1** | **49,603.44** | **50,191.5** | **44,865.9** | 24,409 | **57,989** |
| C3S2_BASE | 36,151.25 | 36,879.5 | 32,440.8 | 23,284 | 41,981 |
| C3S2_M6S1 | 41,210.98 | 42,093.5 | 36,825.9 | 28,932 | 47,980 |
| C2S3_BASE | 30,942.94 | 30,955.0 | 28,845.0 | 26,371 | 33,789 |
| C2S3_M6S1 | 35,232.72 | 34,971.0 | 33,303.8 | 29,963 | 37,970 |

## COW5 crop transfer

C5_M6S1 minus C5_BASE:

- mean **+10,542.09**;
- median **+10,160**;
- CI95 **[+7,160.75,+13,923.44]**;
- signs **29 positive / 3 negative**;
- p10 gap **+13,148.7**;
- 64/64 correct animals, exact animal fingerprint and full 36 MELON + 8 STRAWBERRY output.

This independently confirms the E4 survivor under the fresh E5 seed distribution.

## Fixed mixed-family failure

Both mixed families placed and preserved all five intended animals and matched their own animal-only FEED/CARE/movement/product-output fingerprint in 64/64 cases. They nevertheless failed the frozen hybrid eligibility rule because neither realized the full crop block:

- C3S2_M6S1 sold only **18 MELON + 8 STRAWBERRY** per case;
- C2S3_M6S1 sold only **12 MELON + 8 STRAWBERRY** per case;
- full crop output: **0/64** for each mixed family.

The requested full M6S1 opening is therefore structurally incompatible with these fixed mixed purchases under the frozen ordering/liquidity policy. This gate does not authorize an affordability/order rescue.

The mixed hybrids also failed economic diversity retention versus C5_M6S1:

| Contrast | Mean | Median | CI95 | Signs | p10 gap |
|---|---:|---:|---:|---:|---:|
| C3S2_M6S1 − C5_M6S1 | **−8,392.45** | −9,306.0 | [−10,930.28,−5,854.62] | 4–28 | −8,040.0 |
| C2S3_M6S1 − C5_M6S1 | **−14,370.72** | −15,232.5 | [−16,991.64,−11,749.80] | 2–30 | −11,562.1 |

Both exceed the frozen −4,000 mean/median and −5,000 p10 retention limits.

## Decision

**MIXED_FIXED_FAIL_KEEP_C5_M6S1.**

- close exactly the fixed C3S2/C2S3 + full-opening-M6S1 architectures;
- do not run a C4S1/S4C1 ladder, seed-specific patch or crop-density rescue;
- preserve the elite mixed-animal prior and H9 public-shop-conditioned allocation for a genuinely adaptive controller later;
- advance C5_M6S1 and exact C5_BASE control to the CR089 heterogeneous population gate, where the crop module must demonstrate win/loss transfer rather than passive-opponent bank gain;
- no hosted submission is authorized.
