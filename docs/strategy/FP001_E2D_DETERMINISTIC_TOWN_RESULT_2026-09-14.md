# FP001 E2D — deterministic-town causal result

Date: 2026-09-14
Run: `34866890716`
Conclusion: **PASS**

## Question

Does one dedicated first-cost daily hand make the previously proven H11 STRAWBERRY module economically positive when the animal backbone is held intact, after removing the discovered RNG coupling between crop tile occupancy and random town-shop selection?

## Methodological correction

Earlier E2/E2B matched-seed comparisons showed implausible ±10k–20k bank swings even when animal actions and output were unchanged.

E2C traced the cause to the official engine's end-of-day ordering:

1. one RNG is initialized from episode seed + day;
2. `_spawn_weeds(...)` calls `rng.random()` once for every empty unlocked tile;
3. random shop unlock later calls `rng.choice(...)` using the same RNG.

A crop occupying one otherwise-empty tile therefore changes the number of RNG draws before the shop choice. This changes the future shop sequence, town demand and market prices even with the same episode seed. Setting `weedSpawnChance=0` does not remove this coupling because the per-empty-tile random draws are still consumed.

E2D therefore kept the E2 policy frozen and changed only the causal evaluation environment:

- `weedSpawnChance=0`
- `townShopUnlockInterval=999` (no stochastic shop unlock during the 30-day season)
- normal town-center demand preserved
- fresh nominal seeds `69401..69404`
- both seats

This is a causal economics environment, not a leaderboard simulator.

## Result

All cases mechanically completed; all animals survived.

### COW4_DAILY

- animal-only: `13,628`
- STRAWBERRY no hand: `13,528` (`-100` vs base; seed cost with failed crop)
- STRAWBERRY + dedicated hand: `14,535`
- hand vs same crop without hand: **+1,007**, 8/8
- full module vs animal-only: **+907**, 8/8

### COW5_SURVIVAL

- animal-only: `17,264`
- STRAWBERRY no hand: `17,762`
- STRAWBERRY + dedicated hand: `18,183`
- hand vs same crop without hand: **+421**, 8/8
- full module vs animal-only: **+919**, 8/8
- no-hand crop vs animal-only: `+498`, 8/8

### COW5_DAILY

- animal-only: `14,989`
- STRAWBERRY no hand: `14,889` (`-100`)
- STRAWBERRY + dedicated hand: `15,908`
- hand vs same crop without hand: **+1,019**, 8/8
- full module vs animal-only: **+919**, 8/8

## Mechanical invariants

For each matched architecture, adding the dedicated crop hand preserved:

- full COW survival;
- MILK quantity;
- main FEED count;
- main CARE count;
- main movement count.

The hand produced 8 berries per episode from one STRAWBERRY with two H11 fertilizer applications. The result is therefore a genuine additive crop/labor primitive, not displaced animal work.

## Interpretation

E2D proves the mechanism but does **not** justify a hosted submission by itself.

One STRAWBERRY under-uses a daily hand: the hand has large PASS capacity after servicing one tile. The next high-information question is crop density per first hand, not additional hands.

The causal result also creates a permanent testing rule:

> Same episode seed is not a valid common-random-number control when treatments change empty-tile occupancy, because tile occupancy changes the RNG stream that later selects town shops.

For crop causal gates, disable stochastic shop unlocks (or otherwise decouple that RNG) before attributing bank differences to the policy. Restore the normal environment for robustness/population evaluation after causal selection.

## Decision

**PASS → FP001 E3 single-hand crop-density gate.**

E3 freezes a bounded grid over STRAWBERRY, MELON and mixed blocks while preserving one hand maximum and the COW5_DAILY backbone. No E2 threshold retuning is permitted.
