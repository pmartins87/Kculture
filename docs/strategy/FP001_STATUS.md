# FP001 STATUS — mechanics/economics integration track

Updated: 2026-09-15

Authoritative experimental branch: `research/first-principles-economy-v1`.  
Competition-level source of truth: `STATUS.md` / `ROADMAP.md` on `fix/kaggle-parity-v1`.

## Mission

Discover causally defensible Kaggriculture mechanics, economic primitives and controllers that improve prize probability when integrated with the project's accumulated competitive knowledge.

**FP001 is not a replacement for opponent/replay/top-player knowledge.** Isolation is used only when needed for causal attribution. Final architecture may combine every legal mechanism supported by evidence.

## Proven primitives retained

### H1 — town-pulse WHEAT carry

Workflow `34843184110`: causal PASS, +916.875 mean paired value; flat-price null exactly zero.

### H1B — owned-inventory sale deferral

Workflow `34843556192`: 104/104 exact positive mechanics cases. Preserve as sale-timing primitive.

### H8/B3 — animal production + CARE

Key progression:

- one-animal runtime `34844919444`: COW +4721 mean, SHEEP +3593, GOOSE +3457;
- multi-animal runtime `34846686427`: COW3 led tested small modules;
- DAILY CARE `34847600991`: +14,207.125 over NONE and +5,205 over SURVIVAL, both 16/16 where applicable.

CARE remains a first-order production primitive.

### H9 — public-town animal-product demand

Workflow `34847099631` proved the causal demand prior:

- full-season expected pulls: EGG 228, MILK 327, WOOL 228;
- day-3 `YARN_STORE` can reverse local economics strongly toward WOOL;
- day-3 `PIZZA_SHOP` / other milk shops strongly favor MILK demand.

The official public observation is `town.unlocked_shops`; names may repeat and the list is shared/legal runtime state.

### H10 — compact routing + batched animal harvest

Workflow `34848106237`: compact routing and threshold-6 batching preserved output while reducing action load. No-CARE scaling remained positive through COW6.

### H11 — fertilizer conversion

Workflow `34848464648`: fertilizer is not always best sold. STRAWBERRY has a strong positive conversion region; TOMATO also has positive regions. Preserve fertilizer opportunity-cost logic.

### B4 — scale × CARE frontier

Workflow `34848633407`:

- COW4_DAILY +37,949.75;
- COW5_DAILY +39,447.50;
- COW5_DAILY − COW4_DAILY only +1,497.75 mean, 4–4 paired;
- COW6_DAILY − COW5_DAILY −4,174.75, 0–8;
- all animals survived.

Interpretation: the fifth animal is marginal; the sixth is beyond the action/opportunity-cost frontier under DAILY CARE.

## Premium crop integration history

### E1 — residual-idle crop overlay CLOSED

Run `34860319522`. Main-farmer idle capacity was insufficient; this closes only that architecture, not premium crops.

### E2 — dedicated crop hand CAUSAL PASS

Runs through `34866890716`. After correcting the weed/shop RNG confound, dedicated labor made the premium-crop module additive: +907 to +919 over matched controls.

### E3 — density selection PASS

Run `34868854114` selected frozen M6S1 = 6 MELON + 1 STRAWBERRY, +9,533 over COW5_DAILY in deterministic-town causal testing with full output and animal fingerprint preservation.

### E4 — normal-environment robustness STRONG PASS

Run `34869392514`:

- +9,594.5 mean;
- +8,643 median;
- CI95 [+6,057.83,+13,131.17];
- signs 33–7;
- p10 +7,970.6;
- 80/80 full mechanics/output.

M6S1 is a genuine reusable economic/physical module.

### E5 — fixed COW/SHEEP transfer FAIL

Corrected run `34922557868` passed exact COW5 trajectory parity. C5_M6S1 replicated +10,542.09 over C5_BASE, but fixed C3S2/C2S3 openings damaged M6S1 completion and lost heavily versus C5_M6S1.

Close the fixed mixed opening grid. Mixed species survive only as an adaptive H9 prior.

## CR089 population compatibility — COMPLETE / FAIL

Authoritative run `34923802262` tested C5_BASE and C5_M6S1 against 11 heterogeneous opponent edges, 12 seat-balanced games per edge.

- C5_BASE: **0W–132L**, 11/11 zero-score edges;
- C5_M6S1: **0W–132L**, 11/11 zero-score edges;
- zero mechanical failures;
- M6S1 improved monetary margin on 10/11 edges and by about +16.6k averaged over edge means, but created zero W/L gain.

Binding verdict: `M6S1_FAILS_POPULATION_COMPATIBILITY`.

Interpretation:

- M6S1 remains valid knowledge;
- static C5/C5+M6S1 are closed as competitive backbones;
- no C5 threshold rescue, opponent patch, market factorial or hosted submission.

Competition result: `docs/strategy/CR089_INTEGRATED_PHYSICAL_POPULATION_RESULT_2026-09-15.md` on `fix/kaggle-parity-v1`.

## Current active experiment — CR090 / H9 adaptive fifth animal

Phase-1 implementation:

- candidate: `candidates/fp001_h9_adaptive_fifth_animal.py`;
- test: `tools/fp001_cr090_h9_adaptive_fifth_test.py`;
- workflow: `.github/workflows/fp001-cr090-h9-adaptive-fifth.yml`;
- workflow run: `34979280512`;
- commit: `abe2829ab553fc7cc2b854d3df80f7eee3f89027`.

Frozen design:

1. all treatments use the exact four-COW DAILY H10/B4 core before the first public shop;
2. fifth purchase is deferred to the same first-shop boundary;
3. `DELAY_COW` always adds COW;
4. `DELAY_SHEEP` always adds SHEEP;
5. `H9_ADAPT` uses only `unlocked_shops[0]`, choosing SHEEP iff expected remaining WOOL demand exceeds MILK; otherwise COW;
6. 64 fresh seeds (`90201..90264`) × both seats × all three policies;
7. exact pre-reveal action-prefix parity is mandatory;
8. no automatic Kaggle submission; original final holdout untouched.

The natural seed set is stratified by the pre-treatment first-shop realization after execution; outcomes do not select the strata.

Promotion requires mechanical parity, adequate YARN/MILK support, positive causal value in the corresponding regimes, and positive natural-distribution mean versus both timing-matched fixed controls according to the frozen CR090 protocol.

## Next conditional steps

If CR090 Phase 1 passes:

1. freeze the selector;
2. integrate M6S1 with exact retention/affordability control;
3. require full crop/animal mechanics;
4. then run heterogeneous population W/L testing;
5. only on a surviving adaptive physical/controller base, run separable CR086/CR088/H1/H1B market factors.

If Phase 1 fails causally, close simple first-shop species adaptation without threshold tuning and move to the hierarchical controller.

If causal value exists but natural robustness fails, preserve H9 as a situational signal but also move to the hierarchical controller rather than tuning a threshold ladder.

## Hosted policy

No FP001/CR090 hosted submission is currently authorized. Hosted slots are reserved for mechanically valid, strategically distinct candidates that answer a real population-transfer question.
