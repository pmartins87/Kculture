# FP001 STATUS — first-principles innovation

Updated: 2026-09-14

Authoritative branch: `research/first-principles-economy-v1`.

## Mission

Discover a prize-class Kaggriculture policy from official mechanics, our own experiments and legal runtime state, without using competitor action tapes as policy-construction data.

## Source of truth

Read together:

1. `docs/strategy/FP001_FIRST_PRINCIPLES_INNOVATION_PROTOCOL_2026-09-14.md`
2. `docs/strategy/FP001_ROADMAP.md`
3. `tools/fp001_market_microsim.py`
4. `tools/fp001_engine_parity.py`
5. `candidates/fp001_h1_town_wheat_carry.py`
6. `tools/fp001_h1_causal_test.py`
7. `tools/fp001_h1b_pulse_hold_scan.py`
8. `tools/fp001_h1b_engine_parity.py`
9. `tools/fp001_h8_animal_fertilizer_economics.py`
10. `tools/fp001_h8_control_frontier.py`
11. `candidates/fp001_h8_single_animal_module.py`
12. `tools/fp001_h8_single_animal_runtime_test.py`
13. `candidates/fp001_h8_multi_animal_module.py`
14. `tools/fp001_h8_multi_animal_runtime_test.py`
15. `tools/fp001_h9_town_animal_demand.py`
16. `candidates/fp001_h8_cow3_care_wrapper.py`
17. `tools/fp001_h8_cow3_care_runtime_test.py`

## Proven primitives

- **FP0 mechanics parity: PASS** — workflow `34842825909`.
- **H1 town-pulse WHEAT carry: causal PASS** — workflow `34843184110`; 32 episodes, mean +916.875 vs PASS, flat-price null exactly zero.
- **H1B owned-sale deferral: mechanics PASS** — workflow `34843556192`; 104/104 positive exact cases. Large isolated timing values include MILK q50/D7 +792, STRAWBERRY q50/D7 +731, WOOL q50/D6 +827.

## H8 — animal/fertilizer capital engine

### R2A exact economics — PASS

Workflow `34844070131`. Minimum-survival feeding can keep animals alive on 15 WHEAT over 30 days while exposing 30 fertilizer units. Three-animal raw day-30 economics before pathing/hire costs: SHEEP +10411, COW +10111, GOOSE +9544.

### R2A2-A exact FEED/CARE frontier — PASS

Workflow `34844616747`. In the abstract exact control frontier, SHEEP was best for n=3 at every tested action shadow 0–80 and horizons 10/20/30. This remains an economics/control result, not a physical runtime ranking.

### R2A2-B1 one-animal runtime — PASS

Workflow `34844919444`, 4 fresh seeds × both seats/species. Mean realized deltas:

- COW **+4721**;
- SHEEP **+3593**;
- GOOSE **+3457**.

All animals survived and every episode was profitable. Runtime ranking therefore differed from the abstract frontier.

### R2A2-B2 multi-animal runtime — PASS; physical backbone selected

Workflow **`34846686427`** completed SUCCESS with `H8_MULTI_ANIMAL_RUNTIME_PASS`.

All tested architectures were profitable in all 8 fresh seed/seat episodes. Mean deltas vs starting money:

1. **COW3_H0: +12880.75** — median 12961.5, min 11540, max 14060;
2. COW3_H2: +12824.75;
3. COW2_SHEEP1_H2: +11881.0;
4. COW1_SHEEP2_H2: +10874.75;
5. SHEEP3_H2: +9807.0;
6. COW2_H0: +8522.25;
7. COW2_H2: +8465.0.

For COW3_H0 across the 8 episodes, aggregate realized operations included 456 WHEAT bought, 688 fertilizer sold, 264 MILK sold, 360 FEED actions, 688 fertilizer collections, 264 harvests and 1816 moves.

**Daily HIRE did not help.** Two hands reduced movement but made money slightly worse:

- COW2 H2-H0 = **-57.25** mean;
- COW3 H2-H0 = **-56.0** mean.

This is almost pure hire-cost drag because realized feed/collection/harvest/output stayed unchanged. Therefore the provisional first-principles physical backbone is now:

> **3 COW, main farmer only, fixed NW micro-layout `(4,4),(3,4),(4,3)`, no routine hired hands.**

This architecture is provisional, not a full competitive farm.

## H9 — town-conditioned animal demand — PASS

Workflow **`34847099631`** completed SUCCESS with `H9_TOWN_ANIMAL_DEMAND_PASS`.

Under official defaults, expected full-season town pulls for animal products are:

- EGG **228**;
- MILK **327**;
- WOOL **228**.

Thus prior expected MILK demand is **99 units / 43.4% higher than WOOL**, which explains a meaningful part of COW's runtime advantage that the earlier no-town-credit economics model could not see.

The public unlocked-shop list is also a powerful adaptive signal. Examples for expected remaining demand:

- day 3, one `YARN_STORE`: WOOL **508.5**, MILK 263.25;
- day 3, one `PIZZA_SHOP`: MILK **425.25**, WOOL 184.5;
- day 6, two `YARN_STORE`: WOOL **721.5**, MILK 206.25;
- day 6, `PIZZA_SHOP` + `ICE_CREAM_SHOP`: MILK **494.25**, WOOL 145.5.

Decision: keep COW3 as the opening physical backbone for now, but future capacity expansion should be shop-conditioned rather than hard-coded monoculture.

## Current active gate — R2A2-B3 CARE overlay on COW3/H0

The B3 candidate adds CARE only in otherwise-idle turns on top of the proven B2 safety scheduler, preserving urgent FEED, fertilizer collection and harvest priority.

Paired modes on identical fresh seed/seat pairs:

- `NONE`: exact B2-style COW3/H0 baseline;
- `SURVIVAL`: CARE after baseline survival FEED when idle capacity exists;
- `DAILY`: use idle capacity for additional daily FEED + CARE to bank more COW production bonus.

Files:

- `candidates/fp001_h8_cow3_care_wrapper.py`
- `tools/fp001_h8_cow3_care_runtime_test.py`
- `.github/workflows/fp001-h8-cow3-care-runtime.yml`

Decision gate: promote CARE only if paired realized bank improves on fresh seeds without animal loss, collection loss or new terminal inventory failure. Do not keep CARE merely because the abstract frontier says it can help.

## Additional official-mechanics conclusions

- BUILD_COOP / BUILD_PASTURE is free; animal purchase is setup capital.
- Daily HIRE follows Fibonacci and resets daily, but cheap cash cost does not imply positive marginal value when the main farmer has spare action capacity.
- SELL/BUY_PRODUCT same-slot prices are quoted from the same pre-commit inventory for both players; no intrinsic seat-0 price edge.
- CARE needs FEED to bank bonus, and pending CARE is paid only on a fed production day.

## Next architecture decisions

1. Close B3 CARE overlay causally.
2. If CARE passes, freeze a stronger COW3 primitive and add realized-vs-model attribution.
3. Then test H9 shop-conditioned **expansion** rather than replacing the proven opening COW3 blindly.
4. Only after the physical production primitive stabilizes, combine it with H1/H1B through a common opportunity-cost controller.

## Hosted policy

No hosted submission is authorized yet. We now have a strong zero-lineage runtime production primitive, but not yet a complete population-tested competitive farm policy.
