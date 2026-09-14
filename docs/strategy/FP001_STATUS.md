# FP001 STATUS — first-principles innovation

Updated: 2026-09-14

Authoritative branch: `research/first-principles-economy-v1`.

## Mission

Discover a prize-class Kaggriculture policy from official mechanics, our own experiments and legal runtime state, without using competitor action tapes as policy-construction data.

## Binding source of truth

Read together:

1. `docs/strategy/FP001_FIRST_PRINCIPLES_INNOVATION_PROTOCOL_2026-09-14.md`
2. `docs/strategy/FP001_ROADMAP.md`
3. the FP001/H8/H9/H10 candidates and exact-engine test tools referenced below.

CR088 remains untouched on its authoritative branch. FP001 remains zero-lineage for policy construction.

## Proven market primitives

- **FP0 mechanics parity: PASS** — workflow `34842825909`.
- **H1 town-pulse WHEAT carry: causal PASS** — workflow `34843184110`; mean paired +916.875 over 32 episodes; flat-price null exactly zero.
- **H1B owned-sale deferral: mechanics PASS** — workflow `34843556192`; 104/104 exact positive cases. Large isolated timing values include MILK q50/D7 +792, STRAWBERRY q50/D7 +731, WOOL q50/D6 +827.

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

Routine daily hands were negative marginal value: COW2 H2-H0 -57.25 and COW3 H2-H0 -56.0. B2 therefore selected 3 COW + main farmer only as the physical backbone.

### R2A2-B3 CARE overlay — STRONG PASS

Workflow **`34847600991`** completed SUCCESS with `H8_COW3_CARE_RUNTIME_STABLE` after an initial infrastructure-only import failure in run `34847381440` was fixed without changing policy.

Paired test: 8 fresh seeds × both seats = 16 identical seed/seat cases per mode against PASS.

Final-bank deltas over starting money:

- `NONE`: mean **+13101.375**, median 13083, min 11701, max 14383;
- `SURVIVAL`: mean **+22103.5**, median 22139, min 18243, max 24969;
- `DAILY`: mean **+27308.5**, median 27470, min 20521, max 31843.

Paired causal deltas:

- SURVIVAL minus NONE: **+9002.125 mean**, min +6542, max +10586, **16/16 wins**;
- DAILY minus NONE: **+14207.125 mean**, min +8820, max +17460, **16/16 wins**;
- DAILY minus SURVIVAL: **+5205 mean**, min +2278, max +6874, **16/16 wins**.

Aggregate operations across 16 episodes:

- NONE: 720 FEED, 0 CARE, 912 WHEAT bought, 1376 fertilizer sold, 528 MILK sold, 3632 moves;
- SURVIVAL: 720 FEED, 720 CARE, same 912 WHEAT bought, 1376 fertilizer sold, **1152 MILK sold**, 4352 moves;
- DAILY: 1424 FEED, 1328 CARE, 1536 WHEAT bought, 1392 fertilizer sold, **1648 MILK sold**, 3952 moves.

Interpretation: CARE is a first-order production mechanism, not a marginal refinement. CARE after already-required survival FEED more than doubled realized MILK with no extra WHEAT versus NONE. Additional DAILY FEED+CARE remained highly profitable despite extra feed cost. The provisional production backbone is therefore upgraded to:

> **COW3 + main farmer only + DAILY FEED/CARE overlay**, preserving urgent survival, fertilizer and harvest priorities.

## H9 town-conditioned animal demand — PASS

Workflow `34847099631`.

Full-season prior expected town pulls: EGG 228, MILK 327, WOOL 228. MILK prior demand is +99 / +43.4% over WOOL. Public shop reveals can reverse local species economics strongly; e.g. day3 YARN_STORE implies expected remaining WOOL 508.5 vs MILK 263.25, while day3 PIZZA_SHOP implies MILK 425.25 vs WOOL 184.5.

Decision: opening COW economics are strongly supported, but future expansion should eventually condition on public shop composition.

## H10 — compact COW scale + batched harvest — ACTIVE

The B2 logs exposed an obvious physical inefficiency: COW3 performed roughly one HARVEST per realized MILK unit even though a COW can hold up to 6. At the same time, B2 showed no saturation at the third cow: COW3_H0 exceeded COW2_H0 by about +4358.5 mean.

New files:

- `candidates/fp001_h10_cow_scale_module.py`
- `tools/fp001_h10_cow_scale_runtime_test.py`
- `.github/workflows/fp001-h10-cow-scale-runtime.yml`

Current workflow: **`34848106237`**.

Architectures tested on identical fresh seed/seat pairs:

- B2_COW3 control;
- H10_COW3 with harvest threshold 1;
- H10_COW3 with threshold 6;
- H10_COW4 threshold 6;
- H10_COW5 threshold 6;
- H10_COW6 threshold 6.

H10 uses a zero-lineage compact NW snake `(4,4),(3,4),(2,4),(1,4),(1,3),(2,3)`, bulk animal pickup during setup, main farmer only, urgent survival FEED, daily fertilizer collection and configurable batched MILK harvest.

The gate explicitly separates:

1. new layout/scheduler effect: H10 COW3 T1 - B2 COW3;
2. pure batching effect: H10 COW3 T6 - T1;
3. marginal scale: COW4-COW3, COW5-COW4, COW6-COW5.

Animal loss at scale is recorded as evidence rather than turned into a hidden/aborted experiment.

## Decision rules after H10

- If batching is positive, it becomes part of the physical primitive.
- Scale only while marginal realized bank remains positive and survival remains stable.
- After the best no-CARE scale is identified, combine **that scale** with the proven DAILY CARE mechanism rather than assuming COW3 is globally optimal.
- Do not add routine hired hands unless scale congestion creates measurable positive labor value.
- Only after production scale stabilizes should H9 shop-conditioned expansion and H1/H1B common opportunity-cost integration take priority.

## Hosted policy

No hosted submission yet. FP001 now has a very strong zero-lineage economic/physical primitive, but the optimal scale and complete competitive policy are not frozen.
