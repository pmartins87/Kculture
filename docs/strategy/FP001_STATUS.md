# FP001 STATUS — mechanics/economics innovation track

Updated: 2026-09-14

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

Routine daily hands were negative marginal value in the animal-only small module: COW2 H2-H0 -57.25 and COW3 H2-H0 -56.0. This result does **not** globally close HIRE; H11 crop workload creates a new context where labor can have positive marginal value and must be retested causally.

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

This creates a high-priority integration hypothesis:

> animals are not only sale-product engines; they can be fertilizer factories feeding premium crop production.

Because STRAWBERRY also creates substantial watering/harvest/fertilize workload, the previous animal-only negative-HIRE result must be retested rather than generalized.

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

Decision: do not declare COW5_DAILY a universal farm optimum. Preserve three animal-only controls for hybrid integration:

1. COW4_DAILY — slightly lower mean, more action headroom;
2. COW5_SURVIVAL — lower CARE intensity, more headroom for crop work;
3. COW5_DAILY — mean-best animal-only benchmark.

## Competitive convergence with CR087

The accumulated elite macro evidence independently supports the same direction now suggested by H11: current ~3000-class policies commonly combine premium crops such as MELON/STRAWBERRY with durable animal production and state-adaptive market behavior. FP001 therefore should **not** continue optimizing a pure cow farm in isolation.

The next experiment is an integrated hybrid gate using elite-informed macro priors plus causally proven FP001 primitives.

## Current active decision

Build and compare matched hybrids:

- COW4_DAILY + fertilized STRAWBERRY;
- COW5_SURVIVAL + fertilized STRAWBERRY;
- COW5_DAILY + fertilized STRAWBERRY as action-starvation control;
- bounded dedicated HIRE variants where crop workload can make labor positive;
- an elite-informed mixed COW/SHEEP comparator based on CR087 macro families, without assuming one public action tape is the universal solution.

After causal economic/logistics screening, survivors must face heterogeneous population tests and then hosted calibration. FP001 alone never authorizes a hosted promotion.

## Hosted policy

No FP001-only hosted submission is authorized. The track's value is now its library of proven primitives. A hosted candidate should be an integrated competitive policy unless evidence unexpectedly shows a standalone FP architecture is superior.
