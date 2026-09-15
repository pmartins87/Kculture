# FP001 ROADMAP — mechanics/economics integration

Updated: 2026-09-15

Objective: discover and integrate mechanics-derived economic/physical primitives that increase the probability of a prize-winning Kaggriculture policy.

## Binding rules

- Official environment + controlled experiments are the authority for mechanics and causal attribution.
- Competitive knowledge is cumulative; legal public opponent/replay/top-player evidence may inform architecture, priors, comparators and final policy construction.
- Use isolation when needed for causality, not as a purity requirement.
- Every promotion stage needs a causal hypothesis and matched control/null where applicable.
- Use fresh seeds and both seats.
- No identity/rating/EpisodeId/hidden-seed/future/opponent-private runtime features.
- Changed code does not inherit validation.
- Do not rescue failed architectures with post-result threshold ladders.
- Promotion objective is hosted/population strength, not novelty.

## Completed mechanics foundation

- R0 mechanics parity — PASS, `34842825909`.
- H1 town-pulse WHEAT carry — PASS, `34843184110`.
- H1B owned-sale deferral — PASS, `34843556192`.
- H8 animal/fertilizer economics — PASS, `34844070131`.
- FEED/CARE frontier — PASS, `34844616747`.
- one-animal runtime — PASS, `34844919444`.
- multi-animal runtime — PASS, `34846686427`.
- H9 town-conditioned demand — PASS, `34847099631`.
- DAILY CARE overlay — STRONG PASS, `34847600991`.
- H10 compact scale + batched harvest — PASS, `34848106237`.
- H11 fertilizer conversion — PASS, `34848464648`.
- B4 scale × CARE — PASS / action frontier located, `34848633407`.

Important retained facts:

- COW5_DAILY only weakly exceeds COW4_DAILY (+1,497.75 mean, 4–4);
- COW6_DAILY is decisively worse than COW5_DAILY (−4,174.75, 0–8);
- H9 public shop state can strongly reverse MILK versus WOOL demand;
- CARE, compact routing, batched harvest and fertilizer opportunity cost remain valid reusable primitives.

## Crop integration chain

### E1 — residual-idle STRAWBERRY CLOSED

Run `34860319522`. The architecture lacks labor capacity; do not retune it.

### E2 — dedicated premium-crop hand CAUSAL PASS

Through run `34866890716`. Corrected for weed/shop RNG coupling. Dedicated labor added +907 to +919 over matched animal controls.

### E3 — density PASS / M6S1 frozen

Run `34868854114`: M6S1 = 6 MELON + 1 STRAWBERRY, +9,533 in deterministic-town causal testing with complete output and animal preservation.

### E4 — default-environment robustness STRONG PASS

Run `34869392514`: +9,594.5 mean, CI95 [+6,057.83,+13,131.17], 33–7 signs, 80/80 full mechanics.

### E5 — fixed mixed-animal transfer FAIL

Run `34922557868`: exact COW5 parity passed, C5_M6S1 retained strong economic value, but fixed C3S2/C2S3 openings reduced crop completion and lost heavily. Close the fixed mixed opening grid.

## R3 / CR089 — heterogeneous population gate COMPLETE / FAIL

Run `34923802262`:

- C5_BASE 0W–132L;
- C5_M6S1 0W–132L;
- 11/11 zero-score edges for each;
- zero mechanical failures;
- M6S1 improved margins but zero W/L coverage.

Verdict: `M6S1_FAILS_POPULATION_COMPATIBILITY`.

Binding stop:

- close static C5/C5+M6S1 as competitive backbones;
- preserve M6S1/CARE/H10/H11 as modules;
- do not run market-factor rescue on C5;
- do not submit C5.

## R4 / CR090 — H9 public-shop adaptive marginal expansion CURRENT

### Phase 1 — simple first-shop fifth-animal selector ACTIVE

Run `34979280512`, commit `abe2829ab553fc7cc2b854d3df80f7eee3f89027`.

Architecture:

- exact four-COW DAILY core before first shop reveal;
- fifth animal delayed to the first legal public shop boundary;
- timing-matched `DELAY_COW` and `DELAY_SHEEP` controls;
- `H9_ADAPT` chooses SHEEP iff first-shop-conditioned expected remaining WOOL demand exceeds MILK, else COW;
- selector uses only `town.unlocked_shops[0]` plus frozen official mechanics.

Evaluation:

- fresh seeds `90201..90264`;
- both seats;
- all three policies on every case;
- exact pre-reveal action-prefix parity required;
- natural first-shop strata evaluated without outcome-based selection;
- causal YARN and MILK regime gates plus overall natural robustness gate.

Outcomes are frozen in `docs/strategy/CR090_H9_PUBLIC_SHOP_ADAPTIVE_PROTOCOL_2026-09-15.md` on the competition branch.

### Phase 2 — H9 + M6S1 retention CONDITIONAL

Only if Phase 1 passes:

- freeze the H9 selector;
- combine it with M6S1;
- compare against exact H9 animal-only / timing-matched physical control;
- require full crop completion, animal survival and scheduler fingerprint retention;
- reject any recurrence of E5 opening-liquidity failure.

### Phase 3 — heterogeneous population transfer CONDITIONAL

Only after Phase 2 mechanics/robustness pass. Measure W/L coverage over exact hosted anchors plus diverse top-macro representatives. Monetary gain alone cannot promote.

## R5 — market/economic integration CONDITIONAL

Only on a physical/controller survivor:

- own-base control;
- CR086/CR088 legal latent-supply SELL handling;
- H1 WHEAT pulse carry;
- H1B owned-sale deferral;
- combinations only after individual attribution.

Do not run this factorial on the failed C5 backbone.

## R6 — hierarchical competitive controller

If simple H9 adaptation fails, or after successful H9 physical integration, move to the higher-level controller:

- elite macro production prior;
- physical/action-capacity scheduler;
- fertilizer/crop opportunity-cost allocator;
- public-town-conditioned marginal expansion;
- legal adaptive market controller.

This is the intended path away from fixed tapes and fixed farms toward a genuinely state-adaptive architecture.

## R7 — hosted calibration

Hosted slots are high-information population sensors. Submit only mechanically valid, strategically distinct candidates that answer a transfer question.

A locally profitable or novel policy is insufficient. Target remains the ~3000+ class observed at the current top-10 frontier.

## Stop criteria

- no threshold rescue of the closed C5 backbone;
- no static mixed-opening ladder after E5;
- no threshold ladder for simple H9 first-shop adaptation if CR090 Phase 1 fails;
- no market overlay promotion without own-base causal attribution and population transfer;
- do not revive modal tape, replay stitching, static market-prefix or 1-NN imitation without new evidence that changes their documented failure mechanism;
- continue integrating successful old and new knowledge until a candidate is plausibly prize-class or the active branch reaches its declared stop gate.
