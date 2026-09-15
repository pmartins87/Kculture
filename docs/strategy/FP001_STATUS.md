# FP001 STATUS — mechanics/economics innovation track

Updated: 2026-09-15

Authoritative branch: `research/first-principles-economy-v1`.

## Mission

Discover causally defensible Kaggriculture mechanics, economic primitives and physical schedulers that can increase the probability of winning the competition when integrated with the project's accumulated competitive knowledge.

**FP001 is not a replacement for opponent/replay/top-player knowledge.** Its earlier zero-lineage isolation was useful experimentally because it made attribution clean, but it is no longer a binding architecture restriction. Proven FP001 primitives may now be combined with CR053/CR086/CR087/CR088 knowledge, elite macro priors and legal public replay evidence whenever the combination improves competitive performance.

Originality is not an objective. Hosted/population strength is.

## Binding source of truth

Read together:

1. `docs/strategy/FP001_FIRST_PRINCIPLES_INNOVATION_PROTOCOL_2026-09-14.md` for the experimental-origin protocol and mechanics work;
2. `docs/strategy/FP001_ROADMAP.md` for current integration gates;
3. live `STATUS.md` / `ROADMAP.md` on `fix/kaggle-parity-v1` for the competition-level source of truth;
4. the FP001 candidates/test tools referenced below.

Where the original protocol says competitor evidence cannot construct policy, that restriction now applies only when a test explicitly needs isolation for causal attribution. It is not a global ban on using accumulated competitive knowledge.

## Proven market primitives

- **FP0 mechanics parity: PASS** — workflow `34842825909`.
- **H1 town-pulse WHEAT carry: causal PASS** — workflow `34843184110`; mean paired +916.875 over 32 episodes; flat-price null exactly zero.
- **H1B owned-sale deferral: mechanics PASS** — workflow `34843556192`; 104/104 exact positive cases. Large isolated timing values include MILK q50/D7 +792, STRAWBERRY q50/D7 +731, WOOL q50/D6 +827.

These are preserved as economic operators for later competitive integration, not promoted as standalone strategy.

## H8 animal/fertilizer production track

### R2A exact economics — PASS

Workflow `34844070131`. Minimum-survival feeding keeps animals alive on 15 WHEAT over 30 days while exposing one fertilizer per surviving day. Pre-routing n=3 day-30 economics: SHEEP +10411, COW +10111, GOOSE +9544.

### R2A2-A exact FEED/CARE frontier — PASS

Workflow `34844616747`. Abstract action-priced control favored SHEEP across tested horizons/shadow prices. This was correctly treated as economics/control evidence, not physical architecture evidence.

### R2A2-B1 one-animal runtime — PASS

Workflow `34844919444`. Mean realized deltas: COW +4721, SHEEP +3593, GOOSE +3457. Runtime ranking reversed the abstract species ranking.

### R2A2-B2 multi-animal runtime — PASS

Workflow `34846686427`.

Mean deltas over 8 fresh seed/seat episodes each:

1. COW3_H0 **+12880.75**;
2. COW3_H2 +12824.75;
3. COW2_SHEEP1_H2 +11881.0;
4. COW1_SHEEP2_H2 +10874.75;
5. SHEEP3_H2 +9807.0;
6. COW2_H0 +8522.25;
7. COW2_H2 +8465.0.

Routine daily hands were negative marginal value in the animal-only small module: COW2 H2-H0 -57.25 and COW3 H2-H0 -56.0. This result does **not** globally close HIRE; crop workload creates a new context where labor can have positive marginal value and is being retested causally.

### R2A2-B3 CARE overlay — STRONG PASS

Workflow **`34847600991`**.

Paired 16 fresh seed/seat cases:

- `NONE`: mean **+13101.375**;
- `SURVIVAL`: mean **+22103.5**;
- `DAILY`: mean **+27308.5**.

Paired causal deltas:

- SURVIVAL minus NONE: **+9002.125**, 16/16 wins;
- DAILY minus NONE: **+14207.125**, 16/16 wins;
- DAILY minus SURVIVAL: **+5205**, 16/16 wins.

CARE is therefore a first-order production mechanism and remains promoted.

## H9 town-conditioned animal demand — PASS

Workflow `34847099631`.

Full-season prior expected town pulls: EGG 228, MILK 327, WOOL 228. MILK prior demand is +99 / +43.4% over WOOL. Public shop reveals can strongly reverse local species economics; e.g. day3 YARN_STORE implies expected remaining WOOL 508.5 vs MILK 263.25, while day3 PIZZA_SHOP implies MILK 425.25 vs WOOL 184.5.

