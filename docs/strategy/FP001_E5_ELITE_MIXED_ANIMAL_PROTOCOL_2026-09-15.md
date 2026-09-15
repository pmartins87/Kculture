# FP001 E5 — elite-informed mixed-animal transfer gate

Date: 2026-09-15  
Branch: `research/first-principles-economy-v1`

## Question

Does the E4-validated one-hand M6S1 crop block transfer cleanly to the two fixed COW/SHEEP compositions repeatedly observed in CR087's current ~3000-class macro families, and is either mixed hybrid economically competitive enough to retain for a heterogeneous population gate?

## Frozen architectures

All use five compact pasture positions, H10 threshold-6 harvest batching, DAILY CARE, the same WHEAT-buffer rule and no routine animal hand.

1. `C5_BASE`: 5 COW, no crop;
2. `C5_M6S1`: exact E4 winner;
3. `C3S2_BASE`: 3 COW + 2 SHEEP, no crop;
4. `C3S2_M6S1`: same animal mix + exact M6S1;
5. `C2S3_BASE`: 2 COW + 3 SHEEP, no crop;
6. `C2S3_M6S1`: same animal mix + exact M6S1.

Species order follows the compact snake: COW positions first, then SHEEP. The crop block remains 6 MELON + 1 STRAWBERRY, at most one first-cost hand per day, no MELON fertilizer and H11 STRAWBERRY fertilizer at ages 9 and 13.

No adaptive species switching, public-shop conditioning, CR086/CR088 market overlay or opponent feature is added in this gate.

## Environment and sample

- official default weeds and town-shop unlocks;
- 32 fresh seeds `69701..69732`;
- both seats for every policy;
- passive opponent to isolate production/economic robustness;
- 720 steps, starting money 3000;
- exact `kaggle-environments==1.32.7`.

Primary statistical unit is the seed after averaging seats.

Before the grid is admissible, the generic five-pasture implementation must reproduce the exact frozen E4 COW5 baseline and COW5+M6S1 trajectories in four full-game parity cases (crop/no-crop × both seats) on separate seed `69700`. Any mismatch is an infrastructure failure and invalidates the economic grid.

Crop/no-crop comparisons change tile occupancy and therefore the later shop RNG stream; treat them as expected-distribution contrasts. Mixed-vs-COW5 comparisons among the M6S1 policies have equal occupied tiles, so they preserve the shop RNG path and isolate fixed species composition more cleanly.

## Metrics

- final-bank distribution and p10 for every policy;
- hybrid minus own-base distribution for each species family;
- mixed-hybrid minus C5_M6S1 paired mean, median, CI95 and signs;
- exact animal survival/species placement;
- main FEED/CARE/movement and product-output fingerprint;
- full 36 MELON + 8 STRAWBERRY output;
- engine/non-DONE failures.

## Frozen decisions

### Mechanical eligibility

A hybrid is eligible only with zero failures, five correct surviving animals in every case, full crop output in every case, and an exact main-farmer/animal-output fingerprint against its own no-crop base.

The whole gate is eligible only after 4/4 exact COW5 trajectory-parity cases against the original E4 implementation.

### Crop-transfer PASS

For each mixed family separately, require:

- mean hybrid-minus-base >= +2,000;
- median > 0;
- approximate CI95 lower bound > 0;
- hybrid p10 no worse than base p10 by more than 2,000.

### Primary economic promotion

Promote a mixed hybrid as the primary E5 survivor only if its matched difference versus `C5_M6S1` has positive mean, positive median and CI95 lower bound > 0.

### Diversity retention

If no mixed hybrid wins economically, retain at most one as a secondary population challenger only if it passes crop transfer and all of:

- mean disadvantage versus `C5_M6S1` no worse than 4,000;
- median disadvantage no worse than 4,000;
- p10 disadvantage no worse than 5,000.

Choose the higher-mean qualifying mixed hybrid. Otherwise close fixed mixed composition and keep `C5_M6S1` as the physical survivor.

## After E5

No hosted submission. The survivor set goes to heterogeneous population testing against exact hosted anchors and multiple CR088/current-top macro representatives. H9 public-shop-conditioned species adaptation remains a separate later factor, especially if fixed mixed composition loses self-economics.

## Stop rule

No C4S1/S4C1 composition ladder, no seed-specific patching and no density retuning. A fixed-mix failure redirects to H9 adaptive species allocation or the population gate; it does not reopen the frozen E5 grid.
