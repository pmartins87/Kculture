# CR090 — H9 public-shop adaptive marginal expansion protocol

Date: 2026-09-15  
Authoritative branch: `fix/kaggle-parity-v1`

## Question

Can legal public town-shop information improve the marginal fifth-animal allocation when the purchase timing is held fixed, thereby turning H9 from a descriptive demand model into a causal physical controller?

CR090 is a structural response to CR089. It is **not** a rescue of C5 and it does not inherit C5 population eligibility.

## Why the fifth slot

Three independent results make this the cleanest adaptive boundary:

1. B4: COW5_DAILY exceeded COW4_DAILY by only +1,497.75 mean with a 4–4 paired sign split;
2. B4: a sixth CARE animal was decisively negative despite full survival;
3. H9: public shop composition can strongly reverse expected remaining MILK versus WOOL town demand.

E5 additionally showed that buying a fixed COW/SHEEP mix at the opening can damage liquidity and crop completion. Therefore CR090 does **not** test another fixed opening composition.

## Legal runtime signal

Frozen official environment `kaggle-environments==1.32.7` exposes shared public observation:

- `town.unlocked_shops`: ordered list of currently active public shop names.

The adaptive selector uses only the **first revealed shop** (`unlocked_shops[0]`) and official mechanics. It never uses identity, rating, EpisodeId, hidden seed, future state, opponent-private inventory or replay metadata.

Using only the first shop makes the decision stateless and frozen: later shop unlocks cannot change an animal already purchased/placed.

## Frozen physical architecture for Phase 1

Before the first shop reveal:

- 4 COW;
- H10 compact target positions/routing;
- threshold-6 animal-product harvest batching;
- DAILY CARE;
- no crop hand in Phase 1.

After the first shop is publicly visible, exactly one fifth-animal policy is activated.

### Timing-matched policies

1. `DELAY_COW`: fifth animal is always COW after the first shop reveal;
2. `DELAY_SHEEP`: fifth animal is always SHEEP after the first shop reveal;
3. `H9_ADAPT`: fifth animal is selected by H9 expected remaining public-town demand computed from the first revealed shop plus the official prior over future shop copies.

Frozen selector:

- choose SHEEP iff expected remaining `WOOL > MILK` at the first reveal;
- otherwise choose COW;
- ties choose COW, consistent with the stronger observed one-animal runtime prior.

No performance-derived threshold is allowed.

## Why timing-matched controls are mandatory

All three policies must execute the same four-COW prefix and delay the fifth purchase to the same public information boundary.

This prevents a false conclusion caused by:

- opening liquidity;
- delayed purchase timing;
- delayed wheat demand;
- different early pathing/action load.

The test must verify exact pre-reveal action-prefix parity for all three policies on every evaluated seed/seat case.

## Phase 1 — causal + natural robustness screen

Use fresh seeds `90201..90264`, both seats, against the same passive opponent. All three policies run on every seed/seat pair.

Because the policies are identical until the first public shop appears, the realized first shop must be identical across the three matched trajectories. Cases are then stratified by that pre-treatment public signal:

- `YARN`: first shop `YARN_STORE`;
- `MILK`: first shop in `{PIZZA_SHOP, ICE_CREAM_SHOP, SMOOTHIE_SHOP}`;
- `NEUTRAL`: all other first shops.

This stratification is not selected by outcome.

### Mechanical requirements

All must hold:

- 0 errors / non-DONE games;
- exact pre-reveal prefix parity across all three policies;
- identical first-shop classification across matched trajectories;
- H9 selector decision equals its frozen public-demand rule in 100% of cases;
- fifth animal is eventually placed as intended in 100% of eligible complete episodes;
- no hidden/future/private runtime feature.

### Causal economic requirements

Minimum regime support:

- at least 8 YARN cases;
- at least 16 MILK cases.

On YARN cases, where the frozen selector should choose SHEEP:

- mean `H9_ADAPT - DELAY_COW` final-bank delta > 0;
- median > 0;
- positive-sign rate >= 0.65.

On MILK cases, where the frozen selector should choose COW:

- mean `H9_ADAPT - DELAY_SHEEP` final-bank delta > 0;
- median > 0;
- positive-sign rate >= 0.65.

Natural-distribution robustness over all fresh cases:

- mean `H9_ADAPT - DELAY_COW` > 0;
- median `H9_ADAPT - DELAY_COW` >= 0;
- mean `H9_ADAPT - DELAY_SHEEP` > 0.

No post-result threshold tuning is permitted.

## Phase 1 outcomes

### PASS

If mechanics + regime support + causal rules + natural robustness all pass:

- freeze the H9 selector;
- proceed to Phase 2 integration/retention, adding the already-proven M6S1 module with an exact animal/controller control;
- require crop completion and animal fingerprint retention before any population gate.

### Causal pass / natural robustness fail

Preserve H9 as a situational mechanism but do not promote this simple first-shop selector. Move directly to the hierarchical controller where town state competes with other opportunity-cost signals. Do not threshold-tune this selector.

### FAIL

Close simple first-shop COW/SHEEP adaptation. Do not run a species-threshold ladder. Advance to the higher-level hierarchical controller.

## Later gates if Phase 1 passes

1. Phase 2: H9 + M6S1 retention/affordability with exact matched physical control;
2. Phase 3: heterogeneous population W/L panel;
3. only after a physical/controller survivor: separable CR086/CR088/H1/H1B market integration;
4. hosted sensor only if the resulting candidate is strategically distinct, mechanically valid and answers a population-transfer question.

## Submission policy

CR090 Phase 1 cannot submit to Kaggle. No hosted submission is authorized by this protocol alone.