Decision: expansion/product mix should eventually use public shop composition rather than a fixed monoculture rule.

## H10 compact COW scale + batched harvest — PASS

Workflow **`34848106237`**.

Key causal results over 8 paired cases:

- compact H10 COW3 threshold1 vs B2 COW3: **+137.75 mean**, 8/8 wins;
- harvest threshold6 vs threshold1: **+861.5 mean**, 8/8 wins;
- batching preserved realized milk while cutting animal HARVEST actions from roughly 33/episode to ~7/episode;
- COW4 vs COW3: +4108.5 mean, 8/8;
- COW5 vs COW4: +3354.75 mean, 8/8;
- COW6 vs COW5: +4435.25 mean, 8/8;
- all animals survived at all tested no-CARE scales.

Mean no-CARE COW6 result: **+26764.5**. Thus no-CARE scaling had not saturated at six; the action frontier appears only once CARE intensity is added.

## H11 fertilizer conversion audit — PASS / hybrid mechanism discovered

Workflow **`34848464648`**.

Exact-engine audit disproved the implicit assumption that fertilizer should always be sold.

At nominal market values:

- WHEAT/CARROT fertilizer use is generally inferior to selling fertilizer;
- TOMATO has positive conversion regions;
- **STRAWBERRY is strongly attractive**: two well-timed fertilizer applications produce +4 additional strawberries and approximately **+268 nominal conversion value** versus selling those two fertilizer units at normal prices;
- under product scarcity / fertilizer abundance the advantage can become much larger;
- MELON showed no additional tested fertilizer benefit in this exact setup.

This creates a high-priority integration hypothesis: animals can be fertilizer factories feeding premium crop production. It does not imply that STRAWBERRY is the best labor-adjusted premium crop.

## B4 scale × CARE — PASS; action-capacity frontier located

Workflow **`34848633407`**.

Mean final-bank deltas over starting cash, 8 fresh paired seed/seat cases:

- COW3_NONE +14201.75
- COW3_SURVIVAL +23440.25
- COW3_DAILY +29633.0
- COW4_NONE +18959.25
- COW4_SURVIVAL +31551.75
- **COW4_DAILY +37949.75**
- COW5_NONE +22630.75
- **COW5_SURVIVAL +36685.25**
- **COW5_DAILY +39447.50** — current mean-best animal-only architecture
- COW6_NONE +25406.75
- COW6_SURVIVAL +33054.25
- COW6_DAILY +35272.75

Critical paired interpretation:

- COW5_DAILY − COW5_NONE: **+16816.75**, 8/8;
- COW5_DAILY − COW5_SURVIVAL: **+2762.25**, 6/2;
- COW5_DAILY − COW4_DAILY: **+1497.75**, only 4/4;
- COW6_SURVIVAL − COW5_SURVIVAL: **−3631.0**, 0/8;
- COW6_DAILY − COW5_DAILY: **−4174.75**, 0/8.

All animals survived. Therefore six cows under CARE lose due to **action/opportunity-cost saturation**, not mortality.

Decision: preserve COW4_DAILY, COW5_SURVIVAL and COW5_DAILY as animal-only controls for integration rather than declaring one universal optimum.

## E1 marginal STRAWBERRY overlay — MECHANICAL PASS / ARCHITECTURE CLOSED

Workflow **`34860319522`**. Full result: `docs/strategy/FP001_E1_STRAWBERRY_MARGINAL_RESULT_2026-09-14.md`.

E1 allowed one early STRAWBERRY to use only main-farmer actions that the animal backbone would otherwise PASS. It never overwrote a non-PASS animal action.

Results over 8 paired fresh seed/seat observations per backbone:

- **COW4_DAILY**: S1-control `+317` mean but median `-2474`, only **2W-6L**; crop planted 8/8 but received only one WATER per episode, produced zero berries and failed 8/8. The positive mean is variance, not crop value.
- **COW5_SURVIVAL**: S1-control **`-693.5` mean**, 4W-4L; crop planted 8/8, received 72 WATER total and sold 32 berries = 4/episode, but executed zero fertilizer actions. Animal output/survival stayed intact.
- **COW5_DAILY**: S1-control **exactly `-100` in 8/8**; the control had zero idle PASS. The hybrid bought the 100-cost seed but never obtained a turn to plant it.

Decision: **close only the residual-idle-main-farmer STRAWBERRY architecture. Do not close STRAWBERRY or premium crops.** E1 identifies labor/action allocation as the failure mechanism.

## E2 dedicated STRAWBERRY hand — CAUSAL PASS AFTER RNG CORRECTION

Runs `34864820833`, `34865508451`, `34866389261` and `34866890716`.

The raw/default-environment E2 comparisons contained implausible ±10k–20k swings despite unchanged animal actions/output. E2C traced this to an official-engine RNG coupling: crop occupancy changes the number of weed RNG draws before random shop selection, which changes town demand and market prices. Same nominal seed is therefore not a common-random-number control when tile occupancy changes.

E2D reused the frozen policy with weeds disabled and stochastic shop unlocks removed. One dedicated first-cost hand then produced 8 STRAWBERRY with two H11 fertilizer applications while preserving the animal fingerprint. Full-module gains versus animal-only were **+907** on COW4_DAILY, **+919** on COW5_SURVIVAL and **+919** on COW5_DAILY, all 8/8.

Decision: dedicated labor can make premium crop conversion genuinely additive, but one plant severely under-uses the hand.

## E3 single-hand crop density — PASS / M6S1 SELECTED

Workflow **`34868854114`**. Full result: `docs/strategy/FP001_E3_SINGLE_HAND_CROP_DENSITY_RESULT_2026-09-14.md`.

In the deterministic-town causal environment, the frozen grid showed MELON dominating STRAWBERRY as the dense hand workload. The selected **M6S1** block — 6 MELON + 1 STRAWBERRY — added **+9,533** over COW5_DAILY, reached full 36 MELON + 8 STRAWBERRY output and preserved 5/5 cows plus the exact FEED/CARE/movement/MILK fingerprint. No M7/M8 or post-result density retuning was authorized.

## E4 normal-environment robustness — STRONG PASS

Workflow **`34869392514`**, job `104061255265`. Full result: `docs/strategy/FP001_E4_NORMAL_ENVIRONMENT_ROBUSTNESS_RESULT_2026-09-15.md`.

Across 40 fresh default-environment seeds and both seats:

- base mean final-bank delta: **36,810.8**;
- M6S1 mean: **46,405.3**;
- mean difference: **+9,594.5**; median **+8,643**;
- approximate CI95 **[+6,057.83, +13,131.17]**;
- signs **33 positive / 7 negative**;
- p10 gap **+7,970.6**;
- zero failures; 80/80 survival, exact animal fingerprint and full crop output.

Every frozen Strong-PASS condition fired. M6S1 is a robust additive production module, but it is not yet a hosted candidate.

## Competitive convergence with CR087

Accumulated elite macro evidence independently supports mixed production: current ~3000-class policies commonly combine premium crops such as MELON/STRAWBERRY with durable mixed animals and state-adaptive market behavior.

Important labor-adjusted prior: official mechanics give MELON seed cost 80, nominal base sale 250, one-time crop, max yield 6; STRAWBERRY seed cost 100, base 120 and ongoing maintenance. This does **not** settle the comparison, but together with CR087's strong MELON prevalence it makes MELON a high-priority next comparator rather than endlessly retuning STRAWBERRY.

The historical H8 mixed scheduler remains reusable infrastructure, but its original 3-animal form predates B3 CARE and H10 batching. Future mixed COW/SHEEP work should port those proven primitives into the known scheduler rather than rewrite it from scratch.

## Current active decision

**E5 elite-informed mixed-animal transfer is active and frozen.** Protocol: `docs/strategy/FP001_E5_ELITE_MIXED_ANIMAL_PROTOCOL_2026-09-15.md`.

The gate compares exact COW5+M6S1 with 3-COW/2-SHEEP+M6S1 and 2-COW/3-SHEEP+M6S1, plus own no-crop controls, on 32 fresh default-environment seeds and both seats. It ports H10 compact setup/batching and B3 DAILY CARE without adding H9 adaptation or CR086/CR088 market logic.

Only a mixed hybrid with full mechanics and robust crop transfer may advance. A fixed mix can become the primary survivor only by beating COW5+M6S1 under the frozen paired rule; otherwise at most one bounded non-inferior mixed architecture is retained as a heterogeneous-population challenger.

After E5, the survivor set faces exact hosted anchors and multiple CR088/current-top macro representatives. No FP001-only hosted submission is authorized.

## Hosted policy

No FP001-only hosted submission is authorized. The track's value is its library of proven primitives and its contribution to an integrated competitive policy. A hosted candidate should be strategically distinct, mechanically valid and answer a population-transfer question.
